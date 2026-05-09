from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from typing import Optional

from backend.db.main import get_session
from .model import BannerCreateForm, BannerUpdate
from .service import BannerService

router = APIRouter(prefix="/main-bottom", tags=["Main Bottom Banner"])

# ── PUBLIC ──────────────────────────────────────────────
@router.get("/public")
async def get_public_banners(db: AsyncSession = Depends(get_session)):
    service = BannerService(db)
    banners = await service.get_active_banners()
    return {"status": "success", "data": banners}

# ── ADMIN ───────────────────────────────────────────────
@router.get("/admin")
async def list_all_banners(db: AsyncSession = Depends(get_session)):
    service = BannerService(db)
    banners = await service.get_all_banners()
    return {"status": "success", "data": banners}

@router.post("/admin")
async def create_banner(
    title: str = Form(...),
    route_link: str = Form(...),
    is_active: bool = Form(True),
    sort_order: int = Form(0),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)
):
    data = BannerCreateForm(
        title=title,
        route_link=route_link,
        is_active=is_active,
        sort_order=sort_order
    )
    service = BannerService(db)
    banner = await service.create_banner(data, file)
    return {"status": "success", "data": banner}

@router.put("/admin/{banner_uuid}")
async def update_banner(
    banner_uuid: UUID,
    title: Optional[str] = Form(None),
    route_link: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    sort_order: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_session)
):
    data = BannerUpdate(
        title=title,
        route_link=route_link,
        is_active=is_active,
        sort_order=sort_order
    )
    service = BannerService(db)
    banner = await service.update_banner(banner_uuid, data, file)
    return {"status": "success", "data": banner}

@router.delete("/admin/{banner_uuid}")
async def delete_banner(banner_uuid: UUID, db: AsyncSession = Depends(get_session)):
    service = BannerService(db)
    result = await service.delete_banner(banner_uuid)
    return {"status": "success", "message": result["message"]}