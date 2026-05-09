# seeder_home.py
"""
Jalankan: python seeder_home.py
Pastikan backend berjalan di http://localhost:8000
"""
import os
import asyncio
import httpx
from pathlib import Path

BASE_URL = "http://localhost:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(BASE_DIR, "brand")
IMAGE_PATH = os.path.join(BASE_DIR, "cctv.jpg")

# Data banner (4 banner untuk homepage)
BANNERS = [
    {
        "title": "Ambil Promonya Sekarang!",
        "route_link": "/promo",
        "sort_order": 1,
    },
    {
        "title": "Trusted Company | Teknisi Berpengalaman",
        "route_link": "/about",
        "sort_order": 2,
    },
    {
        "title": "Lebih dari 1.200 Kamera Terpasang!",
        "route_link": "/portofolio",
        "sort_order": 3,
    },
    {
        "title": "KAMERA CCTV • NVR & DVR • PAKET PROMO • AKSESORIS",
        "route_link": "/category/cctv",
        "sort_order": 4,
    },
]


async def upload_banner(client, title, route_link, sort_order, image_path):
    """Upload satu banner ke endpoint admin."""
    with open(image_path, "rb") as f:
        # Gunakan nama file asli untuk header
        filename = os.path.basename(image_path)
        files = {"file": (filename, f, "image/jpeg")}
        data = {
            "title": title,
            "route_link": route_link,
            "is_active": "true",
            "sort_order": str(sort_order),
        }
        response = await client.post(
            f"{BASE_URL}/main-bottom/admin", data=data, files=files
        )
        return response


async def main():
    # Cari file gambar dari folder brand, atau pakai cctv.jpg
    image_files = (
        list(Path(BRAND_DIR).glob("*.jpg"))
        + list(Path(BRAND_DIR).glob("*.jpeg"))
        + list(Path(BRAND_DIR).glob("*.png"))
        + list(Path(BRAND_DIR).glob("*.webp"))
    )

    # Jika folder brand ada isinya, gunakan; jika tidak, pakai IMAGE_PATH
    if not image_files and os.path.exists(IMAGE_PATH):
        image_files = [Path(IMAGE_PATH)]

    if not image_files:
        print(
            "❌ Tidak ada gambar ditemukan. Letakkan gambar di folder 'brand' "
            "atau pastikan 'cctv.jpg' ada di direktori yang sama."
        )
        return

    print(f"📸 {len(image_files)} gambar ditemukan. Mengunggah {len(BANNERS)} banner...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, banner in enumerate(BANNERS):
            # Rotasi gambar jika jumlahnya terbatas
            image_path = image_files[i % len(image_files)]
            print(f"  [{i+1}] {banner['title']} (gambar: {image_path.name})")
            resp = await upload_banner(
                client,
                banner["title"],
                banner["route_link"],
                banner["sort_order"],
                str(image_path),
            )
            if resp.status_code == 200:
                print(f"      ✅ Berhasil: {resp.json()}")
            else:
                print(f"      ❌ Gagal ({resp.status_code}): {resp.text}")

    print("🎉 Selesai mengisi banner homepage!")


if __name__ == "__main__":
    asyncio.run(main())