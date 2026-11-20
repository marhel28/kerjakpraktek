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
from backend.data.public.addon.model import AddonItem, ProductAddonOverride
from backend.data.jasa.model import ServicePackage, ServiceBooking
from backend.data.stock.service import StockService
from backend.data.activity.service import ActivityService

logger = logging.getLogger(__name__)
stock_service = StockService()


# ============================================================
# HELPERS
# ============================================================

def _midtrans_auth_header() -> str:
    raw = f"{Config.MIDTRANS_SERVER_KEY}:"
    return "Basic " + base64.b64encode(raw.encode()).decode()


MIDTRANS_SNAP_URL = "https://app.sandbox.midtrans.com/snap/v1/transactions"
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


async def _send_notification_to_admins(
    session: AsyncSession, title: str, content: str, action_url: str, notif_type: str = "order"
):
    try:
        from backend.auth.model import User, UserMap, UserRole
        # 1. Get all local admin users
        admin_users_query = select(User).where(User.role == UserRole.ADMIN)
        admin_users_result = await session.execute(admin_users_query)
        admin_users = admin_users_result.scalars().all()
        
        if not admin_users:
            return
        
        # 2. Get Supabase User IDs for all admin users
        admin_uuids = [str(u.uuid) for u in admin_users]
        user_maps_query = select(UserMap).where(UserMap.local_user_id.in_(admin_uuids))
        user_maps_result = await session.execute(user_maps_query)
        user_maps = user_maps_result.scalars().all()
        
        supabase_admin_ids = [m.supabase_user_id for m in user_maps if m.supabase_user_id]
        
        if not supabase_admin_ids:
            return
        
        # 3. Send bulk notification
        await SupabaseNotificationService.bulk_notification(
            user_ids=supabase_admin_ids,
            title=title,
            content=content,
            action_url=action_url,
            notif_type=notif_type,
        )
    except Exception as e:
        logger.error(f"Failed to send notification to admins: {e}")


async def _clear_cart_items(session, user_uuid, stock_uuids):
    """Hapus item dari keranjang setelah checkout sukses."""
    try:
        if not stock_uuids:
            return
        
        # Gunakan query DELETE yang lebih efisien (batch delete)
        from sqlalchemy import delete
        stmt = (
            delete(Cart)
            .where(Cart.user_uuid == user_uuid)
            .where(Cart.stock_uuid.in_(stock_uuids))
        )
        await session.execute(stmt)
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

        # ── 1.2. Validasi stok dan hitung berat dasar ─────────────
        sorted_items = sorted(payload.items, key=lambda i: str(i.stock_uuid))
        locked_stocks: dict[str, Stock] = {}
        total_weight = 0

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
            total_weight += stock.weight * item.quantity

        # ── 1.3. Ambil data Addon & Hitung tambahan berat ──────────
        addon_data_map: dict = {}
        from sqlalchemy import and_
        for item in payload.items:
            if not item.addons: continue
            for a in item.addons:
                addon_stmt = select(AddonItem).where(AddonItem.uuid == a.addon_uuid)
                addon_res = await session.execute(addon_stmt)
                addon_item = addon_res.scalar_one_or_none()
                if not addon_item:
                    raise ValueError(f"Addon {a.addon_uuid} tidak ditemukan")
                
                # Cek override harga/stok
                ov_stmt = select(ProductAddonOverride).where(and_(
                    ProductAddonOverride.product_uuid == item.stock_uuid,
                    ProductAddonOverride.addon_item_uuid == addon_item.uuid
                ))
                ov_res = await session.execute(ov_stmt)
                override = ov_res.scalar_one_or_none()
                
                final_price = override.override_price if override and override.override_price is not None else addon_item.price
                
                addon_data_map[str(a.addon_uuid)] = {
                    "item": addon_item,
                    "final_price": final_price,
                    "name": addon_item.name,
                    "weight": addon_item.weight
                }
                total_weight += addon_item.weight * a.quantity

        # ── 1.4. Cek Ongkir dengan Berat Riil ──────────────────────
        addr_result = await session.exec(
            select(UserAddress)
            .where(UserAddress.uuid == payload.address_uuid)
            .where(UserAddress.user_id == user.uuid)
        )
        address = addr_result.one_or_none()
        if not address:
            raise ValueError("Alamat tidak ditemukan atau bukan milik Anda")

        # Minimal berat 100g
        shipping_weight = max(total_weight, 100)

        ongkir_api = OngkirAPI(api_key=Config.SHIPPING_COST)
        ongkir_result = ongkir_api.cek_ongkir(
            destination=address.location_id,
            weight=shipping_weight,
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

        items_subtotal = 0
        for item in payload.items:
            stock = locked_stocks[str(item.stock_uuid)]
            item_total = stock.online_price * item.quantity
            if item.addons:
                for a in item.addons:
                    item_total += addon_data_map[str(a.addon_uuid)]["final_price"] * a.quantity
            items_subtotal += item_total

        discount_amount = 0
        applied_coupon = None
        if payload.coupon_code:
            v_res = await stock_service.validate_coupon(
                session=session, code=payload.coupon_code, cart_total=items_subtotal
            )
            if not v_res["is_valid"]:
                raise ValueError(v_res["message"])
            
            discount_amount = v_res["data"]["discount_amount"]
            applied_coupon = v_res["data"]["coupon_code"]
            
            # Atomic use
            used = await stock_service.increment_coupon_usage(session, applied_coupon)
            if not used:
                raise ValueError("Kuota kupon sudah habis saat checkout")

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
            coupon_code=applied_coupon,
            transaction_status="pending_payment",
        )
        session.add(transaction)
        await session.flush()

        for item in payload.items:
            stock = locked_stocks[str(item.stock_uuid)]
            addon_snapshots = []
            if item.addons:
                for a in item.addons:
                    ad = addon_data_map[str(a.addon_uuid)]
                    addon_snapshots.append({
                        "uuid": str(a.addon_uuid),
                        "name": ad["name"],
                        "price": ad["final_price"],
                        "quantity": a.quantity
                    })

            trx_item = TransactionItem(
                transaction_id=transaction.uuid,
                stock_id=stock.uuid,
                quantity=item.quantity,
                unit_price=stock.online_price,
                subtotal=stock.online_price * item.quantity,
                addons=addon_snapshots if addon_snapshots else None
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
            midtrans_resp = await TransactionService._create_snap_transaction(
                order_id=order_id,
                gross_amount=gross_amount,
                user=user,
                items=payload.items,
                locked_stocks=locked_stocks,
                shipping_cost=shipping_cost,
                addon_data_map=addon_data_map,
                discount_amount=discount_amount,
                payment_type=payload.payment_type
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
        transaction.transaction_status = "pending"
        transaction.payment_type = "midtrans_snap"
        transaction.transaction_time = datetime.now(timezone.utc)
        session.add(transaction)

        await _clear_cart_items(session=session, user_uuid=user.uuid, stock_uuids=stock_uuids)
        
        # 📝 Log Activity
        await ActivityService(session).log_activity(
            activity_type="order",
            title="🛒 Pesanan Baru",
            description=f"Pesanan {order_id} dibuat oleh {user.username}",
            reference_id=order_id,
            user_id=user.uuid,
            status="pending",
            amount=int(gross_amount),
            icon="i-heroicons-shopping-cart",
            color="blue"
        )
        
        await session.commit()

        await _send_transaction_notification(
            session=session, local_user_id=user.uuid,
            title="🛒 Pesanan Baru Dibuat",
            content=f"Pesanan #{order_id} telah dibuat. Silakan selesaikan pembayaran.",
            order_id=order_id,
        )

        await _send_notification_to_admins(
            session=session,
            title="Pesanan Baru! 🛒",
            content=f"Pesanan {order_id} sebesar Rp{int(gross_amount):,} menunggu pembayaran.",
            action_url=f"/transaksi/{order_id}",
            notif_type="order",
        )

        return CheckoutResponse(
            order_id=order_id,
            transaction_uuid=str(transaction.uuid),
            items_subtotal=items_subtotal,
            shipping_cost=shipping_cost,
            discount_amount=discount_amount,
            gross_amount=gross_amount,
            payment_type=payload.payment_type,
            transaction_status=transaction.transaction_status,
            va_numbers=midtrans_resp.get("va_numbers"),
            payment_url=midtrans_resp.get("redirect_url"),
            expiry_time=midtrans_resp.get("expiry_time"),
        )

    # ----------------------------------------------------------
    # MIDTRANS SNAP API (dipakai checkout + repay)
    # ----------------------------------------------------------
    @staticmethod
    async def _create_snap_transaction(
        order_id, gross_amount, user, items, locked_stocks, shipping_cost, addon_data_map=None, discount_amount=0, payment_type=None
    ) -> dict:
        item_details = []
        for item in items:
            stock = locked_stocks[str(item.stock_uuid)]
            item_details.append({
                "id": str(stock.uuid)[:50],
                "price": stock.online_price,
                "quantity": item.quantity,
                "name": stock.title[:50],
            })
            if item.addons and addon_data_map:
                for a in item.addons:
                    ad = addon_data_map[str(a.addon_uuid)]
                    item_details.append({
                        "id": f"ADDON-{str(a.addon_uuid)[:8]}",
                        "price": ad["final_price"],
                        "quantity": a.quantity,
                        "name": f"↳ {ad['name'][:45]}",
                    })
        
        if shipping_cost > 0:
            item_details.append({"id": "SHIPPING", "price": shipping_cost, "quantity": 1, "name": "Ongkos Kirim"})
            
        if discount_amount > 0:
            item_details.append({
                "id": "DISCOUNT",
                "price": -int(discount_amount),
                "quantity": 1,
                "name": "Diskon / Kupon"
            })

        payload = {
            "transaction_details": {"order_id": order_id, "gross_amount": int(gross_amount)},
            "item_details": item_details,
            "customer_details": {"first_name": user.username, "email": user.email},
            "custom_expiry": {"order_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z"), "expiry_duration": 1440, "unit": "minute"}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                MIDTRANS_SNAP_URL,
                json=payload,
                headers={
                    "Authorization": _midtrans_auth_header(),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            if not resp.is_success:
                logger.error(f"Midtrans error: {resp.text}")
                raise ValueError(f"Midtrans error {resp.status_code}")
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
            
            # 1. Main product
            item_details.append({
                "id": str(trx_item.stock_id),
                "price": trx_item.unit_price,
                "quantity": trx_item.quantity,
                "name": name,
            })
            
            # 2. Addons if any
            if trx_item.addons:
                for a in trx_item.addons:
                    item_details.append({
                        "id": f"ADDON-{str(a['uuid'])[:8]}",
                        "price": a["price"],
                        "quantity": a["quantity"],
                        "name": f"↳ {a['name'][:45]}",
                    })

        # 3. Shipping
        if trx.shipping_cost > 0:
            item_details.append({
                "id": "SHIPPING", 
                "price": trx.shipping_cost, 
                "quantity": 1, 
                "name": "Ongkos Kirim"
            })
            
        # 4. Discount (Coupon)
        if trx.discount_amount > 0:
            item_details.append({
                "id": "DISCOUNT", 
                "price": -int(trx.discount_amount), 
                "quantity": 1, 
                "name": "Diskon / Kupon"
            })

        midtrans_order_id = f"{order_id}-R-{int(datetime.now().timestamp())}"

        payload = {
            "transaction_details": {"order_id": midtrans_order_id, "gross_amount": trx.gross_amount},
            "item_details": item_details,
            "customer_details": {"first_name": user.username, "email": user.email},
            "custom_expiry": {"order_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z"), "expiry_duration": 1440, "unit": "minute"}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                MIDTRANS_SNAP_URL,
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
            "success": True,
            "message": "Token pembayaran berhasil diperbarui",
            "data": {
                "order_id": order_id,
                "trx_type": "regular",
                "gross_amount": trx.gross_amount,
                "snap_token": mt.get("token"),
                "payment_url": mt.get("redirect_url"),
                "expiry_time": mt.get("expiry_time"),
                "transaction_status": trx.transaction_status,
            }
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

        midtrans_order_id = f"{order_id}-R-{int(datetime.now().timestamp())}"

        payload = {
            "transaction_details": {"order_id": midtrans_order_id, "gross_amount": promo_trx.gross_amount},
            "item_details": item_details,
            "customer_details": {"first_name": user.username, "email": user.email},
            "custom_expiry": {"order_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z"), "expiry_duration": 1440, "unit": "minute"}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                MIDTRANS_SNAP_URL,
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
            "success": True,
            "message": "Token pembayaran promo berhasil diperbarui",
            "data": {
                "order_id": order_id,
                "trx_type": "promo",
                "gross_amount": promo_trx.gross_amount,
                "snap_token": mt.get("token"),
                "payment_url": mt.get("redirect_url"),
                "expiry_time": mt.get("expiry_time"),
                "transaction_status": promo_trx.transaction_status,
            }
        }

    # ----------------------------------------------------------
    # CONFIRM DELIVERY — user konfirmasi barang sampai
    # ----------------------------------------------------------
    @staticmethod
    async def confirm_delivery(*, session: AsyncSession, user_id: UUID, order_id: str) -> dict:
        """
        User mengonfirmasi barang sudah sampai (delivery_status = 'DELIVERED').
        Mendukung order_id regular (ORD-) maupun promo (PROMO-).
        """
        if order_id.startswith("PROMO-"):
            query = select(PromoTransaction).where(
                PromoTransaction.order_id == order_id,
                PromoTransaction.user_id == user_id
            )
            result = await session.execute(query)
            trx = result.scalar_one_or_none()
            if not trx:
                raise HTTPException(status_code=404, detail="Transaksi promo tidak ditemukan")
            
            ship_query = select(Shipment).where(Shipment.promo_transaction_uuid == trx.uuid)
            ship_result = await session.execute(ship_query)
            shipment = ship_result.scalar_one_or_none()
        else:
            query = select(Transaction).where(
                Transaction.order_id == order_id,
                Transaction.user_id == user_id
            )
            result = await session.execute(query)
            trx = result.scalar_one_or_none()
            if not trx:
                raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
            
            ship_query = select(Shipment).where(Shipment.transaction_uuid == trx.uuid)
            ship_result = await session.execute(ship_query)
            shipment = ship_result.scalar_one_or_none()

        if not shipment:
            raise HTTPException(status_code=400, detail="Pengiriman tidak ditemukan untuk pesanan ini")

        if shipment.delivery_status == "DELIVERED":
            return {
                "success": True,
                "message": "Pesanan sudah dikonfirmasi selesai sebelumnya",
                "data": {"delivery_status": shipment.delivery_status}
            }

        shipment.delivery_status = "DELIVERED"
        session.add(shipment)
        await session.commit()
        await session.refresh(shipment)

        # Kirim notifikasi ke admin
        await _send_notification_to_admins(
            session=session,
            title="Pesanan Diterima Pelanggan! 🎉",
            content=f"Pelanggan telah mengonfirmasi bahwa pesanan {order_id} sudah sampai/diterima.",
            action_url=f"/transaksi/{order_id}",
            notif_type="order",
        )

        # Feedback ke user
        try:
            await _send_transaction_notification(
                session=session, local_user_id=user_id,
                title="✅ Terima Kasih! Pesanan Selesai",
                content=f"Pesanan #{order_id} telah dikonfirmasi diterima. Terima kasih telah berbelanja!",
                order_id=order_id,
            )
        except Exception as e:
            logger.error(f"Failed to send delivery confirm feedback to user: {e}")

        return {
            "success": True,
            "message": "Berhasil mengonfirmasi pesanan telah sampai",
            "data": {"delivery_status": shipment.delivery_status}
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
        total = 0
        offset = (page - 1) * limit

        # ── 1. Ambil Transaction biasa ─────────────────────────────
        if trx_type in (None, "regular"):
            count_q = select(func.count()).select_from(Transaction).where(Transaction.user_id == user_id)
            q = (
                select(Transaction)
                .options(
                    selectinload(Transaction.items),
                    selectinload(Transaction.shipment),
                )
                .where(Transaction.user_id == user_id)
            )
            if status:
                count_q = count_q.where(Transaction.transaction_status == status)
                q = q.where(Transaction.transaction_status == status)
            if min_amount is not None:
                count_q = count_q.where(Transaction.gross_amount >= min_amount)
                q = q.where(Transaction.gross_amount >= min_amount)
            if max_amount is not None:
                count_q = count_q.where(Transaction.gross_amount <= max_amount)
                q = q.where(Transaction.gross_amount <= max_amount)

            reg_count = (await session.exec(count_q)).one()
            total += reg_count

            order_col = desc(Transaction.created_at) if sort == "desc" else asc(Transaction.created_at)
            if trx_type == "regular":
                q = q.order_by(order_col).offset(offset).limit(limit)
            else:
                q = q.order_by(order_col).limit(offset + limit)

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
                        "addons": item.addons,
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
            count_pq = select(func.count()).select_from(PromoTransaction).where(PromoTransaction.user_id == user_id)
            pq = (
                select(PromoTransaction)
                .options(selectinload(PromoTransaction.items))
                .where(PromoTransaction.user_id == user_id)
            )
            if status:
                count_pq = count_pq.where(PromoTransaction.transaction_status == status)
                pq = pq.where(PromoTransaction.transaction_status == status)
            if min_amount is not None:
                count_pq = count_pq.where(PromoTransaction.gross_amount >= min_amount)
                pq = pq.where(PromoTransaction.gross_amount >= min_amount)
            if max_amount is not None:
                count_pq = count_pq.where(PromoTransaction.gross_amount <= max_amount)
                pq = pq.where(PromoTransaction.gross_amount <= max_amount)

            promo_count = (await session.exec(count_pq)).one()
            total += promo_count

            order_pcol = desc(PromoTransaction.created_at) if sort == "desc" else asc(PromoTransaction.created_at)
            if trx_type == "promo":
                pq = pq.order_by(order_pcol).offset(offset).limit(limit)
            else:
                pq = pq.order_by(order_pcol).limit(offset + limit)

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
        def _get_sort_key(x):
            val = x.get("created_at")
            if not val:
                return datetime.min.replace(tzinfo=timezone.utc)
            # Pastikan aware untuk perbandingan
            if val.tzinfo is None:
                val = val.replace(tzinfo=timezone.utc)
            return val

        # ── 4. Pagination ──────────────────────────────────────────
        if trx_type in ("regular", "promo"):
            paginated = combined
        else:
            combined.sort(key=_get_sort_key, reverse=(sort == "desc"))
            paginated = combined[offset : offset + limit]

        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        return {
            "success": True,
            "message": "Riwayat transaksi berhasil diambil",
            "data": paginated,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_page": total_pages,
            }
        }

    # ----------------------------------------------------------
    # GET DETAIL — Transaction biasa
    # ----------------------------------------------------------
    @staticmethod
    async def get_regular_transaction_detail(
        *, session: AsyncSession, user_id: Optional[UUID] = None, order_id: str
    ) -> dict:
        query = select(Transaction).options(selectinload(Transaction.shipment), selectinload(Transaction.items)).where(Transaction.order_id == order_id)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        
        result = await session.exec(query)
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
                "addons": item.addons,
            })

        shipment = trx.shipment
        return {
            "success": True,
            "message": "Detail transaksi berhasil diambil",
            "data": {
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
        }

    # ----------------------------------------------------------
    # GET DETAIL — PromoTransaction
    # ----------------------------------------------------------
    @staticmethod
    async def get_promo_transaction_detail(
        *, session: AsyncSession, user_id: Optional[UUID] = None, order_id: str
    ) -> dict:
        query = select(PromoTransaction).options(selectinload(PromoTransaction.items)).where(PromoTransaction.order_id == order_id)
        if user_id:
            query = query.where(PromoTransaction.user_id == user_id)
            
        result = await session.exec(query)
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
            "success": True,
            "message": "Detail transaksi promo berhasil diambil",
            "data": {
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
        }

    # ----------------------------------------------------------
    # GET DETAIL — ServiceBooking (BK-)
    # ----------------------------------------------------------
    @staticmethod
    async def get_jasa_transaction_detail(
        *, session: AsyncSession, user_id: Optional[UUID] = None, order_id: str
    ) -> dict:
        from backend.data.jasa.model import ServiceBooking, ServicePayment, ServicePackage
        
        # Cari booking berdasarkan booking_number atau order_id di payment
        booking_number = order_id.split("-dp")[0].split("-lunas")[0]
        
        query = select(ServiceBooking).where(ServiceBooking.booking_number == booking_number).options(
            selectinload(ServiceBooking.technician)
        )
        result = await session.exec(query)
        booking = result.one_or_none()
        
        if not booking:
            # Fallback cari via ServicePayment.order_id
            pay_query = select(ServicePayment).where(ServicePayment.order_id == order_id)
            pay_res = await session.exec(pay_query)
            payment = pay_res.one_or_none()
            if payment:
                query = select(ServiceBooking).where(ServiceBooking.uuid == payment.booking_uuid)
                if user_id: query = query.where(ServiceBooking.user_uuid == user_id)
                query = query.options(selectinload(ServiceBooking.technician))
                result = await session.exec(query)
                booking = result.one_or_none()

        if not booking:
            raise HTTPException(404, "Data booking jasa tidak ditemukan")

        # Ambil paket jika ada
        package = None
        if booking.package_uuid:
            pkg_res = await session.exec(select(ServicePackage).where(ServicePackage.uuid == booking.package_uuid))
            package = pkg_res.one_or_none()

        # Ambil payment terakhir yang sukses atau pending
        pay_query = select(ServicePayment).where(ServicePayment.booking_uuid == booking.uuid).order_by(ServicePayment.created_at.desc())
        pay_res = await session.exec(pay_query)
        payments = pay_res.all()
        
        latest_payment = payments[0] if payments else None

        # Map ke format yang kompatibel dengan frontend order detail
        items_data = [{
            "item_type": "service_package" if booking.package_uuid else "custom_service",
            "item_uuid": str(booking.package_uuid or booking.uuid),
            "item_name": package.name if package else f"Layanan {booking.category}",
            "original_price": booking.total_price,
            "discount_value": 0,
            "unit_price": booking.total_price,
            "quantity": 1,
            "subtotal": booking.total_price,
            "cover_image_url": package.thumbnail_url if package else None,
            "specs": {
                "category": booking.category,
                "camera": f"{booking.camera_count} Titik",
                "brand": booking.brand,
                "scheduled": str(booking.scheduled_date),
                "slot": booking.time_slot
            },
            "brand": booking.brand,
            "addons": [{"name": a, "quantity": 1, "price": 0} for a in (booking.addons or [])]
        }]

        # Mapping status booking ke status transaksi agar stepper frontend jalan
        # Booking: pending, confirmed, dp_paid, progress, done, lunas, cancel
        status_map = {
            "pending": "pending",
            "confirmed": "pending",
            "dp_paid": "settlement",
            "progress": "settlement",
            "done": "settlement",
            "lunas": "settlement",
            "cancel": "cancel"
        }

        # Buat Timeline/History
        timeline = []
        timeline.append({"event": "Booking Dibuat", "timestamp": booking.created_at, "status": "done"})
        
        # DP Payment info
        dp_payment = next((p for p in payments if p.payment_type == "dp" and p.status == "success"), None)
        if dp_payment:
            timeline.append({"event": "DP Berhasil Dibayar", "timestamp": dp_payment.paid_at, "status": "done"})
        elif booking.status != "pending":
            timeline.append({"event": "Menunggu Pembayaran DP", "timestamp": None, "status": "pending"})

        # Pengerjaan
        if booking.status in ["progress", "done", "lunas"]:
            # Gunakan paid_at DP sebagai patokan mulai pengerjaan jika tidak ada field khusus
            ts = dp_payment.paid_at if dp_payment else booking.updated_at
            timeline.append({"event": "Teknisi Menuju Lokasi / Pengerjaan", "timestamp": ts, "status": "done"})
            
        if booking.status in ["done", "lunas"]:
            # Gunakan updated_at booking sebagai pengerjaan selesai
            timeline.append({"event": "Pekerjaan Selesai", "timestamp": booking.updated_at, "status": "done"})

        lunas_payment = next((p for p in payments if p.payment_type == "lunas" and p.status == "success"), None)
        if lunas_payment:
            timeline.append({"event": "Pelunasan Berhasil", "timestamp": lunas_payment.paid_at, "status": "done"})
        elif booking.status == "done":
            timeline.append({"event": "Menunggu Pelunasan", "timestamp": None, "status": "pending"})

        return {
            "success": True,
            "message": "Detail booking jasa berhasil diambil",
            "data": {
                "trx_type": "jasa",
                "uuid": str(booking.uuid),
                "order_id": booking.booking_number,
                "gross_amount": booking.total_price,
                "items_subtotal": booking.device_price + booking.service_price + booking.addon_price,
                "total_discount": 0,
                "shipping_cost": 0,
                "service_cost": booking.transport_fee,
                "transaction_status": status_map.get(booking.status, "pending"),
                "payment_type": latest_payment.payment_method if latest_payment else "TRANSFER",
                "transaction_time": booking.created_at,
                "settlement_time": latest_payment.paid_at if latest_payment else None,
                "created_at": booking.created_at,
                "items": items_data,
                "shipment": None,
                "booking": _format_booking(booking),
                "timeline": timeline,
                "payments": [
                    {
                        "type": p.payment_type,
                        "amount": p.gross_amount,
                        "status": p.status,
                        "paid_at": p.paid_at,
                        "method": p.payment_method
                    } for p in payments
                ],
                "can_repay": booking.status in ["confirmed", "done"],
                "snap_token": latest_payment.payment_token if latest_payment and latest_payment.status == "pending" else None,
                "payment_url": latest_payment.payment_url if latest_payment and latest_payment.status == "pending" else None,
                "raw_response": latest_payment.midtrans_response if latest_payment else {},
            }
        }

    # ----------------------------------------------------------
    # WEBHOOK
    # ----------------------------------------------------------
    @staticmethod
    async def handle_webhook(*, session, payload: MidtransWebhookPayload) -> dict:
        full_order_id = payload.order_id or ""
        # Strip suffix -R- jika ada
        order_id = full_order_id.split("-R-")[0]
        
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

        # Gunakan order_id yang sudah di-strip
        order_id = payload.order_id.split("-R-")[0]
        trx_result = await session.exec(
            select(Transaction).where(Transaction.order_id == order_id)
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
                stock_ids = [ti.stock_id for ti in trx_items if ti.stock_id]
                if stock_ids:
                    sr = await session.exec(select(Stock).where(Stock.uuid.in_(stock_ids)))
                    stock_map = {s.uuid: s for s in sr.all()}
                    for trx_item in trx_items:
                        stock = stock_map.get(trx_item.stock_id)
                        if stock:
                            stock.terjual += trx_item.quantity
                            session.add(stock)
                ship_r = await session.exec(select(Shipment).where(Shipment.transaction_uuid == trx.uuid))
                shipment = ship_r.one_or_none()
                if shipment:
                    shipment.delivery_status = "PROCESSING"
                    session.add(shipment)
                notif_title = "✅ Pembayaran Berhasil & Pesanan Diproses 📦"
                notif_content = f"Pembayaran pesanan #{payload.order_id} dikonfirmasi. Pesanan sedang diproses dan akan segera dikirim."
                
                # 📝 Log Activity
                await ActivityService(session).log_activity(
                    activity_type="order",
                    title="💰 Pembayaran Berhasil",
                    description=f"Pembayaran {order_id} sebesar Rp{int(float(payload.gross_amount or 0)):,} telah diterima.",
                    reference_id=order_id,
                    user_id=trx.user_id,
                    status="settlement",
                    amount=int(float(payload.gross_amount or 0)),
                    icon="i-heroicons-check-circle",
                    color="green"
                )

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

            # 🎟️ Reclaim Coupon Quota
            if trx.coupon_code:
                try:
                    from backend.data.stock.service import StockService
                    await StockService().decrement_coupon_usage(session, trx.coupon_code)
                    logger.info(f"🎟️ Reclaimed coupon quota for {order_id}: {trx.coupon_code}")
                except Exception as e:
                    logger.error(f"❌ Failed to reclaim coupon {trx.coupon_code} for {order_id}: {e}")

        if notif_title and old_status != payload.transaction_status:
            await _send_transaction_notification(
                session=session, local_user_id=trx.user_id,
                title=notif_title, content=notif_content, order_id=payload.order_id,
            )
            
            # Kirim notifikasi ke admin jika pembayaran berhasil
            if payload.transaction_status in {"settlement", "capture"}:
                await _send_notification_to_admins(
                    session=session,
                    title="Pesanan Baru Dibayar! 💰",
                    content=f"Pesanan {order_id} sebesar Rp{int(float(payload.gross_amount or 0)):,} telah berhasil dibayar.",
                    action_url=f"/transaksi/{order_id}",
                    notif_type="order",
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
        # Mendelegasikan ke StockService agar logic & cache terpusat
        res = await stock_service.validate_coupon(session, code, subtotal)
        if not res["is_valid"]:
            raise ValueError(res["message"])
        
        # Kembalikan objek dummy/minimal yang kompatibel jika masih ada bagian code lain yang butuh
        from backend.data.stock.model import Coupon
        result = await session.exec(select(Coupon).where(Coupon.code == code.upper()))
        return result.first()

    # ----------------------------------------------------------
    # GENERATE INVOICE PDF
    # ----------------------------------------------------------
    @staticmethod
    async def generate_invoice_pdf(*, session: AsyncSession, user_id: Optional[UUID], order_id: str):
        """
        Menghasilkan PDF invoice menggunakan xhtml2pdf.
        """
        import io
        from jinja2 import Template
        from xhtml2pdf import pisa

        # 1. Ambil detail transaksi
        if order_id.startswith("PROMO-"):
            res = await TransactionService.get_promo_transaction_detail(
                session=session, user_id=user_id, order_id=order_id
            )
        elif order_id.startswith("BK-"):
            res = await TransactionService.get_jasa_transaction_detail(
                session=session, user_id=user_id, order_id=order_id
            )
        else:
            res = await TransactionService.get_regular_transaction_detail(
                session=session, user_id=user_id, order_id=order_id
            )
        
        detail = res.get("data")
        if not detail:
            raise Exception("Detail transaksi tidak ditemukan")

        # 2. Persiapkan data untuk template
        def fmt(v):
            return f"Rp {v:,.0f}".replace(",", ".")

        def fmt_dt(dt):
            if not dt: return "Menunggu"
            if isinstance(dt, str): return dt
            return dt.strftime("%Y-%m-%d %H:%M")

        # Transaction time handle
        t_time = detail.get("transaction_time") or detail.get("created_at")
        if isinstance(t_time, datetime):
            t_time_str = t_time.strftime("%Y-%m-%d %H:%M")
        elif isinstance(t_time, str):
            t_time_str = t_time
        else:
            t_time_str = "-"

        data = {
            "order_id": detail["order_id"],
            "transaction_status": str(detail["transaction_status"]).upper(),
            "transaction_time": t_time_str,
            "payment_type": (detail.get("payment_type") or "N/A").upper(),
            "customer_name": (detail.get("shipment", {}).get("recipient_name") if detail.get("shipment") else (detail.get("booking", {}).get("contact_name") if detail.get("booking") else "Customer")),
            "customer_phone": (detail.get("shipment", {}).get("recipient_phone") if detail.get("shipment") else (detail.get("booking", {}).get("contact_phone") if detail.get("booking") else "-")),
            "shipping_address": (detail.get("shipment", {}).get("shipping_address") if detail.get("shipment") else (detail.get("booking", {}).get("address") if detail.get("booking") else "-")),
            "items": detail.get("items", []),
            "subtotal": detail.get("items_subtotal") or detail.get("items_subtotal_original", 0),
            "shipping_cost": detail.get("shipping_cost", 0),
            "service_cost": detail.get("service_cost", 0),
            "discount_amount": detail.get("total_discount", 0),
            "gross_amount": detail.get("gross_amount", 0),
            "fmt": fmt,
            "fmt_dt": fmt_dt,
            "trx_type": detail.get("trx_type"),
            "timeline": detail.get("timeline", []),
            "booking": detail.get("booking"),
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 3. Template HTML
        html_template = """
        <html>
        <head>
            <style>
                @page { size: A4; margin: 1cm; }
                body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #333; }
                .header { border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }
                .brand { font-size: 24pt; font-weight: bold; }
                .info-table { width: 100%; margin-bottom: 20px; }
                .info-table td { vertical-align: top; width: 50%; }
                .section-title { background: #f4f4f4; padding: 5px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; font-size: 9pt; }
                .items-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                .items-table th { background: #000; color: #fff; padding: 8px; text-align: left; }
                .items-table td { border-bottom: 1px solid #eee; padding: 8px; }
                .text-right { text-align: right; }
                .totals-table { width: 40%; margin-left: 60%; }
                .total-row { font-weight: bold; font-size: 12pt; border-top: 2px solid #000; }
                .footer { margin-top: 50px; font-size: 8pt; color: #999; text-align: center; }
            </style>
        </head>
        <body>
            <table class="info-table">
                <tr>
                    <td>
                        <div class="brand">PasarCctv</div>
                        <div style="font-size: 9pt; color: #666;">
                            Solusi Keamanan Terpercaya<br>
                            Jl. Raya Pajajaran No. 123, Bogor<br>
                            0822-1882-8108 | pasarcctv.com
                        </div>
                    </td>
                    <td class="text-right">
                        <div style="font-size: 18pt; color: #666;">INVOICE</div>
                        <div style="font-weight: bold;">#{{ order_id }}</div>
                        <div>Status: {{ transaction_status }}</div>
                    </td>
                </tr>
            </table>
            <table class="info-table">
                <tr>
                    <td>
                        <div class="section-title">Informasi Pelanggan</div>
                        <strong>{{ customer_name }}</strong><br>
                        Telp: {{ customer_phone }}<br>
                        Alamat: {{ shipping_address }}
                    </td>
                    <td class="text-right">
                        <div class="section-title">Waktu Transaksi</div>
                        Dibuat: {{ transaction_time }}<br>
                        Metode: {{ payment_type }}
                        {% if booking %}
                        <br><strong>Jadwal: {{ booking.scheduled_date }} ({{ booking.time_slot }})</strong>
                        {% endif %}
                    </td>
                </tr>
            </table>

            {% if timeline and trx_type == 'jasa' %}
            <div class="section-title">Riwayat Aktivitas & Pengerjaan</div>
            <table class="items-table" style="font-size: 8pt; margin-bottom: 20px;">
                <thead>
                    <tr>
                        <th style="width: 60%">Tahapan / Event</th>
                        <th style="width: 40%">Waktu / Keterangan</th>
                    </tr>
                </thead>
                <tbody>
                    {% for t in timeline %}
                    <tr>
                        <td>{{ t.event }}</td>
                        <td>{{ fmt_dt(t.timestamp) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}

            <div class="section-title">Rincian Layanan & Produk</div>
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Deskripsi</th>
                        <th class="text-right">Harga Satuan</th>
                        <th class="text-right">Qty</th>
                        <th class="text-right">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td>
                            <strong>{{ item.item_name }}</strong>
                            {% if item.brand %}<br><span style="font-size: 8pt; color: #666;">Brand: {{ item.brand }}</span>{% endif %}
                            {% if item.addons %}<br>
                                {% for ad in item.addons %}
                                <span style="font-size: 8pt; color: #666;">&bull; {{ ad.name }} ({{ ad.quantity }}x)</span><br>
                                {% endfor %}
                            {% endif %}
                        </td>
                        <td class="text-right">{{ fmt(item.unit_price) }}</td>
                        <td class="text-right">{{ item.quantity }}</td>
                        <td class="text-right">{{ fmt(item.subtotal) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <table class="totals-table">
                <tr><td>Subtotal:</td><td class="text-right">{{ fmt(subtotal) }}</td></tr>
                {% if shipping_cost > 0 %}<tr><td>Ongkir:</td><td class="text-right">{{ fmt(shipping_cost) }}</td></tr>{% endif %}
                {% if service_cost > 0 %}<tr><td>Biaya Transport:</td><td class="text-right">{{ fmt(service_cost) }}</td></tr>{% endif %}
                {% if discount_amount > 0 %}<tr><td>Diskon:</td><td class="text-right">-{{ fmt(discount_amount) }}</td></tr>{% endif %}
                <tr class="total-row"><td>TOTAL:</td><td class="text-right">{{ fmt(gross_amount) }}</td></tr>
            </table>

            <div class="footer">
                <p>Invoice ini adalah bukti pembayaran yang sah. Terima kasih telah mempercayakan keamanan Anda kepada PasarCctv.</p>
                <p>Dicetak pada: {{ now }}</p>
            </div>

            {% if booking and booking.technician %}
            <div style="pdf-page-break-before: always;"></div>
            <div class="header">
                <div class="brand">PasarCctv</div>
                <div style="font-size: 14pt; color: #666; font-weight: bold; margin-top: 10px;">DETAIL PENUGASAN TEKNISI</div>
            </div>

            <table class="info-table" style="margin-top: 30px;">
                <tr>
                    <td style="width: 30%;">
                        {% if booking.technician.picture_url %}
                        <img src="{{ booking.technician.picture_url }}" style="width: 150px; height: 150px; border-radius: 10px; border: 1px solid #eee;">
                        {% else %}
                        <div style="width: 150px; height: 150px; background: #f9f9f9; border: 1px solid #eee; text-align: center; line-height: 150px; color: #ccc;">No Photo</div>
                        {% endif %}
                    </td>
                    <td style="width: 70%; padding-left: 20px;">
                        <div class="section-title">Informasi Teknisi</div>
                        <div style="font-size: 16pt; font-weight: bold; color: #000;">{{ booking.technician.name }}</div>
                        <div style="font-size: 11pt; color: #666; margin-bottom: 10px;">ID Pegawai: {{ booking.technician.id_employee }}</div>
                        
                        <div style="margin-top: 20px;">
                            <strong>No. WhatsApp:</strong><br>
                            {{ booking.technician.phone }}
                        </div>

                        <div style="margin-top: 20px;">
                            <strong>Lokasi Pengerjaan:</strong><br>
                            {{ booking.address }}
                        </div>
                    </td>
                </tr>
            </table>

            <div class="section-title" style="margin-top: 40px;">Verifikasi Keamanan</div>
            <div style="padding: 20px; border: 1px dashed #ccc; border-radius: 10px; text-align: center;">
                <p style="margin-bottom: 20px;">Silakan scan QR Code pada aplikasi user atau cocokan ID Pegawai di atas dengan kartu tanda pengenal teknisi saat tiba di lokasi.</p>
                <div style="font-size: 12pt; font-weight: bold; color: #333;">VERIFIED TECHNICIAN</div>
                <div style="font-size: 9pt; color: #999;">#{{ booking.technician.id_employee }}-{{ order_id }}</div>
            </div>

            <div class="footer">
                <p>PasarCctv — Keamanan Anda, Prioritas Kami.</p>
            </div>
            {% endif %}
        </body>
        </html>
        """
        template = Template(html_template)
        rendered_html = template.render(**data)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(rendered_html.encode("utf-8")), result)
        if pdf.err: raise Exception("Gagal menghasilkan PDF")
        result.seek(0)
        return result


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
    
    tech_info = None
    if booking.technician:
        tech_info = {
            "name": booking.technician.name,
            "id_employee": booking.technician.id_employee,
            "phone": booking.technician.phone,
            "picture_url": booking.technician.picture_url
        }

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
        "technician": tech_info
    }