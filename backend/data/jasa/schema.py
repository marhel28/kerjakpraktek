"""
schema.py — Pydantic Schemas: Request/Response
Sistem: Padjajaran CCTV Service Booking
"""

from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .model import BookingStatus, ServiceCategory, TimeSlot, PaymentType, PaymentStatus
import re


# ══════════════════════════════════════════════════════════════════
# PRICING CONFIG
# ══════════════════════════════════════════════════════════════════

class AddonConfig(BaseModel):
    key: str
    label: str
    type: str       # "per_cam" | "flat"
    price: int
    description: Optional[str] = None
    icon: Optional[str] = None


class PricingConfigResponse(BaseModel):
    """
    Dikirim ke frontend untuk inisialisasi form.
    Berisi semua data yang dibutuhkan:
    - kategori layanan + harga dasar
    - brand yang tersedia + multiplier
    - addon yang tersedia
    - aturan transport
    - persentase DP
    - max jarak layanan
    """
    uuid: UUID
    categories: List[Dict[str, Any]]      # [{id, label, base_price, icon, desc}]
    brands: List[Dict[str, Any]]          # [{key, label, multiplier}]
    addons: List[AddonConfig]
    consultation_fee: int
    transport_per_km: int
    transport_min_fee: int
    transport_max_fee: int
    max_distance_km: float
    dp_percentage: int
    routes: List[Dict[str, Any]] = []    # [{key, label, price}]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PricingConfigCreate(BaseModel):
    base_price_per_camera: Dict[str, int]
    brand_multiplier: Dict[str, float]
    consultation_fee: int = Field(default=200_000, ge=0)
    transport_per_km: int = Field(default=5_000, ge=0)
    transport_min_fee: int = Field(default=25_000, ge=0)
    transport_max_fee: int = Field(default=300_000, ge=0)
    max_distance_km: float = Field(default=30.0, ge=1, le=500)
    addons_config: List[Dict[str, Any]] = Field(default_factory=list)
    routes_config: List[Dict[str, Any]] = Field(default_factory=list)
    dp_percentage: int = Field(default=50, ge=10, le=100)


# ══════════════════════════════════════════════════════════════════
# SERVICE PACKAGE
# ══════════════════════════════════════════════════════════════════

class PackageItemCreate(BaseModel):
    stock_uuid: UUID
    quantity: int = Field(default=1, ge=1)
    override_price: Optional[int] = Field(default=None, ge=0)
    label: Optional[str] = Field(default=None, max_length=150)
    sort_order: int = Field(default=0, ge=0)


class PackageItemResponse(BaseModel):
    uuid: UUID
    stock_uuid: UUID
    stock_title: str
    stock_slug: str
    stock_thumbnail: Optional[str]
    quantity: int
    unit_price: int
    subtotal: int
    label: Optional[str]
    sort_order: int

    class Config:
        from_attributes = True


class PackageCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    category: ServiceCategory = ServiceCategory.INSTALLATION
    camera_count: int = Field(..., ge=1, le=200)
    default_brand: str = Field(..., min_length=1, max_length=100)
    thumbnail_url: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    is_active: bool = True
    sort_order: int = 0
    items: List[PackageItemCreate] = Field(default_factory=list)

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        clean = re.sub(r'[^a-z0-9-]', '', v.lower().replace(' ', '-'))
        if not clean:
            raise ValueError("Slug tidak valid")
        return clean


class PackageResponse(BaseModel):
    uuid: UUID
    name: str
    slug: str
    description: Optional[str]
    category: str
    camera_count: int
    default_brand: str
    device_price: int
    estimated_service_price: int
    total_estimated: int           # device_price + estimated_service_price
    dp_amount: int                 # total_estimated × dp_percentage / 100
    thumbnail_url: Optional[str]
    highlights: List[str]
    items: List[PackageItemResponse]
    is_active: bool
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════
# DISTANCE CHECK
# ══════════════════════════════════════════════════════════════════

class DistanceCheckRequest(BaseModel):
    """
    Frontend kirim koordinat user (dari Geolocation API atau geocoded address).
    Backend hitung jarak dari markas Padjajaran CCTV Cimahi.
    """
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None   # untuk display


class DistanceCheckResponse(BaseModel):
    distance_km: float
    transport_fee: int
    is_within_range: bool
    max_distance_km: float
    message: str


# ══════════════════════════════════════════════════════════════════
# ESTIMATE
# ══════════════════════════════════════════════════════════════════

class EstimateRequest(BaseModel):
    category: ServiceCategory
    camera_count: int = Field(..., ge=1, le=200)
    brand: str = Field(..., min_length=1, max_length=100)
    addons: List[str] = Field(default_factory=list)
    distance_km: float = Field(..., ge=0, le=500)
    package_uuid: Optional[UUID] = None   # jika dari paket


class EstimateBreakdown(BaseModel):
    base_per_camera: int
    camera_count: int
    brand_multiplier: float
    service_price: int
    addons: List[Dict[str, Any]]
    addon_price: int
    device_price: int
    distance_km: float
    transport_per_km: int
    transport_fee: int
    dp_percentage: int
    dp_amount: int
    remaining_amount: int
    total_price: int


class EstimateResponse(BaseModel):
    device_price: int
    service_price: int
    addon_price: int
    transport_fee: int
    total_price: int
    dp_amount: int
    remaining_amount: int
    dp_percentage: int
    breakdown: EstimateBreakdown


# ══════════════════════════════════════════════════════════════════
# DRAFT WIZARD (Redis)
# ══════════════════════════════════════════════════════════════════

class DraftStep1(BaseModel):
    """Pilih paket atau konfigurasi manual."""
    category: ServiceCategory
    camera_count: int = Field(..., ge=1, le=200)
    brand: str = Field(..., min_length=1)
    addons: List[str] = Field(default_factory=list)
    package_uuid: Optional[str] = None


class DraftStep2(BaseModel):
    """Jadwal & lokasi."""
    scheduled_date: date
    time_slot: TimeSlot
    address: str = Field(..., min_length=10)
    district: Optional[str] = None
    city: str = Field(..., min_length=2)
    distance_km: float = Field(..., ge=0, le=500)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("scheduled_date")
    @classmethod
    def must_be_future(cls, v: date) -> date:
        from datetime import date as d
        if v <= d.today():
            raise ValueError("Tanggal harus minimal besok")
        return v


class DraftStep3(BaseModel):
    """Kontak."""
    contact_name: str = Field(..., min_length=2, max_length=100)
    contact_phone: str = Field(..., min_length=9, max_length=20)
    contact_notes: Optional[str] = Field(None, max_length=500)

    @field_validator("contact_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = re.sub(r'[^0-9+]', '', v)
        if not re.match(r'^(\+62|62|0)[0-9]{8,13}$', clean):
            raise ValueError("Format nomor WA tidak valid (awali 08xx atau +628xx)")
        return clean


class DraftSaveRequest(BaseModel):
    session_id: str = Field(..., min_length=16, max_length=64)
    step: int = Field(..., ge=1, le=3)
    data: Dict[str, Any]


class DraftResponse(BaseModel):
    session_id: str
    step_completed: int
    draft_data: Dict[str, Any]
    estimate: Optional[EstimateResponse] = None
    expires_in: int


# ══════════════════════════════════════════════════════════════════
# BOOKING
# ══════════════════════════════════════════════════════════════════

class BookingSubmitRequest(BaseModel):
    session_id: str = Field(..., min_length=16, max_length=64)

    class Config:
        extra = "forbid"   # cegah field harga dari frontend


class BookingCreateDirect(BaseModel):
    """Booking langsung tanpa wizard (mobile app / integrasi)."""
    category: ServiceCategory
    camera_count: int = Field(..., ge=1, le=200)
    brand: str = Field(..., min_length=1, max_length=100)
    addons: List[str] = Field(default_factory=list)
    package_uuid: Optional[UUID] = None
    scheduled_date: date
    time_slot: TimeSlot
    address: str = Field(..., min_length=10)
    district: Optional[str] = None
    city: str = Field(..., min_length=2)
    distance_km: float = Field(..., ge=0, le=500)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_name: str = Field(..., min_length=2, max_length=100)
    contact_phone: str = Field(..., min_length=9, max_length=20)
    contact_notes: Optional[str] = Field(None, max_length=500)

    @field_validator("scheduled_date")
    @classmethod
    def must_be_future(cls, v: date) -> date:
        from datetime import date as d
        if v <= d.today():
            raise ValueError("Tanggal harus minimal besok")
        return v

    class Config:
        extra = "forbid"


class BookingPaymentInfo(BaseModel):
    uuid: UUID
    order_id: str
    payment_type: str
    gross_amount: int
    payment_token: Optional[str]
    payment_url: Optional[str]
    status: str


class TechnicianResponse(BaseModel):
    uuid: UUID
    name: str
    id_employee: str
    phone: Optional[str] = None
    picture_url: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class BookingBrief(BaseModel):
    uuid: UUID
    booking_number: str
    scheduled_date: date
    time_slot: str
    status: str
    contact_name: str
    address: str

    class Config:
        from_attributes = True


class TechnicianDetailResponse(TechnicianResponse):
    bookings: List[BookingBrief] = []


class BookingResponse(BaseModel):
    uuid: UUID
    booking_number: str
    category: str
    camera_count: int
    brand: str
    addons: List[str]
    scheduled_date: date
    time_slot: str
    address: str
    city: str
    distance_km: float
    contact_name: str
    contact_phone: str

    # Technician
    technician: Optional[TechnicianResponse] = None

    # Pricing
    device_price: int
    service_price: int
    addon_price: int
    transport_fee: int
    total_price: int
    dp_percentage: int
    dp_amount: int
    remaining_amount: int
    price_breakdown: Dict[str, Any]

    status: str
    payments: List[BookingPaymentInfo] = []
    created_at: datetime

    class Config:
        from_attributes = True


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    notes: Optional[str] = None
    technician_uuid: Optional[UUID] = None


# ══════════════════════════════════════════════════════════════════
# TECHNICIAN
# ══════════════════════════════════════════════════════════════════

class TechnicianCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    id_employee: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    picture_url: Optional[str] = None
    is_active: bool = True


# ══════════════════════════════════════════════════════════════════
# HOLIDAY & OPERATIONAL
# ══════════════════════════════════════════════════════════════════

class HolidayCreate(BaseModel):
    holiday_date: date
    description: Optional[str] = None


class HolidayResponse(BaseModel):
    uuid: UUID
    holiday_date: date
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OperationalHoursCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    is_open: bool = True
    hours: str = Field(default="08:00-17:00")
    max_bookings: int = Field(default=9)


class OperationalHoursResponse(BaseModel):
    uuid: UUID
    day_of_week: int
    is_open: bool
    hours: str
    max_bookings: int

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════
# PAYMENT
# ══════════════════════════════════════════════════════════════════

class CreatePaymentRequest(BaseModel):
    """Frontend minta token Midtrans untuk DP atau Pelunasan."""
    booking_uuid: UUID
    payment_type: PaymentType

    class Config:
        extra = "forbid"


class MidtransWebhookPayload(BaseModel):
    """Notifikasi dari Midtrans (server-to-server)."""
    transaction_status: str
    order_id: str
    gross_amount: str
    payment_type: str
    transaction_id: str
    signature_key: str
    status_code: str
    fraud_status: Optional[str] = None
    transaction_time: Optional[str] = None

    class Config:
        extra = "allow"   # Midtrans bisa kirim field tambahan


# ══════════════════════════════════════════════════════════════════
# SLOT
# ══════════════════════════════════════════════════════════════════

class SlotInfo(BaseModel):
    slot: str
    label: str
    available: bool
    remaining: int
    booked: int


class AvailableSlotsResponse(BaseModel):
    date: date
    slots: List[SlotInfo]
    message: Optional[str] = None