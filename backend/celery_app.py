from celery import Celery
from celery.schedules import crontab
from backend.config import Config

celery_app = Celery(
    "marketplace",
    broker=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/1",
    backend=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/2",
    include=[
        "backend.tasks.auth_tasks",
        "backend.tasks.banner_tasks",
        "backend.tasks.email_tasks",
        "backend.tasks.promo_tasks",          
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,

    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    task_ignore_result=False,
    task_default_rate_limit="100/m",
    task_max_retries=3,
    task_default_retry_delay=60,

    task_routes={
        "backend.tasks.email_tasks.*":  {"queue": "email"},
        "backend.tasks.auth_tasks.*":   {"queue": "auth"},
        "backend.tasks.banner_tasks.*": {"queue": "default"},
        "backend.tasks.promo_tasks.*":  {"queue": "email"},   # ✅ promo tasks masuk queue email
    },

    beat_schedule={
        "refresh-banner-cache": {
            "task": "backend.tasks.banner_tasks.refresh_banner_cache",
            "schedule": crontab(minute="*/5"),
            "options": {"queue": "default"},
        },
        "cleanup-unverified-accounts": {
            "task": "backend.tasks.auth_tasks.cleanup_unverified_accounts_batch",
            "schedule": crontab(minute="*/2"),
            "options": {"queue": "auth"},
        },
        "cleanup-expired-coupons": {
            "task": "backend.tasks.coupon_tasks.cleanup_expired_coupons",
            "schedule": crontab(hour=2, minute=0),
            "options": {"queue": "default"},
        },
        # ✅ Tambahan: cek promo hampir habis setiap hari jam 09:00 WIB
        "check-promos-ending-soon": {
            "task": "backend.tasks.promo_tasks.notify_promo_ending_soon",
            "schedule": crontab(hour=9, minute=0),
            "options": {"queue": "email"},
        },
    },
)