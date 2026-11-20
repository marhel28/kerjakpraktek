import os
import sys
import asyncio
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.config import Config

DATABASE_URL = Config.DATABASE_URL  # ambil dari backend config/env, jangan hardcode
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
db_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
from backend.data.public.promobanner.model import Promo, PromoItem, PromoStatus, PromoType
from backend.data.stock.model import Stock
from backend.data.public.promobanner.flashsale_service import FlashSaleService

async def seed_flashsale():
    async with db_session_maker() as session:
        print("⚡ Seeding Active Flash Sale...")
        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(hours=8)

        # 1. Nonaktifkan flashsale lama
        old_promos = (await session.execute(
            select(Promo).where(Promo.promo_type == PromoType.FLASH_SALE)
        )).scalars().all()
        for p in old_promos:
            p.status = PromoStatus.EXPIRED
            session.add(p)
        await session.commit()

        # 2. Buat Flash Sale Baru
        flash_promo = Promo(
            name="Flash Sale Diskon Kilat Spesial CCTV Bandung",
            slug=f"flash-sale-{int(now.timestamp())}",
            description="Potongan harga langsung 25% - 35% untuk aneka kamera outdoor & paket komplit. Waktu dan kuota terbatas.",
            promo_type=PromoType.FLASH_SALE,
            target="stock",
            discount_value=30,
            quota=50,
            flash_sale_quota=50,
            is_flash_sale=True,
            flash_sale_mode="auto",
            auto_strategy="discount",
            status=PromoStatus.ACTIVE,
            priority=100,
            valid_from=now - timedelta(minutes=5),
            valid_until=valid_until
        )
        session.add(flash_promo)
        await session.commit()
        await session.refresh(flash_promo)

        # 3. Bind beberapa produk stok
        stocks = (await session.execute(select(Stock).where(Stock.stok > 0).limit(8))).scalars().all()
        for s in stocks:
            pi = PromoItem(
                promo_uuid=flash_promo.uuid,
                stock_uuid=s.uuid,
                override_discount_value=35 if s.stok < 10 else 25
            )
            session.add(pi)
        await session.commit()

        # 4. Invalidate Redis Cache
        await FlashSaleService.invalidate_cache()
        print(f"✅ Flash sale live seeded successfully! UUID: {flash_promo.uuid}")

if __name__ == "__main__":
    asyncio.run(seed_flashsale())