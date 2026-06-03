import asyncio
from sqlmodel import select
from sqlalchemy.orm import selectinload
from backend.db.main import db_session_maker
from backend.data.stock.model import Stock
from backend.db.es_client import es_client

async def sync_all_stocks_to_manticore():
    print("🔄 Starting sync of all stocks from Postgres to Manticore Search...")
    
    # 1. Ensure the Manticore table is initialized (re-created to apply new schema)
    await es_client.indices.delete(index="products")
    await es_client.indices.create(index="products")
    
    async with db_session_maker() as session:
        # Fetch all stocks with their assets
        stmt = select(Stock).options(selectinload(Stock.assets))
        res = await session.execute(stmt)
        stocks = res.scalars().all()
        
        print(f"📦 Found {len(stocks)} stocks in Postgres. Syncing...")
        
        count = 0
        for stock in stocks:
            first_image_url = stock.assets[0].url if stock.assets else None
            doc = {
                "uuid":                str(stock.uuid),
                "title":               stock.title,
                "slug":                stock.slug,
                "brand":               stock.brand or "",
                "brand_normalized":    stock.brand.lower().strip() if stock.brand else "",
                "category_slug":       stock.category_slug,
                "subcategory_slug":    stock.subcategory_slug or "",
                "type":                stock.type or "camera cctv",
                "specs":               stock.specs or {},
                "original_price":      stock.original_price or 0,
                "discount_percentage": stock.discount_percentage or 0,
                "online_price":        stock.online_price or 0,
                "stok":                stock.stok or 0,
                "terjual":             stock.terjual or 0,
                "sisa":                max((stock.stok or 0) - (stock.terjual or 0), 0),
                "is_active":           stock.is_active,
                "created_at":          stock.created_at.isoformat() if stock.created_at else None,
                "image_url":           first_image_url,
            }
            try:
                await es_client.index(index="products", id=str(stock.uuid), document=doc)
                count += 1
            except Exception as e:
                print(f"❌ Failed to index stock {stock.uuid}: {e}")
                
        print(f"✅ Indexed {count}/{len(stocks)} stocks into Manticore.")
    
    await es_client.close()

if __name__ == "__main__":
    asyncio.run(sync_all_stocks_to_manticore())
