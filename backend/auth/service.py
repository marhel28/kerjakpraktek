import logging
from uuid import uuid4
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from .model import User
from .schema import UserCreate, UserProfileUpdate, ResetPasswordRequest
from .utility import (
    generate_password_hash,
    verify_hash,
    verify_google_id_token,
)
from backend.db.redis import (
    save_email_verification_token,
    get_email_from_verification_token,
    save_password_reset_token,
    get_email_from_reset_token,
)
from backend.config import Config

logger = logging.getLogger(__name__)


class UserService:

    # ── Helpers ────────────────────────────────────────────────────
    async def get_user_by_email(
        self, email: str, session: AsyncSession
    ) -> User | None:
        result = await session.exec(
            select(User).where(User.email == email)
        )
        return result.first()

    async def get_user_by_uuid(
        self, uuid: str, session: AsyncSession
    ) -> User | None:
        result = await session.exec(
            select(User).where(User.uuid == uuid)
        )
        return result.first()

    async def get_user_by_google_id(
        self, google_id: str, session: AsyncSession
    ) -> User | None:
        result = await session.exec(
            select(User).where(User.google_id == google_id)
        )
        return result.first()

    async def user_exist(self, email: str, session: AsyncSession) -> bool:
        return await self.get_user_by_email(email, session) is not None

    async def _get_unique_username(
        self, base: str, session: AsyncSession
    ) -> str:
        """Pastikan username unik — tambah suffix angka jika collision."""
        username = base[:30]
        attempt = 0
        while True:
            result = await session.exec(
                select(User).where(User.username == username)
            )
            if not result.first():
                return username
            attempt += 1
            username = f"{base[:28]}_{attempt}"

    # ── Register ───────────────────────────────────────────────────
    async def create_user(
        self, user_data: UserCreate, session: AsyncSession
    ) -> User:
        new_user = User(
            username=user_data.username,
            email=user_data.email.lower().strip(),
            password=generate_password_hash(user_data.password),
            is_verified=False,
        )
        try:
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Username atau email sudah terdaftar"
            )
        return new_user

    # ── Email Verification ─────────────────────────────────────────
    async def generate_verification_token(self, email: str) -> str | None:
        """
        Buat token verifikasi dan simpan di Redis.
        Return token jika berhasil, None jika token aktif sudah ada.
        """
        token = str(uuid4())
        saved = await save_email_verification_token(token, email)
        return token if saved else None

    async def verify_email(
        self, token: str, session: AsyncSession
    ) -> dict:
        email = await get_email_from_verification_token(token)
        if not email:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Link verifikasi tidak valid atau sudah kadaluarsa. Silakan daftar ulang."
            )

        user = await self.get_user_by_email(email, session)
        if not user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Akun tidak ditemukan"
            )
        if user.is_verified:
            return {"message": "Email sudah terverifikasi sebelumnya"}

        user.is_verified = True
        session.add(user)
        await session.commit()
        return {"message": "Email berhasil diverifikasi. Akun kamu sudah aktif!"}

    async def cleanup_unverified_user(
        self, email: str, session: AsyncSession
    ) -> None:
        """Hapus akun yang belum verified — dipanggil oleh Celery task."""
        user = await self.get_user_by_email(email, session)
        if user and not user.is_verified:
            await session.delete(user)
            await session.commit()
            logger.info(f"🗑️  Unverified account deleted: {email}")

    # ── Login ──────────────────────────────────────────────────────
    async def authenticate_user(
        self, email: str, password: str, session: AsyncSession
    ) -> User:
        user = await self.get_user_by_email(email.lower().strip(), session)

        # Pesan error sama untuk email/password salah (anti-enumeration)
        if not user or not user.password:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        if not verify_hash(password, user.password):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        if not user.is_verified:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Akun belum diverifikasi. Cek email kamu."
            )
        return user

    # ── Google OAuth ───────────────────────────────────────────────
    async def login_or_register_google(
        self, id_token: str, session: AsyncSession
    ) -> User:
        google_data = await verify_google_id_token(id_token)

        google_id: str = google_data["sub"]
        email: str = google_data["email"].lower().strip()
        name: str = google_data.get("name", email.split("@")[0])

        # 1. Cek by google_id (paling akurat)
        user = await self.get_user_by_google_id(google_id, session)
        if user:
            return user

        # 2. Cek by email — link jika sudah register manual
        user = await self.get_user_by_email(email, session)
        if user:
            if not user.google_id:
                user.google_id = google_id
                user.is_verified = True
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user

        # 3. Buat akun baru via Google
        base_username = name.lower().replace(" ", "_")
        username = await self._get_unique_username(base_username, session)

        new_user = User(
            username=username,
            email=email,
            password=None,       # Google user tidak punya password lokal
            google_id=google_id,
            is_verified=True,    # Google sudah verifikasi email
        )
        try:
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Akun dengan email ini sudah ada"
            )
        return new_user

    # ── Password Reset ─────────────────────────────────────────────
    async def generate_reset_token(self, email: str) -> str | None:
        """
        Buat token reset password dan simpan di Redis.
        Return token jika berhasil, None jika token aktif sudah ada
        atau user tidak eligible.
        """
        token = str(uuid4())
        saved = await save_password_reset_token(token, email)
        return token if saved else None

    async def reset_password(
        self, data: ResetPasswordRequest, session: AsyncSession
    ) -> dict:
        email = await get_email_from_reset_token(data.token)
        if not email:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Link reset password tidak valid atau sudah kadaluarsa"
            )

        user = await self.get_user_by_email(email, session)
        if not user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Akun tidak ditemukan"
            )

        user.password = generate_password_hash(data.new_password)
        session.add(user)
        await session.commit()
        return {"message": "Password berhasil diubah. Silakan login."}

    # ── Profile ────────────────────────────────────────────────────
    async def get_all_user(self, session: AsyncSession) -> dict:
        result = await session.exec(select(User))
        return {"users": result.all()}

    async def update_user_profile(
        self,
        user: User,
        update_data: UserProfileUpdate,
        session: AsyncSession
    ) -> User:
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict.pop("email", None)  # Email tidak bisa diubah di sini

        for key, value in update_dict.items():
            setattr(user, key, value)

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete_user(
        self, user: User, session: AsyncSession
    ) -> dict:
        try:
            await session.delete(user)
            await session.commit()
            return {"message": "Akun berhasil dihapus"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal menghapus akun: {str(e)}"
            )