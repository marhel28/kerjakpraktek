from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import uuid
import logging
import httpx
from fastapi import HTTPException
from backend.config import Config

logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE = 3600       # 1 jam
REFRESH_TOKEN_EXPIRE_DAYS = 7

password_context = CryptContext(schemes=["argon2"], deprecated="auto")


def generate_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_hash(password: str, hashed: str) -> bool:
    return password_context.verify(password, hashed)


def create_access_token(
    user_data: dict,
    expired: timedelta = None,
    refresh: bool = False
) -> str:
    payload = {
        "user": user_data,
        "exp": datetime.utcnow() + (expired or timedelta(seconds=ACCESS_TOKEN_EXPIRE)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM],   # harus list
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


def build_user_payload(user) -> dict:
    """Helper: buat payload token dari User object."""
    return {
        "uuid": str(user.uuid),
        "email": user.email,
        "username": user.username,
        "role": user.role,
    }


# ── Google token verifier ──────────────────────────────────────────
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

async def verify_google_id_token(id_token: str) -> dict:
    """
    Verifikasi id_token Google ke endpoint resmi Google.
    Return payload jika valid.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(
            GOOGLE_TOKENINFO_URL,
            params={"id_token": id_token}
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Google token tidak valid")

    data = resp.json()

    if data.get("aud") != Config.CLIENT_ID:
        raise HTTPException(
            status_code=401,
            detail="Token tidak ditujukan untuk aplikasi ini"
        )

    if data.get("email_verified") != "true":
        raise HTTPException(
            status_code=401,
            detail="Email Google belum diverifikasi"
        )

    return data