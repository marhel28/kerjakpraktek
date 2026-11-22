"""Jembatan Redis pub/sub supaya notifikasi dari Celery sampai ke socket API."""

import asyncio
import logging
from uuid import UUID

import orjson

from backend.db.redis import get_redis_token
from backend.user.notifications.ws_manager import notification_ws_manager

logger = logging.getLogger(__name__)

CHANNEL_PATTERN = "notif:*"


def _channel(user_id: UUID | str) -> str:
    return f"notif:{user_id}"


async def publish_event(user_id: UUID | str, event: str, data: dict) -> None:
    """Publish satu event notifikasi. Gagal publish tidak boleh menggagalkan caller."""
    try:
        payload = orjson.dumps(
            {"user_id": str(user_id), "event": event, "data": data}
        )
        await get_redis_token().publish(_channel(user_id), payload)
    except Exception as exc:
        logger.warning("[Notif WS] publish gagal (data tetap tersimpan): %s", exc)


_subscriber_task: asyncio.Task | None = None


def start_subscriber() -> None:
    """Dipanggil sekali per worker dari lifespan FastAPI."""
    global _subscriber_task
    if _subscriber_task is None or _subscriber_task.done():
        _subscriber_task = asyncio.create_task(notification_subscriber())


async def stop_subscriber() -> None:
    global _subscriber_task
    if _subscriber_task is not None and not _subscriber_task.done():
        _subscriber_task.cancel()
        try:
            await _subscriber_task
        except asyncio.CancelledError:
            pass
    _subscriber_task = None


async def notification_subscriber() -> None:
    """Jalankan satu subscriber per worker API; kirim hanya ke socket lokal worker itu."""
    while True:
        pubsub = None
        try:
            pubsub = get_redis_token().pubsub()
            await pubsub.psubscribe(CHANNEL_PATTERN)
            logger.info("[Notif WS] subscriber aktif di %s", CHANNEL_PATTERN)
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if not message:
                    continue
                raw = message.get("data")
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                try:
                    payload = orjson.loads(raw)
                    user_id = UUID(str(payload["user_id"]))
                    await notification_ws_manager.send_to_user(
                        user_id,
                        {
                            "type": f"notification.{payload['event']}",
                            "data": payload["data"],
                        },
                    )
                except Exception as exc:
                    logger.warning("[Notif WS] event tidak valid: %s", exc)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("[Notif WS] subscriber terputus, retry 5s: %s", exc)
            await asyncio.sleep(5)
        finally:
            if pubsub is not None:
                try:
                    await pubsub.close()
                except Exception:
                    pass
