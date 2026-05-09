"""
dashboard_transaksi_routes.py
──────────────────────────────
GET /admin/dashboard/summary          — KPI cards utama (revenue, order, user)
GET /admin/dashboard/revenue-chart    — Chart revenue harian / mingguan / bulanan
GET /admin/dashboard/activity         — Recent activity feed (transaksi terbaru)
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.db.main import get_session
from backend.auth.depedence import get_admin
from .service import TransaksiDashboardService

router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin Dashboard Transaksi"],
)
_svc = TransaksiDashboardService()


# ── 1. Summary / KPI Cards ─────────────────────────────────────────
@router.get("/summary")
async def dashboard_summary(
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    KPI cards utama dashboard:

    Revenue
    ─────────────────────────────
    - total_revenue          : sum gross_amount status settlement/capture
    - revenue_today          : revenue hari ini
    - revenue_this_week      : revenue 7 hari terakhir
    - revenue_this_month     : revenue bulan berjalan

    Orders
    ─────────────────────────────
    - total_orders           : semua transaksi
    - orders_today           : transaksi hari ini
    - pending_payment_count  : status pending_payment (belum bayar)
    - settlement_count       : status settlement (sukses)
    - cancel_expire_count    : cancel + expire + deny (gagal)

    Shipping
    ─────────────────────────────
    - processing_shipment    : shipment status PROCESSING (sudah bayar, belum kirim)
    - shipped_count          : shipment status SHIPPED
    - delivered_count        : shipment status DELIVERED

    Produk
    ─────────────────────────────
    - total_items_sold       : sum quantity dari TransactionItem (settlement saja)
    - avg_order_value        : rata-rata gross_amount (settlement)
    - total_shipping_cost    : total ongkos kirim terkumpul

    TTL Redis: 60 s
    """
    return await _svc.get_summary(session)


# ── 2. Revenue Chart ───────────────────────────────────────────────
@router.get("/revenue-chart")
async def dashboard_revenue_chart(
    range: str = Query(
        "7d",
        description="Rentang waktu: '7d' (7 hari), '30d' (30 hari), '12m' (12 bulan)",
        pattern="^(7d|30d|12m)$",
    ),
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Data chart revenue berdasarkan rentang:
    - 7d  → 7 hari terakhir, label 'Rab 1 Jan'
    - 30d → 30 hari terakhir, label '1 Jan'
    - 12m → 12 bulan terakhir, label 'Jan 2025'

    Setiap titik mengandung:
    { label, period, gross_revenue, net_revenue, order_count, avg_order }

    gross_revenue = sum gross_amount (settlement)
    net_revenue   = gross_revenue - sum shipping_cost
    TTL Redis: 120 s per range
    """
    return await _svc.get_revenue_chart(session, range=range)


# ── 3. Activity Feed ───────────────────────────────────────────────
@router.get("/activity")
async def dashboard_activity(
    limit: int = Query(15, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Recent activity feed — transaksi terbaru lintas semua status,
    diurut created_at DESC.

    Tiap item mengandung:
    { order_id, user_id, status, gross_amount, payment_type,
      item_count, first_product_name, shipment_status,
      courier_name, created_at }

    TTL Redis: 30 s
    """
    return await _svc.get_activity(session, limit=limit)