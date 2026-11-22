import logging
from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from backend.auth.model import User
from backend.auth.ws_auth import authenticate_ws_token
from backend.user.notifications.service import count_unread
from backend.user.notifications.ws_manager import notification_ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket Notifications"])


@router.websocket("/ws/notifications/{user_id}")
async def notification_websocket_endpoint(
    websocket: WebSocket,
    user_id: UUID,
    token: str = Query(..., description="JWT access token aplikasi"),
):
    authenticated_user: User | None = await authenticate_ws_token(token)
    if not authenticated_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if authenticated_user.uuid != user_id:
        logger.warning(
            "[WS Notif] user_id mismatch: token=%s path=%s",
            authenticated_user.uuid,
            user_id,
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await notification_ws_manager.connect(authenticated_user.uuid, websocket)

    try:
        await websocket.send_json(
            {
                "type": "connection_established",
                "data": {
                    "user_id": str(authenticated_user.uuid),
                    "unread_count": await count_unread(authenticated_user.uuid),
                },
            }
        )
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        notification_ws_manager.disconnect(authenticated_user.uuid, websocket)
    except Exception as exc:
        logger.warning("[WS Notif] koneksi error: %s", exc)
        notification_ws_manager.disconnect(authenticated_user.uuid, websocket)
