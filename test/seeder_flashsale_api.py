import httpx
import asyncio
from datetime import datetime, timezone, timedelta

BASE_URL = "http://localhost:8000"

async def seed_flash_sale_api():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("⚡ Seeding Flash Sale via HTTP API...")
        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(hours=8)

        # 1. Ambil stok aktif
        res_stocks = await client.get(f"{BASE_URL}/stok/public/list", params={"limit": 8})
        stocks = []
        if res_stocks.status_code == 200:
            data = res_stocks.json()
            stocks = data.get("items", []) or data.get("data", {}).get("items", [])

        # 2. Setup promo flash sale
        promo_payload = {
            "name": "Flash Sale Kamera Keamanan Bandung 30% OFF",
            "slug": f"flash-sale-live-{int(now.timestamp())}",
            "description": "Potongan langsung 30% kamera CCTV & paket instalasi resmi. Berlaku hari ini.",
            "banner_url": "https://daganghalal.blob.core.windows.net/44641/Product/cctv-installation-services-1745476968100.jpg",
            "promo_type": "flash_sale",
            "target": "stock",
            "discount_value": 30,
            "max_discount": 500000,
            "min_purchase": 200000,
            "min_qty": 1,
            "quota": 50,
            "max_use_per_user": 2,
            "valid_from": (now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
            "valid_until": valid_until.isoformat().replace("+00:00", "Z"),
            "is_flash_sale": True,
            "flash_sale_quota": 50,
            "priority": 100
        }

        res_promo = await client.post(f"{BASE_URL}/admin/promos", json=promo_payload)
        print(f"Promo create status: {res_promo.status_code}")
        if res_promo.status_code in (200, 201):
            promo_res = res_promo.json()
            promo_uuid = promo_res.get("uuid") or promo_res.get("data", {}).get("uuid")
            print(f"Created promo: {promo_uuid}")

            # Publish promo
            await client.post(f"{BASE_URL}/admin/promos/{promo_uuid}/publish")

            # Bind items
            for s in stocks[:6]:
                s_uuid = s.get("uuid")
                if s_uuid:
                    await client.post(
                        f"{BASE_URL}/admin/promos/{promo_uuid}/items",
                        json={"stock_uuid": s_uuid, "override_discount_value": 30}
                    )
            print("Items bound to flash sale.")
        else:
            print(f"Error promo: {res_promo.text}")

if __name__ == "__main__":
    asyncio.run(seed_flash_sale_api())