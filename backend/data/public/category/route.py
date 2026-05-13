from fastapi import APIRouter, Depends, Response, BackgroundTasks, Form, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from redis.asyncio import Redis
from uuid import UUID

from backend.db.main import get_session
from backend.db.redis import get_redis_token
from .service import *
from .utilis import refresh_category_cache_safe

router = APIRouter()


# =========================
# PUBLIC GET (ULTRA FAST)
# =========================
@router.get("/")
async def get_public_categories(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token)
):
    raw = await get_category_tree_service(session, redis)

    return Response(
        content=raw,
        media_type="application/json",
        headers={
            "Cache-Control": "public, max-age=30"
        }
    )

# =========================
# CREATE CATEGORY
# =========================
@router.post("/admin/category")
async def create_cat(
    bg: BackgroundTasks,
    name: str = Form(...),
    slug: str = Form(...),
    icon_name: str = Form(None),
    position: int = Form(0),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token)
):
    cat = await create_category_service(session, name, slug, icon_name, position)

    # 🔥 refresh async (non blocking request)
    bg.add_task(refresh_category_cache_safe, redis)

    return {"status": "success", "uuid": cat.uuid}


# =========================
# CREATE SUBCATEGORY
# =========================
@router.post("/admin/subcategory")
async def create_sub(
    bg: BackgroundTasks,
    category_uuid: UUID = Form(...),
    name: str = Form(...),
    slug: str = Form(...),
    position: int = Form(0),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token)
):
    sub = await create_subcategory_service(session, category_uuid, name, slug, position)

    bg.add_task(refresh_category_cache_safe, redis)

    return {"status": "success", "uuid": sub.uuid}


# =========================
# DELETE CATEGORY (FAST INVALIDATE)
# =========================
@router.delete("/admin/category/{uuid}")
async def delete_cat(
    uuid: UUID,
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token)
):
    success = await delete_category_service(session, uuid)

    if not success:
        raise HTTPException(status_code=404, detail="Category not found")

    # 🔥 instant invalidate (NO WAIT)
    await redis.delete(CAT_CACHE_KEY)

    # 🔥 Rebuild cache secara aman di background (menggunakan lock dan jeda sync)
    bg.add_task(refresh_category_cache_safe, redis)

    return {"status": "deleted"}