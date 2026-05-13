from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.main import get_session
from backend.db.redis import get_redis_token
from .service import AddonService
from typing import Any, Optional
from uuid import UUID

router = APIRouter(prefix="/addons", tags=["Addons"])

@router.get("/bundle/{product_id_or_slug}")
async def get_addon_bundle(
    product_id_or_slug: str,
    category_slug: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Get dynamic addon bundle for a specific product based on identifier (UUID or Slug).
    Validated with PostgreSQL and DragonflyDB caching.
    """
    redis = get_redis_token()
    bundle = await AddonService.get_bundle_by_product(
        db=db,
        product_id_or_slug=product_id_or_slug,
        category_slug=category_slug,
        redis_client=redis
    )
    return {
        "success": True,
        "message": "Addon bundle fetched successfully",
        "data": bundle
    }
