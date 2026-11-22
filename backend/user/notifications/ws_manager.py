import logging
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class NotificationConnectionManager:
    """Registry socket notifikasi per user (multi-tab didukung)."""

    def __init__(self) -> None:
        self._connections: Dict[UUID, Set[WebSocket]] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)
        logger.info(
            "[WS Notif] user %s connected (%d socket)",
            user_id,
            len(self._connections[user_id]),
        )

    def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        sockets = self._connections.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            del self._connections[user_id]

    async def send_to_user(self, user_id: UUID, payload: dict) -> None:
        dead = []
        for ws in self._connections.get(user_id, set()).copy():
            try:
                await ws.send_json(payload)
            except Exception as exc:
                logger.warning("[WS Notif] kirim ke %s gagal: %s", user_id, exc)
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)


notification_ws_manager = NotificationConnectionManager()
