"""
dashboard_booking_service.py
────────────────────────────
Business logic dashboard booking Padjajaran CCTV.

Strategi cache (Dragonfly):
  kpi          → dash:booking:kpi              TTL 60 s
  revenue      → dash:booking:revenue:{mode}   TTL 120 s
  status       → dash:booking:status           TTL 60 s
  alerts       → dash:booking:alerts           TTL 30 s
  recent       → dash:booking:recent:{limit}   TTL 30 s
  today        → dash:booking:today            TTL 30 s
  payment      → dash:booking:payment          TTL 60 s

Semua query ke Postgres — tidak ada ES dependency di modul ini.
"""

import json
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, and_, case, desc, asc
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..model import (
    ServiceBooking, ServicePayment,
    BookingStatus, PaymentStatus, PaymentType,
)
from backend.db.redis import get_redis_token

logger = logging.getLogger(__name__)

# ── TTL ───────────────────────────────────────────────────────────
TTL_KPI      = 60
TTL_REVENUE  = 120
TTL_STATUS   = 60
TTL_ALERTS   = 30
TTL_RECENT   = 30
TTL_TODAY    = 30
TTL_PAYMENT  = 60

MAX_PER_SLOT = 3

SLOT_LABELS = {
    "08:00-11:00": "Pagi (08:00–11:00)",
    "11:00-14:00": "Siang (11:00–14:00)",
    "14:00-17:00": "Sore (14:00–17:00)",
}

STATUS_LABELS = {
    BookingStatus.PENDING:   "Menunggu Konfirmasi",
    BookingStatus.CONFIRMED: "Dikonfirmasi",
    BookingStatus.DP_PAID:   "DP Dibayar",
    BookingStatus.PROGRESS:  "Sedang Dikerjakan",
    BookingStatus.DONE:      "Selesai",
    BookingStatus.LUNAS:     "Lunas",
    BookingStatus.CANCEL:    "Dibatalkan",
}

# Status yang dianggap "aktif" (bukan terminal)
ACTIVE_STATUSES = [
    BookingStatus.PENDING,
    BookingStatus.CONFIRMED,
    BookingStatus.DP_PAID,
    BookingStatus.PROGRESS,
]

# Status yang dianggap revenue terkumpul
REVENUE_STATUSES = [BookingStatus.DONE, BookingStatus.LUNAS]

# Status yang DP-nya sudah diterima
DP_COLLECTED_STATUSES = [
    BookingStatus.DP_PAID,
    BookingStatus.PROGRESS,
    BookingStatus.DONE,
    BookingStatus.LUNAS,
]


# ══════════════════════════════════════════════════════════════════
class BookingDashboardService:

    # ── Redis helpers ─────────────────────────────────────────────

    async def _cache_get(self, key: str) -> Optional[Any]:
        try:
            raw = await get_redis_token().get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.warning(f"[BookingDash] Redis GET {key}: {exc}")
            return None

    async def _cache_set(self, key: str, value: Any, ttl: int) -> None:
        try:
            await get_redis_token().set(
                key, json.dumps(value, default=str), ex=ttl
            )
        except Exception as exc:
            logger.warning(f"[BookingDash] Redis SET {key}: {exc}")

    # ─────────────────────────────────────────────────────────────
    # 1. KPI CARDS
    # ─────────────────────────────────────────────────────────────

    async def get_kpi(self, session: AsyncSession) -> Dict:
        KEY = "dash:booking:kpi"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        now      = datetime.now(timezone.utc)
        today    = now.date()
        month_start = today.replace(day=1)

        # ── Satu query agregat semua status ──────────────────────
        # Gunakan conditional aggregation — satu round-trip ke DB
        agg = await session.execute(
            select(
                # total
                func.count(ServiceBooking.uuid).label("total"),

                # per status
                func.sum(case((ServiceBooking.status == BookingStatus.PENDING,   1), else_=0)).label("pending"),
                func.sum(case((ServiceBooking.status == BookingStatus.CONFIRMED, 1), else_=0)).label("confirmed"),
                func.sum(case((ServiceBooking.status == BookingStatus.DP_PAID,   1), else_=0)).label("dp_paid"),
                func.sum(case((ServiceBooking.status == BookingStatus.PROGRESS,  1), else_=0)).label("progress"),
                func.sum(case((ServiceBooking.status == BookingStatus.DONE,      1), else_=0)).label("done"),
                func.sum(case((ServiceBooking.status == BookingStatus.LUNAS,     1), else_=0)).label("lunas"),
                func.sum(case((ServiceBooking.status == BookingStatus.CANCEL,    1), else_=0)).label("cancel"),

                # booking hari ini
                func.sum(
                    case((ServiceBooking.scheduled_date == today, 1), else_=0)
                ).label("today"),

                # booking bulan ini (created_at)
                func.sum(
                    case((func.date(ServiceBooking.created_at) >= month_start, 1), else_=0)
                ).label("this_month"),

                # revenue: sum total_price status DONE + LUNAS
                func.sum(
                    case(
                        (ServiceBooking.status.in_(REVENUE_STATUSES), ServiceBooking.total_price),
                        else_=0,
                    )
                ).label("revenue_total"),

                # revenue bulan ini
                func.sum(
                    case(
                        (
                            and_(
                                ServiceBooking.status.in_(REVENUE_STATUSES),
                                func.date(ServiceBooking.updated_at) >= month_start,
                            ),
                            ServiceBooking.total_price,
                        ),
                        else_=0,
                    )
                ).label("revenue_this_month"),

                # DP terkumpul (dp_amount dari status yg sudah bayar DP)
                func.sum(
                    case(
                        (ServiceBooking.status.in_(DP_COLLECTED_STATUSES), ServiceBooking.dp_amount),
                        else_=0,
                    )
                ).label("dp_collected"),
            )
        )
        row = agg.one()

        total    = row.total or 0
        cancel   = int(row.cancel or 0)
        revenue  = int(row.revenue_total or 0)
        confirmed_n = int(row.confirmed or 0)

        conversion_rate = round((confirmed_n / total * 100), 1) if total > 0 else 0.0
        cancel_rate     = round((cancel / total * 100), 1) if total > 0 else 0.0

        data = {
            "total_booking":      total,
            "booking_hari_ini":   int(row.today or 0),
            "booking_bulan_ini":  int(row.this_month or 0),

            "pending_count":   int(row.pending   or 0),
            "confirmed_count": int(row.confirmed or 0),
            "dp_paid_count":   int(row.dp_paid   or 0),
            "progress_count":  int(row.progress  or 0),
            "done_count":      int(row.done       or 0),
            "lunas_count":     int(row.lunas      or 0),
            "cancel_count":    cancel,

            "total_revenue":        revenue,
            "revenue_bulan_ini":    int(row.revenue_this_month or 0),
            "dp_terkumpul":         int(row.dp_collected or 0),

            "conversion_rate": conversion_rate,  # %
            "cancel_rate":     cancel_rate,       # %
        }

        await self._cache_set(KEY, data, TTL_KPI)
        return {"status": "success", "source": "db", "data": data}

    # ─────────────────────────────────────────────────────────────
    # 2. REVENUE CHART
    # ─────────────────────────────────────────────────────────────

    async def get_revenue_chart(
        self, session: AsyncSession, mode: str = "daily"
    ) -> Dict:
        KEY = f"dash:booking:revenue:{mode}"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "mode": mode, "data": cached}

        now   = datetime.now(timezone.utc)
        today = now.date()

        if mode == "monthly":
            # 12 bulan terakhir
            periods = []
            for i in range(11, -1, -1):
                d = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
                # hitung mundur i bulan dari bulan ini
                year  = today.year
                month = today.month - i
                while month <= 0:
                    month += 12
                    year  -= 1
                periods.append(date(year, month, 1))

            # Query: group by year-month
            rows = await session.execute(
                select(
                    func.date_trunc("month", ServiceBooking.updated_at).label("period"),
                    func.sum(
                        case(
                            (ServiceBooking.status.in_(REVENUE_STATUSES), ServiceBooking.total_price),
                            else_=0,
                        )
                    ).label("total_revenue"),
                    func.sum(
                        case(
                            (ServiceBooking.status.in_(DP_COLLECTED_STATUSES), ServiceBooking.dp_amount),
                            else_=0,
                        )
                    ).label("dp_revenue"),
                    func.count(ServiceBooking.uuid).label("booking_count"),
                )
                .where(
                    ServiceBooking.updated_at >= datetime(periods[0].year, periods[0].month, 1, tzinfo=timezone.utc)
                )
                .group_by(func.date_trunc("month", ServiceBooking.updated_at))
                .order_by(func.date_trunc("month", ServiceBooking.updated_at))
            )
            raw_map = {
                r.period.date().replace(day=1): r
                for r in rows
            }

            data = []
            for p in periods:
                r = raw_map.get(p)
                data.append({
                    "label":         p.strftime("%b %Y"),
                    "period":        p.isoformat(),
                    "total_revenue": int(r.total_revenue) if r and r.total_revenue else 0,
                    "dp_revenue":    int(r.dp_revenue)    if r and r.dp_revenue    else 0,
                    "booking_count": int(r.booking_count) if r else 0,
                })

        else:
            # daily — 30 hari terakhir
            since = today - timedelta(days=29)

            rows = await session.execute(
                select(
                    func.date(ServiceBooking.updated_at).label("period"),
                    func.sum(
                        case(
                            (ServiceBooking.status.in_(REVENUE_STATUSES), ServiceBooking.total_price),
                            else_=0,
                        )
                    ).label("total_revenue"),
                    func.sum(
                        case(
                            (ServiceBooking.status.in_(DP_COLLECTED_STATUSES), ServiceBooking.dp_amount),
                            else_=0,
                        )
                    ).label("dp_revenue"),
                    func.count(ServiceBooking.uuid).label("booking_count"),
                )
                .where(func.date(ServiceBooking.updated_at) >= since)
                .group_by(func.date(ServiceBooking.updated_at))
                .order_by(func.date(ServiceBooking.updated_at))
            )
            raw_map = {r.period: r for r in rows}

            data = []
            for i in range(30):
                d = since + timedelta(days=i)
                r = raw_map.get(d)
                data.append({
                    "label":         d.strftime("%-d %b"),
                    "period":        d.isoformat(),
                    "total_revenue": int(r.total_revenue) if r and r.total_revenue else 0,
                    "dp_revenue":    int(r.dp_revenue)    if r and r.dp_revenue    else 0,
                    "booking_count": int(r.booking_count) if r else 0,
                })

        await self._cache_set(KEY, data, TTL_REVENUE)
        return {"status": "success", "source": "db", "mode": mode, "data": data}

    # ─────────────────────────────────────────────────────────────
    # 3. STATUS DISTRIBUTION
    # ─────────────────────────────────────────────────────────────

    async def get_status_distribution(self, session: AsyncSession) -> Dict:
        KEY = "dash:booking:status"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        rows = await session.execute(
            select(
                ServiceBooking.status,
                func.count(ServiceBooking.uuid).label("count"),
            )
            .group_by(ServiceBooking.status)
        )
        counts    = {r.status: r.count for r in rows}
        total     = sum(counts.values()) or 1

        data = [
            {
                "status":     s.value,
                "label":      STATUS_LABELS.get(s, s.value),
                "count":      counts.get(s, 0),
                "percentage": round(counts.get(s, 0) / total * 100, 1),
            }
            for s in BookingStatus
        ]

        await self._cache_set(KEY, data, TTL_STATUS)
        return {"status": "success", "source": "db", "data": data}

    # ─────────────────────────────────────────────────────────────
    # 4. ALERTS
    # ─────────────────────────────────────────────────────────────

    async def get_alerts(self, session: AsyncSession) -> Dict:
        KEY = "dash:booking:alerts"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        now      = datetime.now(timezone.utc)
        today    = now.date()
        tomorrow = today + timedelta(days=1)
        threshold_pending = now - timedelta(hours=24)
        threshold_payment = now + timedelta(hours=2)

        # ── Alert 1: PENDING > 24 jam ─────────────────────────────
        pending_lama_res = await session.execute(
            select(
                ServiceBooking.uuid,
                ServiceBooking.booking_number,
                ServiceBooking.contact_name,
                ServiceBooking.contact_phone,
                ServiceBooking.total_price,
                ServiceBooking.created_at,
            )
            .where(
                and_(
                    ServiceBooking.status == BookingStatus.PENDING,
                    ServiceBooking.created_at <= threshold_pending,
                )
            )
            .order_by(asc(ServiceBooking.created_at))
            .limit(10)
        )
        pending_lama = [
            {
                "uuid":           str(r.uuid),
                "booking_number": r.booking_number,
                "contact_name":   r.contact_name,
                "contact_phone":  r.contact_phone,
                "total_price":    r.total_price,
                "pending_sejak":  r.created_at,
                "jam_pending":    round((now - r.created_at).total_seconds() / 3600, 1),
            }
            for r in pending_lama_res
        ]

        # ── Alert 2: Slot besok hampir penuh / penuh ─────────────
        slots_besok_res = await session.execute(
            select(
                ServiceBooking.time_slot,
                func.count(ServiceBooking.uuid).label("count"),
            )
            .where(
                and_(
                    ServiceBooking.scheduled_date == tomorrow,
                    ServiceBooking.status.in_(ACTIVE_STATUSES),
                )
            )
            .group_by(ServiceBooking.time_slot)
        )
        slot_besok = []
        for r in slots_besok_res:
            remaining = MAX_PER_SLOT - r.count
            if remaining <= 1:   # penuh atau sisa 1
                slot_besok.append({
                    "slot":      r.time_slot,
                    "label":     SLOT_LABELS.get(r.time_slot, r.time_slot),
                    "booked":    r.count,
                    "remaining": max(0, remaining),
                    "is_full":   remaining <= 0,
                })

        # ── Alert 3: Payment DP hampir expire (< 2 jam) ───────────
        payment_expire_res = await session.execute(
            select(
                ServicePayment.uuid,
                ServicePayment.order_id,
                ServicePayment.gross_amount,
                ServicePayment.expired_at,
                ServicePayment.booking_uuid,
            )
            .where(
                and_(
                    ServicePayment.status == PaymentStatus.PENDING,
                    ServicePayment.payment_type == PaymentType.DP,
                    ServicePayment.expired_at.isnot(None),
                    ServicePayment.expired_at > now,
                    ServicePayment.expired_at <= threshold_payment,
                )
            )
            .order_by(asc(ServicePayment.expired_at))
            .limit(10)
        )
        payment_expire = [
            {
                "payment_uuid":  str(r.uuid),
                "order_id":      r.order_id,
                "gross_amount":  r.gross_amount,
                "booking_uuid":  str(r.booking_uuid),
                "expired_at":    r.expired_at,
                "sisa_menit":    round((r.expired_at - now).total_seconds() / 60),
            }
            for r in payment_expire_res
        ]

        # ── Alert 4: Booking besok (reminder teknisi) ─────────────
        besok_res = await session.execute(
            select(
                ServiceBooking.uuid,
                ServiceBooking.booking_number,
                ServiceBooking.contact_name,
                ServiceBooking.contact_phone,
                ServiceBooking.address,
                ServiceBooking.city,
                ServiceBooking.time_slot,
                ServiceBooking.category,
                ServiceBooking.camera_count,
                ServiceBooking.status,
            )
            .where(
                and_(
                    ServiceBooking.scheduled_date == tomorrow,
                    ServiceBooking.status.in_([
                        BookingStatus.CONFIRMED,
                        BookingStatus.DP_PAID,
                    ]),
                )
            )
            .order_by(asc(ServiceBooking.time_slot))
        )
        booking_besok = [
            {
                "uuid":           str(r.uuid),
                "booking_number": r.booking_number,
                "contact_name":   r.contact_name,
                "contact_phone":  r.contact_phone,
                "address":        r.address,
                "city":           r.city,
                "time_slot":      r.time_slot,
                "slot_label":     SLOT_LABELS.get(r.time_slot, r.time_slot),
                "category":       r.category,
                "camera_count":   r.camera_count,
                "status":         r.status,
            }
            for r in besok_res
        ]

        data = {
            "pending_lama":       pending_lama,
            "slot_penuh_besok":   slot_besok,
            "dp_expire_soon":     payment_expire,
            "booking_besok":      booking_besok,
            # Hitung total alert yang butuh aksi
            "alert_count": (
                len(pending_lama) +
                sum(1 for s in slot_besok if s["is_full"]) +
                len(payment_expire)
            ),
        }

        await self._cache_set(KEY, data, TTL_ALERTS)
        return {"status": "success", "source": "db", "data": data}

    # ─────────────────────────────────────────────────────────────
    # 5. RECENT ACTIVITY
    # ─────────────────────────────────────────────────────────────

    async def get_recent_bookings(
        self, session: AsyncSession, limit: int = 10
    ) -> Dict:
        KEY = f"dash:booking:recent:{limit}"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "items": cached}

        rows = await session.execute(
            select(
                ServiceBooking.uuid,
                ServiceBooking.booking_number,
                ServiceBooking.contact_name,
                ServiceBooking.contact_phone,
                ServiceBooking.category,
                ServiceBooking.camera_count,
                ServiceBooking.brand,
                ServiceBooking.scheduled_date,
                ServiceBooking.time_slot,
                ServiceBooking.city,
                ServiceBooking.status,
                ServiceBooking.total_price,
                ServiceBooking.dp_amount,
                ServiceBooking.created_at,
            )
            .order_by(desc(ServiceBooking.created_at))
            .limit(limit)
        )

        items = [
            {
                "uuid":           str(r.uuid),
                "booking_number": r.booking_number,
                "contact_name":   r.contact_name,
                "contact_phone":  r.contact_phone,
                "category":       r.category,
                "camera_count":   r.camera_count,
                "brand":          r.brand,
                "scheduled_date": r.scheduled_date,
                "time_slot":      r.time_slot,
                "slot_label":     SLOT_LABELS.get(r.time_slot, r.time_slot),
                "city":           r.city,
                "status":         r.status,
                "status_label":   STATUS_LABELS.get(r.status, r.status),
                "total_price":    r.total_price,
                "dp_amount":      r.dp_amount,
                "created_at":     r.created_at,
            }
            for r in rows
        ]

        await self._cache_set(KEY, items, TTL_RECENT)
        return {"status": "success", "source": "db", "items": items}

    # ─────────────────────────────────────────────────────────────
    # 6. TODAY SNAPSHOT
    # ─────────────────────────────────────────────────────────────

    async def get_today_snapshot(self, session: AsyncSession) -> Dict:
        KEY = "dash:booking:today"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        today = datetime.now(timezone.utc).date()

        rows = await session.execute(
            select(
                ServiceBooking.uuid,
                ServiceBooking.booking_number,
                ServiceBooking.contact_name,
                ServiceBooking.contact_phone,
                ServiceBooking.address,
                ServiceBooking.city,
                ServiceBooking.category,
                ServiceBooking.camera_count,
                ServiceBooking.brand,
                ServiceBooking.time_slot,
                ServiceBooking.status,
                ServiceBooking.total_price,
                ServiceBooking.dp_amount,
                ServiceBooking.distance_km,
            )
            .where(ServiceBooking.scheduled_date == today)
            .order_by(asc(ServiceBooking.time_slot), asc(ServiceBooking.created_at))
        )
        bookings = rows.all()

        # Hitung slot summary
        slot_count: Dict[str, int] = {}
        for b in bookings:
            if b.status in ACTIVE_STATUSES:
                slot_count[b.time_slot] = slot_count.get(b.time_slot, 0) + 1

        slot_summary = {
            slot: {
                "label":     label,
                "booked":    slot_count.get(slot, 0),
                "remaining": max(0, MAX_PER_SLOT - slot_count.get(slot, 0)),
                "is_full":   slot_count.get(slot, 0) >= MAX_PER_SLOT,
            }
            for slot, label in SLOT_LABELS.items()
        }

        items = [
            {
                "uuid":           str(b.uuid),
                "booking_number": b.booking_number,
                "contact_name":   b.contact_name,
                "contact_phone":  b.contact_phone,
                "address":        b.address,
                "city":           b.city,
                "category":       b.category,
                "camera_count":   b.camera_count,
                "brand":          b.brand,
                "time_slot":      b.time_slot,
                "slot_label":     SLOT_LABELS.get(b.time_slot, b.time_slot),
                "status":         b.status,
                "status_label":   STATUS_LABELS.get(b.status, b.status),
                "total_price":    b.total_price,
                "dp_amount":      b.dp_amount,
                "distance_km":    b.distance_km,
            }
            for b in bookings
        ]

        # Ringkasan cepat
        active_today    = sum(1 for b in bookings if b.status in ACTIVE_STATUSES)
        confirmed_today = sum(1 for b in bookings if b.status == BookingStatus.CONFIRMED)
        dp_paid_today   = sum(1 for b in bookings if b.status == BookingStatus.DP_PAID)
        progress_today  = sum(1 for b in bookings if b.status == BookingStatus.PROGRESS)

        data = {
            "date":             today.isoformat(),
            "total_today":      len(bookings),
            "active_today":     active_today,
            "confirmed_today":  confirmed_today,
            "dp_paid_today":    dp_paid_today,
            "progress_today":   progress_today,
            "slot_summary":     slot_summary,
            "bookings":         items,
        }

        await self._cache_set(KEY, data, TTL_TODAY)
        return {"status": "success", "source": "db", "data": data}

    # ─────────────────────────────────────────────────────────────
    # 7. PAYMENT SUMMARY
    # ─────────────────────────────────────────────────────────────

    async def get_payment_summary(self, session: AsyncSession) -> Dict:
        KEY = "dash:booking:payment"
        cached = await self._cache_get(KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        # Agregat semua payment dalam satu query
        agg = await session.execute(
            select(
                ServicePayment.payment_type,
                ServicePayment.status,
                func.count(ServicePayment.uuid).label("count"),
                func.sum(ServicePayment.gross_amount).label("total"),
            )
            .group_by(ServicePayment.payment_type, ServicePayment.status)
        )
        rows = agg.all()

        # Bangun lookup: (payment_type, status) → {count, total}
        bucket: Dict[tuple, Dict] = {}
        for r in rows:
            bucket[(r.payment_type, r.status)] = {
                "count": r.count or 0,
                "total": int(r.total or 0),
            }

        def _get(ptype: PaymentType, pstatus: PaymentStatus) -> Dict:
            return bucket.get((ptype, pstatus), {"count": 0, "total": 0})

        dp_success  = _get(PaymentType.DP,    PaymentStatus.SUCCESS)
        dp_pending  = _get(PaymentType.DP,    PaymentStatus.PENDING)
        dp_expire   = _get(PaymentType.DP,    PaymentStatus.EXPIRE)
        dp_cancel   = _get(PaymentType.DP,    PaymentStatus.CANCEL)
        dp_failed   = _get(PaymentType.DP,    PaymentStatus.FAILED)

        lunas_success = _get(PaymentType.LUNAS, PaymentStatus.SUCCESS)
        lunas_pending = _get(PaymentType.LUNAS, PaymentStatus.PENDING)
        lunas_expire  = _get(PaymentType.LUNAS, PaymentStatus.EXPIRE)

        grand_total = dp_success["total"] + lunas_success["total"]

        # Ambil payment PENDING yang masih aktif & butuh follow-up
        pending_list_res = await session.execute(
            select(
                ServicePayment.uuid,
                ServicePayment.order_id,
                ServicePayment.payment_type,
                ServicePayment.gross_amount,
                ServicePayment.expired_at,
                ServicePayment.booking_uuid,
                ServicePayment.created_at,
            )
            .where(ServicePayment.status == PaymentStatus.PENDING)
            .order_by(asc(ServicePayment.expired_at))
            .limit(20)
        )
        pending_list = [
            {
                "payment_uuid": str(r.uuid),
                "order_id":     r.order_id,
                "payment_type": r.payment_type,
                "gross_amount": r.gross_amount,
                "booking_uuid": str(r.booking_uuid),
                "expired_at":   r.expired_at,
                "created_at":   r.created_at,
            }
            for r in pending_list_res
        ]

        data = {
            "dp": {
                "success_count": dp_success["count"],
                "success_total": dp_success["total"],
                "pending_count": dp_pending["count"],
                "expire_count":  dp_expire["count"],
                "cancel_count":  dp_cancel["count"],
                "failed_count":  dp_failed["count"],
            },
            "lunas": {
                "success_count": lunas_success["count"],
                "success_total": lunas_success["total"],
                "pending_count": lunas_pending["count"],
                "expire_count":  lunas_expire["count"],
            },
            "grand_total_terkumpul": grand_total,
            "dp_terkumpul":          dp_success["total"],
            "lunas_terkumpul":       lunas_success["total"],
            "payment_pending_list":  pending_list,
        }

        await self._cache_set(KEY, data, TTL_PAYMENT)
        return {"status": "success", "source": "db", "data": data}