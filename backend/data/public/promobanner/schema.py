"""
schema.py — Pydantic Schemas: Promo Checkout
Sistem: Padjajaran CCTV, Cimahi
"""

from pydantic import BaseModel, field_validator, model_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any


# ══════════════════════════════════════════════════════════════════
# PROMO ITEM IN CART
# ══════════════════════════════════════════════════════════════════

class PromoCartStockItem(BaseModel):
    """Item produk (Stock) dalam promo checkout."""
    stock_uuid: UUID
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v):
        if v < 1:
            raise ValueError("Quantity minimal 1")
        return v


class PromoCartServiceItem(BaseModel):
    """Item jasa (ServicePackage) dalam promo checkout."""
    package_uuid: UUID
    quantity: int = 1  # biasanya 1 untuk jasa

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v):
        if v < 1:
            raise ValueError("Quantity minimal 1")
        return v


# ══════════════════════════════════════════════════════════════════
# PROMO CHECKOUT REQUEST
# ══════════════════════════════════════════════════════════════════

class PromoCheckoutRequest(BaseModel):
    """
    Request checkout melalui halaman promo.

    Minimal salah satu dari stock_items atau service_items harus diisi.
    promo_uuid wajib — ini yang membedakan dari checkout biasa.

    Untuk paket jasa (service_items): wajib isi address_service.
    Untuk produk fisik (stock_items): wajib isi address_uuid (alamat pengiriman).
    """
    promo_uuid: UUID

    # Item produk fisik (opsional)
    stock_items: List[PromoCartStockItem] = []

    # Item jasa (opsional)
    service_items: List[PromoCartServiceItem] = []

    # Untuk pengiriman produk fisik
    address_uuid: Optional[UUID] = None
    courier_name: Optional[str] = None      # "jne", "sicepat", "jnt"
    courier_service: Optional[str] = None   # "REG", "YES", "OKE"

    # Untuk booking jasa (jika ada service_items)
    scheduled_date: Optional[str] = None    # "YYYY-MM-DD"
    time_slot: Optional[str] = None         # "08:00-11:00"
    address_service: Optional[str] = None  # alamat pemasangan
    district: Optional[str] = None
    city: Optional[str] = None
    distance_km: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_items(self):
        if not self.stock_items and not self.service_items:
            raise ValueError("Minimal satu item produk atau jasa harus diisi")
        if self.stock_items and not self.address_uuid:
            raise ValueError("address_uuid wajib diisi jika ada produk fisik")
        if self.stock_items and not self.courier_name:
            raise ValueError("courier_name wajib diisi jika ada produk fisik")
        if self.service_items:
            missing = []
            if not self.scheduled_date: missing.append("scheduled_date")
            if not self.time_slot: missing.append("time_slot")
            if not self.address_service: missing.append("address_service")
            if not self.city: missing.append("city")
            if self.distance_km is None: missing.append("distance_km")
            if not self.contact_name: missing.append("contact_name")
            if not self.contact_phone: missing.append("contact_phone")
            if missing:
                raise ValueError(f"Field wajib untuk jasa: {missing}")
        return self


# ══════════════════════════════════════════════════════════════════
# PROMO PRICE BREAKDOWN
# ══════════════════════════════════════════════════════════════════

class PromoItemBreakdown(BaseModel):
    item_uuid: UUID
    item_type: str          # "stock" atau "service_package"
    item_name: str
    original_price: int
    quantity: int
    discount_value: int     # nilai diskon per item
    discount_type: str      # "percentage" atau "fixed"
    after_discount: int
    subtotal: int           # after_discount × quantity


class PromoPriceResult(BaseModel):
    """Hasil kalkulasi harga setelah promo."""
    promo_uuid: UUID
    promo_name: str
    promo_type: str

    items: List[PromoItemBreakdown]
    items_subtotal_original: int   # total sebelum diskon
    total_discount: int
    items_subtotal_discounted: int # total setelah diskon
    shipping_cost: int             # ongkir (0 jika pure jasa)
    service_cost: int              # biaya jasa (transport + addons) jika ada service_items
    gross_amount: int              # final total


# ══════════════════════════════════════════════════════════════════
# PROMO CHECKOUT RESPONSE
# ══════════════════════════════════════════════════════════════════

class PromoCheckoutResponse(BaseModel):
    order_id: str
    promo_transaction_uuid: str

    # Breakdown harga
    items_subtotal_original: int
    total_discount: int
    items_subtotal_discounted: int
    shipping_cost: int
    service_cost: int
    gross_amount: int

    transaction_status: str

    # Midtrans Snap
    snap_token: Optional[str] = None
    payment_url: Optional[str] = None
    expiry_time: Optional[str] = None

    # Jika ada service booking
    booking_number: Optional[str] = None


# ══════════════════════════════════════════════════════════════════
# PROMO LIST / DETAIL RESPONSE
# ══════════════════════════════════════════════════════════════════

class PromoItemResponse(BaseModel):
    """Satu item yang terikat ke promo (stock atau package)."""
    uuid: UUID
    item_type: str          # "stock" atau "service_package"
    item_uuid: UUID
    item_name: str
    item_slug: str
    item_price: int
    thumbnail_url: Optional[str] = None
    override_discount_value: Optional[int] = None


class PromoResponse(BaseModel):
    uuid: UUID
    name: str
    slug: str
    description: Optional[str]
    banner_url: Optional[str]
    promo_type: str
    target: str
    discount_value: int
    max_discount: Optional[int]
    buy_quantity: Optional[int]
    get_quantity: Optional[int]
    min_purchase: int
    min_qty: int
    quota: Optional[int]
    used_count: int
    max_use_per_user: Optional[int]
    valid_from: datetime
    valid_until: datetime
    is_flash_sale: bool
    flash_sale_quota: Optional[int]
    status: str
    priority: int
    items: List[PromoItemResponse] = []

    # Computed fields (dihitung saat response)
    is_valid: bool = True           # masih dalam periode & kuota
    remaining_quota: Optional[int] = None


class PromoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[PromoResponse]


# ══════════════════════════════════════════════════════════════════
# ADMIN: CREATE/UPDATE PROMO
# ══════════════════════════════════════════════════════════════════

class PromoItemCreate(BaseModel):
    stock_uuid: Optional[UUID] = None
    package_uuid: Optional[UUID] = None
    override_discount_value: Optional[int] = None

    @model_validator(mode="after")
    def check_one_of(self):
        if not self.stock_uuid and not self.package_uuid:
            raise ValueError("Salah satu stock_uuid atau package_uuid harus diisi")
        if self.stock_uuid and self.package_uuid:
            raise ValueError("Hanya boleh salah satu: stock_uuid atau package_uuid")
        return self


class PromoCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    banner_url: Optional[str] = None
    promo_type: str
    target: str = "all"
    discount_value: int
    max_discount: Optional[int] = None
    buy_quantity: Optional[int] = None
    get_quantity: Optional[int] = None
    min_purchase: int = 0
    min_qty: int = 1
    quota: Optional[int] = None
    max_use_per_user: Optional[int] = None
    valid_from: datetime
    valid_until: datetime
    is_flash_sale: bool = False
    flash_sale_quota: Optional[int] = None
    extra_config: Dict[str, Any] = {}
    priority: int = 0
    items: List[PromoItemCreate] = []

    @field_validator("discount_value")
    @classmethod
    def validate_discount(cls, v):
        if v < 0:
            raise ValueError("discount_value tidak boleh negatif")
        return v


class PromoUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    banner_url: Optional[str] = None
    discount_value: Optional[int] = None
    max_discount: Optional[int] = None
    min_purchase: Optional[int] = None
    min_qty: Optional[int] = None
    quota: Optional[int] = None
    max_use_per_user: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_flash_sale: Optional[bool] = None
    flash_sale_quota: Optional[int] = None
    extra_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    priority: Optional[int] = None


# ══════════════════════════════════════════════════════════════════
# PROMO VALIDATE (cek sebelum checkout)
# ══════════════════════════════════════════════════════════════════

class PromoValidateRequest(BaseModel):
    promo_uuid: Optional[UUID] = None
    promo_slug: Optional[str] = None
    stock_items: List[PromoCartStockItem] = []
    service_items: List[PromoCartServiceItem] = []

    @model_validator(mode="after")
    def check_identifier(self):
        if not self.promo_uuid and not self.promo_slug:
            raise ValueError("promo_uuid atau promo_slug harus diisi")
        return self


class PromoValidateResponse(BaseModel):
    is_valid: bool
    message: str
    promo: Optional[PromoResponse] = None
    price_result: Optional[PromoPriceResult] = None