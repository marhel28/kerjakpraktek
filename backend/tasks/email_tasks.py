import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery.utils.log import get_task_logger
from backend.celery_app import celery_app

logger = get_task_logger(__name__)


def _build_email(
    to: str,
    subject: str,
    html: str,
    from_addr: str
) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))
    return msg


def _send_smtp(msg: MIMEMultipart, to: str) -> None:
    from backend.config import Config
    with smtplib.SMTP_SSL(Config.SMTP_HOST, int(Config.SMTP_SERVER_PORT)) as server:
        server.login(Config.EMAIL_APPS, Config.SANDIAPPS)
        print("ok")
        server.sendmail(Config.EMAIL_APPS, to, msg.as_string())


@celery_app.task(
    bind=True,
    name="backend.tasks.email_tasks.send_verification_email",
    queue="email",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_verification_email_task(
    self, email: str, token: str, frontend_url: str
):
    from backend.config import Config

    verify_url = f"{frontend_url}/auth/verify-email?token={token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;
                padding:32px;background:#fff;border-radius:16px;
                border:1px solid #e5e7eb">
      <h2 style="font-size:20px;font-weight:900;color:#111827;margin-bottom:8px">
        Verifikasi Email Kamu
      </h2>
      <p style="color:#6b7280;font-size:14px;line-height:1.6;margin-bottom:24px">
        Klik tombol di bawah untuk mengaktifkan akun.
        Link berlaku <strong style="color:#111">10 menit</strong>.
      </p>
      <a href="{verify_url}"
         style="display:block;text-align:center;padding:14px;background:#32cd32;
                color:#fff;border-radius:10px;text-decoration:none;
                font-weight:800;font-size:15px">
        Verifikasi Sekarang
      </a>
      <p style="color:#9ca3af;font-size:11px;margin-top:24px;text-align:center">
        Akun akan otomatis dihapus setelah 10 menit jika tidak diverifikasi.
      </p>
    </div>
    """
    msg = _build_email(
        email,
        "Verifikasi Akun — Padjajaran CCTV",
        html,
        Config.EMAIL_APPS
    )
    _send_smtp(msg, email)
    logger.info(f"✅ Verification email sent: {email}")


@celery_app.task(
    bind=True,
    name="backend.tasks.email_tasks.send_reset_password_email",
    queue="email",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_reset_password_email_task(
    self, email: str, token: str, frontend_url: str
):
    from backend.config import Config

    reset_url = f"{frontend_url}/auth/reset-password?token={token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;
                padding:32px;background:#fff;border-radius:16px;
                border:1px solid #e5e7eb">
      <h2 style="font-size:20px;font-weight:900;color:#111827;margin-bottom:8px">
        Reset Password
      </h2>
      <p style="color:#6b7280;font-size:14px;line-height:1.6;margin-bottom:24px">
        Klik tombol di bawah untuk membuat password baru.
        Link berlaku <strong style="color:#111">15 menit</strong>.
      </p>
      <a href="{reset_url}"
         style="display:block;text-align:center;padding:14px;background:#111827;
                color:#fff;border-radius:10px;text-decoration:none;
                font-weight:800;font-size:15px">
        Reset Password
      </a>
      <p style="color:#9ca3af;font-size:11px;margin-top:24px;text-align:center">
        Jika kamu tidak meminta ini, abaikan email ini.
      </p>
    </div>
    """
    msg = _build_email(
        email,
        "Reset Password — Padjajaran CCTV",
        html,
        Config.EMAIL_APPS
    )
    _send_smtp(msg, email)
    logger.info(f"✅ Reset password email sent: {email}")



@celery_app.task(
    bind=True,
    name="backend.tasks.email_tasks.send_generic_email_task",
    queue="email",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_generic_email_task(self, to: str, subject: str, html_content: str):
    from backend.config import Config
    
    msg = _build_email(to, subject, html_content, Config.EMAIL_APPS)
    _send_smtp(msg, to)
    logger.info(f"✅ Generic email sent to: {to}")