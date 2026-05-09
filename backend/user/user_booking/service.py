"""
service.py — User Booking Dashboard Service
Redis Dragonfly optimized: cache per-user, invalidate on status change
"""
import json
import logging
from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select, or_, and_, func
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.data.jasa.model import (
    ServiceBooking, ServicePayment,
    BookingStatus, PaymentStatus, PaymentType,
)
from .schema import (
    BookingCard, BookingDetail, BookingAction,
    PaymentSummary, PaginatedBookings,
    UserBookingStats, UserDashboardResponse,
    BookingSortBy, BookingFilterStatus,
)

logger = logging.getLogger(__name__)

# ── Cache constants ────────────────────────────────────────────────
USER_STATS_TTL   = 120   # 2 menit
USER_LIST_TTL    = 60    # 1 menit
USER_DETAIL_TTL  = 30    # 30 detik (sering berubah saat payment)

# Status metadata
STATUS_META: Dict[str, Dict[str, str]] = {
    "pending":   {"label": "Menunggu Konfirmasi", "color": "amber"},
    "confirmed": {"label": "Dikonfirmasi",        "color": "blue"},
    "dp_paid":   {"label": "DP Diterima",         "color": "green"},
    "progress":  {"label": "Sedang Dikerjakan",   "color": "purple"},
    "done":      {"label": "Selesai",             "color": "green"},
    "lunas":     {"label": "Lunas",               "color": "green"},
    "cancel":    {"label": "Dibatalkan",          "color": "red"},
}

ACTIVE_STATUSES = [
    BookingStatus.PENDING, BookingStatus.CONFIRMED,
    BookingStatus.DP_PAID, BookingStatus.PROGRESS,
]


def _get_redis():
    from backend.db.redis import get_redis_token
    return get_redis_token()


def _scheduled_label(d: date) -> str:
    delta = (d - date.today()).days
    if delta == 0:   return "Hari ini"
    if delta == 1:   return "Besok"
    if delta < 0:    return f"{abs(delta)} hari lalu"
    if delta < 7:    return f"{delta} hari lagi"
    return d.strftime("%-d %b %Y")


def _resolve_action(
    booking: ServiceBooking,
    payments: List[ServicePayment],
) -> BookingAction:
    """
    Tentukan CTA utama yang bisa dilakukan user sekarang.
    Cek payment yang sudah ada dulu — jika pending & punya URL, resume.
    """
    status = booking.status

    if status == BookingStatus.CONFIRMED:
        # Cek payment DP yang masih pending
        pending_dp = next(
            (p for p in payments
             if p.payment_type == PaymentType.DP
             and p.status == PaymentStatus.PENDING
             and p.payment_url
             and p.expired_at
             and p.expired_at > datetime.now(timezone.utc)),
            None
        )
        if pending_dp:
            return BookingAction(
                action="pay_dp",
                label=f"Lanjut Bayar DP",
                amount=pending_dp.gross_amount,
                payment_url=pending_dp.payment_url,
                booking_uuid=booking.uuid,
            )
        return BookingAction(
            action="pay_dp",
            label=f"Bayar DP",
            amount=booking.dp_amount,
            booking_uuid=booking.uuid,
        )

    if status == BookingStatus.DONE:
        pending_lunas = next(
            (p for p in payments
             if p.payment_type == PaymentType.LUNAS
             and p.status == PaymentStatus.PENDING
             and p.payment_url
             and p.expired_at
             and p.expired_at > datetime.now(timezone.utc)),
            None
        )
        if pending_lunas:
            return BookingAction(
                action="pay_lunas",
                label="Lanjut Bayar Pelunasan",
                amount=pending_lunas.gross_amount,
                payment_url=pending_lunas.payment_url,
                booking_uuid=booking.uuid,
            )
        return BookingAction(
            action="pay_lunas",
            label="Bayar Pelunasan",
            amount=booking.remaining_amount,
            booking_uuid=booking.uuid,
        )

    if status in (BookingStatus.LUNAS, BookingStatus.DP_PAID, BookingStatus.PROGRESS):
        return BookingAction(action="view_receipt", label="Lihat Detail")

    return BookingAction(action="none", label="Lihat Detail")


def _build_payment_summaries(payments: List[ServicePayment]) -> List[PaymentSummary]:
    return [
        PaymentSummary(
            uuid=p.uuid,
            order_id=p.order_id,
            payment_type=p.payment_type,
            gross_amount=p.gross_amount,
            status=p.status,
            payment_token=p.payment_token,
            payment_url=p.payment_url,
            paid_at=p.paid_at,
            expired_at=p.expired_at,
            created_at=p.created_at,
        )
        for p in sorted(payments, key=lambda x: x.created_at, reverse=True)
    ]


def _booking_to_card(
    booking: ServiceBooking,
    payments: List[ServicePayment],
) -> BookingCard:
    meta   = STATUS_META.get(booking.status, {"label": booking.status, "color": "gray"})
    action = _resolve_action(booking, payments)
    has_pending = any(
        p.status == PaymentStatus.PENDING and p.payment_url
        for p in payments
    )
    return BookingCard(
        uuid=booking.uuid,
        booking_number=booking.booking_number,
        category=booking.category,
        camera_count=booking.camera_count,
        brand=booking.brand,
        addons=booking.addons,
        scheduled_date=booking.scheduled_date,
        time_slot=booking.time_slot,
        address=booking.address,
        city=booking.city,
        distance_km=booking.distance_km,
        status=booking.status,
        status_label=meta["label"],
        status_color=meta["color"],
        total_price=booking.total_price,
        dp_amount=booking.dp_amount,
        remaining_amount=booking.remaining_amount,
        dp_percentage=booking.dp_percentage,
        action=action,
        has_pending_payment=has_pending,
        created_at=booking.created_at,
        scheduled_label=_scheduled_label(booking.scheduled_date),
    )


def _booking_to_detail(
    booking: ServiceBooking,
    payments: List[ServicePayment],
) -> BookingDetail:
    meta   = STATUS_META.get(booking.status, {"label": booking.status, "color": "gray"})
    action = _resolve_action(booking, payments)
    return BookingDetail(
        uuid=booking.uuid,
        booking_number=booking.booking_number,
        category=booking.category,
        camera_count=booking.camera_count,
        brand=booking.brand,
        addons=booking.addons,
        scheduled_date=booking.scheduled_date,
        time_slot=booking.time_slot,
        address=booking.address,
        district=booking.district,
        city=booking.city,
        distance_km=booking.distance_km,
        contact_name=booking.contact_name,
        contact_phone=booking.contact_phone,
        contact_notes=booking.contact_notes,
        device_price=booking.device_price,
        service_price=booking.service_price,
        addon_price=booking.addon_price,
        transport_fee=booking.transport_fee,
        total_price=booking.total_price,
        dp_percentage=booking.dp_percentage,
        dp_amount=booking.dp_amount,
        remaining_amount=booking.remaining_amount,
        price_breakdown=booking.price_breakdown,
        status=booking.status,
        status_label=meta["label"],
        status_color=meta["color"],
        action=action,
        payments=_build_payment_summaries(payments),
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


class UserBookingService:

    # ── Cache helpers ──────────────────────────────────────────────

    @staticmethod
    def _cache_key_list(user_uuid: UUID, page: int, size: int,
                        status: str, sort: str, q: str) -> str:
        return f"ubk:list:{user_uuid}:{status}:{sort}:{q or ''}:{page}:{size}"

    @staticmethod
    def _cache_key_stats(user_uuid: UUID) -> str:
        return f"ubk:stats:{user_uuid}"

    @staticmethod
    def _cache_key_detail(booking_uuid: UUID) -> str:
        return f"ubk:detail:{booking_uuid}"

    async def _invalidate_user_cache(self, user_uuid: UUID) -> None:
        """Hapus semua cache list & stats user setelah ada perubahan."""
        r = _get_redis()
        cursor = 0
        keys: List[str] = []
        while True:
            cursor, found = await r.scan(cursor, match=f"ubk:*:{user_uuid}*", count=200)
            keys.extend(found)
            if cursor == 0:
                break
        if keys:
            await r.delete(*keys)

    async def invalidate_booking_detail(self, booking_uuid: UUID) -> None:
        await _get_redis().delete(self._cache_key_detail(booking_uuid))

    # ── Core query ─────────────────────────────────────────────────

    async def _fetch_bookings_with_payments(
        self,
        session: AsyncSession,
        user_uuid: UUID,
        status_filter: BookingFilterStatus,
        sort_by: BookingSortBy,
        q: Optional[str],
        page: int,
        size: int,
    ) -> Tuple[List[Tuple[ServiceBooking, List[ServicePayment]]], int]:
        """
        Single round-trip: ambil bookings + payments sekaligus.
        Avoid N+1 dengan subquery payment.
        """
        # ── Base statement ─────────────────────────────────────────
        stmt = select(ServiceBooking).where(
            ServiceBooking.user_uuid == user_uuid
        )

        # ── Filter status ──────────────────────────────────────────
        if status_filter != BookingFilterStatus.ALL:
            stmt = stmt.where(ServiceBooking.status == status_filter.value)

        # ── Full-text search sederhana (booking number / kota / brand) ─
        if q:
            q_like = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    ServiceBooking.booking_number.ilike(q_like),
                    ServiceBooking.city.ilike(q_like),
                    ServiceBooking.brand.ilike(q_like),
                    ServiceBooking.category.ilike(q_like),
                    ServiceBooking.address.ilike(q_like),
                )
            )

        # ── Sorting ────────────────────────────────────────────────
        sort_map = {
            BookingSortBy.NEWEST:     ServiceBooking.created_at.desc(),
            BookingSortBy.OLDEST:     ServiceBooking.created_at.asc(),
            BookingSortBy.SCHEDULED:  ServiceBooking.scheduled_date.asc(),
            BookingSortBy.TOTAL_HIGH: ServiceBooking.total_price.desc(),
            BookingSortBy.TOTAL_LOW:  ServiceBooking.total_price.asc(),
        }
        stmt = stmt.order_by(sort_map.get(sort_by, ServiceBooking.created_at.desc()))

        # ── Count total (before pagination) ───────────────────────
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        # ── Paginate ───────────────────────────────────────────────
        stmt = stmt.offset((page - 1) * size).limit(size)
        bookings_result = await session.exec(stmt)
        bookings = list(bookings_result.all())

        if not bookings:
            return [], total

        # ── Batch fetch payments — 1 query untuk semua booking ────
        booking_uuids = [b.uuid for b in bookings]
        pay_stmt = select(ServicePayment).where(
            ServicePayment.booking_uuid.in_(booking_uuids)
        ).order_by(ServicePayment.created_at.desc())
        pay_result = await session.exec(pay_stmt)
        all_payments = list(pay_result.all())

        # Group payments by booking_uuid
        pay_map: Dict[UUID, List[ServicePayment]] = {}
        for p in all_payments:
            pay_map.setdefault(p.booking_uuid, []).append(p)

        return [(b, pay_map.get(b.uuid, [])) for b in bookings], total

    # ── Public methods ─────────────────────────────────────────────

    async def get_dashboard(
        self,
        session: AsyncSession,
        user_uuid: UUID,
        status: BookingFilterStatus = BookingFilterStatus.ALL,
        sort: BookingSortBy = BookingSortBy.NEWEST,
        q: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> UserDashboardResponse:
        r = _get_redis()

        # ── Stats (cached) ─────────────────────────────────────────
        stats_key = self._cache_key_stats(user_uuid)
        stats_raw = await r.get(stats_key)
        stats: Optional[UserBookingStats] = None
        if stats_raw:
            try:
                stats = UserBookingStats(**json.loads(stats_raw))
            except Exception:
                stats = None

        if not stats:
            stats = await self._compute_stats(session, user_uuid)
            await r.set(stats_key, stats.model_dump_json(), ex=USER_STATS_TTL)

        # ── List (cached) ──────────────────────────────────────────
        list_key = self._cache_key_list(user_uuid, page, size, status, sort, q or "")
        list_raw = await r.get(list_key)
        paginated: Optional[PaginatedBookings] = None
        if list_raw:
            try:
                paginated = PaginatedBookings(**json.loads(list_raw))
            except Exception:
                paginated = None

        if not paginated:
            pairs, total = await self._fetch_bookings_with_payments(
                session, user_uuid, status, sort, q, page, size
            )
            cards = [_booking_to_card(b, payments) for b, payments in pairs]
            total_pages = max(1, (total + size - 1) // size)
            paginated = PaginatedBookings(
                items=cards,
                total=total,
                page=page,
                size=size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            )
            await r.set(list_key, paginated.model_dump_json(), ex=USER_LIST_TTL)

        return UserDashboardResponse(stats=stats, bookings=paginated)

    async def get_booking_detail(
        self,
        session: AsyncSession,
        booking_uuid: UUID,
        user_uuid: UUID,
    ) -> BookingDetail:
        r = _get_redis()
        detail_key = self._cache_key_detail(booking_uuid)

        # Cache check
        cached = await r.get(detail_key)
        if cached:
            try:
                detail = BookingDetail(**json.loads(cached))
                # Pastikan detail milik user yang request
                if str(detail.uuid) == str(booking_uuid):
                    return detail
            except Exception:
                pass

        # DB fetch
        booking_result = await session.exec(
            select(ServiceBooking).where(
                ServiceBooking.uuid == booking_uuid,
                ServiceBooking.user_uuid == user_uuid,  # security: user hanya bisa lihat miliknya
            )
        )
        booking = booking_result.first()
        if not booking:
            raise HTTPException(404, "Booking tidak ditemukan")

        pay_result = await session.exec(
            select(ServicePayment)
            .where(ServicePayment.booking_uuid == booking_uuid)
            .order_by(ServicePayment.created_at.desc())
        )
        payments = list(pay_result.all())

        detail = _booking_to_detail(booking, payments)

        # Jangan cache terlalu lama jika status aktif (sering berubah)
        ttl = 15 if booking.status in [s.value for s in ACTIVE_STATUSES] else USER_DETAIL_TTL
        await r.set(detail_key, detail.model_dump_json(), ex=ttl)

        return detail

    async def get_booking_by_number(
        self,
        session: AsyncSession,
        booking_number: str,
        user_uuid: UUID,
    ) -> BookingDetail:
        booking_result = await session.exec(
            select(ServiceBooking).where(
                ServiceBooking.booking_number == booking_number,
                ServiceBooking.user_uuid == user_uuid,
            )
        )
        booking = booking_result.first()
        if not booking:
            raise HTTPException(404, "Booking tidak ditemukan")

        return await self.get_booking_detail(session, booking.uuid, user_uuid)

    async def _compute_stats(
        self, session: AsyncSession, user_uuid: UUID
    ) -> UserBookingStats:
        """Hitung stats user dari DB — dipanggil saat cache miss."""
        # Semua booking user
        all_result = await session.exec(
            select(ServiceBooking).where(ServiceBooking.user_uuid == user_uuid)
        )
        bookings = list(all_result.all())

        if not bookings:
            return UserBookingStats(
                total=0, active=0, done=0, cancel=0,
                total_spent=0, pending_payment=0
            )

        booking_uuids = [b.uuid for b in bookings]

        # Semua payment user (batch)
        pay_result = await session.exec(
            select(ServicePayment).where(
                ServicePayment.booking_uuid.in_(booking_uuids)
            )
        )
        all_payments = list(pay_result.all())

        active_statuses = {s.value for s in ACTIVE_STATUSES}
        total_spent = sum(
            p.gross_amount for p in all_payments
            if p.status == PaymentStatus.SUCCESS
        )

        # Hitung tagihan pending: DP belum dibayar (confirmed) + Lunas belum dibayar (done)
        pending_payment = 0
        pay_by_booking: Dict[UUID, List[ServicePayment]] = {}
        for p in all_payments:
            pay_by_booking.setdefault(p.booking_uuid, []).append(p)

        for b in bookings:
            pays = pay_by_booking.get(b.uuid, [])
            has_success_dp = any(
                p.payment_type == PaymentType.DP and p.status == PaymentStatus.SUCCESS
                for p in pays
            )
            has_success_lunas = any(
                p.payment_type == PaymentType.LUNAS and p.status == PaymentStatus.SUCCESS
                for p in pays
            )
            if b.status == BookingStatus.CONFIRMED and not has_success_dp:
                pending_payment += b.dp_amount
            if b.status == BookingStatus.DONE and not has_success_lunas:
                pending_payment += b.remaining_amount

        return UserBookingStats(
            total=len(bookings),
            active=sum(1 for b in bookings if b.status in active_statuses),
            done=sum(1 for b in bookings if b.status == BookingStatus.LUNAS),
            cancel=sum(1 for b in bookings if b.status == BookingStatus.CANCEL),
            total_spent=total_spent,
            pending_payment=pending_payment,
        )