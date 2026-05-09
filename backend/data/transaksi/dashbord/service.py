"""
dashboard_transaksi_service.py
───────────────────────────────
Business logic dashboard transaksi (barang e-commerce).

Cache strategy (Dragonfly):
  summary        → dash:trx:summary          TTL 60 s
  revenue-chart  → dash:trx:revenue:{range}  TTL 120 s
  activity       → dash:trx:activity:{limit} TTL 30 s

Semua query ke PostgreSQL — satu agregat besar per endpoint,
seminimal mungkin round-trip ke DB.
"""

import json
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, case, and_, desc, asc
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.data.transaksi.model import Transaction, TransactionItem
from backend.data.ongkir.model import Shipment
from backend.db.redis import get_redis_token

logger = logging.getLogger(__name__)

# ── TTL ───────────────────────────────────────────────────────────
TTL_SUMMARY  = 60
TTL_REVENUE  = 120
TTL_ACTIVITY = 30

# Status Midtrans yang dianggap "lunas / sukses"
SUCCESS_STATUSES = ("settlement", "capture")

# Status yang dianggap gagal / batal
FAIL_STATUSES = ("cancel", "deny", "expire")


# ══════════════════════════════════════════════════════════════════
class TransaksiDashboardService:

    # ── Redis helpers ─────────────────────────────────────────────

    async def _cache_get(self, key: str) -> Optional[Any]:
        try:
            raw = await get_redis_token().get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.warning(f"[TrxDash] Redis GET {key}: {exc}")
            return None

    async def _cache_set(self, key: str, value: Any, ttl: int) -> None:
        try:
            await get_redis_token().set(
                key, json.dumps(value, default=str), ex=ttl
            )
        except Exception as exc:
            logger.warning(f"[TrxDash] Redis SET {key}: {exc}")

    # ─────────────────────────────────────────────────────────────
    # 1. SUMMARY / KPI CARDS
    # ─────────────────────────────────────────────────────────────

    async def get_summary(self, session: AsyncSession) -> Dict:
        KEY = "dash:trx:summary"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        now         = datetime.now(timezone.utc)
        today       = now.date()
        week_start  = today - timedelta(days=6)   # 7 hari terakhir inklusif
        month_start = today.replace(day=1)

        # ── Agregat utama Transaction — satu round-trip ───────────
        agg = await session.execute(
            select(
                # total orders
                func.count(Transaction.uuid).label("total_orders"),

                # orders hari ini
                func.sum(
                    case((func.date(Transaction.created_at) == today, 1), else_=0)
                ).label("orders_today"),

                # pending payment
                func.sum(
                    case((Transaction.transaction_status == "pending_payment", 1), else_=0)
                ).label("pending_payment"),

                # settlement / capture
                func.sum(
                    case(
                        (Transaction.transaction_status.in_(SUCCESS_STATUSES), 1),
                        else_=0,
                    )
                ).label("settlement_count"),

                # cancel + expire + deny
                func.sum(
                    case(
                        (Transaction.transaction_status.in_(FAIL_STATUSES), 1),
                        else_=0,
                    )
                ).label("cancel_expire_count"),

                # ── Revenue (settlement only) ─────────────────────
                func.sum(
                    case(
                        (Transaction.transaction_status.in_(SUCCESS_STATUSES),
                         Transaction.gross_amount),
                        else_=0,
                    )
                ).label("total_revenue"),

                func.sum(
                    case(
                        (
                            and_(
                                Transaction.transaction_status.in_(SUCCESS_STATUSES),
                                func.date(Transaction.settlement_time) == today,
                            ),
                            Transaction.gross_amount,
                        ),
                        else_=0,
                    )
                ).label("revenue_today"),

                func.sum(
                    case(
                        (
                            and_(
                                Transaction.transaction_status.in_(SUCCESS_STATUSES),
                                func.date(Transaction.settlement_time) >= week_start,
                            ),
                            Transaction.gross_amount,
                        ),
                        else_=0,
                    )
                ).label("revenue_this_week"),

                func.sum(
                    case(
                        (
                            and_(
                                Transaction.transaction_status.in_(SUCCESS_STATUSES),
                                func.date(Transaction.settlement_time) >= month_start,
                            ),
                            Transaction.gross_amount,
                        ),
                        else_=0,
                    )
                ).label("revenue_this_month"),

                # ── Shipping cost terkumpul ───────────────────────
                func.sum(
                    case(
                        (Transaction.transaction_status.in_(SUCCESS_STATUSES),
                         Transaction.shipping_cost),
                        else_=0,
                    )
                ).label("total_shipping_cost"),

                # ── Average order value ───────────────────────────
                func.avg(
                    case(
                        (Transaction.transaction_status.in_(SUCCESS_STATUSES),
                         Transaction.gross_amount),
                        else_=None,
                    )
                ).label("avg_order_value"),
            )
        )
        row = agg.one()

        total_revenue    = int(row.total_revenue    or 0)
        settlement_count = int(row.settlement_count or 0)
        avg_order        = int(row.avg_order_value  or 0)

        # ── Total item terjual (join TransactionItem) ─────────────
        items_agg = await session.execute(
            select(
                func.sum(TransactionItem.quantity).label("total_sold")
            )
            .join(Transaction, Transaction.uuid == TransactionItem.transaction_id)
            .where(Transaction.transaction_status.in_(SUCCESS_STATUSES))
        )
        items_row  = items_agg.one()
        total_sold = int(items_row.total_sold or 0)

        # ── Shipment status ───────────────────────────────────────
        # Hanya settlement — join Transaction agar data konsisten
        ship_agg = await session.execute(
            select(
                Shipment.delivery_status,
                func.count(Shipment.uuid).label("count"),
            )
            .join(Transaction, Transaction.uuid == Shipment.transaction_uuid)
            .where(Transaction.transaction_status.in_(SUCCESS_STATUSES))
            .group_by(Shipment.delivery_status)
        )
        ship_map: Dict[str, int] = {r.delivery_status: r.count for r in ship_agg}

        data = {
            # revenue
            "total_revenue":       total_revenue,
            "revenue_today":       int(row.revenue_today      or 0),
            "revenue_this_week":   int(row.revenue_this_week  or 0),
            "revenue_this_month":  int(row.revenue_this_month or 0),

            # orders
            "total_orders":          int(row.total_orders        or 0),
            "orders_today":          int(row.orders_today         or 0),
            "pending_payment_count": int(row.pending_payment      or 0),
            "settlement_count":      settlement_count,
            "cancel_expire_count":   int(row.cancel_expire_count or 0),

            # shipping
            "processing_shipment": ship_map.get("PROCESSING", 0),
            "shipped_count":       ship_map.get("SHIPPED",    0),
            "delivered_count":     ship_map.get("DELIVERED",  0),
            "cancelled_shipment":  ship_map.get("CANCELLED",  0),

            # produk
            "total_items_sold":  total_sold,
            "avg_order_value":   avg_order,
            "total_shipping_cost": int(row.total_shipping_cost or 0),
        }

        await self._cache_set(KEY, data, TTL_SUMMARY)
        return {"status": "success", "source": "db", "data": data}

    # ─────────────────────────────────────────────────────────────
    # 2. REVENUE CHART
    # ─────────────────────────────────────────────────────────────

    async def get_revenue_chart(
        self, session: AsyncSession, range: str = "7d"
    ) -> Dict:
        KEY = f"dash:trx:revenue:{range}"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "range": range, "data": cached}

        today = datetime.now(timezone.utc).date()

        if range == "12m":
            data = await self._revenue_monthly(session, today)
        else:
            days = 7 if range == "7d" else 30
            data = await self._revenue_daily(session, today, days)

        await self._cache_set(KEY, data, TTL_REVENUE)
        return {"status": "success", "source": "db", "range": range, "data": data}

    async def _revenue_daily(
        self, session: AsyncSession, today: date, days: int
    ) -> List[Dict]:
        since = today - timedelta(days=days - 1)

        rows = await session.execute(
            select(
                func.date(Transaction.settlement_time).label("day"),
                func.sum(Transaction.gross_amount).label("gross_revenue"),
                func.sum(Transaction.shipping_cost).label("shipping_sum"),
                func.count(Transaction.uuid).label("order_count"),
            )
            .where(
                and_(
                    Transaction.transaction_status.in_(SUCCESS_STATUSES),
                    func.date(Transaction.settlement_time) >= since,
                    func.date(Transaction.settlement_time) <= today,
                )
            )
            .group_by(func.date(Transaction.settlement_time))
            .order_by(func.date(Transaction.settlement_time))
        )
        raw_map: Dict[date, Any] = {r.day: r for r in rows}

        result = []
        for i in range(days):
            d = since + timedelta(days=i)
            r = raw_map.get(d)
            gross    = int(r.gross_revenue or 0) if r else 0
            shipping = int(r.shipping_sum  or 0) if r else 0
            count    = int(r.order_count   or 0) if r else 0

            # Format label ringkas: "1 Jan" atau "Sen 1 Jan" (sesuai kebutuhan)
            label = d.strftime("%-d %b") if days <= 30 else d.strftime("%a %-d %b")

            result.append({
                "label":       label,
                "period":      d.isoformat(),
                "gross_revenue": gross,
                "net_revenue":   gross - shipping,   # tanpa ongkir
                "shipping_cost": shipping,
                "order_count":   count,
                "avg_order":     (gross // count) if count else 0,
            })
        return result

    async def _revenue_monthly(
        self, session: AsyncSession, today: date
    ) -> List[Dict]:
        # Hitung bulan pertama (12 bulan lalu)
        year  = today.year
        month = today.month - 11  # bisa negatif
        while month <= 0:
            month += 12
            year  -= 1
        since = date(year, month, 1)

        rows = await session.execute(
            select(
                func.date_trunc("month", Transaction.settlement_time).label("month"),
                func.sum(Transaction.gross_amount).label("gross_revenue"),
                func.sum(Transaction.shipping_cost).label("shipping_sum"),
                func.count(Transaction.uuid).label("order_count"),
            )
            .where(
                and_(
                    Transaction.transaction_status.in_(SUCCESS_STATUSES),
                    func.date(Transaction.settlement_time) >= since,
                )
            )
            .group_by(func.date_trunc("month", Transaction.settlement_time))
            .order_by(func.date_trunc("month", Transaction.settlement_time))
        )
        raw_map: Dict[date, Any] = {}
        for r in rows:
            # date_trunc returns datetime, normalise to date
            key = r.month.date().replace(day=1) if hasattr(r.month, "date") else r.month.replace(day=1)
            raw_map[key] = r

        # Build 12-bulan skeleton
        result = []
        for i in range(12):
            m = today.month - (11 - i)
            y = today.year
            while m <= 0:
                m += 12
                y -= 1
            d = date(y, m, 1)
            r = raw_map.get(d)
            gross    = int(r.gross_revenue or 0) if r else 0
            shipping = int(r.shipping_sum  or 0) if r else 0
            count    = int(r.order_count   or 0) if r else 0
            result.append({
                "label":         d.strftime("%b %Y"),
                "period":        d.isoformat(),
                "gross_revenue": gross,
                "net_revenue":   gross - shipping,
                "shipping_cost": shipping,
                "order_count":   count,
                "avg_order":     (gross // count) if count else 0,
            })
        return result

    # ─────────────────────────────────────────────────────────────
    # 3. ACTIVITY FEED
    # ─────────────────────────────────────────────────────────────

    async def get_activity(
        self, session: AsyncSession, limit: int = 15
    ) -> Dict:
        KEY = f"dash:trx:activity:{limit}"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "items": cached}

        # Ambil transaksi terbaru beserta shipment (LEFT JOIN)
        rows = await session.execute(
            select(
                Transaction.uuid,
                Transaction.order_id,
                Transaction.user_id,
                Transaction.gross_amount,
                Transaction.items_subtotal,
                Transaction.shipping_cost,
                Transaction.discount_amount,
                Transaction.transaction_status,
                Transaction.payment_type,
                Transaction.created_at,
                Transaction.settlement_time,
                # Shipment kolom — bisa NULL (LEFT JOIN)
                Shipment.delivery_status.label("shipment_status"),
                Shipment.courier_name.label("courier_name"),
                Shipment.courier_service.label("courier_service"),
                Shipment.waybill_number.label("waybill_number"),
            )
            .outerjoin(Shipment, Shipment.transaction_uuid == Transaction.uuid)
            .order_by(desc(Transaction.created_at))
            .limit(limit)
        )
        trx_rows = rows.all()

        if not trx_rows:
            return {"status": "success", "source": "db", "items": []}

        # Kumpulkan UUID transaksi → ambil item count + nama produk pertama
        trx_uuids = [r.uuid for r in trx_rows]

        # Subquery: count item + first product name per transaction
        item_rows = await session.execute(
            select(
                TransactionItem.transaction_id,
                func.count(TransactionItem.uuid).label("item_count"),
                func.min(TransactionItem.unit_price).label("_dummy"),  # force group
            )
            .where(TransactionItem.transaction_id.in_(trx_uuids))
            .group_by(TransactionItem.transaction_id)
        )
        item_map: Dict[str, int] = {
            str(r.transaction_id): r.item_count for r in item_rows
        }

        # Ambil nama produk pertama per transaksi (subquery sederhana)
        # Pakai MIN(uuid) sebagai tiebreaker deterministik
        first_item_rows = await session.execute(
            select(
                TransactionItem.transaction_id,
                TransactionItem.stock_id,
            )
            .where(TransactionItem.transaction_id.in_(trx_uuids))
            .distinct(TransactionItem.transaction_id)
            .order_by(
                TransactionItem.transaction_id,
                asc(TransactionItem.uuid),
            )
        )

        # Kumpulkan stock_uuid yang perlu di-lookup
        first_stock_map: Dict[str, str] = {
            str(r.transaction_id): str(r.stock_id) for r in first_item_rows
        }

        # Bulk fetch title semua stock_id unik
        unique_stock_ids = list(set(first_stock_map.values()))
        stock_title_map: Dict[str, str] = {}
        if unique_stock_ids:
            from backend.data.stock.model import Stock
            stock_rows = await session.execute(
                select(Stock.uuid, Stock.title)
                .where(Stock.uuid.in_(unique_stock_ids))
            )
            stock_title_map = {str(r.uuid): r.title for r in stock_rows}

        # ── Build items ───────────────────────────────────────────
        STATUS_LABEL = {
            "pending_payment": "Menunggu Pembayaran",
            "settlement":      "Lunas",
            "capture":         "Lunas",
            "cancel":          "Dibatalkan",
            "deny":            "Ditolak",
            "expire":          "Kadaluarsa",
            "refund":          "Refund",
            "pending":         "Pending",
        }

        items = []
        for r in trx_rows:
            trx_id       = str(r.uuid)
            item_count   = item_map.get(trx_id, 0)
            first_stock  = first_stock_map.get(trx_id)
            product_name = stock_title_map.get(first_stock, "—") if first_stock else "—"

            items.append({
                "uuid":               trx_id,
                "order_id":           r.order_id,
                "user_id":            str(r.user_id),
                "gross_amount":       r.gross_amount,
                "items_subtotal":     r.items_subtotal,
                "shipping_cost":      r.shipping_cost,
                "discount_amount":    r.discount_amount,
                "transaction_status": r.transaction_status,
                "status_label":       STATUS_LABEL.get(r.transaction_status or "", r.transaction_status or "—"),
                "payment_type":       r.payment_type,
                "item_count":         item_count,
                "first_product_name": product_name,
                # Shipment (bisa None jika belum ada)
                "shipment_status":    r.shipment_status,
                "courier_name":       r.courier_name,
                "courier_service":    r.courier_service,
                "waybill_number":     r.waybill_number,
                # Timestamps
                "created_at":         r.created_at,
                "settlement_time":    r.settlement_time,
            })

        await self._cache_set(KEY, items, TTL_ACTIVITY)
        return {"status": "success", "source": "db", "items": items}