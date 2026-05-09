from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from backend.data.public.assets.model import Asset
from backend.data.public.xbanner.model import Banner
from backend.db.cdn import upload_file, delete_file
from uuid import uuid4
from redis.asyncio import Redis
import orjson
import asyncio
import random
from urllib.parse import urlparse

# =========================
# REDIS CONFIG
# =========================
# KITA HANYA PAKAI 1 KEY UNTUK PUBLIC GET (SINGLE ROUNDTRIP)
BANNER_CACHE_KEY = "banner:public:data"
LOCK_KEY = "lock:banner:refresh"

# =========================
# HELPER: GET S3 KEY FROM URL
# =========================
def _get_s3_key_from_url(url: str) -> str:
    """Ekstrak key S3/R2 dengan aman dari URL CDN"""
    path = urlparse(url).path
    return path.lstrip("/") # Hapus slash di depan, cth: "xbanner/uuid.webp"

# =========================
# DB FETCH (OPTIMIZED QUERY)
# =========================
async def _fetch_from_db(session: AsyncSession) -> list[dict]:
    result = await session.execute(
        select(
            Banner.uuid,
            Banner.title,
            Banner.link,
            Banner.position,
            Asset.url
        )
        .join(Asset, Banner.asset_uuid == Asset.uuid)
        .where(Banner.is_active == True)
        .order_by(Banner.position.asc())
    )
    rows = result.all()
    # Response minimal
    return [
        {
            "id": str(uuid),
            "t": title,
            "l": link,
            "img": url,
            "p": position,
        }
        for uuid, title, link, position, url in rows
    ]

# =========================
# REFRESH CACHE (DIPANGGIL OLEH ADMIN / BACKGROUND)
# =========================
async def refresh_banner_cache(session: AsyncSession, redis: Redis):
    """
    Fungsi ini dipanggil sebagai Background Task setiap kali Admin melakukan CRUD.
    Sehingga Public Endpoint selalu mendapatkan data dari RAM (Cache) tanpa perlu Query.
    """
    data = await _fetch_from_db(session)
    json_bytes = orjson.dumps(data)
    
    # TTL panjang, karena cache akan dioverwrite secara manual saat Admin update data
    ttl = 86400 * 7 # 7 Hari
    await redis.set(BANNER_CACHE_KEY, json_bytes, ex=ttl)
    return json_bytes

# =========================
# GET BANNER (ULTRA FAST - ZERO SERIALIZATION)
# =========================
async def get_banner_service(session: AsyncSession, redis: Redis) -> bytes:
    # 1. BACA DARI CACHE (Hanya 1 kali Roundtrip!)
    cached_bytes = await redis.get(BANNER_CACHE_KEY)
    if cached_bytes:
        return cached_bytes # Langsung return raw bytes! Jangan di-loads!

    # 2. LOCK ANTI-STAMPEDE (Jika cache kosong)
    lock = await redis.setnx(LOCK_KEY, 1)
    if lock:
        await redis.expire(LOCK_KEY, 5)
        raw_bytes = await refresh_banner_cache(session, redis)
        return raw_bytes

    # 3. TUNGGU CACHE DIISI REQUEST LAIN
    await asyncio.sleep(0.1)
    cached_bytes = await redis.get(BANNER_CACHE_KEY)
    if cached_bytes:
        return cached_bytes

    # Fallback murni
    data = await _fetch_from_db(session)
    return orjson.dumps(data)


# =========================
# CREATE BANNER
# =========================
async def create_banner_service(
    session: AsyncSession,
    file_bytes: bytes, # Terima bytes, bukan stream sync
    title: str,
    link: str,
    position: int = 0,
):
    filename = f"{uuid4()}.webp"
    url = await upload_file(
        file=file_bytes,
        folder="xbanner",
        filename=filename,
        content_type="image/webp"
    )

    asset = Asset(url=url, type="image", alt_text=title)
    session.add(asset)
    await session.flush() # Butuh UUID dari asset

    banner = Banner(
        title=title,
        link=link,
        asset_uuid=asset.uuid,
        position=position,
        is_active=True
    )
    session.add(banner)
    await session.commit()
    return banner

# =========================
# DELETE BANNER
# =========================
async def delete_banner_service(session: AsyncSession, uuid: str):
    result = await session.execute(
        select(Banner, Asset)
        .join(Asset, Banner.asset_uuid == Asset.uuid)
        .where(Banner.uuid == uuid)
    )
    row = result.first()
    if not row:
        return False

    banner, asset = row

    # 🔥 Hapus file CDN secara aman
    s3_key = _get_s3_key_from_url(asset.url)
    await delete_file(s3_key)

    # Hapus dari DB
    await session.delete(banner)
    await session.delete(asset)
    await session.commit()
    return True

# =========================
# EDIT BANNER
# =========================
async def edit_banner_service(
    session: AsyncSession,
    uuid: str,
    title: str,
    link: str,
    position: int,
    file_bytes: bytes | None = None
):
    result = await session.execute(
        select(Banner, Asset)
        .join(Asset, Banner.asset_uuid == Asset.uuid)
        .where(Banner.uuid == uuid)
    )
    row = result.first()
    if not row:
        return None

    banner, asset = row

    if file_bytes:
        # Hapus file lama dengan aman
        old_s3_key = _get_s3_key_from_url(asset.url)
        await delete_file(old_s3_key)

        # Upload file baru
        filename = f"{uuid4()}.webp"
        new_url = await upload_file(
            file=file_bytes,
            folder="xbanner",
            filename=filename,
            content_type="image/webp"
        )
        asset.url = new_url

    # Update DB
    banner.title = title
    banner.link = link
    banner.position = position
    await session.commit()
    
    return banner