from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import List
from sqlalchemy import func, ForeignKey

from backend.data.public.assets.model import Asset

VALID_MODES = (
    "auto", "single", "double", "mixed", "triple", "quad",
    "asymLeft", "asymRight", "heroStrip", "spotlight", "mosaic",
    "ribbon", "featureWide", "cinematic", "stack", "marquee", "filmStrip",
)


class ImageSection(SQLModel, table=True):
    __tablename__ = "image_section"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True),
    )
    identifier: str = Field(
        sa_column=Column(pg.VARCHAR(100), unique=True, index=True, nullable=False)
    )
    title: str = Field(sa_column=Column(pg.VARCHAR(150), nullable=False))

    # ← NEW: dikonsumsi langsung oleh Vue props `mode`
    mode: str = Field(
        default="auto",
        sa_column=Column(pg.VARCHAR(20), nullable=False, server_default="auto"),
    )

    is_active: bool = Field(
        default=True, sa_column=Column(pg.BOOLEAN, index=True)
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    items: list["ImageSectionItem"] = Relationship(
        back_populates="section",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "ImageSectionItem.order",
        },
    )


class ImageSectionItem(SQLModel, table=True):
    __tablename__ = "image_section_item"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True),
    )
    section_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("image_section.uuid", ondelete="CASCADE"),
        )
    )
    asset_uuid: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("asset.uuid", ondelete="RESTRICT"),
        )
    )
    target_url: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    order: int = Field(default=1, sa_column=Column(pg.INTEGER))

    section: "ImageSection" = Relationship(back_populates="items")
    asset: Asset = Relationship()