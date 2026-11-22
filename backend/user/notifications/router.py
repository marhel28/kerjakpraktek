from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth.depedence import get_current_user
from backend.auth.model import User
from backend.user.notifications.schema import NotificationOut
from backend.user.notifications.service import (
    delete_notification,
    list_for_user,
    mark_all_read,
    mark_read,
)

router = APIRouter(tags=["Notifications"])


@router.get("/notifications", response_model=List[NotificationOut])
async def get_notifications(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    return await list_for_user(current_user.uuid, limit)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
async def patch_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
):
    result = await mark_read(current_user.uuid, notification_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notifikasi tidak ditemukan.")
    return result


@router.post("/notifications/read-all")
async def post_notifications_read_all(current_user: User = Depends(get_current_user)):
    updated = await mark_all_read(current_user.uuid)
    return {"updated": updated}


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = await delete_notification(current_user.uuid, notification_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notifikasi tidak ditemukan.")
