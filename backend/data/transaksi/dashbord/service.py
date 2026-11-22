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
from backend.utils.timezone import day_bounds_utc, period_bounds_utc, timezone_name

logger = logging.getLogger(__name__)

# ── TTL ───────────────────────────────────────────────────────────
TTL_SUMMARY  = 60
TTL_REVENUE  = 120
TTL_ACTIVITY = 30

# Status Midtrans yang dianggap "lunas / sukses"
SUCCESS_STATUSES = ("settlement", "capture")

# Status yang masih menunggu pembayaran
PENDING_STATUSES = ("pending", "pending_payment")

# Status yang dianggap gagal / batal
FAIL_STATUSES = ("cancel", "deny", "expire", "failed")


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

    async def get_summary(self, session: AsyncSession, tz, period: str = "all") -> Dict:
        tz_name = timezone_name(tz)
        KEY = f"dash:trx:summary:{period}:{tz_name}"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        today = datetime.now(tz).date()
        start, end = period_bounds_utc(period, tz, today)
        today_start, today_end = day_bounds_utc(today, tz)
        week_start, _ = day_bounds_utc(today - timedelta(days=6), tz)
        month_start, _ = day_bounds_utc(today.replace(day=1), tz)
        _, month_end = day_bounds_utc(today, tz)

        period_conds = []
        if start is not None:
            period_conds = [Transaction.created_at >= start, Transaction.created_at < end]

        paid = Transaction.transaction_status.in_(SUCCESS_STATUSES)
        pending = Transaction.transaction_status.in_(PENDING_STATUSES)
        failed = Transaction.transaction_status.in_(FAIL_STATUSES)
        not_failed = Transaction.transaction_status.notin_(FAIL_STATUSES)

        # Periode aktif, berdasarkan tanggal order
        agg = await session.execute(
            select(
                func.count(Transaction.uuid).label("orders_total"),
                func.sum(case((paid, 1), else_=0)).label("orders_paid"),
                func.sum(case((pending, 1), else_=0)).label("orders_pending"),
                func.sum(case((not_failed, Transaction.gross_amount), else_=0)).label("sales_total"),
                func.sum(case((paid, Transaction.gross_amount), else_=0)).label("sales_paid"),
                func.sum(case((pending, Transaction.gross_amount), else_=0)).label("sales_pending"),
            ).where(*period_conds)
        )
        row = agg.one()

        # Uang masuk, berdasarkan tanggal settlement
        cash_agg = await session.execute(
            select(
                func.sum(case((paid, Transaction.gross_amount), else_=0)).label("cash_all"),
                func.sum(
                    case(
                        (and_(paid, Transaction.settlement_time >= today_start,
                              Transaction.settlement_time < today_end), Transaction.gross_amount),
                        else_=0,
                    )
                ).label("cash_today"),
                func.sum(
                    case(
                        (and_(paid, Transaction.settlement_time >= week_start,
                              Transaction.settlement_time < today_end), Transaction.gross_amount),
                        else_=0,
                    )
                ).label("cash_week"),
                func.sum(
                    case(
                        (and_(paid, Transaction.settlement_time >= month_start,
                              Transaction.settlement_time < month_end), Transaction.gross_amount),
                        else_=0,
                    )
                ).label("cash_month"),
            ).where(paid)
        )
        cash = cash_agg.one()
        cash_for_period = {
            "all": int(cash.cash_all or 0),
            "today": int(cash.cash_today or 0),
            "week": int(cash.cash_week or 0),
            "month": int(cash.cash_month or 0),
        }.get(period, 0)

        # Agregat seumur hidup untuk sub-kartu dan kompatibilitas API lama
        all_agg = await session.execute(
            select(
                func.count(Transaction.uuid).label("all_orders"),
                func.sum(case((paid, 1), else_=0)).label("all_paid"),
                func.sum(case((pending, 1), else_=0)).label("all_pending"),
                func.sum(case((failed, 1), else_=0)).label("all_failed"),
                func.sum(
                    case(
                        (and_(Transaction.created_at >= today_start,
                              Transaction.created_at < today_end), 1),
                        else_=0,
                    )
                ).label("orders_today"),
                func.sum(case((paid, Transaction.shipping_cost), else_=0)).label("shipping_cost_all"),
            )
        )
        all_row = all_agg.one()

        items_stmt = (
            select(func.sum(TransactionItem.quantity).label("total_sold"))
            .join(Transaction, Transaction.uuid == TransactionItem.transaction_id)
            .where(paid, *period_conds)
        )
        items_row = (await session.execute(items_stmt)).one()
        items_sold = int(items_row.total_sold or 0)

        ship_stmt = (
            select(Shipment.delivery_status, func.count(Shipment.uuid).label("count"))
            .join(Transaction, Transaction.uuid == Shipment.transaction_uuid)
            .where(paid, *period_conds)
            .group_by(Shipment.delivery_status)
        )
        ship_map: Dict[str, int] = {r.delivery_status: r.count for r in await session.execute(ship_stmt)}

        sales_total = int(row.sales_total or 0)
        orders_total = int(row.orders_total or 0)
        orders_paid = int(row.orders_paid or 0)
        orders_pending = int(row.orders_pending or 0)

        data = {
            "period": period,
            "timezone": tz_name,
            # angka besar: nilai order pada periode aktif
            "sales_total": sales_total,
            "sales_paid": int(row.sales_paid or 0),
            "sales_pending": int(row.sales_pending or 0),
            "orders_total": orders_total,
            "orders_paid": orders_paid,
            "orders_pending": orders_pending,
            "items_sold": items_sold,
            "shipped_count": ship_map.get("SHIPPED", 0),
            "processing_shipment": ship_map.get("PROCESSING", 0),
            "delivered_count": ship_map.get("DELIVERED", 0),
            "cancelled_shipment": ship_map.get("CANCELLED", 0),
            "avg_order_value": int(sales_total / orders_total) if orders_total else 0,
            # uang masuk, untuk chart dan kompatibilitas API lama
            "total_revenue": cash_for_period,
            "revenue_today": int(cash.cash_today or 0),
            "revenue_this_week": int(cash.cash_week or 0),
            "revenue_this_month": int(cash.cash_month or 0),
            "total_orders": int(all_row.all_orders or 0),
            "orders_today": int(all_row.orders_today or 0),
            "pending_payment_count": int(all_row.all_pending or 0),
            "settlement_count": int(all_row.all_paid or 0),
            "cancel_expire_count": int(all_row.all_failed or 0),
            "total_items_sold": items_sold,
            "total_shipping_cost": int(all_row.shipping_cost_all or 0),
        }

        await self._cache_set(KEY, data, TTL_SUMMARY)
        return {"status": "success", "source": "db", "data": data}

    # ─────────────────────────────────────────────────────────────
    # 2. REVENUE CHART
    # ─────────────────────────────────────────────────────────────

    async def get_revenue_chart(
        self, session: AsyncSession, tz, range: str = "7d"
    ) -> Dict:
        tz_name = timezone_name(tz)
        KEY = f"dash:trx:revenue:{range}:{tz_name}"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "range": range, "data": cached}

        today = datetime.now(tz).date()

        if range == "12m":
            data = await self._revenue_monthly(session, today, tz)
        else:
            days = 7 if range == "7d" else 30
            data = await self._revenue_daily(session, today, days, tz)

        await self._cache_set(KEY, data, TTL_REVENUE)
        return {"status": "success", "source": "db", "range": range, "data": data}

    async def _revenue_daily(
        self, session: AsyncSession, today: date, days: int, tz
    ) -> List[Dict]:
        since = today - timedelta(days=days - 1)
        since_utc, _ = day_bounds_utc(since, tz)
        _, end_utc = day_bounds_utc(today, tz)
        local_day = func.date(func.timezone(timezone_name(tz), Transaction.settlement_time))

        rows = await session.execute(
            select(
                local_day.label("day"),
                func.sum(Transaction.gross_amount).label("gross_revenue"),
                func.sum(Transaction.shipping_cost).label("shipping_sum"),
                func.count(Transaction.uuid).label("order_count"),
            )
            .where(
                and_(
                    Transaction.transaction_status.in_(SUCCESS_STATUSES),
                    Transaction.settlement_time >= since_utc,
                    Transaction.settlement_time < end_utc,
                )
            )
            .group_by(local_day)
            .order_by(local_day)
        )
        raw_map: Dict[date, Any] = {r.day: r for r in rows}

        result = []
        for i in range(days):
            d = since + timedelta(days=i)
            r = raw_map.get(d)
            gross    = int(r.gross_revenue or 0) if r else 0
            shipping = int(r.shipping_sum  or 0) if r else 0
            count    = int(r.order_count   or 0) if r else 0

            label = d.strftime("%-d %b") if days <= 30 else d.strftime("%a %-d %b")

            result.append({
                "label":       label,
                "period":      d.isoformat(),
                "gross_revenue": gross,
                "net_revenue":   gross - shipping,
                "shipping_cost": shipping,
                "order_count":   count,
                "avg_order":     (gross // count) if count else 0,
            })
        return result

    async def _revenue_monthly(
        self, session: AsyncSession, today: date, tz
    ) -> List[Dict]:
        year  = today.year
        month = today.month - 11
        while month <= 0:
            month += 12
            year  -= 1
        since = date(year, month, 1)
        since_utc, _ = day_bounds_utc(since, tz)
        _, end_utc = day_bounds_utc(today, tz)
        local_month = func.date_trunc(
            "month", func.timezone(timezone_name(tz), Transaction.settlement_time)
        )

        rows = await session.execute(
            select(
                local_month.label("month"),
                func.sum(Transaction.gross_amount).label("gross_revenue"),
                func.sum(Transaction.shipping_cost).label("shipping_sum"),
                func.count(Transaction.uuid).label("order_count"),
            )
            .where(
                and_(
                    Transaction.transaction_status.in_(SUCCESS_STATUSES),
                    Transaction.settlement_time >= since_utc,
                    Transaction.settlement_time < end_utc,
                )
            )
            .group_by(local_month)
            .order_by(local_month)
        )
        raw_map: Dict[date, Any] = {}
        for r in rows:
            key = r.month.date().replace(day=1) if hasattr(r.month, "date") else r.month.replace(day=1)
            raw_map[key] = r

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

    async def invalidate_cache(self) -> None:
        try:
            redis = get_redis_token()
            for pattern in (
                "dash:trx:summary:*",
                "dash:trx:revenue:*",
                "dash:trx:activity:*",
            ):
                async for key in redis.scan_iter(match=pattern):
                    await redis.delete(key)
        except Exception as exc:
            logger.warning(f"[TrxDash] cache invalidation failed: {exc}")


async def invalidate_dashboard_cache() -> None:
    await TransaksiDashboardService().invalidate_cache()