from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, Response, HTTPException
from fastapi.responses import ORJSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from redis.asyncio import Redis

from backend.db.main import get_session
from backend.db.redis import get_redis_token
from .service import *
from .utilis import refresh_brand_cache_safe

router = APIRouter()

# =========================
# PUBLIC: GET BRANDS (SUPER FAST)
# =========================
@router.get("/", response_class=Response)
async def get_brands(
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token)
):
    # Mengirim bytes mentah dari Redis ke Client
    raw_data = await get_brands_service(session, redis)
    bg.add_task(refresh_brand_cache_safe, redis)
    return Response(
        content=raw_data,
        media_type="application/json",
        headers={"Cache-Control": "public, max-age=300"}
    )

# =========================
# ADMIN: CREATE
# =========================
@router.post("/admin/create")
async def create_brand(
    bg: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    slug: str = Form(...),
    route: str = Form(None),
    position: int = Form(0),
    is_featured: bool = Form(False),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token)
):
    file_bytes = await file.read()
    brand = await create_brand_service(session, file_bytes, name, slug, route, position, is_featured)
    
    # Refresh cache di background agar user langsung dapat data baru
    bg.add_task(refresh_brand_cache, session, redis)
    
    return {"status": "success", "id": brand.uuid}

# =========================
# ADMIN: EDIT
# =========================
@router.put("/admin/{uuid}")
async def edit_brand(
    uuid: str,
    bg: BackgroundTasks,
    name: str = Form(...),
    slug: str = Form(...),
    route: str = Form(None),
    position: int = Form(0),
    is_featured: bool = Form(False),
    file: UploadFile = File(None),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token)
):
    file_bytes = await file.read() if file else None
    updated = await edit_brand_service(session, uuid, name, slug, route, position, is_featured, file_bytes)
    
    if not updated:
        raise HTTPException(404, "Brand not found")
        
    bg.add_task(refresh_brand_cache, session, redis)
    return {"status": "updated"}

# =========================
# ADMIN: DELETE
# =========================
@router.delete("/admin/{uuid}")
async def delete_brand(
    uuid: str,
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token)
):
    success = await delete_brand_service(session, uuid)
    if not success:
        raise HTTPException(404, "Brand not found")
        
    bg.add_task(refresh_brand_cache, session, redis)
    return {"status": "deleted"}