import json
import random
import io
import requests
from faker import Faker
import time
import argparse
import os
import sys

fake = Faker()

# ==========================================
# 📁 PATH CONFIG (AUTO DETECT)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(BASE_DIR, "brand")
IMAGE_PATH = os.path.join(BASE_DIR, "cctv.jpg")

BASE_URL = "http://localhost:8000"
URL = f"{BASE_URL}/stok/admin/create"

# ==========================================
# 🔁 RETRY HELPER
# ==========================================
def post_with_retry(url, data, files, retries=3):
    for attempt in range(retries):
        try:
            res = requests.post(url, data=data, files=files, timeout=10)
            if res.status_code in (200, 201):
                return res
        except Exception as e:
            print(f"⚠️ Retry {attempt+1}: {e}")
            time.sleep(1)
    return None

# ==========================================
# 🧠 SPECS
# ==========================================
def generate_specs(category_slug):
    specs_map = {
        "kamera-cctv": lambda: {
            "resolution": random.choice(["2MP", "5MP", "8MP", "4K"]),
            "night_vision": random.choice(["yes", "no"]),
            "lens": random.choice(["2.8mm", "3.6mm", "6mm"])
        },
        "dvr-nvr": lambda: {
            "channels": random.choice([4, 8, 16]),
            "storage_support": random.choice(["1TB", "2TB", "4TB"])
        },
        "networking": lambda: {
            "speed": random.choice(["100Mbps", "1Gbps"]),
            "type": random.choice(["router", "switch"])
        }
    }
    return specs_map.get(category_slug, lambda: {
        "garansi": f"{random.randint(1,3)} tahun",
        "material": random.choice(["plastic", "metal"])
    })()

# ==========================================
# 💰 PRICE
# ==========================================
def generate_price():
    is_discounted = random.random() < 0.3
    base_price = random.randint(10, 500) * 10000

    if is_discounted:
        discount = random.choice([10, 15, 20, 30, 40])
        return base_price, discount, 0, f"🔥 Diskon {discount}%"
    else:
        return base_price, 0, base_price, "Normal"

# ==========================================
# 🚀 SEED STOK
# ==========================================
def seed_stok(image_bytes, total=100):
    print("\n" + "="*40)
    print(f"🚀 SEEDING {total} PRODUK (STANDALONE)")
    print("="*40)

    categories = [
        "kamera-cctv",
        "dvr-nvr",
        "networking",
        "storage",
        "paket-cctv"
    ]

    subcategories = {
        "kamera-cctv": ["kamera-cctv-premium", "kamera-cctv-basic"],
        "dvr-nvr": ["dvr-nvr-pro", "dvr-nvr-lite"],
        "networking": ["networking-router", "networking-switch"],
        "storage": ["storage-hdd", "storage-ssd"],
        "paket-cctv": ["paket-cctv-hemat", "paket-cctv-lengkap"]
    }

    TYPE_MAPPING = {
        "kamera-cctv": "camera cctv",
        "dvr-nvr": "recording system",
        "networking": "jaringan"
    }

    BRAND_MAPPING = {
        "kamera-cctv": ["hkvision", "Dahua", "Ezviz","tiandy","tapo"],
        "dvr-nvr": ["Hikvision", "Dahua"],
        "networking": ["TP-Link", "Mikrotik"]
    }

    success = 0
    failed = 0

    for i in range(total):
        main_cat = random.choice(categories)
        sub_cat = random.choice(subcategories.get(main_cat, [""]))

        original_price, discount, online_price, badge = generate_price()

        data = {
            "title": fake.sentence(nb_words=3).replace(".", ""),
            "brand": random.choice(BRAND_MAPPING.get(main_cat, ["Generic"])),
            "category_slug": main_cat,
            "subcategory_slug": sub_cat,
            "type": TYPE_MAPPING.get(main_cat, "lain-lain"),
            "original_price": original_price,
            "discount_percentage": discount,
            "online_price": online_price,
            "stok": random.randint(1, 100),
            "specs": json.dumps(generate_specs(main_cat))
        }

        files = [
            ("images", (f"img_{j}.jpg", io.BytesIO(image_bytes), "image/jpeg"))
            for j in range(random.randint(1, 3))
        ]

        res = post_with_retry(URL, data, files)

        if res:
            success += 1
            print(f"[{i+1}] ✅ {main_cat} | {badge}")
        else:
            failed += 1
            print(f"[{i+1}] ❌ FAILED")

    print("\n📊 HASIL:")
    print(f"✅ Success: {success}")
    print(f"❌ Failed : {failed}")

# ==========================================
# 🎯 RUNNER
# ==========================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--total", type=int, default=100, help="Jumlah produk")

    args = parser.parse_args()

    # 🔥 VALIDASI IMAGE PATH
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Gambar tidak ditemukan: {IMAGE_PATH}")
        sys.exit(1)

    print(f"📁 BASE_DIR   : {BASE_DIR}")
    print(f"🖼️ IMAGE_PATH : {IMAGE_PATH}")

    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    seed_stok(image_bytes, total=args.total)

if __name__ == "__main__":
    main()