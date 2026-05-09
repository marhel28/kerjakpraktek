import os
import sys
import json
import random
import io
import requests
from faker import Faker

# ==========================================
# ⚙️ KONFIGURASI GLOBAL
# ==========================================
BASE_URL = "http://localhost:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(BASE_DIR, "brand")
IMAGE_PATH = os.path.join(BASE_DIR, "cctv.jpg")

fake = Faker()

# ==========================================
# 1️⃣ SEED CATEGORIES
# ==========================================
def seed_categories():
    print("\n" + "="*40)
    print("🚀 STEP 1: SEEDING CATEGORIES")
    print("="*40)
    
    categories = [
        {"name": "CCTV Camera", "slug": "kamera-cctv", "icon_name": "i-heroicons-video-camera", "position": 1},
        {"name": "DVR & NVR", "slug": "dvr-nvr", "icon_name": "i-heroicons-cpu-chip", "position": 2},
        {"name": "Security Alarm", "slug": "security-alarm", "icon_name": "i-heroicons-bell-alert", "position": 3},
        {"name": "Access Control", "slug": "access-control", "icon_name": "i-heroicons-lock-closed", "position": 4},
        {"name": "Networking", "slug": "networking", "icon_name": "i-heroicons-wifi", "position": 5},
        {"name": "Cables & Accessories", "slug": "cables-accessories", "icon_name": "i-heroicons-link", "position": 6},
        {"name": "Smart Home", "slug": "smart-home", "icon_name": "i-heroicons-home-modern", "position": 7},
        {"name": "Storage", "slug": "storage", "icon_name": "i-heroicons-server", "position": 8},
        {"name": "Paket CCTV", "slug": "paket-cctv", "icon_name": "i-heroicons-gift", "position": 9},
    ]

    created_categories = {}

    for cat in categories:
        try:
            res = requests.post(f"{BASE_URL}/category/admin/category", data=cat)
            if res.status_code == 200:
                data = res.json()
                created_categories[cat["slug"]] = {
                    "uuid": data.get("uuid") or data.get("data", {}).get("uuid"), 
                    "name": cat["name"]
                }
                print(f" ✅ SUCCESS : {cat['name']}")
            else:
                print(f" ⚠️ FAILED  : {cat['name']} ({res.status_code})")
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR FATAL: Gagal konek ke server. Pastikan FastAPI jalan di port 8000.")
            sys.exit(1)

    return created_categories

# ==========================================
# 2️⃣ SEED SUBCATEGORIES
# ==========================================
def seed_subcategories(created_categories):
    print("\n" + "="*40)
    print("🚀 STEP 2: SEEDING SUBCATEGORIES")
    print("="*40)

    subcategory_mapping = {}

    if not created_categories:
        print("⚠️ Tidak ada category yang berhasil dibuat. Skip subcategory.")
        return subcategory_mapping

    SUBCATEGORY_POOL = [
        "Premium", "Basic", "Advanced", "Pro", "Lite",
        "Accessories", "Original", "Bundle", "Limited",
        "Series A", "Series B", "Series C",
        "Classic", "Modern", "Eco", "Smart"
    ]

    for main_slug, cat_data in created_categories.items():
        category_uuid = cat_data["uuid"]
        category_name = cat_data["name"]
        
        subcategory_mapping[main_slug] = [] 

        print(f"\n📦 Category: {category_name}")
        total_sub = random.randint(2, 5)
        names = random.sample(SUBCATEGORY_POOL, total_sub)

        for i, name in enumerate(names):
            sub_slug = name.lower().replace(" ", "-")
            full_sub_slug = f"{main_slug}-{sub_slug}"
            
            payload = {
                "category_uuid": category_uuid, 
                "name": f"{category_name} {name}",
                "slug": full_sub_slug,
                "position": i + 1
            }

            res = requests.post(f"{BASE_URL}/category/admin/subcategory", data=payload)
            if res.status_code == 200:
                print(f"  ➜ ✅ {payload['name']}")
                subcategory_mapping[main_slug].append(full_sub_slug)
            else:
                print(f"  ➜ ⚠️ {payload['name']} ({res.status_code})")

    return subcategory_mapping

# ==========================================
# 3️⃣ SEED BRANDS
# ==========================================
def seed_brands():
    print("\n" + "="*40)
    print("🚀 STEP 3: SEEDING BRANDS")
    print("="*40)

    if not os.path.exists(BRAND_DIR):
        print(f"⚠️ Skip Brands: Folder '{BRAND_DIR}' tidak ditemukan.")
        return

    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    images = [f for f in os.listdir(BRAND_DIR) if f.lower().endswith(valid_extensions)]

    if not images:
        print(f"⚠️ Skip Brands: Tidak ada file gambar di '{BRAND_DIR}'")
        return

    print(f"Mempersiapkan {len(images)} brands...")
    URL = f"{BASE_URL}/brands/admin/create"

    for index, filename in enumerate(images):
        filepath = os.path.join(BRAND_DIR, filename)
        raw_name = os.path.splitext(filename)[0]
        
        name = raw_name.replace("-", " ").replace("_", " ").title()
        slug = raw_name.lower().replace(" ", "-").replace("_", "-")
        
        data = {
            "name": name,
            "slug": slug,
            "title": name,
            "route": f"/brands/{slug}",
            "position": random.randint(1, 100),
            "is_featured": random.choice(["true"])
        }

        with open(filepath, "rb") as f:
            files = {"file": (filename, f, "image/jpeg")}
            res = requests.post(URL, data=data, files=files)
            
            if res.status_code == 200:
                print(f"[{index+1}/{len(images)}] ✅ {name}")
            else:
                print(f"[{index+1}/{len(images)}] ⚠️ GAGAL {name} ({res.status_code})")

# ==========================================
# 4️⃣ SEED PRODUCTS (STOK) + FITUR DISKON
# ==========================================
def generate_specs(category_slug):
    if category_slug == "kamera-cctv":
        return {"resolution": random.choice(["2MP", "5MP", "8MP", "4K"]), "night_vision": random.choice(["yes", "no"]), "lens": random.choice(["2.8mm", "3.6mm", "6mm"])}
    elif category_slug == "dvr-nvr":
        return {"channels": random.choice([4, 8, 16]), "storage_support": random.choice(["1TB", "2TB", "4TB"])}
    elif category_slug == "networking":
        return {"speed": random.choice(["100Mbps", "1Gbps"]), "type": random.choice(["router", "switch"])}
    elif category_slug == "cables-accessories":
        return {"length": random.choice(["5m", "10m", "20m"]), "type": random.choice(["coaxial", "UTP", "power cable"])}
    elif category_slug == "storage":
        return {"capacity": random.choice(["500GB", "1TB", "2TB", "4TB"]), "type": random.choice(["HDD", "SSD"])}
    elif category_slug == "paket-cctv":
        return {"camera_count": random.choice([2, 4, 8]), "include_dvr": random.choice(["yes", "no"])}
    else:
        return {"garansi": f"{random.randint(1,3)} tahun", "type": random.choice(["connector", "adapter", "bracket"]), "material": random.choice(["plastic", "metal"])}

def seed_products(created_categories, subcategory_mapping, total=100):
    print("\n" + "="*40)
    print(f"🚀 STEP 4: SEEDING {total} PRODUCTS (WITH DISCOUNTS)")
    print("="*40)

    if not os.path.exists(IMAGE_PATH):
        print(f"❌ File tidak ditemukan: {IMAGE_PATH}. Batal seeding produk.")
        return

    available_slugs = list(created_categories.keys())
    if not available_slugs:
        print("⚠️ Tidak ada kategori valid. Batal seeding produk.")
        return

    TYPE_MAPPING = {
        "kamera-cctv": "camera cctv", "dvr-nvr": "recording system", "security-alarm": "alarm system",
        "access-control": "access control", "networking": "jaringan", "cables-accessories": "kabel",
        "smart-home": "smart device", "storage": "penyimpanan", "paket-cctv": "paket bundling"
    }

    BRAND_MAPPING = {
        "kamera-cctv": ["Hkvision", "Dahua", "Ezviz", "Imou","tiandy","tapo"], "dvr-nvr": ["Hkvision", "Dahua"],
        "security-alarm": ["Bosch", "Honeywell"], "access-control": ["ZKTeco", "Hkvision"],
        "networking": ["TP-Link", "Mikrotik", "Tenda"], "cables-accessories": ["Belden", "AMP"],
        "smart-home": ["Xiaomi", "Tuya", "Sonoff"], "storage": ["Seagate", "WD", "Toshiba"],
        "paket-cctv": ["Hkvision", "Dahua", "Ezviz"]
    }

    with open(IMAGE_PATH, "rb") as f:
        cached_image_bytes = f.read()

    URL = f"{BASE_URL}/stok/admin/create"

    for i in range(total):
        title = fake.sentence(nb_words=3).replace(".", "")
        
        main_category_slug = random.choice(available_slugs)
        available_subs = subcategory_mapping.get(main_category_slug, [])
        sub_category_slug = random.choice(available_subs) if available_subs else ""

        brand = random.choice(BRAND_MAPPING.get(main_category_slug, [fake.company()]))
        item_type = TYPE_MAPPING.get(main_category_slug, "lain-lain")
        
        # 🔥 LOGIKA DISKON (30% Peluang Produk Sedang Diskon)
        is_discounted = random.choice([True, False, False])
        
        if is_discounted:
            # Harga Asli (Harga Coret) lebih tinggi
            original_price = random.randint(20, 500) * 10000 # Contoh: 200rb - 5jt
            discount_percentage = random.choice([10, 15, 20, 30, 40, 50])
            online_price = 0 # Biarkan Backend yang menghitung hasil diskonnya
            badge_text = f"Diskon {discount_percentage}%"
        else:
            original_price = random.randint(10, 300) * 10000
            discount_percentage = 0
            online_price = original_price # Harga normal
            badge_text = "Harga Normal"

        data = {
            "title": title,
            "brand": brand,
            "category_slug": main_category_slug,
            "subcategory_slug": sub_category_slug,
            "type": item_type,
            "original_price": original_price,         # 🔥 Kirim Original Price
            "discount_percentage": discount_percentage, # 🔥 Kirim Diskon Percentage
            "online_price": online_price,             # 🔥 Kirim Online Price
            "stok": random.randint(1, 100),
            "specs": json.dumps(generate_specs(main_category_slug))
        }

        num_images = random.randint(1, 4)
        files = [("images", (f"cctv_{j}.jpg", io.BytesIO(cached_image_bytes), "image/jpeg")) for j in range(num_images)]

        res = requests.post(URL, data=data, files=files)
        
        if res.status_code in (200, 201):
            print(f"[{i+1}/{total}] ✅ {data['subcategory_slug'][:15]}... | {badge_text}")
        else:
            print(f"[{i+1}/{total}] ⚠️ FAILED ({res.status_code}) - {res.text}")

# ==========================================
# 🚦 MAIN RUNNER
# ==========================================
if __name__ == "__main__":
    print("🌟 MEMULAI FULL DATABASE SEEDING 🌟")
    
    db_categories = seed_categories()
    db_subcategory_map = seed_subcategories(db_categories)
    seed_brands()
    seed_products(db_categories, db_subcategory_map, total=100)
    
    print("\n🎉🎉 FULL SEEDING SELESAI 🎉🎉")