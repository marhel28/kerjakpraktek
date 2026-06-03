from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from backend.config import Config
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker

dB_engine = create_async_engine(
    Config.DATABASE_URL,
    echo=False,  
    pool_pre_ping=True,
    pool_size=30,          
    max_overflow=50,      
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
        from backend.data.chatbot.model import ChatbotKnowledge, ChatbotFeedback  # noqa
        await conn.run_sync(SQLModel.metadata.create_all)
        
        # Self-healing migration for chatbot_feedback column
        from sqlalchemy import text
        await conn.execute(text("ALTER TABLE chatbot_feedback ADD COLUMN IF NOT EXISTS bot_reply VARCHAR(4000);"))


async def init_knowledge_index():
    """Load TurboQuant knowledge base index ke memori setelah DB init dan seed default FAQ."""
    try:
        import json
        import os
        from sqlmodel import select
        from backend.data.chatbot.model import ChatbotKnowledge
        from backend.data.chatbot.knowledge_repository import ChatbotKnowledgeRepository, compute_bit_vector_hex

        # Path to faq.json
        faq_path = os.path.join(os.path.dirname(__file__), "..", "data", "chatbot", "faq.json")
        faq_items = []
        if os.path.exists(faq_path):
            with open(faq_path, "r", encoding="utf-8") as f:
                faq_items = json.load(f)

        async with db_session_maker() as session:
            # Seed FAQ if not exists
            for item in faq_items:
                stmt = select(ChatbotKnowledge).where(ChatbotKnowledge.question == item["question"])
                res = await session.execute(stmt)
                existing = res.scalar_one_or_none()
                if not existing:
                    bvec = compute_bit_vector_hex(item["question"])
                    # Use naive UTC datetimes to comply with PostgreSQL TIMESTAMP WITHOUT TIME ZONE
                    from datetime import datetime
                    naive_now = datetime.utcnow()
                    new_kb = ChatbotKnowledge(
                        question=item["question"],
                        answer=item["answer"],
                        category=item.get("category", "general"),
                        bit_vector=bvec,
                        is_active=True,
                        created_by="system",
                        created_at=naive_now,
                        updated_at=naive_now
                    )
                    session.add(new_kb)
            await session.commit()

            repo = ChatbotKnowledgeRepository()
            await repo.init_index(session)
        print("✅ TurboQuant KB index loaded successfully.")

        # Initialize Qdrant and Sync all products from DB to Qdrant
        try:
            from backend.data.chatbot.qdrant_service import QdrantService
            qdrant_service = QdrantService()
            if qdrant_service.init_collection():
                async with db_session_maker() as session:
                    await qdrant_service.sync_all_products(session)
                print("✅ Qdrant database sync complete.")
        except Exception as q_err:
            print(f"⚠️  Failed to sync products to Qdrant: {q_err}")
    except Exception as e:
        print(f"⚠️  Failed to load KB index: {e}")
    




celery_engine = create_async_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionCelery = sessionmaker(
    celery_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)