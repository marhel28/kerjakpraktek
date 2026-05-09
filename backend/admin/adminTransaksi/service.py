from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc
from typing import Optional
from datetime import datetime

from backend.data.transaksi.model import Transaction


class TransactionAdminService:

    @staticmethod
    async def get_all_transactions(
        session: AsyncSession,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        transaction_status: Optional[str] = None,
        payment_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ):
        offset = (page - 1) * limit

        query = select(Transaction)

        # ===== FILTER =====
        if transaction_status:
            query = query.where(Transaction.transaction_status == transaction_status)

        if payment_type:
            query = query.where(Transaction.payment_type == payment_type)

        if user_id:
            query = query.where(Transaction.user_id == user_id)

        if start_date:
            query = query.where(Transaction.created_at >= start_date)

        if end_date:
            query = query.where(Transaction.created_at <= end_date)

        # ===== SORTING =====
        sort_column = getattr(Transaction, sort_by, Transaction.created_at)

        if sort_order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        # ===== PAGINATION =====
        query = query.offset(offset).limit(limit)

        result = await session.execute(query)
        data = result.scalars().all()

        return data
