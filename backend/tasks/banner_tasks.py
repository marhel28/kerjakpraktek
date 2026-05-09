from celery.utils.log import get_task_logger
from backend.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(
    name="backend.tasks.banner_tasks.refresh_banner_cache",
    queue="default",
    max_retries=3,
    default_retry_delay=30,
)
def refresh_banner_cache():
    """
    Periodic task: refresh banner cache di Redis setiap 5 menit.
    Menggantikan refresh manual di lifespan.
    """
    import asyncio
    from backend.db.redis import get_redis_token
    from backend.utils.task_banner import refresh_banner_cache_safe

    async def _run():
        redis = get_redis_token()
        await refresh_banner_cache_safe(redis)
        logger.info("✅ Banner cache refreshed by Celery Beat")

    asyncio.run(_run())