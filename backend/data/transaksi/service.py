# ============================================================
# FILE: backend/data/transaksi/service.py  (FULL REPLACE)
#
# Tambahan method:
#   - get_all_user_transactions()     → gabung Transaction + PromoTransaction
#   - get_regular_transaction_detail() → detail satu Transaction biasa
#   - get_promo_transaction_detail()   → detail satu PromoTransaction
#   - repay()                          → buat ulang Snap token (pending only)
# ============================================================

import hashlib
import httpx
import base64
import logging
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc, func
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException

from .model import Transaction, TransactionItem
from .schema import CheckoutRequest, CheckoutResponse, MidtransWebhookPayload
from backend.data.stock.model import Stock, Coupon
from backend.data.ongkir.model import Shipment
from backend.auth.model import User, UserAddress, UserMap
from backend.user.cart.model import Cart
from backend.config import Config
from sqlalchemy.orm import selectinload
from backend.db.supabse import SupabaseNotificationService

# Import PromoTransaction models
from backend.data.public.promobanner.model import (
    PromoTransaction,
    PromoTransactionItem,
)
from backend.data.jasa.model import ServicePackage, ServiceBooking

logger = logging.getLogger(__name__)


# ============================================================
# HELPERS
# ============================================================

def _midtrans_auth_header() -> str:
    raw = f"{Config.MIDTRANS_SERVER_KEY}:"
    return "Basic " + base64.b64encode(raw.encode()).decode()


MIDTRANS_CHARGE_URL   = "https://app.sandbox.midtrans.com/snap/v1/transactions"
RAJAONGKIR_CHARGE_URL = "https://rajaongkir.komerce.id/api/v1/calculate/domestic-cost"
ORIGIN_BOGOR_UTARA    = "16155"

# Status yang sudah final — tidak bisa bayar ulang
FINAL_STATUSES = {"settlement", "capture", "cancel", "deny", "expire", "refund"}


def verify_midtrans_signature(order_id, status_code, gross_amount, signature_key) -> bool:
    raw = f"{order_id}{status_code}{gross_amount}{Config.MIDTRANS_SERVER_KEY}"
    return hashlib.sha512(raw.encode()).hexdigest() == signature_key


def _generate_order_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    uid = str(uuid4()).replace("-", "")[:8].upper()
    return f"ORD-{ts}-{uid}"


def _parse_dt(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


async def _get_supabase_user_id(session: AsyncSession, local_user_id: UUID) -> Optional[str]:
    try:
        result = await session.exec(
            select(UserMap).where(UserMap.local_user_id == str(local_user_id))
        )
        user_map = result.one_or_none()
        return user_map.supabase_user_id if user_map else None
    except Exception as e:
        logger.error(f"Error getting supabase_user_id: {e}")
        return None


async def _send_transaction_notification(
    session, local_user_id, title, content, order_id, notif_type="order"
):
    try:
        supabase_user_id = await _get_supabase_user_id(session, local_user_id)
        if not supabase_user_id:
            return
        await SupabaseNotificationService.send_notification(
            user_id=supabase_user_id,
            title=title,
            content=content,
            action_url=f"/dashboard/orders/{order_id}",
            notif_type=notif_type,
            metadata={"order_id": order_id},
        )
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


async def _clear_cart_items(session, user_uuid, stock_uuids):
    try:
        for stock_uuid in stock_uuids:
            await session.exec(
                delete(Cart)
                .where(Cart.user_uuid == user_uuid)
                .where(Cart.stock_uuid == stock_uuid)
            )
    except Exception as e:
        logger.error(f"Failed to clear cart items: {e}")


# ============================================================
# SERVICE
# ============================================================

class TransactionService:

    # ----------------------------------------------------------
    # CHECKOUT
    # ----------------------------------------------------------
    @staticmethod
    async def checkout(*, session, user, payload: CheckoutRequest) -> CheckoutResponse:
        from backend.data.ongkir.service import OngkirAPI

        stock_uuids = [item.stock_uuid for item in payload.items]
        if len(stock_uuids) != len(set(str(u) for u in stock_uuids)):
            raise ValueError("Terdapat produk duplikat dalam pesanan")

        addr_result = await session.exec(
            select(UserAddress)
            .where(UserAddress.uuid == payload.address_uuid)
            .where(UserAddress.user_id == user.uuid)
        )
        address = addr_result.one_or_none()
        if not address:
            raise ValueError("Alamat tidak ditemukan atau bukan milik Anda")

        ongkir_api = OngkirAPI(api_key=Config.SHIPPING_COST)
        ongkir_result = ongkir_api.cek_ongkir(
            destination=address.location_id,
            weight=1000 * len(payload.items),
            courier=payload.courier_name.lower(),
        )
        if isinstance(ongkir_result, dict) and "error" in ongkir_result:
            raise ValueError(f"Gagal cek ongkir: {ongkir_result['error']}")
        if not ongkir_result:
            raise ValueError("Layanan kurir tidak tersedia ke alamat tujuan")

        courier_service_upper = (payload.courier_service or "REG").upper()
        selected_courier = next(
            (o for o in ongkir_result if o.get("service", "").upper() == courier_service_upper),
            ongkir_result[0],
        )
        shipping_cost = selected_courier.get("price", 0)

        sorted_items = sorted(payload.items, key=lambda i: str(i.stock_uuid))
        locked_stocks: dict[str, Stock] = {}
        for item in sorted_items:
            try:
                result = await session.exec(
                    select(Stock)
                    .where(Stock.uuid == item.stock_uuid)
                    .where(Stock.is_active == True)
                    .with_for_update(nowait=True)
                )
                stock = result.one_or_none()
            except OperationalError:
                raise ValueError("Stok produk sedang diproses, coba lagi")
            if not stock:
                raise ValueError(f"Produk {item.stock_uuid} tidak ditemukan atau tidak aktif")
            if stock.stok < item.quantity:
                raise ValueError(f"Stok '{stock.title}' tidak cukup. Tersedia: {stock.stok}")
            locked_stocks[str(item.stock_uuid)] = stock

        items_subtotal = sum(
            locked_stocks[str(item.stock_uuid)].online_price * item.quantity
            for item in payload.items
        )

        discount_amount = 0
        if payload.coupon_code:
            coupon = await TransactionService._validate_coupon(
                session=session, code=payload.coupon_code, subtotal=items_subtotal
            )
            if coupon:
                if coupon.discount_type == "percentage":
                    discount_amount = int(items_subtotal * coupon.discount_value / 100)
                    if coupon.max_discount:
                        discount_amount = min(discount_amount, coupon.max_discount)
                else:
                    discount_amount = coupon.discount_value
                coupon.used_count += 1
                session.add(coupon)

        gross_amount = max(items_subtotal - discount_amount, 0) + shipping_cost

        for item in payload.items:
            stock = locked_stocks[str(item.stock_uuid)]
            stock.stok -= item.quantity
            session.add(stock)

        order_id = _generate_order_id()
        transaction = Transaction(
            user_id=user.uuid,
            order_id=order_id,
            gross_amount=gross_amount,
            items_subtotal=items_subtotal,
            shipping_cost=shipping_cost,
            discount_amount=discount_amount,
            transaction_status="pending_payment",
        )
        session.add(transaction)
        await session.flush()

        for item in payload.items:
            stock = locked_stocks[str(item.stock_uuid)]
            trx_item = TransactionItem(
                transaction_id=transaction.uuid,
                stock_id=stock.uuid,
                quantity=item.quantity,
                unit_price=stock.online_price,
                subtotal=stock.online_price * item.quantity,
            )
            session.add(trx_item)

        shipment = Shipment(
            transaction_uuid=transaction.uuid,
            courier_name=payload.courier_name,
            courier_service=selected_courier.get("service", payload.courier_service),
            recipient_name=getattr(user, "full_name", user.username),
            recipient_phone=getattr(user, "phone", ""),
            shipping_address=(
                f"{address.full_address}, {address.subdistrict or ''}, "
                f"{address.district or ''}, {address.city or ''}, "
                f"{address.province or ''} {address.zip_code}"
            ).strip(", "),
            delivery_status="PENDING",
            shipping_cost=shipping_cost,
            etd=selected_courier.get("etd"),
        )
        session.add(shipment)
        await session.flush()

        try:
            midtrans_resp = await TransactionService._create_midtrans_snap(
                order_id=order_id,
                gross_amount=gross_amount,
                user=user,
                items=payload.items,
                locked_stocks=locked_stocks,
                shipping_cost=shipping_cost,
            )
        except Exception as e:
            logger.error(f"Midtrans error: {e}")
            for item in payload.items:
                locked_stocks[str(item.stock_uuid)].stok += item.quantity
                session.add(locked_stocks[str(item.stock_uuid)])
            transaction.transaction_status = "failed"
            session.add(transaction)
            await session.flush()
            raise ValueError("Gagal membuat pembayaran. Silakan coba lagi.")

        transaction.raw_response = midtrans_resp
        transaction.transaction_status = midtrans_resp.get("transaction_status", "pending")
        transaction.payment_type = midtrans_resp.get("payment_type")
        transaction.transaction_time = _parse_dt(midtrans_resp.get("transaction_time"))
        session.add(transaction)

        await _clear_cart_items(session=session, user_uuid=user.uuid, stock_uuids=stock_uuids)
        await session.commit()

        await _send_transaction_notification(
            session=session, local_user_id=user.uuid,
            title="🛒 Pesanan Baru Dibuat",
            content=f"Pesanan #{order_id} telah dibuat. Silakan selesaikan pembayaran.",
            order_id=order_id,
        )

        return CheckoutResponse(
            order_id=order_id,
            transaction_uuid=str(transaction.uuid),
            items_subtotal=items_subtotal,
            shipping_cost=shipping_cost,
            discount_amount=discount_amount,
            gross_amount=gross_amount,
            transaction_status=transaction.transaction_status,
            snap_token=midtrans_resp.get("token"),
            payment_url=midtrans_resp.get("redirect_url"),
            expiry_time=midtrans_resp.get("expiry_time"),
        )

    # ----------------------------------------------------------
    # MIDTRANS SNAP (dipakai checkout + repay)
    # ----------------------------------------------------------
    @staticmethod
    async def _create_midtrans_snap(
        order_id, gross_amount, user, items, locked_stocks, shipping_cost
    ) -> dict:
        item_details = []
        for item in items:
            stock = locked_stocks[str(item.stock_uuid)]
            item_details.append({
                "id": str(stock.uuid),
                "price": stock.online_price,
                "quantity": item.quantity,
                "name": stock.title[:50],
            })
        if shipping_cost > 0:
            item_details.append({"id": "SHIPPING", "price": shipping_cost, "quantity": 1, "name": "Ongkos Kirim"})

        payload = {
            "payment_type": "qris",
            "transaction_details": {"order_id": order_id, "gross_amount": gross_amount},
            "item_details": item_details,
            "customer_details": {"first_name": user.username, "email": user.email},
            "qris": {"acquirer": "gopay"},
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                MIDTRANS_CHARGE_URL,
                json=payload,
                headers={
                    "Authorization": _midtrans_auth_header(),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            if not resp.is_success:
                raise ValueError(f"Midtrans error {resp.status_code}: {resp.text}")
            return resp.json()

    # ----------------------------------------------------------
    # REPAY — buat ulang Snap token untuk transaksi pending
    # ----------------------------------------------------------
    @staticmethod
    async def repay(*, session: AsyncSession, user_id: UUID, order_id: str) -> dict:
        """
        Membuat ulang Midtrans Snap token.
        Mendukung ORD- (Transaction) dan PROMO- (PromoTransaction).
        Hanya bisa untuk status pending / pending_payment.
        """
        if order_id.startswith("PROMO-"):
            return await TransactionService._repay_promo(
                session=session, user_id=user_id, order_id=order_id
            )
        return await TransactionService._repay_regular(
            session=session, user_id=user_id, order_id=order_id
        )

    @staticmethod
    async def _repay_regular(*, session, user_id, order_id) -> dict:
        result = await session.exec(
            select(Transaction)
            .options(selectinload(Transaction.items))
            .where(Transaction.order_id == order_id, Transaction.user_id == user_id)
        )
        trx = result.one_or_none()
        if not trx:
            raise HTTPException(404, "Transaksi tidak ditemukan")

        if trx.transaction_status in FINAL_STATUSES:
            raise ValueError(f"Transaksi sudah final ({trx.transaction_status}), tidak bisa bayar ulang")

        # Ambil user untuk customer_details
        user_result = await session.exec(
            select(User).where(User.uuid == user_id)
        )
        user = user_result.one_or_none()
        if not user:
            raise HTTPException(404, "User tidak ditemukan")

        # Rebuild item_details dari TransactionItem + Stock
        stock_ids = [i.stock_id for i in trx.items]
        stocks_result = await session.exec(select(Stock).where(Stock.uuid.in_(stock_ids)))
        stock_map = {s.uuid: s for s in stocks_result.all()}

        item_details = []
        for trx_item in trx.items:
            stock = stock_map.get(trx_item.stock_id)
            name = stock.title[:50] if stock else f"Produk {trx_item.stock_id}"
            item_details.append({
                "id": str(trx_item.stock_id),
                "price": trx_item.unit_price,
                "quantity": trx_item.quantity,
                "name": name,
            })
        if trx.shipping_cost > 0:
            item_details.append({"id": "SHIPPING", "price": trx.shipping_cost, "quantity": 1, "name": "Ongkos Kirim"})

        payload = {
            "payment_type": "qris",
            "transaction_details": {"order_id": order_id, "gross_amount": trx.gross_amount},
            "item_details": item_details,
            "customer_details": {"first_name": user.username, "email": user.email},
            "qris": {"acquirer": "gopay"},
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                MIDTRANS_CHARGE_URL,
                json=payload,
                headers={
                    "Authorization": _midtrans_auth_header(),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            if not resp.is_success:
                raise ValueError(f"Midtrans error {resp.status_code}: {resp.text}")
            mt = resp.json()

        # Update raw_response dengan token baru
        trx.raw_response = mt
        session.add(trx)
        await session.commit()

        return {
            "order_id": order_id,
            "trx_type": "regular",
            "gross_amount": trx.gross_amount,
            "snap_token": mt.get("token"),
            "payment_url": mt.get("redirect_url"),
            "expiry_time": mt.get("expiry_time"),
            "transaction_status": trx.transaction_status,
        }

    @staticmethod
    async def _repay_promo(*, session, user_id, order_id) -> dict:
        result = await session.exec(
            select(PromoTransaction)
            .options(selectinload(PromoTransaction.items))
            .where(PromoTransaction.order_id == order_id, PromoTransaction.user_id == user_id)
        )
        promo_trx = result.one_or_none()
        if not promo_trx:
            raise HTTPException(404, "Transaksi promo tidak ditemukan")

        if promo_trx.transaction_status in FINAL_STATUSES:
            raise ValueError(f"Transaksi sudah final ({promo_trx.transaction_status}), tidak bisa bayar ulang")

        user_result = await session.exec(select(User).where(User.uuid == user_id))
        user = user_result.one_or_none()
        if not user:
            raise HTTPException(404, "User tidak ditemukan")

        # Rebuild item_details dari PromoTransactionItem (sudah ada unit_price after discount)
        item_details = []
        for pti in promo_trx.items:
            item_details.append({
                "id": str(pti.stock_uuid or pti.package_uuid),
                "price": pti.unit_price,
                "quantity": pti.quantity,
                "name": pti.item_name[:50],
            })
        if promo_trx.shipping_cost > 0:
            item_details.append({"id": "SHIPPING", "price": promo_trx.shipping_cost, "quantity": 1, "name": "Ongkos Kirim"})
        if promo_trx.service_cost > 0:
            item_details.append({"id": "SERVICE_TRANSPORT", "price": promo_trx.service_cost, "quantity": 1, "name": "Biaya Transport Teknisi"})

        payload = {
            "payment_type": "qris",
            "transaction_details": {"order_id": order_id, "gross_amount": promo_trx.gross_amount},
            "item_details": item_details,
            "customer_details": {"first_name": user.username, "email": user.email},
            "qris": {"acquirer": "gopay"},
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                MIDTRANS_CHARGE_URL,
                json=payload,
                headers={
                    "Authorization": _midtrans_auth_header(),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            if not resp.is_success:
                raise ValueError(f"Midtrans error {resp.status_code}: {resp.text}")
            mt = resp.json()

        promo_trx.raw_response = mt
        session.add(promo_trx)
        await session.commit()

        return {
            "order_id": order_id,
            "trx_type": "promo",
            "gross_amount": promo_trx.gross_amount,
            "snap_token": mt.get("token"),
            "payment_url": mt.get("redirect_url"),
            "expiry_time": mt.get("expiry_time"),
            "transaction_status": promo_trx.transaction_status,
        }

    # ----------------------------------------------------------
    # GET ALL TRANSACTIONS — reguler + promo digabung
    # ----------------------------------------------------------
    @staticmethod
    async def get_all_user_transactions(
        *,
        session: AsyncSession,
        user_id: UUID,
        page: int = 1,
        limit: int = 10,
        sort: str = "desc",
        status: Optional[str] = None,
        trx_type: Optional[str] = None,   # "regular" | "promo" | None
        min_amount: Optional[int] = None,
        max_amount: Optional[int] = None,
    ) -> dict:
        """
        Menggabungkan Transaction (reguler) + PromoTransaction ke satu list,
        diurutkan by created_at (desc/asc).
        """
        combined = []

        # ── 1. Ambil Transaction biasa ─────────────────────────────
        if trx_type in (None, "regular"):
            q = (
                select(Transaction)
                .options(
                    selectinload(Transaction.items),
                    selectinload(Transaction.shipment),
                )
                .where(Transaction.user_id == user_id)
            )
            if status:
                q = q.where(Transaction.transaction_status == status)
            if min_amount is not None:
                q = q.where(Transaction.gross_amount >= min_amount)
            if max_amount is not None:
                q = q.where(Transaction.gross_amount <= max_amount)

            trx_result = await session.exec(q)
            trx_list = trx_result.all()

            # Kumpulkan semua stock_id yang dibutuhkan
            all_stock_ids = []
            for trx in trx_list:
                all_stock_ids.extend([i.stock_id for i in trx.items])

            stock_map: dict = {}
            if all_stock_ids:
                stocks_q = await session.exec(
                    select(Stock)
                    .options(selectinload(Stock.assets))
                    .where(Stock.uuid.in_(all_stock_ids))
                )
                stock_map = {s.uuid: s for s in stocks_q.all()}

            for trx in trx_list:
                items_data = []
                for item in trx.items:
                    stock = stock_map.get(item.stock_id)
                    cover = None
                    if stock and stock.assets:
                        cover = stock.assets[0].url
                    items_data.append({
                        "item_type": "stock",
                        "item_uuid": str(item.stock_id),
                        "item_name": stock.title if stock else None,
                        "item_slug": stock.slug if stock else None,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "original_price": item.unit_price,
                        "discount_value": 0,
                        "subtotal": item.subtotal,
                        "cover_image_url": cover,
                    })

                shipment = trx.shipment
                combined.append({
                    "trx_type": "regular",
                    "uuid": str(trx.uuid),
                    "order_id": trx.order_id,
                    "gross_amount": trx.gross_amount,
                    "items_subtotal": trx.items_subtotal,
                    "total_discount": trx.discount_amount,
                    "shipping_cost": trx.shipping_cost,
                    "service_cost": 0,
                    "transaction_status": trx.transaction_status,
                    "payment_type": trx.payment_type,
                    "transaction_time": trx.transaction_time,
                    "settlement_time": trx.settlement_time,
                    "created_at": trx.created_at,
                    "promo_name": None,
                    "promo_type": None,
                    "items": items_data,
                    "shipment": _format_shipment(shipment),
                    "booking": None,
                    # Info bayar ulang (diisi jika masih pending)
                    "can_repay": trx.transaction_status not in FINAL_STATUSES,
                    "snap_token": (
                        trx.raw_response.get("token")
                        if trx.raw_response and trx.transaction_status not in FINAL_STATUSES
                        else None
                    ),
                    "payment_url": (
                        trx.raw_response.get("redirect_url")
                        if trx.raw_response and trx.transaction_status not in FINAL_STATUSES
                        else None
                    ),
                })

        # ── 2. Ambil PromoTransaction ──────────────────────────────
        if trx_type in (None, "promo"):
            pq = (
                select(PromoTransaction)
                .options(selectinload(PromoTransaction.items))
                .where(PromoTransaction.user_id == user_id)
            )
            if status:
                pq = pq.where(PromoTransaction.transaction_status == status)
            if min_amount is not None:
                pq = pq.where(PromoTransaction.gross_amount >= min_amount)
            if max_amount is not None:
                pq = pq.where(PromoTransaction.gross_amount <= max_amount)

            promo_result = await session.exec(pq)
            promo_list = promo_result.all()

            # Kumpulkan stock_uuid & package_uuid
            all_pstock_ids = []
            all_pkg_ids = []
            for pt in promo_list:
                for pti in pt.items:
                    if pti.stock_uuid:
                        all_pstock_ids.append(pti.stock_uuid)
                    if pti.package_uuid:
                        all_pkg_ids.append(pti.package_uuid)

            pstock_map: dict = {}
            if all_pstock_ids:
                sr = await session.exec(
                    select(Stock)
                    .options(selectinload(Stock.assets))
                    .where(Stock.uuid.in_(all_pstock_ids))
                )
                pstock_map = {s.uuid: s for s in sr.all()}

            pkg_map: dict = {}
            if all_pkg_ids:
                pkgr = await session.exec(
                    select(ServicePackage).where(ServicePackage.uuid.in_(all_pkg_ids))
                )
                pkg_map = {p.uuid: p for p in pkgr.all()}

            # Ambil shipment promo (via promo_transaction_uuid)
            promo_uuids = [pt.uuid for pt in promo_list]
            pshipment_map: dict = {}
            if promo_uuids:
                pship_r = await session.exec(
                    select(Shipment).where(Shipment.promo_transaction_uuid.in_(promo_uuids))
                )
                for s in pship_r.all():
                    pshipment_map[s.promo_transaction_uuid] = s

            # Ambil service_booking (jika ada)
            booking_uuids = [pt.service_booking_uuid for pt in promo_list if pt.service_booking_uuid]
            booking_map: dict = {}
            if booking_uuids:
                bk_r = await session.exec(
                    select(ServiceBooking).where(ServiceBooking.uuid.in_(booking_uuids))
                )
                for b in bk_r.all():
                    booking_map[b.uuid] = b

            for pt in promo_list:
                items_data = []
                for pti in pt.items:
                    cover = None
                    if pti.stock_uuid:
                        stock = pstock_map.get(pti.stock_uuid)
                        if stock and stock.assets:
                            cover = stock.assets[0].url
                    elif pti.package_uuid:
                        pkg = pkg_map.get(pti.package_uuid)
                        if pkg:
                            cover = getattr(pkg, "thumbnail_url", None)

                    items_data.append({
                        "item_type": pti.item_type,
                        "item_uuid": str(pti.stock_uuid or pti.package_uuid),
                        "item_name": pti.item_name,
                        "item_slug": None,
                        "quantity": pti.quantity,
                        "unit_price": pti.unit_price,
                        "original_price": pti.original_price,
                        "discount_value": pti.discount_value,
                        "subtotal": pti.subtotal,
                        "cover_image_url": cover,
                    })

                shipment = pshipment_map.get(pt.uuid)
                booking = booking_map.get(pt.service_booking_uuid) if pt.service_booking_uuid else None
                snapshot = pt.promo_snapshot or {}

                combined.append({
                    "trx_type": "promo",
                    "uuid": str(pt.uuid),
                    "order_id": pt.order_id,
                    "gross_amount": pt.gross_amount,
                    "items_subtotal": pt.items_subtotal_original,
                    "total_discount": pt.total_discount,
                    "shipping_cost": pt.shipping_cost,
                    "service_cost": pt.service_cost,
                    "transaction_status": pt.transaction_status,
                    "payment_type": pt.payment_type,
                    "transaction_time": pt.transaction_time,
                    "settlement_time": pt.settlement_time,
                    "created_at": pt.created_at,
                    "promo_name": snapshot.get("name"),
                    "promo_type": snapshot.get("promo_type"),
                    "items": items_data,
                    "shipment": _format_shipment(shipment),
                    "booking": _format_booking(booking),
                    "can_repay": pt.transaction_status not in FINAL_STATUSES,
                    "snap_token": (
                        pt.raw_response.get("token")
                        if pt.raw_response and pt.transaction_status not in FINAL_STATUSES
                        else None
                    ),
                    "payment_url": (
                        pt.raw_response.get("redirect_url")
                        if pt.raw_response and pt.transaction_status not in FINAL_STATUSES
                        else None
                    ),
                })

        # ── 3. Sort gabungan by created_at ─────────────────────────
        combined.sort(
            key=lambda x: x["created_at"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=(sort == "desc"),
        )

        # ── 4. Pagination ──────────────────────────────────────────
        total = len(combined)
        offset = (page - 1) * limit
        paginated = combined[offset : offset + limit]

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_page": (total + limit - 1) // limit,
            "data": paginated,
        }

    # ----------------------------------------------------------
    # GET DETAIL — Transaction biasa
    # ----------------------------------------------------------
    @staticmethod
    async def get_regular_transaction_detail(
        *, session: AsyncSession, user_id: UUID, order_id: str
    ) -> dict:
        result = await session.exec(
            select(Transaction)
            .options(selectinload(Transaction.shipment), selectinload(Transaction.items))
            .where(Transaction.order_id == order_id, Transaction.user_id == user_id)
        )
        trx = result.one_or_none()
        if not trx:
            raise HTTPException(404, "Transaksi tidak ditemukan")

        stock_ids = [item.stock_id for item in trx.items]
        stock_map = {}
        if stock_ids:
            sr = await session.exec(
                select(Stock).options(selectinload(Stock.assets)).where(Stock.uuid.in_(stock_ids))
            )
            stock_map = {s.uuid: s for s in sr.all()}

        items_data = []
        for item in trx.items:
            stock = stock_map.get(item.stock_id)
            cover = stock.assets[0].url if (stock and stock.assets) else None
            items_data.append({
                "item_type": "stock",
                "item_uuid": str(item.stock_id),
                "item_name": stock.title if stock else None,
                "item_slug": stock.slug if stock else None,
                "original_price": item.unit_price,
                "discount_value": 0,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
                "cover_image_url": cover,
                "specs": stock.specs if stock else {},
                "brand": stock.brand if stock else None,
            })

        shipment = trx.shipment
        return {
            "trx_type": "regular",
            "uuid": str(trx.uuid),
            "order_id": trx.order_id,
            "gross_amount": trx.gross_amount,
            "items_subtotal": trx.items_subtotal,
            "total_discount": trx.discount_amount,
            "shipping_cost": trx.shipping_cost,
            "service_cost": 0,
            "transaction_status": trx.transaction_status,
            "payment_type": trx.payment_type,
            "transaction_time": trx.transaction_time,
            "settlement_time": trx.settlement_time,
            "created_at": trx.created_at,
            "promo_name": None,
            "promo_type": None,
            "items": items_data,
            "shipment": _format_shipment(shipment),
            "booking": None,
            "can_repay": trx.transaction_status not in FINAL_STATUSES,
            "snap_token": (
                trx.raw_response.get("token")
                if trx.raw_response and trx.transaction_status not in FINAL_STATUSES
                else None
            ),
            "payment_url": (
                trx.raw_response.get("redirect_url")
                if trx.raw_response and trx.transaction_status not in FINAL_STATUSES
                else None
            ),
            "raw_response": trx.raw_response,
        }

    # ----------------------------------------------------------
    # GET DETAIL — PromoTransaction
    # ----------------------------------------------------------
    @staticmethod
    async def get_promo_transaction_detail(
        *, session: AsyncSession, user_id: UUID, order_id: str
    ) -> dict:
        result = await session.exec(
            select(PromoTransaction)
            .options(selectinload(PromoTransaction.items))
            .where(PromoTransaction.order_id == order_id, PromoTransaction.user_id == user_id)
        )
        pt = result.one_or_none()
        if not pt:
            raise HTTPException(404, "Transaksi promo tidak ditemukan")

        # Items — ambil stock & package
        stock_ids = [pti.stock_uuid for pti in pt.items if pti.stock_uuid]
        pkg_ids = [pti.package_uuid for pti in pt.items if pti.package_uuid]

        stock_map: dict = {}
        if stock_ids:
            sr = await session.exec(
                select(Stock).options(selectinload(Stock.assets)).where(Stock.uuid.in_(stock_ids))
            )
            stock_map = {s.uuid: s for s in sr.all()}

        pkg_map: dict = {}
        if pkg_ids:
            pkgr = await session.exec(select(ServicePackage).where(ServicePackage.uuid.in_(pkg_ids)))
            pkg_map = {p.uuid: p for p in pkgr.all()}

        items_data = []
        for pti in pt.items:
            cover = None
            extra = {}
            if pti.stock_uuid:
                stock = stock_map.get(pti.stock_uuid)
                if stock:
                    cover = stock.assets[0].url if stock.assets else None
                    extra = {"specs": stock.specs, "brand": stock.brand, "item_slug": stock.slug}
            elif pti.package_uuid:
                pkg = pkg_map.get(pti.package_uuid)
                if pkg:
                    cover = getattr(pkg, "thumbnail_url", None)
                    extra = {"item_slug": pkg.slug}

            items_data.append({
                "item_type": pti.item_type,
                "item_uuid": str(pti.stock_uuid or pti.package_uuid),
                "item_name": pti.item_name,
                "original_price": pti.original_price,
                "discount_value": pti.discount_value,
                "unit_price": pti.unit_price,
                "quantity": pti.quantity,
                "subtotal": pti.subtotal,
                "cover_image_url": cover,
                **extra,
            })

        # Shipment
        ship_r = await session.exec(
            select(Shipment).where(Shipment.promo_transaction_uuid == pt.uuid)
        )
        shipment = ship_r.one_or_none()

        # Booking
        booking = None
        if pt.service_booking_uuid:
            bk_r = await session.exec(
                select(ServiceBooking).where(ServiceBooking.uuid == pt.service_booking_uuid)
            )
            booking = bk_r.one_or_none()

        snapshot = pt.promo_snapshot or {}

        return {
            "trx_type": "promo",
            "uuid": str(pt.uuid),
            "order_id": pt.order_id,
            "gross_amount": pt.gross_amount,
            "items_subtotal_original": pt.items_subtotal_original,
            "items_subtotal_discounted": pt.items_subtotal_discounted,
            "total_discount": pt.total_discount,
            "shipping_cost": pt.shipping_cost,
            "service_cost": pt.service_cost,
            "transaction_status": pt.transaction_status,
            "payment_type": pt.payment_type,
            "transaction_time": pt.transaction_time,
            "settlement_time": pt.settlement_time,
            "created_at": pt.created_at,
            "promo_uuid": str(pt.promo_uuid),
            "promo_name": snapshot.get("name"),
            "promo_type": snapshot.get("promo_type"),
            "promo_discount_value": snapshot.get("discount_value"),
            "items": items_data,
            "shipment": _format_shipment(shipment),
            "booking": _format_booking(booking),
            "can_repay": pt.transaction_status not in FINAL_STATUSES,
            "snap_token": (
                pt.raw_response.get("token")
                if pt.raw_response and pt.transaction_status not in FINAL_STATUSES
                else None
            ),
            "payment_url": (
                pt.raw_response.get("redirect_url")
                if pt.raw_response and pt.transaction_status not in FINAL_STATUSES
                else None
            ),
            "raw_response": pt.raw_response,
        }

    # ----------------------------------------------------------
    # WEBHOOK
    # ----------------------------------------------------------
    @staticmethod
    async def handle_webhook(*, session, payload: MidtransWebhookPayload) -> dict:
        order_id = payload.order_id or ""
        if order_id.startswith("BK-"):
            from backend.data.jasa.service import PaymentService,MidtransService
            from backend.config import Config
            midtrans = MidtransService(
            server_key=Config.MIDTRANS_SERVER_KEY,
            is_production='false',
        )
            payment_service = PaymentService(midtrans=midtrans)

            return await payment_service.handle_service_webhook(
                session=session,
                payload=payload,
            )
           
        if order_id.startswith("PROMO-"):
            from backend.data.public.promobanner.service import PromoCheckoutService
            return await PromoCheckoutService().handle_webhook(session=session, payload=payload)
        return await TransactionService._handle_goods_webhook(session=session, payload=payload)

    @staticmethod
    async def _handle_goods_webhook(*, session, payload: MidtransWebhookPayload) -> dict:
        if payload.signature_key and payload.status_code and payload.gross_amount:
            if not verify_midtrans_signature(
                payload.order_id, payload.status_code, payload.gross_amount, payload.signature_key
            ):
                raise PermissionError("Invalid signature")

        trx_result = await session.exec(
            select(Transaction).where(Transaction.order_id == payload.order_id)
        )
        trx = trx_result.one_or_none()
        if not trx:
            logger.warning(f"Webhook: order_id tidak ditemukan: {payload.order_id}")
            return {"status": "ignored", "reason": "order_id not found"}

        if trx.transaction_status in FINAL_STATUSES:
            return {"status": "skipped", "reason": "already final"}

        items_result = await session.exec(
            select(TransactionItem).where(TransactionItem.transaction_id == trx.uuid)
        )
        trx_items = items_result.all()

        old_status = trx.transaction_status
        trx.transaction_status = payload.transaction_status
        trx.payment_type = payload.payment_type
        trx.fraud_status = payload.fraud_status
        trx.status_code = payload.status_code
        trx.raw_response = payload.model_dump()
        if payload.transaction_time:
            trx.transaction_time = _parse_dt(payload.transaction_time)
        if payload.settlement_time:
            trx.settlement_time = _parse_dt(payload.settlement_time)
        session.add(trx)

        notif_title, notif_content = "", ""

        if payload.transaction_status in {"settlement", "capture"}:
            if not (payload.fraud_status and payload.fraud_status == "challenge"):
                for trx_item in trx_items:
                    sr = await session.exec(select(Stock).where(Stock.uuid == trx_item.stock_id))
                    stock = sr.one_or_none()
                    if stock:
                        stock.terjual += trx_item.quantity
                        session.add(stock)
                ship_r = await session.exec(select(Shipment).where(Shipment.transaction_uuid == trx.uuid))
                shipment = ship_r.one_or_none()
                if shipment:
                    shipment.delivery_status = "PROCESSING"
                    session.add(shipment)
                notif_title = "✅ Pembayaran Berhasil"
                notif_content = f"Pembayaran pesanan #{payload.order_id} dikonfirmasi."

        elif payload.transaction_status in {"cancel", "deny", "expire"}:
            for trx_item in trx_items:
                sr = await session.exec(select(Stock).where(Stock.uuid == trx_item.stock_id))
                stock = sr.one_or_none()
                if stock:
                    stock.stok += trx_item.quantity
                    session.add(stock)
            ship_r = await session.exec(select(Shipment).where(Shipment.transaction_uuid == trx.uuid))
            shipment = ship_r.one_or_none()
            if shipment:
                shipment.delivery_status = "CANCELLED"
                session.add(shipment)
            label = {"cancel": "dibatalkan", "deny": "ditolak", "expire": "kedaluwarsa"}.get(
                payload.transaction_status, payload.transaction_status
            )
            notif_title = f"❌ Pesanan {label.capitalize()}"
            notif_content = f"Pesanan #{payload.order_id} {label}."

        if notif_title and old_status != payload.transaction_status:
            await _send_transaction_notification(
                session=session, local_user_id=trx.user_id,
                title=notif_title, content=notif_content, order_id=payload.order_id,
            )

        await session.commit()
        return {"status": "ok", "order_id": payload.order_id, "new_status": trx.transaction_status}

    # ----------------------------------------------------------
    # GET HISTORY — reguler only (backward compat)
    # ----------------------------------------------------------
    @staticmethod
    async def get_user_transactions(
        *, session, user_id, page=1, limit=10, sort="desc", sort_by="created_at",
        stock_id=None, stock_name=None, status=None, min_amount=None, max_amount=None,
    ):
        offset = (page - 1) * limit
        query = (
            select(Transaction, TransactionItem, Stock)
            .join(TransactionItem, TransactionItem.transaction_id == Transaction.uuid)
            .join(Stock, Stock.uuid == TransactionItem.stock_id)
            .where(Transaction.user_id == user_id)
            .options(selectinload(Transaction.shipment), selectinload(Stock.assets))
        )
        if status:
            query = query.where(Transaction.transaction_status == status)
        if min_amount is not None:
            query = query.where(Transaction.gross_amount >= min_amount)
        if max_amount is not None:
            query = query.where(Transaction.gross_amount <= max_amount)
        if stock_id:
            query = query.where(TransactionItem.stock_id == stock_id)
        if stock_name:
            query = query.where(Stock.title.ilike(f"%{stock_name}%"))

        sort_col = getattr(Transaction, sort_by)
        query = query.order_by(asc(sort_col) if sort == "asc" else desc(sort_col))
        rows = (await session.exec(query)).all()

        trx_map = {}
        for trx, item, stock in rows:
            if trx.uuid not in trx_map:
                trx_map[trx.uuid] = {
                    "uuid": str(trx.uuid),
                    "order_id": trx.order_id,
                    "gross_amount": trx.gross_amount,
                    "items_subtotal": trx.items_subtotal,
                    "shipping_cost": trx.shipping_cost,
                    "transaction_status": trx.transaction_status,
                    "payment_type": trx.payment_type,
                    "transaction_time": trx.transaction_time,
                    "settlement_time": trx.settlement_time,
                    "created_at": trx.created_at,
                    "items": [],
                    "shipment": _format_shipment(trx.shipment) if trx.shipment else None,
                    "can_repay": trx.transaction_status not in FINAL_STATUSES,
                }
            cover = next(
                (a.url for a in stock.assets if a.uuid == stock.asset_uuid),
                stock.assets[0].url if stock.assets else None,
            )
            trx_map[trx.uuid]["items"].append({
                "stock_uuid": str(stock.uuid),
                "stock_title": stock.title,
                "stock_slug": stock.slug,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal,
                "cover_image_url": cover,
            })

        trx_list = list(trx_map.values())
        total = len(trx_list)
        return {
            "page": page, "limit": limit, "total": total,
            "total_page": (total + limit - 1) // limit,
            "data": trx_list[offset : offset + limit],
        }

    # ----------------------------------------------------------
    # INTERNAL: Validate coupon
    # ----------------------------------------------------------
    @staticmethod
    async def _validate_coupon(session, code, subtotal):
        now = datetime.now(timezone.utc)
        result = await session.exec(
            select(Coupon)
            .where(Coupon.code == code.upper())
            .where(Coupon.is_active == True)
            .where(Coupon.used_count < Coupon.quota)
        )
        coupon = result.one_or_none()
        if not coupon:
            raise ValueError("Kupon tidak valid atau sudah habis")
        if coupon.valid_from and now < coupon.valid_from:
            raise ValueError("Kupon belum berlaku")
        if coupon.valid_until and now > coupon.valid_until:
            raise ValueError("Kupon sudah kadaluarsa")
        if subtotal < coupon.min_purchase:
            raise ValueError(f"Minimal pembelian Rp{coupon.min_purchase:,} untuk kupon ini")
        return coupon


# ============================================================
# FORMAT HELPERS
# ============================================================

def _format_shipment(shipment) -> Optional[dict]:
    if not shipment:
        return None
    return {
        "waybill_number": shipment.waybill_number,
        "delivery_status": shipment.delivery_status,
        "courier_name": shipment.courier_name,
        "courier_service": shipment.courier_service,
        "recipient_name": shipment.recipient_name,
        "recipient_phone": shipment.recipient_phone,
        "shipping_address": shipment.shipping_address,
        "etd": getattr(shipment, "etd", None),
    }


def _format_booking(booking) -> Optional[dict]:
    if not booking:
        return None
    return {
        "booking_number": booking.booking_number,
        "status": booking.status,
        "scheduled_date": str(booking.scheduled_date) if booking.scheduled_date else None,
        "time_slot": booking.time_slot,
        "address": booking.address,
        "district": booking.district,
        "city": booking.city,
        "contact_name": booking.contact_name,
        "contact_phone": booking.contact_phone,
    }