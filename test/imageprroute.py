import os
import httpx
import asyncio
import random
from uuid import uuid4

BASE_URL = "http://localhost:8000"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "Imagesection")

IDENTIFIERS = [
    "home:hero-carousel",
    "category:kamera-cctv",
    "category:ip-camera",
    "promo:ramadan-sale"
]

async def seed_image_sections():
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("🚀 Starting Seeder: Image Sections & Banners")

        if not os.path.exists(IMAGE_FOLDER):
            print(f"❌ Folder {IMAGE_FOLDER} tidak ditemukan!")
            return

        all_images = [
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        ]

        if not all_images:
            print("❌ Tidak ada gambar di folder tersebut.")
            return

        for ident in IDENTIFIERS:
            section_data = {
                "identifier": ident,
                "title": f"Banner untuk {ident.replace(':', ' ').title()}",
                "is_active": True
            }

            print(f"\n📂 Creating Section: [{ident}]")
            res_section = await client.post(f"{BASE_URL}/image-sections", json=section_data)

            if res_section.status_code != 200:
                print(f"⚠️ Skip {ident}: {res_section.text}")

            num_images = random.randint(1, 3)
            selected_images = random.sample(all_images, min(num_images, len(all_images)))

            for i, img_name in enumerate(selected_images):
                img_path = os.path.join(IMAGE_FOLDER, img_name)

                with open(img_path, "rb") as f:
                    files = {"file": (img_name, f, "image/jpeg")}
                    data = {
                        "target_url": f"https://pasarcctv.com/promo/{uuid4().hex[:8]}",
                        "alt_text": f"Alt text for {img_name}",
                        "order": i + 1
                    }

                    print(f"  📤 Uploading {img_name}")
                    res_upload = await client.post(
                        f"{BASE_URL}/image-sections/{ident}/upload-banner",
                        data=data,
                        files=files
                    )

                    if res_upload.status_code == 200:
                        print(f"  ✅ Success")
                    else:
                        print(f"  ❌ Failed: {res_upload.text}")

        print("\n✨ Seeding Completed!")

if __name__ == "__main__":
    asyncio.run(seed_image_sections())