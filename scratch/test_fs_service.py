import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.config import Config

DATABASE_URL = Config.DATABASE_URL  # ambil dari backend config/env, jangan hardcode
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
db_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
from backend.data.public.promobanner.flashsale_service import FlashSaleService

async def main():
    async with db_session_maker() as session:
        print("Invalidating cache...")
        await FlashSaleService.invalidate_cache()
        print("Querying flash sale...")
        try:
            res = await FlashSaleService.get_active_flashsale(session)
            print("Response:", res)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())