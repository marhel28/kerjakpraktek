import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as AlchemySession
from sqlalchemy.orm import sessionmaker
from backend.data.jasa.model import ServicePackage, ServiceCategory
from sqlmodel import select

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user_admin:password_rahasia@localhost:5433/marketplace_db")
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AlchemySession, expire_on_commit=False)

async def seed_packages():
    async with async_session() as session:
        packages = [
            ServicePackage(
                name="Paket Hemat 2 Kamera Dahua",
                slug="paket-hemat-2-kamera-dahua",
                description="Paket 2 kamera untuk rumah kecil.",
                category=ServiceCategory.INSTALLATION,
                camera_count=2,
                default_brand="dahua",
                device_price=800000,
                estimated_service_price=300000,
                sort_order=10,
                thumbnail_url="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&q=80"
            ),
            ServicePackage(
                name="Paket Pintar 4 Kamera Hikvision",
                slug="paket-pintar-4-kamera-hikvision",
                description="Paket 4 kamera terlaris untuk rumah menengah.",
                category=ServiceCategory.INSTALLATION,
                camera_count=4,
                default_brand="hikvision",
                device_price=1500000,
                estimated_service_price=600000,
                sort_order=1,
                thumbnail_url="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&q=80"
            ),
            ServicePackage(
                name="Paket Bisnis 8 Kamera",
                slug="paket-bisnis-8-kamera",
                description="Paket 8 kamera untuk ruko atau kantor.",
                category=ServiceCategory.INSTALLATION,
                camera_count=8,
                default_brand="hikvision",
                device_price=3000000,
                estimated_service_price=1200000,
                sort_order=2,
                thumbnail_url="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&q=80"
            ),
            ServicePackage(
                name="Paket Enterprise 16 Kamera",
                slug="paket-enterprise-16-kamera",
                description="Solusi enterprise 16 kamera.",
                category=ServiceCategory.INSTALLATION,
                camera_count=16,
                default_brand="dahua",
                device_price=6000000,
                estimated_service_price=2400000,
                sort_order=20,
                thumbnail_url="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&q=80"
            )
        ]
        
        for p in packages:
            existing = await session.execute(select(ServicePackage).where(ServicePackage.slug == p.slug))
            if not existing.scalars().first():
                session.add(p)
                print(f"Added {p.name}")
        
        await session.commit()
        print("Done seeding packages.")

if __name__ == "__main__":
    asyncio.run(seed_packages())
