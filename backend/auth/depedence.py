import logging
from typing import Optional
from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from .utility import decode_token
from .service import UserService
from .model import User, UserRole
from backend.db.redis import token_jti_bloclist
from backend.db.main import get_session

logger = logging.getLogger(__name__)
user_service = UserService()



class TokenBearer(HTTPBearer):
    """Base class — validasi token structure & blocklist."""

    async def __call__(self, request: Request) -> dict:
        cred: HTTPAuthorizationCredentials = await super().__call__(request)
        token = cred.credentials

        token_data = decode_token(token)
        if token_data is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid atau sudah kadaluarsa"
            )

        # Validasi structure payload
        if "user" not in token_data or "uuid" not in token_data.get("user", {}):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Struktur token tidak valid"
            )

        # Cek blocklist Redis
        if await token_jti_bloclist(token_data["jti"]):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Token sudah dicabut. Silakan login ulang."
            )

        self.verify_token_type(token_data)
        return token_data

    def verify_token_type(self, token_data: dict) -> None:
        raise NotImplementedError


class AccessTokenBearer(TokenBearer):
    def verify_token_type(self, token_data: dict) -> None:
        if token_data.get("refresh"):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Gunakan access token, bukan refresh token"
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_type(self, token_data: dict) -> None:
        if not token_data.get("refresh"):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Gunakan refresh token"
            )


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        user_email = token_details["user"]["email"]
    except (KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Payload token tidak valid"
        )

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Akun belum diverifikasi"
        )
    return user


async def get_admin(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        user_email = token_details["user"]["email"]
    except (KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Payload token tidak valid")

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    # Bug fix dari kode asli: logika terbalik & case salah
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Akses ditolak: bukan admin")

    return user


async def get_optional_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    try:
        if not auth_header.lower().startswith("bearer "):
            return None
        token = auth_header.split(" ")[1]
        token_data = decode_token(token)
        if token_data is None:
            return None
        
        # Structure validation
        if "user" not in token_data or "uuid" not in token_data.get("user", {}):
            return None

        # Check blocklist Redis
        if await token_jti_bloclist(token_data["jti"]):
            return None

        user_email = token_data["user"]["email"]
        user = await user_service.get_user_by_email(user_email, session)
        if not user or not user.is_verified:
            return None
        return user
    except Exception as e:
        logger.warning(f"get_optional_current_user error parsing token: {e}")
        return None