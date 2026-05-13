from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from backend.db.main import get_session
from backend.auth.depedence import get_admin
from backend.auth.model import User
from .service import AdminSettingService

router_settings = APIRouter()

@router_settings.get("/couriers")
async def get_courier_settings(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin)
):
    prefs = await AdminSettingService.get_courier_preferences(session)
    return {
        "success": True,
        "data": prefs
    }

@router_settings.put("/couriers")
async def update_courier_settings(
    payload: Dict[str, bool],
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin)
):
    # Filter only valid couriers
    valid_keys = ["jne", "jnt", "sicepat", "tiki", "pos", "wahana", "anteraja"]
    filtered = {k: v for k, v in payload.items() if k in valid_keys}
    
    await AdminSettingService.update_setting(
        session=session,
        key="active_couriers",
        value=filtered,
        description="Daftar kurir aktif yang muncul di checkout"
    )
    
    return {
        "success": True,
        "message": "Preferensi kurir berhasil diperbarui"
    }
