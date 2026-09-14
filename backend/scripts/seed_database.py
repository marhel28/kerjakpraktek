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

import json
import random
import io
import asyncio
from datetime import datetime, timezone
import requests

from sqlmodel import select, delete
from sqlalchemy.orm import selectinload
from backend.db.main import db_session_maker
from backend.auth.service import UserService
from backend.auth.utility import create_access_token, build_user_payload
from backend.auth.model import User, UserRole

BASE_URL = "http://localhost:8000"
TEST_DIR = os.path.join(PROJECT_ROOT, "test")
BRAND_DIR = os.path.join(TEST_DIR, "brand")
IMAGE_PATH = os.path.join(TEST_DIR, "cctv.jpg")
IMAGE_SECTION_DIR = os.path.join(TEST_DIR, "Imagesection")

print(f"📁 PROJECT_ROOT: {PROJECT_ROOT}")
print(f"📁 TEST_DIR: {TEST_DIR}")

# ══════════════════════════════════════════════════════════════
# 1️⃣ ENSURE ADMIN USER & GET ADMIN TOKEN
# ══════════════════════════════════════════════════════════════
async def get_or_create_admin_token() -> str:
    print("\n" + "="*50)
    print("🔑 STEP 1: PREPARING ADMIN USER & TOKEN")
    print("="*50)
    user_svc = UserService()
    async with db_session_maker() as session:
        admin = await user_svc.get_user_by_email("ammarmaulahela20@gmail.com", session)
        if not admin:
            print("Creating new admin user...")
            admin = User(
                username="admin_padjajaran",
                email="ammarmaulahela20@gmail.com",
                role=UserRole.ADMIN,
                is_verified=True
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
        else:
            admin.role = UserRole.ADMIN
            session.add(admin)
            await session.commit()
            await session.refresh(admin)

        token = create_access_token(build_user_payload(admin))
        print(f"✅ Admin: {admin.username} ({admin.email}) | Role: {admin.role}")
        return token


# ══════════════════════════════════════════════════════════════
# 2️⃣ SEED CATEGORIES & SUBCATEGORIES
# ══════════════════════════════════════════════════════════════
def seed_categories_and_subs():
    print("\n" + "="*50)
    print("📦 STEP 2: SEEDING CATEGORIES & SUBCATEGORIES")
    print("="*50)
    
    categories = [
        {"name": "CCTV Camera", "slug": "kamera-cctv", "icon_name": "i-heroicons-video-camera", "position": 1,
         "subs": [("Kamera Indoor", "kamera-indoor"), ("Kamera Outdoor", "kamera-outdoor"), ("Kamera PTZ", "kamera-ptz"), ("Kamera Wireless", "kamera-wireless")]},
        {"name": "DVR & NVR", "slug": "dvr-nvr", "icon_name": "i-heroicons-cpu-chip", "position": 2,
         "subs": [("DVR 4 Channel", "dvr-4ch"), ("DVR 8 Channel", "dvr-8ch"), ("NVR 16 Channel", "nvr-16ch"), ("NVR 32 Channel", "nvr-32ch")]},
        {"name": "Security Alarm", "slug": "security-alarm", "icon_name": "i-heroicons-bell-alert", "position": 3,
         "subs": [("Sensor Gerak PIR", "sensor-pir"), ("Sirine & Strobe", "sirine-strobe"), ("Magnetic Door Sensor", "door-sensor")]},
        {"name": "Access Control", "slug": "access-control", "icon_name": "i-heroicons-lock-closed", "position": 4,
         "subs": [("Fingerprint Reader", "fingerprint"), ("Face Recognition", "face-recognition"), ("RFID Card Access", "rfid-access")]},
        {"name": "Networking", "slug": "networking", "icon_name": "i-heroicons-wifi", "position": 5,
         "subs": [("PoE Switch", "poe-switch"), ("Wireless Router", "wireless-router"), ("Access Point", "access-point")]},
        {"name": "Cables & Accessories", "slug": "cables-accessories", "icon_name": "i-heroicons-link", "position": 6,
         "subs": [("Kabel Coaxial RG59", "coaxial-rg59"), ("Kabel UTP Cat6", "utp-cat6"), ("Power Supply Central", "psu-central"), ("BNC & DC Jack", "bnc-dc")]},
        {"name": "Smart Home", "slug": "smart-home", "icon_name": "i-heroicons-home-modern", "position": 7,
         "subs": [("Smart Plug", "smart-plug"), ("Smart Light", "smart-light"), ("Smart Door Lock", "smart-door-lock")]},
        {"name": "Storage", "slug": "storage", "icon_name": "i-heroicons-server", "position": 8,
         "subs": [("HDD Surveillance 1TB", "hdd-1tb"), ("HDD Surveillance 2TB", "hdd-2tb"), ("HDD Surveillance 4TB", "hdd-4tb"), ("MicroSD C10", "microsd")]},
        {"name": "Paket CCTV", "slug": "paket-cctv", "icon_name": "i-heroicons-gift", "position": 9,
         "subs": [("Paket 2 Kamera", "paket-2-cam"), ("Paket 4 Kamera", "paket-4-cam"), ("Paket 8 Kamera", "paket-8-cam")]},
    ]

    # Fetch existing categories first
    existing_map = {}
    try:
        r = requests.get(f"{BASE_URL}/category/")
        if r.status_code == 200:
            for item in r.json():
                existing_map[item["slug"]] = item
    except Exception as e:
        print(f"Warning fetching existing categories: {e}")

    cat_slug_to_uuid = {}
    subcat_mapping = {}

    for cat_data in categories:
        slug = cat_data["slug"]
        name = cat_data["name"]
        subs = cat_data["subs"]
        subcat_mapping[slug] = []

        if slug in existing_map:
            cat_uuid = existing_map[slug]["id"]
            print(f" ℹ️  Category '{name}' already exists.")
            cat_slug_to_uuid[slug] = cat_uuid
            for sub in existing_map[slug].get("subcategories", []):
                subcat_mapping[slug].append(sub["slug"])
        else:
            payload = {
                "name": name,
                "slug": slug,
                "icon_name": cat_data["icon_name"],
                "position": cat_data["position"]
            }
            res = requests.post(f"{BASE_URL}/category/admin/category", data=payload)
            if res.status_code == 200:
                cat_uuid = res.json().get("uuid")
                cat_slug_to_uuid[slug] = cat_uuid
                print(f" ✅ Created Category: {name}")
            else:
                print(f" ⚠️ Failed Category: {name} ({res.status_code})")
                continue

        # Create subcategories
        for sub_name, sub_slug in subs:
            if sub_slug not in subcat_mapping[slug]:
                sub_payload = {
                    "category_uuid": cat_uuid,
                    "name": sub_name,
                    "slug": sub_slug,
                    "position": 1
                }
                res_sub = requests.post(f"{BASE_URL}/category/admin/subcategory", data=sub_payload)
                if res_sub.status_code == 200:
                    subcat_mapping[slug].append(sub_slug)
                    print(f"   ➜ ✅ Subcategory: {sub_name}")
                else:
                    print(f"   ➜ ⚠️ Failed Sub: {sub_name} ({res_sub.status_code})")

    return cat_slug_to_uuid, subcat_mapping


# ══════════════════════════════════════════════════════════════
# 3️⃣ SEED BRANDS
# ══════════════════════════════════════════════════════════════
def seed_brands():
    print("\n" + "="*50)
    print("🏷️ STEP 3: SEEDING BRANDS")
    print("="*50)
    
    if not os.path.exists(BRAND_DIR):
        print(f"⚠️ Brand dir {BRAND_DIR} not found!")
        return

    images = [f for f in os.listdir(BRAND_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    for idx, filename in enumerate(images):
        raw_name = os.path.splitext(filename)[0]
        name = raw_name.replace("-", " ").replace("_", " ").title()
        slug = raw_name.lower().replace(" ", "-").replace("_", "-")

        data = {
            "name": name,
            "slug": slug,
            "title": name,
            "route": f"/brands/{slug}",
            "position": idx + 1,
            "is_featured": "true"
        }

        filepath = os.path.join(BRAND_DIR, filename)
        with open(filepath, "rb") as f:
            files = {"file": (filename, f, "image/webp")}
            res = requests.post(f"{BASE_URL}/brands/admin/create", data=data, files=files)
            if res.status_code == 200:
                print(f" ✅ Brand: {name}")
            else:
                print(f" ⚠️ Brand {name} ({res.status_code})")


# ══════════════════════════════════════════════════════════════
# 4️⃣ SEED PRODUCTS (STOCKS)
# ══════════════════════════════════════════════════════════════
def seed_products(subcat_mapping, total=60):
    print("\n" + "="*50)
    print(f"🛍️ STEP 4: SEEDING {total} PRODUCTS (WITH SPECS & DISCOUNTS)")
    print("="*50)

    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Image not found: {IMAGE_PATH}")
        return []

    with open(IMAGE_PATH, "rb") as f:
        cached_img = f.read()

    # Product templates
    PRODUCT_TEMPLATES = [
        ("Dahua IP Camera 2MP Full HD Outdoor Night Color", "Dahua", "kamera-cctv", "camera cctv", 420000, 15, {"resolution": "2MP", "night_vision": "yes", "lens": "3.6mm", "type": "bullet", "waterproof": "IP67"}),
        ("Hikvision ColorVu 4MP Dome Kamera Audio Mic", "Hikvision", "kamera-cctv", "camera cctv", 650000, 20, {"resolution": "4MP", "night_vision": "yes", "audio": "built-in mic", "lens": "2.8mm"}),
        ("Ezviz C6N Smart WiFi Camera 1080P Auto Tracking", "Ezviz", "kamera-cctv", "camera cctv", 380000, 0, {"resolution": "2MP", "tracking": "pan-tilt 360", "audio": "two-way"}),
        ("Imou Ranger 2 4MP AI Human Detection PTZ", "Imou", "kamera-cctv", "camera cctv", 495000, 10, {"resolution": "4MP", "ai_detection": "human & pet", "cloud": "supported"}),
        ("Tiandy Super Starlight 5MP POE IP Camera", "Tiandy", "kamera-cctv", "camera cctv", 780000, 25, {"resolution": "5MP", "starlight": "0.002 Lux", "poe": "yes"}),
        ("TP-Link Tapo C320WS 2K Outdoor Security Wi-Fi", "Tapo", "kamera-cctv", "camera cctv", 540000, 10, {"resolution": "4MP", "siren": "yes", "night_vision": "full color"}),
        ("Dahua XVR 8 Channel 1080P WizSense AI", "Dahua", "dvr-nvr", "recording system", 890000, 10, {"channels": 8, "ai": "smd plus", "h265": "plus"}),
        ("Hikvision NVR 16 Channel 4K PoE 2 SATA", "Hikvision", "dvr-nvr", "recording system", 2350000, 15, {"channels": 16, "poe_ports": 16, "max_resolution": "4K 8MP"}),
        ("Seagate SkyHawk 4TB Surveillance Harddisk SATA", "Seagate", "storage", "penyimpanan", 1450000, 5, {"capacity": "4TB", "rpm": "5900", "workload": "180TB/year"}),
        ("Western Digital Purple 2TB CCTV Harddrive", "WD", "storage", "penyimpanan", 950000, 0, {"capacity": "2TB", "allframe": "4K", "cache": "64MB"}),
        ("Kabel UTP Belden Cat6 Original 305 Meter", "Belden", "cables-accessories", "kabel", 1850000, 10, {"length": "305m", "category": "Cat6", "conductor": "Pure Copper"}),
        ("Power Supply Jaring 12V 20A Central 18 Port", "Glenz", "cables-accessories", "aksesoris", 280000, 0, {"voltage": "12V", "amperage": "20A", "ports": 18}),
        ("Paket CCTV Hikvision 4 Titik Full Color 2MP + HDD 1TB", "Hikvision", "paket-cctv", "paket bundling", 2850000, 20, {"kamera": "4 pcs ColorVu", "dvr": "4 Channel", "hdd": "1TB Seagate"}),
        ("Paket CCTV Dahua 8 Titik 4K Audio Mic + Pasang", "Dahua", "paket-cctv", "paket bundling", 5800000, 25, {"kamera": "8 pcs 4MP Audio", "dvr": "8 Channel AI", "hdd": "2TB"}),
        ("TP-Link TL-SG1008P 8-Port Gigabit PoE Switch", "TP-Link", "networking", "jaringan", 820000, 5, {"ports": 8, "poe_budget": "64W", "speed": "1000Mbps"}),
    ]

    created_stocks = []
    
    for i in range(total):
        tmpl = PRODUCT_TEMPLATES[i % len(PRODUCT_TEMPLATES)]
        base_title, brand, cat_slug, item_type, orig_price, disc, specs = tmpl
        
        # Add variation
        variant = (i // len(PRODUCT_TEMPLATES)) + 1
        title = f"{base_title} (Varian {variant})" if variant > 1 else base_title
        
        available_subs = subcat_mapping.get(cat_slug, [])
        sub_slug = available_subs[i % len(available_subs)] if available_subs else ""
        
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
            "stok": random.randint(20, 100),
            "weight": random.choice([500, 700, 1200, 2500]),
            "specs": json.dumps(specs)
        }

        files = [("images", ("cctv.jpg", io.BytesIO(cached_img), "image/jpeg"))]
        try:
            res = requests.post(f"{BASE_URL}/stok/admin/create", data=data, files=files, timeout=15)
            if res.status_code in (200, 201):
                res_data = res.json().get("data", {})
                created_stocks.append(res_data)
                print(f"[{i+1}/{total}] ✅ {title[:40]} | Rp {final_price:,}")
            else:
                print(f"[{i+1}/{total}] ⚠️ GAGAL ({res.status_code}) {res.text[:80]}")
        except Exception as e:
            print(f"[{i+1}/{total}] ❌ Error: {e}")

    return created_stocks


# ══════════════════════════════════════════════════════════════
# 5️⃣ SEED SERVICE PRICING & PACKAGES
# ══════════════════════════════════════════════════════════════
def seed_service_booking(admin_token: str, stocks: list):
    print("\n" + "="*50)
    print("🛠️ STEP 5: SEEDING SERVICE PRICING CONFIG & PACKAGES")
    print("="*50)

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    # 1. Pricing Config
    pricing_payload = {
        "base_price_per_camera": {
            "installation": 250000,
            "maintenance": 150000,
            "troubleshoot": 100000
        },
        "brand_multiplier": {
            "glenz": 1.0,
            "ezviz": 1.2,
            "dahua": 1.3,
            "hikvision": 1.5,
            "tiandy": 1.4,
            "tapo": 1.2
        },
        "consultation_fee": 0,
        "transport_per_km": 4000,
        "transport_min_fee": 25000,
        "transport_max_fee": 350000,
        "max_distance_km": 60.0,
        "dp_percentage": 30,
        "addons_config": [
            {"key": "night_vision", "label": "ColorVu / Full Color Malam Hari", "type": "per_cam", "price": 175000, "description": "Kamera tetap berwarna saat gelap total", "icon": "lucide:moon"},
            {"key": "audio_mic", "label": "Built-in Microphone", "type": "per_cam", "price": 125000, "description": "Merekam suara percakapan sekitar kamera", "icon": "lucide:mic"},
            {"key": "conduit_pipe", "label": "Pipa Pelindung Kabel (Conduit)", "type": "flat", "price": 350000, "description": "Kabel rapi & aman dari gigitan tikus", "icon": "lucide:shield-check"}
        ]
    }

    try:
        r_p = requests.post(f"{BASE_URL}/admin/service/pricing", headers=headers, json=pricing_payload)
        if r_p.status_code in (200, 201):
            print(" ✅ Service Pricing Config created successfully.")
        else:
            print(f" ⚠️ Pricing Config: {r_p.status_code} - {r_p.text}")
    except Exception as e:
        print(f" ❌ Pricing Config error: {e}")

    # 2. Service Packages
    # Select stock uuids for bundle items if available
    camera_stock = stocks[0]["uuid"] if len(stocks) > 0 else None
    cable_stock = stocks[1]["uuid"] if len(stocks) > 1 else None

    packages = [
        {
            "name": "Paket Pintar Residensial 4 Titik",
            "slug": "paket-pintar-residensial-4-titik",
            "description": "Solusi keamanan cerdas untuk rumah tinggal. Dilengkapi pantauan langsung dari HP 24 Jam.",
            "category": "installation",
            "camera_count": 4,
            "default_brand": "ezviz",
            "thumbnail_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80",
            "highlights": ["4x Kamera 2MP Full Color", "Koneksi Langsung ke HP", "Gratis Setting Aplikasi", "Pengerjaan Rapi 1 Hari"],
            "is_active": True,
            "sort_order": 1,
            "items": [
                {"stock_uuid": camera_stock, "quantity": 4, "label": "Smart IP Camera 2MP", "sort_order": 1},
                {"stock_uuid": cable_stock, "quantity": 4, "label": "Kabel UTP 15m", "sort_order": 2}
            ] if camera_stock and cable_stock else []
        },
        {
            "name": "Paket Premium Bisnis 8 Titik",
            "slug": "paket-premium-bisnis-8-titik",
            "description": "Proteksi tingkat tinggi untuk ruko, kantor, dan gudang. Resolusi tajam hingga 4K Ultra HD.",
            "category": "installation",
            "camera_count": 8,
            "default_brand": "hikvision",
            "thumbnail_url": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=600&q=80",
            "highlights": ["8x Kamera 4MP Ultra HD", "DVR 8 Channel H.265+", "Harddisk Surveillance 2TB", "Garansi Servis 1 Tahun"],
            "is_active": True,
            "sort_order": 2,
            "items": [
                {"stock_uuid": camera_stock, "quantity": 8, "label": "Kamera Hikvision 4MP", "sort_order": 1},
                {"stock_uuid": cable_stock, "quantity": 8, "label": "Kabel Belden (per 10m)", "sort_order": 2}
            ] if camera_stock and cable_stock else []
        }
    ]

    form_headers = {"Authorization": f"Bearer {admin_token}"}
    for pkg in packages:
        try:
            res_pkg = requests.post(
                f"{BASE_URL}/admin/service/packages",
                headers=form_headers,
                data={"data": json.dumps(pkg)},
                timeout=15
            )
            if res_pkg.status_code in (200, 201):
                print(f" ✅ Created Package: {pkg['name']}")
            else:
                print(f" ⚠️ Package {pkg['name']} ({res_pkg.status_code}) {res_pkg.text[:100]}")
        except Exception as e:
            print(f" ❌ Package error: {e}")


# ══════════════════════════════════════════════════════════════
# 6️⃣ SEED BANNERS & IMAGE SECTIONS
# ══════════════════════════════════════════════════════════════
def seed_banners():
    print("\n" + "="*50)
    print("🎨 STEP 6: SEEDING HOMEPAGE & BOTTOM BANNERS")
    print("="*50)

    if os.path.exists(IMAGE_PATH):
        with open(IMAGE_PATH, "rb") as f:
            img_bytes = f.read()

        bottom_banners = [
            ("Promo Spesial Pemasangan CCTV Bulan Ini", "/promo", 1),
            ("Teknisi Bersertifikasi & Bergaransi Resmi", "/about", 2),
            ("Portofolio Proyek 1.000+ Kamera Terpasang", "/portfolio", 3),
            ("Katalog Kamera CCTV & Aksesori Terlengkap", "/category/kamera-cctv", 4)
        ]

        for title, link, order in bottom_banners:
            files = {"file": ("banner.jpg", io.BytesIO(img_bytes), "image/jpeg")}
            data = {"title": title, "route_link": link, "is_active": "true", "sort_order": str(order)}
            try:
                r = requests.post(f"{BASE_URL}/main-bottom/admin", data=data, files=files, timeout=15)
                if r.status_code == 200:
                    print(f" ✅ Bottom Banner: {title[:35]}")
                else:
                    print(f" ⚠️ Bottom Banner ({r.status_code})")
            except Exception as e:
                print(f" ❌ Error Bottom Banner: {e}")

    # Image Sections
    if os.path.exists(IMAGE_SECTION_DIR):
        img_files = [f for f in os.listdir(IMAGE_SECTION_DIR) if f.lower().endswith(('.jpg', '.png', '.webp'))]
        sections = [
            ("home:hero-carousel", "Hero Carousel Utama Homepage"),
            ("category:kamera-cctv", "Banner Kategori Kamera CCTV"),
            ("promo:ramadan-sale", "Banner Promo Eksklusif")
        ]

        for ident, sec_title in sections:
            try:
                r_sec = requests.post(f"{BASE_URL}/image-sections", json={"identifier": ident, "title": sec_title, "is_active": True})
                print(f" 📂 Section: [{ident}] ({r_sec.status_code})")
                
                # Upload item
                if img_files:
                    pick_img = img_files[0]
                    with open(os.path.join(IMAGE_SECTION_DIR, pick_img), "rb") as f:
                        files = {"file": (pick_img, f, "image/jpeg")}
                        data = {"target_url": f"/promo/{ident}", "alt_text": sec_title, "order": 1}
                        r_item = requests.post(f"{BASE_URL}/image-sections/{ident}/upload-banner", data=data, files=files, timeout=15)
                        if r_item.status_code in (200, 201):
                            print(f"   ➜ ✅ Uploaded banner item to [{ident}]")
            except Exception as e:
                print(f" ❌ Error Image Section {ident}: {e}")


# ══════════════════════════════════════════════════════════════
# 7️⃣ SEED ABOUT US PAGE
# ══════════════════════════════════════════════════════════════
def seed_about_us():
    print("\n" + "="*50)
    print("ℹ️ STEP 7: SEEDING ABOUT US PAGE")
    print("="*50)

    about_payload = {
        "hero_badge_text": "Partner Keamanan Anda",
        "hero_heading": "Solusi Sistem Keamanan CCTV Profesional & Terpercaya",
        "hero_subheading": "Padjajaran CCTV mendesain, memasang, dan memelihara sistem keamanan berkualitas tinggi untuk rumah, bisnis, dan industri.",
        "cta_heading": "Garansi Resmi Ganti Baru",
        "cta_body": "Kamera bermasalah atau unit rusak? Kami berikan jaminan penggantian unit baru di tahun pertama tanpa prosedur berbelit-belit.",
        "stats": [
            {"value": "1.200+", "label": "Kamera Terpasang", "order": 1},
            {"value": "99.4%", "label": "Kepuasan Pelanggan", "order": 2},
            {"value": "12+", "label": "Tahun Pengalaman", "order": 3},
            {"value": "24/7", "label": "Layanan Darurat", "order": 4}
        ],
        "values": [
            {"icon": "lucide:shield-check", "title": "Kualitas Tanpa Kompromi", "desc": "Hanya menggunakan kabel tembaga murni dan perangkat original bergaransi resmi.", "order": 1},
            {"icon": "lucide:sparkles", "title": "Instalasi Estetik & Rapi", "desc": "Pemasangan kabel tersembunyi dengan conduit pelindung agar rapi dan aman.", "order": 2},
            {"icon": "lucide:headphones", "title": "Edukasi & Pelayanan Tuntas", "desc": "Pelatihan setting HP dan panduan penggunaan sistem CCTV hingga tuntas.", "order": 3}
        ]
    }

    try:
        r = requests.post(f"{BASE_URL}/abouts", json=about_payload, timeout=15)
        if r.status_code in (200, 201):
            print(" ✅ About Us page created successfully.")
        else:
            print(f" ℹ️ About Us: {r.status_code} ({r.text[:60]})")

        # Gallery
        if os.path.exists(IMAGE_PATH):
            with open(IMAGE_PATH, "rb") as f:
                files = {"file": ("gallery.jpg", f, "image/jpeg")}
                data = {"caption": "Instalasi CCTV Ruko & Kantor", "order": 1}
                r_g = requests.post(f"{BASE_URL}/abouts/gallery", data=data, files=files, timeout=15)
                if r_g.status_code in (200, 201):
                    print(" ✅ About Gallery image uploaded.")
    except Exception as e:
        print(f" ❌ About Us error: {e}")


# ══════════════════════════════════════════════════════════════
# 8️⃣ SEED PORTFOLIO PROJECTS & REVIEWS
# ══════════════════════════════════════════════════════════════
def seed_portfolio():
    print("\n" + "="*50)
    print("🏆 STEP 8: SEEDING PORTFOLIO PROJECTS & REVIEWS")
    print("="*50)

    projects = [
        {
            "title": "Sistem CCTV Gudang Logistik PT Maju Bersama",
            "category": "Manufaktur",
            "location": "Bekasi, Jawa Barat",
            "cameras": 24,
            "package_slug": "enterprise",
            "client_type": "Pemilik Gudang & Logistik",
            "problem": "Area gudang 5.000 m2 rawan titik buta dengan kamera analog lama.",
            "solution": "Instalasi 24 unit kamera IP 4MP ColorVu dengan NVR 16CH dan storage 20TB.",
            "result": "Kehilangan barang turun 95% dan pemantauan mobile aktif 24 jam.",
            "is_featured": True,
            "sort_order": 1
        },
        {
            "title": "Pengawasan Terpadu Komplek Pergudangan Cikarang",
            "category": "Komersial",
            "location": "Cikarang, Jawa Barat",
            "cameras": 16,
            "package_slug": "bisnis",
            "client_type": "Komersial",
            "problem": "Pintu gerbang utama memerlukan rekaman plat nomor kendaraan yang jelas.",
            "solution": "Pemasangan kamera ANPR dan PTZ Optical Zoom 25x pada gerbang utama.",
            "result": "Pencatatan kendaraan 100% otomatis dan akurat.",
            "is_featured": True,
            "sort_order": 2
        }
    ]

    for p in projects:
        try:
            r = requests.post(f"{BASE_URL}/portfolio/projects", json=p, timeout=15)
            if r.status_code in (200, 201):
                p_id = r.json().get("id")
                print(f" ✅ Portfolio Project: {p['title'][:35]}")
                # Upload image
                if os.path.exists(IMAGE_PATH):
                    with open(IMAGE_PATH, "rb") as f:
                        files = [("files", ("cctv.jpg", f, "image/jpeg"))]
                        data = {"role": "cover", "alt": p["title"]}
                        requests.post(f"{BASE_URL}/portfolio/projects/{p_id}/images", data=data, files=files, timeout=15)
            else:
                print(f" ⚠️ Portfolio {p['title'][:30]} ({r.status_code})")
        except Exception as e:
            print(f" ❌ Portfolio error: {e}")

    # Reviews
    reviews = [
        {"name": "Budi Santoso", "role": "Pemilik Gudang", "rating": 5, "text": "Instalasi sangat rapi, teknisi profesional, hasil kamera jernih siang malam!"},
        {"name": "Hendra Wijaya", "role": "Owner Restoran", "rating": 5, "text": "Harga sangat bersahabat, kualitas pengerjaan bintang lima. Sangat puas!"},
        {"name": "Siti Aminah", "role": "Kepala Sekolah", "rating": 5, "text": "Sistem CCTV sekolah kami sekarang aman terkendali, monitoring lewat HP mudah digunakan."}
    ]
    for rev in reviews:
        try:
            requests.post(f"{BASE_URL}/portfolio/reviews", json=rev, timeout=10)
        except Exception:
            pass
    print(" ✅ Portfolio customer reviews seeded.")


# ══════════════════════════════════════════════════════════════
# 9️⃣ RUN TECHNICIANS & MANTICORE SYNC
# ══════════════════════════════════════════════════════════════
async def run_technicians_and_manticore():
    print("\n" + "="*50)
    print("🔧 STEP 9: SEEDING TECHNICIANS & FULL MANTICORE SYNC")
    print("="*50)

    # 1. Technicians
    try:
        from backend.scripts.seed_technicians import seed_technicians
        await seed_technicians()
        print(" ✅ Technicians seeded.")
    except Exception as e:
        print(f" ⚠️ Technicians seeder: {e}")

    # 2. Manticore Full Sync
    try:
        from backend.scratch.sync_manticore import sync_all_stocks_to_manticore
        await sync_all_stocks_to_manticore()
        print(" ✅ Manticore full sync complete.")
    except Exception as e:
        print(f" ⚠️ Manticore sync error: {e}")


# ══════════════════════════════════════════════════════════════
# 🚀 MASTER EXECUTION
# ══════════════════════════════════════════════════════════════
async def main():
    print("\n🚀 MEMULAI PROSES DATABASE SEEDING LENGKAP & TERVALIDASI 🚀\n")
    
    # 1. Admin Auth
    admin_token = await get_or_create_admin_token()

    # 2. Categories & Subcategories
    cat_map, sub_map = seed_categories_and_subs()

    # 3. Brands
    seed_brands()

    # 4. Products (Stocks)
    created_stocks = seed_products(sub_map, total=60)

    # 5. Service Booking
    seed_service_booking(admin_token, created_stocks)

    # 6. Banners
    seed_banners()

    # 7. About Us
    seed_about_us()

    # 8. Portfolio
    seed_portfolio()

    # 9. Technicians & Manticore
    await run_technicians_and_manticore()

    print("\n" + "="*50)
    print("🎉 SEMUA DATA DATABASE BERHASIL DI-SEED 100%!")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
