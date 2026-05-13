"""
schemas/portfolio.py
Request / Response schema untuk Portfolio Projects, Images, Reviews
"""
from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from .model import ImageRole, ProjectCategory


# ══════════════════════════════════════════════════════════════════
# IMAGE SCHEMAS
# ══════════════════════════════════════════════════════════════════

class ImageOut(BaseModel):
    id         : UUID
    url        : str
    r2_key     : str
    role       : ImageRole
    alt_text   : Optional[str]
    sort_order : int
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class ImageUpdateRequest(BaseModel):
    """Hanya field yang boleh di-PATCH setelah upload."""
    role      : Optional[ImageRole] = None
    alt_text  : Optional[str]       = Field(None, max_length=200)
    sort_order: Optional[int]       = None


# ══════════════════════════════════════════════════════════════════
# REVIEW SCHEMAS
# ══════════════════════════════════════════════════════════════════

class ReviewCreateRequest(BaseModel):
    project_id: Optional[UUID] = None
    name      : str = Field(..., min_length=2, max_length=100)
    role      : Optional[str] = Field(None, max_length=100)
    rating    : int = Field(..., ge=1, le=5)
    text      : str = Field(..., min_length=5, max_length=1000)


class ReviewUpdateRequest(BaseModel):
    name     : Optional[str] = Field(None, min_length=2, max_length=100)
    role     : Optional[str] = Field(None, max_length=100)
    rating   : Optional[int] = Field(None, ge=1, le=5)
    text     : Optional[str] = Field(None, min_length=5, max_length=1000)
    is_active: Optional[bool] = None


class ReviewOut(BaseModel):
    id        : UUID
    project_id: Optional[UUID]
    name      : str
    role      : Optional[str]
    rating    : int
    text      : str
    is_active : bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════
# PROJECT SCHEMAS
# ══════════════════════════════════════════════════════════════════

class ProjectCreateRequest(BaseModel):
    title       : str = Field(..., min_length=3, max_length=200)
    category    : ProjectCategory
    location    : str = Field(..., min_length=2, max_length=150)
    cameras     : int = Field(..., ge=0)
    package_slug: Optional[str] = Field(None, max_length=100)

    # Case-study fields
    client_type : Optional[str] = Field(None, max_length=100)
    problem     : Optional[str] = None
    solution    : Optional[str] = None
    result      : Optional[str] = None
    is_featured : bool = False


class ProjectUpdateRequest(BaseModel):
    title       : Optional[str] = Field(None, min_length=3, max_length=200)
    category    : Optional[ProjectCategory] = None
    location    : Optional[str] = Field(None, min_length=2, max_length=150)
    cameras     : Optional[int] = Field(None, ge=0)
    package_slug: Optional[str] = Field(None, max_length=100)
    client_type : Optional[str] = Field(None, max_length=100)
    problem     : Optional[str] = None
    solution    : Optional[str] = None
    result      : Optional[str] = None
    is_featured : Optional[bool] = None
    is_active   : Optional[bool] = None


class ProjectOut(BaseModel):
    """Response lengkap dengan relasi images & reviews."""
    id          : UUID
    title       : str
    category    : ProjectCategory
    location    : str
    cameras     : int
    package_slug: Optional[str]
    client_type : Optional[str]
    problem     : Optional[str]
    solution    : Optional[str]
    result      : Optional[str]
    is_featured : bool
    is_active   : bool
    created_at  : datetime
    updated_at  : Optional[datetime]
    images      : List[ImageOut] = []
    reviews     : List[ReviewOut] = []

    model_config = {"from_attributes": True}


class ProjectListOut(BaseModel):
    """Response ringkas untuk grid galeri (tanpa reviews)."""
    id          : UUID
    title       : str
    category    : ProjectCategory
    location    : str
    cameras     : int
    package_slug: Optional[str]
    is_featured : bool
    cover_image : Optional[str] = None  # URL cover, di-resolve di service

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════
# PORTFOLIO PAGE (agregat untuk halaman frontend)
# ══════════════════════════════════════════════════════════════════

class FeaturedProjectOut(BaseModel):
    """Khusus section case-study di atas halaman."""
    id         : UUID
    client_type: Optional[str]
    title      : str
    problem    : Optional[str]
    solution   : Optional[str]
    result     : Optional[str]
    before_image: Optional[str] = None  # URL gambar role=before
    after_image : Optional[str] = None  # URL gambar role=after

    model_config = {"from_attributes": True}


class PortfolioPageOut(BaseModel):
    """Satu endpoint untuk semua kebutuhan halaman /portfolio."""
    featured    : Optional[FeaturedProjectOut]
    projects    : List[ProjectListOut]
    testimonials: List[ReviewOut]