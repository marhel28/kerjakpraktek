from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import unquote
from uuid import UUID

from backend.db.redis import get_redis_token
from backend.db.main import get_session
from .service import ImageSectionService
from .schema import ImageSectionCreate, ImageSectionUpdate

router = APIRouter()

# ─────────────────────────────────────────────────────────────
# 🟢 PUBLIC
# ─────────────────────────────────────────────────────────────

@router.get("/public/{identifier:path}", summary="[PUBLIC] Get section by identifier (Redis cached)")
async def get_public_section(
    identifier: str,
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis_token),
):
    return await ImageSectionService.get_section_by_identifier(
        session, redis, unquote(identifier)
    )

# ─────────────────────────────────────────────────────────────
# 🔴 ADMIN — Section CRUD
# ─────────────────────────────────────────────────────────────

@router.get("", summary="[ADMIN] Get all sections with items")
async def get_all_sections(
    session: AsyncSession = Depends(get_session),
    # current_admin=Depends(get_current_admin),
):
    return await ImageSectionService.get_all_sections(session)


@router.post("", summary="[ADMIN] Create new section")
async def create_section(
    data: ImageSectionCreate,
    session: AsyncSession = Depends(get_session),
    # current_admin=Depends(get_current_admin),
):
    return await ImageSectionService.create_section(session, data)


@router.put("/{section_uuid}", summary="[ADMIN] Update section title / mode / status")
async def update_section(
    section_uuid: UUID,
    data: ImageSectionUpdate,
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis_token),
    # current_admin=Depends(get_current_admin),
):
    return await ImageSectionService.update_section(session, redis, section_uuid, data)


@router.delete("/{section_uuid}", summary="[ADMIN] Delete section + all its items")
async def delete_section(
    section_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis_token),
    # current_admin=Depends(get_current_admin),
):
    return await ImageSectionService.delete_section(session, redis, section_uuid)

# ─────────────────────────────────────────────────────────────
# 🔴 ADMIN — Banner Items
# ─────────────────────────────────────────────────────────────

@router.post(
    "/{section_identifier}/upload-banner",
    summary="[ADMIN] Upload image and attach to section",
)
async def upload_banner(
    section_identifier: str,
    file: UploadFile = File(..., description="File gambar (jpg/png/webp)"),
    target_url: str = Form(..., description="URL tujuan saat banner diklik"),
    alt_text: str = Form(None, description="Alt text untuk aksesibilitas / SEO"),
    order: int = Form(1, description="Urutan tampil (ascending)"),
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis_token),
    # current_admin=Depends(get_current_admin),
):
    return await ImageSectionService.add_banner_with_upload(
        session,
        redis,
        unquote(section_identifier),
        file,
        target_url,
        alt_text,
        order,
    )


@router.delete(
    "/items/{item_uuid}",
    summary="[ADMIN] Delete single banner item (also removes from CDN)",
)
async def delete_banner_item(
    item_uuid: UUID,
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis_token),
    # current_admin=Depends(get_current_admin),
):
    return await ImageSectionService.delete_banner_item(session, redis, item_uuid)