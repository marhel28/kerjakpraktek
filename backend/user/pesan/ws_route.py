import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from backend.auth.utility import decode_token
from backend.auth.service import UserService
from backend.auth.model import User, UserRole
from backend.db.redis import token_jti_bloclist
from backend.db.main import db_session_maker
from backend.user.pesan.ws_manager import chat_ws_manager

logger = logging.getLogger(__name__)
user_service = UserService()

router = APIRouter(tags=["WebSocket Chat"])


async def authenticate_ws_token(token: str) -> Optional[User]:
    """
    Validasi JWT token dari query param WebSocket.
    Mengecek payload, expiration, dan blacklist Redis.
    Session DB dibuka-tutup sendiri agar tidak bocor (get_session adalah
    async generator yang harus di-close; di konteks WS tidak ada Depends).
    """
    token_data = decode_token(token)
    if not token_data:
        return None

    if "user" not in token_data or "email" not in token_data["user"]:
        return None

    jti = token_data.get("jti")
    if jti and await token_jti_bloclist(jti):
        return None

    user_email = token_data["user"]["email"]
    async with db_session_maker() as db:
        user = await user_service.get_user_by_email(user_email, db)
        if not user or not user.is_verified:
            return None
        # Detach agar bisa dipakai setelah session close (hanya field sederhana)
        db.expunge(user)
        return user


@router.websocket("/ws/chat/{user_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    user_id: UUID,
    token: str = Query(..., description="Bearer JWT access token"),
):
    """
    Duplex WebSocket untuk sistem pesan customer ↔ admin.
    URL: ws://{host}/ws/chat/{user_id}?token={token}
    """
    authenticated_user: Optional[User] = await authenticate_ws_token(token)

    if not authenticated_user:
        logger.warning("[WS Chat] Unauthorized connection rejected for user_id: %s", user_id)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    is_admin = authenticated_user.role == UserRole.ADMIN

    # Jika bukan admin, pastikan user_id pada path cocok dengan user_id di token
    if not is_admin and authenticated_user.uuid != user_id:
        logger.warning(
            f"[WS Chat] Forbidden user_id mismatch: token user={authenticated_user.uuid} vs path={user_id}"
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await chat_ws_manager.connect(authenticated_user.uuid, websocket, is_admin=is_admin)

    try:
        # Kirim event koneksi berhasil
        await websocket.send_json({
            "type": "connection_established",
            "data": {
                "user_id": str(authenticated_user.uuid),
                "is_admin": is_admin,
            },
        })

        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "ping" or event_type == "pong":
                await websocket.send_json({"type": "pong" if event_type == "ping" else "ping"})
            elif event_type == "typing":
                # Forward typing status ke lawan bicara
                target_user_id = data.get("target_user_id")
                if is_admin and target_user_id:
                    try:
                        await chat_ws_manager.send_to_user(
                            UUID(str(target_user_id)),
                            {"type": "typing", "sender": "admin"},
                        )
                    except (ValueError, AttributeError):
                        logger.warning("[WS Chat] Invalid target_user_id: %r", target_user_id)
                elif not is_admin:
                    await chat_ws_manager.broadcast_to_admins({
                        "type": "typing",
                        "sender": "user",
                        "user_id": str(authenticated_user.uuid),
                    })

    except WebSocketDisconnect:
        chat_ws_manager.disconnect(authenticated_user.uuid, websocket, is_admin=is_admin)
        logger.info(f"[WS Chat] Socket cleanly disconnected for user {authenticated_user.uuid}")
    except Exception as e:
        chat_ws_manager.disconnect(authenticated_user.uuid, websocket, is_admin=is_admin)
        logger.error(f"[WS Chat] Socket error: {e}")
