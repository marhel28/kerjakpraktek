from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.main import get_session
from .service import AddonService
from typing import List, Any
from uuid import UUID
from pydantic import BaseModel

router = APIRouter(prefix="/admin/addons", tags=["Admin Addons"])

class AddonGroupSchema(BaseModel):
    name: str
    selection_type: str = "multi"
    is_required: bool = False
    is_active: bool = True
    sort_order: int = 1
    category_uuids: List[UUID] = []

class AddonItemSchema(BaseModel):
    group_uuid: UUID
    name: str
    description: str = ""
    price: int = 0
    weight: int = 0
    stock: int = 0
    image_url: str = ""
    is_active: bool = True
    allow_quantity: bool = True
    max_quantity: int = 10

@router.get("/groups")
async def list_groups(db: AsyncSession = Depends(get_session)):
    groups = await AddonService.get_all_groups(db)
    return {"success": True, "data": groups}

@router.get("/groups/{group_uuid}/items")
async def list_items(group_uuid: UUID, db: AsyncSession = Depends(get_session)):
    items = await AddonService.get_group_items(db, group_uuid)
    return {"success": True, "data": items}

@router.get("/groups/{group_uuid}/categories")
async def list_group_categories(group_uuid: UUID, db: AsyncSession = Depends(get_session)):
    from .model import CategoryAddonMapping
    from sqlalchemy import select
    stmt = select(CategoryAddonMapping.category_uuid, CategoryAddonMapping.subcategory_uuid).where(CategoryAddonMapping.addon_group_uuid == group_uuid)
    result = await db.execute(stmt)
    rows = result.all()
    
    # Combine both and filter None
    cat_uuids = []
    for r in rows:
        if r.category_uuid: cat_uuids.append(r.category_uuid)
        if r.subcategory_uuid: cat_uuids.append(r.subcategory_uuid)
        
    return {"success": True, "data": cat_uuids}

from backend.db.redis import get_redis_token

@router.post("/groups")
async def create_group(data: AddonGroupSchema, db: AsyncSession = Depends(get_session)):
    redis = get_redis_token()
    group = await AddonService.create_group(db, data.dict(), redis_client=redis)
    return {"success": True, "data": group}

@router.patch("/groups/{group_uuid}")
async def update_group(group_uuid: UUID, data: dict, db: AsyncSession = Depends(get_session)):
    redis = get_redis_token()
    group = await AddonService.update_group(db, group_uuid, data, redis_client=redis)
    return {"success": True, "data": group}

@router.delete("/groups/{group_uuid}")
async def delete_group(group_uuid: UUID, db: AsyncSession = Depends(get_session)):
    redis = get_redis_token()
    success = await AddonService.delete_group(db, group_uuid, redis_client=redis)
    return {"success": success}

@router.post("/items")
async def create_item(data: AddonItemSchema, db: AsyncSession = Depends(get_session)):
    item = await AddonService.create_item(db, data.dict())
    return {"success": True, "data": item}

@router.patch("/items/{item_uuid}")
async def update_item(item_uuid: UUID, data: dict, db: AsyncSession = Depends(get_session)):
    item = await AddonService.update_item(db, item_uuid, data)
    return {"success": True, "data": item}

@router.delete("/items/{item_uuid}")
async def delete_item(item_uuid: UUID, db: AsyncSession = Depends(get_session)):
    success = await AddonService.delete_item(db, item_uuid)
    return {"success": success}

@router.get("/stock/{stock_uuid}")
async def list_stock_mappings(stock_uuid: UUID, db: AsyncSession = Depends(get_session)):
    uuids = await AddonService.get_stock_mappings(db, stock_uuid)
    return {"success": True, "data": uuids}

@router.post("/stock/{stock_uuid}/sync")
async def sync_stock_mappings(stock_uuid: UUID, data: List[UUID], db: AsyncSession = Depends(get_session)):
    redis = get_redis_token()
    await AddonService.sync_stock_mappings(db, stock_uuid, data, redis_client=redis)
    return {"success": True}
