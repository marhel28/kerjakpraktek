"""
services/portfolio_service.py
Business logic: CRUD project, upload/delete gambar, CRUD review.
Cache Redis untuk halaman publik.
"""
from __future__ import annotations

import json
import uuid
import mimetypes
from typing import Optional

from fastapi import UploadFile, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from ..model import (
    PortfolioProject, PortfolioImage, PortfolioReview,
    ImageRole,
)
from ..schema import (
    ProjectCreateRequest, ProjectUpdateRequest,
    ReviewCreateRequest, ReviewUpdateRequest,
    ImageUpdateRequest,
    ImageOut, ProjectOut, ProjectListOut, ReviewOut,
    FeaturedProjectOut, PortfolioPageOut,
)
from backend.db.cdn   import upload_file, delete_file
from backend.db.redis import get_redis_token

# ── Cache config ─────────────────────────────────────────────────
PAGE_CACHE_TTL       = 300   # 5 menit
PROJECT_CACHE_TTL    = 300

PORTFOLIO_PAGE_KEY   = "portfolio:page"
PROJECT_CACHE_PREFIX = "portfolio:project:"

MAX_IMAGES_PER_PROJECT = 10
ALLOWED_CONTENT_TYPES  = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB       = 5


# ══════════════════════════════════════════════════════════════════
# PRIVATE HELPERS
# ══════════════════════════════════════════════════════════════════

def _cover_url(project: PortfolioProject) -> Optional[str]:
    for img in project.images:
        if img.role == ImageRole.COVER:
            return img.url
    return project.images[0].url if project.images else None


def _before_url(project: PortfolioProject) -> Optional[str]:
    return next((img.url for img in project.images if img.role == ImageRole.BEFORE), None)


def _after_url(project: PortfolioProject) -> Optional[str]:
    return next((img.url for img in project.images if img.role == ImageRole.AFTER), None)


async def _invalidate_portfolio_cache() -> None:
    r = get_redis_token()
    await r.delete(PORTFOLIO_PAGE_KEY)
    cursor = 0
    while True:
        cursor, keys = await r.scan(cursor, match=f"{PROJECT_CACHE_PREFIX}*", count=100)
        if keys:
            await r.delete(*keys)
        if cursor == 0:
            break


def _validate_upload(file: UploadFile) -> str:
    ct = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""
    if ct not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipe file tidak didukung: {ct}. Gunakan JPEG/PNG/WebP.",
        )
    return ct


async def _get_project_or_404(project_id: uuid.UUID, db: AsyncSession) -> PortfolioProject:
    q = (
        select(PortfolioProject)
        .where(PortfolioProject.id == project_id)
        .options(
            selectinload(PortfolioProject.images),
            selectinload(PortfolioProject.reviews),
        )
    )
    row = (await db.execute(q)).scalars().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project tidak ditemukan.")
    return row


async def _get_image_or_404(image_id: uuid.UUID, db: AsyncSession) -> PortfolioImage:
    row = (await db.execute(
        select(PortfolioImage).where(PortfolioImage.id == image_id)
    )).scalars().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gambar tidak ditemukan.")
    return row


async def _get_review_or_404(review_id: uuid.UUID, db: AsyncSession) -> PortfolioReview:
    row = (await db.execute(
        select(PortfolioReview).where(PortfolioReview.id == review_id)
    )).scalars().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review tidak ditemukan.")
    return row


# ══════════════════════════════════════════════════════════════════
# PROJECT SERVICE
# ══════════════════════════════════════════════════════════════════

async def get_portfolio_page(db: AsyncSession) -> PortfolioPageOut:
    """Endpoint publik utama — di-cache Redis 5 menit."""
    r = get_redis_token()
    cached = await r.get(PORTFOLIO_PAGE_KEY)
    if cached:
        return PortfolioPageOut(**json.loads(cached))

    # Featured project
    q_featured = (
        select(PortfolioProject)
        .where(PortfolioProject.is_featured == True, PortfolioProject.is_active == True)
        .options(selectinload(PortfolioProject.images))
        .limit(1)
    )
    featured_row = (await db.execute(q_featured)).scalars().first()
    featured = None
    if featured_row:
        featured = FeaturedProjectOut(
            id=featured_row.id,
            client_type=featured_row.client_type,
            title=featured_row.title,
            problem=featured_row.problem,
            solution=featured_row.solution,
            result=featured_row.result,
            before_image=_before_url(featured_row),
            after_image=_after_url(featured_row),
        )

    # Grid semua project aktif
    q_projects = (
        select(PortfolioProject)
        .where(PortfolioProject.is_active == True)
        .options(selectinload(PortfolioProject.images))
        .order_by(PortfolioProject.created_at.desc())
    )
    rows = (await db.execute(q_projects)).scalars().all()
    projects = [
        ProjectListOut(
            id=p.id,
            title=p.title,
            category=p.category,
            location=p.location,
            cameras=p.cameras,
            package_slug=p.package_slug,
            is_featured=p.is_featured,
            cover_image=_cover_url(p),
        )
        for p in rows
    ]

    # Testimonial aktif
    q_reviews = (
        select(PortfolioReview)
        .where(PortfolioReview.is_active == True)
        .order_by(PortfolioReview.created_at.desc())
    )
    reviews = (await db.execute(q_reviews)).scalars().all()
    testimonials = [ReviewOut.model_validate(rv) for rv in reviews]

    page = PortfolioPageOut(featured=featured, projects=projects, testimonials=testimonials)
    await r.set(PORTFOLIO_PAGE_KEY, page.model_dump_json(), ex=PAGE_CACHE_TTL)
    return page


async def list_projects(db: AsyncSession) -> list[ProjectOut]:
    q = (
        select(PortfolioProject)
        .options(
            selectinload(PortfolioProject.images),
            selectinload(PortfolioProject.reviews),
        )
        .order_by(PortfolioProject.created_at.desc())
    )
    rows = (await db.execute(q)).scalars().all()
    return [ProjectOut.model_validate(p) for p in rows]


async def get_project(project_id: uuid.UUID, db: AsyncSession) -> ProjectOut:
    r = get_redis_token()
    cache_key = f"{PROJECT_CACHE_PREFIX}{project_id}"
    cached = await r.get(cache_key)
    if cached:
        return ProjectOut(**json.loads(cached))

    row = await _get_project_or_404(project_id, db)
    out = ProjectOut.model_validate(row)
    await r.set(cache_key, out.model_dump_json(), ex=PROJECT_CACHE_TTL)
    return out


async def create_project(data: ProjectCreateRequest, db: AsyncSession) -> ProjectOut:
    if data.is_featured:
        await db.execute(
            update(PortfolioProject)
            .where(PortfolioProject.is_featured == True)
            .values(is_featured=False)
        )

    project = PortfolioProject(**data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    await _invalidate_portfolio_cache()
    return ProjectOut.model_validate(project)


async def update_project(
    project_id: uuid.UUID, data: ProjectUpdateRequest, db: AsyncSession
) -> ProjectOut:
    project = await _get_project_or_404(project_id, db)
    payload = data.model_dump(exclude_none=True)

    if payload.get("is_featured"):
        await db.execute(
            update(PortfolioProject)
            .where(PortfolioProject.is_featured == True)
            .values(is_featured=False)
        )

    for k, v in payload.items():
        setattr(project, k, v)

    await db.commit()
    await db.refresh(project)
    await _invalidate_portfolio_cache()
    return ProjectOut.model_validate(project)


async def delete_project(project_id: uuid.UUID, db: AsyncSession) -> None:
    project = await _get_project_or_404(project_id, db)
    for img in project.images:
        try:
            await delete_file(img.r2_key)
        except Exception:
            pass
    await db.delete(project)
    await db.commit()
    await _invalidate_portfolio_cache()


# ══════════════════════════════════════════════════════════════════
# IMAGE SERVICE
# ══════════════════════════════════════════════════════════════════

async def upload_project_images(
    project_id: uuid.UUID,
    files: list[UploadFile],
    role: ImageRole,
    db: AsyncSession,
) -> list[ImageOut]:
    project = await _get_project_or_404(project_id, db)

    if len(project.images) + len(files) > MAX_IMAGES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maksimal {MAX_IMAGES_PER_PROJECT} gambar per project.",
        )

    results: list[ImageOut] = []
    for file in files:
        ct = _validate_upload(file)

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File {file.filename} melebihi {MAX_FILE_SIZE_MB}MB.",
            )

        filename = f"{uuid.uuid4()}.webp"
        folder   = f"portfolio/{project_id}/{role.value}"
        r2_key   = f"{folder}/{filename}"

        url = await upload_file(
            file=content,
            folder=folder,
            filename=filename,
            content_type=ct,
        )

        img = PortfolioImage(
            project_id=project_id,
            url=url,          # simpan full URL langsung
            r2_key=r2_key,    # key R2 untuk keperluan delete
            role=role,
            alt_text=file.filename,
            sort_order=len(project.images) + len(results),
        )
        db.add(img)
        await db.flush()   # dapat id tanpa commit dulu
        results.append(ImageOut.model_validate(img))

    await db.commit()
    await _invalidate_portfolio_cache()
    return results


async def update_image(image_id: uuid.UUID, data: ImageUpdateRequest, db: AsyncSession) -> ImageOut:
    img = await _get_image_or_404(image_id, db)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(img, k, v)
    await db.commit()
    await db.refresh(img)
    await _invalidate_portfolio_cache()
    return ImageOut.model_validate(img)


async def delete_image(image_id: uuid.UUID, db: AsyncSession) -> None:
    img = await _get_image_or_404(image_id, db)
    try:
        await delete_file(img.r2_key)
    except Exception:
        pass
    await db.delete(img)
    await db.commit()
    await _invalidate_portfolio_cache()


# ══════════════════════════════════════════════════════════════════
# REVIEW SERVICE
# ══════════════════════════════════════════════════════════════════

async def create_review(data: ReviewCreateRequest, db: AsyncSession) -> ReviewOut:
    if data.project_id:
        await _get_project_or_404(data.project_id, db)

    review = PortfolioReview(**data.model_dump())
    db.add(review)
    await db.commit()
    await db.refresh(review)
    await _invalidate_portfolio_cache()
    return ReviewOut.model_validate(review)


async def list_reviews(
    db: AsyncSession, project_id: Optional[uuid.UUID] = None
) -> list[ReviewOut]:
    q = select(PortfolioReview).order_by(PortfolioReview.created_at.desc())
    if project_id:
        q = q.where(PortfolioReview.project_id == project_id)
    rows = (await db.execute(q)).scalars().all()
    return [ReviewOut.model_validate(r) for r in rows]


async def update_review(
    review_id: uuid.UUID, data: ReviewUpdateRequest, db: AsyncSession
) -> ReviewOut:
    review = await _get_review_or_404(review_id, db)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(review, k, v)
    await db.commit()
    await db.refresh(review)
    await _invalidate_portfolio_cache()
    return ReviewOut.model_validate(review)


async def delete_review(review_id: uuid.UUID, db: AsyncSession) -> None:
    review = await _get_review_or_404(review_id, db)
    await db.delete(review)
    await db.commit()
    await _invalidate_portfolio_cache()