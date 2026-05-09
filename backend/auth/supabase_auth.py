# service/supabase_auth.py

import logging
import secrets
import string
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from backend.db.supabse import (
    admin_create_supabase_user,
    admin_get_supabase_user_by_email,
    admin_sign_in_with_password,
)
from backend.auth.model import UserMap  # model baru, lihat di bawah

logger = logging.getLogger(__name__)


def _generate_secure_password(length: int = 32) -> str:
    """
    Generate random password untuk Supabase user.
    User tidak pernah tahu password ini — login lewat bridge saja.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


class SupabaseAuthBridge:

    # ── Mapping Helpers ────────────────────────────────────────────

    async def get_mapping_by_local_id(
        self, local_user_id: str, session: AsyncSession  # ← str/UUID bukan int
    ) -> UserMap | None:
        result = await session.exec(
            select(UserMap).where(UserMap.local_user_id == str(local_user_id))
        )
        return result.first()

    async def get_mapping_by_supabase_id(
        self, supabase_user_id: str, session: AsyncSession
    ) -> UserMap | None:
        result = await session.exec(
            select(UserMap).where(UserMap.supabase_user_id == supabase_user_id)
        )
        return result.first()

    async def create_mapping(
    self,
    local_user_id: str,        # ← str/UUID bukan int
    supabase_user_id: str,
    supabase_password: str,
    session: AsyncSession,
) -> UserMap:
        mapping = UserMap(
            local_user_id=str(local_user_id),
            supabase_user_id=supabase_user_id,
            supabase_password=supabase_password,
        )
        session.add(mapping)
        await session.commit()
        await session.refresh(mapping)
        return mapping

    # ── Core Bridge Logic ──────────────────────────────────────────

    async def get_or_create_supabase_session(
        self,
        local_user_id: int,
        email: str,
        session: AsyncSession,
    ) -> dict | None:
        """
        Entrypoint utama:
        1. Cek mapping di user_maps
        2. Jika belum ada → cek apakah email sudah ada di Supabase
        3. Jika belum → buat user baru di Supabase
        4. Simpan mapping
        5. Sign in ke Supabase → return session

        Return None jika ada error non-fatal (Supabase down, dll).
        Auth utama sistem kita tetap jalan.
        """
        email = email.lower().strip()

        try:
            # STEP 1: Cek mapping
            mapping = await self.get_mapping_by_local_id(local_user_id, session)

            if mapping:
                # Sudah mapped — langsung sign in
                supabase_session = await admin_sign_in_with_password(
                    email, mapping.supabase_password
                )
                return supabase_session

            # STEP 2: Belum mapped — cek apakah email sudah ada di Supabase
            existing_sb_user = await admin_get_supabase_user_by_email(email)

            password = _generate_secure_password()

            if existing_sb_user:
                # User ada di Supabase tapi belum di-map
                supabase_user_id = existing_sb_user["id"]
                logger.warning(
                    f"Supabase user exists but not mapped: email={email}, "
                    f"supabase_id={supabase_user_id}"
                )
                # Update password supbase agar bisa kita kontrol
                await _admin_update_supabase_password(supabase_user_id, password)
            else:
                # STEP 3: Buat user baru di Supabase
                created = await admin_create_supabase_user(email, password)
                supabase_user_id = created["id"]
                logger.info(f"Created Supabase user: {supabase_user_id} for email={email}")

            # STEP 4: Simpan mapping
            await self.create_mapping(
                local_user_id=local_user_id,
                supabase_user_id=supabase_user_id,
                supabase_password=password,
                session=session,
            )

            # STEP 5: Sign in ke Supabase
            supabase_session = await admin_sign_in_with_password(email, password)
            return supabase_session

        except Exception as e:
            # Supabase failure TIDAK boleh break auth utama
            logger.error(f"Supabase bridge error for user {local_user_id}: {e}")
            return None


async def _admin_update_supabase_password(supabase_user_id: str, new_password: str):
    """Update password Supabase user via Admin REST API."""
    import httpx
    from backend.config import Config

    url = f"{Config.SUPABASE_URL}/auth/v1/admin/users/{supabase_user_id}"
    headers = {
        "apikey": Config.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, json={"password": new_password}, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to update Supabase password: {response.text}")


# Singleton
supabase_auth_bridge = SupabaseAuthBridge()