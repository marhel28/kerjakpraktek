import uuid
import asyncio
from backend.db.main import db_session_maker
from .service import refresh_category_cache, CAT_CACHE_KEY
from redis.asyncio import Redis

async def refresh_category_cache_safe(redis: Redis):
    """
    Background task aman untuk me-refresh cache kategori.
    Dilengkapi dengan locking dan jeda sinkronisasi DB untuk mencegah zombie data.
    """
    lock_key = "lock:category:refresh"
    lock_id = str(uuid.uuid4())

    # 1. Acquire Lock (TTL 10s untuk safety)
    acquired = await redis.set(lock_key, lock_id, ex=10, nx=True)

    if not acquired:
        return

    try:
        # 2. Jeda singkat untuk memastikan transaksi DB asal sudah ter-commit sepenuhnya
        await asyncio.sleep(0.5)

        # 3. Invalidate cache lama sebelum rebuild
        await redis.delete(CAT_CACHE_KEY)

        # 4. Rebuild menggunakan session baru yang segar
        async with db_session_maker() as session:
            await refresh_category_cache(session, redis)

    except Exception as e:
        # Silently log error or handle it as per production standards
        print(f"[CACHE_REFRESH_ERROR] {str(e)}")
    finally:
        # 5. Release Lock secara aman
        val = await redis.get(lock_key)
        if val and val.decode() == lock_id:
            await redis.delete(lock_key)