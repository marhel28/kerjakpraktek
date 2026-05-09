"""
router.py — User Booking Dashboard
GET  /user/bookings              → list + stats (dashboard)
GET  /user/bookings/{uuid}       → detail booking
GET  /user/bookings/number/{no}  → detail by booking number
POST /user/bookings/{uuid}/pay   → buat / resume payment
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.db.main import get_session
from backend.db.redis import get_redis_token
from backend.auth.depedence import get_current_user
from backend.auth.model import User

from .schema import (
    UserDashboardResponse, BookingDetail,
    BookingSortBy, BookingFilterStatus,
)
from .service import UserBookingService

# Import payment service dari jasa module
from backend.data.jasa.service import PaymentService, MidtransService, BookingService
from backend.data.jasa.schema import CreatePaymentRequest
from backend.data.jasa.model import PaymentType
from backend.config import Config
import os

router = APIRouter()
svc = UserBookingService()

_midtrans = MidtransService(
    server_key=os.getenv("MIDTRANS_SERVER_KEY", Config.MIDTRANS_SERVER_KEY),
    is_production=os.getenv("MIDTRANS_PRODUCTION", "false").lower() == "true",
)
payment_svc = PaymentService(_midtrans)

RATE_LIMIT_TTL = 60
RATE_LIMIT_MAX = 20   # lebih longgar karena halaman dashboard


async def _rate_limit(request: Request, user_uuid: UUID, prefix: str = "ubk") -> None:
    r = get_redis_token()
    key = f"rl:{prefix}:{user_uuid}"
    cnt = await r.incr(key)
    if cnt == 1:
        await r.expire(key, RATE_LIMIT_TTL)
    if cnt > RATE_LIMIT_MAX:
        raise HTTPException(429, "Terlalu banyak permintaan.")


# ══════════════════════════════════════════════════════════════════
# DASHBOARD — List + Stats
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/user/bookings",
    response_model=UserDashboardResponse,
    tags=["User Booking"],
    summary="Dashboard booking user (stats + list + filter + search)",
)
async def user_dashboard(
    # ── Filter ────────────────────────────────────────────────────
    status: BookingFilterStatus = Query(
        BookingFilterStatus.ALL,
        description="Filter status: all | pending | confirmed | dp_paid | progress | done | lunas | cancel"
    ),
    sort: BookingSortBy = Query(
        BookingSortBy.NEWEST,
        description="Urutan: newest | oldest | scheduled | total_high | total_low"
    ),
    q: Optional[str] = Query(
        None,
        min_length=2,
        max_length=100,
        description="Cari: nomor booking, kota, brand, kategori, alamat"
    ),
    # ── Pagination ─────────────────────────────────────────────────
    page: int = Query(1, ge=1, description="Nomor halaman"),
    size: int = Query(10, ge=1, le=50, description="Item per halaman"),
    # ── Auth ───────────────────────────────────────────────────────
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """
    Dashboard lengkap user:
    - Stats (total, aktif, selesai, tagihan pending)
    - List booking dengan filter status & sort
    - Search by nomor booking / kota / brand / kategori
    - Setiap item sudah include `action` (CTA) + link bayar jika ada

    Cache Redis per user+filter: 1 menit.
    Stats cache: 2 menit.
    """
    await _rate_limit(request, current_user.uuid)
    return await svc.get_dashboard(
        session=session,
        user_uuid=current_user.uuid,
        status=status,
        sort=sort,
        q=q,
        page=page,
        size=size,
    )


# ══════════════════════════════════════════════════════════════════
# DETAIL — By UUID
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/user/bookings/{booking_uuid}",
    response_model=BookingDetail,
    tags=["User Booking"],
    summary="Detail booking lengkap by UUID",
)
async def user_booking_detail(
    booking_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Full detail: pricing breakdown, semua payment, status, CTA.
    Jika status CONFIRMED/DONE + ada payment pending → `action.payment_url` sudah terisi.
    Cache 15 detik (status aktif) / 30 detik (status final).
    """
    return await svc.get_booking_detail(session, booking_uuid, current_user.uuid)


# ══════════════════════════════════════════════════════════════════
# DETAIL — By Booking Number
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/user/bookings/number/{booking_number}",
    response_model=BookingDetail,
    tags=["User Booking"],
    summary="Detail booking by nomor (BK-YYYYMMDD-XXXXXX)",
)
async def user_booking_by_number(
    booking_number: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await svc.get_booking_by_number(session, booking_number, current_user.uuid)


# ══════════════════════════════════════════════════════════════════
# PAY — Buat / resume payment untuk booking user sendiri
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/user/bookings/{booking_uuid}/pay",
    tags=["User Booking"],
    summary="Buat atau resume payment (DP / Pelunasan)",
)
async def user_pay_booking(
    booking_uuid: UUID,
    payment_type: PaymentType = Query(..., description="dp | lunas"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """
    Flow:
    1. Validasi booking milik user + status sesuai
    2. Cek payment pending yang masih valid → kembalikan jika ada (resume)
    3. Jika tidak ada / expired → buat transaksi Midtrans baru
    4. Return payment_token + payment_url

    Frontend buka payment_url di tab baru / Snap popup.
    """
    await _rate_limit(request, current_user.uuid, prefix="pay")

    # Validasi kepemilikan booking sebelum buat payment
    await svc.get_booking_detail(session, booking_uuid, current_user.uuid)

    req = CreatePaymentRequest(
        booking_uuid=booking_uuid,
        payment_type=payment_type,
    )
    payment = await payment_svc.create_payment(req, session)

    # Invalidate cache detail booking (payment berubah)
    await svc.invalidate_booking_detail(booking_uuid)
    # Invalidate stats + list
    await svc._invalidate_user_cache(current_user.uuid)

    return {
        "status":        "ok",
        "order_id":      payment.order_id,
        "payment_type":  payment.payment_type,
        "gross_amount":  payment.gross_amount,
        "payment_token": payment.payment_token,
        "payment_url":   payment.payment_url,   # ← link langsung ke Midtrans
        "expired_at":    payment.expired_at,
    }


# ══════════════════════════════════════════════════════════════════
# STATS ONLY — Ringan, untuk notification badge
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/user/bookings/stats/summary",
    tags=["User Booking"],
    summary="Stats ringkas (untuk badge notifikasi di navbar)",
)
async def user_booking_stats_only(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint ringan hanya untuk stats.
    Dipakai navbar badge: total aktif + total tagihan pending.
    Cache 2 menit.
    """
    r = get_redis_token()
    stats_key = svc._cache_key_stats(current_user.uuid)
    cached = await r.get(stats_key)
    if cached:
        import json
        return json.loads(cached)

    stats = await svc._compute_stats(session, current_user.uuid)
    await r.set(stats_key, stats.model_dump_json(), ex=120)
    return stats