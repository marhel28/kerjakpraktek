"""
models/portfolio.py
Tabel: portfolio_projects, portfolio_images, portfolio_reviews

CATATAN PENTING:
  - Tidak ada 'from __future__ import annotations' — menyebabkan SQLModel
    gagal resolve generic List["X"] pada Relationship.
  - Relationship pakai Mapped[List[...]] dari sqlalchemy.orm agar mapper
    tidak bingung membedakan type hint biasa vs ORM relationship.
"""
import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Enum as SAEnum, Text
from sqlalchemy.orm import Mapped
from sqlmodel import Column, Field, Relationship, SQLModel


# ══════════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════════

class ProjectCategory(str, enum.Enum):
    RESIDENSIAL    = "Residensial"
    KOMERSIAL      = "Komersial"
    RETAIL         = "Retail"
    KORPORAT       = "Korporat"
    FASILITAS_UMUM = "Fasilitas Umum"
    FNB            = "F&B"
    MANUFAKTUR     = "Manufaktur"
    LAINNYA        = "Lainnya"


class ImageRole(str, enum.Enum):
    COVER   = "cover"     # gambar utama card grid
    BEFORE  = "before"    # foto sebelum — case study
    AFTER   = "after"     # foto sesudah — case study
    GALLERY = "gallery"   # foto tambahan


# ══════════════════════════════════════════════════════════════════
# PORTFOLIO PROJECT
# ══════════════════════════════════════════════════════════════════

class PortfolioProject(SQLModel, table=True):
    __tablename__ = "portfolio_projects"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )

    title:        str           = Field(max_length=200)
    location:     str           = Field(max_length=150)
    cameras:      int           = Field(default=0)
    package_slug: Optional[str] = Field(default=None, max_length=100)

    category: ProjectCategory = Field(
        sa_column=Column(
            SAEnum(ProjectCategory, name="projectcategory", create_type=True),
            nullable=False,
        )
    )

    # Case-study fields — hanya diisi untuk project is_featured=True
    client_type: Optional[str] = Field(default=None, max_length=100)
    problem:     Optional[str] = Field(default=None, sa_column=Column("problem",  Text, nullable=True))
    solution:    Optional[str] = Field(default=None, sa_column=Column("solution", Text, nullable=True))
    result:      Optional[str] = Field(default=None, sa_column=Column("result",   Text, nullable=True))

    is_featured: bool = Field(default=False, nullable=False)
    is_active:   bool = Field(default=True,  nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # ── Relationships ────────────────────────────────────────────
    # Mapped[List[...]] wajib agar SQLAlchemy mapper tidak salah
    # mengira ini generic Python type hint biasa.
    images: Mapped[List["PortfolioImage"]] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "PortfolioImage.sort_order",
            "lazy": "selectin",
        },
    )
    reviews: Mapped[List["PortfolioReview"]] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
        },
    )


# ══════════════════════════════════════════════════════════════════
# PORTFOLIO IMAGE
# ══════════════════════════════════════════════════════════════════

class PortfolioImage(SQLModel, table=True):
    __tablename__ = "portfolio_images"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )

    project_id: uuid.UUID = Field(
        foreign_key="portfolio_projects.id",
        nullable=False,
        ondelete="CASCADE",
    )

    url:    str = Field(max_length=500)   # full URL R2
    r2_key: str = Field(max_length=300)   # key bucket untuk delete

    role: ImageRole = Field(
        default=ImageRole.GALLERY,
        sa_column=Column(
            SAEnum(ImageRole, name="imagerole", create_type=True),
            nullable=False,
            # Tidak pakai server_default — default dihandle Python
        ),
    )

    alt_text:    Optional[str] = Field(default=None, max_length=200)
    sort_order:  int           = Field(default=0, nullable=False)
    uploaded_at: datetime      = Field(default_factory=datetime.utcnow, nullable=False)

    # ── Relationships ────────────────────────────────────────────
    project: Mapped[Optional["PortfolioProject"]] = Relationship(back_populates="images")


# ══════════════════════════════════════════════════════════════════
# PORTFOLIO REVIEW
# ══════════════════════════════════════════════════════════════════

class PortfolioReview(SQLModel, table=True):
    __tablename__ = "portfolio_reviews"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )

    # Nullable — review boleh berdiri sendiri tanpa linked project
    project_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="portfolio_projects.id",
        nullable=True,
        ondelete="SET NULL",
    )

    name:   str           = Field(max_length=100)
    role:   Optional[str] = Field(default=None, max_length=100)  # "Pemilik Gudang"
    rating: int           = Field(default=5, ge=1, le=5)
    text:   str           = Field(sa_column=Column("text", Text, nullable=False))

    is_active:  bool     = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # ── Relationships ────────────────────────────────────────────
    project: Mapped[Optional["PortfolioProject"]] = Relationship(back_populates="reviews")