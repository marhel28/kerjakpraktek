from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from backend.db.main import get_session
from backend.auth.depedence import get_admin
from backend.auth.model import User
from .service import TransactionAdminService

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
    data = await TransactionAdminService.get_all_transactions(
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

    return {
        "page": page,
        "limit": limit,
        "count": len(data),
        "data": data
    }
