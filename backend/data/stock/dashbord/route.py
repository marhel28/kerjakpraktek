"""
GET /admin/dashboard/stock/summary       — KPI cards (total, active, low, out)
GET /admin/dashboard/stock/low           — produk stok hampir habis
GET /admin/dashboard/stock/out           — produk stok = 0
GET /admin/dashboard/stock/distribution  — data chart distribusi kategori / brand
GET /admin/dashboard/stock/top-selling   — top terjual
GET /admin/dashboard/stock/recent        — produk terbaru
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.db.main import get_session
from backend.auth.depedence import get_admin
from .service import StockDashboardService

router = APIRouter(prefix="/admin/dashboard/stock", tags=["Admin Dashboard Stock"])
_svc = StockDashboardService()


# ── 1. Summary / KPI Cards ─────────────────────────────────────────
@router.get("/summary")
async def dashboard_summary(
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Kartu KPI utama:
    - total_products, active_products, inactive_products
    - low_stock_count  (stok ≤ threshold)
    - out_of_stock_count (stok = 0)
    - total_revenue_potential (sum online_price * stok aktif)
    - total_terjual
    TTL Redis: 60 detik
    """
    return await _svc.get_summary(session)


# ── 2. Low Stock ───────────────────────────────────────────────────
@router.get("/low")
async def dashboard_low_stock(
    threshold: int = Query(5, ge=1, description="Batas stok dianggap 'hampir habis'"),
    size: int = Query(20, le=100),
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Produk dengan 1 ≤ stok ≤ threshold (default 5), terurut stok ASC.
    TTL Redis: 60 detik  (key menyertakan threshold)
    """
    return await _svc.get_low_stock(session, threshold=threshold, size=size)


# ── 3. Out of Stock ────────────────────────────────────────────────
@router.get("/out")
async def dashboard_out_of_stock(
    page: int = Query(1, ge=1),
    size: int = Query(20, le=100),
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Produk dengan stok = 0, terurut terjual DESC (yang paling laris dulu).
    TTL Redis: 60 detik
    """
    return await _svc.get_out_of_stock(session, page=page, size=size)


# ── 4. Distribution (Chart Data) ───────────────────────────────────
@router.get("/distribution")
async def dashboard_distribution(
    _: any = Depends(get_admin),
):
    """
    Data untuk chart distribusi:
    - by_category  : {label, count, revenue}
    - by_brand     : {label, count, revenue}
    - price_buckets: histogram harga
    Sumber: Elasticsearch aggregation.
    TTL Redis: 5 menit
    """
    return await _svc.get_distribution()


# ── 5. Top Selling ─────────────────────────────────────────────────
@router.get("/top-selling")
async def dashboard_top_selling(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Produk dengan terjual tertinggi.
    TTL Redis: 2 menit
    """
    return await _svc.get_top_selling(session, limit=limit)


# ── 6. Recent Products ─────────────────────────────────────────────
@router.get("/recent")
async def dashboard_recent(
    limit: int = Query(10, ge=1, le=50),
    _: any = Depends(get_admin),
):
    """
    Produk yang baru ditambahkan (created_at DESC).
    Sumber: Elasticsearch.
    TTL Redis: 2 menit
    """
    return await _svc.get_recent_products(limit=limit)