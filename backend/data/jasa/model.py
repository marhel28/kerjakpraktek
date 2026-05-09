"""
model.py — CCTV Service Booking Models
Sistem: Padjajaran CCTV, Cimahi
"""

from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import func, Index, text, ForeignKey, UniqueConstraint
from enum import Enum


# ══════════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════════

class BookingStatus(str, Enum):
    PENDING    = "pending"     # submitted, menunggu konfirmasi admin
    CONFIRMED  = "confirmed"   # admin konfirmasi, menunggu DP
    DP_PAID    = "dp_paid"     # DP 50% sudah dibayar → jadwalkan teknisi
    PROGRESS   = "progress"    # teknisi sedang di lokasi
    DONE       = "done"        # pekerjaan selesai, menunggu pelunasan
    LUNAS      = "lunas"       # bayar lunas (sisa 50%)
    CANCEL     = "cancel"      # dibatalkan

class ServiceCategory(str, Enum):
    INSTALLATION   = "installation"    # Pemasangan baru
    MAINTENANCE    = "maintenance"     # Servis / perbaikan
    CONSULTATION   = "consultation"    # Konsultasi + survey
    TROUBLESHOOT   = "troubleshoot"    # Diagnosa masalah

class TimeSlot(str, Enum):
    MORNING   = "08:00-11:00"
    MIDDAY    = "11:00-14:00"
    AFTERNOON = "14:00-17:00"

class PaymentType(str, Enum):
    DP      = "dp"      # Bayar 50% di awal
    LUNAS   = "lunas"   # Bayar sisa 50% setelah selesai

class PaymentStatus(str, Enum):
    PENDING  = "pending"
    SUCCESS  = "success"
    FAILED   = "failed"
    EXPIRE   = "expire"
    CANCEL   = "cancel"


# ══════════════════════════════════════════════════════════════════
# PRICING CONFIG — Admin-managed, Redis-cached
# ══════════════════════════════════════════════════════════════════

class ServicePricingConfig(SQLModel, table=True):
    """
    Satu baris aktif = satu versi pricing.
    Append-only (audit trail). Cache Redis 1 jam.

    base_price_per_camera: {"installation": 150000, "maintenance": 75000, ...}
    brand_multiplier: {"hikvision": 1.0, "dahua": 1.0, "axis": 1.3, ...}
    addons_config: [{"key": "conduit", "label": "Conduit Kabel", "type": "per_cam", "price": 25000}, ...]
    consultation_fee: biaya flat konsultasi/survey
    """
    __tablename__ = "service_pricing_config"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    base_price_per_camera: Dict[str, int] = Field(
        sa_column=Column(pg.JSONB, nullable=False)
    )
    brand_multiplier: Dict[str, float] = Field(
        sa_column=Column(pg.JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    )
    consultation_fee: int = Field(default=200_000)  # flat fee untuk konsultasi
    transport_per_km: int = Field(default=5_000)
    transport_min_fee: int = Field(default=25_000)
    transport_max_fee: int = Field(default=300_000)
    max_distance_km: float = Field(default=30.0)     # batas layanan dari Cimahi
    addons_config: List[Dict[str, Any]] = Field(
        sa_column=Column(pg.JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    )
    dp_percentage: int = Field(default=50)           # persentase DP (default 50%)
    is_active: bool = Field(
        default=True,
        sa_column=Column(pg.BOOLEAN, index=True)
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    )


# ══════════════════════════════════════════════════════════════════
# SERVICE PACKAGE — Bundle kamera yang bisa dipesan sebagai paket
# ══════════════════════════════════════════════════════════════════

class ServicePackage(SQLModel, table=True):
    """
    Paket layanan CCTV: misal 'Paket Rumah 4 Kamera Hikvision'.
    Berisi daftar item Stock (kamera, DVR, kabel, dll).
    Harga paket = harga perangkat + estimasi jasa pemasangan.

    Berbeda dari BundleLink (yang hanya mengatur relasi antar Stock),
    ServicePackage adalah produk komersial siap pesan.
    """
    __tablename__ = "service_package"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR(200), nullable=False))
    slug: str = Field(sa_column=Column(pg.VARCHAR(200), unique=True, nullable=False, index=True))
    description: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    category: ServiceCategory = Field(
        default=ServiceCategory.INSTALLATION,
        sa_column=Column(pg.VARCHAR(30), nullable=False, index=True)
    )

    # Snapshot kamera: berapa unit & brand default
    camera_count: int = Field(default=1)
    default_brand: str = Field(default="hikvision", sa_column=Column(pg.VARCHAR(100)))

    # Harga perangkat (dari bundle Stock) — dihitung otomatis oleh BundleService
    device_price: int = Field(default=0)

    # Harga estimasi jasa (dihitung dari pricing config × camera_count × multiplier)
    # Disimpan sebagai snapshot untuk display; recalc saat booking
    estimated_service_price: int = Field(default=0)

    # Gambar thumbnail (pakai asset dari Stock pertama atau upload sendiri)
    thumbnail_url: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))

    # Tags / fitur highlight (JSON array of string)
    highlights: List[str] = Field(
        default_factory=list,
        sa_column=Column(pg.JSONB, server_default=text("'[]'::jsonb"))
    )

    is_active: bool = Field(default=True, sa_column=Column(pg.BOOLEAN, index=True))
    sort_order: int = Field(default=0)

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    )


class ServicePackageItem(SQLModel, table=True):
    """
    Item-item Stock dalam satu ServicePackage.
    Misal: 4x Kamera Hikvision DS-2CD2143G2, 1x DVR 4CH, 50m Kabel Coaxial.
    """
    __tablename__ = "service_package_item"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    package_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("service_package.uuid", ondelete="CASCADE"),
            index=True,
            nullable=False,
        )
    )
    stock_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("stock.uuid", ondelete="RESTRICT"),
            index=True,
            nullable=False,
        )
    )
    quantity: int = Field(default=1)
    override_price: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )  # null = pakai stock.online_price
    label: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(150), nullable=True)
    )  # "Kamera Utama", "DVR", "Kabel", dll.
    sort_order: int = Field(default=0)

    __table_args__ = (
        Index("idx_spi_package", "package_uuid"),
        Index("idx_spi_stock", "stock_uuid"),
    )


# ══════════════════════════════════════════════════════════════════
# SERVICE BOOKING
# ══════════════════════════════════════════════════════════════════

class ServiceBooking(SQLModel, table=True):
    __tablename__ = "service_booking"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    booking_number: str = Field(
        sa_column=Column(pg.VARCHAR(30), unique=True, nullable=False, index=True)
    )  # Format: BK-YYYYMMDD-XXXXXX

    # ── Relasi ────────────────────────────────────────────────────
    user_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("user.uuid", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )
    )
    # Jika dari paket → simpan UUID paket
    package_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("service_package.uuid", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )
    )
    pricing_config_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("service_pricing_config.uuid"),
            nullable=True,
        )
    )

    # ── Konfigurasi Layanan ───────────────────────────────────────
    category: ServiceCategory = Field(
        sa_column=Column(pg.VARCHAR(30), nullable=False, index=True)
    )
    camera_count: int = Field(default=1, sa_column=Column(pg.INTEGER, nullable=False))
    brand: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False))
    addons: List[str] = Field(
        default_factory=list,
        sa_column=Column(pg.JSONB, server_default=text("'[]'::jsonb"))
    )
    # Snapshot spesifikasi dari paket (untuk invoice)
    package_snapshot: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(pg.JSONB, nullable=True)
    )

    # ── Jadwal ────────────────────────────────────────────────────
    scheduled_date: date = Field(
        sa_column=Column(pg.DATE, nullable=False, index=True)
    )
    time_slot: TimeSlot = Field(
        sa_column=Column(pg.VARCHAR(20), nullable=False)
    )

    # ── Lokasi ────────────────────────────────────────────────────
    address: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    district: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(100)))
    city: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False))
    distance_km: float = Field(default=0.0, sa_column=Column(pg.FLOAT, nullable=False))
    latitude: Optional[float] = Field(default=None, sa_column=Column(pg.FLOAT, nullable=True))
    longitude: Optional[float] = Field(default=None, sa_column=Column(pg.FLOAT, nullable=True))

    # ── Kontak ────────────────────────────────────────────────────
    contact_name: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False))
    contact_phone: str = Field(sa_column=Column(pg.VARCHAR(20), nullable=False))
    contact_notes: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))

    # ── Pricing Snapshot (IMMUTABLE setelah submit) ───────────────
    device_price: int = Field(default=0)       # harga perangkat dari paket
    service_price: int = Field(default=0)      # harga jasa
    addon_price: int = Field(default=0)        # harga addon
    transport_fee: int = Field(default=0)      # biaya transportasi
    total_price: int = Field(default=0, sa_column=Column(pg.INTEGER, nullable=False, index=True))

    # ── Pembayaran DP ─────────────────────────────────────────────
    dp_percentage: int = Field(default=50)
    dp_amount: int = Field(default=0)          # total_price × dp_percentage / 100
    remaining_amount: int = Field(default=0)   # total_price − dp_amount

    price_breakdown: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(pg.JSONB, server_default=text("'{}'::jsonb"))
    )

    # ── Status ────────────────────────────────────────────────────
    status: BookingStatus = Field(
        default=BookingStatus.PENDING,
        sa_column=Column(pg.VARCHAR(20), nullable=False, index=True)
    )

    # ── Anti double-booking ───────────────────────────────────────
    slot_lock_key: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(150), nullable=True, index=True)
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    __table_args__ = (
        Index("idx_booking_status_date", "status", "scheduled_date"),
        Index("idx_booking_slot",        "scheduled_date", "time_slot", "status"),
        Index("idx_booking_user",        "user_uuid"),
    )


# ══════════════════════════════════════════════════════════════════
# PAYMENT — Midtrans transactions (DP & Lunas)
# ══════════════════════════════════════════════════════════════════

class ServicePayment(SQLModel, table=True):
    """
    Satu booking bisa punya 2 payment: DP dan Pelunasan.
    Setiap payment = satu transaksi Midtrans terpisah.
    """
    __tablename__ = "service_payment"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    booking_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("service_booking.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    payment_type: PaymentType = Field(
        sa_column=Column(pg.VARCHAR(10), nullable=False)
    )  # "dp" atau "lunas"

    # Midtrans
    order_id: str = Field(
        sa_column=Column(pg.VARCHAR(100), unique=True, nullable=False, index=True)
    )  # Format: BK-YYYYMMDD-XXXXXX-dp / -lunas
    gross_amount: int = Field(nullable=False)
    payment_token: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    payment_url: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    midtrans_status: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(50)))
    midtrans_response: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(pg.JSONB, nullable=True)
    )
    payment_method: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(50)))

    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        sa_column=Column(pg.VARCHAR(20), nullable=False, index=True)
    )
    paid_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True)
    )
    expired_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True)
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )

    __table_args__ = (
        Index("idx_payment_booking", "booking_uuid"),
        Index("idx_payment_order",   "order_id"),
    )