"""
backend/data/about/service.py
Business logic About Us:
  - CRUD page (hero, stats, values, CTA)
  - Upload / delete gallery → Cloudflare R2
  - Cache JSON di Redis Dragonfly (TTL 10 menit)
  - Invalidasi cache otomatis setiap write
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..model import AboutPage, AboutStat, AboutValue, AboutGallery
from ..schema import (
    AboutPageCreate, AboutPageUpdate,
    AboutPageResponse, GalleryUploadResponse,
    GalleryReorderRequest,
)
from backend.db.cdn import upload_file, delete_file
from backend.db.redis import get_redis_token

# ─── Konstanta ────────────────────────────────────────────────────────────────
ABOUT_CACHE_KEY   = "about:active_page"
ABOUT_CACHE_TTL   = 600   # 10 menit
ALLOWED_IMG_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMG_SIZE_MB   = 5


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ══════════════════════════════════════════════════════════════════════════════
# PRIVATE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

async def _get_active_page(session: AsyncSession) -> AboutPage | None:
    """Ambil halaman aktif + semua relasi via selectinload (async-safe)."""
    result = await session.exec(
        select(AboutPage)
        .where(AboutPage.is_active == True)  # noqa: E712
        .options(
            selectinload(AboutPage.stats),
            selectinload(AboutPage.values),
            selectinload(AboutPage.gallery),
        )
        .limit(1)
    )
    return result.first()


async def _load_full_page(session: AsyncSession, page_id: uuid.UUID) -> AboutPage:
    """Reload page dengan relasi lengkap setelah commit (async-safe)."""
    result = await session.exec(
        select(AboutPage)
        .where(AboutPage.id == page_id)
        .options(
            selectinload(AboutPage.stats),
            selectinload(AboutPage.values),
            selectinload(AboutPage.gallery),
        )
    )
    return result.one()


async def _invalidate_cache() -> None:
    await get_redis_token().delete(ABOUT_CACHE_KEY)


async def _validate_image(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_IMG_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipe file tidak didukung: {file.content_type}. Gunakan JPEG/PNG/WebP.",
        )
    data = await file.read()
    if len(data) > MAX_IMG_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Ukuran file melebihi {MAX_IMG_SIZE_MB} MB.",
        )
    return data


def _build_response(page: AboutPage) -> AboutPageResponse:
    """Konversi ORM → Pydantic response (sorted by order)."""
    page.stats   = sorted(page.stats,   key=lambda x: x.order)
    page.values  = sorted(page.values,  key=lambda x: x.order)
    page.gallery = sorted(page.gallery, key=lambda x: x.order)
    return AboutPageResponse.model_validate(page)


# ══════════════════════════════════════════════════════════════════════════════
# GET (dengan cache Redis)
# ══════════════════════════════════════════════════════════════════════════════

async def get_about_page(session: AsyncSession) -> AboutPageResponse:
    """
    Redis hit  → langsung kembalikan (cepat, ~1 ms)
    Redis miss → query DB → simpan cache → kembalikan
    """
    r = get_redis_token()
    cached = await r.get(ABOUT_CACHE_KEY)
    if cached:
        return AboutPageResponse.model_validate_json(cached)

    page = await _get_active_page(session)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Halaman About Us belum dikonfigurasi.",
        )

    resp = _build_response(page)
    await r.set(ABOUT_CACHE_KEY, resp.model_dump_json(), ex=ABOUT_CACHE_TTL)
    return resp


# ══════════════════════════════════════════════════════════════════════════════
# CREATE
# ══════════════════════════════════════════════════════════════════════════════

async def create_about_page(
    payload: AboutPageCreate,
    session: AsyncSession,
) -> AboutPageResponse:
    """
    Buat versi halaman baru → otomatis nonaktifkan yang lama.
    """
    # Nonaktifkan semua halaman aktif
    old_pages_result = await session.exec(
        select(AboutPage).where(AboutPage.is_active == True)  # noqa: E712
    )
    for old in old_pages_result.all():
        old.is_active = False
        session.add(old)

    # Buat halaman baru
    page = AboutPage(
        hero_badge_text    = payload.hero_badge_text,
        hero_heading       = payload.hero_heading,
        hero_subheading    = payload.hero_subheading,
        cta_heading        = payload.cta_heading,
        cta_body           = payload.cta_body,
        cta_primary_text   = payload.cta_primary_text,
        cta_secondary_text = payload.cta_secondary_text,
        cta_secondary_url  = payload.cta_secondary_url,
        is_active          = True,
    )
    session.add(page)
    await session.flush()   # dapatkan page.id sebelum insert children

    # Insert stats
    for i, s in enumerate(payload.stats):
        session.add(AboutStat(page_id=page.id, order=i, **s.model_dump(exclude={"order"})))

    # Insert values
    for i, v in enumerate(payload.values):
        session.add(AboutValue(page_id=page.id, order=i, **v.model_dump(exclude={"order"})))

    await session.commit()

    page = await _load_full_page(session, page.id)
    await _invalidate_cache()
    return _build_response(page)


# ══════════════════════════════════════════════════════════════════════════════
# UPDATE (PATCH)
# ══════════════════════════════════════════════════════════════════════════════

async def update_about_page(
    payload: AboutPageUpdate,
    session: AsyncSession,
) -> AboutPageResponse:
    """
    Partial update halaman aktif.
    Jika stats/values dikirim → replace seluruhnya.
    """
    page = await _get_active_page(session)
    if not page:
        raise HTTPException(status_code=404, detail="Halaman About Us tidak ditemukan.")

    # Update scalar fields
    scalar_fields = [
        "hero_badge_text", "hero_heading", "hero_subheading",
        "cta_heading", "cta_body", "cta_primary_text",
        "cta_secondary_text", "cta_secondary_url",
    ]
    for field in scalar_fields:
        val = getattr(payload, field)
        if val is not None:
            setattr(page, field, val)

    page.updated_at = _utcnow()
    session.add(page)

    # ── Replace Stats ─────────────────────────────────────────────────────────
    if payload.stats is not None:
        # 1. Hapus dari database menggunakan list memori yang sudah di-load
        for old_stat in list(page.stats):
            await session.delete(old_stat)
            
        # 2. Putuskan ikatan di memori induk agar SQLAlchemy tidak bingung
        page.stats.clear()
        
        # 3. Pastikan proses delete selesai sebelum insert baru
        await session.flush()

        # 4. Masukkan data baru
        for i, s in enumerate(payload.stats):
            new_stat = AboutStat(page_id=page.id, order=i, **s.model_dump(exclude={"order"}))
            session.add(new_stat)
            page.stats.append(new_stat) # Sinkronkan kembali ke memori

    # ── Replace Values ────────────────────────────────────────────────────────
    if payload.values is not None:
        for old_value in list(page.values):
            await session.delete(old_value)
            
        page.values.clear()
        
        await session.flush()

        for i, v in enumerate(payload.values):
            new_val = AboutValue(page_id=page.id, order=i, **v.model_dump(exclude={"order"}))
            session.add(new_val)
            page.values.append(new_val)

    # ── Finalize ──────────────────────────────────────────────────────────────
    await session.commit()

    page = await _load_full_page(session, page.id)
    await _invalidate_cache()
    return _build_response(page)
# ══════════════════════════════════════════════════════════════════════════════
# GALLERY – UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

async def upload_gallery_image(
    file: UploadFile,
    alt: str,
    session: AsyncSession,
) -> GalleryUploadResponse:
    """Upload 1 gambar ke R2, simpan record DB, invalidasi cache."""
    page = await _get_active_page(session)
    if not page:
        raise HTTPException(status_code=404, detail="Halaman About Us tidak ditemukan.")

    data     = await _validate_image(file)
    filename = f"{uuid.uuid4()}.webp"
    folder   = "about/gallery"
    cdn_key  = f"{folder}/{filename}"

    cdn_url = await upload_file(
        file         = data,
        folder       = folder,
        filename     = filename,
        content_type = "image/webp",
    )

    # Hitung order berikutnya dari relasi yang sudah di-load
    next_order = len(page.gallery)

    item = AboutGallery(
        page_id = page.id,
        cdn_url = cdn_url,
        cdn_key = cdn_key,
        alt     = alt,
        order   = next_order,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)

    await _invalidate_cache()
    return GalleryUploadResponse.model_validate(item)


# ══════════════════════════════════════════════════════════════════════════════
# GALLERY – DELETE
# ══════════════════════════════════════════════════════════════════════════════

async def delete_gallery_image(
    gallery_id: uuid.UUID,
    session: AsyncSession,
) -> dict:
    """Hapus dari DB dan Cloudflare R2 sekaligus."""
    result = await session.exec(
        select(AboutGallery).where(AboutGallery.id == gallery_id)
    )
    item = result.first()
    if not item:
        raise HTTPException(status_code=404, detail="Gambar tidak ditemukan.")

    await delete_file(item.cdn_key)
    await session.delete(item)
    await session.commit()
    await _invalidate_cache()
    return {"detail": "Gambar berhasil dihapus.", "id": str(gallery_id)}


# ══════════════════════════════════════════════════════════════════════════════
# GALLERY – REORDER
# ══════════════════════════════════════════════════════════════════════════════

async def reorder_gallery(
    payload: GalleryReorderRequest,
    session: AsyncSession,
) -> dict:
    """Update urutan swiper gallery (drag-and-drop dari admin panel)."""
    id_map = {item.id: item.order for item in payload.items}

    result = await session.exec(
        select(AboutGallery).where(AboutGallery.id.in_(list(id_map.keys())))  # type: ignore[attr-defined]
    )
    rows = result.all()

    if len(rows) != len(id_map):
        raise HTTPException(status_code=404, detail="Beberapa gambar tidak ditemukan.")

    for row in rows:
        row.order = id_map[row.id]
        session.add(row)

    await session.commit()
    await _invalidate_cache()
    return {"detail": f"{len(rows)} gambar berhasil diurutkan ulang."}


# ══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL SERVICE INSTANCE (opsional, untuk import di router)
# ══════════════════════════════════════════════════════════════════════════════

class _AboutService:
    get_about_page        = staticmethod(get_about_page)
    create_about_page     = staticmethod(create_about_page)
    update_about_page     = staticmethod(update_about_page)
    upload_gallery_image  = staticmethod(upload_gallery_image)
    delete_gallery_image  = staticmethod(delete_gallery_image)
    reorder_gallery       = staticmethod(reorder_gallery)

about_service = _AboutService()