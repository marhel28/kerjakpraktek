"""
routes/portfolio.py  (atau portfolio/route.py — sesuaikan dengan struktur folder)

Prefix : /portfolio
Tags   : ["Portfolio"]

PUBLIC  (tanpa auth)
  GET  /portfolio/page               → PortfolioPageOut (Redis-cached)
  GET  /portfolio/projects/{id}      → ProjectOut

ADMIN   (tambahkan dependency auth di AdminDep)
  GET    /portfolio/projects              → list semua project
  POST   /portfolio/projects              → buat project baru
  PATCH  /portfolio/projects/{id}         → update project
  DELETE /portfolio/projects/{id}         → hapus project + semua gambar R2

  POST   /portfolio/projects/{id}/images  → upload 1–10 gambar
  PATCH  /portfolio/images/{id}           → update meta gambar
  DELETE /portfolio/images/{id}           → hapus gambar R2 + DB

  GET    /portfolio/reviews               → list semua review
  POST   /portfolio/reviews               → tambah review
  PATCH  /portfolio/reviews/{id}          → edit review
  DELETE /portfolio/reviews/{id}          → hapus review
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import (
    APIRouter, Depends, File, Form,
    HTTPException, Query, UploadFile, status,
)
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.db.main import get_session
from .model import ImageRole
from .schema import (
    ImageOut, ImageUpdateRequest,
    ProjectCreateRequest, ProjectOut, ProjectUpdateRequest,
    ReviewCreateRequest, ReviewOut, ReviewUpdateRequest,
    PortfolioPageOut,
)
from .services import portfolio_service as svc

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# ── Ganti dengan dependency auth kamu, misal: Depends(get_current_admin) ──
# AdminDep = Depends(get_current_admin)


# ══════════════════════════════════════════════════════════════════
# PUBLIC
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/page",
    response_model=PortfolioPageOut,
    summary="Halaman portofolio publik (featured + projects + testimonials)",
)
async def portfolio_page(db: AsyncSession = Depends(get_session)):
    """
    Satu endpoint untuk semua kebutuhan halaman /portfolio di Nuxt.
    - Featured project (case study before/after)
    - Grid semua project aktif
    - Testimonial aktif
    Di-cache Redis 5 menit, otomatis invalidate saat ada perubahan data.
    """
    return await svc.get_portfolio_page(db)


@router.get(
    "/projects/{project_id}",
    response_model=ProjectOut,
    summary="Detail satu project (publik)",
)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    return await svc.get_project(project_id, db)


# ══════════════════════════════════════════════════════════════════
# ADMIN — PROJECTS
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/projects",
    response_model=List[ProjectOut],
    summary="[Admin] List semua project",
)
async def list_projects(db: AsyncSession = Depends(get_session)):
    return await svc.list_projects(db)


@router.post(
    "/projects",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Buat project baru",
)
async def create_project(
    data: ProjectCreateRequest,
    db: AsyncSession = Depends(get_session),
):
    return await svc.create_project(data, db)


@router.patch(
    "/projects/{project_id}",
    response_model=ProjectOut,
    summary="[Admin] Update project",
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdateRequest,
    db: AsyncSession = Depends(get_session),
):
    return await svc.update_project(project_id, data, db)


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Hapus project beserta semua gambarnya dari R2",
)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    await svc.delete_project(project_id, db)


# ══════════════════════════════════════════════════════════════════
# ADMIN — IMAGES
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/projects/{project_id}/images",
    response_model=List[ImageOut],
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Upload 1–10 gambar ke project",
)
async def upload_images(
    project_id: uuid.UUID,
    files: List[UploadFile] = File(
        ..., description="Maksimal 10 file (JPEG/PNG/WebP, max 5 MB per file)"
    ),
    role: ImageRole = Form(
        ImageRole.GALLERY,
        description="cover | before | after | gallery",
    ),
    db: AsyncSession = Depends(get_session),
):
    """
    Upload beberapa gambar sekaligus ke satu project.
    - `role=cover`   → gambar utama yang muncul di card grid
    - `role=before`  → foto sebelum untuk case study (featured)
    - `role=after`   → foto sesudah untuk case study (featured)
    - `role=gallery` → foto tambahan
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tidak ada file yang dikirim.",
        )
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maksimal 10 file per request.",
        )
    return await svc.upload_project_images(project_id, files, role, db)


@router.patch(
    "/images/{image_id}",
    response_model=ImageOut,
    summary="[Admin] Update meta gambar (role, alt_text, sort_order)",
)
async def update_image(
    image_id: uuid.UUID,
    data: ImageUpdateRequest,
    db: AsyncSession = Depends(get_session),
):
    return await svc.update_image(image_id, data, db)


@router.delete(
    "/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Hapus satu gambar dari R2 dan DB",
)
async def delete_image(
    image_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    await svc.delete_image(image_id, db)


# ══════════════════════════════════════════════════════════════════
# ADMIN — REVIEWS / TESTIMONIALS
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/reviews",
    response_model=List[ReviewOut],
    summary="[Admin] List semua review",
)
async def list_reviews(
    project_id: Optional[uuid.UUID] = Query(
        None, description="Filter review berdasarkan project"
    ),
    db: AsyncSession = Depends(get_session),
):
    return await svc.list_reviews(db, project_id)


@router.post(
    "/reviews",
    response_model=ReviewOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Tambah review / testimonial",
)
async def create_review(
    data: ReviewCreateRequest,
    db: AsyncSession = Depends(get_session),
):
    return await svc.create_review(data, db)


@router.patch(
    "/reviews/{review_id}",
    response_model=ReviewOut,
    summary="[Admin] Edit review",
)
async def update_review(
    review_id: uuid.UUID,
    data: ReviewUpdateRequest,
    db: AsyncSession = Depends(get_session),
):
    return await svc.update_review(review_id, data, db)


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Hapus review",
)
async def delete_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    await svc.delete_review(review_id, db)