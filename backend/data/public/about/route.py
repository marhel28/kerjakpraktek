"""
backend/data/about/router.py
FastAPI router – About Us / Tentang Kami
Menggunakan get_session dari backend.db.main (SQLModel AsyncSession)
────────────────────────────────────────────────────────────────────
GET    /about                       → publik, cache Redis 10 menit
POST   /about                       → buat halaman baru       [admin]
PATCH  /about                       → update partial           [admin]
POST   /about/gallery               → upload gambar ke R2     [admin]
DELETE /about/gallery/{gallery_id}  → hapus gambar            [admin]
PATCH  /about/gallery/reorder       → urutkan ulang swiper    [admin]
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.db.main import get_session                     # ← pakai get_session proyek
# from backend.auth.dependencies import require_admin       # ← aktifkan bila auth siap

from .schema import (
    AboutPageCreate, AboutPageUpdate, AboutPageResponse,
    GalleryUploadResponse, GalleryReorderRequest,
)
from .service import about_service as about_service

router = APIRouter(prefix="/abouts", tags=["About Us"])


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC
# ══════════════════════════════════════════════════════════════════════════════

@router.get(
    "",
    response_model=AboutPageResponse,
    summary="Ambil konten halaman About Us (Redis cached)",
)
async def get_about(session: AsyncSession = Depends(get_session)):
    return await about_service.get_about_page(session)


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "",
    response_model=AboutPageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Buat halaman About Us baru",
)
async def create_about(
    payload: AboutPageCreate,
    session: AsyncSession = Depends(get_session),
    # _: None = Depends(require_admin),
):
    return await about_service.create_about_page(payload, session)


@router.patch(
    "",
    response_model=AboutPageResponse,
    summary="[Admin] Update partial halaman About Us aktif",
)
async def update_about(
    payload: AboutPageUpdate,
    session: AsyncSession = Depends(get_session),
    # _: None = Depends(require_admin),
):
    return await about_service.update_about_page(payload, session)


# ── Gallery ───────────────────────────────────────────────────────────────────

@router.post(
    "/gallery",
    response_model=GalleryUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Upload gambar gallery ke CDN",
)
async def upload_gallery(
    file   : UploadFile     = File(..., description="JPEG/PNG/WebP ≤ 5 MB"),
    alt    : str            = Form(..., description="Caption gambar", max_length=200),
    session: AsyncSession   = Depends(get_session),
    # _: None = Depends(require_admin),
):
    return await about_service.upload_gallery_image(file, alt, session)


@router.delete(
    "/gallery/{gallery_id}",
    summary="[Admin] Hapus gambar gallery",
)
async def delete_gallery(
    gallery_id : UUID,
    session    : AsyncSession = Depends(get_session),
    # _: None = Depends(require_admin),
):
    return await about_service.delete_gallery_image(gallery_id, session)


@router.patch(
    "/gallery/reorder",
    summary="[Admin] Urutkan ulang gambar swiper gallery",
)
async def reorder_gallery(
    payload : GalleryReorderRequest,
    session : AsyncSession = Depends(get_session),
    # _: None = Depends(require_admin),
):
    return await about_service.reorder_gallery(payload, session)