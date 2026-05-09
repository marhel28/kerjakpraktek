"""
models/portfolio.py
Tabel:  portfolio_projects, portfolio_images, portfolio_reviews
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Boolean,
    DateTime, ForeignKey, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.db.database import Base   # sesuaikan import Base kamu
import enum


# ── Enum Kategori ────────────────────────────────────────────────────────────
class ProjectCategory(str, enum.Enum):
    RESIDENSIAL    = "Residensial"
    KOMERSIAL      = "Komersial"
    RETAIL         = "Retail"
    KORPORAT       = "Korporat"
    FASILITAS_UMUM = "Fasilitas Umum"
    FNB            = "F&B"
    MANUFAKTUR     = "Manufaktur"
    LAINNYA        = "Lainnya"


# ── Portfolio Project ─────────────────────────────────────────────────────────
class PortfolioProject(Base):
    __tablename__ = "portfolio_projects"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title        = Column(String(200), nullable=False)
    category     = Column(SAEnum(ProjectCategory), nullable=False)
    location     = Column(String(150), nullable=False)
    cameras      = Column(Integer, nullable=False, default=0)
    package_slug = Column(String(100), nullable=True)   # link ke halaman paket

    # Case-study fields (nullable — hanya untuk project featured)
    client_type  = Column(String(100), nullable=True)
    problem      = Column(Text, nullable=True)
    solution     = Column(Text, nullable=True)
    result       = Column(Text, nullable=True)
    is_featured  = Column(Boolean, default=False, nullable=False)

    is_active    = Column(Boolean, default=True, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    images  = relationship(
        "PortfolioImage", back_populates="project",
        cascade="all, delete-orphan", order_by="PortfolioImage.sort_order"
    )
    reviews = relationship(
        "PortfolioReview", back_populates="project",
        cascade="all, delete-orphan"
    )


# ── Portfolio Image ───────────────────────────────────────────────────────────
class ImageRole(str, enum.Enum):
    COVER  = "cover"    # gambar utama card
    BEFORE = "before"   # foto before (case study)
    AFTER  = "after"    # foto after  (case study)
    GALLERY = "gallery" # foto tambahan


class PortfolioImage(Base):
    __tablename__ = "portfolio_images"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("portfolio_projects.id", ondelete="CASCADE"),
        nullable=False
    )
    url        = Column(String(500), nullable=False)   # URL R2 lengkap
    r2_key     = Column(String(300), nullable=False)   # key di bucket untuk delete
    role       = Column(SAEnum(ImageRole), default=ImageRole.GALLERY, nullable=False)
    alt_text   = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("PortfolioProject", back_populates="images")


# ── Portfolio Review ──────────────────────────────────────────────────────────
class PortfolioReview(Base):
    __tablename__ = "portfolio_reviews"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("portfolio_projects.id", ondelete="SET NULL"),
        nullable=True   # review global boleh tanpa project
    )
    name       = Column(String(100), nullable=False)
    role       = Column(String(100), nullable=True)   # "Pemilik Gudang", dll.
    rating     = Column(Integer, nullable=False, default=5)  # 1–5
    text       = Column(Text, nullable=False)
    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("PortfolioProject", back_populates="reviews")