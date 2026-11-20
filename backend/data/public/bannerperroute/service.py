from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import UploadFile, HTTPException
from uuid import UUID
from urllib.parse import unquote
import orjson

from backend.db.cdn import upload_file, delete_file
from backend.data.public.assets.model import Asset
from .model import ImageSection, ImageSectionItem
from .schema import ImageSectionCreate, ImageSectionUpdate


def _fmt_item(item: ImageSectionItem) -> dict:
    return {
        "uuid": str(item.uuid),
        "image_url": item.asset.url if item.asset else "",
        "alt_text": item.asset.alt_text if item.asset else "",
        "target_url": item.target_url,
        "order": item.order,
        "asset_uuid": str(item.asset_uuid),
    }


def _fmt_section(section: ImageSection, include_asset_uuid: bool = False) -> dict:
    items = sorted(
        [_fmt_item(i) for i in section.items],
        key=lambda x: x["order"],
    )
    if not include_asset_uuid:
        for i in items:
            i.pop("asset_uuid", None)

    return {
        "uuid": str(section.uuid),
        "identifier": section.identifier,
        "title": section.title,
        "mode": section.mode,           # ← selalu disertakan
        "is_active": section.is_active,
        "created_at": str(section.created_at),
        "items": items,
    }


class ImageSectionService:
    CACHE_PREFIX = "cache:imagesection:"
    CACHE_TTL = 86400  # 24 jam

    # ──────────────────────────────────────────────────────
    # GET ALL (Admin)
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def get_all_sections(session: AsyncSession) -> dict:
        stmt = (
            select(ImageSection)
            .options(joinedload(ImageSection.items).joinedload(ImageSectionItem.asset))
            .order_by(ImageSection.created_at.desc())
        )
        result = await session.execute(stmt)
        sections = result.unique().scalars().all()
        return {
            "status": "success",
            "data": [_fmt_section(s, include_asset_uuid=True) for s in sections],
        }

    # ──────────────────────────────────────────────────────
    # GET BY IDENTIFIER (Public + Redis)
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def get_section_by_identifier(
        session: AsyncSession, redis, identifier: str
    ) -> dict:
        identifier = unquote(identifier)
        cache_key = f"{ImageSectionService.CACHE_PREFIX}{identifier}"

        cached = await redis.get(cache_key)
        if cached:
            data = orjson.loads(cached)
            if data is None:
                raise HTTPException(status_code=404, detail="Section tidak ditemukan")
            return {"status": "success", "source": "redis", "data": data}

        stmt = (
            select(ImageSection)
            .where(
                ImageSection.identifier == identifier,
                ImageSection.is_active == True,
            )
            .options(joinedload(ImageSection.items).joinedload(ImageSectionItem.asset))
        )
        section = (await session.execute(stmt)).unique().scalars().first()

        if not section:
            await redis.set(cache_key, orjson.dumps(None), ex=60)
            raise HTTPException(status_code=404, detail="Section tidak ditemukan")

        data = _fmt_section(section)
        await redis.set(cache_key, orjson.dumps(data), ex=ImageSectionService.CACHE_TTL)
        return {"status": "success", "source": "db", "data": data}

    # ──────────────────────────────────────────────────────
    # CREATE (Admin)
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def create_section(session: AsyncSession, data: ImageSectionCreate) -> dict:
        exist = (
            await session.execute(
                select(ImageSection).where(ImageSection.identifier == data.identifier)
            )
        ).scalars().first()
        if exist:
            raise HTTPException(status_code=400, detail="Identifier sudah digunakan.")

        section = ImageSection(
            identifier=data.identifier,
            title=data.title,
            mode=data.mode,
            is_active=data.is_active,
        )
        session.add(section)
        await session.commit()
        await session.refresh(section)

        return {
            "status": "success",
            "message": "Section dibuat",
            "data": _fmt_section(section),
        }

    # ──────────────────────────────────────────────────────
    # UPDATE (Admin)
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def update_section(
        session: AsyncSession, redis, section_uuid: UUID, data: ImageSectionUpdate
    ) -> dict:
        section = (
            await session.execute(
                select(ImageSection).where(ImageSection.uuid == section_uuid)
            )
        ).scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section tidak ditemukan")

        if data.title is not None:
            section.title = data.title
        if data.mode is not None:
            section.mode = data.mode
        if data.is_active is not None:
            section.is_active = data.is_active

        await session.commit()
        await redis.delete(f"{ImageSectionService.CACHE_PREFIX}{section.identifier}")
        return {"status": "success", "message": "Section diupdate"}

    # ──────────────────────────────────────────────────────
    # DELETE SECTION (Admin)
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def delete_section(
        session: AsyncSession, redis, section_uuid: UUID
    ) -> dict:
        section = (
            await session.execute(
                select(ImageSection).where(ImageSection.uuid == section_uuid)
            )
        ).scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section tidak ditemukan")

        identifier = section.identifier
        await session.delete(section)
        await session.commit()
        await redis.delete(f"{ImageSectionService.CACHE_PREFIX}{identifier}")
        return {"status": "success", "message": "Section dihapus"}

    # ──────────────────────────────────────────────────────
    # DELETE ITEM (Admin)
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def delete_banner_item(
        session: AsyncSession, redis, item_uuid: UUID
    ) -> dict:
        item = (
            await session.execute(
                select(ImageSectionItem)
                .where(ImageSectionItem.uuid == item_uuid)
                .options(joinedload(ImageSectionItem.section))
            )
        ).unique().scalars().first()
        if not item:
            raise HTTPException(status_code=404, detail="Item tidak ditemukan")

        identifier = item.section.identifier
        try:
            if item.asset:
                await delete_file(item.asset.url.split(".com/")[-1])
        except Exception:
            pass

        await session.delete(item)
        await session.commit()
        await redis.delete(f"{ImageSectionService.CACHE_PREFIX}{identifier}")
        return {"status": "success", "message": "Banner item dihapus"}

    # ──────────────────────────────────────────────────────
    # UPLOAD & ATTACH BANNER (Admin)
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def add_banner_with_upload(
        session: AsyncSession,
        redis,
        section_identifier: str,
        file: UploadFile,
        target_url: str,
        alt_text: str | None,
        order: int,
    ) -> dict:
        section_identifier = unquote(section_identifier)
        clean_url = target_url.strip()
        low_url = clean_url.lower()
        if any(low_url.startswith(prefix) for prefix in ("javascript:", "data:", "vbscript:", "file:")):
            raise HTTPException(status_code=400, detail="Skema target_url tidak diizinkan.")
        if not (clean_url.startswith("/") or low_url.startswith("https://") or low_url.startswith("http://")):
            raise HTTPException(status_code=400, detail="target_url harus berupa internal path (diawali /) atau URL https://")

        section = (
            await session.execute(
                select(ImageSection).where(
                    ImageSection.identifier == section_identifier
                )
            )
        ).scalars().first()
        if not section:
            raise HTTPException(status_code=404, detail="Section tidak ditemukan.")

        existing = (
            await session.execute(
                select(ImageSectionItem).where(
                    ImageSectionItem.section_uuid == section.uuid
                )
            )
        ).scalars().all()
        if len(existing) >= 5:
            raise HTTPException(
                status_code=400, detail="Maksimal 5 gambar per section."
            )

        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="Hanya file gambar yang diperbolehkan."
            )

        file_bytes = await file.read()
        cdn_url: str | None = None

        try:
            cdn_url = await upload_file(
                file=file_bytes,
                folder=f"banners/{section_identifier}",
                content_type=file.content_type,
            )
            asset = Asset(url=cdn_url, type="banner", alt_text=alt_text)
            session.add(asset)
            await session.flush()

            new_item = ImageSectionItem(
                section_uuid=section.uuid,
                asset_uuid=asset.uuid,
                target_url=clean_url,
                order=order,
            )
            session.add(new_item)
            await session.commit()
            await session.refresh(new_item)

            await redis.delete(
                f"{ImageSectionService.CACHE_PREFIX}{section_identifier}"
            )

            return {
                "status": "success",
                "message": "Banner berhasil ditambahkan",
                "data": {
                    "uuid": str(new_item.uuid),
                    "image_url": cdn_url,
                    "alt_text": alt_text,
                    "target_url": clean_url,
                    "order": order,
                },
            }

        except Exception as e:
            await session.rollback()
            if cdn_url:
                try:
                    await delete_file(cdn_url.split(".com/")[-1])
                except Exception:
                    pass
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")