"""
schemas/about.py
Pydantic v2 schemas – request & response untuk About Us API
"""

from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, HttpUrl, model_validator


# ══════════════════════════════════════════════════════════════════════════════
# STAT
# ══════════════════════════════════════════════════════════════════════════════

class StatBase(BaseModel):
    value : Annotated[str, Field(max_length=50,  examples=["1,200+"])]
    label : Annotated[str, Field(max_length=100, examples=["Kamera Aktif"])]
    order : int = 0


class StatCreate(StatBase):
    pass


class StatResponse(StatBase):
    id: UUID

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════════════════
# VALUE (keunggulan)
# ══════════════════════════════════════════════════════════════════════════════

class ValueBase(BaseModel):
    icon  : Annotated[str, Field(max_length=60,  examples=["lucide:shield-alert"])]
    title : Annotated[str, Field(max_length=150, examples=["Zero Blind-Spot Design"])]
    desc  : Annotated[str, Field(min_length=10)]
    order : int = 0


class ValueCreate(ValueBase):
    pass


class ValueResponse(ValueBase):
    id: UUID

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════════════════
# GALLERY
# ══════════════════════════════════════════════════════════════════════════════

class GalleryResponse(BaseModel):
    id       : UUID
    cdn_url  : str
    alt      : Annotated[str, Field(max_length=200)]
    order    : int
    created_at: datetime

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════════════════
# ABOUT PAGE – CREATE / UPDATE
# ══════════════════════════════════════════════════════════════════════════════

class AboutPageCreate(BaseModel):
    # Hero
    hero_badge_text : Annotated[str, Field(max_length=100,  default="Partner Keamanan Anda")]
    hero_heading    : Annotated[str, Field(min_length=5,    examples=["Jangan Pertaruhkan Aset Anda"])]
    hero_subheading : Annotated[str | None, Field(default=None)]

    # CTA
    cta_heading       : Annotated[str, Field(max_length=200, default="Garansi Ganti Baru Tanpa Debat")]
    cta_body          : str | None = None
    cta_primary_text  : Annotated[str, Field(max_length=80, default="Jadwalkan Survey Gratis")]
    cta_secondary_text: Annotated[str, Field(max_length=80, default="Lihat Harga Paket")]
    cta_secondary_url : Annotated[str, Field(max_length=200, default="/services/booking")]

    # Nested children
    stats  : list[StatCreate]  = Field(default_factory=list)
    values : list[ValueCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def min_one_stat(self) -> "AboutPageCreate":
        if len(self.stats) < 1:
            raise ValueError("Minimal 1 stat harus diisi.")
        return self


class AboutPageUpdate(BaseModel):
    """Semua field opsional untuk PATCH."""
    hero_badge_text   : str | None = None
    hero_heading      : str | None = None
    hero_subheading   : str | None = None
    cta_heading       : str | None = None
    cta_body          : str | None = None
    cta_primary_text  : str | None = None
    cta_secondary_text: str | None = None
    cta_secondary_url : str | None = None
    stats             : list[StatCreate]  | None = None
    values            : list[ValueCreate] | None = None


# ══════════════════════════════════════════════════════════════════════════════
# ABOUT PAGE – RESPONSE
# ══════════════════════════════════════════════════════════════════════════════

class AboutPageResponse(BaseModel):
    id              : UUID
    is_active       : bool
    hero_badge_text : str
    hero_heading    : str
    hero_subheading : str | None
    cta_heading     : str
    cta_body        : str | None
    cta_primary_text  : str
    cta_secondary_text: str
    cta_secondary_url : str
    stats           : list[StatResponse]
    values          : list[ValueResponse]
    gallery         : list[GalleryResponse]
    created_at      : datetime
    updated_at      : datetime

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════════════════
# GALLERY – UPLOAD RESPONSE
# ══════════════════════════════════════════════════════════════════════════════

class GalleryUploadResponse(BaseModel):
    id      : UUID
    cdn_url : str
    alt     : str
    order   : int

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════════════════
# GALLERY – ORDER UPDATE (drag-and-drop reorder)
# ══════════════════════════════════════════════════════════════════════════════

class GalleryOrderItem(BaseModel):
    id    : UUID
    order : int

class GalleryReorderRequest(BaseModel):
    items: list[GalleryOrderItem] = Field(min_length=1)