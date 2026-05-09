"""
router.py — FastAPI Routes: Service Booking, Package, Payment
Sistem: Padjajaran CCTV, Cimahi
"""

import os
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.db.main import get_session
from backend.db.redis import get_redis_token
from backend.auth.depedence import get_current_user, get_admin
from backend.auth.model import User

from .model import (
    BookingStatus, ServiceBooking, ServicePayment,
    ServicePackage, ServicePricingConfig,
)
from .schema import (
    PricingConfigCreate, PricingConfigResponse,
    PackageCreate, PackageResponse,
    DistanceCheckRequest, DistanceCheckResponse,
    EstimateRequest, EstimateResponse,
    DraftSaveRequest, DraftResponse,
    BookingSubmitRequest, BookingCreateDirect, BookingResponse,
    BookingStatusUpdate, BookingPaymentInfo,
    CreatePaymentRequest, MidtransWebhookPayload,
    AvailableSlotsResponse,
)
from .service import (
    BookingService, PackageService, PaymentService, MidtransService,
)
from backend.config import Config
router = APIRouter()

# ── Singletons ─────────────────────────────────────────────────────
_midtrans = MidtransService(
    server_key    = os.getenv("MIDTRANS_SERVER_KEY", Config.MIDTRANS_SERVER_KEY),
    is_production = os.getenv("MIDTRANS_PRODUCTION", "false").lower() == "true",
)
booking_svc = BookingService()
package_svc = PackageService()
payment_svc = PaymentService(_midtrans)

RATE_LIMIT_MAX = 5
RATE_LIMIT_TTL = 60


# ── Rate limiter ──────────────────────────────────────────────────

async def _rate_limit(request: Request, prefix: str = "svc") -> None:
    ip  = (request.client.host if request.client else "unknown")
    r   = get_redis_token()
    key = f"rl:{prefix}:{ip}"
    cnt = await r.incr(key)
    if cnt == 1:
        await r.expire(key, RATE_LIMIT_TTL)
    if cnt > RATE_LIMIT_MAX:
        raise HTTPException(429, "Terlalu banyak permintaan. Tunggu 1 menit.")


# ── Response builder ──────────────────────────────────────────────

async def _booking_response(
    booking: ServiceBooking, session: AsyncSession
) -> BookingResponse:
    payments = await booking_svc.get_booking_payments(booking.uuid, session)
    pay_list = [
        BookingPaymentInfo(
            uuid          = p.uuid,
            order_id      = p.order_id,
            payment_type  = p.payment_type,
            gross_amount  = p.gross_amount,
            payment_token = p.payment_token,
            payment_url   = p.payment_url,
            status        = p.status,
        )
        for p in payments
    ]
    return BookingResponse(
        uuid             = booking.uuid,
        booking_number   = booking.booking_number,
        category         = booking.category,
        camera_count     = booking.camera_count,
        brand            = booking.brand,
        addons           = booking.addons,
        scheduled_date   = booking.scheduled_date,
        time_slot        = booking.time_slot,
        address          = booking.address,
        city             = booking.city,
        distance_km      = booking.distance_km,
        contact_name     = booking.contact_name,
        contact_phone    = booking.contact_phone,
        device_price     = booking.device_price,
        service_price    = booking.service_price,
        addon_price      = booking.addon_price,
        transport_fee    = booking.transport_fee,
        total_price      = booking.total_price,
        dp_percentage    = booking.dp_percentage,
        dp_amount        = booking.dp_amount,
        remaining_amount = booking.remaining_amount,
        price_breakdown  = booking.price_breakdown,
        status           = booking.status,
        payments         = pay_list,
        created_at       = booking.created_at,
    )


# ══════════════════════════════════════════════════════════════════
# PUBLIC — Config & Packages
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/services/config",
    response_model=PricingConfigResponse,
    tags=["Public Services"],
    summary="Konfigurasi layanan (harga, brand, addon, DP%)",
)
async def get_service_config(session: AsyncSession = Depends(get_session)):
    """
    Endpoint utama untuk inisialisasi form booking.
    Di-cache Redis 1 jam.
    Berisi: kategori + harga dasar, daftar brand + multiplier,
    addon yang tersedia, aturan transport, persentase DP, max jarak.
    """
    config = await booking_svc.get_active_pricing_config(session)
    return booking_svc.build_pricing_response(config)


@router.get(
    "/services/packages",
    response_model=List[PackageResponse],
    tags=["Public Services"],
    summary="Daftar paket CCTV siap pesan",
)
async def list_packages(
    category: Optional[str] = Query(None, description="Filter kategori layanan"),
    session: AsyncSession    = Depends(get_session),
):
    """
    Daftar paket CCTV (bundle kamera + estimasi jasa).
    Digunakan di halaman beranda / halaman produk.
    """
    config   = await booking_svc.get_active_pricing_config(session)
    packages = await package_svc.list_packages(session, category=category)
    return [await package_svc.build_package_response(p, session, config) for p in packages]

@router.get(
    "/services/payment/status/{booking_uuid}",
    tags=["Payment"],
    summary="Cek status payment terkini untuk booking",
)
async def get_payment_status(
    booking_uuid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Frontend poll endpoint ini setelah user selesai bayar di Midtrans Snap.
    Return semua payment record + status booking terkini.
    """
    booking  = await booking_svc.get_booking(booking_uuid, session)
    payments = await booking_svc.get_booking_payments(booking_uuid, session)

    return {
        "booking_uuid":   str(booking_uuid),
        "booking_status": booking.status,
        "payments": [
            {
                "uuid":          str(p.uuid),
                "order_id":      p.order_id,
                "payment_type":  p.payment_type,
                "gross_amount":  p.gross_amount,
                "payment_token": p.payment_token,
                "payment_url":   p.payment_url,
                "status":        p.status,
                "paid_at":       p.paid_at,
                "expired_at":    p.expired_at,
            }
            for p in payments
        ],
    }
    
    
@router.get(
    "/services/packages/{pkg_uuid}",
    response_model=PackageResponse,
    tags=["Public Services"],
    summary="Detail paket + breakdown harga",
)
async def get_package(
    pkg_uuid: UUID,
    session: AsyncSession = Depends(get_session),
):
    config = await booking_svc.get_active_pricing_config(session)
    pkg    = await package_svc.get_package(pkg_uuid, session)
    return await package_svc.build_package_response(pkg, session, config)


@router.get(
    "/services/packages/slug/{slug}",
    response_model=PackageResponse,
    tags=["Public Services"],
    summary="Detail paket by slug (SEO-friendly)",
)
async def get_package_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
):
    from sqlmodel import select
    result = await session.exec(select(ServicePackage).where(ServicePackage.slug == slug))
    pkg    = result.first()
    if not pkg:
        raise HTTPException(404, "Paket tidak ditemukan")
    config = await booking_svc.get_active_pricing_config(session)
    return await package_svc.build_package_response(pkg, session, config)


# ══════════════════════════════════════════════════════════════════
# PUBLIC — Distance & Estimate
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/services/distance",
    response_model=DistanceCheckResponse,
    tags=["Public Services"],
    summary="Cek jarak dari Cimahi + estimasi ongkir",
)
async def check_distance(
    req: DistanceCheckRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Hitung jarak haversine dari markas Padjajaran CCTV (Cimahi)
    ke koordinat user. Validasi max jarak layanan.
    Frontend kirim lat/lon dari Geolocation API atau hasil geocoding.
    """
    await _rate_limit(request, "distance")
    return await booking_svc.check_distance(req, session)


@router.post(
    "/services/estimate",
    response_model=EstimateResponse,
    tags=["Public Services"],
    summary="Estimasi harga real-time (no DB write)",
)
async def estimate_price(
    req: EstimateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Kalkulasi harga instan tanpa menyimpan data.
    Rate-limited: 5 request/menit per IP.
    Berisi: harga jasa, addon, transport, total, DP & sisa.
    """
    await _rate_limit(request, "estimate")
    return await booking_svc.estimate(req, session)


# ══════════════════════════════════════════════════════════════════
# PUBLIC — Slot Availability
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/services/slots",
    response_model=AvailableSlotsResponse,
    tags=["Public Services"],
    summary="Cek slot tersedia untuk tanggal tertentu",
)
async def available_slots(
    target_date: date = Query(..., description="Format YYYY-MM-DD"),
    session: AsyncSession = Depends(get_session),
):
    """
    Cek sisa slot per time slot untuk satu tanggal.
    Frontend pakai ini untuk disable slot yang sudah penuh di date picker.
    Max 3 booking per slot.
    """
    return await booking_svc.get_available_slots(target_date, session)


# ══════════════════════════════════════════════════════════════════
# BOOKING — Draft Wizard
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/services/booking/draft",
    response_model=DraftResponse,
    tags=["Booking"],
    summary="Simpan step wizard ke Redis draft (TTL 30 menit)",
)
async def save_draft(
    req: DraftSaveRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Frontend panggil setiap berpindah step.
    Draft di-merge (bukan replace), jadi aman untuk partial update.
    Jika step 1 & 2 sudah ada, estimasi dihitung otomatis.
    Session ID: generate di frontend (UUID v4 / random 32 char).
    """
    await _rate_limit(request, "draft")
    result = await booking_svc.save_draft_step(
        session_id=req.session_id,
        step=req.step,
        data=req.data,
        session=session,
    )
    return DraftResponse(**result)


@router.get(
    "/services/booking/draft/{session_id}",
    tags=["Booking"],
    summary="Ambil draft tersimpan (restore wizard saat reload)",
)
async def get_draft(session_id: str):
    draft = await booking_svc.get_draft(session_id)
    if not draft:
        raise HTTPException(404, "Draft tidak ditemukan atau sudah expired")
    return {"status": "ok", "data": draft}


@router.post(
    "/services/booking/submit",
    response_model=BookingResponse,
    tags=["Booking"],
    summary="Submit booking dari draft (harga dihitung ulang di backend)",
)
async def submit_booking(
    req: BookingSubmitRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Submit final dari draft wizard.
    Backend SELALU hitung ulang harga — frontend tidak bisa inject harga.
    Anti double-booking via Redis SETNX (atomic).
    Max 3 booking per slot.
    Validasi max jarak layanan.
    """
    await _rate_limit(request, "submit")
    booking = await booking_svc.submit_from_draft(
        session_id=req.session_id,
        session=session,
        user_uuid=current_user.uuid if current_user else None,
    )
    return await _booking_response(booking, session)


@router.post(
    "/services/booking/direct",
    response_model=BookingResponse,
    tags=["Booking"],
    summary="Booking langsung (tanpa wizard, untuk mobile/integrasi)",
)
async def create_booking_direct(
    req: BookingCreateDirect,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user),
):
    await _rate_limit(request, "submit")

    config = await booking_svc.get_active_pricing_config(session)
    if req.distance_km > config.max_distance_km:
        raise HTTPException(400, f"Jarak melebihi batas layanan {config.max_distance_km:.0f} km")

    if await booking_svc._count_active_slot(session, req.scheduled_date, req.time_slot) >= 3:
        raise HTTPException(409, "Slot sudah penuh")

    acquired, lock_key = await booking_svc._acquire_slot_lock(req.scheduled_date, req.time_slot)
    if not acquired:
        raise HTTPException(409, "Slot sedang diproses. Coba lagi.")

    try:
        device_price = 0
        if req.package_uuid:
            from sqlmodel import select
            pkg_res = await session.exec(
                select(ServicePackage).where(ServicePackage.uuid == req.package_uuid)
            )
            pkg = pkg_res.first()
            if pkg:
                device_price = pkg.device_price

        pricing = _price_engine(config, req, device_price)

        from .service import BookingService as BS
        booking = ServiceBooking(
            user_uuid         = current_user.uuid if current_user else None,
            package_uuid      = req.package_uuid,
            pricing_config_uuid = config.uuid,
            booking_number    = BookingService._gen_booking_number(BS),
            category          = req.category,
            camera_count      = req.camera_count,
            brand             = req.brand,
            addons            = req.addons,
            scheduled_date    = req.scheduled_date,
            time_slot         = req.time_slot,
            address           = req.address,
            district          = req.district,
            city              = req.city,
            distance_km       = req.distance_km,
            latitude          = req.latitude,
            longitude         = req.longitude,
            contact_name      = req.contact_name,
            contact_phone     = req.contact_phone,
            contact_notes     = req.contact_notes,
            **{k: pricing[k] for k in [
                "device_price","service_price","addon_price","transport_fee",
                "total_price","dp_percentage","dp_amount","remaining_amount",
            ]},
            price_breakdown   = pricing["breakdown"].model_dump(),
            status            = BookingStatus.PENDING,
            slot_lock_key     = lock_key,
        )
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        return await _booking_response(booking, session)

    except HTTPException:
        await booking_svc._release_slot_lock(lock_key)
        raise
    except Exception as e:
        await booking_svc._release_slot_lock(lock_key)
        await session.rollback()
        raise HTTPException(500, f"Gagal membuat booking: {e}")


def _price_engine(config, req, device_price: int):
    from .service import PricingEngine
    return PricingEngine.calculate(
        config=config,
        category=req.category,
        camera_count=req.camera_count,
        brand=req.brand,
        addons=req.addons,
        distance_km=req.distance_km,
        device_price=device_price,
    )


# ══════════════════════════════════════════════════════════════════
# BOOKING — Lookup
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/services/booking/{booking_uuid}",
    response_model=BookingResponse,
    tags=["Booking"],
    summary="Cek status booking by UUID",
)
async def get_booking(
    booking_uuid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """UUID cukup aman sebagai secret URL (128-bit random)."""
    booking = await booking_svc.get_booking(booking_uuid, session)
    return await _booking_response(booking, session)


@router.get(
    "/services/booking/number/{booking_number}",
    response_model=BookingResponse,
    tags=["Booking"],
    summary="Cek status booking by nomor (BK-YYYYMMDD-XXXXXX)",
)
async def get_booking_by_number(
    booking_number: str,
    session: AsyncSession = Depends(get_session),
):
    booking = await booking_svc.get_booking_by_number(booking_number, session)
    return await _booking_response(booking, session)


# ══════════════════════════════════════════════════════════════════
# PAYMENT
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/services/payment/create",
    tags=["Payment"],
    summary="Buat transaksi Midtrans Snap (DP atau Pelunasan)",
)
async def create_payment(
    req: CreatePaymentRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    # current_user: Optional[User] = Depends(get_current_user),
):
    """
    Validasi state booking, hitung amount DP/Pelunasan,
    buat transaksi Midtrans Snap, simpan ke DB.
    Mengembalikan payment_token untuk Midtrans Snap.js di frontend.

    Flow DP:   booking CONFIRMED → bayar dp_amount (50%) → status DP_PAID → jadwalkan teknisi
    Flow Lunas: booking DONE → bayar remaining_amount (50%) → status LUNAS
    """
    await _rate_limit(request, "payment")
    payment = await payment_svc.create_payment(req, session)
    return {
        "status":        "ok",
        "order_id":      payment.order_id,
        "payment_token": payment.payment_token,
        "payment_url":   payment.payment_url,
        "gross_amount":  payment.gross_amount,
        "payment_type":  payment.payment_type,
        "expired_at":    payment.expired_at,
    }


@router.post(
    "/services/payment/webhook",
    tags=["Payment"],
    summary="Midtrans webhook notification (server-to-server)",
    include_in_schema=False,  # sembunyikan dari Swagger publik
)
async def midtrans_webhook(
    payload: MidtransWebhookPayload,
    session: AsyncSession = Depends(get_session),
):
    """
    Menerima notifikasi dari server Midtrans.
    Verifikasi signature SHA512 sebelum update status.
    Update status payment & booking secara otomatis.
    """
    return await payment_svc.handle_service_webhook(payload, session)


# ══════════════════════════════════════════════════════════════════
# ADMIN — Booking Management
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/admin/service/bookings",
    tags=["Admin Booking"],
    summary="Daftar semua booking (paginated)",
)
async def admin_list_bookings(
    status:    Optional[BookingStatus] = Query(None),
    date_from: Optional[date]          = Query(None),
    date_to:   Optional[date]          = Query(None),
    page: int  = Query(1, ge=1),
    size: int  = Query(20, le=100),
    session: AsyncSession = Depends(get_session),
    _: User   = Depends(get_admin),
):
    result = await booking_svc.list_bookings(
        session, status=status, date_from=date_from, date_to=date_to, page=page, size=size
    )
    items = [await _booking_response(b, session) for b in result["items"]]
    return {"status": "ok", "total": result["total"], "page": page, "size": size, "items": items}


@router.patch(
    "/admin/service/bookings/{booking_uuid}/status",
    response_model=BookingResponse,
    tags=["Admin Booking"],
    summary="Update status booking (state machine validated)",
)
async def admin_update_status(
    booking_uuid: UUID,
    body: BookingStatusUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    """
    Validasi transisi status:
    PENDING → CONFIRMED / CANCEL
    CONFIRMED → DP_PAID / CANCEL   (setelah admin verifikasi DP di Midtrans)
    DP_PAID → PROGRESS / CANCEL
    PROGRESS → DONE
    DONE → LUNAS
    """
    booking = await booking_svc.update_status(booking_uuid, body.status, session, body.notes)
    return await _booking_response(booking, session)


@router.get(
    "/admin/service/stats",
    tags=["Admin Booking"],
    summary="Dashboard statistik booking & revenue",
)
async def admin_stats(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    stats = await booking_svc.get_stats(session)
    return {"status": "ok", "data": stats}


# ══════════════════════════════════════════════════════════════════
# ADMIN — Package Management
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/admin/service/packages",
    response_model=PackageResponse,
    tags=["Admin Package"],
    summary="Buat paket CCTV baru beserta item Stock",
)
async def admin_create_package(
    data: PackageCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    """
    Buat paket baru. item = list Stock UUID dengan quantity & harga override opsional.
    device_price dihitung otomatis dari item.
    """
    pkg    = await package_svc.create_package(data, session)
    config = await booking_svc.get_active_pricing_config(session)
    return await package_svc.build_package_response(pkg, session, config)


@router.get(
    "/admin/service/packages",
    response_model=List[PackageResponse],
    tags=["Admin Package"],
    summary="Daftar semua paket (termasuk non-aktif)",
)
async def admin_list_packages(
    category: Optional[str] = Query(None),
    session: AsyncSession    = Depends(get_session),
    _: User = Depends(get_admin),
):
    config   = await booking_svc.get_active_pricing_config(session)
    packages = await package_svc.list_packages(session, category=category, active_only=False)
    return [await package_svc.build_package_response(p, session, config) for p in packages]


@router.patch(
    "/admin/service/packages/{pkg_uuid}",
    response_model=PackageResponse,
    tags=["Admin Package"],
    summary="Update metadata paket (name, desc, is_active, dll)",
)
async def admin_update_package(
    pkg_uuid: UUID,
    updates: dict,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    pkg = await package_svc.get_package(pkg_uuid, session)
    allowed = {"name","description","thumbnail_url","highlights","is_active","sort_order","estimated_service_price"}
    for k, v in updates.items():
        if k in allowed:
            setattr(pkg, k, v)
    session.add(pkg)
    await session.commit()
    await session.refresh(pkg)
    config = await booking_svc.get_active_pricing_config(session)
    return await package_svc.build_package_response(pkg, session, config)


@router.post(
    "/admin/service/packages/{pkg_uuid}/recalculate",
    response_model=PackageResponse,
    tags=["Admin Package"],
    summary="Recalculate device_price dari item terkini",
)
async def admin_recalculate_package(
    pkg_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    pkg    = await package_svc.recalculate_device_price(pkg_uuid, session)
    config = await booking_svc.get_active_pricing_config(session)
    return await package_svc.build_package_response(pkg, session, config)


# ══════════════════════════════════════════════════════════════════
# ADMIN — Pricing Config
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/admin/service/pricing",
    response_model=PricingConfigResponse,
    tags=["Admin Pricing"],
    summary="Buat versi pricing config baru (append-only, cache invalidated)",
)
async def admin_create_pricing(
    data: PricingConfigCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    """
    Versi lama TIDAK dihapus (audit trail).
    Cache Redis diinvalidate otomatis.
    """
    from sqlmodel import select

    # Nonaktifkan semua config lama
    old_res = await session.exec(
        select(ServicePricingConfig).where(ServicePricingConfig.is_active == True)
    )
    for old in old_res.all():
        old.is_active = False
        session.add(old)

    new_cfg = ServicePricingConfig(**data.model_dump())
    session.add(new_cfg)
    await session.commit()
    await session.refresh(new_cfg)

    await booking_svc.invalidate_pricing_cache()
    return booking_svc.build_pricing_response(new_cfg)


@router.get(
    "/admin/service/pricing/active",
    response_model=PricingConfigResponse,
    tags=["Admin Pricing"],
    summary="Lihat pricing config aktif saat ini",
)
async def admin_get_pricing(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_admin),
):
    config = await booking_svc.get_active_pricing_config(session)
    return booking_svc.build_pricing_response(config)

from .service import _send_service_notification

# user manager
@router.post("/test-notification")
async def test_notification(
    user: User = Depends(get_current_user),
    tags=["Booking"],
    session: AsyncSession = Depends(get_session)
):
    await _send_service_notification(
        session=session,
        local_user_id=user.uuid,
        title="Test Notification",
        content="Ini test dari backend",
        booking_number="TEST-123",
        notif_type="system"
    )
    return {"message": "Notification sent (check logs)"}