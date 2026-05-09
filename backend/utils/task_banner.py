from backend.db.main import db_session_maker
from backend.data.public.xbanner.service import refresh_banner_cache, LOCK_KEY
from redis.asyncio import Redis

# =========================
# SAFE BACKGROUND TASK (ATOMIC VERSION)
# =========================

async def refresh_banner_cache_safe(redis: Redis):
    # 🔥 ATOMIC LOCK: 'nx=True' akan mengembalikan True hanya jika key belum ada.
    # Ini mencegah race condition secara sempurna.
    success = await redis.set(LOCK_KEY, "1", ex=10, nx=True)
    
    if not success:
        # Berarti sudah ada worker lain yang sedang memproses refresh
        return 

    try:
        # Gunakan session maker untuk membuat session baru di background
        async with db_session_maker() as session:
            await refresh_banner_cache(session, redis)
    finally:
        # Lepas lock agar admin bisa update lagi nanti
        await redis.delete(LOCK_KEY)