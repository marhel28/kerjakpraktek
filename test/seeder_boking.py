import requests
import json

# ==========================================
# 1. KONFIGURASI & AUTENTIKASI
# ==========================================
BASE_URL = "http://localhost:8000"

ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7InV1aWQiOiJkMGJhZDQ2Yi1lZjkxLTQ2NzItYmIzZS0xZTM1NDRlMTc0YzUiLCJlbWFpbCI6ImFtbWFybWF1bGFoZWxhMjBAZ21haWwuY29tIiwidXNlcm5hbWUiOiJxdWVlbiIsInJvbGUiOiJhZG1pbiJ9LCJleHAiOjE3NzgwNzM4MDksImp0aSI6IjgzNTMzM2I3LTEyZGMtNDBhMS1iMzVhLTRhYmNmZDg0ZGJmNiIsInJlZnJlc2giOmZhbHNlfQ.hPDENwhyZZfq3gVfKviljfRMewDevpjWuxTVCy2Ims0"

HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

# ==========================================
# 2. SEEDER: PRICING CONFIGURATION
# ==========================================
def seed_pricing_config():
    print("\n⏳ [1/2] Menyimpan Konfigurasi Harga Dasar (Pricing Config)...")
    url = f"{BASE_URL}/admin/service/pricing"

    payload = {
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
            "tiandy": 1.4
        },
        "consultation_fee": 0,
        "transport_per_km": 4000,
        "transport_min_fee": 25000,
        "transport_max_fee": 350000,
        "max_distance_km": 60.0,
        "dp_percentage": 30,
        "addons_config": [
            {
                "key": "night_vision",
                "label": "ColorVu / Full Color Mlm Hari",
                "type": "per_cam",
                "price": 175000,
                "description": "Kamera tetap berwarna meski kondisi gelap total",
                "icon": "lucide:moon"
            },
            {
                "key": "audio_mic",
                "label": "Built-in Microphone",
                "type": "per_cam",
                "price": 125000,
                "description": "Merekam suara dan percakapan di sekitar kamera",
                "icon": "lucide:mic"
            },
            {
                "key": "conduit_pipe",
                "label": "Pipa Pelindung Kabel (Conduit)",
                "type": "flat",
                "price": 350000,
                "description": "Kabel aman dari gigitan tikus dan lebih estetik",
                "icon": "lucide:shield-check"
            }
        ]
    }

    try:
        res = requests.post(url, headers=HEADERS, json=payload)
        if res.status_code in [200, 201]:
            print(f"   ✅ BERHASIL! UUID Config: {res.json().get('uuid')}")
        else:
            print(f"   ❌ GAGAL: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"   ❌ Error API Pricing: {e}")


# ==========================================
# 3. SEEDER: SERVICE PACKAGES
# ==========================================
def seed_packages():
    print("\n⏳ [2/2] Membuat Paket Jasa + Bundle Barang (Service Packages)...")

    STOCK_KAMERA_HKV   = "fe39bc24-edd2-4490-826b-fd2648376a0b"
    STOCK_KAMERA_IMOU  = "086f26c7-4c41-4acc-ba05-928f4b984e33"
    STOCK_DVR_DAHUA    = "713f829c-7be6-4ae1-a542-21f4368642ef"
    STOCK_HDD_SEAGATE  = "81becc1d-782a-4c4e-91bd-3d2cd18ab234"
    STOCK_KABEL_BELDEN = "39e8a45c-c158-4e6f-bc0b-6ccbd432e49a"

    packages = [
        {
            "name": "Paket Pintar Residensial 4 Titik (Imou)",
            "slug": "paket-pintar-residensial-4-titik",
            "description": "Solusi keamanan cerdas untuk rumah. Dilengkapi koneksi WiFi dan pantauan langsung dari HP Anda 24 Jam.",
            "category": "installation",
            "camera_count": 4,
            "default_brand": "ezviz",
            "thumbnail_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80",
            "highlights": [
                "4x Smart IP Camera 2MP",
                "Fitur Deteksi Manusia",
                "Gratis Setting Aplikasi HP",
                "Pengerjaan 1 Hari Selesai"
            ],
            "is_active": True,
            "sort_order": 1,
            "items": [
                {"stock_uuid": STOCK_KAMERA_IMOU, "quantity": 4, "label": "Imou Smart Camera 2MP", "sort_order": 1},
                {"stock_uuid": STOCK_KABEL_BELDEN, "quantity": 4, "label": "Kabel Belden 10m", "sort_order": 2}
            ]
        },
        {
            "name": "Paket Premium Bisnis 8 Titik (Hikvision)",
            "slug": "paket-premium-bisnis-8-titik",
            "description": "Keamanan kelas atas untuk toko, minimarket, atau kantor. Tahan cuaca ekstrim dan gambar tajam 8 Megapixel.",
            "category": "installation",
            "camera_count": 8,
            "default_brand": "hikvision",
            "thumbnail_url": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=600&q=80",
            "highlights": [
                "8x Kamera Hikvision Ultra HD 8MP",
                "1x DVR 4/8 Channel Dahua",
                "Storage Besar Seagate 4TB",
                "Kabel Premium Anti Putus"
            ],
            "is_active": True,
            "sort_order": 2,
            "items": [
                {"stock_uuid": STOCK_KAMERA_HKV,   "quantity": 8,  "label": "Kamera Hikvision 8MP Ultra HD",   "sort_order": 1},
                {"stock_uuid": STOCK_DVR_DAHUA,     "quantity": 1,  "label": "DVR 4/8 CH System",              "sort_order": 2},
                {"stock_uuid": STOCK_HDD_SEAGATE,   "quantity": 1,  "label": "HDD Seagate Surveillance 4TB",   "sort_order": 3},
                {"stock_uuid": STOCK_KABEL_BELDEN,  "quantity": 10, "label": "Kabel Belden (per 10m)",         "sort_order": 4}
            ]
        }
    ]

    for pkg in packages:
        slug = pkg["slug"]

        # ── Idempotency check: skip jika slug sudah ada ──────────
        try:
            check = requests.get(
                f"{BASE_URL}/services/packages/slug/{slug}",
                headers=HEADERS,
                timeout=10,
            )
            if check.status_code == 200:
                print(f"   ⏭️  SKIP: Paket '{slug}' sudah ada di database.")
                continue
        except Exception as e:
            print(f"   ⚠️  Tidak bisa cek slug '{slug}': {e}. Lanjut coba insert...")

        # ── Insert ────────────────────────────────────────────────
        print(f"   📦 Mengirim paket: {pkg['name']} ...")
        try:
            res = requests.post(
                f"{BASE_URL}/admin/service/packages",
                headers=HEADERS,
                json=pkg,
                timeout=15,
            )
            if res.status_code in [200, 201]:
                data = res.json()
                print(f"      ✅ OK! UUID: {data.get('uuid')}")
                print(f"      💰 Total Estimasi (Alat + Jasa): Rp {data.get('total_estimated'):,}")
            elif res.status_code == 409:
                print(f"      ⏭️  SKIP (409): {res.json().get('detail', 'Slug sudah ada.')}")
            else:
                print(f"      ❌ GAGAL: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"      ❌ Error API Packages: {e}")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("🚀 MEMULAI SEEDING PADJAJARAN SERVICE BOOKING\n" + "=" * 60)

    seed_pricing_config()
    seed_packages()

    print("\n" + "=" * 60 + "\n🏁 PROSES SEEDING SELESAI.")