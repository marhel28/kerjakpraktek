# backend/data/activity/model.py

from sqlmodel import SQLModel, Field, Column, func
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_log"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    
    # 'order', 'booking', 'promo', 'user', 'system'
    activity_type: str = Field(sa_column=Column(pg.VARCHAR(50), index=True))
    
    # Judul singkat (e.g. "Order Baru", "Booking Selesai", "Kupon Digunakan")
    title: str = Field(sa_column=Column(pg.VARCHAR(255)))
    
    # Detail tambahan
    description: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    
    # Link ke entity terkait
    reference_id: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(100), index=True))
    user_id: Optional[UUID] = Field(default=None, sa_column=Column(pg.UUID(as_uuid=True), index=True))
    
    # Status/Visual
    status: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(50))) # settlement, pending, etc.
    amount: Optional[int] = Field(default=None, sa_column=Column(pg.INTEGER))
    
    # UI Hints
    icon: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(100))) # i-heroicons-...
    color: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(20))) # green, blue, red, orange
    
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    )
