from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, func, UniqueConstraint
from backend.auth.model import User
from backend.data.stock.model import Stock

class Wishlist(SQLModel, table=True):
    __tablename__ = "wishlist"

    # 🔥 TEPAT: Cegah duplikasi barang yang sama untuk user yang sama
    __table_args__ = (
        UniqueConstraint("user_uuid", "stock_uuid", name="uq_user_stock_wishlist"),
    )

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    user_uuid: UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("user.uuid", ondelete="CASCADE"), index=True)
    )

    stock_uuid: UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("stock.uuid", ondelete="CASCADE"), index=True)
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )

    # Relationships
    user: Optional["User"] = Relationship()
    stock: Optional["Stock"] = Relationship()