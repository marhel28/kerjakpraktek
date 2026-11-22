"""Penulis/pembaca notifikasi lokal.

Semua fungsi memakai session sendiri dan bersifat best-effort: notifikasi
tidak boleh menggagalkan transaksi/webhook yang memanggilnya.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import func, select

from backend.db.main import db_session_maker
from backend.user.notifications.model import Notification
from backend.user.notifications.pubsub import publish_event
from backend.user.notifications.schema import NotificationOut

logger = logging.getLogger(__name__)


def _as_dict(row: Notification) -> dict:
    return NotificationOut.model_validate(row).model_dump(mode="json")


async def notify_user(
    user_id: UUID | str,
    title: str,
    content: str = "",
    notif_type: str = "general",
    action_url: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    recipient = UUID(str(user_id))
    meta = dict(metadata or {})
    if action_url:
        meta["action_url"] = action_url

    row = Notification(
        user_id=recipient,
        title=title,
        content=content or "",
        type=notif_type,
        meta=meta,
    )
    async with db_session_maker() as db:
        db.add(row)
        await db.commit()
        await db.refresh(row)
        result = _as_dict(row)

    await publish_event(recipient, "created", result)
    return result


async def notify_users(
    user_ids: list[UUID | str],
    title: str,
    content: str = "",
    notif_type: str = "general",
    action_url: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> list[dict]:
    unique_ids = list(dict.fromkeys(str(uid) for uid in user_ids if uid))
    if not unique_ids:
        return []

    meta = dict(metadata or {})
    if action_url:
        meta["action_url"] = action_url

    rows: list[dict] = []
    async with db_session_maker() as db:
        for uid in unique_ids:
            row = Notification(
                user_id=UUID(uid),
                title=title,
                content=content or "",
                type=notif_type,
                meta=meta,
            )
            db.add(row)
            rows.append(row)
        await db.commit()
        for row in rows:
            await db.refresh(row)
        results = [_as_dict(row) for row in rows]

    for result in results:
        await publish_event(result["user_id"], "created", result)
    return results


async def list_for_user(user_id: UUID | str, limit: int = 50) -> list[dict]:
    async with db_session_maker() as db:
        statement = (
            select(Notification)
            .where(Notification.user_id == UUID(str(user_id)))
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
        )
        rows = (await db.execute(statement)).scalars().all()
        return [_as_dict(row) for row in rows]


async def count_unread(user_id: UUID | str) -> int:
    async with db_session_maker() as db:
        statement = select(func.count()).select_from(Notification).where(
            Notification.user_id == UUID(str(user_id)),
            Notification.read_at.is_(None),
        )
        return int((await db.execute(statement)).scalar_one())


async def mark_read(user_id: UUID | str, notification_id: int) -> Optional[dict]:
    async with db_session_maker() as db:
        row = (
            await db.execute(
                select(Notification).where(
                    Notification.id == notification_id,
                    Notification.user_id == UUID(str(user_id)),
                )
            )
        ).scalar_one_or_none()
        if not row:
            return None
        row.read_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(row)
        result = _as_dict(row)

    await publish_event(result["user_id"], "updated", result)
    return result


async def mark_all_read(user_id: UUID | str) -> int:
    recipient = UUID(str(user_id))
    now = datetime.now(timezone.utc)
    async with db_session_maker() as db:
        rows = (
            await db.execute(
                select(Notification).where(
                    Notification.user_id == recipient,
                    Notification.read_at.is_(None),
                )
            )
        ).scalars().all()
        for row in rows:
            row.read_at = now
        await db.commit()
        results = [_as_dict(row) for row in rows]

    for result in results:
        await publish_event(recipient, "updated", result)
    return len(results)


async def delete_notification(user_id: UUID | str, notification_id: int) -> bool:
    async with db_session_maker() as db:
        row = (
            await db.execute(
                select(Notification).where(
                    Notification.id == notification_id,
                    Notification.user_id == UUID(str(user_id)),
                )
            )
        ).scalar_one_or_none()
        if not row:
            return False
        await db.delete(row)
        await db.commit()

    await publish_event(user_id, "deleted", {"id": notification_id})
    return True
