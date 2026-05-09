from backend.config import Config
from redis.asyncio import Redis, ConnectionPool
from functools import lru_cache

EXPIRE_JTI_TIME   = 3600   # 1 jam
VERIFY_TOKEN_EXPIRE = 600  # 10 menit
RESET_TOKEN_EXPIRE  = 900  # 15 menit
COUPON_CACHE_TTL    = 300  # 5 menit


@lru_cache()
def get_redis_token() -> Redis:
    pool = ConnectionPool(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=0,
        max_connections=200,
        # ⚠️ decode_responses=True agar semua nilai string langsung
        # Tidak perlu .decode("utf-8") manual di mana-mana
        decode_responses=True,
    )
    return Redis(connection_pool=pool)


# ── JTI blocklist ──────────────────────────────────────────────────
async def add_jti_to_blocklist(jti: str) -> None:
    await get_redis_token().set(jti, "revoked", ex=EXPIRE_JTI_TIME)


async def token_jti_bloclist(jti: str) -> bool:
    val = await get_redis_token().get(jti)
    return val is not None


# ── Email verification ─────────────────────────────────────────────
async def save_email_verification_token(token: str, email: str) -> bool:
    r = get_redis_token()
    existing = await r.get(f"verify_active:{email}")
    if existing:
        return False
    pipe = r.pipeline()
    pipe.set(f"verify:{token}", email, ex=VERIFY_TOKEN_EXPIRE)
    pipe.set(f"verify_active:{email}", token, ex=VERIFY_TOKEN_EXPIRE)
    await pipe.execute()
    return True


async def get_email_from_verification_token(token: str) -> str | None:
    r = get_redis_token()
    email = await r.get(f"verify:{token}")
    if not email:
        return None
    # decode_responses=True — sudah string, tidak perlu .decode()
    pipe = r.pipeline()
    pipe.delete(f"verify:{token}")
    pipe.delete(f"verify_active:{email}")
    await pipe.execute()
    return email


# ── Password reset ─────────────────────────────────────────────────
async def save_password_reset_token(token: str, email: str) -> bool:
    r = get_redis_token()
    existing = await r.get(f"reset_active:{email}")
    if existing:
        return False
    pipe = r.pipeline()
    pipe.set(f"reset:{token}", email, ex=RESET_TOKEN_EXPIRE)
    pipe.set(f"reset_active:{email}", token, ex=RESET_TOKEN_EXPIRE)
    await pipe.execute()
    return True


async def get_email_from_reset_token(token: str) -> str | None:
    r = get_redis_token()
    email = await r.get(f"reset:{token}")
    if not email:
        return None
    pipe = r.pipeline()
    pipe.delete(f"reset:{token}")
    pipe.delete(f"reset_active:{email}")
    await pipe.execute()
    return email


# ── Coupon cache helpers ───────────────────────────────────────────
# Dragonfly-optimized: pipeline untuk batch ops
async def cache_coupon(code: str, payload: str) -> None:
    """Simpan coupon JSON ke Redis dengan TTL 5 menit."""
    await get_redis_token().set(f"coupon:{code.upper()}", payload, ex=COUPON_CACHE_TTL)


async def get_cached_coupon(code: str) -> str | None:
    return await get_redis_token().get(f"coupon:{code.upper()}")


async def invalidate_coupon_cache(code: str) -> None:
    """Hapus cache satu kupon."""
    await get_redis_token().delete(f"coupon:{code.upper()}")


async def invalidate_all_coupon_cache() -> None:
    """
    Scan + hapus semua key coupon:*.
    Dragonfly mendukung SCAN — lebih aman dari KEYS di production.
    """
    r = get_redis_token()
    cursor = 0
    keys_to_delete = []
    while True:
        cursor, keys = await r.scan(cursor, match="coupon:*", count=100)
        keys_to_delete.extend(keys)
        if cursor == 0:
            break
    if keys_to_delete:
        await r.delete(*keys_to_delete)