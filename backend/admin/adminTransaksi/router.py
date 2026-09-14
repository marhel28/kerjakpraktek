from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from backend.db.main import get_session
from backend.auth.depedence import get_admin
from backend.auth.model import User
from .service import TransactionAdminService
from .schemas import TransactionRead
from typing import List

router_transaksi_admin = APIRouter()


@router_transaksi_admin.get("/transaksi")
async def get_all_transaksi_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    transaction_status: Optional[str] = None,
    payment_type: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin)
):
    data, total, summary = await TransactionAdminService.get_all_transactions(
        session=session,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        transaction_status=transaction_status,
        payment_type=payment_type,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )

    # Map data to include stock titles and thumbnails for the frontend
    formatted_data = []
    for t in data:
        t_dict = TransactionRead.model_validate(t)
        for i, item in enumerate(t.items):
            if item.stock:
                t_dict.items[i].stock_title = item.stock.title
                if item.stock.assets:
                    t_dict.items[i].thumbnail_url = item.stock.assets[0].url
        formatted_data.append(t_dict)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_page": (total + limit - 1) // limit,
        "summary": summary,
        "data": formatted_data
    }
@router_transaksi_admin.put("/transaksi/{order_id}/waybill")
async def update_transaction_waybill(
    order_id: str,
    waybill_number: str = Query(..., min_length=1),
    courier_name: Optional[str] = Query(None),
    status: str = Query("SHIPPED"),
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin)
):
    transaction = await TransactionAdminService.update_waybill(
        session=session,
        order_id=order_id,
        waybill_number=waybill_number,
        courier_name=courier_name,
        delivery_status=status
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
        
    return {
        "success": True,
        "message": "Resi berhasil diupdate",
        "data": transaction
    }


@router_transaksi_admin.get("/notifications")
async def get_admin_notifications(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin)
):
    notifs = await TransactionAdminService.get_admin_notifications(session, admin)
    return notifs


@router_transaksi_admin.patch("/notifications/{notification_id}/read")
async def mark_admin_notification_read(
    notification_id: int,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin)
):
    success = await TransactionAdminService.mark_admin_notification_read(session, admin, notification_id)
    return {"success": success}


@router_transaksi_admin.post("/notifications/read-all")
async def mark_all_admin_notifications_read(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin)
):
    success = await TransactionAdminService.mark_all_admin_notifications_read(session, admin)
    return {"success": success}

