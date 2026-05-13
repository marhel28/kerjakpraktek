from typing import Optional, List
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, JSON, DateTime
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class AddonGroup(SQLModel, table=True):
    __tablename__ = "addon_groups"
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(pg.UUID(as_uuid=True), primary_key=True))
    name: str = Field(index=True)
    selection_type: str = Field(default="single")  # single | multi
    is_required: bool = Field(default=False)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    group_type: str = Field(default="optional", sa_column=Column(pg.VARCHAR(20), server_default="optional", nullable=False)) # required, optional, recommended
    is_global: bool = Field(default=False, sa_column=Column(pg.BOOLEAN, server_default="false", index=True))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default="now()"))

    items: List["AddonItem"] = Relationship(back_populates="group")

class AddonItem(SQLModel, table=True):
    __tablename__ = "addon_items"
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(pg.UUID(as_uuid=True), primary_key=True))
    group_uuid: UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("addon_groups.uuid", ondelete="CASCADE"), index=True))
    name: str
    description: Optional[str] = None
    price: float = Field(default=0.0)
    stock: int = Field(default=0)
    sku: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = Field(default=True)
    allow_quantity: bool = Field(default=False)
    max_quantity: int = Field(default=1)
    weight: int = Field(default=0, sa_column=Column(pg.INTEGER, nullable=False, server_default="0", comment="gram"))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default="now()"))
    
    group: AddonGroup = Relationship(back_populates="items")

class CategoryAddonMapping(SQLModel, table=True):
    __tablename__ = "category_addon_mapping"
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(pg.UUID(as_uuid=True), primary_key=True))
    category_uuid: Optional[UUID] = Field(default=None, sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("category.uuid", ondelete="CASCADE"), index=True, nullable=True))
    subcategory_uuid: Optional[UUID] = Field(default=None, sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("subcategory.uuid", ondelete="CASCADE"), index=True, nullable=True))
    addon_group_uuid: UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("addon_groups.uuid", ondelete="CASCADE"), index=True))
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)

class ProductAddonOverride(SQLModel, table=True):
    __tablename__ = "product_addon_override"
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(pg.UUID(as_uuid=True), primary_key=True))
    product_uuid: UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("stock.uuid", ondelete="CASCADE"), index=True))
    addon_item_uuid: UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("addon_items.uuid", ondelete="CASCADE"), index=True))
    override_price: Optional[float] = None
    override_stock: Optional[int] = None
    is_active: bool = Field(default=True)
    is_hidden: bool = Field(default=False)

class StockAddonMapping(SQLModel, table=True):
    __tablename__ = "stock_addon_mapping"
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(pg.UUID(as_uuid=True), primary_key=True))
    stock_uuid: UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("stock.uuid", ondelete="CASCADE"), index=True))
    addon_group_uuid: UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("addon_groups.uuid", ondelete="CASCADE"), index=True))
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)
