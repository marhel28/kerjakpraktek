"""
backend/data/about/model.py
Model SQLModel – About Us / Tentang Kami
Konsisten dengan pola proyek: SQLModel + AsyncSession dari backend.db.main
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship,Column
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime


def _utcnow() -> datetime:
    # FIX: Menghapus informasi timezone (tzinfo=None) agar menjadi offset-naive.
    # Ini akan cocok secara sempurna dengan tipe TIMESTAMP WITHOUT TIME ZONE di PostgreSQL.
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ══════════════════════════════════════════════════════════════════════════════
# ABOUT PAGE  (master – 1 row aktif)
# ══════════════════════════════════════════════════════════════════════════════

class AboutPage(SQLModel, table=True):
    """
    Master record halaman About Us.
    Hanya 1 row is_active=True pada satu waktu.
    """
    __tablename__ = "about_pages"

    id        : uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    is_active : bool = Field(default=True, nullable=False, index=True)

    # ── Hero ──────────────────────────────────────────────────────
    hero_badge_text : str         = Field(default="Partner Keamanan Anda", max_length=100)
    hero_heading    : str         = Field(nullable=False)
    hero_subheading : Optional[str] = Field(default=None, nullable=True)

    # ── CTA ───────────────────────────────────────────────────────
    cta_heading        : str = Field(default="Garansi Ganti Baru Tanpa Debat", max_length=200)
    cta_body           : Optional[str] = Field(default=None, nullable=True)
    cta_primary_text   : str = Field(default="Jadwalkan Survey Gratis", max_length=80)
    cta_secondary_text : str = Field(default="Lihat Harga Paket",       max_length=80)
    cta_secondary_url  : str = Field(default="/services/booking",        max_length=200)

    # ── Timestamps ────────────────────────────────────────────────
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    # ── Relasi ────────────────────────────────────────────────────
    stats   : list["AboutStat"]    = Relationship(back_populates="page")
    values  : list["AboutValue"]   = Relationship(back_populates="page")
    gallery : list["AboutGallery"] = Relationship(back_populates="page")


# ══════════════════════════════════════════════════════════════════════════════
# ABOUT STAT  (angka-angka kepercayaan)
# ══════════════════════════════════════════════════════════════════════════════

class AboutStat(SQLModel, table=True):
    """
    Contoh: value='1,200+', label='Kamera Aktif'
    """
    __tablename__ = "about_stats"

    id      : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    page_id : uuid.UUID = Field(foreign_key="about_pages.id", nullable=False, index=True)
    value   : str       = Field(max_length=50,  nullable=False)
    label   : str       = Field(max_length=100, nullable=False)
    order   : int       = Field(default=0,      nullable=False)

    page : Optional[AboutPage] = Relationship(back_populates="stats")


# ══════════════════════════════════════════════════════════════════════════════
# ABOUT VALUE  (kartu keunggulan / why choose us)
# ══════════════════════════════════════════════════════════════════════════════

class AboutValue(SQLModel, table=True):
    """
    Kartu keunggulan: icon lucide + title + desc
    """
    __tablename__ = "about_values"

    id      : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    page_id : uuid.UUID = Field(foreign_key="about_pages.id", nullable=False, index=True)
    icon    : str       = Field(max_length=60,  nullable=False)   # "lucide:shield-alert"
    title   : str       = Field(max_length=150, nullable=False)
    desc    : str       = Field(nullable=False)
    order   : int       = Field(default=0, nullable=False)

    page : Optional[AboutPage] = Relationship(back_populates="values")


# ══════════════════════════════════════════════════════════════════════════════
# ABOUT GALLERY  (foto swiper hasil kerja lapangan)
# ══════════════════════════════════════════════════════════════════════════════

class AboutGallery(SQLModel, table=True):
    """
    cdn_url = URL publik Cloudflare R2   (untuk <img src>)
    cdn_key = object key R2              (untuk delete_file())
    """
    __tablename__ = "about_gallery"

    id       : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    page_id  : uuid.UUID = Field(foreign_key="about_pages.id", nullable=False, index=True)
    cdn_url  : str       = Field(nullable=False)                 # https://cdn.x.com/about/xxx.webp
    cdn_key  : str       = Field(max_length=300, nullable=False) # about/gallery/xxx.webp
    alt      : str       = Field(max_length=200, nullable=False)
    order    : int       = Field(default=0, nullable=False)
    created_at : datetime = Field(default_factory=_utcnow, nullable=False)

    page : Optional[AboutPage] = Relationship(back_populates="gallery")