from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import func, Index, text, ForeignKey


class AssetStock(SQLModel, table=True):
    __tablename__ = "assetstock"
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(pg.UUID(as_uuid=True), primary_key=True))
    url: str = Field(sa_column=Column(pg.TEXT, nullable=False, index=True))
    type: str = Field(sa_column=Column(pg.VARCHAR(20), index=True, default="image"))
    alt_text: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    stock_uuid: Optional[UUID] = Field(default=None, sa_column=Column(
        pg.UUID(as_uuid=True), ForeignKey("stock.uuid", ondelete="CASCADE"), index=True
    ))
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), server_default=func.now(), index=True
    ))
    stock: Optional["Stock"] = Relationship(
        back_populates="assets",
        sa_relationship_kwargs={"foreign_keys": "[AssetStock.stock_uuid]"}
    )


class BundleLink(SQLModel, table=True):
    __tablename__ = "bundle_link"

    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    parent_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("stock.uuid", ondelete="CASCADE"),
            index=True
        )
    )
    child_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("stock.uuid", ondelete="CASCADE"),
            index=True
        )
    )
    quantity: int = Field(default=1)
    # ── NEW: override harga child di dalam bundle ini ──────────────
    # Null = pakai harga asli dari Stock.online_price
    override_price: Optional[int] = Field(
        default=None,
        sa_column=Column(pg.INTEGER, nullable=True)
    )
    # Label/keterangan posisi item dalam bundle (opsional)
    position_label: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(100), nullable=True)
    )
    sort_order: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, nullable=False, server_default="0")
    )

    __table_args__ = (
        Index("idx_bundle_parent", "parent_uuid"),
        Index("idx_bundle_child", "child_uuid"),
    )


class Stock(SQLModel, table=True):
    __tablename__ = "stock"
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(
        pg.UUID(as_uuid=True), primary_key=True, nullable=False
    ))
    asset_uuid: Optional[UUID] = Field(default=None, sa_column=Column(pg.UUID(as_uuid=True), index=True))
    title: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False, index=True))
    slug: str = Field(sa_column=Column(pg.VARCHAR(255), index=True, unique=True))
    brand: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(100), index=True))
    category_slug: str = Field(sa_column=Column(pg.VARCHAR(50), index=True))
    subcategory_slug: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(100), index=True))
    type: str = Field(default="camera cctv", sa_column=Column(
        pg.VARCHAR(50), index=True, server_default="camera cctv"
    ))
    specs: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(
        pg.JSONB, server_default=text("'{}'::jsonb")
    ))
    description: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    original_price: int = Field(default=0, sa_column=Column(pg.INTEGER))
    discount_percentage: int = Field(default=0, sa_column=Column(pg.INTEGER))
    online_price: int = Field(default=0, sa_column=Column(pg.INTEGER, index=True))
    weight: int = Field(default=700, sa_column=Column(
        pg.INTEGER, nullable=False, server_default="700", comment="gram"
    ))
    stok: int = Field(default=0)
    terjual: int = Field(default=0)
    is_active: bool = Field(default=True, sa_column=Column(pg.BOOLEAN, index=True))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    ))
    assets: List[AssetStock] = Relationship(
        back_populates="stock",
        sa_relationship_kwargs={
            "foreign_keys": "[AssetStock.stock_uuid]",
            "order_by": "AssetStock.created_at"
        }
    )
    __table_args__ = (
        Index("idx_stock_title_gin", text("to_tsvector('simple', title)"), postgresql_using="gin"),
    )


class Coupon(SQLModel, table=True):
    __tablename__ = "coupon"
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(pg.UUID(as_uuid=True), primary_key=True))
    code: str = Field(sa_column=Column(pg.VARCHAR(50), unique=True, index=True, nullable=False))
    discount_type: str = Field(sa_column=Column(pg.VARCHAR(20), nullable=False))
    discount_value: int = Field(default=0)
    min_purchase: int = Field(default=0)
    max_discount: Optional[int] = Field(default=None)
    quota: int = Field(default=100)
    used_count: int = Field(default=0)
    valid_from: Optional[datetime] = Field(default=None, sa_column=Column(pg.TIMESTAMP(timezone=True)))
    valid_until: Optional[datetime] = Field(default=None, sa_column=Column(pg.TIMESTAMP(timezone=True)))
    is_active: bool = Field(default=True, sa_column=Column(pg.BOOLEAN, index=True))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now()))
    # ── Soft delete: null = aktif, ada timestamp = sudah dihapus ──
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True, index=True)
    )