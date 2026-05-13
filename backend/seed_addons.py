import asyncio
from sqlmodel import select, delete
from backend.db.main import db_session_maker
from backend.data.public.addon.model import AddonGroup, AddonItem, CategoryAddonMapping, ProductAddonOverride
from backend.data.public.category.model import Category
from datetime import datetime, timezone

async def seed_addons():
    async with db_session_maker() as session:
        print("🧹 Cleaning up old addon data...")
        await session.execute(delete(CategoryAddonMapping))
        await session.execute(delete(ProductAddonOverride))
        await session.execute(delete(AddonItem))
        await session.execute(delete(AddonGroup))
        await session.commit()

        # 1. Pastikan kategori 'networking' ada
        result = await session.execute(select(Category).where(Category.slug == "networking"))
        category = result.scalar_one_or_none()
        
        if not category:
            print("❌ Kategori 'networking' tidak ditemukan. Membuat kategori baru...")
            category = Category(
                name="Networking",
                slug="networking",
                is_active=True
            )
            session.add(category)
            await session.commit()
            await session.refresh(category)
        
        print(f"✅ Menggunakan Kategori: {category.name} ({category.uuid})")

        # 2. Buat Addon Group
        now = datetime.now(timezone.utc)
        group = AddonGroup(
            name="Kebutuhan Tambahan Networking",
            selection_type="multi",
            is_required=False,
            is_active=True,
            sort_order=1,
            created_at=now
        )
        session.add(group)
        await session.commit()
        await session.refresh(group)
        print(f"✅ Addon Group Dibuat: {group.name}")

        # 3. Buat Addon Items dengan BERAT (Weight)
        items = [
            AddonItem(
                group_uuid=group.uuid,
                name="Kabel LAN Cat6 Outdoor 100 Meter",
                description="Kabel outdoor kualitas industri dengan pelindung ganda",
                price=1500000,
                weight=1800, # 1.8kg
                stock=100,
                is_active=True,
                allow_quantity=True,
                max_quantity=5,
                created_at=now
            ),
            AddonItem(
                group_uuid=group.uuid,
                name="Kabel LAN Cat6 Indoor 100 Meter",
                description="Kabel indoor standard perkantoran",
                price=1000000,
                weight=1200, # 1.2kg
                stock=100,
                is_active=True,
                allow_quantity=True,
                max_quantity=10,
                created_at=now
            ),
            AddonItem(
                group_uuid=group.uuid,
                name="Hardisk 4TB Surveillance WD Purple",
                description="Penyimpanan khusus CCTV 24/7",
                price=3200000,
                weight=800, # 800g
                stock=30,
                is_active=True,
                allow_quantity=True,
                max_quantity=2,
                created_at=now
            ),
            AddonItem(
                group_uuid=group.uuid,
                name="Hardisk 2TB Surveillance WD Purple",
                description="Penyimpanan khusus CCTV standard",
                price=2000000,
                weight=600, # 600g
                stock=50,
                is_active=True,
                allow_quantity=True,
                max_quantity=4,
                created_at=now
            ),
            AddonItem(
                group_uuid=group.uuid,
                name="Switch Hub 8 Port PoE Gigabyte",
                description="Switch hub dengan power over ethernet untuk IP Camera",
                price=1250000,
                weight=1100, # 1.1kg
                stock=20,
                is_active=True,
                allow_quantity=True,
                max_quantity=3,
                created_at=now
            ),
            AddonItem(
                group_uuid=group.uuid,
                name="Router Mikrotik RB750Gr3 hEX",
                description="Router board untuk management bandwidth networking",
                price=1100000,
                weight=400, # 400g
                stock=15,
                is_active=True,
                allow_quantity=True,
                max_quantity=2,
                created_at=now
            ),
            AddonItem(
                group_uuid=group.uuid,
                name="Jasa Setting Mikrotik & Load Balancing",
                description="Konfigurasi professional network oleh teknisi ahli",
                price=750000,
                weight=0,
                stock=999,
                is_active=True,
                allow_quantity=False,
                created_at=now
            )
        ]
        
        for item in items:
            session.add(item)
        
        await session.commit()
        print(f"✅ {len(items)} Addon Items berhasil ditambahkan.")

        # 4. Mapping Group ke Kategori
        mapping = CategoryAddonMapping(
            category_uuid=category.uuid,
            addon_group_uuid=group.uuid,
            is_active=True,
            sort_order=1
        )
        session.add(mapping)
        await session.commit()
        print(f"✅ Addon Group berhasil di-mapping ke kategori 'networking'.")
        
        print("\n🚀 SEEDING ADDON SELESAI DENGAN DATA BERAT TERBARU!")

if __name__ == "__main__":
    asyncio.run(seed_addons())
