import requests

BASE_URL = "http://localhost:8000"

categories = [
    {"name": "CCTV Camera", "slug": "camera-cctv", "icon_name": "i-heroicons-video-camera", "position": 1},
    {"name": "DVR & NVR", "slug": "dvr-nvr", "icon_name": "i-heroicons-cpu-chip", "position": 2},
    {"name": "Security Alarm", "slug": "security-alarm", "icon_name": "i-heroicons-bell-alert", "position": 3},
    {"name": "Access Control", "slug": "access-control", "icon_name": "i-heroicons-lock-closed", "position": 4},
    {"name": "Networking", "slug": "networking", "icon_name": "i-heroicons-wifi", "position": 5},
    {"name": "Cables & Accessories", "slug": "asesoris", "icon_name": "i-heroicons-link", "position": 6},
    {"name": "Smart Home", "slug": "smart-home", "icon_name": "i-heroicons-home-modern", "position": 7},
]

created_categories = {}

for cat in categories:
    res = requests.post(
        f"{BASE_URL}/category/admin/category",
        data=cat  # karena form-urlencoded
    )

    print("CATEGORY:", cat["name"], res.status_code)

    if res.status_code == 200:
        data = res.json()
        created_categories[cat["slug"]] = data.get("uuid")  # sesuaikan response kamu