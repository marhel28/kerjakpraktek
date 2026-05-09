"""
backend/services.py
═══════════════════════════════════════════════════════════════════
Tugas file ini:
  - Semua business logic portofolio CCTV
  - Tiga service class:
      • ProjectService     → CRUD project + media gallery
      • TestimonialService → CRUD + moderasi testimoni
      • PortfolioPageService → aggregated data halaman portofolio

Dependency:
  - DB query   : SQLAlchemy AsyncSession
  - Cache      : backend.db.redis  (semua helper cache langsung diimport)
  - CDN        : backend.db.cdn    (upload / delete / public_url)

Pola cache:
  1. Cek cache dulu (redis helper)
  2. Jika hit → return langsung (tanpa sentuh DB)
  3. Jika miss → query DB → simpan ke cache → return
  4. Setiap mutasi (create/update/delete) → bust cache terkait
═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .model import (
    MediaType, Project, ProjectCategory,
    ProjectMedia, Testimonial, TestimonialStatus,
)
from .schema import (
    MediaOut, MediaRegisterIn,
    PaginatedProjects, PaginatedTestimonials,
    PortfolioPageOut,
    ProjectCardOut, ProjectCreateIn, ProjectDetailOut, ProjectUpdateIn,
    PresignedUploadOut,
    TestimonialAdminUpdateIn, TestimonialCreateIn, TestimonialOut,
)

# ── Infrastructure imports (pattern dari db/ layer) ───────────────
import backend.db.cdn as cdn
import backend.db.redis as cache

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text)


# ─────────────────────────────────────────────────────────────────
# PROJECT SERVICE
# ─────────────────────────────────────────────────────────────────

class ProjectService:
    """CRUD project instalasi CCTV + manajemen media gallery."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── ORM → Schema mappers ──────────────────────────────────────

    @staticmethod
    def _media_out(m: ProjectMedia) -> MediaOut:
        return MediaOut(
            id=m.id,
            media_type=m.media_type,
            url=cdn.public_url(m.cdn_key),   # cdn.public_url() dari db/cdn.py
            alt_text=m.alt_text,
            caption=m.caption,
            is_before=m.is_before,
            display_order=m.display_order,
        )

    @staticmethod
    def _to_card(p: Project) -> ProjectCardOut:
        return ProjectCardOut(
            id=p.id,
            title=p.title,
            slug=p.slug,
            category=p.category,
            location=p.location,
            cameras=p.cameras,
            package_slug=p.package_slug,
            cover_url=cdn.public_url(p.cover_image_key) if p.cover_image_key else None,
            is_featured=p.is_featured,
            display_order=p.display_order,
            created_at=p.created_at,
        )

    @staticmethod
    def _to_detail(p: Project) -> ProjectDetailOut:
        return ProjectDetailOut(
            id=p.id,
            title=p.title,
            slug=p.slug,
            category=p.category,
            location=p.location,
            cameras=p.cameras,
            package_slug=p.package_slug,
            cover_url=cdn.public_url(p.cover_image_key) if p.cover_image_key else None,
            is_featured=p.is_featured,
            display_order=p.display_order,
            created_at=p.created_at,
            problem=p.problem,
            solution=p.solution,
            result=p.result,
            media=[ProjectService._media_out(m) for m in (p.media or [])],
        )

    # ── Slug uniqueness ───────────────────────────────────────────

    async def _unique_slug(self, base: str, exclude_id: int = 0) -> str:
        slug = _slugify(base)
        candidate = slug
        counter = 1
        while True:
            q = select(Project).where(Project.slug == candidate)
            if exclude_id:
                q = q.where(Project.id != exclude_id)
            if not (await self.db.execute(q)).scalar_one_or_none():
                return candidate
            candidate = f"{slug}-{counter}"
            counter += 1

    # ── LIST (galeri) ─────────────────────────────────────────────

    async def list_projects(
        self,
        category: Optional[ProjectCategory] = None,
        page: int = 1,
        size: int = 12,
        published_only: bool = True,
    ) -> PaginatedProjects:
        # 1. Cek cache
        cat_key = category.value if category else "all"
        cached = await cache.cache_get_project_list(cat_key, page, size)
        if cached:
            return PaginatedProjects(**cached)

        # 2. Query DB
        q = (
            select(Project)
            .order_by(Project.display_order, Project.created_at.desc())
        )
        if published_only:
            q = q.where(Project.is_published == True)
        if category:
            q = q.where(Project.category == category)

        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        items_orm = (await self.db.execute(q.offset((page - 1) * size).limit(size))).scalars().all()
        items = [self._to_card(p) for p in items_orm]

        # 3. Simpan cache + return
        result = PaginatedProjects(total=total, page=page, size=size, items=items)
        await cache.cache_set_project_list(cat_key, page, size, result.model_dump())
        return result

    # ── DETAIL ────────────────────────────────────────────────────

    async def get_project(self, id_or_slug: int | str) -> Optional[ProjectDetailOut]:
        # 1. Cek cache
        cached = await cache.cache_get_project_detail(id_or_slug)
        if cached:
            return ProjectDetailOut(**cached)

        # 2. Query DB
        q = select(Project).options(selectinload(Project.media))
        if isinstance(id_or_slug, int):
            q = q.where(Project.id == id_or_slug)
        else:
            q = q.where(Project.slug == id_or_slug)
        project = (await self.db.execute(q)).scalar_one_or_none()
        if not project:
            return None

        # 3. Simpan cache + return
        out = self._to_detail(project)
        await cache.cache_set_project_detail(id_or_slug, out.model_dump())
        return out

    # ── FEATURED ──────────────────────────────────────────────────

    async def get_featured(self) -> Optional[ProjectDetailOut]:
        cached = await cache.cache_get_featured()
        if cached:
            return ProjectDetailOut(**cached)

        q = (
            select(Project)
            .where(Project.is_featured == True, Project.is_published == True)
            .options(selectinload(Project.media))
            .order_by(Project.display_order)
            .limit(1)
        )
        project = (await self.db.execute(q)).scalar_one_or_none()
        if not project:
            return None

        out = self._to_detail(project)
        await cache.cache_set_featured(out.model_dump())
        return out

    # ── CREATE ────────────────────────────────────────────────────

    async def create_project(self, payload: ProjectCreateIn) -> ProjectDetailOut:
        slug = await self._unique_slug(payload.title)
        project = Project(slug=slug, **payload.model_dump())
        self.db.add(project)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(project)

        out = self._to_detail(project)
        await cache.bust_project_cache(project.id, slug)
        return out

    # ── UPDATE ────────────────────────────────────────────────────

    async def update_project(
        self, project_id: int, payload: ProjectUpdateIn
    ) -> Optional[ProjectDetailOut]:
        q = select(Project).where(Project.id == project_id).options(selectinload(Project.media))
        project = (await self.db.execute(q)).scalar_one_or_none()
        if not project:
            return None

        data = payload.model_dump(exclude_none=True)
        if "title" in data:
            data["slug"] = await self._unique_slug(data["title"], exclude_id=project_id)
        for k, v in data.items():
            setattr(project, k, v)
        project.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(project)
        await cache.bust_project_cache(project.id, project.slug)
        return self._to_detail(project)

    # ── SET COVER IMAGE ───────────────────────────────────────────

    async def set_cover_image(self, project_id: int, new_cdn_key: str) -> bool:
        """
        Set cover image dari CDN key yang sudah diupload.
        Hapus cover lama dari R2 jika berbeda.
        """
        project = (await self.db.execute(
            select(Project).where(Project.id == project_id)
        )).scalar_one_or_none()
        if not project:
            return False

        # Hapus cover lama dari CDN
        if project.cover_image_key and project.cover_image_key != new_cdn_key:
            await cdn.delete_file(project.cover_image_key)   # cdn.delete_file() dari db/cdn.py

        project.cover_image_key = new_cdn_key
        project.updated_at = datetime.utcnow()
        await self.db.commit()
        await cache.bust_project_cache(project_id, project.slug)
        return True

    # ── DELETE PROJECT ────────────────────────────────────────────

    async def delete_project(self, project_id: int) -> bool:
        """
        Hapus project + semua media dari DB.
        Hapus semua CDN object secara batch (cdn.delete_many).
        """
        q = select(Project).where(Project.id == project_id).options(selectinload(Project.media))
        project = (await self.db.execute(q)).scalar_one_or_none()
        if not project:
            return False

        # Kumpulkan semua CDN key sebelum delete DB
        keys: list[str] = [m.cdn_key for m in project.media if m.cdn_key]
        if project.cover_image_key:
            keys.append(project.cover_image_key)

        slug = project.slug
        await self.db.delete(project)
        await self.db.commit()

        # Hapus batch dari CDN setelah DB commit (tidak blocking response)
        if keys:
            await cdn.delete_many(keys)   # cdn.delete_many() dari db/cdn.py

        await cache.bust_project_cache(project_id, slug)
        return True

    # ── MEDIA: PRESIGN UPLOAD ─────────────────────────────────────

    async def presign_media_upload(
        self, project_id: int, filename: str, is_before: bool = False
    ) -> PresignedUploadOut:
        """
        Buat presigned PUT URL untuk client-side upload ke R2.
        cdn_key dibangun pakai helper dari db/cdn.py.
        """
        cdn_key = cdn.key_project_gallery(project_id, is_before=is_before)
        result = await cdn.generate_upload_url(cdn_key=cdn_key)  # db/cdn.py
        return PresignedUploadOut(**result)

    async def presign_cover_upload(self, project_id: int) -> PresignedUploadOut:
        cdn_key = cdn.key_project_cover(project_id)
        result = await cdn.generate_upload_url(cdn_key=cdn_key)
        return PresignedUploadOut(**result)

    # ── MEDIA: REGISTER AFTER UPLOAD ─────────────────────────────

    async def add_media(
        self, project_id: int, payload: MediaRegisterIn
    ) -> MediaOut:
        """
        Daftarkan media ke DB setelah client sukses upload ke CDN.
        cdn_key dari payload.cdn_key (berasal dari response presign).
        """
        media = ProjectMedia(
            project_id=project_id,
            cdn_key=payload.cdn_key,
            media_type=payload.media_type,
            alt_text=payload.alt_text,
            caption=payload.caption,
            is_before=payload.is_before,
            display_order=payload.display_order,
        )
        self.db.add(media)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(media)

        # Bust cache detail project
        project = (await self.db.execute(
            select(Project).where(Project.id == project_id)
        )).scalar_one_or_none()
        if project:
            await cache.bust_project_cache(project_id, project.slug)

        return self._media_out(media)

    # ── MEDIA: DELETE ─────────────────────────────────────────────

    async def delete_media(self, media_id: int) -> bool:
        """Hapus satu media dari DB dan CDN."""
        media = (await self.db.execute(
            select(ProjectMedia).where(ProjectMedia.id == media_id)
        )).scalar_one_or_none()
        if not media:
            return False

        cdn_key    = media.cdn_key
        project_id = media.project_id
        await self.db.delete(media)
        await self.db.commit()

        await cdn.delete_file(cdn_key)   # db/cdn.py

        project = (await self.db.execute(
            select(Project).where(Project.id == project_id)
        )).scalar_one_or_none()
        if project:
            await cache.bust_project_cache(project_id, project.slug)

        return True


# ─────────────────────────────────────────────────────────────────
# TESTIMONIAL SERVICE
# ─────────────────────────────────────────────────────────────────

class TestimonialService:
    """CRUD + moderasi testimoni pelanggan."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _to_out(t: Testimonial) -> TestimonialOut:
        return TestimonialOut(
            id=t.id,
            project_id=t.project_id,
            name=t.name,
            role=t.role,
            rating=t.rating,
            text=t.text,
            avatar_url=cdn.public_url(t.avatar_key) if t.avatar_key else None,
            status=t.status,
            is_featured=t.is_featured,
            display_order=t.display_order,
            created_at=t.created_at,
        )

    # ── LIST ──────────────────────────────────────────────────────

    async def list_testimonials(
        self,
        status: Optional[TestimonialStatus] = TestimonialStatus.APPROVED,
        featured_only: bool = False,
        page: int = 1,
        size: int = 12,
    ) -> PaginatedTestimonials:
        status_key = status.value if status else "all"
        cached = await cache.cache_get_testimonial_list(status_key, featured_only, page, size)
        if cached:
            return PaginatedTestimonials(**cached)

        q = select(Testimonial).order_by(
            Testimonial.display_order, Testimonial.created_at.desc()
        )
        if status:
            q = q.where(Testimonial.status == status)
        if featured_only:
            q = q.where(Testimonial.is_featured == True)

        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        items_orm = (await self.db.execute(q.offset((page - 1) * size).limit(size))).scalars().all()
        items = [self._to_out(t) for t in items_orm]

        result = PaginatedTestimonials(total=total, page=page, size=size, items=items)
        await cache.cache_set_testimonial_list(status_key, featured_only, page, size, result.model_dump())
        return result

    # ── CREATE (publik) ───────────────────────────────────────────

    async def create_testimonial(self, payload: TestimonialCreateIn) -> TestimonialOut:
        """Status selalu PENDING dari publik — tidak auto-approved."""
        testi = Testimonial(
            **payload.model_dump(),
            status=TestimonialStatus.PENDING,
        )
        self.db.add(testi)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(testi)
        # Tidak bust cache — status PENDING tidak tampil publik
        return self._to_out(testi)

    # ── MODERATE (admin) ──────────────────────────────────────────

    async def moderate_testimonial(
        self, testi_id: int, payload: TestimonialAdminUpdateIn
    ) -> Optional[TestimonialOut]:
        testi = (await self.db.execute(
            select(Testimonial).where(Testimonial.id == testi_id)
        )).scalar_one_or_none()
        if not testi:
            return None

        for k, v in payload.model_dump(exclude_none=True).items():
            setattr(testi, k, v)
        testi.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(testi)
        await cache.bust_testimonial_cache()   # db/redis.py
        return self._to_out(testi)

    # ── DELETE ────────────────────────────────────────────────────

    async def delete_testimonial(self, testi_id: int) -> bool:
        testi = (await self.db.execute(
            select(Testimonial).where(Testimonial.id == testi_id)
        )).scalar_one_or_none()
        if not testi:
            return False

        if testi.avatar_key:
            await cdn.delete_file(testi.avatar_key)   # db/cdn.py

        await self.db.delete(testi)
        await self.db.commit()
        await cache.bust_testimonial_cache()
        return True

    # ── PRESIGN AVATAR UPLOAD ─────────────────────────────────────

    async def presign_avatar_upload(self) -> PresignedUploadOut:
        cdn_key = cdn.key_testimonial_avatar()   # db/cdn.py
        result = await cdn.generate_upload_url(cdn_key=cdn_key)
        return PresignedUploadOut(**result)


# ─────────────────────────────────────────────────────────────────
# PORTFOLIO PAGE SERVICE  (aggregated)
# ─────────────────────────────────────────────────────────────────

class PortfolioPageService:
    """
    Menggabungkan featured + galeri + testimoni dalam satu call.
    Dipakai GET /portfolio → langsung dikonsumsi useAsyncData() di Vue.
    Cache di level ini (portfolio page) menggunakan TTL_PORTFOLIO_PAGE.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._proj  = ProjectService(db)
        self._testi = TestimonialService(db)

    async def get_page_data(self) -> PortfolioPageOut:
        # 1. Cek cache portfolio page (aggregated)
        cached = await cache.cache_get_portfolio_page()
        if cached:
            return PortfolioPageOut(**cached)

        # 2. Jalankan 3 query paralel — asyncio.gather
        featured, projects_page, testi_page = await asyncio.gather(
            self._proj.get_featured(),
            self._proj.list_projects(page=1, size=6, published_only=True),
            self._testi.list_testimonials(
                status=TestimonialStatus.APPROVED,
                featured_only=True,
                page=1,
                size=3,
            ),
        )

        out = PortfolioPageOut(
            featured=featured,
            projects=projects_page.items,
            testimonials=testi_page.items,
        )

        # 3. Simpan cache + return
        await cache.cache_set_portfolio_page(out.model_dump())
        return out