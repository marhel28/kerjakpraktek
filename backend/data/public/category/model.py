from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, func, Index, text
from backend.data.public.assets import *


class Category(SQLModel, table=True):
    __tablename__ = "category"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    name: str = Field(
        sa_column=Column(pg.VARCHAR(100), nullable=False, index=True)
    )

    slug: str = Field(
        sa_column=Column(pg.VARCHAR(100), nullable=False, unique=True, index=True)
    )

    # 🔥 NEW: icon dari Nuxt Icon (heroicons, dll)
    icon_name: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(100), nullable=True)
    )

    # 🔥 OPTIONAL: fallback kalau pakai custom icon (upload)
    icon_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("asset.uuid", ondelete="SET NULL"),
            index=True
        )
    )

    is_active: bool = Field(
        default=True,
        sa_column=Column(pg.BOOLEAN, server_default="true", index=True)
    )

    position: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, index=True)
    )

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=func.now(),
            index=True
        )
    )

    # RELATION
    icon: Optional["Asset"] = Relationship()
    subcategories: List["SubCategory"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )

    __table_args__ = (
        Index(
            "idx_category_name_search",
            text("lower(name)")
        ),
    )


# =========================
# SUB CATEGORY
# =========================
class SubCategory(SQLModel, table=True):
    __tablename__ = "subcategory"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    name: str = Field(
        sa_column=Column(pg.VARCHAR(100), nullable=False, index=True)
    )

    slug: str = Field(
        sa_column=Column(pg.VARCHAR(100), nullable=False, index=True)
    )

    category_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("category.uuid", ondelete="CASCADE"),
            index=True
        )
    )

    position: int = Field(
        default=0,
        sa_column=Column(pg.INTEGER, index=True)
    )

    is_active: bool = Field(
        default=True,
        sa_column=Column(pg.BOOLEAN, server_default="true", index=True)
    )

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=func.now(),
            index=True
        )
    )

    # RELATION
    category: Optional["Category"] = Relationship(back_populates="subcategories")

    __table_args__ = (
        Index(
            "idx_subcategory_name_search",
            text("lower(name)")
        ),
    )