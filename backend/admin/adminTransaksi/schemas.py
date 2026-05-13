from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    uuid: UUID
    username: str
    email: str

    class Config:
        from_attributes = True

class ShipmentBase(BaseModel):
    uuid: UUID
    courier_name: str
    courier_service: Optional[str] = None
    waybill_number: Optional[str] = None
    delivery_status: str
    recipient_name: str
    shipping_address: str

    class Config:
        from_attributes = True

class TransactionItemRead(BaseModel):
    uuid: UUID
    stock_id: UUID
    quantity: int
    unit_price: int
    subtotal: int
    stock_title: Optional[str] = None
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionRead(BaseModel):
    uuid: UUID
    order_id: str
    user_id: UUID
    gross_amount: int
    shipping_cost: int = 0
    transaction_status: Optional[str] = None
    payment_type: Optional[str] = None
    transaction_time: Optional[datetime] = None
    created_at: datetime
    
    # Relationships
    user: Optional[UserBase] = None
    shipment: Optional[ShipmentBase] = None
    items: List[TransactionItemRead] = []
    
    # Raw response fallback
    raw_response: Optional[dict] = None

    class Config:
        from_attributes = True
