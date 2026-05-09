"""
route.py — FastAPI Routes: Promo & Promo Checkout
Sistem: Padjajaran CCTV, Cimahi

Public Endpoints:
  GET  /promos                     — list promo aktif
  GET  /promos/{slug}              — detail promo by slug
  POST /promos/validate            — cek harga + validasi promo (preview)
  POST /promos/checkout            — checkout via promo (Midtrans)
  POST /promos/webhook/midtrans    — webhook callback

Admin Endpoints:
  POST   /admin/promos             — buat promo baru
  GET    /admin/promos             — list semua promo
  PATCH  /admin/promos/{uuid}      — update promo
  POST   /admin/promos/{uuid}/publish    — publish promo
  POST   /admin/promos/{uuid}/pause      — pause promo
  DELETE /admin/promos/{uuid}      — soft delete / arsip
  POST   /admin/promos/{uuid}/items      — tambah item ke promo
  DELETE /admin/promos/{uuid}/items/{item_uuid} — hapus item dari promo
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.main import get_session
from backend.auth.depedence import get_current_user, get_admin
from backend.auth.model import User

from .service import PromoService, PromoCheckoutService
from .schema import (
    PromoCreate, PromoUpdate, PromoResponse, PromoListResponse,
    PromoCheckoutRequest, PromoCheckoutResponse,
    PromoValidateRequest, PromoValidateResponse,
    PromoItemCreate,
)
from .model import Promo, PromoItem, PromoStatus
from backend.celery_app import celery_app 
from fastapi import UploadFile, File
# Sesuaikan path import cdn di bawah ini dengan struktur foldermu
from backend.db.cdn import upload_file, delete_file
logger = logging.getLogger(__name__)

promo_router = APIRouter()
promo_svc    = PromoService()
checkout_svc = PromoCheckoutService()


# ══════════════════════════════════════════════════════════════════
# PUBLIC — List & Detail
# ══════════════════════════════════════════════════════════════════

@promo_router.get(
    "/promos",
    response_model=PromoListResponse,
    tags=["Promo"],
    summary="Daftar promo aktif",
)
async def list_promos(
    target: Optional[str] = Query(None, description="Filter: stock | service_package | all"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """
    Daftar promo yang sedang aktif, diurutkan berdasarkan priority (tertinggi → terendah).
    Bisa difilter berdasarkan target: produk, jasa, atau semua.
    """
    result = await promo_svc.list_active(session, target=target, page=page, size=size)
    items = [await promo_svc.build_promo_response(session, p) for p in result["items"]]
    return PromoListResponse(total=result["total"], page=page, size=size, items=items)



@promo_router.get(
    "/promos/flash-sale",
    response_model=PromoListResponse,
    tags=["Promo"],
    summary="Daftar flash sale aktif",
)
async def list_flash_sales(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    """Flash sale dengan kuota terbatas. Tampilkan remaining_quota untuk urgency."""
    from datetime import datetime, timezone
    from sqlmodel import select

    now = datetime.now(timezone.utc)
    stmt = (
        select(Promo)
        .where(
            Promo.is_flash_sale == True,
            Promo.status == PromoStatus.ACTIVE,
            Promo.valid_from <= now,
            Promo.valid_until >= now,
            Promo.deleted_at.is_(None),
        )
        .order_by(Promo.priority.desc(), Promo.valid_until.asc())  # yang mau habis duluan
    )
    result = await session.exec(stmt)
    all_items = result.all()
    total = len(all_items)
    paginated = all_items[(page - 1) * size : page * size]
    items = [await promo_svc.build_promo_response(session, p) for p in paginated]
    return PromoListResponse(total=total, page=page, size=size, items=items)


@promo_router.get(
    "/promos/{slug}",
    response_model=PromoResponse,
    tags=["Promo"],
    summary="Detail promo by slug",
)
async def get_promo(
    slug: str,
    session: AsyncSession = Depends(get_session),
):
    """Detail promo beserta daftar item yang terikat (produk / paket jasa)."""
    promo = await promo_svc.get_by_slug(session, slug)
    return await promo_svc.build_promo_response(session, promo)


# ══════════════════════════════════════════════════════════════════
# PUBLIC — Validate & Preview Harga
# ══════════════════════════════════════════════════════════════════

@promo_router.post(
    "/promos/validate",
    response_model=PromoValidateResponse,
    tags=["Promo"],
    summary="Preview harga + validasi promo (tanpa checkout)",
)
async def validate_promo_price(
    req: PromoValidateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Gunakan endpoint ini untuk menampilkan estimasi harga di halaman promo
    sebelum user menekan tombol 'Checkout'.

    Tidak ada perubahan data — murni kalkulasi.
    """
    try:
        if req.promo_uuid:
            promo = await promo_svc.get_by_uuid(session, req.promo_uuid)
        else:
            promo = await promo_svc.get_by_slug(session, req.promo_slug)

        # Cek validitas dasar
        is_valid, msg = await promo_svc.validate_promo(
            session, promo,
            user_id=current_user.uuid if current_user else None,
        )
        if not is_valid:
            return PromoValidateResponse(is_valid=False, message=msg)

        price_result = await checkout_svc.calculate_price(session, current_user, req)
        promo_resp   = await promo_svc.build_promo_response(session, promo)

        return PromoValidateResponse(
            is_valid=True,
            message="Promo valid",
            promo=promo_resp,
            price_result=price_result,
        )

    except HTTPException as e:
        return PromoValidateResponse(is_valid=False, message=e.detail)
    except ValueError as e:
        return PromoValidateResponse(is_valid=False, message=str(e))


# ══════════════════════════════════════════════════════════════════
# PUBLIC — Checkout
# ══════════════════════════════════════════════════════════════════

@promo_router.post(
    "/promos/checkout",
    response_model=PromoCheckoutResponse,
    tags=["Promo"],
    summary="Checkout melalui halaman promo",
)
async def promo_checkout(
    body: PromoCheckoutRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Checkout produk / jasa yang menggunakan promo.

    Flow:
    1. Validasi promo (aktif, kuota, periode, user limit)
    2. Kalkulasi diskon per item berdasarkan tipe promo
    3. Jika ada produk fisik → cek ongkir + lock stok
    4. Jika ada jasa → hitung biaya transport + buat ServiceBooking
    5. Buat PromoTransaction + charge Midtrans Snap
    6. Catat PromoUsage (idempotency + rollback support)

    Return: snap_token untuk Midtrans Snap.js di frontend.
    """
    try:
        result = await checkout_svc.checkout(
            session=session,
            user=current_user,
            payload=body,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.exception(f"Promo checkout error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ══════════════════════════════════════════════════════════════════
# WEBHOOK — Midtrans callback
# ══════════════════════════════════════════════════════════════════

@promo_router.post(
    "/promos/webhook/midtrans",
    tags=["Promo"],
    summary="Midtrans webhook untuk promo order",
    include_in_schema=False,
)
async def promo_midtrans_webhook(
    body: dict,
    session: AsyncSession = Depends(get_session),
):
    """
    Midtrans kirim notifikasi ke sini untuk order dengan prefix PROMO-.
    Verifikasi signature SHA512 sebelum proses.
    Selalu return 200.
    """
    from pydantic import BaseModel

    class WebhookPayload(BaseModel):
        order_id: str
        transaction_status: str
        status_code: Optional[str] = None
        gross_amount: Optional[str] = None
        payment_type: Optional[str] = None
        transaction_time: Optional[str] = None
        settlement_time: Optional[str] = None
        fraud_status: Optional[str] = None
        signature_key: Optional[str] = None
        status_message: Optional[str] = None

    try:
        payload = WebhookPayload(**body)
        result  = await checkout_svc.handle_webhook(session, payload)
        return result
    except PermissionError as e:
        logger.warning(f"Promo webhook rejected: {e}")
        raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as e:
        logger.exception(f"Promo webhook error: {e}")
        return {"status": "error", "message": str(e)}


# ══════════════════════════════════════════════════════════════════
# USER — Riwayat Promo Order
# ══════════════════════════════════════════════════════════════════

@promo_router.get(
    "/promos/my-orders",
    tags=["Promo"],
    summary="Riwayat order promo user",
)
async def my_promo_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from sqlmodel import select as sel, desc
    from .model import PromoTransaction, PromoTransactionItem

    stmt = (
        sel(PromoTransaction)
        .where(PromoTransaction.user_id == current_user.uuid)
        .order_by(desc(PromoTransaction.created_at))
    )
    if status:
        stmt = stmt.where(PromoTransaction.transaction_status == status)

    all_result = await session.exec(stmt)
    all_items  = all_result.all()
    total = len(all_items)
    paginated = all_items[(page - 1) * limit : page * limit]

    result_list = []
    for pt in paginated:
        items_result = await session.exec(
            sel(PromoTransactionItem)
            .where(PromoTransactionItem.promo_transaction_id == pt.uuid)
        )
        items = items_result.all()
        result_list.append({
            "uuid": str(pt.uuid),
            "order_id": pt.order_id,
            "promo_snapshot": pt.promo_snapshot,
            "items_subtotal_original": pt.items_subtotal_original,
            "total_discount": pt.total_discount,
            "gross_amount": pt.gross_amount,
            "shipping_cost": pt.shipping_cost,
            "service_cost": pt.service_cost,
            "transaction_status": pt.transaction_status,
            "payment_type": pt.payment_type,
            "transaction_time": pt.transaction_time,
            "settlement_time": pt.settlement_time,
            "service_booking_uuid": str(pt.service_booking_uuid) if pt.service_booking_uuid else None,
            "created_at": pt.created_at,
            "items": [
                {
                    "item_type": i.item_type,
                    "item_name": i.item_name,
                    "quantity": i.quantity,
                    "original_price": i.original_price,
                    "discount_value": i.discount_value,
                    "unit_price": i.unit_price,
                    "subtotal": i.subtotal,
                }
                for i in items
            ],
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_page": (total + limit - 1) // limit,
        "data": result_list,
    }


@promo_router.get(
    "/promos/order/{order_id}",
    tags=["Promo"],
    summary="Detail promo order by order_id",
)
async def get_promo_order_detail(
    order_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from sqlmodel import select as sel
    from .model import PromoTransaction, PromoTransactionItem

    result = await session.exec(
        sel(PromoTransaction)
        .where(
            PromoTransaction.order_id == order_id,
            PromoTransaction.user_id == current_user.uuid,
        )
    )
    pt = result.first()
    if not pt:
        raise HTTPException(404, "Order promo tidak ditemukan")

    items_r = await session.exec(
        sel(PromoTransactionItem)
        .where(PromoTransactionItem.promo_transaction_id == pt.uuid)
    )

    return {
        "uuid": str(pt.uuid),
        "order_id": pt.order_id,
        "promo_snapshot": pt.promo_snapshot,
        "items_subtotal_original": pt.items_subtotal_original,
        "total_discount": pt.total_discount,
        "items_subtotal_discounted": pt.items_subtotal_discounted,
        "gross_amount": pt.gross_amount,
        "shipping_cost": pt.shipping_cost,
        "service_cost": pt.service_cost,
        "transaction_status": pt.transaction_status,
        "payment_type": pt.payment_type,
        "transaction_time": pt.transaction_time,
        "settlement_time": pt.settlement_time,
        "service_booking_uuid": str(pt.service_booking_uuid) if pt.service_booking_uuid else None,
        "has_shipment": pt.has_shipment,
        "created_at": pt.created_at,
        "items": [
            {
                "item_type": i.item_type,
                "item_name": i.item_name,
                "stock_uuid": str(i.stock_uuid) if i.stock_uuid else None,
                "package_uuid": str(i.package_uuid) if i.package_uuid else None,
                "quantity": i.quantity,
                "original_price": i.original_price,
                "discount_value": i.discount_value,
                "unit_price": i.unit_price,
                "subtotal": i.subtotal,
            }
            for i in items_r.all()
        ],
    }


# ══════════════════════════════════════════════════════════════════
# ADMIN — Promo CRUD
# ══════════════════════════════════════════════════════════════════

@promo_router.post(
    "/admin/promos",
    response_model=PromoResponse,
    tags=["Admin Promo"],
    summary="Buat promo baru (status DRAFT)",
)
async def admin_create_promo(
    data: PromoCreate,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin),
):
    """
    Buat promo dengan status DRAFT.
    Publish via endpoint /publish.
    """
    promo = await promo_svc.create_promo(session, data, created_by=admin.uuid)
    return await promo_svc.build_promo_response(session, promo)

# ══════════════════════════════════════════════════════════════════
# ADMIN — Stats & Analytics
# ══════════════════════════════════════════════════════════════════

@promo_router.get(
    "/admin/promos/dashboard",
    tags=["Admin Promo"],
    summary="Data lengkap untuk Dashboard Promo (Summary, Trend 7 Hari, Recent Activity)",
)
async def admin_promo_dashboard(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    from sqlalchemy import cast, Date
    from .model import Promo, PromoTransaction
    from sqlmodel import select as sel, func as sqlfunc, desc
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)

    # 1. SUMMARY METRICS (Keseluruhan)
    # Total Promo Aktif
    active_r = await session.exec(
        sel(Promo).where(
            Promo.status == PromoStatus.ACTIVE,
            Promo.valid_from <= now,
            Promo.valid_until >= now,
            Promo.deleted_at.is_(None),
        )
    )
    active_count = len(active_r.all())

    # Total Order, Revenue, dan Savings
    trx_r = await session.exec(sel(PromoTransaction))
    all_trx = trx_r.all()
    settled_trx = [t for t in all_trx if t.transaction_status in ("settlement", "capture")]
    
    total_orders = len(all_trx)
    total_revenue = sum(t.gross_amount for t in settled_trx)
    total_savings = sum(t.total_discount for t in settled_trx)

    # 2. TREND 7 HARI TERAKHIR (Untuk Grafik/Chart)
    trend_stmt = (
        sel(
            cast(PromoTransaction.created_at, Date).label("date"),
            sqlfunc.count(PromoTransaction.uuid).label("order_count"),
            sqlfunc.sum(PromoTransaction.gross_amount).label("revenue")
        )
        .where(
            PromoTransaction.created_at >= seven_days_ago,
            PromoTransaction.transaction_status.in_(["settlement", "capture"])
        )
        .group_by(cast(PromoTransaction.created_at, Date))
        .order_by(cast(PromoTransaction.created_at, Date).asc())
    )
    trend_result = await session.exec(trend_stmt)
    
    trend_data = []
    for row in trend_result:
        trend_data.append({
            "date": row.date.strftime("%Y-%m-%d"),
            "order_count": row.order_count,
            "revenue": row.revenue or 0
        })

    # 3. RECENT ACTIVITIES (10 Transaksi Terakhir)
    # Join untuk mendapatkan nama User dan nama Promo
    recent_stmt = (
        sel(PromoTransaction, User.username, Promo.name)
        .join(User, PromoTransaction.user_id == User.uuid)
        .join(Promo, PromoTransaction.promo_uuid == Promo.uuid)
        .order_by(desc(PromoTransaction.created_at))
        .limit(10)
    )
    recent_result = await session.exec(recent_stmt)
    
    recent_activities = []
    for trx, username, promo_name in recent_result:
        recent_activities.append({
            "order_id": trx.order_id,
            "username": username,
            "promo_name": promo_name,
            "gross_amount": trx.gross_amount,
            "total_discount": trx.total_discount,
            "status": trx.transaction_status,
            "created_at": trx.created_at
        })

    # 4. TOP PROMOS
    top_promo_stmt = (
        sel(Promo)
        .where(Promo.used_count > 0, Promo.deleted_at.is_(None))
        .order_by(desc(Promo.used_count))
        .limit(5)
    )
    top_promos = [
        {"uuid": str(p.uuid), "name": p.name, "used_count": p.used_count}
        for p in (await session.exec(top_promo_stmt)).all()
    ]

    return {
        "summary": {
            "active_promos": active_count,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_savings": total_savings,
        },
        "trend_7_days": trend_data,
        "recent_activities": recent_activities,
        "top_promos": top_promos
    }
@promo_router.get(
    "/admin/promos/status",
    tags=["Admin Promo"],
    summary="Statistik penggunaan promo",
)
async def admin_promo_stats(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    from sqlmodel import select as sel, func as sqlfunc
    from .model import PromoTransaction
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    # Total promo aktif
    active_r = await session.exec(
        sel(Promo).where(
            Promo.status == PromoStatus.ACTIVE,
            Promo.valid_from <= now,
            Promo.valid_until >= now,
            Promo.deleted_at.is_(None),
        )
    )
    active_count = len(active_r.all())

    # Total transaksi promo
    trx_r = await session.exec(sel(PromoTransaction))
    all_trx = trx_r.all()

    settled = [t for t in all_trx if t.transaction_status in ("settlement", "capture")]
    total_revenue = sum(t.gross_amount for t in settled)
    total_savings = sum(t.total_discount for t in settled)

    # Top promo berdasarkan usage
    promo_usage_r = await session.exec(
        sel(Promo).where(Promo.used_count > 0).order_by(Promo.used_count.desc()).limit(5)
    )
    top_promos = [
        {"uuid": str(p.uuid), "name": p.name, "used_count": p.used_count}
        for p in promo_usage_r.all()
    ]

    return {
        "active_promos": active_count,
        "total_promo_orders": len(all_trx),
        "settled_orders": len(settled),
        "total_revenue_from_promo": total_revenue,
        "total_customer_savings": total_savings,
        "top_promos_by_usage": top_promos,
    }
@promo_router.get(
    "/admin/promos",
    tags=["Admin Promo"],
    summary="Daftar semua promo (termasuk draft & archived)",
)
async def admin_list_promos(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    from sqlmodel import select as sel, desc

    stmt = sel(Promo).order_by(
            desc(Promo.priority), desc(Promo.created_at)
    )
    if status:
        stmt = stmt.where(Promo.status == status)

    all_r  = await session.exec(stmt)
    all_p  = all_r.all()
    total  = len(all_p)
    paged  = all_p[(page - 1) * size : page * size]
    items  = [await promo_svc.build_promo_response(session, p) for p in paged]
    return {"total": total, "page": page, "size": size, "items": items}


@promo_router.get(
    "/admin/promos/{promo_uuid}",
    response_model=PromoResponse,
    tags=["Admin Promo"],
    summary="Detail promo by UUID (admin)",
)
async def admin_get_promo(
    promo_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    promo = await promo_svc.get_by_uuid(session, promo_uuid)
    return await promo_svc.build_promo_response(session, promo)


@promo_router.patch(
    "/admin/promos/{promo_uuid}",
    response_model=PromoResponse,
    tags=["Admin Promo"],
    summary="Update metadata promo",
)
async def admin_update_promo(
    promo_uuid: UUID,
    data: PromoUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    promo = await promo_svc.update_promo(session, promo_uuid, data)
    return await promo_svc.build_promo_response(session, promo)


@promo_router.post(
    "/admin/promos/{promo_uuid}/publish",
    response_model=PromoResponse,
    tags=["Admin Promo"],
    summary="Publish promo (DRAFT/PAUSED → ACTIVE)",
)
async def admin_publish_promo(
    promo_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    promo = await promo_svc.publish_promo(session, promo_uuid)
    return await promo_svc.build_promo_response(session, promo)


@promo_router.post(
    "/admin/promos/{promo_uuid}/pause",
    response_model=PromoResponse,
    tags=["Admin Promo"],
    summary="Pause promo aktif",
)
async def admin_pause_promo(
    promo_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    promo = await promo_svc.get_by_uuid(session, promo_uuid)
    if promo.status != PromoStatus.ACTIVE:
        raise HTTPException(400, "Hanya promo ACTIVE yang bisa di-pause")
    promo.status = PromoStatus.PAUSED
    session.add(promo)
    await session.commit()
    await session.refresh(promo)
    return await promo_svc.build_promo_response(session, promo)


@promo_router.delete(
    "/admin/promos/{promo_uuid}",
    tags=["Admin Promo"],
    summary="Soft delete / arsip promo",
)
async def admin_delete_promo(
    promo_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    return await promo_svc.soft_delete_promo(session, promo_uuid)


# ══════════════════════════════════════════════════════════════════
# ADMIN — PromoItem Management
# ══════════════════════════════════════════════════════════════════

@promo_router.post(
    "/admin/promos/{promo_uuid}/items",
    tags=["Admin Promo"],
    summary="Tambah item (Stock/ServicePackage) ke promo",
)
async def admin_add_promo_item(
    promo_uuid: UUID,
    data: PromoItemCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    # Pastikan promo exist
    promo = await promo_svc.get_by_uuid(session, promo_uuid)

    # Cek tidak duplicate
    from sqlmodel import select as sel
    if data.stock_uuid:
        dup = await session.exec(
            sel(PromoItem).where(
                PromoItem.promo_uuid == promo_uuid,
                PromoItem.stock_uuid == data.stock_uuid
            )
        )
        if dup.first():
            raise HTTPException(409, "Stock sudah ada di promo ini")

    if data.package_uuid:
        dup = await session.exec(
            sel(PromoItem).where(
                PromoItem.promo_uuid == promo_uuid,
                PromoItem.package_uuid == data.package_uuid
            )
        )
        if dup.first():
            raise HTTPException(409, "Package sudah ada di promo ini")

    pi = PromoItem(
        promo_uuid=promo_uuid,
        stock_uuid=data.stock_uuid,
        package_uuid=data.package_uuid,
        override_discount_value=data.override_discount_value,
    )
    session.add(pi)
    await session.commit()
    await session.refresh(pi)

    return {
        "uuid": str(pi.uuid),
        "promo_uuid": str(promo_uuid),
        "stock_uuid": str(pi.stock_uuid) if pi.stock_uuid else None,
        "package_uuid": str(pi.package_uuid) if pi.package_uuid else None,
        "override_discount_value": pi.override_discount_value,
    }


@promo_router.delete(
    "/admin/promos/{promo_uuid}/items/{item_uuid}",
    tags=["Admin Promo"],
    summary="Hapus item dari promo",
)
async def admin_remove_promo_item(
    promo_uuid: UUID,
    item_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    from sqlmodel import select as sel

    result = await session.exec(
        sel(PromoItem).where(
            PromoItem.uuid == item_uuid,
            PromoItem.promo_uuid == promo_uuid,
        )
    )
    pi = result.first()
    if not pi:
        raise HTTPException(404, "Item tidak ditemukan di promo ini")

    await session.delete(pi)
    await session.commit()
    return {"message": "Item berhasil dihapus dari promo"}

# backend admin kirim notif ke user 
@promo_router.post("/admin/promos/{promo_uuid}/notify")
async def trigger_notify_new_promo(
    promo_uuid: str,
    current_admin = Depends(get_admin),
):
    celery_app.send_task(
        "backend.tasks.promo_tasks.notify_new_promo",
        args=[promo_uuid],
        queue="email"
    )
    return {"message": "Notifikasi promo baru sedang dikirim"}


@promo_router.post(
    "/admin/promos/upload-banner",
    tags=["Admin Promo"],
    summary="Upload banner promo ke CDN R2",
)
async def admin_upload_promo_banner(
    file: UploadFile = File(...),
    _: User = Depends(get_admin),
):
    """
    Endpoint khusus untuk mengunggah gambar banner ke Cloudflare R2.
    Mengembalikan URL public dari gambar tersebut.
    """
    # Validasi tipe file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar (JPEG, PNG, WEBP, dll)")

    # Batasi ukuran file (misal maksimal 2MB)
    MAX_SIZE = 2 * 1024 * 1024
    file_size = 0
    file_bytes = b""
    
    # Membaca file per chunk agar aman untuk memori
    for chunk in file.file:
        file_bytes += chunk
        file_size += len(chunk)
        if file_size > MAX_SIZE:
            raise HTTPException(status_code=400, detail="Ukuran gambar maksimal 2MB")

    try:
        # Menggunakan db.cdn.py untuk upload
        # Kita biarkan filename=None agar CDN meng-generate UUID otomatis (mencegah bentrok nama)
        banner_url = await upload_file(
            file=file_bytes,
            folder="promo_banners",
            content_type=file.content_type
        )
        return {"banner_url": banner_url}
    except Exception as e:
        logger.error(f"Gagal upload banner promo: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengunggah gambar ke server CDN")


@promo_router.post(
    "/admin/promos/upload-banner",
    tags=["Admin Promo"],
    summary="Upload banner promo ke CDN R2",
)
async def admin_upload_promo_banner(
    file: UploadFile = File(...),
    _: User = Depends(get_admin),
):
    """
    Endpoint khusus untuk mengunggah gambar banner ke Cloudflare R2.
    Mengembalikan URL public dari gambar tersebut.
    """
    # Validasi tipe file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar (JPEG, PNG, WEBP, dll)")

    # Batasi ukuran file (misal maksimal 2MB)
    MAX_SIZE = 2 * 1024 * 1024
    file_size = 0
    file_bytes = b""
    
    # Membaca file per chunk agar aman untuk memori
    for chunk in file.file:
        file_bytes += chunk
        file_size += len(chunk)
        if file_size > MAX_SIZE:
            raise HTTPException(status_code=400, detail="Ukuran gambar maksimal 2MB")

    try:
        # Menggunakan db.cdn.py untuk upload
        # Kita biarkan filename=None agar CDN meng-generate UUID otomatis (mencegah bentrok nama)
        banner_url = await upload_file(
            file=file_bytes,
            folder="promo_banners",
            content_type=file.content_type
        )
        return {"banner_url": banner_url}
    except Exception as e:
        logger.error(f"Gagal upload banner promo: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengunggah gambar ke server CDN")



