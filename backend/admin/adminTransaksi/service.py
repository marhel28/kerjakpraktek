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

        from sqlalchemy.orm import selectinload
        from backend.data.transaksi.model import TransactionItem
        from backend.data.stock.model import Stock, AssetStock

        query = select(Transaction).options(
            selectinload(Transaction.shipment),
            selectinload(Transaction.user),
            selectinload(Transaction.items).selectinload(TransactionItem.stock).selectinload(Stock.assets)
        )

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

        # ===== TOTAL COUNT (BEFORE PAGINATION) =====
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()

        # ===== SUMMARY COUNTS =====
        lunas_query = select(func.count(Transaction.uuid)).where(Transaction.transaction_status == "settlement")
        pending_query = select(func.count(Transaction.uuid)).where(Transaction.transaction_status.in_(["pending", "pending_payment"]))
        
        lunas_res = await session.execute(lunas_query)
        pending_res = await session.execute(pending_query)
        
        lunas_count = lunas_res.scalar_one()
        pending_count = pending_res.scalar_one()

        # ===== PAGINATION =====
        query = query.offset(offset).limit(limit)

        result = await session.execute(query)
        data = result.scalars().all()

        return data, total, {"lunas": lunas_count, "pending": pending_count}

    @staticmethod
    async def update_waybill(
        session: AsyncSession,
        order_id: str,
        waybill_number: str,
        courier_name: Optional[str] = None,
        delivery_status: str = "SHIPPED"
    ):
        from backend.data.ongkir.model import Shipment
        from sqlalchemy.orm import selectinload

        # PROMO dual-path (Shipment.promo_transaction_uuid)
        if order_id.startswith("PROMO-"):
            from backend.data.public.promobanner.model import PromoTransaction
            promo_r = await session.execute(
                select(PromoTransaction).where(PromoTransaction.order_id == order_id)
            )
            promo_trx = promo_r.scalar_one_or_none()
            if not promo_trx:
                return None
            ship_r = await session.execute(
                select(Shipment).where(Shipment.promo_transaction_uuid == promo_trx.uuid)
            )
            promo_ship = ship_r.scalar_one_or_none()
            if not promo_ship:
                promo_ship = Shipment(
                    promo_transaction_uuid=promo_trx.uuid,
                    waybill_number=waybill_number,
                    courier_name=courier_name or "JNE",
                    delivery_status=delivery_status,
                    recipient_name="User",
                    recipient_phone="000",
                    shipping_address="Address",
                )
                session.add(promo_ship)
            else:
                promo_ship.waybill_number = waybill_number
                promo_ship.delivery_status = delivery_status
                if courier_name:
                    promo_ship.courier_name = courier_name
                session.add(promo_ship)
            await session.commit()
            await session.refresh(promo_ship)
            try:
                from backend.user.notifications import notify_user

                await notify_user(
                    user_id=promo_trx.user_id,
                    title="Pesanan Dikirim! 📦",
                    content=f"Pesanan promo {order_id} telah dikirim dengan resi: {waybill_number}. Silakan cek berkala.",
                    action_url=f"/dashboard/orders/{order_id}",
                    notif_type="order",
                    metadata={"order_id": order_id, "waybill": waybill_number},
                )
            except Exception as e:
                print(f"Failed to send shipping notification: {e}")
            return promo_trx

        # Cari transaksi
        query = select(Transaction).where(Transaction.order_id == order_id).options(selectinload(Transaction.shipment))
        result = await session.execute(query)
        transaction = result.scalar_one_or_none()

        if not transaction:
            return None

        if not transaction.shipment:
            # Jika belum ada shipment (biasanya harusnya ada dari checkout, tapi jaga-jaga)
            shipment = Shipment(
                transaction_uuid=transaction.uuid,
                waybill_number=waybill_number,
                courier_name=courier_name or "JNE", # Default jika kosong
                delivery_status=delivery_status,
                recipient_name="User", # Placeholder
                recipient_phone="000",
                shipping_address="Address"
            )
            session.add(shipment)
        else:
            transaction.shipment.waybill_number = waybill_number
            transaction.shipment.delivery_status = delivery_status
            if courier_name:
                transaction.shipment.courier_name = courier_name
            session.add(transaction.shipment)

        await session.commit()
        await session.refresh(transaction)

        # ===== SEND NOTIFICATION =====
        try:
            from backend.user.notifications import notify_user

            title = "Pesanan Dikirim! 📦"
            content = f"Pesanan {order_id} telah dikirim dengan resi: {waybill_number}. Silakan cek berkala."

            await notify_user(
                user_id=transaction.user_id,
                title=title,
                content=content,
                action_url=f"/dashboard/orders/{order_id}",
                notif_type="order",
                metadata={"order_id": order_id, "waybill": waybill_number},
            )
        except Exception as e:
            # Notif failed should not rollback the waybill update
            print(f"Failed to send shipping notification: {e}")

        return transaction

    @staticmethod
    async def get_admin_notifications(session: AsyncSession, admin):
        from backend.user.notifications import list_for_user

        return await list_for_user(admin.uuid)

    @staticmethod
    async def mark_admin_notification_read(session: AsyncSession, admin, notification_id: int):
        from backend.user.notifications import mark_read

        result = await mark_read(admin.uuid, notification_id)
        return result is not None

    @staticmethod
    async def mark_all_admin_notifications_read(session: AsyncSession, admin):
        from backend.user.notifications import mark_all_read

        await mark_all_read(admin.uuid)
        return True

