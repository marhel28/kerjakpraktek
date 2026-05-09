import asyncio
import logging
import pytz
from datetime import datetime, timedelta
from celery.utils.log import get_task_logger
from backend.celery_app import celery_app

logger = get_task_logger(__name__)
jakarta_tz = pytz.timezone("Asia/Jakarta")


def _run_async(coro):
    """Helper: jalankan coroutine dari sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="backend.tasks.auth_tasks.schedule_unverified_cleanup",
    queue="auth",
    max_retries=2,
    default_retry_delay=60,
)
def schedule_unverified_cleanup(email: str):
    """
    Dipanggil dengan countdown=660 saat register.
    Hapus akun jika masih belum verified setelah 11 menit.
    """
    async def _run():
        from backend.db.main import dB_engine
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import select  # 🔥 ganti dari sqlmodel
        from backend.auth.model import User
        from backend.db.main import AsyncSessionCelery
        
        async with AsyncSessionCelery()  as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()  # 🔥 lebih tepat

            if user and not user.is_verified:
                await session.delete(user)
                await session.commit()
                logger.info(f"🗑️  Unverified account deleted: {email}")
            else:
                logger.info(f"ℹ️  Account already verified or not found: {email}")

    _run_async(_run())

@celery_app.task(
    name="backend.tasks.auth_tasks.cleanup_unverified_accounts_batch",
    queue="auth",
)
def cleanup_unverified_accounts_batch():
    """
    Safety net — dijalankan Celery Beat setiap 2 menit.
    Hapus semua akun unverified yang sudah lewat 10 menit.
    """
    async def _run():
        from backend.db.main import dB_engine
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlmodel import select
        from backend.auth.model import User

        cutoff = datetime.now(jakarta_tz) - timedelta(minutes=10)
        from backend.db.main import AsyncSessionCelery
        async with AsyncSession(AsyncSessionCelery) as session:
            result = await session.exec(
                select(User).where(
                    User.is_verified == False,
                    User.google_id == None,   # Jangan hapus Google user
                    User.waktu_create <= cutoff,
                )
            )
            users = result.all()
            if not users:
                return

            for user in users:
                await session.delete(user)

            await session.commit()
            logger.info(f"🗑️  Batch cleanup: {len(users)} unverified accounts deleted")

    _run_async(_run())