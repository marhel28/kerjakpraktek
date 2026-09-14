import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if "DATABASE_URL" not in os.environ or "@db:" in os.environ.get("DATABASE_URL", ""):
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user_admin:password_rahasia@localhost:5433/marketplace_db"

if "MANTICORE_URL" not in os.environ or "manticore:9308" in os.environ.get("MANTICORE_URL", ""):
    os.environ["MANTICORE_URL"] = "http://localhost:9308"

import io
import json
import random
import asyncio
import requests
from PIL import Image
from uuid import uuid4
from sqlmodel import select
from sqlalchemy.orm import selectinload

from backend.db.main import db_session_maker
from backend.data.public.branlogo.model import Brand
from backend.data.public.assets.model import Asset
from backend.data.public.xbanner.model import Banner
from backend.data.stock.model import Stock
from backend.db.cdn import upload_file
from backend.scratch.sync_manticore import sync_all_stocks_to_manticore

BASE_URL = "http://localhost:8000"
TEST_DIR = os.path.join(PROJECT_ROOT, "test")
BRAND_DIR = os.path.join(TEST_DIR, "brand")
JUMBO_DIR = os.path.join(TEST_DIR, "Imagesection", "jumbo")
SECTION_DIR = os.path.join(TEST_DIR, "Imagesection")
FALLBACK_IMG = os.path.join(TEST_DIR, "cctv.jpg")


def get_compressed_webp_bytes(file_path: str, max_width: int = 1920, quality: int = 85) -> bytes:
    """Mengompres gambar besar menjadi WebP optimal untuk web agar upload cepat & anti-timeout"""
    with Image.open(file_path) as img:
        img = img.convert("RGB")
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=quality)
        return buf.getvalue()


# ══════════════════════════════════════════════════════════════
# 1️⃣ SEED JUMBOTRON UTAMA (/banner/ & home:hero-carousel)
# ══════════════════════════════════════════════════════════════
async def seed_jumbotron_banners():
    print("\n" + "="*50)
    print("🖼️ STEP 1: SEEDING JUMBOTRON UTAMA DARI FOLDER JUMBO")
    print("="*50)

    if not os.path.exists(JUMBO_DIR):
        print(f"❌ Folder jumbo tidak ditemukan di {JUMBO_DIR}")
        return

    jumbo_files = [f for f in os.listdir(JUMBO_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    jumbo_files.sort()

    banner_configs = [
        ("Spesialis CCTV & Smart Security Bandung - Pemasangan Rapi Bergaransi", "/services/booking", 1),
        ("Promo Diskon Paket CCTV Terlengkap 2026 - Hemat Hingga 25%", "/category/paket-cctv", 2),
        ("Sistem Keamanan Pintar Rumah & Kantor 24 Jam Nonstop", "/promo", 3),
    ]

    # Pastikan bersih atau update banner yang ada
    async with db_session_maker() as session:
        # 1. Hapus banner lama dari DB agar posisi fresh 1, 2, 3
        existing_banners = (await session.exec(select(Banner))).all()
        for b in existing_banners:
            await session.delete(b)
        await session.commit()
        print(f"🧹 Membersihkan banner jumbotron lama (total: {len(existing_banners)})")

    for i, file_name in enumerate(jumbo_files[:3]):
        file_path = os.path.join(JUMBO_DIR, file_name)
        title, link, pos = banner_configs[i % len(banner_configs)]

        print(f"[{i+1}/3] Mengompres & mengunggah Jumbotron: {file_name} ...")
        webp_bytes = get_compressed_webp_bytes(file_path, max_width=1920, quality=85)

        # Upload ke /banner/admin/create
        files = {"file": (f"jumbotron_{i+1}.webp", io.BytesIO(webp_bytes), "image/webp")}
        data = {"title": title, "link": link, "position": pos}

        try:
            r = requests.post(f"{BASE_URL}/banner/admin/create", data=data, files=files, timeout=30)
            if r.status_code == 200:
                print(f"  ✅ Sukses Upload Jumbotron Utama: {title[:40]} -> {r.json().get('uuid')}")
            else:
                print(f"  ⚠️ Gagal Upload Jumbotron ({r.status_code}): {r.text[:80]}")
        except Exception as e:
            print(f"  ❌ Error upload jumbotron: {e}")

        # Sekaligus upload ke Image Section 'home:hero-carousel'
        try:
            files_sec = {"file": (f"hero_{i+1}.webp", io.BytesIO(webp_bytes), "image/webp")}
            data_sec = {"target_url": link, "alt_text": title, "order": pos}
            r_sec = requests.post(
                f"{BASE_URL}/image-sections/home:hero-carousel/upload-banner",
                data=data_sec,
                files=files_sec,
                timeout=30
            )
            if r_sec.status_code in (200, 201):
                print(f"  ✅ Tersinkron ke Image Section 'home:hero-carousel'")
        except Exception as e:
            print(f"  ⚠️ Gagal sync ke hero carousel section: {e}")


# ══════════════════════════════════════════════════════════════
# 2️⃣ SEED ALL BRANDS (DARI test/brand + FALLBACK LOGO)
# ══════════════════════════════════════════════════════════════
async def seed_all_brands():
    print("\n" + "="*50)
    print("🏷️ STEP 2: SEEDING ALL BRANDS DENGAN LOGO RESMI & FALLBACK")
    print("="*50)

    # Definisi semua brand yang ada di toko CCTV
    brand_definitions = [
        {"name": "Dahua", "slug": "dahua", "file": "dahua.webp", "pos": 1},
        {"name": "Hikvision", "slug": "hikvision", "file": "hkvision.webp", "pos": 2},
        {"name": "Ezviz", "slug": "ezviz", "file": "ezviz.webp", "pos": 3},
        {"name": "Imou", "slug": "imou", "file": "imou.webp", "pos": 4},
        {"name": "Tapo", "slug": "tapo", "file": "tapo.webp", "pos": 5},
        {"name": "Tiandy", "slug": "tiandy", "file": "tiandy.webp", "pos": 6},
        {"name": "Glenz", "slug": "glenz", "file": "ezviz.webp", "pos": 7},
        {"name": "TP-Link", "slug": "tp-link", "file": "tapo.webp", "pos": 8},
        {"name": "Seagate", "slug": "seagate", "file": "dahua.webp", "pos": 9},
        {"name": "WD", "slug": "wd", "file": "tiandy.webp", "pos": 10},
        {"name": "Belden", "slug": "belden", "file": "hkvision.webp", "pos": 11},
    ]

    fallback_bytes = None
    if os.path.exists(FALLBACK_IMG):
        with open(FALLBACK_IMG, "rb") as f:
            fallback_bytes = f.read()

    async with db_session_maker() as session:
        for b_def in brand_definitions:
            name = b_def["name"]
            slug = b_def["slug"]
            logo_file = b_def["file"]
            pos = b_def["pos"]

            # Cari logo di folder test/brand
            logo_path = os.path.join(BRAND_DIR, logo_file)
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    file_bytes = f.read()
            elif fallback_bytes:
                file_bytes = fallback_bytes
            else:
                continue

            # Cek apakah brand sudah ada di DB berdasarkan slug atau name
            res = await session.exec(select(Brand).where((Brand.slug == slug) | (Brand.name.ilike(name))))
            existing = res.first()

            if existing:
                existing.name = name
                existing.slug = slug
                existing.route = f"/brands/{slug}"
                existing.position = pos
                existing.is_featured = True
                existing.is_active = True
                session.add(existing)
                await session.commit()
                print(f"  ℹ️ Brand '{name}' ({slug}) diperbarui.")
            else:
                # Upload logo ke CDN R2
                url = await upload_file(
                    file=file_bytes,
                    folder="brands",
                    filename=f"{slug}-{uuid4().hex[:8]}.webp",
                    content_type="image/webp"
                )
                asset = Asset(url=url, type="image", alt_text=f"Logo {name}")
                session.add(asset)
                await session.flush()

                new_brand = Brand(
                    name=name,
                    slug=slug,
                    logo_uuid=asset.uuid,
                    route=f"/brands/{slug}",
                    position=pos,
                    is_featured=True,
                    is_active=True
                )
                session.add(new_brand)
                await session.commit()
                print(f"  ✅ Brand '{name}' ({slug}) berhasil dibuat dengan logo CDN!")

    # Invalidate & refresh Redis cache for brands
    try:
        requests.get(f"{BASE_URL}/brands/")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
# 3️⃣ SEED PRODUK LENGKAP SETIAP BRAND ("DAN ISINYA JUGA")
# ══════════════════════════════════════════════════════════════
def seed_products_for_all_brands():
    print("\n" + "="*50)
    print("🛍️ STEP 3: SEEDING PRODUK LENGKAP SETIAP BRAND")
    print("="*50)

    # Ambil sample gambar untuk produk
    cached_img = None
    if os.path.exists(FALLBACK_IMG):
        with open(FALLBACK_IMG, "rb") as f:
            cached_img = f.read()
    else:
        # Fallback gambar apapun di test
        for root, _, files in os.walk(TEST_DIR):
            for f in files:
                if f.lower().endswith(('.jpg', '.png', '.webp')):
                    with open(os.path.join(root, f), "rb") as fl:
                        cached_img = fl.read()
                        break
            if cached_img:
                break

    # Daftar produk spesifik & berkualitas tinggi untuk setiap brand
    BRAND_PRODUCTS = [
        # Dahua
        ("Dahua IP Camera 2MP Full HD Outdoor Night Color", "Dahua", "kamera-cctv", "kamera-outdoor", "camera cctv", 420000, 15, {"resolution": "2MP", "night_color": "yes", "lens": "3.6mm", "waterproof": "IP67"}),
        ("Dahua Eyeball Dome 4MP Audio Mic Indoor", "Dahua", "kamera-cctv", "kamera-indoor", "camera cctv", 510000, 10, {"resolution": "4MP", "audio": "built-in mic", "lens": "2.8mm"}),
        ("Dahua Speed Dome PTZ 4MP 25x Optical Zoom", "Dahua", "kamera-cctv", "kamera-ptz", "camera cctv", 2850000, 20, {"resolution": "4MP", "zoom": "25x optical", "ir_distance": "100m"}),
        ("Dahua XVR 8 Channel 1080P WizSense AI SMD Plus", "Dahua", "dvr-nvr", "dvr-8ch", "recording system", 890000, 10, {"channels": 8, "ai": "SMD Plus", "compression": "H.265+"}),

        # Hikvision
        ("Hikvision ColorVu 4MP Full Color Audio Outdoor", "Hikvision", "kamera-cctv", "kamera-outdoor", "camera cctv", 650000, 20, {"resolution": "4MP", "night_vision": "full color 24h", "audio": "mic"}),
        ("Hikvision AcuSense Dome 2MP Smart Human Detection", "Hikvision", "kamera-cctv", "kamera-indoor", "camera cctv", 480000, 10, {"resolution": "2MP", "ai": "AcuSense human/vehicle", "poe": "yes"}),
        ("Hikvision NVR 16 Channel 4K PoE 2 SATA HDD", "Hikvision", "dvr-nvr", "nvr-16ch", "recording system", 2350000, 15, {"channels": 16, "poe_ports": 16, "max_resolution": "4K 8MP"}),
        ("Paket CCTV Hikvision 4 Titik Full Color 2MP + HDD", "Hikvision", "paket-cctv", "paket-4-cam", "paket bundling", 2850000, 20, {"kamera": "4 pcs ColorVu", "dvr": "4 Channel", "hdd": "1TB"}),

        # Ezviz
        ("Ezviz C6N Smart WiFi Camera 1080P Auto Tracking", "Ezviz", "kamera-cctv", "kamera-wireless", "camera cctv", 380000, 0, {"resolution": "2MP", "tracking": "360 degree pan-tilt", "audio": "two-way"}),
        ("Ezviz C3W Pro 4MP Full Color Night Vision Outdoor", "Ezviz", "kamera-cctv", "kamera-outdoor", "camera cctv", 720000, 15, {"resolution": "4MP", "color_night": "yes", "siren": "active defense"}),
        ("Ezviz C8C 360 Pan Tilt Outdoor AI Person Detection", "Ezviz", "kamera-cctv", "kamera-ptz", "camera cctv", 890000, 10, {"resolution": "2MP 1080P", "pan_tilt": "360 motorized", "waterproof": "IP65"}),

        # Imou
        ("Imou Ranger 2 4MP AI Human Detection PTZ WiFi", "Imou", "kamera-cctv", "kamera-wireless", "camera cctv", 495000, 10, {"resolution": "4MP", "ai_detection": "human & pet", "privacy_mask": "yes"}),
        ("Imou Bullet 2C 4MP Weatherproof Outdoor WiFi", "Imou", "kamera-cctv", "kamera-outdoor", "camera cctv", 520000, 12, {"resolution": "4MP", "night_vision": "30m", "mic": "built-in"}),
        ("Imou Cruiser 4MP Full Color Outdoor PTZ Camera", "Imou", "kamera-cctv", "kamera-ptz", "camera cctv", 920000, 15, {"resolution": "4MP", "ip_rating": "IP66", "spotlight": "built-in"}),

        # Tapo
        ("TP-Link Tapo C200 Pan Tilt Smart Security Camera", "Tapo", "kamera-cctv", "kamera-wireless", "camera cctv", 360000, 0, {"resolution": "1080P", "pan_tilt": "360 horizontal", "night_vision": "850nm"}),
        ("TP-Link Tapo C320WS 2K Outdoor Security Wi-Fi", "Tapo", "kamera-cctv", "kamera-outdoor", "camera cctv", 540000, 10, {"resolution": "4MP 2K QHD", "siren": "yes", "color_night": "starlight"}),
        ("TP-Link Tapo C500 Outdoor Pan/Tilt Security WiFi", "Tapo", "kamera-cctv", "kamera-ptz", "camera cctv", 650000, 10, {"resolution": "1080P", "ai_person": "yes", "weatherproof": "IP65"}),

        # Tiandy
        ("Tiandy Super Starlight 5MP POE IP Camera Outdoor", "Tiandy", "kamera-cctv", "kamera-outdoor", "camera cctv", 780000, 25, {"resolution": "5MP", "starlight": "0.002 Lux", "poe": "yes"}),
        ("Tiandy Color Maker 4MP Dome CCTV Camera Audio", "Tiandy", "kamera-cctv", "kamera-indoor", "camera cctv", 620000, 15, {"resolution": "4MP", "audio": "built-in mic", "housing": "metal"}),
        ("Tiandy 8 Channel 4K Ultra NVR PoE Plug and Play", "Tiandy", "dvr-nvr", "nvr-16ch", "recording system", 1450000, 10, {"channels": 8, "poe": "8 ports", "decoding": "4K Ultra HD"}),

        # Glenz
        ("Power Supply Jaring Glenz 12V 20A Central 18 Port", "Glenz", "cables-accessories", "psu-central", "aksesoris", 280000, 0, {"voltage": "12V", "amperage": "20A", "fuse": "individual PTC"}),
        ("Glenz Video Balun 4K Passive Transceiver Pasang", "Glenz", "cables-accessories", "bnc-dc", "aksesoris", 45000, 0, {"resolution": "up to 8MP 4K", "transmission": "300m UTP"}),
        ("Glenz Adaptor CCTV 12V 2A Switching Murni", "Glenz", "cables-accessories", "psu-central", "aksesoris", 35000, 0, {"input": "220V AC", "output": "12V 2A DC"}),

        # TP-Link
        ("TP-Link TL-SG1008P 8-Port Gigabit PoE Switch 64W", "TP-Link", "networking", "poe-switch", "jaringan", 820000, 5, {"ports": 8, "poe_budget": "64W", "speed": "1000Mbps"}),
        ("TP-Link Archer AX12 WiFi 6 Gigabit Dual-Band Router", "TP-Link", "networking", "wireless-router", "jaringan", 590000, 10, {"speed": "1500Mbps", "wifi_standard": "WiFi 6 AX", "antennas": 4}),
        ("TP-Link Omada EAP225 Ceiling Mount AC1350 AP", "TP-Link", "networking", "access-point", "jaringan", 890000, 8, {"band": "Dual-Band AC1350", "poe": "802.3af", "mesh": "Omada Mesh"}),

        # Seagate
        ("Seagate SkyHawk 1TB Surveillance Harddisk SATA", "Seagate", "storage", "hdd-1tb", "penyimpanan", 680000, 0, {"capacity": "1TB", "workload": "180TB/year", "firmware": "ImagePerfect"}),
        ("Seagate SkyHawk 2TB Surveillance Harddisk SATA", "Seagate", "storage", "hdd-2tb", "penyimpanan", 920000, 5, {"capacity": "2TB", "workload": "180TB/year", "cache": "64MB"}),
        ("Seagate SkyHawk 4TB Surveillance Harddisk SATA 64MB", "Seagate", "storage", "hdd-4tb", "penyimpanan", 1450000, 5, {"capacity": "4TB", "rpm": "5900", "workload": "180TB/year"}),

        # WD
        ("Western Digital Purple 1TB CCTV Harddrive SATA", "WD", "storage", "hdd-1tb", "penyimpanan", 670000, 0, {"capacity": "1TB", "technology": "AllFrame 4K", "workload": "180TB/year"}),
        ("Western Digital Purple 2TB CCTV Harddrive SATA", "WD", "storage", "hdd-2tb", "penyimpanan", 950000, 0, {"capacity": "2TB", "technology": "AllFrame 4K", "cache": "64MB"}),
        ("Western Digital Purple 4TB CCTV Harddrive SATA", "WD", "storage", "hdd-4tb", "penyimpanan", 1480000, 5, {"capacity": "4TB", "technology": "AllFrame 4K", "cache": "256MB"}),

        # Belden
        ("Kabel UTP Belden Cat6 Original 305 Meter USA Quality", "Belden", "cables-accessories", "utp-cat6", "kabel", 1850000, 10, {"length": "305m", "category": "Cat6 1000Mbps", "conductor": "Pure Solid Copper"}),
        ("Kabel Coaxial RG59 Belden + Power 300 Meter Roll", "Belden", "cables-accessories", "coaxial-rg59", "kabel", 1650000, 8, {"length": "300m", "type": "RG59 + 2x0.75 Power", "shield": "95% Braid"}),
    ]

    success_count = 0
    for i, prod in enumerate(BRAND_PRODUCTS):
        title, brand, cat_slug, sub_slug, item_type, orig_price, disc, specs = prod
        final_price = int(orig_price - (orig_price * disc / 100)) if disc > 0 else orig_price

        data = {
            "title": title,
            "brand": brand,
            "category_slug": cat_slug,
            "subcategory_slug": sub_slug,
            "type": item_type,
            "original_price": orig_price,
            "discount_percentage": disc,
            "online_price": final_price,
            "stok": random.randint(25, 80),
            "weight": random.choice([500, 800, 1500, 3000]),
            "specs": json.dumps(specs)
        }

        files = [("images", ("product.jpg", io.BytesIO(cached_img), "image/jpeg"))]
        try:
            res = requests.post(f"{BASE_URL}/stok/admin/create", data=data, files=files, timeout=15)
            if res.status_code in (200, 201):
                success_count += 1
                print(f"  [{i+1}/{len(BRAND_PRODUCTS)}] ✅ [{brand}] {title[:38]} | Rp {final_price:,}")
            elif res.status_code == 500 and "duplicate key" in res.text:
                print(f"  [{i+1}/{len(BRAND_PRODUCTS)}] ℹ️ [{brand}] {title[:38]} (Sudah ada di DB)")
            else:
                print(f"  [{i+1}/{len(BRAND_PRODUCTS)}] ⚠️ Gagal ({res.status_code}): {res.text[:80]}")
        except Exception as e:
            print(f"  [{i+1}/{len(BRAND_PRODUCTS)}] ❌ Error: {e}")

    print(f"\n✅ Total produk baru berhasil ditambahkan: {success_count}")


# ══════════════════════════════════════════════════════════════
# 🚀 MAIN RUNNER
# ══════════════════════════════════════════════════════════════
async def main():
    print("\n🚀 MEMULAI SEEDER JUMBOTRON UTAMA & BRANDS LENGKAP 🚀")

    # 1. Jumbotron Utama
    await seed_jumbotron_banners()

    # 2. Brands
    await seed_all_brands()

    # 3. Produk untuk semua Brands
    seed_products_for_all_brands()

    # 4. Sinkronisasi penuh ke Manticore Search
    print("\n" + "="*50)
    print("🔍 STEP 4: SINKRONISASI KE MANTICORE SEARCH ENGINE")
    print("="*50)
    await sync_all_stocks_to_manticore()

    print("\n" + "="*50)
    print("🎉 SEEDER JUMBOTRON & SEMUA BRAND SELESAI 100%!")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
