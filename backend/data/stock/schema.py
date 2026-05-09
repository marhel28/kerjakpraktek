from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime


# ── Cart ───────────────────────────────────────────────────────────
class CartAddRequest(BaseModel):
    stock_uuid: UUID
    quantity: int = Field(default=1, ge=1)


class CartUpdateRequest(BaseModel):
    quantity: int = Field(default=1, ge=1)


class CartStockResponse(BaseModel):
    uuid: UUID
    title: str
    slug: str
    online_price: int
    original_price: int
    discount_percentage: int
    brand: Optional[str] = None
    category_slug: str
    subcategory_slug: Optional[str] = None
    specs: Dict[str, Any] = Field(default_factory=dict)
    cover_image_url: Optional[str] = None


class CartItemResponse(BaseModel):
    cart_uuid: UUID
    quantity: int
    subtotal: int
    stock: CartStockResponse


class CartSummaryResponse(BaseModel):
    items: List[CartItemResponse]
    total_quantity: int
    total_price: int


# ── Coupon ─────────────────────────────────────────────────────────
class CouponCreateRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    discount_type: str = Field(..., pattern="^(percentage|fixed_amount)$")
    discount_value: int = Field(..., ge=1)
    min_purchase: int = Field(default=0, ge=0)
    max_discount: Optional[int] = Field(default=None, ge=1)
    quota: int = Field(default=100, ge=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("discount_value")
    @classmethod
    def validate_percentage(cls, v: int, info) -> int:
        if info.data.get("discount_type") == "percentage" and v > 100:
            raise ValueError("Persentase diskon tidak boleh lebih dari 100")
        return v


class CouponUpdateRequest(BaseModel):
    discount_type: Optional[str] = Field(default=None, pattern="^(percentage|fixed_amount)$")
    discount_value: Optional[int] = Field(default=None, ge=1)
    min_purchase: Optional[int] = Field(default=None, ge=0)
    max_discount: Optional[int] = Field(default=None, ge=1)
    quota: Optional[int] = Field(default=None, ge=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None


class CouponResponse(BaseModel):
    uuid: UUID
    code: str
    discount_type: str
    discount_value: int
    min_purchase: int
    max_discount: Optional[int]
    quota: int
    used_count: int
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CouponValidateRequest(BaseModel):
    code: str
    cart_total: int = Field(..., ge=0)