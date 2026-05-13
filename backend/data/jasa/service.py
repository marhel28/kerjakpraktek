"""
service.py — Business Logic: PricingEngine, BookingService, PackageService, PaymentService
Sistem: Padjajaran CCTV, Cimahi
"""
from __future__ import annotations
from sqlalchemy.exc import IntegrityError
import hashlib
import hmac
import json
import logging
import math
import secrets
import string
from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import selectinload
from sqlmodel import select
from backend.data.stock.model import Stock
from backend.db.cdn import upload_file  # 🆕 Import upload helper

import httpx
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .model import (
    ServiceBooking, ServicePricingConfig, ServicePackage,
    ServicePackageItem, ServicePayment,
    BookingStatus, PaymentStatus, PaymentType, ServiceCategory,
    Technician, ServiceHoliday, ServiceOperationalHours
)
from .schema import (
    EstimateRequest, EstimateResponse, EstimateBreakdown,
    BookingCreateDirect, BookingResponse,
    PricingConfigResponse, AddonConfig,
    PackageItemResponse, PackageResponse,
    PackageCreate, PackageItemCreate,
    DistanceCheckRequest, DistanceCheckResponse,
    CreatePaymentRequest, MidtransWebhookPayload,
    SlotInfo, AvailableSlotsResponse,
    BookingPaymentInfo,
)

# 🆕 Import untuk notifikasi
from backend.auth.model import UserMap
from backend.db.supabse import SupabaseNotificationService
from backend.data.activity.service import ActivityService

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

HQ_LATITUDE  = -6.8861
HQ_LONGITUDE = 107.5425

PRICING_CACHE_KEY  = "service:pricing:active"
PRICING_CACHE_TTL  = 3_600
DRAFT_TTL          = 1_800
SLOT_LOCK_TTL      = 300
RATE_LIMIT_TTL     = 60
RATE_LIMIT_MAX     = 5
MAX_BOOKINGS_PER_SLOT = 3

SLOT_LABELS = {
    "08:00-11:00": "Pagi (08:00–11:00 WIB)",
    "11:00-14:00": "Siang (11:00–14:00 WIB)",
    "14:00-17:00": "Sore (14:00–17:00 WIB)",
}

CATEGORY_META = {
    "installation":  {"label": "Pemasangan Baru",    "icon": "home",         "desc": "Instalasi CCTV dari awal"},
    "maintenance":   {"label": "Perbaikan & Service", "icon": "wrench",       "desc": "Servis & maintenance rutin"},
    "consultation":  {"label": "Konsultasi",          "icon": "message-circle","desc": "Survey & rekomendasi sistem"},
    "troubleshoot":  {"label": "Troubleshoot",        "icon": "search-x",     "desc": "Diagnosa masalah CCTV"},
}


# ═══════════════════════════════════════════════════════════════════
# HAVERSINE
# ═══════════════════════════════════════════════════════════════════

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


# ═══════════════════════════════════════════════════════════════════
# 🆕 NOTIFICATION HELPER
# ═══════════════════════════════════════════════════════════════════

async def _get_supabase_user_id_from_local(session: AsyncSession, local_user_id: UUID) -> Optional[str]:
    """Ambil supabase_user_id dari user_maps."""
    try:
        result = await session.exec(
            select(UserMap).where(UserMap.local_user_id == str(local_user_id))
        )
        user_map = result.one_or_none()
        if user_map:
            return user_map.supabase_user_id
        logger.warning(f"UserMap not found for local_user_id: {local_user_id}")
        return None
    except Exception as e:
        logger.error(f"Error getting supabase_user_id: {e}")
        return None


async def _send_service_notification(
    session: AsyncSession,
    local_user_id: UUID,
    title: str,
    content: str,
    booking_number: str,
    notif_type: str = "order",
):
    """Kirim notifikasi ke Supabase. Error tidak boleh menghentikan proses utama."""
    try:
        if not local_user_id:
            logger.warning("❌ local_user_id is None, skipping notification")
            return

        # Cari supabase_user_id dari user_maps
        supabase_user_id = await _get_supabase_user_id_from_local(session, local_user_id)
        if not supabase_user_id:
            logger.warning(f"❌ UserMap not found for local_user_id={local_user_id}, cannot send notification")
            return

        metadata = {
            "booking_number": booking_number,
            "url": f"/booking/status/{booking_number}"
        }

        logger.info(f"📤 Sending notification to supabase_user={supabase_user_id}: {title}")

        await SupabaseNotificationService.send_notification(
            user_id=supabase_user_id,
            title=title,
            content=content or "",
            action_url=metadata["url"],
            notif_type=notif_type,
            metadata=metadata,
        )
        logger.info(f"✅ Notification sent: {title}")
    except Exception as e:
        # Jangan raise, cukup log error
        logger.error(f"❌ Failed to send notification '{title}': {e}", exc_info=True)
# ═══════════════════════════════════════════════════════════════════
# PRICING ENGINE
# ═══════════════════════════════════════════════════════════════════

class PricingEngine:

    @staticmethod
    def calculate(
        config: ServicePricingConfig,
        category: str,
        camera_count: int,
        brand: str,
        addons: List[str],
        distance_km: float,
        device_price: int = 0,
    ) -> Dict[str, Any]:
        brand_norm = brand.lower().strip()

        if category == ServiceCategory.CONSULTATION:
            service_price = config.consultation_fee
            base_per_cam  = config.consultation_fee
            multiplier    = 1.0
        else:
            base_per_cam  = config.base_price_per_camera.get(category, 150_000)
            multiplier    = config.brand_multiplier.get(brand_norm, 1.0)
            service_price = int(base_per_cam * camera_count * multiplier)

        addon_map   = {a["key"]: a for a in config.addons_config}
        addon_price = 0
        addon_breakdown: List[Dict[str, Any]] = []
        for key in addons:
            a = addon_map.get(key)
            if not a:
                continue
            price = a["price"] * camera_count if a["type"] == "per_cam" else a["price"]
            addon_price += price
            addon_breakdown.append({
                "key":   key,
                "label": a.get("label", key),
                "type":  a["type"],
                "price": price,
            })

        if distance_km == 0:
            transport_fee = 0
        else:
            raw = int(distance_km * config.transport_per_km)
            transport_fee = max(
                config.transport_min_fee,
                min(raw, config.transport_max_fee),
            )

        total_price      = device_price + service_price + addon_price + transport_fee
        dp_amount        = int(total_price * config.dp_percentage / 100)
        remaining_amount = total_price - dp_amount

        breakdown = EstimateBreakdown(
            base_per_camera   = base_per_cam,
            camera_count      = camera_count,
            brand_multiplier  = multiplier,
            service_price     = service_price,
            addons            = addon_breakdown,
            addon_price       = addon_price,
            device_price      = device_price,
            distance_km       = distance_km,
            transport_per_km  = config.transport_per_km,
            transport_fee     = transport_fee,
            dp_percentage     = config.dp_percentage,
            dp_amount         = dp_amount,
            remaining_amount  = remaining_amount,
            total_price       = total_price,
        )

        return {
            "device_price":     device_price,
            "service_price":    service_price,
            "addon_price":      addon_price,
            "transport_fee":    transport_fee,
            "total_price":      total_price,
            "dp_amount":        dp_amount,
            "remaining_amount": remaining_amount,
            "dp_percentage":    config.dp_percentage,
            "breakdown":        breakdown,
        }


# ═══════════════════════════════════════════════════════════════════
# MIDTRANS SERVICE
# ═══════════════════════════════════════════════════════════════════

class MidtransService:
    """Wrapper Midtrans Snap API."""

    def __init__(self, server_key: str, is_production: bool = False):
        self.server_key  = server_key
        self.base_url    = (
            "https://app.midtrans.com/snap/v1"
            if is_production
            else "https://app.sandbox.midtrans.com/snap/v1"
        )
        self.notify_url_base = (
            "https://api.padjajaran.id"
            if is_production
            else "https://dev.padjajaran.id"
        )

    async def create_transaction(
        self,
        order_id: str,
        gross_amount: int,
        customer: Dict[str, str],
        item_details: List[Dict[str, Any]],
        expiry_minutes: int = 1440,
    ) -> Dict[str, Any]:
        import base64
        auth = base64.b64encode(f"{self.server_key}:".encode()).decode()

        payload = {
            "transaction_details": {
                "order_id":     order_id,
                "gross_amount": gross_amount,
            },
            "customer_details": customer,
            "item_details": item_details,
            "expiry": {
                "unit":     "minutes",
                "duration": expiry_minutes,
            },
            "callbacks": {
                "finish":       f"{self.notify_url_base}/pembayaran/selesai",
                "error":        f"{self.notify_url_base}/pembayaran/gagal",
                "pending":      f"{self.notify_url_base}/pembayaran/pending",
            },
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.base_url}/transactions",
                json=payload,
                headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
            )

        if resp.status_code not in (200, 201):
            logger.error(f"Midtrans error {resp.status_code}: {resp.text}")
            raise HTTPException(502, "Gagal membuat transaksi pembayaran")

        return resp.json()

    def verify_signature(self, order_id: str, status_code: str, gross_amount: str, signature_key: str) -> bool:
        raw = f"{order_id}{status_code}{gross_amount}{self.server_key}"
        expected = hashlib.sha512(raw.encode()).hexdigest()
        return hmac.compare_digest(expected, signature_key)


# ═══════════════════════════════════════════════════════════════════
# BOOKING SERVICE
# ═══════════════════════════════════════════════════════════════════

def _get_redis():
    from backend.db.redis import get_redis_token
    return get_redis_token()


class BookingService:

    # ── Pricing Config ────────────────────────────────────────────

    async def get_active_pricing_config(self, session: AsyncSession) -> ServicePricingConfig:
        r = _get_redis()

        cached = await r.get(PRICING_CACHE_KEY)
        if cached:
            try:
                data = json.loads(cached)
                return ServicePricingConfig(**data)
            except Exception as e:
                logger.warning(f"Pricing cache parse error: {e}")

        result = await session.exec(
            select(ServicePricingConfig)
            .where(ServicePricingConfig.is_active == True)
            .order_by(ServicePricingConfig.created_at.desc())
            .limit(1)
        )
        config = result.first()
        if not config:
            raise HTTPException(503, "Pricing config belum dikonfigurasi. Hubungi admin.")

        await r.set(
            PRICING_CACHE_KEY,
            json.dumps({
                "uuid":                  str(config.uuid),
                "base_price_per_camera": config.base_price_per_camera,
                "brand_multiplier":      config.brand_multiplier,
                "consultation_fee":      config.consultation_fee,
                "transport_per_km":      config.transport_per_km,
                "transport_min_fee":     config.transport_min_fee,
                "transport_max_fee":     config.transport_max_fee,
                "max_distance_km":       config.max_distance_km,
                "addons_config":         config.addons_config,
                "routes_config":         config.routes_config,
                "dp_percentage":         config.dp_percentage,
                "is_active":             config.is_active,
                "created_at":            config.created_at.isoformat(),
                "updated_at":            config.updated_at.isoformat(),
            }),
            ex=PRICING_CACHE_TTL,
        )
        return config

    async def invalidate_pricing_cache(self) -> None:
        await _get_redis().delete(PRICING_CACHE_KEY)

    def build_pricing_response(self, config: ServicePricingConfig) -> PricingConfigResponse:
        categories = []
        for cat_id, meta in CATEGORY_META.items():
            base = (
                config.consultation_fee
                if cat_id == "consultation"
                else config.base_price_per_camera.get(cat_id, 0)
            )
            categories.append({
                "id":         cat_id,
                "label":      meta["label"],
                "icon":       meta["icon"],
                "desc":       meta["desc"],
                "base_price": base,
            })

        brands = [
            {"key": k, "label": k.title(), "multiplier": v}
            for k, v in config.brand_multiplier.items()
        ]

        addons = [
            AddonConfig(
                key=a["key"],
                label=a.get("label", a["key"]),
                type=a["type"],
                price=a["price"],
                description=a.get("description"),
                icon=a.get("icon"),
            )
            for a in config.addons_config
        ]

        return PricingConfigResponse(
            uuid=config.uuid,
            categories=categories,
            brands=brands,
            addons=addons,
            consultation_fee=config.consultation_fee,
            transport_per_km=config.transport_per_km,
            transport_min_fee=config.transport_min_fee,
            transport_max_fee=config.transport_max_fee,
            max_distance_km=config.max_distance_km,
            dp_percentage=config.dp_percentage,
            routes=config.routes_config or [],
            is_active=config.is_active,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )

    # ── Distance Check ────────────────────────────────────────────

    async def check_distance(
        self, req: DistanceCheckRequest, session: AsyncSession
    ) -> DistanceCheckResponse:
        config = await self.get_active_pricing_config(session)

        km = haversine_km(HQ_LATITUDE, HQ_LONGITUDE, req.latitude, req.longitude)
        km = max(0, km - 100)
        km = round(km, 2)

        within = km <= config.max_distance_km
        if km == 0:
            fee = 0
        else:
            raw = int(km * config.transport_per_km)
            fee = max(config.transport_min_fee, min(raw, config.transport_max_fee))

        if not within:
            msg = (
                f"Maaf, lokasi Anda berjarak {km:.1f} km dari markas kami. "
                f"Batas layanan kami adalah {config.max_distance_km:.0f} km."
            )
        else:
            msg = f"Lokasi Anda berjarak {km:.1f} km, estimasi biaya transport {_fmt_rp(fee)}."

        return DistanceCheckResponse(
            distance_km=km,
            transport_fee=fee,
            is_within_range=within,
            max_distance_km=config.max_distance_km,
            message=msg,
        )

    # ── Estimate ──────────────────────────────────────────────────

    async def estimate(self, req: EstimateRequest, session: AsyncSession) -> EstimateResponse:
        config = await self.get_active_pricing_config(session)

        device_price = 0
        if req.package_uuid:
            pkg_result = await session.exec(
                select(ServicePackage).where(ServicePackage.uuid == req.package_uuid)
            )
            pkg = pkg_result.first()
            if pkg:
                device_price = pkg.device_price

        result = PricingEngine.calculate(
            config=config,
            category=req.category,
            camera_count=req.camera_count,
            brand=req.brand,
            addons=req.addons,
            distance_km=req.distance_km,
            device_price=device_price,
        )
        return EstimateResponse(
            device_price=result["device_price"],
            service_price=result["service_price"],
            addon_price=result["addon_price"],
            transport_fee=result["transport_fee"],
            total_price=result["total_price"],
            dp_amount=result["dp_amount"],
            remaining_amount=result["remaining_amount"],
            dp_percentage=result["dp_percentage"],
            breakdown=result["breakdown"],
        )

    # ── Draft Wizard ──────────────────────────────────────────────

    async def save_draft_step(
        self,
        session_id: str,
        step: int,
        data: Dict[str, Any],
        session: AsyncSession,
    ) -> Dict[str, Any]:
        r = _get_redis()
        key = f"booking:draft:{session_id}"

        raw = await r.get(key)
        draft: Dict[str, Any] = json.loads(raw) if raw else {}

        draft[f"step{step}"] = data
        draft["last_step"]   = step
        draft["updated_at"]  = datetime.now(timezone.utc).isoformat()

        estimate = None
        if draft.get("step1") and draft.get("step2"):
            try:
                s1, s2 = draft["step1"], draft["step2"]
                config  = await self.get_active_pricing_config(session)
                pricing = PricingEngine.calculate(
                    config=config,
                    category=s1["category"],
                    camera_count=s1["camera_count"],
                    brand=s1["brand"],
                    addons=s1.get("addons", []),
                    distance_km=s2["distance_km"],
                    device_price=0,
                )
                draft["estimate"] = {k: v for k, v in pricing.items() if k != "breakdown"}
                estimate = EstimateResponse(
                    device_price=pricing["device_price"],
                    service_price=pricing["service_price"],
                    addon_price=pricing["addon_price"],
                    transport_fee=pricing["transport_fee"],
                    total_price=pricing["total_price"],
                    dp_amount=pricing["dp_amount"],
                    remaining_amount=pricing["remaining_amount"],
                    dp_percentage=pricing["dp_percentage"],
                    breakdown=pricing["breakdown"],
                )
            except Exception as e:
                logger.warning(f"Draft estimate error: {e}")

        await r.set(key, json.dumps(draft, default=str), ex=DRAFT_TTL)

        return {
            "session_id":     session_id,
            "step_completed": step,
            "draft_data":     draft,
            "estimate":       estimate,
            "expires_in":     DRAFT_TTL,
        }

    async def get_draft(self, session_id: str) -> Optional[Dict[str, Any]]:
        raw = await _get_redis().get(f"booking:draft:{session_id}")
        return json.loads(raw) if raw else None

    async def delete_draft(self, session_id: str) -> None:
        await _get_redis().delete(f"booking:draft:{session_id}")

    # ── Booking Number ────────────────────────────────────────────

    @staticmethod
    def _gen_booking_number() -> str:
        today  = datetime.now().strftime("%Y%m%d")
        suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f"BK-{today}-{suffix}"

    # ── Slot Lock ─────────────────────────────────────────────────

    async def _acquire_slot_lock(self, scheduled_date: date, time_slot: str) -> Tuple[bool, str]:
        r   = _get_redis()
        key = f"slot:lock:{scheduled_date}:{time_slot}"
        ok  = await r.set(key, "1", ex=SLOT_LOCK_TTL, nx=True)
        return bool(ok), key

    async def _release_slot_lock(self, lock_key: str) -> None:
        await _get_redis().delete(lock_key)

    async def _get_active_tech_count(self, session: AsyncSession) -> int:
        from sqlalchemy import func
        res = await session.exec(select(func.count(Technician.uuid)).where(Technician.is_active == True))
        count = res.one()
        return max(1, count) # Minimal 1 sebagai fallback

    async def _count_active_slot(
        self, session: AsyncSession, scheduled_date: date, time_slot: str
    ) -> int:
        # Menghitung semua booking yang tidak dibatalkan pada tanggal & slot tersebut
        stmt = select(ServiceBooking).where(
            ServiceBooking.scheduled_date == scheduled_date,
            ServiceBooking.time_slot      == time_slot,
            ServiceBooking.status != BookingStatus.CANCEL
        )
        result = await session.exec(stmt)
        return len(result.all())

    # ── Submit dari Draft ─────────────────────────────────────────

    async def submit_from_draft(
        self,
        session_id: str,
        session: AsyncSession,
        user_uuid: Optional[UUID] = None,
    ) -> ServiceBooking:
        draft = await self.get_draft(session_id)
        if not draft:
            raise HTTPException(400, "Draft tidak ditemukan atau sudah kadaluarsa (30 menit)")

        s1, s2, s3 = draft.get("step1"), draft.get("step2"), draft.get("step3")
        if not all([s1, s2, s3]):
            missing = [i + 1 for i, s in enumerate([s1, s2, s3]) if not s]
            raise HTTPException(400, f"Draft belum lengkap. Step belum diisi: {missing}")

        scheduled_date = date.fromisoformat(s2["scheduled_date"])
        if scheduled_date <= date.today():
            raise HTTPException(400, "Tanggal booking sudah lewat")

        config = await self.get_active_pricing_config(session)
        if s2["distance_km"] > config.max_distance_km:
            raise HTTPException(
                400,
                f"Jarak {s2['distance_km']:.1f} km melebihi batas layanan {config.max_distance_km:.0f} km"
            )

        # 🆕 DYNAMIC CAPACITY CHECK
        max_capacity = await self._get_active_tech_count(session)
        current_booked = await self._count_active_slot(session, scheduled_date, s2["time_slot"])
        
        if current_booked >= max_capacity:
            raise HTTPException(409, f"Slot ini sudah penuh ({max_capacity} teknisi sedang bertugas). Pilih waktu lain.")

        acquired, lock_key = await self._acquire_slot_lock(scheduled_date, s2["time_slot"])
        if not acquired:
            raise HTTPException(409, "Sedang ada proses booking di slot yang sama. Coba lagi.")

        try:
            device_price  = 0
            package_snap  = None
            package_uuid  = UUID(s1["package_uuid"]) if s1.get("package_uuid") else None

            if package_uuid:
                pkg_res = await session.exec(
                    select(ServicePackage).where(ServicePackage.uuid == package_uuid)
                )
                pkg = pkg_res.first()
                if pkg:
                    device_price = pkg.device_price
                    package_snap = {
                        "uuid":   str(pkg.uuid),
                        "name":   pkg.name,
                        "slug":   pkg.slug,
                    }

            pricing = PricingEngine.calculate(
                config=config,
                category=s1["category"],
                camera_count=s1["camera_count"],
                brand=s1["brand"],
                addons=s1.get("addons", []),
                distance_km=s2["distance_km"],
                device_price=device_price,
            )

            booking = ServiceBooking(
                user_uuid         = user_uuid,
                package_uuid      = package_uuid,
                pricing_config_uuid = config.uuid,
                booking_number    = self._gen_booking_number(),
                category          = s1["category"],
                camera_count      = s1["camera_count"],
                brand             = s1["brand"],
                addons            = s1.get("addons", []),
                package_snapshot  = package_snap,
                scheduled_date    = scheduled_date,
                time_slot         = s2["time_slot"],
                address           = s2["address"],
                district          = s2.get("district"),
                city              = s2["city"],
                distance_km       = s2["distance_km"],
                latitude          = s2.get("latitude"),
                longitude         = s2.get("longitude"),
                contact_name      = s3["contact_name"],
                contact_phone     = s3["contact_phone"],
                contact_notes     = s3.get("contact_notes"),
                device_price      = pricing["device_price"],
                service_price     = pricing["service_price"],
                addon_price       = pricing["addon_price"],
                transport_fee     = pricing["transport_fee"],
                total_price       = pricing["total_price"],
                dp_percentage     = pricing["dp_percentage"],
                dp_amount         = pricing["dp_amount"],
                remaining_amount  = pricing["remaining_amount"],
                price_breakdown   = pricing["breakdown"].model_dump(),
                status            = BookingStatus.PENDING,
                slot_lock_key     = lock_key,
            )

            session.add(booking)
            # 📝 Log Activity
            await ActivityService(session).log_activity(
                activity_type="booking",
                title="📅 Booking Baru",
                description=f"Booking {booking.booking_number} ({booking.category}) dibuat oleh {booking.contact_name}",
                reference_id=booking.booking_number,
                user_id=user_uuid,
                status="pending",
                amount=int(booking.total_price),
                icon="i-heroicons-calendar-days",
                color="blue"
            )

            await session.commit()
            await session.refresh(booking)
            await self.delete_draft(session_id)

            # 🆕 NOTIFIKASI: Booking Dibuat
            if user_uuid:
                await _send_service_notification(
                    session=session,
                    local_user_id=user_uuid,
                    title="📋 Booking Jasa Dibuat",
                    content=f"Booking #{booking.booking_number} untuk layanan {s1['category']} telah dibuat. Menunggu konfirmasi admin.",
                    booking_number=booking.booking_number,
                    notif_type="order",
                )

            return booking

        except HTTPException:
            await self._release_slot_lock(lock_key)
            raise
        except Exception as e:
            await self._release_slot_lock(lock_key)
            await session.rollback()
            logger.error(f"submit_from_draft error: {e}")
            raise HTTPException(500, "Gagal membuat booking. Coba lagi.")

    # ── Get ───────────────────────────────────────────────────────

    async def get_booking(self, booking_uuid: UUID, session: AsyncSession) -> ServiceBooking:
        result = await session.exec(
            select(ServiceBooking)
            .where(ServiceBooking.uuid == booking_uuid)
            .options(selectinload(ServiceBooking.technician))
        )
        b = result.first()
        if not b:
            raise HTTPException(404, "Booking tidak ditemukan")
        return b

    async def get_booking_by_number(self, number: str, session: AsyncSession) -> ServiceBooking:
        result = await session.exec(
            select(ServiceBooking)
            .where(ServiceBooking.booking_number == number)
            .options(selectinload(ServiceBooking.technician))
        )
        b = result.first()
        if not b:
            raise HTTPException(404, "Booking tidak ditemukan")
        return b

    async def get_booking_payments(
        self, booking_uuid: UUID, session: AsyncSession
    ) -> List[ServicePayment]:
        result = await session.exec(
            select(ServicePayment).where(ServicePayment.booking_uuid == booking_uuid)
        )
        return list(result.all())

    # ── Admin: list ───────────────────────────────────────────────

    async def list_bookings(
        self,
        session: AsyncSession,
        status: Optional[BookingStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        stmt = select(ServiceBooking)
        if status:
            stmt = stmt.where(ServiceBooking.status == status)
        if date_from:
            stmt = stmt.where(ServiceBooking.scheduled_date >= date_from)
        if date_to:
            stmt = stmt.where(ServiceBooking.scheduled_date <= date_to)
        stmt = stmt.order_by(ServiceBooking.created_at.desc())

        all_r = await session.exec(stmt)
        total = len(all_r.all())

        stmt  = stmt.offset((page - 1) * size).limit(size)
        items = (await session.exec(stmt)).all()
        return {"items": list(items), "total": total, "page": page, "size": size}

    # ── Admin: update status (state machine) ──────────────────────

    VALID_TRANSITIONS = {
        BookingStatus.PENDING:   [BookingStatus.CONFIRMED, BookingStatus.CANCEL],
        BookingStatus.CONFIRMED: [BookingStatus.DP_PAID,   BookingStatus.CANCEL],
        BookingStatus.DP_PAID:   [BookingStatus.PROGRESS,  BookingStatus.CANCEL],
        BookingStatus.PROGRESS:  [BookingStatus.DONE],
        BookingStatus.DONE:      [BookingStatus.LUNAS],
        BookingStatus.LUNAS:     [],
        BookingStatus.CANCEL:    [],
    }

    async def update_status(
        self,
        booking_uuid: UUID,
        new_status: BookingStatus,
        session: AsyncSession,
        notes: Optional[str] = None,
        technician_uuid: Optional[UUID] = None,
    ) -> ServiceBooking:
        stmt = select(ServiceBooking).where(ServiceBooking.uuid == booking_uuid).options(
            selectinload(ServiceBooking.technician)
        )
        res = await session.exec(stmt)
        booking = res.first()
        if not booking:
            raise HTTPException(404, "Booking tidak ditemukan")

        old_status = booking.status
        
        # 🔄 ALLOW SELF-TRANSITION (Untuk update data lain spt teknisi tanpa ubah status)
        allowed = self.VALID_TRANSITIONS.get(booking.status, [])
        if new_status != old_status and new_status not in allowed:
            raise HTTPException(
                400,
                f"Transisi tidak valid: '{booking.status}' → '{new_status}'. "
                f"Diizinkan: {[s.value for s in allowed]}"
            )
        
        booking.status = new_status
        
        if technician_uuid:
            # 🆕 CEK KONFLIK JADWAL TEKNISI
            check = await self.check_technician_availability(
                technician_uuid=technician_uuid,
                target_date=booking.scheduled_date,
                target_slot=booking.time_slot,
                exclude_booking_uuid=booking.uuid,
                session=session
            )
            
            if check["conflict"]:
                raise HTTPException(409, check["message"])
                
            booking.technician_uuid = technician_uuid
        
        # 📝 Log Activity Status Update
        await ActivityService(session).log_activity(
            activity_type="booking",
            title=f"🔄 Status Booking: {new_status.value}",
            description=f"Booking {booking.booking_number} diperbarui ke status {new_status.value}",
            reference_id=booking.booking_number,
            user_id=booking.user_uuid,
            status=new_status.value,
            amount=int(booking.total_price),
            icon="i-heroicons-arrow-path",
            color="orange"
        )
        
        if new_status in (BookingStatus.CANCEL, BookingStatus.LUNAS):
            if booking.slot_lock_key:
                await self._release_slot_lock(booking.slot_lock_key)
        
        session.add(booking)
        await session.commit()
        await session.refresh(booking)

        # 🆕 NOTIFIKASI: Status berubah
        if booking.user_uuid and old_status != new_status:
            status_labels = {
                BookingStatus.PENDING: "Menunggu",
                BookingStatus.CONFIRMED: "Dikonfirmasi",
                BookingStatus.DP_PAID: "DP Dibayar",
                BookingStatus.PROGRESS: "Dalam Pengerjaan",
                BookingStatus.DONE: "Selesai",
                BookingStatus.LUNAS: "Lunas",
                BookingStatus.CANCEL: "Dibatalkan",
            }
            
            label = status_labels.get(new_status, new_status.value)
            
            await _send_service_notification(
                session=session,
                local_user_id=booking.user_uuid,
                title=f"🔔 Status Booking: {label}",
                content=f"Booking #{booking.booking_number} statusnya berubah menjadi {label}. {notes or ''}",
                booking_number=booking.booking_number,
                notif_type="order",
            )

        return booking

    # ── Available Slots ───────────────────────────────────────────

    async def get_available_slots(
        self, target_date: date, session: AsyncSession
    ) -> AvailableSlotsResponse:
        from .model import TimeSlot, ServiceHoliday, ServiceOperationalHours
        
        # 1. Cek apakah tanggal ini hari libur
        holiday_stmt = select(ServiceHoliday).where(ServiceHoliday.holiday_date == target_date)
        is_holiday = (await session.exec(holiday_stmt)).first()
        
        # 2. Ambil konfigurasi operasional untuk hari tersebut (0=Senin, 6=Minggu)
        # Note: target_date.weekday() di python 0=Senin, 6=Minggu. 
        # Kita sesuaikan dengan data seeder (0-6)
        day_of_week = target_date.weekday()
        op_stmt = select(ServiceOperationalHours).where(ServiceOperationalHours.day_of_week == day_of_week)
        op_config = (await session.exec(op_stmt)).first()
        
        is_open = True
        
        # 🆕 DYNAMIC CAPACITY PER SLOT = JUMLAH TEKNISI AKTIF
        tech_count = await self._get_active_tech_count(session)
        limit_per_slot = tech_count
        
        if is_holiday:
            is_open = False
        elif op_config:
            is_open = op_config.is_open
            # Jika admin menset max_bookings di jam operasional, gunakan nilai terkecil 
            # (Misal: teknisi ada 5, tapi admin ingin batasi max 3 booking per slot)
            if op_config.max_bookings > 0:
                limit_per_slot = min(tech_count, op_config.max_bookings)

        slots = []
        for slot in TimeSlot:
            booked = 0
            if is_open:
                booked = await self._count_active_slot(session, target_date, slot.value)
            
            remaining = max(0, limit_per_slot - booked)
            slots.append(SlotInfo(
                slot      = slot.value,
                label     = SLOT_LABELS.get(slot.value, slot.value),
                available = is_open and remaining > 0,
                remaining = remaining if is_open else 0,
                booked    = booked,
            ))
            
        return AvailableSlotsResponse(
            date=target_date, 
            slots=slots,
            message="Toko Libur" if is_holiday else "Toko Tutup" if not is_open else None
        )

    # ── Stats ─────────────────────────────────────────────────────

    async def get_stats(self, session: AsyncSession) -> Dict[str, Any]:
        result    = await session.exec(select(ServiceBooking))
        bookings  = result.all()

        by_status: Dict[str, int] = {}
        revenue   = 0
        dp_revenue= 0

        for b in bookings:
            by_status[b.status] = by_status.get(b.status, 0) + 1
            if b.status in (BookingStatus.LUNAS, BookingStatus.DONE):
                revenue += b.total_price
            if b.status in (BookingStatus.DP_PAID, BookingStatus.PROGRESS,
                            BookingStatus.DONE, BookingStatus.LUNAS):
                dp_revenue += b.dp_amount

        paid_count = (
            by_status.get(BookingStatus.LUNAS, 0)
            + by_status.get(BookingStatus.DONE, 0)
        )
        return {
            "total":           len(bookings),
            "by_status":       by_status,
            "total_revenue":   revenue,
            "dp_revenue":      dp_revenue,
            "avg_order_value": revenue // paid_count if paid_count else 0,
        }

    # ── Technician Management ─────────────────────────────────────

    async def list_technicians(self, session: AsyncSession, active_only: bool = True) -> List[Technician]:
        stmt = select(Technician)
        if active_only:
            stmt = stmt.where(Technician.is_active == True)
        res = await session.exec(stmt)
        return list(res.all())

    async def create_technician(self, data: Dict[str, Any], session: AsyncSession) -> Technician:
        tech = Technician(**data)
        session.add(tech)
        await session.commit()
        await session.refresh(tech)
        return tech

    async def update_technician(self, uuid: UUID, data: Dict[str, Any], session: AsyncSession) -> Technician:
        tech = await session.get(Technician, uuid)
        if not tech: raise HTTPException(404, "Teknisi tidak ditemukan")
        for k, v in data.items():
            setattr(tech, k, v)
        session.add(tech)
        await session.commit()
        await session.refresh(tech)
        return tech

    async def check_technician_availability(
        self, 
        technician_uuid: UUID, 
        target_date: date, 
        target_slot: str, 
        exclude_booking_uuid: Optional[UUID],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Cek apakah teknisi tersedia pada tanggal & slot tersebut.
        Returns: { "available": bool, "conflict": bool, "tight": bool, "message": str }
        """
        # 1. Ambil semua booking teknisi ini pada tanggal tersebut
        stmt = select(ServiceBooking).where(
            ServiceBooking.technician_uuid == technician_uuid,
            ServiceBooking.scheduled_date == target_date,
            ServiceBooking.status != BookingStatus.CANCEL
        )
        if exclude_booking_uuid:
            stmt = stmt.where(ServiceBooking.uuid != exclude_booking_uuid)
            
        result = await session.exec(stmt)
        existing_bookings = result.all()
        
        slot_order = {
            "08:00-11:00": 0,
            "11:00-14:00": 1,
            "14:00-17:00": 2
        }
        
        target_idx = slot_order.get(target_slot)
        if target_idx is None:
            return {"available": True, "conflict": False, "tight": False, "message": "Slot tidak valid"}

        conflict = False
        tight = False
        conflict_booking = None
        
        for b in existing_bookings:
            b_idx = slot_order.get(b.time_slot)
            if b_idx == target_idx:
                conflict = True
                conflict_booking = b.booking_number
                break
            elif abs(b_idx - target_idx) == 1:
                tight = True
                conflict_booking = b.booking_number
        
        if conflict:
            return {
                "available": False, 
                "conflict": True, 
                "tight": False, 
                "message": f"Teknisi sudah ditugaskan pada {target_slot} (Booking {conflict_booking})"
            }
        
        if tight:
            return {
                "available": True, 
                "conflict": False, 
                "tight": True, 
                "message": f"Jadwal mepet dengan Booking {conflict_booking} (selisih < 2 jam)"
            }
            
        return {"available": True, "conflict": False, "tight": False, "message": "Tersedia"}

    async def get_technician_detail(self, uuid: UUID, session: AsyncSession) -> Technician:
        stmt = select(Technician).where(Technician.uuid == uuid).options(
            selectinload(Technician.bookings)
        )
        res = await session.exec(stmt)
        tech = res.first()
        if not tech:
            raise HTTPException(404, "Teknisi tidak ditemukan")
        
        # Filter bookings yang tidak cancel, urutkan terbaru
        tech.bookings = sorted(
            [b for b in tech.bookings if b.status != BookingStatus.CANCEL],
            key=lambda x: (x.scheduled_date, x.time_slot),
            reverse=True
        )
        return tech

    # ── Holiday & Operational Management ──────────────────────────

    async def list_holidays(self, session: AsyncSession) -> List[ServiceHoliday]:
        res = await session.exec(select(ServiceHoliday).order_by(ServiceHoliday.holiday_date.asc()))
        return list(res.all())

    async def create_holiday(self, holiday_date: date, description: str, session: AsyncSession) -> ServiceHoliday:
        h = ServiceHoliday(holiday_date=holiday_date, description=description)
        session.add(h)
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(400, "Tanggal libur sudah ada")
        await session.refresh(h)
        return h

    async def delete_holiday(self, uuid: UUID, session: AsyncSession):
        h = await session.get(ServiceHoliday, uuid)
        if h:
            await session.delete(h)
            await session.commit()

    async def list_operational_hours(self, session: AsyncSession) -> List[ServiceOperationalHours]:
        res = await session.exec(select(ServiceOperationalHours).order_by(ServiceOperationalHours.day_of_week.asc()))
        return list(res.all())

    async def update_operational_hours(self, day: int, data: Dict[str, Any], session: AsyncSession) -> ServiceOperationalHours:
        stmt = select(ServiceOperationalHours).where(ServiceOperationalHours.day_of_week == day)
        res = await session.exec(stmt)
        oh = res.first()
        if not oh:
            oh = ServiceOperationalHours(day_of_week=day, **data)
        else:
            for k, v in data.items():
                setattr(oh, k, v)
        session.add(oh)
        await session.commit()
        await session.refresh(oh)
        return oh


# ═══════════════════════════════════════════════════════════════════
# PACKAGE SERVICE
# ═══════════════════════════════════════════════════════════════════

class PackageService:

    async def create_package(
        self, data: PackageCreate, session: AsyncSession, image_file: Optional[bytes] = None
    ) -> ServicePackage:
        thumbnail_url = data.thumbnail_url
        if image_file:
            # Upload image to CDN
            filename = f"{uuid.uuid4()}.webp"
            thumbnail_url = await upload_file(
                file=image_file,
                folder="services/packages",
                filename=filename,
                content_type="image/webp"
            )

        pkg = ServicePackage(
            name          = data.name,
            slug          = data.slug,
            description   = data.description,
            category      = data.category,
            camera_count  = data.camera_count,
            default_brand = data.default_brand,
            thumbnail_url = thumbnail_url,
            highlights    = data.highlights,
            is_active     = data.is_active,
            sort_order    = data.sort_order,
        )
        session.add(pkg)

        try:
            await session.flush()
        except IntegrityError as e:
            await session.rollback()
            if "ix_service_package_slug" in str(e.orig):
                raise HTTPException(409, f"Slug '{data.slug}' sudah digunakan.")
            raise HTTPException(409, "Duplikat data paket.")

        device_total = 0
        for item in data.items:
            from backend.data.stock.model import Stock
            stock_res = await session.exec(select(Stock).where(Stock.uuid == item.stock_uuid))
            stock     = stock_res.first()
            if not stock:
                raise HTTPException(404, f"Stock {item.stock_uuid} tidak ditemukan")

            unit_price   = item.override_price if item.override_price is not None else stock.online_price
            device_total += unit_price * item.quantity

            spi = ServicePackageItem(
                package_uuid   = pkg.uuid,
                stock_uuid     = item.stock_uuid,
                quantity       = item.quantity,
                override_price = item.override_price,
                label          = item.label,
                sort_order     = item.sort_order,
            )
            session.add(spi)

        pkg.device_price = device_total
        session.add(pkg)
        await session.commit()
        await session.refresh(pkg)
        return pkg

    async def get_package(self, pkg_uuid: UUID, session: AsyncSession) -> ServicePackage:
        result = await session.exec(
            select(ServicePackage).where(ServicePackage.uuid == pkg_uuid)
        )
        pkg = result.first()
        if not pkg:
            raise HTTPException(404, "Paket tidak ditemukan")
        return pkg

    async def list_packages(
        self, session: AsyncSession, category: Optional[str] = None, active_only: bool = True
    ) -> List[ServicePackage]:
        stmt = select(ServicePackage)
        if active_only:
            stmt = stmt.where(ServicePackage.is_active == True)
        if category:
            stmt = stmt.where(ServicePackage.category == category)
        stmt = stmt.order_by(ServicePackage.sort_order, ServicePackage.created_at)
        result = await session.exec(stmt)
        return list(result.all())

    async def build_package_response(
        self, pkg: ServicePackage, session: AsyncSession, config: Optional[ServicePricingConfig] = None
    ) -> PackageResponse:
        items_result = await session.exec(
            select(ServicePackageItem).where(ServicePackageItem.package_uuid == pkg.uuid)
            .order_by(ServicePackageItem.sort_order)
        )
        items = list(items_result.all())

        item_responses = []
        for item in items:
            statement = (
                select(Stock)
                .where(Stock.uuid == item.stock_uuid)
                .options(selectinload(Stock.assets))
            )
            stock_res = await session.exec(statement)
            stock     = stock_res.first()
            
            if not stock:
                continue
                
            unit_price = item.override_price if item.override_price is not None else stock.online_price
            thumb      = stock.assets[0].url if stock.assets else None
            
            item_responses.append(PackageItemResponse(
                uuid           = item.uuid,
                stock_uuid     = item.stock_uuid,
                stock_title    = stock.title,
                stock_slug     = stock.slug,
                stock_thumbnail= thumb,
                quantity       = item.quantity,
                unit_price     = unit_price,
                subtotal       = unit_price * item.quantity,
                label          = item.label,
                sort_order     = item.sort_order,
            ))

        est_service = pkg.estimated_service_price
        if config and est_service == 0:
            base = config.base_price_per_camera.get(pkg.category, 150_000)
            mult = config.brand_multiplier.get(pkg.default_brand.lower(), 1.0)
            est_service = int(base * pkg.camera_count * mult)

        total_est = pkg.device_price + est_service
        dp_pct    = config.dp_percentage if config else 50
        dp_amount = int(total_est * dp_pct / 100)

        return PackageResponse(
            uuid                    = pkg.uuid,
            name                    = pkg.name,
            slug                    = pkg.slug,
            description             = pkg.description,
            category                = pkg.category,
            camera_count            = pkg.camera_count,
            default_brand           = pkg.default_brand,
            device_price            = pkg.device_price,
            estimated_service_price = est_service,
            total_estimated         = total_est,
            dp_amount               = dp_amount,
            thumbnail_url           = pkg.thumbnail_url,
            highlights              = pkg.highlights,
            items                   = item_responses,
            is_active               = pkg.is_active,
            sort_order              = pkg.sort_order,
            created_at              = pkg.created_at,
        )

    async def recalculate_device_price(self, pkg_uuid: UUID, session: AsyncSession) -> ServicePackage:
        pkg = await self.get_package(pkg_uuid, session)
        items_result = await session.exec(
            select(ServicePackageItem).where(ServicePackageItem.package_uuid == pkg_uuid)
        )
        items = list(items_result.all())

        from backend.data.stock.model import Stock
        total = 0
        for item in items:
            stock_res = await session.exec(select(Stock).where(Stock.uuid == item.stock_uuid))
            stock     = stock_res.first()
            if stock:
                unit = item.override_price if item.override_price is not None else stock.online_price
                total += unit * item.quantity

        pkg.device_price = total
        session.add(pkg)
        await session.commit()
        await session.refresh(pkg)
        return pkg

    async def update_package(
        self, pkg_uuid: UUID, updates: dict, session: AsyncSession, image_file: Optional[bytes] = None
    ) -> ServicePackage:
        pkg = await self.get_package(pkg_uuid, session)
        
        if image_file:
            # Upload image to CDN
            filename = f"{uuid.uuid4()}.webp"
            url = await upload_file(
                file=image_file,
                folder="services/packages",
                filename=filename,
                content_type="image/webp"
            )
            pkg.thumbnail_url = url
        elif "thumbnail_url" in updates:
            pkg.thumbnail_url = updates["thumbnail_url"]

        allowed = {"name", "description", "category", "camera_count", "default_brand", "highlights", "is_active", "sort_order", "estimated_service_price"}
        for k, v in updates.items():
            if k in allowed:
                setattr(pkg, k, v)
        
        session.add(pkg)
        await session.commit()
        await session.refresh(pkg)
        return pkg


# ═══════════════════════════════════════════════════════════════════
# PAYMENT SERVICE
# ═══════════════════════════════════════════════════════════════════

class PaymentService:

    def __init__(self, midtrans: MidtransService):
        self.midtrans = midtrans

    async def create_payment(
        self,
        req: CreatePaymentRequest,
        session: AsyncSession,
    ) -> ServicePayment:
        booking = await BookingService().get_booking(req.booking_uuid, session)

        if req.payment_type == PaymentType.DP:
            if booking.status != BookingStatus.CONFIRMED:
                raise HTTPException(
                    400,
                    f"Booking belum dikonfirmasi admin (status: {booking.status}). "
                    "DP hanya bisa dilakukan setelah status CONFIRMED."
                )
        elif req.payment_type == PaymentType.LUNAS:
            if booking.status != BookingStatus.DONE:
                raise HTTPException(
                    400,
                    f"Pekerjaan belum selesai (status: {booking.status}). "
                    "Pelunasan hanya bisa dilakukan setelah status DONE."
                )

        existing_result = await session.exec(
            select(ServicePayment).where(
                ServicePayment.booking_uuid == req.booking_uuid,
                ServicePayment.payment_type == req.payment_type,
                ServicePayment.status       == PaymentStatus.PENDING,
            )
        )
        existing_pay = existing_result.first()
        if existing_pay and existing_pay.payment_token:
            if existing_pay.expired_at and existing_pay.expired_at > datetime.now(timezone.utc):
                return existing_pay

        amount = (
            booking.dp_amount
            if req.payment_type == PaymentType.DP
            else booking.remaining_amount
        )

        if amount <= 0:
            raise HTTPException(400, "Amount pembayaran tidak valid")

        order_id   = f"{booking.booking_number}-{req.payment_type.value}"
        type_label = (
            f"DP {booking.dp_percentage}%"
            if req.payment_type == PaymentType.DP
            else f"Pelunasan {100 - booking.dp_percentage}%"
        )

        item_details = [
            {
                "id":       booking.booking_number,
                "price":    amount,
                "quantity": 1,
                "name":     f"Jasa CCTV {booking.category.title()} — {type_label}",
                "brand":    "Padjajaran CCTV",
                "category": "Layanan CCTV",
            }
        ]

        customer = {
            "first_name": booking.contact_name,
            "phone":      booking.contact_phone,
        }

        mt_resp = await self.midtrans.create_transaction(
            order_id=order_id,
            gross_amount=amount,
            customer=customer,
            item_details=item_details,
        )

        payment = ServicePayment(
            booking_uuid  = booking.uuid,
            payment_type  = req.payment_type,
            order_id      = order_id,
            gross_amount  = amount,
            payment_token = mt_resp.get("token"),
            payment_url   = mt_resp.get("redirect_url"),
            status        = PaymentStatus.PENDING,
            expired_at    = datetime.now(timezone.utc) + timedelta(hours=24),
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)

        # 🆕 NOTIFIKASI: Pembayaran Dibuat
        if booking.user_uuid:
            await _send_service_notification(
                session=session,
                local_user_id=booking.user_uuid,
                title=f"💳 Pembayaran {type_label} Dibuat",
                content=f"Pembayaran {type_label} untuk booking #{booking.booking_number} sebesar Rp{amount:,} telah dibuat. Segera selesaikan pembayaran.",
                booking_number=booking.booking_number,
                notif_type="order",
            )

        return payment

    async def handle_service_webhook(
    self,
    payload,
    session: AsyncSession,
) -> Dict[str, str]:
        if not self.midtrans.verify_signature(
            payload.order_id,
            payload.status_code,
            payload.gross_amount,
            payload.signature_key,
        ):
            raise HTTPException(403, "Signature tidak valid")

        result = await session.exec(
            select(ServicePayment).where(ServicePayment.order_id == payload.order_id)
        )
        payment = result.first()
        if not payment:
            logger.warning(f"Service webhook: payment {payload.order_id} tidak ditemukan")
            return {"status": "ignored"}

        mt_status = payload.transaction_status
        fraud     = payload.fraud_status or "accept"

        if mt_status == "capture":
            new_status = PaymentStatus.SUCCESS if fraud == "accept" else PaymentStatus.FAILED
        elif mt_status == "settlement":
            new_status = PaymentStatus.SUCCESS
        elif mt_status in ("cancel", "deny"):
            new_status = PaymentStatus.CANCEL
        elif mt_status == "expire":
            new_status = PaymentStatus.EXPIRE
        elif mt_status == "pending":
            new_status = PaymentStatus.PENDING
        else:
            new_status = PaymentStatus.FAILED

        # Ensure new_status is always a PaymentStatus enum
        if isinstance(new_status, str):
            new_status = PaymentStatus(new_status)

        old_status = payment.status
        # Ensure old_status is also enum for comparison
        if isinstance(old_status, str):
            old_status = PaymentStatus(old_status)

        payment.status            = new_status
        payment.midtrans_status   = mt_status
        payment.payment_method    = payload.payment_type
        payment.midtrans_response = payload.model_dump()
        if new_status == PaymentStatus.SUCCESS:
            payment.paid_at = datetime.now(timezone.utc)

        if new_status == PaymentStatus.SUCCESS:
            booking_res = await session.exec(
                select(ServiceBooking).where(ServiceBooking.uuid == payment.booking_uuid)
            )
            booking = booking_res.first()
            if booking:
                if payment.payment_type == PaymentType.DP or payment.payment_type == PaymentType.DP.value:
                    booking.status = BookingStatus.DP_PAID
                elif payment.payment_type == PaymentType.LUNAS or payment.payment_type == PaymentType.LUNAS.value:
                    booking.status = BookingStatus.LUNAS
                session.add(booking)
                
                # 📝 Log Activity Payment
                await ActivityService(session).log_activity(
                    activity_type="booking",
                    title="💰 Pembayaran Jasa",
                    description=f"Pembayaran {payment.payment_type} untuk {booking.booking_number} berhasil diterima.",
                    reference_id=booking.booking_number,
                    user_id=booking.user_uuid,
                    status="settlement",
                    amount=int(payment.gross_amount),
                    icon="i-heroicons-currency-dollar",
                    color="green"
                )

        session.add(payment)
        await session.commit()

        # NOTIFIKASI: Status Pembayaran Berubah
        if old_status != new_status:
            booking_res2 = await session.exec(
                select(ServiceBooking).where(ServiceBooking.uuid == payment.booking_uuid)
            )
            booking2 = booking_res2.first()

            if booking2 and booking2.user_uuid:
                status_labels = {
                    PaymentStatus.SUCCESS: "✅ Pembayaran Berhasil",
                    PaymentStatus.FAILED:  "❌ Pembayaran Gagal",
                    PaymentStatus.CANCEL:  "❌ Pembayaran Dibatalkan",
                    PaymentStatus.EXPIRE:  "⏰ Pembayaran Kedaluwarsa",
                    PaymentStatus.PENDING: "⏳ Menunggu Pembayaran",
                }

                # Safe .value access
                payment_type_val = (
                    payment.payment_type.value
                    if hasattr(payment.payment_type, "value")
                    else payment.payment_type
                )
                new_status_val = (
                    new_status.value
                    if hasattr(new_status, "value")
                    else new_status
                )

                title   = status_labels.get(new_status, f"Status Pembayaran: {new_status_val}")
                content = (
                    f"Pembayaran untuk booking #{booking2.booking_number} "
                    f"({payment_type_val}) statusnya: {new_status_val}."
                )

                await _send_service_notification(
                    session=session,
                    local_user_id=booking2.user_uuid,
                    title=title,
                    content=content,
                    booking_number=booking2.booking_number,
                    notif_type="order",
                )

        logger.info(f"Service webhook OK: {payload.order_id} → {new_status.value if hasattr(new_status, 'value') else new_status}")
        return {"status": "ok", "payment_status": new_status.value if hasattr(new_status, "value") else new_status}


# ═══════════════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════════════

def _fmt_rp(n: int) -> str:
    return f"Rp {n:,.0f}".replace(",", ".")