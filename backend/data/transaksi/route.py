# ============================================================
# FILE: backend/data/transaksi/route.py  (UNIFIED — FULL REPLACE)
# Perubahan:
#   - GET /my        → hanya Transaction biasa (backward compat)
#   - GET /my/all    → gabungan Transaction + PromoTransaction (BARU)
#   - GET /detail/{order_id} → auto-detect prefix PROMO- / ORD-
#   - POST /repay/{order_id} → bayar ulang (BARU)
# ============================================================

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
import logging

from backend.db.main import get_session
from backend.auth.depedence import get_current_user
from backend.auth.model import User, UserAddress
from .service import TransactionService
from .schema import CheckoutRequest, CheckoutResponse, MidtransWebhookPayload

logger = logging.getLogger(__name__)
transaksi_route = APIRouter()


# ============================================================
# CEK ONGKIR
# ============================================================
@transaksi_route.get("/shipping/estimate")
async def estimate_shipping(
    address_uuid: UUID,
    stock_uuid: UUID,
    quantity: int = Query(1, ge=1),
    weight: Optional[int] = Query(None, description="Berat total dalam gram (opsional, jika tidak diisi akan hitung dari stock * qty)"),
    courier: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Ambil preferensi kurir dari admin
    from backend.admin.adminSettings.service import AdminSettingService
    prefs = await AdminSettingService.get_courier_preferences(session)
    
    # Filter kurir yang aktif (True)
    active_couriers = [k for k, v in prefs.items() if v]
    
    # Jika tidak ada yang aktif, default ke jne
    courier_str = ":".join(active_couriers) if active_couriers else "jne"
    
    # Gunakan courier_str alih-alih parameter input agar sesuai setting admin
    target_courier = courier_str
    from sqlmodel import select
    from backend.data.stock.model import Stock
    import httpx
    from backend.config import Config

    addr_result = await session.exec(
        select(UserAddress)
        .where(UserAddress.uuid == address_uuid)
        .where(UserAddress.user_id == user.uuid)
    )
    address = addr_result.one_or_none()
    if not address:
        raise HTTPException(404, "Alamat tidak ditemukan")

    if weight is not None:
        total_weight = weight
    else:
        stock_result = await session.exec(
            select(Stock).where(Stock.uuid == stock_uuid).where(Stock.is_active == True)
        )
        stock = stock_result.one_or_none()
        if not stock:
            raise HTTPException(404, "Produk tidak ditemukan")
        total_weight = stock.weight * quantity

    RAJAONGKIR_URL = "https://rajaongkir.komerce.id/api/v1/calculate/domestic-cost"
    ORIGIN = "16155"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(
                RAJAONGKIR_URL,
                headers={"key": Config.SHIPPING_COST, "Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "origin": ORIGIN,
                    "destination": address.location_id,
                    "weight": max(total_weight, 1),
                    "courier": target_courier.lower().replace(" ", ""),
                    "price": "lowest",
                },
            )
            resp.raise_for_status()
        except Exception as e:
            raise HTTPException(503, f"Gagal mengambil data ongkir: {e}")

    options = resp.json().get("data", [])
    return {
        "origin": ORIGIN,
        "destination": address.location_id,
        "total_weight": total_weight,
        "options": [
            {
                "courier": item.get("name"),
                "service": item.get("service"),
                "etd": item.get("etd"),
                "price": item.get("cost"),
            }
            for item in options
        ],
    }


# ============================================================
# CHECKOUT
# ============================================================
@transaksi_route.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    body: CheckoutRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await TransactionService.checkout(session=session, user=user, payload=body)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.exception(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# WEBHOOK MIDTRANS
# ============================================================
@transaksi_route.post("/webhook/midtrans")
async def midtrans_webhook(
    body: MidtransWebhookPayload,
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await TransactionService.handle_webhook(session=session, payload=body)
        return result
    except PermissionError as e:
        logger.warning(f"Webhook rejected: {e}")
        raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as e:
        logger.exception(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================
# RIWAYAT TRANSAKSI BIASA (backward compat)
# ============================================================
@transaksi_route.get("/my")
async def get_my_transactions(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("desc", pattern="^(asc|desc)$"),
    sort_by: str = Query("created_at", pattern="^(created_at|gross_amount)$"),
    stock_id: Optional[UUID] = Query(None),
    stock_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_amount: Optional[int] = Query(None),
    max_amount: Optional[int] = Query(None),
):
    return await TransactionService.get_user_transactions(
        session=session,
        user_id=user.uuid,
        page=page,
        limit=limit,
        sort=sort,
        sort_by=sort_by,
        stock_id=stock_id,
        stock_name=stock_name,
        status=status,
        min_amount=min_amount,
        max_amount=max_amount,
    )


# ============================================================
# RIWAYAT SEMUA TRANSAKSI — biasa + promo (BARU)
# ============================================================
@transaksi_route.get("/my/all")
async def get_all_my_transactions(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("desc", pattern="^(asc|desc)$"),
    status: Optional[str] = Query(None),
    trx_type: Optional[str] = Query(None, description="Filter: 'regular' | 'promo' | None = semua"),
    min_amount: Optional[int] = Query(None),
    max_amount: Optional[int] = Query(None),
):
    """
    Mengembalikan semua transaksi user (reguler + promo) digabung,
    diurutkan by created_at, dengan pagination.

    Tiap item punya field:
      - trx_type: "regular" | "promo"
      - order_id
      - gross_amount
      - transaction_status
      - items: list produk / paket yang dibeli
      - snap_token / payment_url (jika masih pending → bisa dipakai repay)
    """
    try:
        return await TransactionService.get_all_user_transactions(
            session=session,
            user_id=user.uuid,
            page=page,
            limit=limit,
            sort=sort,
            status=status,
            trx_type=trx_type,
            min_amount=min_amount,
            max_amount=max_amount,
        )
    except Exception as e:
        logger.exception(f"get_all_my_transactions error: {e}")
        raise HTTPException(500, f"Gagal mengambil data pesanan: {str(e)}")


# ============================================================
# DETAIL TRANSAKSI — auto-detect reguler / promo
# ============================================================
@transaksi_route.get("/detail/{order_id}")
async def get_transaction_detail(
    order_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Mendukung dua format order_id:
      - ORD-YYYYMMDD-XXXXXXXX  → Transaction biasa
      - PROMO-YYYYMMDD-XXXXXXXX → PromoTransaction
    """
    try:
        # Check if user is admin
        from backend.auth.model import UserRole
        target_user_id = user.uuid if user.role != UserRole.ADMIN else None

        if order_id.startswith("PROMO-"):
            return await TransactionService.get_promo_transaction_detail(
                session=session, user_id=target_user_id, order_id=order_id
            )
        elif order_id.startswith("BK-"):
            return await TransactionService.get_jasa_transaction_detail(
                session=session, user_id=target_user_id, order_id=order_id
            )
        else:
            return await TransactionService.get_regular_transaction_detail(
                session=session, user_id=target_user_id, order_id=order_id
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"get_transaction_detail error: {e}")
        raise HTTPException(500, "Internal server error")

# ============================================================
# DOWNLOAD INVOICE PDF
# ============================================================
@transaksi_route.get("/invoice/{order_id}")
async def download_invoice(
    order_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Menghasilkan file PDF invoice untuk transaksi tertentu.
    """
    from fastapi.responses import StreamingResponse
    try:
        from backend.auth.model import UserRole
        target_user_id = user.uuid if user.role != UserRole.ADMIN else None

        pdf_buffer = await TransactionService.generate_invoice_pdf(
            session=session, user_id=target_user_id, order_id=order_id
        )
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=Invoice-{order_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"download_invoice error: {e}")
        raise HTTPException(500, f"Gagal generate invoice: {str(e)}")


# ============================================================
# REPAY — bayar ulang untuk transaksi pending (reguler & promo)
# ============================================================
@transaksi_route.post("/repay/{order_id}")
async def repay_transaction(
    order_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Membuat ulang Midtrans Snap token untuk transaksi yang masih pending.
    Mendukung transaksi reguler (ORD-) maupun promo (PROMO-).

    Response:
      {
        "order_id": "...",
        "snap_token": "...",
        "payment_url": "...",
        "gross_amount": 123456,
        "trx_type": "regular" | "promo"
      }
    """
    try:
        return await TransactionService.repay(
            session=session, user_id=user.uuid, order_id=order_id
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        logger.exception(f"repay error: {e}")
        raise HTTPException(500, "Internal server error")