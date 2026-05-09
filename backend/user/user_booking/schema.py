"""
schema.py — User Booking Dashboard Schemas
"""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class BookingSortBy(str, Enum):
    NEWEST      = "newest"
    OLDEST      = "oldest"
    SCHEDULED   = "scheduled"
    TOTAL_HIGH  = "total_high"
    TOTAL_LOW   = "total_low"


class BookingFilterStatus(str, Enum):
    ALL         = "all"
    PENDING     = "pending"
    CONFIRMED   = "confirmed"
    DP_PAID     = "dp_paid"
    PROGRESS    = "progress"
    DONE        = "done"
    LUNAS       = "lunas"
    CANCEL      = "cancel"


# ── Payment summary ────────────────────────────────────────────────
class PaymentSummary(BaseModel):
    uuid: UUID
    order_id: str
    payment_type: str        # "dp" | "lunas"
    gross_amount: int
    status: str              # "pending" | "success" | "failed" | "expire" | "cancel"
    payment_token: Optional[str] = None
    payment_url: Optional[str] = None   # link langsung ke Midtrans
    paid_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    created_at: datetime


# ── Action yang bisa dilakukan user saat ini ───────────────────────
class BookingAction(BaseModel):
    action: str          # "pay_dp" | "pay_lunas" | "view_receipt" | "none"
    label: str
    amount: Optional[int] = None
    payment_url: Optional[str] = None   # diisi jika payment sudah ada & pending
    booking_uuid: Optional[UUID] = None


# ── Booking card (list view) ───────────────────────────────────────
class BookingCard(BaseModel):
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
    status: str
    status_label: str
    status_color: str        # "amber" | "blue" | "green" | "purple" | "red" | "gray"
    total_price: int
    dp_amount: int
    remaining_amount: int
    dp_percentage: int
    action: BookingAction    # CTA utama yang bisa dilakukan sekarang
    has_pending_payment: bool
    created_at: datetime
    scheduled_label: str     # "Besok", "2 hari lagi", "28 Apr 2026"


# ── Booking detail (full) ──────────────────────────────────────────
class BookingDetail(BaseModel):
    uuid: UUID
    booking_number: str
    category: str
    camera_count: int
    brand: str
    addons: List[str]
    scheduled_date: date
    time_slot: str
    address: str
    district: Optional[str]
    city: str
    distance_km: float
    contact_name: str
    contact_phone: str
    contact_notes: Optional[str]
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
    status_label: str
    status_color: str
    action: BookingAction
    payments: List[PaymentSummary]
    created_at: datetime
    updated_at: datetime


# ── Pagination ─────────────────────────────────────────────────────
class PaginatedBookings(BaseModel):
    items: List[BookingCard]
    total: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ── Stats ringkas di atas dashboard ───────────────────────────────
class UserBookingStats(BaseModel):
    total: int
    active: int          # pending + confirmed + dp_paid + progress
    done: int            # lunas
    cancel: int
    total_spent: int     # sum semua payment SUCCESS
    pending_payment: int # total tagihan yang belum dibayar (dp + lunas)


# ── Dashboard response (stats + list) ─────────────────────────────
class UserDashboardResponse(BaseModel):
    stats: UserBookingStats
    bookings: PaginatedBookings