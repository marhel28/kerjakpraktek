# ============================================================
# FILE: backend/data/transaksi/schema.py  (FULL REPLACE)
# ============================================================
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


# ============================================================
# REQUEST: Checkout (single item)
# ============================================================
# backend/data/transaksi/schema.py

class CheckoutAddon(BaseModel):
    addon_uuid: UUID
    quantity: int = Field(ge=1, le=99)


class CheckoutItem(BaseModel):
    stock_uuid: UUID
    quantity: int = Field(ge=1, le=999)
    addons: Optional[list[CheckoutAddon]] = Field(default_factory=list)


class CheckoutRequest(BaseModel):
    items: list[CheckoutItem] = Field(..., min_length=1, max_length=20)

    address_uuid: UUID = Field(..., description="UUID alamat pengiriman tersimpan")
    courier_name: str = Field(default="jne", max_length=50)
    courier_service: Optional[str] = Field(default="REG", max_length=50)

    coupon_code: Optional[str] = Field(default=None, max_length=50)


class CheckoutResponse(BaseModel):
    order_id: str
    transaction_uuid: str
    items_subtotal: int
    shipping_cost: int
    discount_amount: int
    gross_amount: int
    qr_code_url: Optional[str] = None
    payment_url: Optional[str] = None
    transaction_status: str = "pending"
    expiry_time: Optional[str] = None
    snap_token:Optional[str] = None
    message: str = "Silakan selesaikan pembayaran"


# ============================================================
# RESPONSE: Ongkir estimate (dipakai di endpoint cek ongkir)
# ============================================================
class ShippingOptionResponse(BaseModel):
    courier: str
    service: str
    etd: Optional[str]
    price: int


# ============================================================
# RESPONSE: Detail transaksi user (riwayat)
# ============================================================
class TransactionDetailResponse(BaseModel):
    uuid: str
    order_id: str
    quantity: int
    gross_amount: int
    shipping_cost: int
    transaction_status: Optional[str]
    payment_type: Optional[str]
    transaction_time: Optional[datetime]
    settlement_time: Optional[datetime]
    created_at: datetime

    # Stock info
    stock_uuid: str
    stock_title: str
    stock_slug: str
    stock_online_price: int
    stock_brand: Optional[str]
    cover_image_url: Optional[str] = None

    # Shipment
    waybill_number: Optional[str]   = None
    delivery_status: Optional[str]  = None
    recipient_name: Optional[str]   = None
    shipping_address: Optional[str] = None
    courier_name: Optional[str]     = None
    courier_service: Optional[str]  = None


# ============================================================
# WEBHOOK dari Midtrans
# ============================================================
class MidtransWebhookPayload(BaseModel):
    order_id: str
    transaction_status: str
    payment_type: Optional[str]     = None
    gross_amount: Optional[str]     = None
    transaction_time: Optional[str] = None
    settlement_time: Optional[str]  = None
    fraud_status: Optional[str]     = None
    status_code: Optional[str]      = None
    status_message: Optional[str]  = None
    signature_key: Optional[str]   = None

    class Config:
        extra = "allow"   # Midtrans kirim banyak field extra