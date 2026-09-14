from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from io import BytesIO
from PIL import Image
import logging

from backend.db.main import get_session
from backend.auth.depedence import get_admin
from backend.auth.model import User
from backend.db.cdn import upload_file
from .service import AdminSettingService

logger = logging.getLogger("uvicorn")
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

@router_settings.get("/promo-popup")
async def get_promo_popup(
    session: AsyncSession = Depends(get_session)
):
    data = await AdminSettingService.get_setting(session, "promo_popup")
    return {
        "success": True,
        "data": data or {
            "image_url": "",
            "route": "",
            "is_active": False
        }
    }

@router_settings.put("/promo-popup")
async def update_promo_popup(
    payload: Dict[str, Any],
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin)
):
    image_url = payload.get("image_url", "")
    route = payload.get("route", "")
    is_active = payload.get("is_active", False)
    
    value = {
        "image_url": image_url,
        "route": route,
        "is_active": is_active
    }
    
    await AdminSettingService.update_setting(
        session=session,
        key="promo_popup",
        value=value,
        description="Popup promo besar yang muncul saat user masuk website"
    )
    
    return {
        "success": True,
        "message": "Pengaturan popup promo berhasil diperbarui",
        "data": value
    }

@router_settings.post("/promo-popup/upload")
async def upload_promo_popup_image(
    file: UploadFile = File(...),
    admin: User = Depends(get_admin)
):
    # Validasi tipe file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar (JPEG, PNG, WEBP, dll)")

    # Batasi ukuran file (2MB)
    MAX_SIZE = 2 * 1024 * 1024
    file_size = 0
    file_bytes = b""
    
    # Membaca file
    for chunk in file.file:
        file_bytes += chunk
        file_size += len(chunk)
        if file_size > MAX_SIZE:
            raise HTTPException(status_code=400, detail="Ukuran gambar maksimal 2MB")

    try:
        # Convert ke WebP secara otomatis agar ringan
        img = Image.open(BytesIO(file_bytes)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="WEBP", quality=80)
        buf.seek(0)

        # Menggunakan db.cdn.py untuk upload ke Cloudflare R2
        image_url = await upload_file(
            file=buf,
            folder="promo_popup",
            filename=None,  # UUID otomatis dari upload_file
            content_type="image/webp"
        )
        return {"success": True, "image_url": image_url}
    except Exception as e:
        logger.error(f"Gagal memproses/mengunggah gambar popup promo: {e}")
        raise HTTPException(status_code=500, detail="Gagal memproses atau mengunggah gambar ke server CDN")


