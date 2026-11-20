"""
service.py — Business Logic: PromoService, PromoCheckoutService
Sistem: Padjajaran CCTV, Cimahi

Flow Checkout Promo:
1. Validasi promo (aktif, kuota, periode, user limit)
2. Resolve item (Stock / ServicePackage) yang terikat promo
3. Kalkulasi diskon per item berdasarkan PromoType
4. Jika ada produk fisik → hitung ongkir via RajaOngkir
5. Jika ada jasa → hitung biaya transport + buat ServiceBooking
6. Buat PromoTransaction + PromoTransactionItem
7. Charge Midtrans Snap
8. Catat PromoUsage (idempotency)
9. Kurangi stok & update used_count promo
"""

import hashlib
import httpx
import base64
import json
import logging
import secrets
import string
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

from fastapi import HTTPException
from sqlmodel import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import selectinload

from .model import (
    Promo, PromoItem, PromoUsage,
    PromoType, PromoTarget, PromoStatus,
)
from .model import PromoTransaction, PromoTransactionItem
from backend.data.stock.model import Stock
from backend.data.jasa.model import ServicePackage, ServiceBooking, BookingStatus
from backend.auth.model import User, UserAddress, UserMap
from backend.user.cart.model import Cart
from backend.config import Config
from backend.db.supabse import SupabaseNotificationService
from backend.data.activity.service import ActivityService

from .schema import (
    PromoCheckoutRequest, PromoCheckoutResponse,
    PromoPriceResult, PromoItemBreakdown,
    PromoResponse, PromoItemResponse,
    PromoValidateResponse,
)

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════

MIDTRANS_SNAP_URL = "https://app.sandbox.midtrans.com/snap/v1/transactions"
RAJAONGKIR_URL    = "https://rajaongkir.komerce.id/api/v1/calculate/domestic-cost"
ORIGIN_ID         = "16155"

PROMO_CACHE_PREFIX      = "promo:detail:"
PROMO_ACTIVE_CACHE_KEY  = "promo:active:list"
PROMO_CACHE_TTL         = 3_600     # 1 jam
PROMO_ACTIVE_LIST_TTL   = 300       # 5 menit


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _midtrans_auth() -> str:
    return "Basic " + base64.b64encode(f"{Config.MIDTRANS_SERVER_KEY}:".encode()).decode()


def _generate_promo_order_id() -> str:
    ts  = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    uid = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return f"PROMO-{ts}-{uid}"


def _generate_booking_number() -> str:
    today  = datetime.now().strftime("%Y%m%d")
    suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"BK-{today}-{suffix}"


def _parse_dt(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def _get_redis():
    from backend.db.redis import get_redis_token
    return get_redis_token()


# ══════════════════════════════════════════════════════════════════
# NOTIFICATION HELPER
# ══════════════════════════════════════════════════════════════════

async def _get_supabase_uid(session: AsyncSession, local_user_id: UUID) -> Optional[str]:
    try:
        result = await session.exec(
            select(UserMap).where(UserMap.local_user_id == str(local_user_id))
        )
        um = result.one_or_none()
        return um.supabase_user_id if um else None
    except Exception as e:
        logger.error(f"Error getting supabase_user_id: {e}")
        return None


async def _send_notif(
    session: AsyncSession,
    local_user_id: UUID,
    title: str,
    content: str,
    order_id: str,
    notif_type: str = "order",
) -> None:
    try:
        uid = await _get_supabase_uid(session, local_user_id)
        if not uid:
            return
        await SupabaseNotificationService.send_notification(
            user_id=uid,
            title=title,
            content=content,
            action_url=f"/dashboard/orders/{order_id}",
            notif_type=notif_type,
            metadata={"order_id": order_id},
        )
    except Exception as e:
        logger.error(f"Notification failed: {e}")


# ══════════════════════════════════════════════════════════════════
# PROMO CALCULATOR
# ══════════════════════════════════════════════════════════════════

class PromoCalculator:
    """
    Menghitung diskon berdasarkan PromoType.

    PERCENTAGE  : discount_value% dari original_price, dibatasi max_discount
    FIXED       : potongan flat discount_value per item
    BOGO        : beli buy_quantity → bayar buy_quantity - get_quantity (gratis get_quantity)
    BUNDLE_DISC : diskon persentase dari total bundle
    FLASH_SALE  : sama dengan PERCENTAGE tapi ada kuota terpisah (flash_sale_quota)
    """

    @staticmethod
    def calc_item_discount(
        promo: Promo,
        original_price: int,
        quantity: int,
        override_discount_value: Optional[int] = None,
    ) -> Tuple[int, int]:
        """
        Return (discount_per_unit, unit_price_after_discount).
        discount_per_unit = diskon per 1 unit.
        """
        disc_value = override_discount_value if override_discount_value is not None else promo.discount_value

        if promo.promo_type in (PromoType.PERCENTAGE, PromoType.FLASH_SALE):
            raw_discount = int(original_price * disc_value / 100)
            if promo.max_discount:
                raw_discount = min(raw_discount, promo.max_discount)
            discount_per_unit = raw_discount
            unit_price = max(original_price - discount_per_unit, 0)

        elif promo.promo_type == PromoType.FIXED:
            discount_per_unit = min(disc_value, original_price)
            unit_price = original_price - discount_per_unit

        elif promo.promo_type == PromoType.BOGO:
            # buy_quantity = harus beli min berapa
            # get_quantity = dapat gratis berapa
            # contoh: beli 2 gratis 1 → dari tiap set buy_quantity, get_quantity unit = free
            buy_q = promo.buy_quantity or 1
            get_q = promo.get_quantity or 1
            set_count = quantity // buy_q
            free_units = set_count * get_q
            # total yang dibayar
            paid_units = max(quantity - free_units, 0)
            total_paid = paid_units * original_price
            # avg discount per unit
            total_discount = (quantity - paid_units) * original_price
            discount_per_unit = total_discount // quantity if quantity else 0
            unit_price = total_paid // quantity if quantity else original_price

        elif promo.promo_type == PromoType.BUNDLE_DISC:
            # Diskon dari total bundle — diterapkan sama seperti PERCENTAGE
            raw_discount = int(original_price * disc_value / 100)
            if promo.max_discount:
                raw_discount = min(raw_discount, promo.max_discount)
            discount_per_unit = raw_discount
            unit_price = max(original_price - discount_per_unit, 0)

        else:
            discount_per_unit = 0
            unit_price = original_price

        return discount_per_unit, unit_price


# ══════════════════════════════════════════════════════════════════
# PROMO SERVICE — CRUD & Validasi
# ══════════════════════════════════════════════════════════════════

class PromoService:

    # ── Get Promo ─────────────────────────────────────────────────

    async def get_by_uuid(self, session: AsyncSession, promo_uuid: UUID) -> Promo:
        result = await session.exec(select(Promo).where(Promo.uuid == promo_uuid))
        promo = result.first()
        if not promo:
            raise HTTPException(404, "Promo tidak ditemukan")
        return promo

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Promo:
        result = await session.exec(select(Promo).where(Promo.slug == slug))
        promo = result.first()
        if not promo:
            raise HTTPException(404, f"Promo '{slug}' tidak ditemukan")
        return promo

    async def list_active(
        self,
        session: AsyncSession,
        target: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Promo)
            .where(
                Promo.status == PromoStatus.ACTIVE,
                Promo.valid_from <= now,
                Promo.valid_until >= now,
                Promo.deleted_at.is_(None),
            )
            .order_by(Promo.priority.desc(), Promo.created_at.desc())
        )
        if target:
            stmt = stmt.where(Promo.target.in_([target, PromoTarget.ALL]))

        all_result = await session.exec(stmt)
        all_items  = all_result.all()
        total      = len(all_items)

        paginated = all_items[(page - 1) * size : page * size]
        return {"total": total, "page": page, "size": size, "items": list(paginated)}

    # ── Get PromoItems ────────────────────────────────────────────

    async def get_promo_items(
        self, session: AsyncSession, promo_uuid: UUID
    ) -> List[PromoItem]:
        result = await session.exec(
            select(PromoItem).where(PromoItem.promo_uuid == promo_uuid)
        )
        return list(result.all())

    # ── Validate Promo ────────────────────────────────────────────

    async def validate_promo(
        self,
        session: AsyncSession,
        promo: Promo,
        user_id: Optional[UUID] = None,
        cart_total: int = 0,
        qty_total: int = 1,
    ) -> Tuple[bool, str]:
        """
        Return (is_valid, message).
        Cek: status, periode, kuota, min_purchase, min_qty, max_use_per_user.
        """
        now = datetime.now(timezone.utc)

        if promo.status != PromoStatus.ACTIVE:
            return False, f"Promo tidak aktif (status: {promo.status})"

        if now < promo.valid_from:
            return False, "Promo belum dimulai"

        if now > promo.valid_until:
            return False, "Promo sudah berakhir"

        if promo.quota is not None and promo.used_count >= promo.quota:
            return False, "Kuota promo sudah habis"

        if promo.is_flash_sale and promo.flash_sale_quota is not None:
            if promo.used_count >= promo.flash_sale_quota:
                return False, "Kuota flash sale sudah habis"

        if cart_total < promo.min_purchase:
            return False, f"Minimum pembelian Rp{promo.min_purchase:,} untuk promo ini"

        if qty_total < promo.min_qty:
            return False, f"Minimum {promo.min_qty} item untuk promo ini"

        if user_id and promo.max_use_per_user:
            usage_result = await session.exec(
                select(PromoUsage).where(
                    PromoUsage.promo_uuid == promo.uuid,
                    PromoUsage.user_uuid == user_id,
                    PromoUsage.rolled_back_at.is_(None),
                )
            )
            user_usage = len(usage_result.all())
            if user_usage >= promo.max_use_per_user:
                return False, f"Anda sudah memakai promo ini {promo.max_use_per_user}x (maksimum)"

        return True, "Promo valid"

    # ── Build Response ────────────────────────────────────────────

    async def build_promo_response(
        self, session: AsyncSession, promo: Promo
    ) -> PromoResponse:
        promo_items = await self.get_promo_items(session, promo.uuid)
        item_responses = []

        now = datetime.now(timezone.utc)
        is_valid = (
            promo.status == PromoStatus.ACTIVE
            and promo.valid_from <= now <= promo.valid_until
            and (promo.quota is None or promo.used_count < promo.quota)
        )

        for pi in promo_items:
            if pi.stock_uuid:
                stock_result = await session.exec(
                    select(Stock).options(selectinload(Stock.assets))
                    .where(Stock.uuid == pi.stock_uuid)
                )
                stock = stock_result.first()
                if stock:
                    item_responses.append(PromoItemResponse(
                        uuid=pi.uuid,
                        item_type="stock",
                        item_uuid=stock.uuid,
                        item_name=stock.title,
                        item_slug=stock.slug,
                        item_price=stock.online_price,
                        thumbnail_url=stock.assets[0].url if stock.assets else None,
                        override_discount_value=pi.override_discount_value,
                    ))
            elif pi.package_uuid:
                pkg_result = await session.exec(
                    select(ServicePackage).where(ServicePackage.uuid == pi.package_uuid)
                )
                pkg = pkg_result.first()
                if pkg:
                    item_responses.append(PromoItemResponse(
                        uuid=pi.uuid,
                        item_type="service_package",
                        item_uuid=pkg.uuid,
                        item_name=pkg.name,
                        item_slug=pkg.slug,
                        item_price=pkg.device_price + pkg.estimated_service_price,
                        thumbnail_url=pkg.thumbnail_url,
                        override_discount_value=pi.override_discount_value,
                    ))

        remaining = None
        if promo.quota is not None:
            remaining = max(0, promo.quota - promo.used_count)

        return PromoResponse(
            uuid=promo.uuid,
            name=promo.name,
            slug=promo.slug,
            description=promo.description,
            banner_url=promo.banner_url,
            promo_type=promo.promo_type,
            target=promo.target,
            discount_value=promo.discount_value,
            max_discount=promo.max_discount,
            buy_quantity=promo.buy_quantity,
            get_quantity=promo.get_quantity,
            min_purchase=promo.min_purchase,
            min_qty=promo.min_qty,
            quota=promo.quota,
            used_count=promo.used_count,
            max_use_per_user=promo.max_use_per_user,
            valid_from=promo.valid_from,
            valid_until=promo.valid_until,
            is_flash_sale=promo.is_flash_sale,
            flash_sale_quota=promo.flash_sale_quota,
            status=promo.status,
            priority=promo.priority,
            items=item_responses,
            is_valid=is_valid,
            remaining_quota=remaining,
        )

    # ── Admin CRUD ────────────────────────────────────────────────

    async def create_promo(
        self, session: AsyncSession, data, created_by: Optional[UUID] = None
    ) -> Promo:
        from .schema import PromoCreate
        promo = Promo(
            name=data.name,
            slug=data.slug,
            description=data.description,
            banner_url=data.banner_url,
            promo_type=data.promo_type,
            target=data.target,
            discount_value=data.discount_value,
            max_discount=data.max_discount,
            buy_quantity=data.buy_quantity,
            get_quantity=data.get_quantity,
            min_purchase=data.min_purchase,
            min_qty=data.min_qty,
            quota=data.quota,
            max_use_per_user=data.max_use_per_user,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            is_flash_sale=data.is_flash_sale,
            flash_sale_quota=data.flash_sale_quota,
            extra_config=data.extra_config,
            priority=data.priority,
            status=PromoStatus.DRAFT,
            created_by=created_by,
        )
        session.add(promo)
        await session.flush()

        for item_data in data.items:
            pi = PromoItem(
                promo_uuid=promo.uuid,
                stock_uuid=item_data.stock_uuid,
                package_uuid=item_data.package_uuid,
                override_discount_value=item_data.override_discount_value,
            )
            session.add(pi)

        await session.commit()
        await session.refresh(promo)

        # Invalidate cache
        await _get_redis().delete(PROMO_ACTIVE_CACHE_KEY)

        return promo

    async def update_promo(
        self, session: AsyncSession, promo_uuid: UUID, data
    ) -> Promo:
        promo = await self.get_by_uuid(session, promo_uuid)
        update_dict = data.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(promo, k, v)
        session.add(promo)
        await session.commit()
        await session.refresh(promo)

        # Invalidate cache
        r = _get_redis()
        await r.delete(f"{PROMO_CACHE_PREFIX}{promo_uuid}")
        await r.delete(PROMO_ACTIVE_CACHE_KEY)

        return promo

    async def publish_promo(self, session: AsyncSession, promo_uuid: UUID) -> Promo:
        promo = await self.get_by_uuid(session, promo_uuid)
        if promo.status not in (PromoStatus.DRAFT, PromoStatus.PAUSED):
            raise HTTPException(400, f"Tidak bisa publish promo dengan status '{promo.status}'")
        promo.status = PromoStatus.ACTIVE
        session.add(promo)
        await session.commit()
        await session.refresh(promo)
        await _get_redis().delete(PROMO_ACTIVE_CACHE_KEY)
        return promo

    async def soft_delete_promo(self, session: AsyncSession, promo_uuid: UUID) -> Dict[str, str]:
        promo = await self.get_by_uuid(session, promo_uuid)
        promo.deleted_at = datetime.now(timezone.utc)
        promo.status = PromoStatus.ARCHIVED
        session.add(promo)
        await session.commit()
        await _get_redis().delete(f"{PROMO_CACHE_PREFIX}{promo_uuid}")
        await _get_redis().delete(PROMO_ACTIVE_CACHE_KEY)
        return {"message": f"Promo '{promo.name}' berhasil diarsipkan"}


# ══════════════════════════════════════════════════════════════════
# PROMO CHECKOUT SERVICE
# ══════════════════════════════════════════════════════════════════

class PromoCheckoutService:
    """
    Menangani seluruh flow checkout melalui halaman promo.
    """

    def __init__(self):
        self.promo_svc = PromoService()

    # ── Main Checkout ──────────────────────────────────────────────

    async def checkout(
        self,
        session: AsyncSession,
        user: User,
        payload: PromoCheckoutRequest,
    ) -> PromoCheckoutResponse:

        # 1. Load promo
        promo = await self.promo_svc.get_by_uuid(session, payload.promo_uuid)
        promo_items_db = await self.promo_svc.get_promo_items(session, promo.uuid)

        # 2. Resolve & lock stock items
        locked_stocks: Dict[str, Stock] = {}
        if payload.stock_items:
            sorted_stock = sorted(payload.stock_items, key=lambda i: str(i.stock_uuid))
            for item in sorted_stock:
                try:
                    result = await session.exec(
                        select(Stock)
                        .where(Stock.uuid == item.stock_uuid, Stock.is_active == True)
                        .with_for_update(nowait=True)
                    )
                    stock = result.one_or_none()
                except OperationalError:
                    raise ValueError("Stok sedang diproses, coba lagi")

                if not stock:
                    raise ValueError(f"Produk {item.stock_uuid} tidak ditemukan")
                if stock.stok < item.quantity:
                    raise ValueError(f"Stok '{stock.title}' tidak cukup (tersedia: {stock.stok})")
                locked_stocks[str(item.stock_uuid)] = stock

        # 3. Resolve service packages
        resolved_packages: Dict[str, ServicePackage] = {}
        if payload.service_items:
            for item in payload.service_items:
                result = await session.exec(
                    select(ServicePackage)
                    .where(ServicePackage.uuid == item.package_uuid, ServicePackage.is_active == True)
                )
                pkg = result.first()
                if not pkg:
                    raise ValueError(f"Paket {item.package_uuid} tidak ditemukan")
                resolved_packages[str(item.package_uuid)] = pkg

        # 4. Build promo_item_map: uuid → override_discount_value
        promo_item_map: Dict[str, Optional[int]] = {}
        for pi in promo_items_db:
            if pi.stock_uuid:
                promo_item_map[f"stock:{pi.stock_uuid}"] = pi.override_discount_value
            if pi.package_uuid:
                promo_item_map[f"pkg:{pi.package_uuid}"] = pi.override_discount_value

        # 5. Kalkulasi harga untuk setiap item
        items_breakdown: List[PromoItemBreakdown] = []
        items_original_total = 0

        # Stock items
        for item in payload.stock_items:
            stock = locked_stocks[str(item.stock_uuid)]
            override = promo_item_map.get(f"stock:{item.stock_uuid}")

            # Jika promo.target = STOCK atau ALL → terapkan diskon
            apply_discount = promo.target in (PromoTarget.STOCK, PromoTarget.ALL)
            # Jika ada PromoItem spesifik → hanya item itu yang dapat diskon
            if promo_items_db:
                apply_discount = f"stock:{item.stock_uuid}" in promo_item_map

            if apply_discount:
                disc_per_unit, unit_price = PromoCalculator.calc_item_discount(
                    promo, stock.online_price, item.quantity, override
                )
            else:
                disc_per_unit, unit_price = 0, stock.online_price

            subtotal = unit_price * item.quantity
            items_original_total += stock.online_price * item.quantity

            items_breakdown.append(PromoItemBreakdown(
                item_uuid=item.stock_uuid,
                item_type="stock",
                item_name=stock.title,
                original_price=stock.online_price,
                quantity=item.quantity,
                discount_value=disc_per_unit,
                discount_type=promo.promo_type,
                after_discount=unit_price,
                subtotal=subtotal,
            ))

        # Service package items
        for item in payload.service_items:
            pkg = resolved_packages[str(item.package_uuid)]
            pkg_price = pkg.device_price + pkg.estimated_service_price
            override = promo_item_map.get(f"pkg:{item.package_uuid}")

            apply_discount = promo.target in (PromoTarget.SERVICE_PACKAGE, PromoTarget.ALL)
            if promo_items_db:
                apply_discount = f"pkg:{item.package_uuid}" in promo_item_map

            if apply_discount:
                disc_per_unit, unit_price = PromoCalculator.calc_item_discount(
                    promo, pkg_price, item.quantity, override
                )
            else:
                disc_per_unit, unit_price = 0, pkg_price

            subtotal = unit_price * item.quantity
            items_original_total += pkg_price * item.quantity

            items_breakdown.append(PromoItemBreakdown(
                item_uuid=item.package_uuid,
                item_type="service_package",
                item_name=pkg.name,
                original_price=pkg_price,
                quantity=item.quantity,
                discount_value=disc_per_unit,
                discount_type=promo.promo_type,
                after_discount=unit_price,
                subtotal=subtotal,
            ))

        items_discounted_total = sum(b.subtotal for b in items_breakdown)
        total_discount = items_original_total - items_discounted_total
        qty_total = sum(i.quantity for i in payload.stock_items) + sum(i.quantity for i in payload.service_items)

        # 6. Validasi promo (setelah tahu total)
        is_valid, msg = await self.promo_svc.validate_promo(
            session, promo,
            user_id=user.uuid,
            cart_total=items_discounted_total,
            qty_total=qty_total,
        )
        if not is_valid:
            raise ValueError(msg)

        # 7. Hitung ongkir produk fisik
        shipping_cost = 0
        selected_courier_info: Dict[str, Any] = {}
        if payload.stock_items and payload.address_uuid:
            shipping_cost, selected_courier_info = await self._get_shipping(
                session=session,
                user=user,
                address_uuid=payload.address_uuid,
                stock_items=payload.stock_items,
                locked_stocks=locked_stocks,
                courier_name=payload.courier_name or "jne",
                courier_service=payload.courier_service or "REG",
            )

        # 8. Hitung biaya jasa (transport) dari config aktif
        service_cost = 0
        if payload.service_items:
            service_cost = await self._calc_service_transport_cost(
                session=session,
                distance_km=payload.distance_km or 0,
            )

        gross_amount = items_discounted_total + shipping_cost + service_cost

        # 9. Buat PromoTransaction
        order_id = _generate_promo_order_id()
        promo_trx = PromoTransaction(
            user_id=user.uuid,
            promo_uuid=promo.uuid,
            promo_snapshot={
                "uuid": str(promo.uuid),
                "name": promo.name,
                "promo_type": promo.promo_type,
                "discount_value": promo.discount_value,
                "valid_from": promo.valid_from.isoformat(),
                "valid_until": promo.valid_until.isoformat(),
            },
            order_id=order_id,
            items_subtotal_original=items_original_total,
            total_discount=total_discount,
            items_subtotal_discounted=items_discounted_total,
            shipping_cost=shipping_cost,
            service_cost=service_cost,
            gross_amount=gross_amount,
            transaction_status="pending_payment",
            has_shipment=bool(payload.stock_items),
        )
        session.add(promo_trx)
        await session.flush()

        # 10. Buat PromoTransactionItem
        for bd in items_breakdown:
            pti = PromoTransactionItem(
                promo_transaction_id=promo_trx.uuid,
                stock_uuid=bd.item_uuid if bd.item_type == "stock" else None,
                package_uuid=bd.item_uuid if bd.item_type == "service_package" else None,
                item_type=bd.item_type,
                item_name=bd.item_name,
                quantity=bd.quantity,
                original_price=bd.original_price,
                discount_value=bd.discount_value,
                unit_price=bd.after_discount,
                subtotal=bd.subtotal,
            )
            session.add(pti)

        # 11. Buat ServiceBooking jika ada jasa
        booking_number = None
        if payload.service_items:
            booking_number = await self._create_service_booking(
                session=session,
                user=user,
                payload=payload,
                promo_trx=promo_trx,
                service_cost=service_cost,
                resolved_packages=resolved_packages,
            )

        # 12. Buat Shipment jika ada produk fisik
        if payload.stock_items and payload.address_uuid:
            await self._create_shipment(
                session=session,
                user=user,
                payload=payload,
                promo_trx_uuid=promo_trx.uuid,
                shipping_cost=shipping_cost,
                selected_courier_info=selected_courier_info,
            )

        # 13. Kurangi stok
        for item in payload.stock_items:
            stock = locked_stocks[str(item.stock_uuid)]
            stock.stok -= item.quantity
            session.add(stock)

        # 14. Midtrans Snap
        try:
            mt_resp = await self._charge_midtrans(
                order_id=order_id,
                gross_amount=gross_amount,
                user=user,
                items_breakdown=items_breakdown,
                shipping_cost=shipping_cost,
                service_cost=service_cost,
            )
        except Exception as e:
            logger.error(f"Midtrans error: {e}")
            # Rollback stok
            for item in payload.stock_items:
                locked_stocks[str(item.stock_uuid)].stok += item.quantity
            raise ValueError("Gagal membuat pembayaran, coba lagi")

        # 15. Update status dari Midtrans
        promo_trx.raw_response = mt_resp
        promo_trx.transaction_status = mt_resp.get("transaction_status", "pending")
        promo_trx.payment_type = mt_resp.get("payment_type")
        promo_trx.transaction_time = _parse_dt(mt_resp.get("transaction_time"))
        session.add(promo_trx)

        # 16. Catat PromoUsage
        idempotency_key = f"{promo.uuid}:{user.uuid}:{order_id}"
        usage = PromoUsage(
            promo_uuid=promo.uuid,
            user_uuid=user.uuid,
            order_id=order_id,
            discount_applied=total_discount,
            idempotency_key=idempotency_key,
        )
        session.add(usage)

        # 17. Increment used_count promo
        promo.used_count += 1
        session.add(promo)
        
        # 📝 Log Activity
        await ActivityService(session).log_activity(
            activity_type="promo",
            title="🎁 Pesanan Promo",
            description=f"Pesanan promo {order_id} ({promo.name}) dibuat oleh {user.username}",
            reference_id=order_id,
            user_id=user.uuid,
            status="pending",
            amount=int(gross_amount),
            icon="i-heroicons-gift",
            color="purple"
        )

        await session.commit()
        
        # 18. Bersihkan cart jika item yang dicheckout ada di cart
        try:
            if payload.stock_items:
                s_uuids = [item.stock_uuid for item in payload.stock_items]
                await session.execute(
                    delete(Cart)
                    .where(Cart.user_uuid == user.uuid)
                    .where(Cart.stock_uuid.in_(s_uuids))
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to clear cart after promo checkout: {e}")

        # 18. Notifikasi
        await _send_notif(
            session=session,
            local_user_id=user.uuid,
            title="🎉 Pesanan Promo Dibuat",
            content=f"Pesanan promo #{order_id} berhasil dibuat. Hemat Rp{total_discount:,}! Selesaikan pembayaran segera.",
            order_id=order_id,
        )

        try:
            from backend.data.transaksi.service import _send_notification_to_admins
            await _send_notification_to_admins(
                session=session,
                title="Pesanan Promo Baru! 🎁",
                content=f"Pesanan promo {order_id} ({promo.name}) sebesar Rp{int(gross_amount):,} menunggu pembayaran.",
                action_url=f"/transaksi/{order_id}",
                notif_type="order",
            )
        except Exception as e:
            logger.error(f"Failed to send promo created notification to admin: {e}")

        # 19. Invalidate cache promo
        r = _get_redis()
        await r.delete(f"{PROMO_CACHE_PREFIX}{promo.uuid}")
        await r.delete(PROMO_ACTIVE_CACHE_KEY)

        return PromoCheckoutResponse(
            order_id=order_id,
            promo_transaction_uuid=str(promo_trx.uuid),
            items_subtotal_original=items_original_total,
            total_discount=total_discount,
            items_subtotal_discounted=items_discounted_total,
            shipping_cost=shipping_cost,
            service_cost=service_cost,
            gross_amount=gross_amount,
            transaction_status=promo_trx.transaction_status,
            snap_token=mt_resp.get("token"),
            payment_url=mt_resp.get("redirect_url"),
            expiry_time=mt_resp.get("expiry_time"),
            booking_number=booking_number,
        )

    # ── Calculate Price Preview (tanpa commit) ─────────────────────

    async def calculate_price(
        self,
        session: AsyncSession,
        user: Optional[User],
        payload,  # PromoValidateRequest
    ) -> PromoPriceResult:
        """Kalkulasi harga promo tanpa menyimpan apapun ke DB."""
        if payload.promo_uuid:
            promo = await self.promo_svc.get_by_uuid(session, payload.promo_uuid)
        else:
            promo = await self.promo_svc.get_by_slug(session, payload.promo_slug)

        promo_items_db = await self.promo_svc.get_promo_items(session, promo.uuid)
        promo_item_map: Dict[str, Optional[int]] = {}
        for pi in promo_items_db:
            if pi.stock_uuid:
                promo_item_map[f"stock:{pi.stock_uuid}"] = pi.override_discount_value
            if pi.package_uuid:
                promo_item_map[f"pkg:{pi.package_uuid}"] = pi.override_discount_value

        items_breakdown: List[PromoItemBreakdown] = []
        items_original_total = 0

        for item in payload.stock_items:
            result = await session.exec(
                select(Stock).where(Stock.uuid == item.stock_uuid, Stock.is_active == True)
            )
            stock = result.first()
            if not stock:
                raise HTTPException(404, f"Produk {item.stock_uuid} tidak ditemukan")

            override = promo_item_map.get(f"stock:{item.stock_uuid}")
            apply_discount = promo.target in (PromoTarget.STOCK, PromoTarget.ALL)
            if promo_items_db:
                apply_discount = f"stock:{item.stock_uuid}" in promo_item_map

            if apply_discount:
                disc, unit_price = PromoCalculator.calc_item_discount(
                    promo, stock.online_price, item.quantity, override
                )
            else:
                disc, unit_price = 0, stock.online_price

            items_original_total += stock.online_price * item.quantity
            items_breakdown.append(PromoItemBreakdown(
                item_uuid=item.stock_uuid,
                item_type="stock",
                item_name=stock.title,
                original_price=stock.online_price,
                quantity=item.quantity,
                discount_value=disc,
                discount_type=promo.promo_type,
                after_discount=unit_price,
                subtotal=unit_price * item.quantity,
            ))

        for item in payload.service_items:
            result = await session.exec(
                select(ServicePackage)
                .where(ServicePackage.uuid == item.package_uuid, ServicePackage.is_active == True)
            )
            pkg = result.first()
            if not pkg:
                raise HTTPException(404, f"Paket {item.package_uuid} tidak ditemukan")

            pkg_price = pkg.device_price + pkg.estimated_service_price
            override = promo_item_map.get(f"pkg:{item.package_uuid}")
            apply_discount = promo.target in (PromoTarget.SERVICE_PACKAGE, PromoTarget.ALL)
            if promo_items_db:
                apply_discount = f"pkg:{item.package_uuid}" in promo_item_map

            if apply_discount:
                disc, unit_price = PromoCalculator.calc_item_discount(
                    promo, pkg_price, item.quantity, override
                )
            else:
                disc, unit_price = 0, pkg_price

            items_original_total += pkg_price * item.quantity
            items_breakdown.append(PromoItemBreakdown(
                item_uuid=item.package_uuid,
                item_type="service_package",
                item_name=pkg.name,
                original_price=pkg_price,
                quantity=item.quantity,
                discount_value=disc,
                discount_type=promo.promo_type,
                after_discount=unit_price,
                subtotal=unit_price * item.quantity,
            ))

        discounted = sum(b.subtotal for b in items_breakdown)
        total_discount = items_original_total - discounted

        return PromoPriceResult(
            promo_uuid=promo.uuid,
            promo_name=promo.name,
            promo_type=promo.promo_type,
            items=items_breakdown,
            items_subtotal_original=items_original_total,
            total_discount=total_discount,
            items_subtotal_discounted=discounted,
            shipping_cost=0,     # dihitung saat checkout resmi
            service_cost=0,
            gross_amount=discounted,
        )

    # ── Webhook Handler ────────────────────────────────────────────

    async def handle_webhook(
        self, session: AsyncSession, payload
    ) -> Dict[str, Any]:
        """
        Terima notifikasi Midtrans untuk promo order.
        Format order_id: PROMO-YYYYMMDD-XXXXXXXX
        """
        # Verifikasi signature
        if payload.signature_key and payload.status_code and payload.gross_amount:
            raw = f"{payload.order_id}{payload.status_code}{payload.gross_amount}{Config.MIDTRANS_SERVER_KEY}"
            expected = hashlib.sha512(raw.encode()).hexdigest()
            if expected != payload.signature_key:
                raise PermissionError("Invalid signature")

        full_order_id = payload.order_id or ""
        order_id = full_order_id.split("-R-")[0]

        result = await session.exec(
            select(PromoTransaction).where(PromoTransaction.order_id == order_id)
        )
        promo_trx = result.first()

        if not promo_trx:
            logger.warning(f"Promo webhook: order {payload.order_id} tidak ditemukan")
            return {"status": "ignored"}

        FINAL = {"settlement", "capture", "cancel", "deny", "expire", "refund"}
        if promo_trx.transaction_status in FINAL:
            return {"status": "skipped", "reason": "already final"}

        old_status = promo_trx.transaction_status

        promo_trx.transaction_status = payload.transaction_status
        promo_trx.payment_type       = payload.payment_type
        promo_trx.fraud_status       = payload.fraud_status
        promo_trx.status_code        = payload.status_code
        promo_trx.raw_response       = payload.model_dump()
        if payload.transaction_time:
            promo_trx.transaction_time = _parse_dt(payload.transaction_time)
        if payload.settlement_time:
            promo_trx.settlement_time  = _parse_dt(payload.settlement_time)
        session.add(promo_trx)

        notif_title = ""
        notif_content = ""

        if payload.transaction_status in ("settlement", "capture"):
            if not (payload.fraud_status and payload.fraud_status == "challenge"):
                # Update terjual untuk stock items
                items_result = await session.exec(
                    select(PromoTransactionItem)
                    .where(PromoTransactionItem.promo_transaction_id == promo_trx.uuid)
                )
                for pti in items_result.all():
                    if pti.stock_uuid:
                        stock_r = await session.exec(select(Stock).where(Stock.uuid == pti.stock_uuid))
                        stock = stock_r.first()
                        if stock:
                            stock.terjual += pti.quantity
                            session.add(stock)

                from backend.data.ongkir.model import Shipment as _PromoShipment
                ship_r = await session.exec(
                    select(_PromoShipment).where(_PromoShipment.promo_transaction_uuid == promo_trx.uuid)
                )
                promo_ship = ship_r.one_or_none()
                if promo_ship:
                    promo_ship.delivery_status = "PROCESSING"
                    session.add(promo_ship)
                notif_title = "✅ Pembayaran Promo Berhasil & Pesanan Diproses 📦"
                notif_content = f"Pesanan promo #{payload.order_id} dikonfirmasi. Hemat terjamin! Pesanan sedang diproses."
                
                # 📝 Log Activity
                await ActivityService(session).log_activity(
                    activity_type="promo",
                    title="💰 Pembayaran Promo",
                    description=f"Pembayaran promo {order_id} sebesar Rp{int(float(payload.gross_amount or 0)):,} telah diterima.",
                    reference_id=order_id,
                    user_id=promo_trx.user_id,
                    status="settlement",
                    amount=int(float(payload.gross_amount or 0)),
                    icon="i-heroicons-check-badge",
                    color="green"
                )

        elif payload.transaction_status in ("cancel", "deny", "expire"):
            # Kembalikan stok
            items_result = await session.exec(
                select(PromoTransactionItem)
                .where(PromoTransactionItem.promo_transaction_id == promo_trx.uuid)
            )
            for pti in items_result.all():
                if pti.stock_uuid:
                    stock_r = await session.exec(select(Stock).where(Stock.uuid == pti.stock_uuid))
                    stock = stock_r.first()
                    if stock:
                        stock.stok += pti.quantity
                        session.add(stock)

            # Rollback PromoUsage
            usage_r = await session.exec(
                select(PromoUsage).where(PromoUsage.order_id == payload.order_id)
            )
            usage = usage_r.first()
            if usage:
                usage.rolled_back_at = datetime.now(timezone.utc)
                session.add(usage)

            # Kembalikan used_count promo
            promo_r = await session.exec(
                select(Promo).where(Promo.uuid == promo_trx.promo_uuid)
            )
            promo = promo_r.first()
            if promo:
                promo.used_count = max(0, promo.used_count - 1)
                session.add(promo)

            status_label = {"cancel": "dibatalkan", "deny": "ditolak", "expire": "kedaluwarsa"}.get(
                payload.transaction_status, payload.transaction_status
            )
            notif_title = f"❌ Pesanan Promo {status_label.capitalize()}"
            notif_content = f"Pesanan promo #{payload.order_id} {status_label}."

        if notif_title and old_status != payload.transaction_status:
            await _send_notif(
                session=session,
                local_user_id=promo_trx.user_id,
                title=notif_title,
                content=notif_content,
                order_id=payload.order_id,
            )

            # Kirim notifikasi ke admin jika pembayaran promo berhasil
            if payload.transaction_status in ("settlement", "capture"):
                try:
                    from backend.data.transaksi.service import _send_notification_to_admins
                    await _send_notification_to_admins(
                        session=session,
                        title="Pesanan Baru Dibayar! 💰",
                        content=f"Pesanan promo {order_id} sebesar Rp{int(float(payload.gross_amount or 0)):,} telah berhasil dibayar.",
                        action_url=f"/transaksi/{order_id}",
                        notif_type="order",
                    )
                except Exception as e:
                    logger.error(f"Failed to send promo paid notification to admin: {e}")

        await session.commit()

        return {
            "status": "ok",
            "order_id": payload.order_id,
            "new_status": promo_trx.transaction_status,
        }

    # ══════════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ══════════════════════════════════════════════════════════════

    async def _get_shipping(
        self,
        session: AsyncSession,
        user: User,
        address_uuid: UUID,
        stock_items,
        locked_stocks: Dict[str, Stock],
        courier_name: str,
        courier_service: str,
    ) -> Tuple[int, Dict[str, Any]]:
        addr_r = await session.exec(
            select(UserAddress)
            .where(UserAddress.uuid == address_uuid, UserAddress.user_id == user.uuid)
        )
        address = addr_r.one_or_none()
        
        if not address:
            raise ValueError("Alamat pengiriman tidak ditemukan.")

        if not address.location_id:
            raise ValueError("Alamat ini belum memiliki data area (Kecamatan/Kota). Silakan perbarui alamat Anda.")

        # ─── TAMBAHKAN NORMALISASI NAMA KURIR DI SINI ───
        raw_courier = courier_name.lower().strip()
        
        # Mapping nama kurir dari frontend ke format standar Komerce/RajaOngkir
        courier_mapping = {
            "j&t express": "jnt",
            "j&t": "jnt",
            "sicepat ekspres": "sicepat",
        }
        # Gunakan nama hasil mapping jika ada, jika tidak, gunakan aslinya
        normalized_courier = courier_mapping.get(raw_courier, raw_courier)
        # ────────────────────────────────────────────────

        total_weight = sum(
            (locked_stocks[str(item.stock_uuid)].weight or 1000) * item.quantity
            for item in stock_items
        )

        payload_to_komerce = {
            "origin": ORIGIN_ID,
            "originType": "subdistrict",
            "destination": str(address.location_id),
            "destinationType": "subdistrict",
            "weight": max(int(total_weight), 1),
            "courier": normalized_courier, # <--- GUNAKAN NORMALIZED COURIER
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                RAJAONGKIR_URL,
                headers={"key": Config.SHIPPING_COST, "Content-Type": "application/x-www-form-urlencoded"},
                data=payload_to_komerce,
            )
            
            # TANGKAP DAN BACA ERROR DARI KOMERCE
            if not resp.is_success:
                error_detail = resp.text
                try:
                    err_json = resp.json()
                    # Menangkap format pesan error RajaOngkir / Komerce
                    if "rajaongkir" in err_json and "status" in err_json["rajaongkir"]:
                        error_detail = err_json["rajaongkir"]["status"].get("description", resp.text)
                    elif "meta" in err_json:
                        error_detail = err_json["meta"].get("message", resp.text)
                    elif "message" in err_json:
                        error_detail = err_json["message"]
                except Exception:
                    pass
                
                # Log ke terminal agar developer bisa lihat payload vs error-nya
                logger.error(f"[Komerce 422] Payload: {payload_to_komerce} | Error: {error_detail}")
                
                # Lempar error jelas ke frontend
                raise ValueError(f"Gagal cek ongkos kirim: {error_detail}")

        options = resp.json().get("data", [])
        target  = courier_service.upper()
        selected = next((o for o in options if o.get("service", "").upper() == target), None)
        
        if not selected and options:
            selected = min(options, key=lambda x: x.get("cost", 999_999))
            
        if not selected:
            raise ValueError(f"Layanan kurir '{courier_name.upper()} {courier_service.upper()}' tidak tersedia untuk wilayah Anda.")

        return int(selected.get("cost", 0)), selected

    async def _calc_service_transport_cost(
        self, session: AsyncSession, distance_km: float
    ) -> int:
        """Ambil transport fee dari ServicePricingConfig aktif."""
        try:
            from backend.data.jasa.model import ServicePricingConfig
            result = await session.exec(
                select(ServicePricingConfig)
                .where(ServicePricingConfig.is_active == True)
                .order_by(ServicePricingConfig.created_at.desc())
                .limit(1)
            )
            config = result.first()
            if not config or distance_km <= 0:
                return 0
            raw = int(distance_km * config.transport_per_km)
            return max(config.transport_min_fee, min(raw, config.transport_max_fee))
        except Exception as e:
            logger.warning(f"Service transport cost error: {e}")
            return 0

    async def _create_service_booking(
        self,
        session: AsyncSession,
        user: User,
        payload: PromoCheckoutRequest,
        promo_trx: PromoTransaction,
        service_cost: int,
        resolved_packages: Dict[str, ServicePackage],
    ) -> str:
        from datetime import date as date_type
        from backend.data.jasa.model import TimeSlot

        scheduled_date = date_type.fromisoformat(payload.scheduled_date)

        # Ambil package pertama sebagai referensi utama
        first_pkg = next(iter(resolved_packages.values()))

        booking_number = _generate_booking_number()
        booking = ServiceBooking(
            user_uuid=user.uuid,
            package_uuid=first_pkg.uuid,
            booking_number=booking_number,
            category=first_pkg.category,
            camera_count=first_pkg.camera_count,
            brand=first_pkg.default_brand,
            addons=[],
            package_snapshot={
                "promo_order_id": promo_trx.order_id,
                "packages": [
                    {"uuid": str(pkg.uuid), "name": pkg.name, "qty": item.quantity}
                    for item in payload.service_items
                    for pkg in [resolved_packages[str(item.package_uuid)]]
                ],
            },
            scheduled_date=scheduled_date,
            time_slot=payload.time_slot,
            address=payload.address_service,
            district=payload.district,
            city=payload.city,
            distance_km=payload.distance_km or 0,
            latitude=payload.latitude,
            longitude=payload.longitude,
            contact_name=payload.contact_name,
            contact_phone=payload.contact_phone,
            contact_notes=payload.contact_notes,
            device_price=first_pkg.device_price,
            service_price=first_pkg.estimated_service_price,
            addon_price=0,
            transport_fee=service_cost,
            total_price=first_pkg.device_price + first_pkg.estimated_service_price + service_cost,
            dp_percentage=50,
            dp_amount=0,        # sudah dibayar via promo transaction
            remaining_amount=0,
            price_breakdown={"source": "promo", "promo_order_id": promo_trx.order_id},
            status=BookingStatus.CONFIRMED,  # langsung CONFIRMED karena bayar via promo
        )
        session.add(booking)
        await session.flush()

        # Update promo_trx dengan service_booking_uuid
        promo_trx.service_booking_uuid = booking.uuid
        session.add(promo_trx)

        return booking_number

    async def _create_shipment(
        self,
        session: AsyncSession,
        user: User,
        payload: PromoCheckoutRequest,
        promo_trx_uuid: UUID,
        shipping_cost: int,
        selected_courier_info: Dict[str, Any],
    ) -> None:
        from backend.data.ongkir.model import Shipment
        from sqlmodel import select as sel

        addr_r = await session.exec(
            sel(UserAddress)
            .where(UserAddress.uuid == payload.address_uuid, UserAddress.user_id == user.uuid)
        )
        address = addr_r.one_or_none()
        if not address:
            return

        shipment = Shipment(
            promo_transaction_uuid=promo_trx_uuid,
            courier_name=payload.courier_name,
            courier_service=selected_courier_info.get("service", payload.courier_service),
            recipient_name=getattr(user, "full_name", user.username),
            recipient_phone=getattr(user, "phone", ""),
            shipping_address=(
                f"{address.full_address}, "
                f"{address.subdistrict or ''}, "
                f"{address.district or ''}, "
                f"{address.city or ''}, "
                f"{address.province or ''} "
                f"{address.zip_code}"
            ).strip(", "),
            delivery_status="PENDING",
            shipping_cost=shipping_cost,
            etd=selected_courier_info.get("etd"),
        )
        session.add(shipment)

    async def _charge_midtrans(
        self,
        order_id: str,
        gross_amount: int,
        user: User,
        items_breakdown: List[PromoItemBreakdown],
        shipping_cost: int,
        service_cost: int,
    ) -> Dict[str, Any]:
        item_details = []

        for bd in items_breakdown:
            item_details.append({
                "id": str(bd.item_uuid),
                "price": bd.after_discount,
                "quantity": bd.quantity,
                "name": bd.item_name[:50],
            })

        if shipping_cost > 0:
            item_details.append({
                "id": "SHIPPING",
                "price": shipping_cost,
                "quantity": 1,
                "name": "Ongkos Kirim",
            })

        if service_cost > 0:
            item_details.append({
                "id": "SERVICE_TRANSPORT",
                "price": service_cost,
                "quantity": 1,
                "name": "Biaya Transport Teknisi",
            })

        payload = {
            "payment_type": "qris",
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": gross_amount,
            },
            "item_details": item_details,
            "customer_details": {
                "first_name": user.username,
                "email": user.email,
            },
            "qris": {"acquirer": "gopay"},
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                MIDTRANS_SNAP_URL,
                json=payload,
                headers={
                    "Authorization": _midtrans_auth(),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            if not resp.is_success:
                raise ValueError(f"Midtrans error {resp.status_code}: {resp.text}")
            return resp.json()