"""Autentikasi JWT untuk endpoint WebSocket.

Dipakai bersama oleh WS chat dan WS notifikasi supaya aturan token,
blacklist Redis, dan status user tidak berbeda antar endpoint.
"""

from typing import Optional

from backend.auth.model import User
from backend.auth.service import UserService
from backend.auth.utility import decode_token
from backend.db.main import db_session_maker
from backend.db.redis import token_jti_bloclist

user_service = UserService()


async def authenticate_ws_token(token: str) -> Optional[User]:
    """Validasi JWT aplikasi; session DB dibuka-tutup sendiri (tanpa Depends)."""
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
        db.expunge(user)
        return user
