from pydantic import BaseModel,Field
from uuid import UUID
from typing import List, Optional,Any,Dict
from datetime import datetime

# schemas.py


class WishlistAddRequest(BaseModel):
    stock_uuid: UUID

class WishlistStockResponse(BaseModel):
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
    
class WishlistItemResponse(BaseModel):
    wishlist_uuid: UUID
    created_at: datetime
    stock: WishlistStockResponse
    
class WishlistUpdateRequest(BaseModel):
    notes: Optional[str] = None

class WishlistItemResponse(BaseModel):
    wishlist_uuid: UUID
    created_at: datetime
    notes: Optional[str] = None # Tambahkan di response agar muncul di UI
    stock: WishlistStockResponse