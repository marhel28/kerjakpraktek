import orjson
import asyncio
from uuid import uuid4
from urllib.parse import urlparse
from sqlalchemy import select
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from .model import Brand
from backend.data.public.assets.model import Asset
from backend.db.cdn import upload_file, delete_file

# CONFIG REDIS
BRAND_CACHE_KEY = "brand:public:data"
BRAND_LOCK_KEY = "lock:brand:refresh"

def _get_s3_key(url: str) -> str:
    return urlparse(url).path.lstrip("/")

async def _fetch_brands_from_db(session: AsyncSession):
    """Query dioptimasi hanya mengambil kolom yang dibutuhkan frontend"""
    result = await session.execute(
        select(
            Brand.uuid,
            Brand.name,
            Brand.slug,
            Brand.route,
            Brand.is_featured,
            Asset.url
        )
        .join(Asset, Brand.logo_uuid == Asset.uuid)
        .where(Brand.is_active == True)
        .order_by(Brand.position.asc())
    )
    rows = result.all()
    return [
        {
            "id": str(uuid),
            "n": name,     # name
            "s": slug,     # slug
            "r": route,    # route/link
            "f": is_featured,
            "img": url     # logo url
        }
        for uuid, name, slug, route, is_featured, url in rows
    ]

# =========================
# CACHE ENGINE
# =========================

async def refresh_brand_cache(session: AsyncSession, redis: Redis) -> bytes:
    data = await _fetch_brands_from_db(session)
    json_bytes = orjson.dumps(data)
    await redis.set(BRAND_CACHE_KEY, json_bytes, ex=86400 * 7) # Cache 7 hari
    return json_bytes

async def get_brands_service(session: AsyncSession, redis: Redis) -> bytes:
    # 1. Hit Redis
    cached = await redis.get(BRAND_CACHE_KEY)
    if cached:
        return cached

    # 2. Lock & Build (Anti Stampede)
    if await redis.set(BRAND_LOCK_KEY, "1", ex=5, nx=True):
        try:
            return await refresh_brand_cache(session, redis)
        finally:
            await redis.delete(BRAND_LOCK_KEY)
    
    # 3. Wait fallback
    await asyncio.sleep(0.1)
    cached = await redis.get(BRAND_CACHE_KEY)
    return cached if cached else orjson.dumps([])

# =========================
# CRUD OPERATIONS
# =========================

async def create_brand_service(
    session: AsyncSession,
    file_bytes: bytes,
    name: str,
    slug: str,
    route: str = None,
    position: int = 0,
    is_featured: bool = False
):
    # Upload Logo
    url = await upload_file(
        file=file_bytes,
        folder="brands",
        filename=f"{slug}-{uuid4().hex[:8]}.webp",
        content_type="image/webp"
    )

    asset = Asset(url=url, type="image", alt_text=f"Logo {name}")
    session.add(asset)
    await session.flush()

    brand = Brand(
        name=name,
        slug=slug,
        logo_uuid=asset.uuid,
        route=route,
        position=position,
        is_featured=is_featured
    )
    session.add(brand)
    await session.commit()
    return brand

async def edit_brand_service(
    session: AsyncSession,
    uuid: str,
    name: str,
    slug: str,
    route: str,
    position: int,
    is_featured: bool,
    file_bytes: bytes = None
):
    result = await session.execute(
        select(Brand, Asset).join(Asset, Brand.logo_uuid == Asset.uuid).where(Brand.uuid == uuid)
    )
    row = result.first()
    if not row: return None
    
    brand, asset = row
    
    if file_bytes:
        await delete_file(_get_s3_key(asset.url))
        new_url = await upload_file(file_bytes, "brands", f"{slug}.webp", "image/webp")
        asset.url = new_url

    brand.name = name
    brand.slug = slug
    brand.route = route
    brand.position = position
    brand.is_featured = is_featured
    
    await session.commit()
    return brand

async def delete_brand_service(session: AsyncSession, uuid: str):
    result = await session.execute(
        select(Brand, Asset).join(Asset, Brand.logo_uuid == Asset.uuid).where(Brand.uuid == uuid)
    )
    row = result.first()
    if not row: return False

    brand, asset = row
    await delete_file(_get_s3_key(asset.url))
    await session.delete(brand)
    await session.delete(asset)
    await session.commit()
    return True