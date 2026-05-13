"""
seed_portfolio.py
=================
Seeder untuk mengisi data portfolio: projects, images, dan reviews.
Gambar diambil dari file lokal `cctv.jpg` (dipakai untuk semua role).

Jalankan:
    python seed_portfolio.py

Pastikan server FastAPI sudah berjalan di BASE_URL.
"""

import os
import sys
import json
import random
import asyncio
import mimetypes
from pathlib import Path

import httpx  # pip install httpx

# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

BASE_URL = "http://localhost:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(BASE_DIR, "brand")
IMAGE_PATH = os.path.join(BASE_DIR, "cctv.jpg")

TIMEOUT = httpx.Timeout(60.0)   # upload bisa lambat di local


# ══════════════════════════════════════════════════════════════════
# DATA SEED
# ══════════════════════════════════════════════════════════════════

PROJECTS = [
    # ── FEATURED (case study) ─────────────────────────────────────
    {
        "title": "Sistem CCTV Gudang Logistik PT Maju Bersama",
        "category": "Manufaktur",
        "location": "Bekasi, Jawa Barat",
        "cameras": 24,
        "package_slug": "enterprise",
        "client_type": "Pemilik Gudang & Logistik",
        "problem": (
            "Gudang seluas 5.000 m² hanya memiliki 4 kamera analog lama "
            "dengan resolusi sangat rendah. Rekaman sering tidak dapat diidentifikasi "
            "saat terjadi kehilangan barang, dan tidak ada monitoring real-time."
        ),
        "solution": (
            "Instalasi 24 kamera IP 4MP dengan kemampuan night vision, "
            "dilengkapi NVR 16 channel, storage 20 TB, dan integrasi dengan "
            "aplikasi mobile sehingga pemilik bisa memantau kapan saja dan di mana saja."
        ),
        "result": (
            "Kasus kehilangan barang turun 90% dalam 3 bulan pertama. "
            "Klaim asuransi yang sebelumnya sulit dibuktikan kini dapat diselesaikan "
            "dengan rekaman video beresolusi tinggi."
        ),
        "is_featured": True,
        "images": [
            {"role": "cover",   "alt": "Cover gudang logistik"},
            {"role": "before",  "alt": "Kondisi kamera lama sebelum upgrade"},
            {"role": "after",   "alt": "Instalasi kamera IP baru"},
            {"role": "gallery", "alt": "Ruang server NVR"},
            {"role": "gallery", "alt": "Tampilan monitoring mobile"},
        ],
    },

    # ── RESIDENSIAL ───────────────────────────────────────────────
    {
        "title": "Keamanan Rumah Mewah Cluster Greenville",
        "category": "Residensial",
        "location": "Tangerang Selatan, Banten",
        "cameras": 8,
        "package_slug": "premium",
        "client_type": None,
        "problem": None,
        "solution": None,
        "result": None,
        "is_featured": False,
        "images": [
            {"role": "cover",   "alt": "Eksterior rumah cluster Greenville"},
            {"role": "gallery", "alt": "Kamera pintu masuk utama"},
            {"role": "gallery", "alt": "Kamera area garasi"},
        ],
    },

    # ── KOMERSIAL ─────────────────────────────────────────────────
    {
        "title": "CCTV Mall Central Park Extension",
        "category": "Komersial",
        "location": "Jakarta Barat, DKI Jakarta",
        "cameras": 120,
        "package_slug": "enterprise",
        "client_type": None,
        "problem": None,
        "solution": None,
        "result": None,
        "is_featured": False,
        "images": [
            {"role": "cover",   "alt": "Lobby utama mall"},
            {"role": "gallery", "alt": "Area food court"},
            {"role": "gallery", "alt": "Parkir basement"},
            {"role": "gallery", "alt": "Entrance eskalator"},
        ],
    },

    # ── RETAIL ────────────────────────────────────────────────────
    {
        "title": "Pengamanan Minimarket Jaringan Waralaba",
        "category": "Retail",
        "location": "Depok, Jawa Barat",
        "cameras": 6,
        "package_slug": "basic",
        "client_type": None,
        "problem": None,
        "solution": None,
        "result": None,
        "is_featured": False,
        "images": [
            {"role": "cover",   "alt": "Tampak depan minimarket"},
            {"role": "gallery", "alt": "Area kasir"},
        ],
    },

    # ── KORPORAT ──────────────────────────────────────────────────
    {
        "title": "Gedung Perkantoran PT Sejahtera Abadi",
        "category": "Korporat",
        "location": "Sudirman, Jakarta Pusat",
        "cameras": 48,
        "package_slug": "enterprise",
        "client_type": None,
        "problem": None,
        "solution": None,
        "result": None,
        "is_featured": False,
        "images": [
            {"role": "cover",   "alt": "Lobi perkantoran"},
            {"role": "gallery", "alt": "Ruang server perusahaan"},
            {"role": "gallery", "alt": "Area parkir gedung"},
        ],
    },

    # ── FASILITAS UMUM ────────────────────────────────────────────
    {
        "title": "Sistem Pengawasan Puskesmas Kecamatan Cilandak",
        "category": "Fasilitas Umum",
        "location": "Cilandak, Jakarta Selatan",
        "cameras": 16,
        "package_slug": "standard",
        "client_type": None,
        "problem": None,
        "solution": None,
        "result": None,
        "is_featured": False,
        "images": [
            {"role": "cover",   "alt": "Ruang tunggu puskesmas"},
            {"role": "gallery", "alt": "Area apotek"},
        ],
    },

    # ── F&B ───────────────────────────────────────────────────────
    {
        "title": "CCTV Restoran Padang Sari Raso",
        "category": "F&B",
        "location": "Kebayoran Baru, Jakarta Selatan",
        "cameras": 10,
        "package_slug": "premium",
        "client_type": None,
        "problem": None,
        "solution": None,
        "result": None,
        "is_featured": False,
        "images": [
            {"role": "cover",   "alt": "Area makan utama restoran"},
            {"role": "gallery", "alt": "Dapur restoran"},
            {"role": "gallery", "alt": "Area kasir restoran"},
        ],
    },

    # ── LAINNYA ───────────────────────────────────────────────────
    {
        "title": "Keamanan Lapangan Futsal Sport Center",
        "category": "Lainnya",
        "location": "Bogor, Jawa Barat",
        "cameras": 12,
        "package_slug": "standard",
        "client_type": None,
        "problem": None,
        "solution": None,
        "result": None,
        "is_featured": False,
        "images": [
            {"role": "cover",   "alt": "Lapangan futsal dari atas"},
            {"role": "gallery", "alt": "Ruang ganti"},
            {"role": "gallery", "alt": "Area parkir sport center"},
        ],
    },
]


REVIEWS = [
    {
        "name": "Budi Santoso",
        "role": "Pemilik Gudang",
        "rating": 5,
        "text": (
            "Sangat puas dengan hasil pemasangan! Tim teknisi datang tepat waktu, "
            "rapi dalam pengkabelan, dan kamera hasilnya jernih sekali bahkan malam hari. "
            "Sudah 6 bulan berjalan tanpa masalah. Highly recommended!"
        ),
    },
    {
        "name": "Siti Rahayu",
        "role": "Manajer Operasional Mall",
        "rating": 5,
        "text": (
            "Kami pasang 120 kamera di seluruh area mall dan hasilnya memuaskan. "
            "Proses instalasi cepat, tidak mengganggu operasional mall, "
            "dan tim support sangat responsif jika ada kendala."
        ),
    },
    {
        "name": "Hendra Wijaya",
        "role": "Pemilik Rumah",
        "rating": 5,
        "text": (
            "Awalnya ragu karena harga yang ditawarkan lebih murah dari kompetitor, "
            "ternyata kualitasnya justru lebih baik. Kamera tahan hujan, gambar tajam, "
            "dan bisa dipantau lewat HP dengan mudah."
        ),
    },
    {
        "name": "Dewi Permatasari",
        "role": "Owner Restoran",
        "rating": 4,
        "text": (
            "Pemasangan berjalan lancar dan hasilnya bagus. Sedikit masukan: "
            "waktu tunggu estimasi awal agak lama, tapi setelah deal proses cepat. "
            "Overall puas dan akan merekomendasikan ke teman-teman."
        ),
    },
    {
        "name": "Agus Triyono",
        "role": "Kepala Keamanan Gedung",
        "rating": 5,
        "text": (
            "Sistem CCTV di gedung kami kini jauh lebih andal. "
            "Integrasi dengan access control berjalan mulus dan tim teknisi "
            "sangat profesional menjelaskan cara penggunaan sistem monitoring."
        ),
    },
    {
        "name": "Rina Marlina",
        "role": "Pemilik Minimarket",
        "rating": 5,
        "text": (
            "Harga terjangkau tapi kualitas tidak murahan. "
            "Sudah pasang di 3 cabang minimarket dan semua berjalan dengan baik. "
            "Kalau ada masalah teknis, tim langsung datang dalam 1-2 jam."
        ),
    },
    {
        "name": "Fauzan Hakim",
        "role": "Pengelola Sport Center",
        "rating": 4,
        "text": (
            "CCTV di lapangan futsal kami berfungsi sangat baik untuk mengawasi "
            "area dari potensi kerusakan fasilitas. Rekaman jelas dan storage 30 hari "
            "sudah lebih dari cukup untuk kebutuhan kami."
        ),
    },
    {
        "name": "dr. Amelia Kusuma",
        "role": "Kepala Puskesmas",
        "rating": 5,
        "text": (
            "Sebagai fasilitas kesehatan publik, keamanan sangat penting. "
            "Sistem CCTV yang dipasang membantu kami memantau area dan meningkatkan "
            "rasa aman bagi pasien maupun staf. Terima kasih!"
        ),
    },
]


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def log(msg: str, level: str = "INFO") -> None:
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌", "SEED": "🌱"}
    print(f"{icons.get(level, '  ')} {msg}")


def check_image_file() -> bool:
    if not os.path.isfile(IMAGE_PATH):
        log(f"File gambar tidak ditemukan: {IMAGE_PATH}", "ERR")
        log("Letakkan file 'cctv.jpg' di direktori yang sama dengan seeder ini.", "WARN")
        return False
    size_kb = os.path.getsize(IMAGE_PATH) / 1024
    log(f"Gambar ditemukan: {IMAGE_PATH} ({size_kb:.1f} KB)", "OK")
    return True


# ══════════════════════════════════════════════════════════════════
# SEEDER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

async def seed_project(client: httpx.AsyncClient, project_data: dict) -> dict | None:
    """POST /portfolio/projects → return project dict atau None jika gagal."""
    payload = {k: v for k, v in project_data.items() if k != "images"}
    # Hapus None agar tidak dikirim (server punya default)
    payload = {k: v for k, v in payload.items() if v is not None}

    resp = await client.post(f"{BASE_URL}/portfolio/projects", json=payload)
    if resp.status_code not in (200, 201):
        log(f"Gagal buat project '{project_data['title']}': {resp.status_code} {resp.text}", "ERR")
        return None

    project = resp.json()
    log(f"Project dibuat: [{project['id'][:8]}…] {project['title']}", "OK")
    return project


async def seed_images(
    client: httpx.AsyncClient,
    project_id: str,
    image_specs: list[dict],
) -> None:
    """Upload gambar per-role (karena role dikirim sebagai Form field)."""
    if not os.path.isfile(IMAGE_PATH):
        log("  Lewati upload gambar — file tidak ada.", "WARN")
        return

    # Kelompokkan spec per role agar bisa batch per role
    from collections import defaultdict
    by_role: dict[str, list[dict]] = defaultdict(list)
    for spec in image_specs:
        by_role[spec["role"]].append(spec)

    ct = mimetypes.guess_type(IMAGE_PATH)[0] or "image/jpeg"
    img_bytes = Path(IMAGE_PATH).read_bytes()

    for role, specs in by_role.items():
        files = []
        for spec in specs:
            files.append(
                ("files", (spec["alt"] + ".jpg", img_bytes, ct))
            )

        data = {"role": role}
        resp = await client.post(
            f"{BASE_URL}/portfolio/projects/{project_id}/images",
            files=files,
            data=data,
        )
        if resp.status_code not in (200, 201):
            log(
                f"  Gagal upload gambar role={role} untuk project {project_id[:8]}: "
                f"{resp.status_code} {resp.text}",
                "ERR",
            )
        else:
            uploaded = resp.json()
            log(f"  Upload {len(uploaded)} gambar role={role}", "OK")


async def seed_review(
    client: httpx.AsyncClient,
    review_data: dict,
    project_id: str | None = None,
) -> None:
    payload = {**review_data}
    if project_id:
        payload["project_id"] = project_id

    resp = await client.post(f"{BASE_URL}/portfolio/reviews", json=payload)
    if resp.status_code not in (200, 201):
        log(f"Gagal buat review '{review_data['name']}': {resp.status_code} {resp.text}", "ERR")
    else:
        rv = resp.json()
        log(f"Review dibuat: {rv['name']} (rating {rv['rating']}★)", "OK")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

async def main() -> None:
    log("=" * 60, "SEED")
    log("Portfolio Seeder dimulai", "SEED")
    log("=" * 60, "SEED")

    # Validasi file gambar
    image_ok = check_image_file()

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # ── 1. Cek koneksi server ──────────────────────────────────
        try:
            ping = await client.get(f"{BASE_URL}/docs")
            if ping.status_code != 200:
                log(f"Server tidak merespons dengan baik di {BASE_URL}", "WARN")
        except httpx.ConnectError:
            log(f"Tidak dapat terhubung ke server di {BASE_URL}", "ERR")
            log("Pastikan server FastAPI sudah berjalan.", "WARN")
            sys.exit(1)

        log(f"Server terhubung di {BASE_URL}", "OK")

        # ── 2. Seed Projects + Images ─────────────────────────────
        log("\n📦 Membuat projects...", "SEED")
        created_projects: list[dict] = []

        for project_data in PROJECTS:
            project = await seed_project(client, project_data)
            if project is None:
                continue

            # Upload gambar
            if image_ok and project_data.get("images"):
                await seed_images(client, project["id"], project_data["images"])

            created_projects.append(project)

        log(f"\nTotal project berhasil dibuat: {len(created_projects)}", "OK")

        # ── 3. Seed Reviews ───────────────────────────────────────
        log("\n💬 Membuat reviews...", "SEED")

        # Distribusikan review ke project yang ada
        # Review pertama → linked ke project pertama (featured), sisanya sebagian random
        for i, review_data in enumerate(REVIEWS):
            linked_project_id = None

            if i == 0 and created_projects:
                # Review pertama selalu ke featured project
                linked_project_id = created_projects[0]["id"]
            elif i < len(created_projects) and random.random() > 0.3:
                # Sebagian review di-link ke project secara acak
                linked_project_id = random.choice(created_projects)["id"]
            # else: review standalone (tidak di-link ke project manapun)

            await seed_review(client, review_data, linked_project_id)

        # ── 4. Summary ────────────────────────────────────────────
        log("\n" + "=" * 60, "SEED")
        log("Seeding selesai! 🎉", "SEED")
        log(f"  Projects : {len(created_projects)}", "INFO")
        log(f"  Reviews  : {len(REVIEWS)}", "INFO")
        log("=" * 60, "SEED")

        if created_projects:
            log("\nEndpoint untuk cek hasil:", "INFO")
            log(f"  GET {BASE_URL}/portfolio/page", "INFO")
            log(f"  GET {BASE_URL}/portfolio/projects", "INFO")
            log(f"  GET {BASE_URL}/portfolio/reviews", "INFO")


if __name__ == "__main__":
    asyncio.run(main())