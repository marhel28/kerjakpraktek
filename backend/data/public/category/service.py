import orjson
import asyncio
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

from .model import Category, SubCategory

# CONFIG REDIS
CAT_CACHE_KEY = "category:public:tree"
CAT_LOCK_KEY = "lock:category:refresh"

# =========================
# TREE BUILDER (OPTIMIZED)
# =========================
async def _fetch_category_tree_from_db(session: AsyncSession):
    result = await session.execute(
        select(Category)
        .options(selectinload(Category.subcategories))
        .where(Category.is_active == True)
        .order_by(Category.position.asc())
    )
    categories = result.scalars().all()

    return [
        {
            "id": str(c.uuid),
            "name": c.name,
            "slug": c.slug,
            "icon": c.icon_name,
            "subcategories": [
                {
                    "name": s.name,
                    "slug": s.slug
                }
                for s in c.subcategories
                if s.is_active
            ]
        }
        for c in categories
    ]

# =========================
# CACHE ENGINE
# =========================
async def refresh_category_cache(session: AsyncSession, redis: Redis) -> bytes:
    data = await _fetch_category_tree_from_db(session)

    json_bytes = orjson.dumps(
        data,
        option=orjson.OPT_NON_STR_KEYS
    )

    await redis.set(CAT_CACHE_KEY, json_bytes, ex=60 * 60 * 24 * 7)  # 7 hari
    return json_bytes

async def get_category_tree_service(session: AsyncSession, redis: Redis) -> bytes:
    cached = await redis.get(CAT_CACHE_KEY)
    if cached:
        return cached

    lock_id = str(uuid4)

    # atomic lock acquire
    acquired = await redis.set(CAT_LOCK_KEY, lock_id, ex=5, nx=True)

    if acquired:
        return await _warm_cache(session, redis, lock_id)
    return orjson.dumps([])

# =========================
# CRUD OPERATIONS
# =========================

async def _warm_cache(session: AsyncSession, redis: Redis, lock_id: str):
    try:
        data = await refresh_category_cache(session, redis)
        return data

    finally:
        # ✔ atomic safe delete (NO race GET/DELETE)
        await redis.eval(
            """
            if redis.call('get', KEYS[1]) == ARGV[1] then
                return redis.call('del', KEYS[1])
            else
                return 0
            end
            """,
            1,
            CAT_LOCK_KEY,
            lock_id
        )
        
        
async def create_category_service(
    session: AsyncSession,
    name: str,
    slug: str,
    icon_name: str = None,
    position: int = 0
):
    # Cek unik slug
    existing = await session.execute(select(Category).where(Category.slug == slug))
    if existing.first():
        raise HTTPException(status_code=400, detail="Slug kategori sudah digunakan")

    new_cat = Category(
        name=name,
        slug=slug,
        icon_name=icon_name,
        position=position
    )
    session.add(new_cat)
    await session.commit()
    await session.refresh(new_cat)
    return new_cat

async def create_subcategory_service(
    session: AsyncSession,
    category_uuid: UUID,
    name: str,
    slug: str,
    position: int = 0
):
    new_sub = SubCategory(
        category_uuid=category_uuid,
        name=name,
        slug=slug,
        position=position
    )
    session.add(new_sub)
    await session.commit()
    await session.refresh(new_sub)
    return new_sub

async def delete_category_service(session: AsyncSession, uuid: UUID):
    cat = await session.get(Category, uuid)
    if not cat: return False
    await session.delete(cat)
    await session.commit()
    return True