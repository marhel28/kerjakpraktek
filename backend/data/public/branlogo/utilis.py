from backend.db.main import db_session_maker
from .service import refresh_brand_cache, BRAND_LOCK_KEY
from redis.asyncio import Redis

# =========================
# SAFE BACKGROUND TASK (BRAND LOGO)
# =========================

async def refresh_brand_cache_safe(redis: Redis):
    """
    Menjalankan refresh cache Brand secara aman dengan Atomic Lock.
    Mencegah multiple workers melakukan query berat ke DB di waktu yang sama.
    """
    success = await redis.set(BRAND_LOCK_KEY, "1", ex=10, nx=True)
    
    if not success:
        # Berarti proses refresh sedang berjalan oleh task lain, kita skip saja.
        return 

    try:
        # Membuka session database baru karena task ini biasanya jalan di Background
        async with db_session_maker() as session:
            await refresh_brand_cache(session, redis)
            
    finally:
        # Lepas lock setelah selesai agar admin bisa memicu update lagi nanti.
        await redis.delete(BRAND_LOCK_KEY)