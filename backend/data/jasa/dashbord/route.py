"""
dashboard_booking_routes.py
───────────────────────────
GET /admin/dashboard/booking/kpi       — KPI Cards
GET /admin/dashboard/booking/revenue   — Chart Revenue (harian / bulanan)
GET /admin/dashboard/booking/status    — Chart distribusi status
GET /admin/dashboard/booking/alerts    — Alert: outstanding & kritis
GET /admin/dashboard/booking/recent    — Recent activity
GET /admin/dashboard/booking/today     — Booking hari ini + slot
GET /admin/dashboard/booking/payment   — Summary payment DP & Lunas
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.db.main import get_session
from backend.auth.depedence import get_admin
from .service import BookingDashboardService

router = APIRouter(
    prefix="/admin/dashboard/booking",
    tags=["Admin Dashboard Booking"],
)
_svc = BookingDashboardService()


# ── 1. KPI Cards ───────────────────────────────────────────────────
@router.get("/kpi")
async def dashboard_booking_kpi(
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    KPI utama dashboard booking:
    - total_booking, booking_bulan_ini, booking_hari_ini
    - pending_count, confirmed_count, progress_count
    - total_revenue (LUNAS + DONE), revenue_bulan_ini
    - dp_terkumpul (DP_PAID + PROGRESS + DONE + LUNAS)
    - conversion_rate  (confirmed / total × 100)
    - cancel_rate      (cancel / total × 100)
    TTL Redis: 60 s
    """
    return await _svc.get_kpi(session)


# ── 2. Revenue Chart ───────────────────────────────────────────────
@router.get("/revenue")
async def dashboard_booking_revenue(
    mode: str = Query("daily", description="'daily' (30 hari) atau 'monthly' (12 bulan)"),
    _: any = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    """
    Data chart revenue:
    - mode=daily   → 30 hari terakhir (label: 'DD MMM')
    - mode=monthly → 12 bulan terakhir (label: 'MMM YYYY')

    Setiap titik: { label, total_revenue, dp_revenue, booking_count }
    TTL Redis: 120 s
    """
    if mode not in ("daily", "monthly"):
        mode = "daily"
    return await _svc.get_revenue_chart(session, mode=mode)


# ── 3. Status Distribution Chart ───────────────────────────────────
@router.get("/status")
async def dashboard_booking_status(
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Distribusi booking per status (untuk pie / bar chart).
    Return: list { status, label, count, percentage }
    TTL Redis: 60 s
    """
    return await _svc.get_status_distribution(session)


# ── 4. Alerts ──────────────────────────────────────────────────────
@router.get("/alerts")
async def dashboard_booking_alerts(
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Alert yang perlu tindakan admin:
    - pending_lama     : booking PENDING > 24 jam tanpa respons
    - slot_penuh_besok : slot besok yang sudah ≥ 3 booking
    - dp_expire_soon   : payment DP pending yang < 2 jam expired
    - booking_besok    : daftar booking terjadwal besok (reminder teknisi)
    TTL Redis: 30 s (fresh, karena operasional)
    """
    return await _svc.get_alerts(session)


# ── 5. Recent Activity ─────────────────────────────────────────────
@router.get("/recent")
async def dashboard_booking_recent(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Booking terbaru (created_at DESC).
    Tiap item: uuid, booking_number, contact_name, category,
               status, total_price, scheduled_date, created_at
    TTL Redis: 30 s
    """
    return await _svc.get_recent_bookings(session, limit=limit)


# ── 6. Today ───────────────────────────────────────────────────────
@router.get("/today")
async def dashboard_booking_today(
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Snapshot booking HARI INI:
    - bookings   : list booking terjadwal hari ini (semua slot)
    - slot_summary: { "08:00-11:00": {count, remaining}, ... }
    - total_today, confirmed_today, dp_paid_today
    TTL Redis: 30 s
    """
    return await _svc.get_today_snapshot(session)


# ── 7. Payment Summary ─────────────────────────────────────────────
@router.get("/payment")
async def dashboard_booking_payment(
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Ringkasan status semua payment Midtrans:
    - dp_pending_count / dp_success_count / dp_expire_count
    - lunas_pending_count / lunas_success_count
    - total_dp_terkumpul, total_lunas_terkumpul
    - grand_total_terkumpul
    - payment_pending_list: payment yang masih menggantung (butuh follow-up)
    TTL Redis: 60 s
    """
    return await _svc.get_payment_summary(session)