import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from .service import UserService
from .schema import (
    UserCreate, UserLogin, UserRead,
    UserProfileUpdate, EmailRequest,
    ResetPasswordRequest, ChangePasswordRequest,
    GoogleAuthRequest, TokenResponse, SupabaseSession, SupabaseUserData,
)
from .depedence import (
    AccessTokenBearer, RefreshTokenBearer,
    get_current_user, get_admin,
)
from .utility import create_access_token, build_user_payload
from .model import User
from backend.db.redis import add_jti_to_blocklist
from backend.db.main import get_session
from backend.tasks.auth_tasks import schedule_unverified_cleanup
from backend.tasks.email_tasks import (
    send_verification_email_task,
    send_reset_password_email_task,
)
from backend.config import Config
from .supabase_auth import supabase_auth_bridge  # ← NEW

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
user_router = APIRouter(prefix="/users", tags=["Users"])

user_service = UserService()


# ── Register ───────────────────────────────────────────────────────
@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi akun baru"
)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.create_user(user_data, session)

    token = await user_service.generate_verification_token(user.email)
    if token:
        send_verification_email_task.delay(
            user.email, token, Config.FRONTEND_URL
        )

    schedule_unverified_cleanup.apply_async(
        args=[user.email],
        countdown=660,
    )

    return {
        "message": "Registrasi berhasil. Cek email kamu untuk verifikasi akun.",
        "email": user.email,
    }


# ── Verify Email ───────────────────────────────────────────────────
@auth_router.get(
    "/verify-email",
    summary="Verifikasi email via link"
)
async def verify_email(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.verify_email(token, session)


# ── Resend Verification ────────────────────────────────────────────
@auth_router.post(
    "/resend-verification",
    summary="Kirim ulang email verifikasi"
)
async def resend_verification(
    data: EmailRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_email(
        data.email.lower().strip(), session
    )

    if user and not user.is_verified:
        token = await user_service.generate_verification_token(user.email)
        if token:
            send_verification_email_task.delay(
                user.email, token, Config.FRONTEND_URL
            )
            schedule_unverified_cleanup.apply_async(
                args=[user.email],
                countdown=660,
            )

    return {
        "message": "Jika email terdaftar dan belum diverifikasi, link baru telah dikirim."
    }


# ── Login ──────────────────────────────────────────────────────────
@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login dengan email & password"
)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    # Auth utama — tidak berubah
    user = await user_service.authenticate_user(
        credentials.email, credentials.password, session
    )

    payload = build_user_payload(user)
    access_token = create_access_token(payload)
    refresh_token = create_access_token(
        payload,
        expired=timedelta(days=7),
        refresh=True
    )

    # ── Supabase Bridge ────────────────────────────────────────────
    # Jalankan async, tapi TIDAK block login jika Supabase gagal
    supabase_data: SupabaseSession | None = None
    try:
        sb_session = await supabase_auth_bridge.get_or_create_supabase_session(
            local_user_id=user.uuid,
            email=user.email,
            session=session,
        )
        if sb_session:
            sb_user = sb_session.get("user", {})
            supabase_data = SupabaseSession(
                access_token=sb_session["access_token"],
                refresh_token=sb_session["refresh_token"],
                user=SupabaseUserData(
                    id=sb_user.get("id") or sb_user.get("uuid") or sb_user.get("sub", ""),
                    email=sb_user.get("email", user.email),
                ),
            )
    except Exception as e:
        logger.error(f"Supabase bridge failed silently for user {user.uuid}: {e}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
        supabase=supabase_data,  # None jika Supabase down — frontend handle gracefully
    )


# ── Google OAuth ───────────────────────────────────────────────────
@auth_router.post(
    "/google",
    response_model=TokenResponse,
    summary="Login atau register via Google"
)
async def google_auth(
    payload: GoogleAuthRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.login_or_register_google(
        payload.id_token, session
    )

    token_payload = build_user_payload(user)
    access_token = create_access_token(token_payload)
    refresh_token = create_access_token(
        token_payload,
        expired=timedelta(days=7),
        refresh=True
    )

    # ── Supabase Bridge ────────────────────────────────────────────
    supabase_data: SupabaseSession | None = None
    try:
        sb_session = await supabase_auth_bridge.get_or_create_supabase_session(
            local_user_id=user.uuid,
            email=user.email,
            session=session,
        )
        if sb_session:
            sb_user = sb_session.get("user", {})
            supabase_data = SupabaseSession(
                access_token=sb_session["access_token"],
                refresh_token=sb_session["refresh_token"],
                user=SupabaseUserData(
                    id=sb_user.get("id") or sb_user.get("uuid") or sb_user.get("sub", ""),
                    email=sb_user.get("email", user.email),
                ),
            )
    except Exception as e:
        logger.error(f"Supabase bridge failed silently for Google user {user.id}: {e}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
        supabase=supabase_data,
    )


# ── Refresh Token ──────────────────────────────────────────────────
@auth_router.post(
    "/refresh",
    summary="Dapatkan access token baru via refresh token"
)
async def refresh_token(
    token_details: dict = Depends(RefreshTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_data = token_details.get("user", {})
    user = await user_service.get_user_by_email(
        user_data.get("email", ""), session
    )

    if not user or not user.is_verified:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="Akun tidak valid atau belum diverifikasi"
        )

    new_access = create_access_token(build_user_payload(user))
    return {
        "access_token": new_access,
        "token_type": "bearer"
    }


# ── Logout ─────────────────────────────────────────────────────────
@auth_router.post(
    "/logout",
    summary="Logout & revoke token"
)
async def logout(
    token_details: dict = Depends(AccessTokenBearer()),
):
    await add_jti_to_blocklist(token_details["jti"])
    return {"message": "Logout berhasil"}


# ── Forgot Password ────────────────────────────────────────────────
@auth_router.post(
    "/forgot-password",
    summary="Request link reset password"
)
async def forgot_password(
    data: EmailRequest,
    session: AsyncSession = Depends(get_session),
):
    email = data.email.lower().strip()
    user = await user_service.get_user_by_email(email, session)

    if user and user.is_verified and user.password:
        token = await user_service.generate_reset_token(email)
        if token:
            send_reset_password_email_task.delay(
                email, token, Config.FRONTEND_URL
            )

    return {
        "message": "Jika email terdaftar, link reset password telah dikirim."
    }


# ── Reset Password ─────────────────────────────────────────────────
@auth_router.post(
    "/reset-password",
    summary="Submit password baru"
)
async def reset_password(
    data: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.reset_password(data, session)



@user_router.post(
    "/me/change-password",
    summary="Ganti password (user yang sudah login)"
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from .utility import verify_hash, generate_password_hash
    from fastapi import HTTPException

    if not current_user.password:
        raise HTTPException(
            status_code=400,
            detail="Akun Google tidak memiliki password lokal. Gunakan Google untuk masuk."
        )

    if not verify_hash(data.old_password, current_user.password):
        raise HTTPException(
            status_code=400,
            detail="Password lama salah"
        )

    current_user.password = generate_password_hash(data.new_password)
    session.add(current_user)
    await session.commit()
    return {"message": "Password berhasil diubah"}


# ══════════════════════════════════════════════════════════════════
# USER ROUTES — TIDAK ADA PERUBAHAN
# ══════════════════════════════════════════════════════════════════

@user_router.get(
    "/me",
    response_model=UserRead,
    summary="Profil user yang sedang login"
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@user_router.patch(
    "/me",
    response_model=UserRead,
    summary="Update profil"
)
async def update_profile(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.update_user_profile(
        current_user, update_data, session
    )


@user_router.delete(
    "/me",
    summary="Hapus akun permanen"
)
async def delete_account(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer()),
):
    await add_jti_to_blocklist(token_details["jti"])
    return await user_service.delete_user(current_user, session)


@user_router.get(
    "/all",
    summary="[Admin] Daftar semua user"
)
async def get_all_users(
    _: User = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.get_all_user(session)


router_user = APIRouter()
router_user.include_router(auth_router)
router_user.include_router(user_router)