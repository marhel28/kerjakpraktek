"""
seed_promo.py — Seeder Promo & Promo Checkout
Sistem: Padjajaran CCTV, Cimahi

Jalankan:
    python seed_promo.py

Seeder ini membuat:
  1. Promo Flash Sale Kamera (PERCENTAGE, target STOCK)
  2. Promo Paket Lebaran Bundle (BUNDLE_DISC, target SERVICE_PACKAGE)
  3. Promo BOGO Kabel Belden (BOGO, target STOCK)
  4. Promo Diskon Flat DVR (FIXED, target STOCK)
  5. Promo All-In Servis + Produk (PERCENTAGE, target ALL)
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone, timedelta

# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

BASE_URL     = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7InV1aWQiOiJkMGJhZDQ2Yi1lZjkxLTQ2NzItYmIzZS0xZTM1NDRlMTc0YzUiLCJlbWFpbCI6ImFtbWFybWF1bGFoZWxhMjBAZ21haWwuY29tIiwidXNlcm5hbWUiOiJxdWVlbiIsInJvbGUiOiJhZG1pbiJ9LCJleHAiOjE3NzgwNzc2NjMsImp0aSI6ImQ3OTY2M2UwLTQ5NjEtNDE0Ni1iZGVmLTMwMzhjOTM0ZTI0MSIsInJlZnJlc2giOmZhbHNlfQ.k5ZxN1KSbtPrENnhQxMCItXiN5oqM_gRk2ZFqawXhJk"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# Dari data produk yang ada (document index 10)
STOCK_KAMERA_TIANDY     = "10a2b5ce-cc9f-490d-a32e-4b538f4cf36e"  # Could finally - kamera 5MP
STOCK_KAMERA_HIKVISION  = "fe39bc24-edd2-4490-826b-fd2648376a0b"  # Bring court - kamera 8MP
STOCK_KABEL_BELDEN_10M  = "39e8a45c-c158-4e6f-bc0b-6ccbd432e49a"  # Participant hair all - kabel
STOCK_KABEL_BELDEN_5M   = "6d1b3294-e7da-429a-8f34-184c7095b851"  # At red - kabel 5m
STOCK_DVR_DAHUA         = "713f829c-7be6-4ae1-a542-21f4368642ef"  # Direction sea - DVR Dahua
STOCK_DVR_DAHUA_MINI    = "7340ffa1-37a4-4df9-acaf-4f1712d6d3c8"  # Head art - DVR
STOCK_HDD_SEAGATE       = "81becc1d-782a-4c4e-91bd-3d2cd18ab234"  # Customer resource - HDD
STOCK_PAKET_EZVIZ       = "f68f05cd-1092-4565-8fff-88b6ed7ebb8a"  # Need relationship marriage - paket Ezviz
STOCK_PAKET_EZVIZ_2     = "b3d89755-c0b5-487f-8da8-02ba06744654"  # Civil recent - paket Ezviz 30%off

# Dari data service package (document index 11)
PKG_RESIDENSIAL_4K      = "934bf542-138c-427f-ba3f-ed87fb37c31d"  # Paket Pintar Residensial
PKG_PREMIUM_BISNIS_8K   = "8b4273fe-3852-495c-9094-e699c680d317"  # Paket Premium Bisnis

# Waktu promo
NOW       = datetime.now(timezone.utc)
IN_1HR    = NOW + timedelta(hours=1)
IN_7DAYS  = NOW + timedelta(days=7)
IN_14DAYS = NOW + timedelta(days=14)
IN_30DAYS = NOW + timedelta(days=30)

def fmt_dt(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


# ══════════════════════════════════════════════════════════════════
# DATA PROMO
# ══════════════════════════════════════════════════════════════════

PROMOS = [

    # ─────────────────────────────────────────────────────────────
    # 1. FLASH SALE: Kamera CCTV Diskon 25%
    # ─────────────────────────────────────────────────────────────
    {
        "meta": {
            "name": "Flash Sale Kamera CCTV 25% OFF",
            "slug": "flash-sale-kamera-cctv-25-off",
            "description": "Dapatkan kamera CCTV premium dengan diskon 25%! Stok terbatas, hanya 50 transaksi pertama. Berlaku hari ini saja!",
            "banner_url": "https://images.unsplash.com/photo-1557597774-9d475d030a4f?w=1200&q=80",
            "promo_type": "flash_sale",
            "target": "stock",
            "discount_value": 25,
            "max_discount": 500000,
            "min_purchase": 500000,
            "min_qty": 1,
            "quota": 50,
            "max_use_per_user": 1,
            "valid_from": fmt_dt(NOW),
            "valid_until": fmt_dt(IN_7DAYS),
            "is_flash_sale": True,
            "flash_sale_quota": 50,
            "priority": 10,
            "items": [
                {
                    "stock_uuid": STOCK_KAMERA_TIANDY,
                    "override_discount_value": 25,
                },
                {
                    "stock_uuid": STOCK_KAMERA_HIKVISION,
                    "override_discount_value": 25,
                },
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────
    # 2. BUNDLE_DISC: Promo Paket Jasa Lebaran
    # ─────────────────────────────────────────────────────────────
    {
        "meta": {
            "name": "Promo Lebaran: Paket Jasa Pemasangan 20% OFF",
            "slug": "promo-lebaran-paket-jasa-20-off",
            "description": "Menyambut Lebaran, kami hadir dengan diskon 20% untuk paket jasa pemasangan CCTV rumah dan bisnis. Rumah aman, keluarga tenang!",
            "banner_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200&q=80",
            "promo_type": "bundle_disc",
            "target": "service_package",
            "discount_value": 20,
            "max_discount": 3000000,
            "min_purchase": 0,
            "min_qty": 1,
            "quota": 30,
            "max_use_per_user": 1,
            "valid_from": fmt_dt(NOW),
            "valid_until": fmt_dt(IN_14DAYS),
            "is_flash_sale": False,
            "flash_sale_quota": None,
            "priority": 8,
            "items": [
                {
                    "package_uuid": PKG_RESIDENSIAL_4K,
                    "override_discount_value": 20,
                },
                {
                    "package_uuid": PKG_PREMIUM_BISNIS_8K,
                    "override_discount_value": 15,   # bisnis override lebih kecil
                },
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────
    # 3. BOGO: Beli 2 Kabel Belden Gratis 1
    # ─────────────────────────────────────────────────────────────
    {
        "meta": {
            "name": "BOGO Kabel Belden: Beli 2 Gratis 1",
            "slug": "bogo-kabel-belden-beli-2-gratis-1",
            "description": "Beli 2 roll kabel Belden, langsung gratis 1! Cocok untuk instalasi rumah 4-8 kamera. Hemat biaya kabel sampai 33%.",
            "banner_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80",
            "promo_type": "bogo",
            "target": "stock",
            "discount_value": 0,        # tidak dipakai di BOGO (kalkulasi dari buy/get qty)
            "max_discount": None,
            "buy_quantity": 2,          # beli 2 ...
            "get_quantity": 1,          # ... gratis 1
            "min_purchase": 0,
            "min_qty": 2,
            "quota": 100,
            "max_use_per_user": 3,
            "valid_from": fmt_dt(NOW),
            "valid_until": fmt_dt(IN_30DAYS),
            "is_flash_sale": False,
            "flash_sale_quota": None,
            "priority": 5,
            "items": [
                {
                    "stock_uuid": STOCK_KABEL_BELDEN_10M,
                },
                {
                    "stock_uuid": STOCK_KABEL_BELDEN_5M,
                },
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────
    # 4. FIXED: Diskon Flat Rp 200.000 untuk DVR
    # ─────────────────────────────────────────────────────────────
    {
        "meta": {
            "name": "Diskon Rp 200.000 untuk DVR Dahua",
            "slug": "diskon-flat-dvr-dahua-200rb",
            "description": "Potongan langsung Rp 200.000 untuk pembelian DVR Dahua. Tidak perlu kode kupon, diskon otomatis diterapkan saat checkout.",
            "banner_url": "https://images.unsplash.com/photo-1622480916113-9000ac49b79d?w=1200&q=80",
            "promo_type": "fixed",
            "target": "stock",
            "discount_value": 200000,
            "max_discount": None,
            "min_purchase": 400000,
            "min_qty": 1,
            "quota": 200,
            "max_use_per_user": 2,
            "valid_from": fmt_dt(NOW),
            "valid_until": fmt_dt(IN_30DAYS),
            "is_flash_sale": False,
            "flash_sale_quota": None,
            "priority": 4,
            "items": [
                {
                    "stock_uuid": STOCK_DVR_DAHUA,
                    "override_discount_value": 200000,
                },
                {
                    "stock_uuid": STOCK_DVR_DAHUA_MINI,
                    "override_discount_value": 150000,  # override lebih kecil untuk yg lebih murah
                },
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────
    # 5. PERCENTAGE (ALL): Promo Grand Opening 10% untuk Semua
    # ─────────────────────────────────────────────────────────────
    {
        "meta": {
            "name": "Grand Opening: Semua Produk & Jasa 10% OFF",
            "slug": "grand-opening-semua-10-off",
            "description": "Rayakan grand opening toko online kami! Dapatkan diskon 10% untuk SEMUA produk CCTV dan paket jasa pemasangan. Berlaku untuk semua pelanggan baru maupun lama.",
            "banner_url": "https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=1200&q=80",
            "promo_type": "percentage",
            "target": "all",
            "discount_value": 10,
            "max_discount": 1500000,
            "min_purchase": 200000,
            "min_qty": 1,
            "quota": 500,
            "max_use_per_user": 2,
            "valid_from": fmt_dt(NOW),
            "valid_until": fmt_dt(IN_30DAYS),
            "is_flash_sale": False,
            "flash_sale_quota": None,
            "priority": 3,
            "items": [],   # target=ALL + tidak ada items = berlaku untuk semua
        },
    },

    # ─────────────────────────────────────────────────────────────
    # 6. FLASH SALE: Paket Residensial 4 Kamera (Limited 10)
    # ─────────────────────────────────────────────────────────────
    {
        "meta": {
            "name": "Flash Sale Paket Rumah 4 Kamera - Hemat 30%",
            "slug": "flash-sale-paket-rumah-4-kamera-30-off",
            "description": "HANYA 10 SLOT! Paket Pintar Residensial 4 titik dengan diskon 30%. Termasuk kamera smart IP 2MP, koneksi WiFi, dan pengerjaan 1 hari. Jangan sampai ketinggalan!",
            "banner_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200&q=80",
            "promo_type": "flash_sale",
            "target": "service_package",
            "discount_value": 30,
            "max_discount": 5000000,
            "min_purchase": 0,
            "min_qty": 1,
            "quota": 10,
            "max_use_per_user": 1,
            "valid_from": fmt_dt(NOW),
            "valid_until": fmt_dt(IN_7DAYS),
            "is_flash_sale": True,
            "flash_sale_quota": 10,
            "priority": 9,
            "extra_config": {
                "urgency_label": "Tersisa 10 slot",
                "badge": "🔥 LIMITED",
            },
            "items": [
                {
                    "package_uuid": PKG_RESIDENSIAL_4K,
                    "override_discount_value": 30,
                },
            ],
        },
    },

]


# ══════════════════════════════════════════════════════════════════
# SEEDER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

async def create_promo(client: httpx.AsyncClient, promo_data: dict) -> dict | None:
    meta   = promo_data["meta"]
    items  = meta.pop("items", [])

    # Buat promo dulu (tanpa items)
    payload = {**meta, "items": items}

    resp = await client.post(
        f"{BASE_URL}/admin/promos",
        json=payload,
        headers=HEADERS,
    )

    if resp.status_code not in (200, 201):
        print(f"  ❌ GAGAL buat promo '{meta['name']}': {resp.status_code} — {resp.text[:300]}")
        return None

    created = resp.json()
    promo_uuid = created.get("uuid")
    print(f"  ✅ Promo dibuat: [{promo_uuid}] {meta['name']}")
    return created


async def publish_promo(client: httpx.AsyncClient, promo_uuid: str, name: str) -> bool:
    resp = await client.post(
        f"{BASE_URL}/admin/promos/{promo_uuid}/publish",
        headers=HEADERS,
    )
    if resp.status_code not in (200, 201):
        print(f"  ⚠️  Gagal publish '{name}': {resp.status_code} — {resp.text[:200]}")
        return False
    print(f"  🚀 Published: {name}")
    return True


async def run_seeder():
    print("\n" + "═" * 60)
    print("  SEEDER: Promo & Diskon Padjajaran CCTV")
    print("═" * 60)
    print(f"  Base URL   : {BASE_URL}")
    print(f"  Total Promo: {len(PROMOS)}")
    print("═" * 60 + "\n")

    results = {
        "success": [],
        "failed": [],
        "published": [],
    }

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Cek koneksi dulu
        try:
            ping = await client.get(f"{BASE_URL}/services/config", headers=HEADERS)
            print(f"  🔗 Koneksi: OK (status {ping.status_code})\n")
        except Exception as e:
            print(f"  ❌ Koneksi GAGAL: {e}")
            print("  Pastikan server sudah berjalan di", BASE_URL)
            return

        for i, promo_data in enumerate(PROMOS, 1):
            name = promo_data["meta"]["name"]
            print(f"[{i}/{len(PROMOS)}] Membuat: {name}")

            # Deep copy agar tidak merusak original
            import copy
            data_copy = copy.deepcopy(promo_data)

            created = await create_promo(client, data_copy)
            if not created:
                results["failed"].append(name)
                print()
                continue

            results["success"].append(name)
            promo_uuid = created["uuid"]

            # Publish semua promo
            published = await publish_promo(client, promo_uuid, name)
            if published:
                results["published"].append(name)

            print()

    # Summary
    print("═" * 60)
    print("  HASIL SEEDER")
    print("═" * 60)
    print(f"  ✅ Berhasil dibuat  : {len(results['success'])}/{len(PROMOS)}")
    print(f"  🚀 Berhasil publish : {len(results['published'])}/{len(PROMOS)}")
    print(f"  ❌ Gagal            : {len(results['failed'])}")
    if results["failed"]:
        print("\n  Promo yang gagal:")
        for name in results["failed"]:
            print(f"    - {name}")
    print("═" * 60 + "\n")


# ══════════════════════════════════════════════════════════════════
# EXTRA: Seeder via DB langsung (tanpa API) — untuk development
# ══════════════════════════════════════════════════════════════════

async def seed_via_db():
    """
    Alternatif seeder langsung ke database.
    Gunakan ini jika API belum siap atau untuk development.

    Jalankan: python seed_promo.py --db
    """
    try:
        from sqlmodel import SQLModel
        from sqlmodel.ext.asyncio.session import AsyncSession
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as AlchemySession
        from sqlalchemy.orm import sessionmaker
        import os

        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5433/padjajaran_cctv"
        )

        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, class_=AlchemySession, expire_on_commit=False)

        from .model import Promo, PromoItem, PromoStatus
        import copy, secrets, string

        print("\n  🗄️  Mode: Langsung ke Database")

        async with async_session() as session:
            for promo_data in PROMOS:
                meta  = copy.deepcopy(promo_data["meta"])
                items = meta.pop("items", [])

                # Convert datetime strings kembali ke datetime objects
                valid_from  = datetime.fromisoformat(meta["valid_from"].replace("Z", "+00:00"))
                valid_until = datetime.fromisoformat(meta["valid_until"].replace("Z", "+00:00"))

                promo = Promo(
                    name=meta["name"],
                    slug=meta["slug"],
                    description=meta.get("description"),
                    banner_url=meta.get("banner_url"),
                    promo_type=meta["promo_type"],
                    target=meta["target"],
                    discount_value=meta["discount_value"],
                    max_discount=meta.get("max_discount"),
                    buy_quantity=meta.get("buy_quantity"),
                    get_quantity=meta.get("get_quantity"),
                    min_purchase=meta.get("min_purchase", 0),
                    min_qty=meta.get("min_qty", 1),
                    quota=meta.get("quota"),
                    max_use_per_user=meta.get("max_use_per_user"),
                    valid_from=valid_from,
                    valid_until=valid_until,
                    is_flash_sale=meta.get("is_flash_sale", False),
                    flash_sale_quota=meta.get("flash_sale_quota"),
                    extra_config=meta.get("extra_config", {}),
                    priority=meta.get("priority", 0),
                    status=PromoStatus.ACTIVE,
                )
                session.add(promo)
                await session.flush()

                for item in items:
                    pi = PromoItem(
                        promo_uuid=promo.uuid,
                        stock_uuid=item.get("stock_uuid"),
                        package_uuid=item.get("package_uuid"),
                        override_discount_value=item.get("override_discount_value"),
                    )
                    session.add(pi)

                print(f"  ✅ [{promo.uuid}] {promo.name}")

            await session.commit()
            print(f"\n  ✅ {len(PROMOS)} promo berhasil diseed ke database")

        await engine.dispose()

    except ImportError as e:
        print(f"  ❌ Import error (pastikan PYTHONPATH benar): {e}")
    except Exception as e:
        print(f"  ❌ DB error: {e}")
        raise


# ══════════════════════════════════════════════════════════════════
# ENTRYPOINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if "--db" in sys.argv:
        asyncio.run(seed_via_db())
    else:
        asyncio.run(run_seeder())