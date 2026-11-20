import logging
from typing import Dict, Set
from uuid import UUID
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ChatConnectionManager:
    """
    Singleton connection manager untuk WebSocket chat pesan.
    Mendukung koneksi multipel per user (misal multi-tab) dan admin channel.
    """

    def __init__(self):
        self._user_connections: Dict[UUID, Set[WebSocket]] = {}
        self._admin_connections: Set[WebSocket] = set()

    async def connect(self, user_id: UUID, websocket: WebSocket, is_admin: bool = False) -> None:
        await websocket.accept()
        if is_admin:
            self._admin_connections.add(websocket)
            logger.info(f"[WS Chat] Admin connected. Total admins: {len(self._admin_connections)}")
        else:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(websocket)
            logger.info(f"[WS Chat] User {user_id} connected. Active sockets: {len(self._user_connections[user_id])}")

    def disconnect(self, user_id: UUID, websocket: WebSocket, is_admin: bool = False) -> None:
        if is_admin:
            self._admin_connections.discard(websocket)
            logger.info(f"[WS Chat] Admin disconnected. Remaining: {len(self._admin_connections)}")
        else:
            if user_id in self._user_connections:
                self._user_connections[user_id].discard(websocket)
                if not self._user_connections[user_id]:
                    del self._user_connections[user_id]
            logger.info(f"[WS Chat] User {user_id} disconnected.")

    async def send_to_user(self, user_id: UUID, payload: dict) -> None:
        sockets = self._user_connections.get(user_id, set()).copy()
        dead = []
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception as e:
                logger.warning(f"[WS Chat] Send to user {user_id} failed: {e}")
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws, is_admin=False)

    async def broadcast_to_admins(self, payload: dict) -> None:
        dead = []
        for ws in self._admin_connections.copy():
            try:
                await ws.send_json(payload)
            except Exception as e:
                logger.warning(f"[WS Chat] Broadcast to admin failed: {e}")
                dead.append(ws)
        for ws in dead:
            self._admin_connections.discard(ws)


chat_ws_manager = ChatConnectionManager()
