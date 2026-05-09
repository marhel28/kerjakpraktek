from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, Response
from fastapi.responses import ORJSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.db.main import get_session
from backend.db.redis import get_redis_token
from redis.asyncio import Redis
from fastapi import HTTPException
from backend.utils.task_banner import *
from .service import *

router = APIRouter()

# =========================
# PUBLIC GET BANNER (ULTRA FAST)
# =========================
@router.post("/admin/create", response_class=ORJSONResponse)
async def create_banner(
    bg: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    link: str = Form(...),
    position: int = Form(0),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token),
):
    # 1. Validasi format
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Format gambar tidak didukung")

    # 2. Baca bytes (Non-blocking untuk S3)
    file_bytes = await file.read()

    # 3. Simpan ke DB & S3
    banner = await create_banner_service(
        session=session,
        file_bytes=file_bytes,
        title=title,
        link=link,
        position=position,
    )

    # 4. Trigger Refresh Cache di Background (Tanpa nunggu selesai)
    # Kita panggil versi "SAFE" agar tidak bentrok
    bg.add_task(refresh_banner_cache_safe, redis)

    return ORJSONResponse({"message": "ok", "uuid": str(banner.uuid)})


@router.get("/", response_class=Response)
async def get_banners(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token),
):
    """
    ENDPOINT PUBLIK: ULTRA FAST
    Mengembalikan raw bytes dari Redis tanpa overhead JSON parsing di Python.
    """
    raw_json_bytes = await get_banner_service(session, redis)

    return Response(
        content=raw_json_bytes,
        media_type="application/json",
        headers={
            "Cache-Control": "public, max-age=60",
            "X-Cache-Source": "Redis-Optimized"
        }
    )

# =========================
# ADMIN DELETE BANNER
# =========================
@router.delete("/admin/{uuid}", response_class=ORJSONResponse)
async def delete_banner(
    uuid: str,
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token),
):
    success = await delete_banner_service(session, uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Banner not found")

    # 🔥 Update cache di background
    bg.add_task(refresh_banner_cache, session, redis)

    return ORJSONResponse({"message": "deleted"})

# =========================
# ADMIN EDIT BANNER
# =========================
@router.put("/admin/{uuid}", response_class=ORJSONResponse)
async def edit_banner(
    uuid: str,
    bg: BackgroundTasks,
    file: UploadFile | None = File(None),
    title: str = Form(...),
    link: str = Form(...),
    position: int = Form(0),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_token),
):
    file_bytes = None
    if file:
        if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format")
        file_bytes = await file.read()

    banner = await edit_banner_service(
        session=session,
        uuid=uuid,
        title=title,
        link=link,
        position=position,
        file_bytes=file_bytes
    )

    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    # 🔥 Update cache di background
    bg.add_task(refresh_banner_cache, session, redis)

    return ORJSONResponse({
        "message": "updated",
        "uuid": str(banner.uuid)
    })