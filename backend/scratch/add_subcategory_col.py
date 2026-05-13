import asyncio
from sqlalchemy import text
from backend.db.main import dB_engine

async def add_missing_column():
    print("🚀 Adding missing column subcategory_uuid to category_addon_mapping...")
    async with dB_engine.begin() as conn:
        try:
            # Check if column exists (PostgreSQL specific)
            res = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='category_addon_mapping' AND column_name='subcategory_uuid';
            """))
            exists = res.scalar()
            
            if not exists:
                await conn.execute(text("""
                    ALTER TABLE category_addon_mapping 
                    ADD COLUMN subcategory_uuid UUID REFERENCES subcategory(uuid) ON DELETE CASCADE;
                """))
                print("✅ Column subcategory_uuid added successfully.")
            else:
                print("ℹ️ Column subcategory_uuid already exists.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_missing_column())
