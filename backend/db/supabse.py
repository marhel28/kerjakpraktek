"""Supabase Admin API helper — dipakai HANYA oleh auth bridge.

Jalur notifikasi sudah berpindah ke backend/user/notifications/ dan
tidak lagi memakai modul ini.
"""

import httpx

from backend.config import Config


async def admin_create_supabase_user(email: str, password: str) -> dict:
    url = f"{Config.SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "apikey": Config.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
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
        "apikey": Config.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {Config.SUPABASE_SERVICE_ROLE_KEY}",
    }
    params = {"filter": f"email={email}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    data = response.json()
    users = data.get("users", [])
    for user in users:
        if user.get("email", "").lower() == email.lower():
            return user
    return None


async def admin_sign_in_with_password(email: str, password: str) -> dict:
    url = f"{Config.SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": Config.SUPABASE_ANON_KEY,
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
