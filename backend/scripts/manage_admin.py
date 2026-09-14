import os
import sys

# Ensure root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import asyncio
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.config import Config
from backend.auth.model import User, UserRole, UserType
from backend.auth.utility import generate_password_hash

# Handle host connection when running locally outside docker
db_url = Config.DATABASE_URL
if "@db:" in db_url:
    db_url = db_url.replace("@db:5432", "@localhost:5433").replace("@db:5433", "@localhost:5433")
elif "@db/" in db_url:
    db_url = db_url.replace("@db/", "@localhost:5433/")

engine = create_async_engine(db_url, echo=False)
session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def create_admin():
    try:
        async with session_maker() as session:
            accounts = [
                {"email": "admin@pasarcctv.com", "username": "admin"},
                {"email": "admin@admin.com", "username": "admin_master"},
            ]
            password = "@admin"
            hashed_pw = generate_password_hash(password)
            
            for acc in accounts:
                email = acc["email"]
                username = acc["username"]
                result = await session.exec(select(User).where((User.email == email) | (User.username == username)))
                existing = result.first()
                if existing:
                    existing.password = hashed_pw
                    existing.role = UserRole.ADMIN
                    existing.is_verified = True
                    session.add(existing)
                    await session.commit()
                    print(f"[OK] Updated account: {existing.email} (Username: {existing.username})")
                else:
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
                    print(f"[OK] Created account: {new_admin.email} (Username: {new_admin.username})")


            # Verify password check
            assert verify_hash(password, hashed_pw), "Hash verification failed!"
            print("[OK] Password hash verification successful!")
            
            # Print all users in DB
            result = await session.exec(select(User))
            users = result.all()
            print("--- Current Users in DB ---")
            for u in users:
                print(f"- Username: {u.username} | Email: {u.email} | Role: {u.role} | Verified: {u.is_verified}")

    finally:
        await engine.dispose()

if __name__ == "__main__":
    from backend.auth.utility import verify_hash
    asyncio.run(create_admin())



