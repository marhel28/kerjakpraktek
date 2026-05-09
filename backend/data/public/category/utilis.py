import uuid
from backend.db.main import db_session_maker
from .service import refresh_category_cache, CAT_CACHE_KEY
from redis import Redis

async def refresh_category_cache_safe(redis: Redis):
    lock_key = "lock:category:refresh"
    lock_id = str(uuid.uuid4())

    # short lock only (avoid long holding)
    acquired = await redis.set(lock_key, lock_id, ex=5, nx=True)

    if not acquired:
        return

    try:
        async with db_session_maker() as session:
            await refresh_category_cache(session, redis)

    finally:
        val = await redis.get(lock_key)
        if val and val.decode() == lock_id:
            await redis.delete(lock_key)