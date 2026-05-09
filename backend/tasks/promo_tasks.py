import asyncio
import logging
from celery import shared_task
from datetime import datetime, timedelta
import pytz
from sqlmodel import select
from sqlalchemy import cast, String
from backend.db.main import AsyncSessionCelery
from backend.db.supabse import SupabaseNotificationService
from .email_tasks import send_generic_email_task
from backend.data.public.promobanner.model import Promo, PromoStatus
from backend.auth.model import User, UserMap

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

            # ✅ FIX: Ambil User + UserMap menggunakan Outer Join
            stmt_users = (
                select(User, UserMap)
                .outerjoin(UserMap, cast(User.uuid, String) == UserMap.local_user_id)
                .where(
                    User.is_verified == True,
                    User.email.is_not(None),
                )
            )
            user_results = (await session.execute(stmt_users)).all()

            # Pisahkan list email (untuk semua user) dan list supabase_id (hanya jika ada di UserMap)
            emails = [row.User.email for row in user_results if row.User.email]
            supabase_user_ids = [row.UserMap.supabase_user_id for row in user_results if row.UserMap]

            if not emails and not supabase_user_ids:
                return

            for promo in promos:
                title = f"⏳ Promo Segera Berakhir: {promo.name}"
                content = (
                    f"Promo '{promo.name}' berakhir pada "
                    f"{promo.valid_until.astimezone(WIB).strftime('%d %b %Y %H:%M')} WIB. "
                    "Manfaatkan sebelum kehabisan!"
                )
                action_url = f"/promo/{promo.slug}"

                if supabase_user_ids:
                    try:
                        await SupabaseNotificationService.bulk_notification(
                            user_ids=supabase_user_ids,
                            title=title,
                            content=content,
                            action_url=action_url,
                            notif_type="promo_ending",
                        )
                    except Exception as e:
                        logger.error(f"Supabase bulk notif failed for ending promo: {e}")

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

            # ✅ FIX: Ambil User + UserMap menggunakan Outer Join
            stmt_users = (
                select(User, UserMap)
                .outerjoin(UserMap, cast(User.uuid, String) == UserMap.local_user_id)
                .where(
                    User.is_verified == True,
                    User.email.is_not(None),
                )
            )
            user_results = (await session.execute(stmt_users)).all()

            # Pisahkan list email (untuk semua user) dan list supabase_id (hanya jika ada di UserMap)
            emails = [row.User.email for row in user_results if row.User.email]
            supabase_user_ids = [row.UserMap.supabase_user_id for row in user_results if row.UserMap]

            title = f"🎉 Promo Baru: {promo.name}"
            content = promo.description or f"Segera cek promo {promo.name}"
            action_url = f"/promo/{promo.slug}"

            if supabase_user_ids:
                try:
                    await SupabaseNotificationService.bulk_notification(
                        user_ids=supabase_user_ids,
                        title=title,
                        content=content,
                        action_url=action_url,
                        notif_type="promo_new",
                    )
                except Exception as e:
                    logger.error(f"Supabase bulk notif failed for new promo: {e}")
            
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