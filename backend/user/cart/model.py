from sqlmodel import SQLModel, Field, Column, Relationship,UniqueConstraint
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, func, Index, desc
from backend.auth.model import User
from backend.data.stock.model import Stock

class Cart(SQLModel, table=True):
    __tablename__ = "cart"

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

    quantity: int = Field(default=1)

    options: Optional[dict] = Field(
        default=None,
        sa_column=Column(pg.JSONB, nullable=True)
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    __table_args__ = (
        UniqueConstraint("user_uuid", "stock_uuid", "options", name="uq_user_stock_options_cart"),
        Index("idx_cart_user_created", "user_uuid", desc("created_at")),
    )

    # Relationships
    user: Optional["User"] = Relationship()
    # Pastikan di model Stock ada relationship ke Asset untuk ambil gambar
    stock: Optional["Stock"] = Relationship()