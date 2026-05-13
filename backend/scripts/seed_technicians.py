import asyncio
import os
import random
import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.db.main import db_session_maker
from backend.data.jasa.model import Technician
from backend.db.cdn import upload_file

# List of technician names
TECH_NAMES = [
    "Budi Santoso", "Andi Wijaya", "Siti Aminah", "Rahmat Hidayat",
    "Eko Prasetyo", "Dewi Lestari", "Agus Setiawan", "Linda Permata"
]

# Path to brand images
BRAND_DIR = "c:/Users/Administrator/Desktop/kp/kerjapraktek/test/brand"

async def seed_technicians():
    async with db_session_maker() as session:
        # Check if already seeded
        res = await session.exec(select(Technician))
        if res.first():
            print("Technicians already seeded. Skipping...")
            return

        print("Seeding technicians...")
        
        # Get list of images
        images = [f for f in os.listdir(BRAND_DIR) if f.endswith(('.webp', '.png', '.jpg'))]
        
        for i, name in enumerate(TECH_NAMES):
            # Pick a random image
            img_name = random.choice(images)
            img_path = os.path.join(BRAND_DIR, img_name)
            
            with open(img_path, "rb") as f:
                content = f.read()
            
            # Upload to CDN (local mock or actual)
            # Using the same logic as route.py
            filename = f"{uuid.uuid4()}.webp"
            try:
                picture_url = await upload_file(content, folder="technicians", filename=filename)
            except Exception as e:
                print(f"Failed to upload picture for {name}: {e}")
                picture_url = None

            tech = Technician(
                name=name,
                id_employee=f"PJC-{str(101 + i)}",
                phone=f"0812345678{i}",
                picture_url=picture_url,
                is_active=True
            )
            session.add(tech)
            print(f"Added technician: {name} ({tech.id_employee})")

        await session.commit()
        print("Seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_technicians())
