# db/supabase.py

import httpx
import logging
from typing import Optional
from supabase import create_client, Client
from backend.config import Config

logger = logging.getLogger(__name__)

supabase_public: Client = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_ANON_KEY,
)

# 🔐 SERVICE ROLE — BACKEND ONLY, NEVER expose to frontend
supabase_admin: Client = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_SERVICE_ROLE_KEY,
)


# =============================================================
# HELPER: USER CONTEXT CLIENT
# =============================================================
def get_supabase_user_client(jwt_token: str) -> Client:
    return create_client(
        Config.SUPABASE_URL,
        Config.SUPABASE_ANON_KEY,
        options={"headers": {"Authorization": f"Bearer {jwt_token}"}},
    )


# =============================================================
# ADMIN API HELPERS (via REST)
# =============================================================

async def admin_create_supabase_user(email: str, password: str) -> dict:
    url = f"{Config.SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "apikey":        Config.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {"email": email, "password": password, "email_confirm": True}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        raise Exception(
            f"Supabase admin create user failed: {response.status_code} {response.text}"
        )
    return response.json()


async def admin_get_supabase_user_by_email(email: str) -> dict | None:
    url = f"{Config.SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "apikey":        Config.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
    }
    params = {"filter": f"email={email}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    data  = response.json()
    users = data.get("users", [])
    for user in users:
        if user.get("email", "").lower() == email.lower():
            return user
    return None


async def admin_sign_in_with_password(email: str, password: str) -> dict:
    url = f"{Config.SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey":       Config.SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }
    payload = {"email": email, "password": password}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Supabase sign in failed: {response.status_code} {response.text}"
        )
    return response.json()


# =============================================================
# NOTIFICATION SERVICE
# =============================================================

class SupabaseNotificationService:

    @staticmethod
    async def send_notification(
        user_id: str,
        title: str,
        content: Optional[str] = None,
        action_url: Optional[str] = None,
        notif_type: str = "general",
        metadata: dict = {},
    ) -> dict:
        """
        Insert satu notifikasi ke tabel 'notifications' via Supabase REST API.
        action_url dimasukkan ke dalam metadata, BUKAN field terpisah.
        """
        url = f"{Config.SUPABASE_URL}/rest/v1/notifications"
        headers = {
            "apikey":        Config.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type":  "application/json",
            "Prefer":        "return=representation",
        }
        
        # Gabungkan action_url ke metadata
        final_metadata = {**metadata}
        if action_url:
            final_metadata["action_url"] = action_url
        
        payload = {
            "user_id":    user_id,
            "title":      title,
            "content":    content or "",
            "type":       notif_type,
            "metadata":   final_metadata,
        }

        logger.info(f"[Notif] Sending → user_id={user_id} title='{title}'")

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)

        if resp.status_code not in (200, 201):
            logger.error(
                f"[Notif] Insert GAGAL: {resp.status_code} — {resp.text}"
            )
            raise Exception(
                f"Supabase notification insert failed: {resp.status_code} {resp.text}"
            )

        data = resp.json()
        logger.info(f"[Notif] Terkirim ✓ → {data}")
        return data[0] if isinstance(data, list) and data else {}

    @staticmethod
    async def bulk_notification(
        user_ids: list[str],
        title: str,
        content: Optional[str] = None,
        action_url: Optional[str] = None,
        notif_type: str = "general",
    ) -> list:
        if not user_ids:
            return []

        url = f"{Config.SUPABASE_URL}/rest/v1/notifications"
        headers = {
            "apikey":        Config.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type":  "application/json",
            "Prefer":        "return=representation",
        }
        
        final_metadata = {}
        if action_url:
            final_metadata["action_url"] = action_url
        
        payload = [
            {
                "user_id":    uid,
                "title":      title,
                "content":    content or "",
                "type":       notif_type,
                "metadata":   final_metadata,
            }
            for uid in user_ids
        ]

        logger.info(f"[Notif] Bulk send → {len(user_ids)} users, title='{title}'")

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)

        if resp.status_code not in (200, 201):
            logger.error(f"[Notif] Bulk insert GAGAL: {resp.status_code} — {resp.text}")
            raise Exception(
                f"Supabase bulk notification failed: {resp.status_code} {resp.text}"
            )

        data = resp.json()
        logger.info(f"[Notif] Bulk terkirim ✓ → {len(data)} rows")
        return data

    @staticmethod
    async def get_notifications(user_id: str, limit: int = 50) -> list:
        url = f"{Config.SUPABASE_URL}/rest/v1/notifications"
        headers = {
            "apikey":        Config.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
        }
        params = {
            "user_id": f"eq.{user_id}",
            "order": "created_at.desc",
            "limit": str(limit),
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers, params=params)
            if resp.status_code != 200:
                logger.error(f"[Notif] Fetch GAGAL: {resp.status_code} — {resp.text}")
                return []
            return resp.json()
        except Exception as e:
            logger.error(f"[Notif] Fetch error: {e}")
            return []

    @staticmethod
    async def mark_as_read(user_id: str, notification_id: int) -> bool:
        url = f"{Config.SUPABASE_URL}/rest/v1/notifications"
        headers = {
            "apikey":        Config.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type":  "application/json",
        }
        params = {
            "user_id": f"eq.{user_id}",
            "id": f"eq.{notification_id}",
        }
        from datetime import datetime
        payload = {
            "read_at": datetime.utcnow().isoformat() + "Z"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.patch(url, json=payload, headers=headers, params=params)
            if resp.status_code not in (200, 204):
                logger.error(f"[Notif] Mark read GAGAL: {resp.status_code} — {resp.text}")
                return False
            return True
        except Exception as e:
            logger.error(f"[Notif] Mark read error: {e}")
            return False

    @staticmethod
    async def mark_all_as_read(user_id: str) -> bool:
        url = f"{Config.SUPABASE_URL}/rest/v1/notifications"
        headers = {
            "apikey":        Config.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type":  "application/json",
        }
        params = {
            "user_id": f"eq.{user_id}",
            "read_at": "is.null",
        }
        from datetime import datetime
        payload = {
            "read_at": datetime.utcnow().isoformat() + "Z"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.patch(url, json=payload, headers=headers, params=params)
            if resp.status_code not in (200, 204):
                logger.error(f"[Notif] Mark all read GAGAL: {resp.status_code} — {resp.text}")
                return False
            return True
        except Exception as e:
            logger.error(f"[Notif] Mark all read error: {e}")
            return False



# =============================================================
# AUTH HELPER
# =============================================================
class SupabaseAuthService:

    @staticmethod
    def verify_user(jwt_token: str):
        client = get_supabase_user_client(jwt_token)
        user   = client.auth.get_user()
        if not user:
            raise Exception("Invalid token")
        return user