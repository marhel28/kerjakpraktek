import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.config import Config

DATABASE_URL = Config.DATABASE_URL  # ambil dari backend config/env, jangan hardcode
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
db_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def migrate():
    async with db_session_maker() as s:
        await s.execute(text("ALTER TABLE promo ADD COLUMN IF NOT EXISTS flash_sale_mode VARCHAR DEFAULT 'auto';"))
        await s.execute(text("ALTER TABLE promo ADD COLUMN IF NOT EXISTS auto_strategy VARCHAR DEFAULT 'discount';"))
        await s.commit()
        print("Migration done successfully")

if __name__ == "__main__":
    asyncio.run(migrate())