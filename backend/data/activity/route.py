# backend/data/activity/route.py

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.db.main import get_session
from backend.data.activity.service import ActivityService
from typing import Optional, List
from backend.auth.depedence import get_admin

router = APIRouter(prefix="/admin/activities", tags=["Admin Activities"])

@router.get("")
async def get_activities(
    type: Optional[str] = Query('all', description="Filter by type: order, booking, promo, all"),
    limit: int = Query(20, le=100),
    session: AsyncSession = Depends(get_session),
    admin = Depends(get_admin)
):
    """
    Get unified recent activities for dashboard.
    """
    svc = ActivityService(session)
    activities = await svc.get_recent_activities(limit=limit, activity_type=type)
    
    return {
        "success": True,
        "message": "Activities fetched successfully",
        "data": activities
    }
