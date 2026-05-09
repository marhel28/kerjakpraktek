import requests
import random

BASE_URL = "http://localhost:8000"

# 🔥 pool nama subcategory random
SUBCATEGORY_POOL = [
    "Premium", "Basic", "Advanced", "Pro", "Lite",
    "Accessories", "Original", "Bundle", "Limited",
    "Series A", "Series B", "Series C",
    "Classic", "Modern", "Eco", "Smart"
]

# ⚡ 1. Ambil semua category
res = requests.get(f"{BASE_URL}/category/")
categories = res.json()

print("TOTAL CATEGORY:", len(categories))

# ⚡ 2. Loop tiap category
for cat in categories:
    category_uuid = cat.get("uuid")
    category_name = cat.get("name")

    if not category_uuid:
        continue

    print(f"\n📦 Category: {category_name}")

    # ⚡ random jumlah subcategory (2–5)
    total_sub = random.randint(2, 5)

    # ⚡ ambil random nama
    names = random.sample(SUBCATEGORY_POOL, total_sub)

    for i, name in enumerate(names):
        slug = name.lower().replace(" ", "-")

        payload = {
            "category_uuid": category_uuid,
            "name": f"{category_name} {name}",
            "slug": f"{category_name.lower()}-{slug}",
            "position": i + 1
        }

        res = requests.post(
            f"{BASE_URL}/category/admin/subcategory",
            data=payload
        )

        print("  ➜", payload["name"], "|", res.status_code)