"""
model.py — Promo / Discount Campaign Models
Sistem: Padjajaran CCTV, Cimahi

Mendukung promo untuk:
  - Stock (produk)
  - ServicePackage (paket jasa)
  - Kombinasi keduanya

Tipe promo:
  - PERCENTAGE   : diskon % dari harga asli
  - FIXED        : potongan harga tetap (Rp)
  - BOGO         : buy X get Y (misal beli 2 gratis 1)
  - BUNDLE_DISC  : diskon kalau beli paket tertentu
  - FLASH_SALE   : limited time + limited quota flash sale
"""

from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import func, Index, text, ForeignKey, UniqueConstraint, desc
from enum import Enum


# ══════════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════════

class PromoType(str, Enum):
    PERCENTAGE  = "percentage"    # diskon persentase
    FIXED       = "fixed"         # potongan harga tetap
    BOGO        = "bogo"          # buy X get Y
    BUNDLE_DISC = "bundle_disc"   # diskon khusus untuk bundle/paket
    FLASH_SALE  = "flash_sale"    # flash sale terbatas waktu & kuota

class PromoTarget(str, Enum):
    STOCK           = "stock"            # berlaku untuk produk (Stock)
    SERVICE_PACKAGE = "service_package"  # berlaku untuk paket jasa
    ALL             = "all"              # berlaku untuk semua

class PromoStatus(str, Enum):
    DRAFT    = "draft"     # belum publish
    ACTIVE   = "active"    # sedang berjalan
    PAUSED   = "paused"    # dijeda sementara
    EXPIRED  = "expired"   # sudah habis waktu / kuota
    ARCHIVED = "archived"  # diarsipkan


# ══════════════════════════════════════════════════════════════════
# PROMO CAMPAIGN
# ══════════════════════════════════════════════════════════════════

class Promo(SQLModel, table=True):
    """
    Master promo / campaign.

    Contoh:
      - "Flash Sale Kamera Hikvision 30% OFF"
      - "Paket Lebaran: Beli Paket Rumah gratis instalasi"
      - "Diskon Rp 200.000 untuk servis perdana"

    Promo bisa mengikat ke item spesifik (via PromoItem)
    atau berlaku global untuk semua produk.

    Redis Cache:
      - Key aktif: promo:active:{target}        → list UUID promo aktif
      - Key detail: promo:detail:{uuid}         → full promo JSON
      - Key kuota: promo:quota:{uuid}           → remaining_quota (DECR atomic)
      TTL: 5 menit untuk list, 1 jam untuk detail, no-TTL untuk kuota
    """
    __tablename__ = "promo"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    # ── Identitas ──────────────────────────────────────────────────
    name: str = Field(
        sa_column=Column(pg.VARCHAR(200), nullable=False)
    )
    slug: str = Field(
        sa_column=Column(pg.VARCHAR(200), unique=True, nullable=False, index=True)
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.TEXT)
    )
    banner_url: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.TEXT)
    )  # URL gambar banner promo (dari R2/CDN)

    # ── Tipe & Target ──────────────────────────────────────────────
    promo_type: PromoType = Field(
        sa_column=Column(pg.VARCHAR(30), nullable=False, index=True)
    )
    target: PromoTarget = Field(
        default=PromoTarget.ALL,
        sa_column=Column(pg.VARCHAR(30), nullable=False, index=True)
    )

    # ── Nilai Diskon ───────────────────────────────────────────────
    # Untuk PERCENTAGE: discount_value = angka persen (1-100)
    # Untuk FIXED: discount_value = nominal rupiah
    # Untuk BOGO: discount_value = jumlah item gratis (buy_quantity wajib diisi)
    # Untuk BUNDLE_DISC: discount_value = persen/nominal dari total bundle
    discount_value: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False)
    )
    max_discount: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )  # Batas maksimal potongan (untuk PERCENTAGE, agar tidak kelewatan)

    # ── BOGO Config ────────────────────────────────────────────────
    buy_quantity: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )  # Harus beli berapa unit untuk trigger BOGO
    get_quantity: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )  # Dapat berapa unit gratis

    # ── Syarat Minimum ─────────────────────────────────────────────
    min_purchase: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False)
    )  # Minimum total belanja untuk dapat promo
    min_qty: int = Field(
        default=1,
        sa_column=Column(pg.INTEGER, nullable=False)
    )  # Minimum jumlah item

    # ── Kuota & Periode ───────────────────────────────────────────
    quota: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )  # null = unlimited
    used_count: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False, server_default="0")
    )
    # Per-user limit
    max_use_per_user: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )  # null = unlimited per user

    valid_from: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False, index=True)
    )
    valid_until: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False, index=True)
    )

    # ── Flash Sale Config ──────────────────────────────────────────
    is_flash_sale: bool = Field(
        default=False,
        sa_column=Column(pg.BOOLEAN, nullable=False, server_default="false")
    )
    flash_sale_quota: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )  # Kuota khusus flash sale (terpisah dari quota utama)
    flash_sale_mode: str = Field(
        default="manual",
        sa_column=Column(pg.VARCHAR(20), nullable=False, server_default="manual")
    )  # manual | auto
    auto_strategy: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(30), nullable=True)
    )  # discount | sold | stock_clearance

    # ── Metadata Tambahan ──────────────────────────────────────────
    # Untuk menyimpan config tambahan spesifik tipe promo
    # Contoh: {"applicable_brands": ["hikvision", "dahua"], "service_categories": ["installation"]}
    extra_config: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(pg.JSONB, server_default=text("'{}'::jsonb"))
    )

    # ── Status ─────────────────────────────────────────────────────
    status: PromoStatus = Field(
        default=PromoStatus.DRAFT,
        sa_column=Column(pg.VARCHAR(20), nullable=False, index=True)
    )
    priority: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False, server_default="0")
    )  # Promo dengan priority lebih tinggi ditampilkan lebih dulu & dipakai lebih dulu jika tumpang tindih

    # ── Audit ──────────────────────────────────────────────────────
    created_by: Optional[UUID] = Field(
        default=None,
        sa_column=Column(pg.UUID(as_uuid=True), nullable=True)
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True, index=True)
    )  # Soft delete

    __table_args__ = (
        Index("idx_promo_status_valid", "status", "valid_from", "valid_until"),
        Index("idx_promo_type_target",  "promo_type", "target"),
        Index(
            "idx_promo_name_gin",
            text("to_tsvector('simple', name)"),
            postgresql_using="gin"
        ),
    )


# ══════════════════════════════════════════════════════════════════
# PROMO ITEM — Binding promo ke produk/paket spesifik
# ══════════════════════════════════════════════════════════════════

class PromoItem(SQLModel, table=True):
    """
    Menghubungkan satu Promo ke satu atau lebih Stock / ServicePackage.

    Jika Promo.target = ALL dan tidak ada PromoItem → berlaku untuk semua.
    Jika ada PromoItem → hanya berlaku untuk item yang terdaftar.

    Contoh:
      - Flash Sale Kamera Hikvision → PromoItem → stock_uuid = [UUID kamera DS-...]
      - Diskon Paket Rumah → PromoItem → package_uuid = [UUID service_package]
    """
    __tablename__ = "promo_item"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    promo_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("promo.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    # Salah satu dari dua ini diisi (tidak keduanya sekaligus)
    stock_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("stock.uuid", ondelete="CASCADE"),
            nullable=True,
            index=True,
        )
    )
    package_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("service_package.uuid", ondelete="CASCADE"),
            nullable=True,
            index=True,
        )
    )

    # Override diskon khusus item ini (null = pakai diskon dari Promo induk)
    override_discount_value: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )

    __table_args__ = (
        Index("idx_promo_item_promo",   "promo_uuid"),
        Index("idx_promo_item_stock",   "stock_uuid"),
        Index("idx_promo_item_package", "package_uuid"),
        UniqueConstraint("promo_uuid", "stock_uuid",   name="uq_promo_stock"),
        UniqueConstraint("promo_uuid", "package_uuid", name="uq_promo_package"),
    )


# ══════════════════════════════════════════════════════════════════
# PROMO USAGE — Audit trail pemakaian promo per user/booking/order
# ══════════════════════════════════════════════════════════════════

class PromoUsage(SQLModel, table=True):
    """
    Mencatat setiap kali promo dipakai.
    Dipakai untuk:
      1. Validasi max_use_per_user
      2. Audit trail / laporan
      3. Rollback jika transaksi gagal (via idempotency key)
    """
    __tablename__ = "promo_usage"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    promo_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("promo.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    user_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(pg.UUID(as_uuid=True), nullable=True, index=True)
    )

    # Referensi ke transaksi yang memakai promo
    # Salah satu diisi
    booking_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("service_booking.uuid", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )
    )
    order_id: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(100), nullable=True, index=True)
    )  # Untuk order produk (jika ada order model terpisah)

    discount_applied: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False)
    )  # Nilai diskon yang benar-benar diberikan (dalam Rupiah)

    # Idempotency: mencegah double-apply promo
    idempotency_key: str = Field(
        sa_column=Column(pg.VARCHAR(200), unique=True, nullable=False, index=True)
    )  # Format: {promo_uuid}:{user_uuid}:{booking_uuid or order_id}

    used_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    )

    # Untuk rollback: null = aktif, ada value = sudah di-rollback
    rolled_back_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True)
    )

    __table_args__ = (
        Index("idx_promo_usage_promo",   "promo_uuid"),
        Index("idx_promo_usage_user",    "user_uuid"),
        Index("idx_promo_usage_booking", "booking_uuid"),
    )


class PromoTransactionItem(SQLModel, table=True):
    """
    Satu baris item dalam PromoTransaction.
    Bisa berupa Stock (produk fisik) atau ServicePackage (paket jasa).
    Menyimpan snapshot diskon per item.
    """
    __tablename__ = "promo_transaction_item"
 
    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    promo_transaction_id: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("promo_transaction.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
 
    # Salah satu diisi
    stock_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("stock.uuid", ondelete="RESTRICT"),
            nullable=True,
            index=True,
        )
    )
    package_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("service_package.uuid", ondelete="RESTRICT"),
            nullable=True,
            index=True,
        )
    )
    promo_transaction: Optional["PromoTransaction"] = Relationship(
        back_populates="items"
    )
    item_type: str = Field(
        sa_column=Column(pg.VARCHAR(20), nullable=False)
    )  # "stock" atau "service_package"
 
    item_name: str = Field(
        sa_column=Column(pg.VARCHAR(255), nullable=False)
    )  # snapshot nama item
 
    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    original_price: int = Field(sa_column=Column(pg.INTEGER, nullable=False))   # harga asli per unit
    discount_value: int = Field(default=0, sa_column=Column(pg.INTEGER, nullable=False))  # diskon per unit
    unit_price: int = Field(sa_column=Column(pg.INTEGER, nullable=False))       # harga setelah diskon per unit
    subtotal: int = Field(sa_column=Column(pg.INTEGER, nullable=False))         # unit_price × quantity
 
    __table_args__ = (
        Index("idx_pti_transaction", "promo_transaction_id"),
        Index("idx_pti_stock", "stock_uuid"),
        Index("idx_pti_package", "package_uuid"),
    )
 
 
# ══════════════════════════════════════════════════════════════════
# PROMO TRANSACTION
# ══════════════════════════════════════════════════════════════════
 
class PromoTransaction(SQLModel, table=True):
    """
    Transaksi yang dibuat melalui halaman promo.
    Berbeda dari Transaction biasa:
      - Terikat ke Promo (promo_uuid)
      - Bisa mix produk fisik + jasa
      - Jika ada jasa: ada service_booking_uuid (foreign key ke service_booking)
      - Order ID format: PROMO-YYYYMMDD-XXXXXXXX
 
    Midtrans charge tetap menggunakan endpoint yang sama,
    hanya order_id yang berbeda prefix.
    """
    __tablename__ = "promo_transaction"
 
    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
 
    # ── Relasi User ────────────────────────────────────────────────
    user_id: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("user.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    
    # ── Promo yang dipakai ─────────────────────────────────────────
    promo_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("promo.uuid", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        )
    )
    promo_snapshot: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(pg.JSONB, nullable=True)
    )  # snapshot promo saat transaksi dibuat (immutable)
 
    # ── Order ID ───────────────────────────────────────────────────
    order_id: str = Field(
        sa_column=Column(pg.VARCHAR(100), unique=True, nullable=False, index=True)
    )  # Format: PROMO-YYYYMMDD-XXXXXXXX
 
    # ── Harga ──────────────────────────────────────────────────────
    items_subtotal_original: int = Field(
        sa_column=Column(pg.INTEGER, nullable=False)
    )  # total sebelum diskon
    total_discount: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False)
    )
    items_subtotal_discounted: int = Field(
        sa_column=Column(pg.INTEGER, nullable=False)
    )  # total setelah diskon
    shipping_cost: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False)
    )  # ongkir produk fisik
    service_cost: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False)
    )  # transport + addons jasa (jika ada)
    gross_amount: int = Field(
        sa_column=Column(pg.INTEGER, nullable=False)
    )
    items: List[PromoTransactionItem] = Relationship(
        back_populates="promo_transaction",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "select"},
    )
 
    # ── Status & Payment ───────────────────────────────────────────
    transaction_status: Optional[str] = Field(
        default="pending_payment",
        sa_column=Column(pg.VARCHAR(50))
    )
    payment_type: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(50)))
    transaction_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True))
    )
    settlement_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True))
    )
    fraud_status: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(30)))
    status_code: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(10)))
    status_message: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    raw_response: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(pg.JSONB, nullable=True)
    )
 
    # ── Relasi ke Service Booking (jika ada jasa) ──────────────────
    service_booking_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("service_booking.uuid", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )
    )  # Jika promo mengandung service_items, booking dibuat otomatis
 
    # ── Relasi ke Shipment (jika ada produk fisik) ─────────────────
    # Shipment UUID: disimpan di tabel ongkir.Shipment,
    # relasi via transaction_uuid → shipment.promo_transaction_uuid
    has_shipment: bool = Field(
        default=False,
        sa_column=Column(pg.BOOLEAN, nullable=False, server_default="false")
    )
 
    # ── Audit ──────────────────────────────────────────────────────
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )
 
    __table_args__ = (
        Index("idx_pt_user", "user_id"),
        Index("idx_pt_promo", "promo_uuid"),
        Index("idx_pt_status", "transaction_status"),
        Index("idx_pt_booking", "service_booking_uuid"),
        Index("idx_promo_trx_user_created", "user_id", desc("created_at")),
    )