# backend/data/activity/service.py

from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.data.activity.model import ActivityLog
from typing import List, Optional
from uuid import UUID

class ActivityService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_activity(
        self,
        activity_type: str,
        title: str,
        description: Optional[str] = None,
        reference_id: Optional[str] = None,
        user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        amount: Optional[int] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None
    ) -> ActivityLog:
        """
        Record a new activity in the system.
        """
        activity = ActivityLog(
            activity_type=activity_type,
            title=title,
            description=description,
            reference_id=reference_id,
            user_id=user_id,
            status=status,
            amount=amount,
            icon=icon,
            color=color
        )
        self.session.add(activity)
        return activity

    async def get_recent_activities(self, limit: int = 20, activity_type: Optional[str] = None) -> List[ActivityLog]:
        """
        Fetch recent activities for the admin dashboard.
        """
        statement = select(ActivityLog).order_by(desc(ActivityLog.created_at))
        
        if activity_type and activity_type != 'all':
            statement = statement.where(ActivityLog.activity_type == activity_type)
            
        statement = statement.limit(limit)
        results = await self.session.execute(statement)
        return results.scalars().all()
