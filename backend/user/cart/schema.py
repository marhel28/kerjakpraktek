from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional,Dict,Any

class CartAddRequest(BaseModel):
    stock_uuid: UUID
    quantity: int = Field(default=1, ge=1, description="Minimal kuantitas adalah 1")

class CartUpdateRequest(BaseModel):
    quantity: int = Field(default=1, ge=1)

# Skema untuk summary item di keranjang
class CartStockResponse(BaseModel):
    uuid: UUID
    title: str
    slug: str
    online_price: int
    original_price: int = 0
    discount_percentage: int = 0
    brand: Optional[str] = None
    category_slug: Optional[str] = None
    subcategory_slug: Optional[str] = None
    specs: Dict[str, Any] = Field(default_factory=dict)
    cover_image_url: Optional[str] = None
    weight:int
    

class CartItemResponse(BaseModel):
    cart_uuid: UUID
    quantity: int
    subtotal: int
    stock: CartStockResponse

class CartSummaryResponse(BaseModel):
    items: List[CartItemResponse]
    total_quantity: int
    total_price: int