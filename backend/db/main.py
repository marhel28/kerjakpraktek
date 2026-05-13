from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from backend.config import Config
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker

dB_engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,  
    pool_pre_ping=True,
    pool_size=10,          
    max_overflow=20,      
    pool_recycle=1800,
    pool_timeout=30,            
    connect_args={
        "statement_cache_size": 1000,
    },
)
 
db_session_maker = async_sessionmaker(
    dB_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,   
)
 

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_session_maker() as session:
        yield session


async def init_db():
    async with dB_engine.begin() as conn:  
        from backend.data.stock.model import Stock
        from backend.auth.model import User
        from backend.data.transaksi.model import Transaction
        from backend.data.activity.model import ActivityLog
        await conn.run_sync(SQLModel.metadata.create_all)
    




celery_engine = create_async_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionCelery = sessionmaker(
    celery_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)