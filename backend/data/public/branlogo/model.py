from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlalchemy import func, Index, ForeignKey, text


class Brand(SQLModel, table=True):
    __tablename__ = "brand"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    name: str = Field(
        sa_column=Column(pg.VARCHAR(100), nullable=False, unique=True, index=True)
    )

    slug: str = Field(
        sa_column=Column(pg.VARCHAR(100), nullable=False, unique=True, index=True)
    )

    logo_uuid: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("asset.uuid", ondelete="SET NULL"),
            index=True
        )
    )

    route: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.TEXT)
    )

    description: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.TEXT)
    )

    is_active: bool = Field(
        default=True,
        sa_column=Column(pg.BOOLEAN, server_default="true", index=True)
    )

    is_featured: bool = Field(
        default=False,
        sa_column=Column(pg.BOOLEAN, server_default="false", index=True)
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

    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        )
    )

    logo: Optional["Asset"] = Relationship()

    __table_args__ = (
        Index(
            "idx_brand_name_search",
            text("lower(name)")  # 🔥 FIX
        ),
    )