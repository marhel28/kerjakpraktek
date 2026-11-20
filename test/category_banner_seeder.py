import os
import asyncio
import httpx
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "http://localhost:8000"
BANNER_DIR = os.path.join(os.path.dirname(__file__), "generated", "category_banners")

BANNERS = [
    {
        "filename": "cctv_deal_1.jpg",
        "title": "PROMO SPESIAL CCTV",
        "subtitle": "Diskon Hingga 45% - Garansi Resmi 2 Tahun",
        "badge": "OFFICIAL DEAL",
        "bg_color": (15, 23, 42),      # Slate 900
        "accent_color": (234, 179, 8),  # Amber 500
        "target_url": "/category/kamera-cctv",
        "alt_text": "Promo Kamera CCTV Diskon 45%",
        "order": 1,
    },
    {
        "filename": "cctv_deal_2.jpg",
        "title": "SMART IP CAMERA COLORVU",
        "subtitle": "Pengawasan 24 Jam Full Color Siap Pasang",
        "badge": "BEST SELLER",
        "bg_color": (24, 24, 27),       # Zinc 900
        "accent_color": (56, 189, 248), # Sky 400
        "target_url": "/category/ip-camera",
        "alt_text": "IP Camera ColorVu Pengawasan Full Color",
        "order": 2,
    },
]

def generate_banner_images():
    os.makedirs(BANNER_DIR, exist_ok=True)
    for b in BANNERS:
        filepath = os.path.join(BANNER_DIR, b["filename"])
        img = Image.new("RGB", (1000, 500), color=b["bg_color"])
        draw = ImageDraw.Draw(img)

        # Draw visual accents
        draw.rectangle([0, 0, 30, 500], fill=b["accent_color"])
        draw.rectangle([50, 40, 220, 80], fill=b["accent_color"])
        draw.text((65, 52), b["badge"], fill=(0, 0, 0))

        # Typography
        draw.text((50, 130), b["title"], fill=(255, 255, 255))
        draw.text((50, 190), b["subtitle"], fill=(203, 213, 225))

        # Button shape
        draw.rectangle([50, 300, 260, 360], fill=b["accent_color"])
        draw.text((75, 322), "BELI SEKARANG", fill=(0, 0, 0))

        img.save(filepath, "JPEG", quality=90)
        print(f"Generated image: {filepath}")

async def seed_category_banner():
    generate_banner_images()

    async with httpx.AsyncClient(timeout=30.0) as client:
        ident = "category:kamera-cctv"
        print(f"\nChecking image section for [{ident}]...")

        # Create or update section
        section_payload = {
            "identifier": ident,
            "title": "Banner Kategori Kamera CCTV",
            "mode": "asymRight",
            "is_active": True,
        }

        res = await client.post(f"{BASE_URL}/image-sections", json=section_payload)
        if res.status_code == 200:
            print(f"Section created: {res.json()}")
        else:
            print(f"Section already exists or info: {res.status_code} - {res.text}")

        # Upload images
        for b in BANNERS:
            filepath = os.path.join(BANNER_DIR, b["filename"])
            print(f"Uploading banner: {b['filename']} -> {b['target_url']}")
            with open(filepath, "rb") as f:
                upload_res = await client.post(
                    f"{BASE_URL}/image-sections/{ident}/upload-banner",
                    data={
                        "target_url": b["target_url"],
                        "alt_text": b["alt_text"],
                        "order": b["order"],
                    },
                    files={"file": (b["filename"], f, "image/jpeg")},
                )
                print(f"Upload result ({upload_res.status_code}): {upload_res.text[:120]}")

        # Test Public Endpoint
        print("\nTesting Public API Endpoint:")
        pub_res = await client.get(f"{BASE_URL}/image-sections/public/{ident}")
        print(f"GET /image-sections/public/{ident} -> Status {pub_res.status_code}")
        if pub_res.status_code == 200:
            data = pub_res.json()
            print("Public Data:", data)

if __name__ == "__main__":
    asyncio.run(seed_category_banner())