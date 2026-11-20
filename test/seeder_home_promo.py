import os
import httpx
import asyncio

BASE_URL = "http://localhost:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEN_DIR = os.path.join(BASE_DIR, "generated")

SECTION_ID = "home:promo-strip"

IMAGES = [
    {
        "filename": "promo_cctv_exclusive.jpg",
        "target_url": "/promos",
        "alt_text": "Penawaran Eksklusif CCTV",
        "order": 1
    },
    {
        "filename": "promo_flashsale_cctv.jpg",
        "target_url": "/category/paket-cctv",
        "alt_text": "Flash Sale Paket CCTV",
        "order": 2
    },
    {
        "filename": "promo_access_control.jpg",
        "target_url": "/category/access-control",
        "alt_text": "Access Control Security",
        "order": 3
    }
]

async def seed_home_promo():
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"🚀 Seeding Section: {SECTION_ID}")
        
        # 1. Pastikan section terdaftar
        sec_payload = {
            "identifier": SECTION_ID,
            "title": "Promo Eksklusif Beranda",
            "mode": "heroStrip",
            "is_active": True
        }
        res = await client.post(f"{BASE_URL}/image-sections", json=sec_payload)
        print(f"Section status: {res.status_code}")

        # 2. Upload setiap banner gambar yang di-generate
        for img_info in IMAGES:
            file_path = os.path.join(GEN_DIR, img_info["filename"])
            if not os.path.exists(file_path):
                print(f"File {file_path} tidak ada, skip.")
                continue

            with open(file_path, "rb") as f:
                files = {"file": (img_info["filename"], f, "image/jpeg")}
                data = {
                    "target_url": img_info["target_url"],
                    "alt_text": img_info["alt_text"],
                    "order": img_info["order"]
                }
                up_res = await client.post(
                    f"{BASE_URL}/image-sections/{SECTION_ID}/upload-banner",
                    data=data,
                    files=files
                )
                print(f"Uploaded {img_info['filename']}: {up_res.status_code}")

if __name__ == "__main__":
    asyncio.run(seed_home_promo())