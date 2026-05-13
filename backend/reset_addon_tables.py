import asyncio
from sqlmodel import SQLModel, text
from backend.db.main import dB_engine
# Import models to ensure they are registered in metadata
from backend.data.public.addon.model import AddonGroup, AddonItem, CategoryAddonMapping, ProductAddonOverride

async def reset_addon_tables():
    print("🧹 Dropping and creating addon tables...")
    async with dB_engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS product_addon_override CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS category_addon_mapping CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS addon_items CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS addon_groups CASCADE"))
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✅ Done.")

if __name__ == "__main__":
    asyncio.run(reset_addon_tables())
