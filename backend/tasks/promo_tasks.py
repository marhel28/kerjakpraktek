import asyncio
import logging
from celery import shared_task
from datetime import datetime, timedelta
import pytz
from sqlmodel import select
from backend.db.main import AsyncSessionCelery
from backend.user.notifications import notify_users
from .email_tasks import send_generic_email_task
from backend.data.public.promobanner.model import Promo, PromoStatus
from backend.auth.model import User

logger = logging.getLogger(__name__)
WIB = pytz.timezone("Asia/Jakarta")

def get_or_create_loop():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Loop is closed")
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def notify_promo_ending_soon(self):
    async def _run():
        now = datetime.now(WIB)
        threshold = now + timedelta(hours=24)

        async with AsyncSessionCelery() as session:
            stmt1 = select(Promo).where(
                Promo.status == PromoStatus.ACTIVE,
                Promo.valid_until <= threshold,
                Promo.valid_until > now,
            )
            stmt2 = select(Promo).where(
                Promo.status == PromoStatus.ACTIVE,
                Promo.quota.is_not(None),
                Promo.quota > 0,
                (Promo.used_count * 100 / Promo.quota) >= 90,
            )
            res1 = await session.execute(stmt1)
            res2 = await session.execute(stmt2)
            promos = list(res1.scalars().all()) + list(res2.scalars().all())

            if not promos:
                logger.info("Tidak ada promo yang akan berakhir.")
                return

            stmt_users = select(User).where(
                User.is_verified == True,
                User.email.is_not(None),
            )
            users = (await session.execute(stmt_users)).scalars().all()

            emails = [user.email for user in users if user.email]
            user_ids = [user.uuid for user in users]

            if not emails and not user_ids:
                return

            for promo in promos:
                title = f"⏳ Promo Segera Berakhir: {promo.name}"
                content = (
                    f"Promo '{promo.name}' berakhir pada "
                    f"{promo.valid_until.astimezone(WIB).strftime('%d %b %Y %H:%M')} WIB. "
                    "Manfaatkan sebelum kehabisan!"
                )
                action_url = f"/promo/{promo.slug}"

                if user_ids:
                    try:
                        await notify_users(
                            user_ids=user_ids,
                            title=title,
                            content=content,
                            action_url=action_url,
                            notif_type="promo_ending",
                        )
                    except Exception as e:
                        logger.error(f"Bulk notif failed for ending promo: {e}")

                for email in emails:
                    html_content = f"""
                    <h3>{title}</h3>
                    <p>{content}</p>
                    <a href="{action_url}">Lihat Promo</a>
                    """
                    send_generic_email_task.delay(email, title, html_content)

    loop = get_or_create_loop()
    try:
        loop.run_until_complete(_run())
    except Exception as exc:
        logger.error(f"notify_promo_ending_soon error: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def notify_new_promo(self, promo_uuid: str):
    async def _run():
        async with AsyncSessionCelery() as session:
            promo = await session.get(Promo, promo_uuid)
            if not promo:
                logger.error(f"Promo {promo_uuid} tidak ditemukan")
                return

            stmt_users = select(User).where(
                User.is_verified == True,
                User.email.is_not(None),
            )
            users = (await session.execute(stmt_users)).scalars().all()

            emails = [user.email for user in users if user.email]
            user_ids = [user.uuid for user in users]

            title = f"🎉 Promo Baru: {promo.name}"
            content = promo.description or f"Segera cek promo {promo.name}"
            action_url = f"/promo/{promo.slug}"

            if user_ids:
                try:
                    await notify_users(
                        user_ids=user_ids,
                        title=title,
                        content=content,
                        action_url=action_url,
                        notif_type="promo_new",
                    )
                except Exception as e:
                    logger.error(f"Bulk notif failed for new promo: {e}")
            
            for email in emails:
                html_content = f"""
                <h3>{title}</h3>
                <p>{content}</p>
                <a href="{action_url}">Lihat Sekarang</a>
                """
                send_generic_email_task.delay(email, title, html_content)

    loop = get_or_create_loop()
    try:
        loop.run_until_complete(_run())
    except Exception as exc:
        logger.error(f"notify_new_promo error: {exc}", exc_info=True)
        raise self.retry(exc=exc)