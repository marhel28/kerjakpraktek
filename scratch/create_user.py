import asyncio
from sqlmodel import select, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.auth.model import User, UserRole, UserType
from backend.auth.utility import generate_password_hash

from backend.config import Config

DATABASE_URL = Config.DATABASE_URL  # ambil dari backend config/env, jangan hardcode

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_single_user():
    email = "user1@example.com"
    username = "user1"
    password = "password123"

    async with SessionLocal() as session:
        result = await session.exec(select(User).where(User.email == email))
        user = result.first()
        if user:
            user.password = generate_password_hash(password)
            user.is_verified = True
            user.role = UserRole.USER
            user.user_type = UserType.BIASA
            session.add(user)
            await session.commit()
            print(f"User updated: email={email}, username={username}, password={password}")
            return

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=UserRole.USER,
            user_type=UserType.BIASA,
            is_verified=True,
        )
        session.add(new_user)
        await session.commit()
        print(f"User created: email={email}, username={username}, password={password}")

if __name__ == "__main__":
    asyncio.run(create_single_user())
