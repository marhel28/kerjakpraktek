import asyncio
import logging
from celery.utils.log import get_task_logger
from backend.celery_app import celery_app

logger = get_task_logger(__name__)


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="backend.tasks.coupon_tasks.hard_delete_coupon_task",
    queue="default",
    max_retries=3,
    default_retry_delay=300,
)
def hard_delete_coupon_task(code: str):
    """
    Hard delete kupon setelah 30 hari dari soft delete.
    Dipanggil via apply_async(countdown=30*24*3600).
    """
    async def _run_async():
        from backend.db.main import engine
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlmodel import select
        from backend.data.stock.model import Coupon
        from backend.db.redis import invalidate_coupon_cache

        async with AsyncSession(engine) as session:
            result = await session.exec(
                select(Coupon).where(
                    Coupon.code == code.upper(),
                    Coupon.deleted_at != None,   # hanya yang sudah soft-deleted
                )
            )
            coupon = result.first()
            if coupon:
                await session.delete(coupon)
                await session.commit()
                await invalidate_coupon_cache(code)
                logger.info(f"🗑️ Hard deleted coupon: {code}")
            else:
                logger.info(f"ℹ️ Coupon {code} not found or not soft-deleted, skip.")

    _run(_run_async())


@celery_app.task(
    name="backend.tasks.coupon_tasks.cleanup_expired_coupons",
    queue="default",
)
def cleanup_expired_coupons():
    """
    Periodic task via Beat: soft-delete semua kupon yang sudah expired
    (valid_until < now) dan masih is_active=True.
    Jadwal di celery_app.py: setiap hari jam 02:00 WIB.
    """
    async def _run_async():
        from datetime import datetime, timezone
        from backend.db.main import engine
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlmodel import select
        from backend.data.stock.model import Coupon
        from backend.db.redis import invalidate_coupon_cache

        now = datetime.now(timezone.utc)

        async with AsyncSession(engine) as session:
            result = await session.exec(
                select(Coupon).where(
                    Coupon.is_active == True,
                    Coupon.deleted_at == None,
                    Coupon.valid_until != None,
                    Coupon.valid_until < now,
                )
            )
            expired = result.all()
            if not expired:
                return

            for coupon in expired:
                coupon.is_active = False
                coupon.deleted_at = now
                session.add(coupon)
                await invalidate_coupon_cache(coupon.code)

            await session.commit()
            logger.info(f"🕐 Auto-deactivated {len(expired)} expired coupons")

    _run(_run_async())