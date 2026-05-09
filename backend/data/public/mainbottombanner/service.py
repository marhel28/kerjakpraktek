import json
import logging
from io import BytesIO
from uuid import UUID
from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, UploadFile
from PIL import Image

from backend.db.redis import get_redis_token
from backend.db.cdn import upload_file, delete_file
from .model import MainBottomBanner, BannerCreateForm, BannerUpdate

logger = logging.getLogger(__name__)

REDIS_BANNER_KEY = "cache:main_bottom_banners:active"
CACHE_TTL = 86400  # 24 jam
MAX_ACTIVE_BANNERS = 4

class BannerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis = get_redis_token()

    # ─── Helper: convert & upload image ─────────────────────
    async def _upload_image(self, file: UploadFile) -> str:
        """Baca file, convert ke WebP, upload ke CDN, return URL."""
        try:
            contents = await file.read()
            img = Image.open(BytesIO(contents)).convert("RGB")
            buf = BytesIO()
            img.save(buf, format="WEBP", quality=80)
            buf.seek(0)
            url = await upload_file(
                file=buf,
                folder="banners",
                filename=None,
                content_type="image/webp"
            )
            return url
        except Exception as e:
            raise HTTPException(400, f"Gagal memproses gambar: {e}")

    # ─── Helper: extract key from CDN URL ──────────────────
    def _extract_key(self, url: str) -> str:
        # URL: https://cdn.../banners/uuid.webp -> key: banners/uuid.webp
        parts = url.split("/")
        return parts[-2] + "/" + parts[-1]

    # ─── Helper: check active limit ────────────────────────
    async def _check_active_limit(self, exclude_uuid: Optional[UUID] = None):
        query = select(MainBottomBanner).where(MainBottomBanner.is_active == True)
        if exclude_uuid:
            query = query.where(MainBottomBanner.uuid != exclude_uuid)
        result = await self.db.exec(query)
        active_count = len(result.all())
        if active_count >= MAX_ACTIVE_BANNERS:
            raise HTTPException(400, f"Maksimal {MAX_ACTIVE_BANNERS} banner aktif untuk homepage")

    # ─── Public Read (cached) ──────────────────────────────
    async def get_active_banners(self):
        cached = await self.redis.get(REDIS_BANNER_KEY)
        if cached:
            return json.loads(cached)

        query = select(MainBottomBanner).where(MainBottomBanner.is_active == True)\
                  .order_by(MainBottomBanner.sort_order.asc())
        result = await self.db.exec(query)
        banners = result.all()

        data = [
            {
                "uuid": str(b.uuid),
                "title": b.title,
                "image_url": b.image_url,
                "route_link": b.route_link,
                "sort_order": b.sort_order
            } for b in banners
        ]
        await self.redis.set(REDIS_BANNER_KEY, json.dumps(data), ex=CACHE_TTL)
        return data

    # ─── Admin List (all, no cache) ────────────────────────
    async def get_all_banners(self):
        query = select(MainBottomBanner).order_by(MainBottomBanner.sort_order.asc())
        result = await self.db.exec(query)
        return result.all()

    # ─── Create (with file) ────────────────────────────────
    async def create_banner(self, data: BannerCreateForm, file: UploadFile):
        # Cek kuota active
        if data.is_active:
            await self._check_active_limit()

        # Upload gambar
        image_url = await self._upload_image(file)

        banner = MainBottomBanner(
            title=data.title,
            image_url=image_url,
            route_link=data.route_link,
            is_active=data.is_active,
            sort_order=data.sort_order
        )
        self.db.add(banner)
        await self.db.commit()
        await self.db.refresh(banner)

        # Invalidate cache
        await self.redis.delete(REDIS_BANNER_KEY)
        return banner

    # ─── Update (with optional file) ───────────────────────
    async def update_banner(self, banner_uuid: UUID, data: BannerUpdate, file: Optional[UploadFile] = None):
        query = select(MainBottomBanner).where(MainBottomBanner.uuid == banner_uuid)
        result = await self.db.exec(query)
        banner = result.first()
        if not banner:
            raise HTTPException(404, "Banner tidak ditemukan")

        # Cek kuota active jika diubah ke active
        if data.is_active is True and not banner.is_active:
            await self._check_active_limit(exclude_uuid=banner_uuid)

        # Update field teks
        update_dict = data.dict(exclude_unset=True)
        if "file" in update_dict:
            del update_dict["file"]
        for key, value in update_dict.items():
            if value is not None:
                setattr(banner, key, value)

        # Jika ada file baru, upload dan hapus yang lama
        if file:
            old_url = banner.image_url
            new_url = await self._upload_image(file)
            banner.image_url = new_url
            try:
                key = self._extract_key(old_url)
                await delete_file(key)
            except Exception as e:
                logger.warning(f"Gagal hapus gambar lama: {e}")

        self.db.add(banner)
        await self.db.commit()
        await self.db.refresh(banner)

        await self.redis.delete(REDIS_BANNER_KEY)
        return banner

    # ─── Delete ────────────────────────────────────────────
    async def delete_banner(self, banner_uuid: UUID):
        query = select(MainBottomBanner).where(MainBottomBanner.uuid == banner_uuid)
        result = await self.db.exec(query)
        banner = result.first()
        if not banner:
            raise HTTPException(404, "Banner tidak ditemukan")

        # Hapus file dari CDN
        try:
            key = self._extract_key(banner.image_url)
            await delete_file(key)
        except Exception as e:
            logger.warning(f"Gagal hapus gambar: {e}")

        await self.db.delete(banner)
        await self.db.commit()

        await self.redis.delete(REDIS_BANNER_KEY)
        return {"message": "Banner berhasil dihapus"}