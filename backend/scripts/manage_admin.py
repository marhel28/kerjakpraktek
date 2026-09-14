import os
import sys

# Ensure root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import asyncio
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.config import Config
from backend.auth.model import User, UserMap, UserRole, UserType
from backend.auth.utility import generate_password_hash, verify_hash

# Handle host connection when running locally outside docker vs inside docker container
is_in_docker = os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')
db_url = Config.DATABASE_URL

if not is_in_docker:
    if "@db:" in db_url:
        db_url = db_url.replace("@db:5432", "@localhost:5433").replace("@db:5433", "@localhost:5433")
    elif "@db/" in db_url:
        db_url = db_url.replace("@db/", "@localhost:5433/")

engine = create_async_engine(db_url, echo=False)
session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def recreate_admins(target_accounts=None):
    try:
        async with session_maker() as session:
            if not target_accounts:
                target_accounts = [
                    {"email": "admin@pasarcctv.com", "username": "admin", "password": "@admin"},
                    {"email": "admin@admin.com", "username": "admin_master", "password": "@admin"},
                ]

            for acc in target_accounts:
                email = acc["email"]
                username = acc["username"]
                raw_pw = acc["password"]
                hashed_pw = generate_password_hash(raw_pw)

                # 1. Cari dan HAPUS akun lama jika sudah ada
                result = await session.exec(select(User).where((User.email == email) | (User.username == username)))
                existing_users = result.all()
                for existing in existing_users:
                    # Hapus pemetaan usermap jika ada
                    await session.exec(delete(UserMap).where(UserMap.local_user_id == str(existing.uuid)))
                    # Hapus user (tabel relasi lain seperti cart/whitlish otomatis CASCADE)
                    await session.delete(existing)
                    await session.commit()
                    print(f"[DELETED] Deleted existing admin: {existing.email} (UUID: {existing.uuid})")

                # 2. Buat akun admin BARU dari awal
                new_admin = User(
                    username=username,
                    email=email,
                    password=hashed_pw,
                    role=UserRole.ADMIN,
                    user_type=UserType.BIASA,
                    is_verified=True,
                )
                session.add(new_admin)
                await session.commit()
                await session.refresh(new_admin)
                print(f"[CREATED] Brand new admin: {new_admin.email} (Username: {new_admin.username}, UUID: {new_admin.uuid})")

                # Verify password check
                assert verify_hash(raw_pw, hashed_pw), "Hash verification failed!"
                print(f"[OK] Password hash verified for {email}")

            # Print all admin users in DB
            result = await session.exec(select(User).where(User.role == UserRole.ADMIN))
            admins = result.all()
            print("\n--- Current Admin Users in DB ---")
            for u in admins:
                print(f"- Username: {u.username} | Email: {u.email} | Role: {u.role} | Verified: {u.is_verified} | UUID: {u.uuid}")

    finally:
        await engine.dispose()

if __name__ == "__main__":
    accounts = None
    if len(sys.argv) >= 4:
        accounts = [{
            "email": sys.argv[1],
            "username": sys.argv[2],
            "password": sys.argv[3]
        }]
    asyncio.run(recreate_admins(accounts))
