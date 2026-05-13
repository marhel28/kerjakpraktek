from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
from uuid import UUID

from backend.db.main import get_session
from backend.data.stock.service import StockService
from backend.data.stock.schema import (
    CouponCreateRequest, CouponUpdateRequest,
    CouponResponse
)
from backend.auth.depedence import get_admin

router = APIRouter()
service = StockService()

@router.post("", response_model=CouponResponse)
async def admin_create_coupon(
    data: CouponCreateRequest,
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """Buat kupon baru."""
    return await service.create_coupon(session, data)


@router.get("")
async def admin_list_coupons(
    include_inactive: bool = Query(False),
    page: int = Query(1, ge=1),
    size: int = Query(20, le=100),
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """List semua kupon (aktif & non-aktif, exclude deleted)."""
    result = await service.get_all_coupons(session, include_inactive, page, size)
    return {
        "success": True,
        "message": "Data kupon berhasil diambil",
        "data": {
            "total": result["total"],
            "page": result["page"],
            "size": result["size"],
            "items": result["items"],
        }
    }


@router.get("/{code}", response_model=CouponResponse)
async def admin_get_coupon(
    code: str,
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """Detail satu kupon by code."""
    coupon = await service.get_coupon_by_code(session, code)
    if not coupon:
        raise HTTPException(404, detail="Kupon tidak ditemukan")
    return coupon


@router.patch("/{code}", response_model=CouponResponse)
async def admin_update_coupon(
    code: str,
    data: CouponUpdateRequest,
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """Update sebagian field kupon."""
    return await service.update_coupon(session, code, data)


@router.delete("/{code}")
async def admin_delete_coupon(
    code: str,
    session: AsyncSession = Depends(get_session),
    _: any = Depends(get_admin),
):
    """
    Soft delete kupon.
    Hard delete dijadwalkan Celery task setelah 30 hari.
    """
    result = await service.soft_delete_coupon(session, code)

    # Jadwalkan hard delete via Celery setelah 30 hari
    from backend.tasks.coupon_tasks import hard_delete_coupon_task
    hard_delete_coupon_task.apply_async(
        args=[code],
        countdown=60 * 60 * 24 * 30,  # 30 hari
    )

    return {
        "success": True,
        "message": f"Kupon '{code}' berhasil dihapus",
        "data": result
    }
