"""
seed_about.py
=============
Seeder untuk mengisi data halaman About Us / Tentang Kami.

Yang di-seed:
  1. AboutPage  (hero + CTA)
  2. AboutStat  (nested dalam create)
  3. AboutValue (nested dalam create)
  4. AboutGallery – upload gambar ke CDN via endpoint multipart

Gambar diambil dari file lokal `cctv.jpg` (satu file dipakai semua slot gallery).

Jalankan:
    python seed_about.py

Pastikan server FastAPI sudah berjalan di BASE_URL.
"""

import os
import sys
import asyncio
import mimetypes
from pathlib import Path

import httpx  # pip install httpx


# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

BASE_URL   = "http://localhost:8000"   # sesuaikan prefix proyekmu
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cctv.jpg")
TIMEOUT    = httpx.Timeout(60.0)              # upload bisa lambat di lokal


# ══════════════════════════════════════════════════════════════════
# DATA SEED
# ══════════════════════════════════════════════════════════════════

ABOUT_PAGE = {
    # ── Hero ──────────────────────────────────────────────────────
    "hero_badge_text": "Partner Keamanan Anda",
    "hero_heading": (
        "Jangan Pertaruhkan Aset Anda Pada Instalasi Amatir."
    ),
    "hero_subheading": (
        "Kami bukan sekadar tukang tarik kabel. Padjajaran CCTV mendesain, "
        "memasang, dan memastikan sistem keamanan Anda beroperasi prima untuk "
        "investasi ketenangan bertahun-tahun."
    ),

    # ── CTA ───────────────────────────────────────────────────────
    "cta_heading": "Garansi Ganti Baru Tanpa Debat",
    "cta_body": (
        "Kamera mati tiba-tiba? NVR rusak? Kami berikan jaminan ganti unit baru "
        "(bukan servis) di tahun pertama. Kami yang repot urus ke pabrik, "
        "Anda tetap tenang memantau."
    ),
    "cta_primary_text":   "Jadwalkan Survey Gratis",
    "cta_secondary_text": "Lihat Harga Paket",
    "cta_secondary_url":  "/services/booking",

    # ── Stats (angka kepercayaan) ─────────────────────────────────
    "stats": [
        {"value": "1,200+", "label": "Kamera Aktif",       "order": 0},
        {"value": "500+",   "label": "Klien Terlindungi",  "order": 1},
        {"value": "100%",   "label": "Kabel Dalam Pipa",   "order": 2},
        {"value": "1 Thn",  "label": "Garansi Ganti Baru", "order": 3},
    ],

    # ── Values (kartu keunggulan) ─────────────────────────────────
    "values": [
        {
            "icon":  "lucide:shield-alert",
            "title": "Zero Blind-Spot Design",
            "desc": (
                "Kami tidak asal pasang. Tim kami mensimulasikan sudut pandang kamera "
                "untuk memastikan tidak ada celah bagi penyusup yang luput dari pantauan."
            ),
            "order": 0,
        },
        {
            "icon":  "lucide:zap",
            "title": "Kelistrikan Anti-Sabotase",
            "desc": (
                "Instalasi kabel menggunakan jalur tertutup (conduit) yang mustahil "
                "dipotong sembarangan, lengkap dengan sentralisasi power supply yang aman."
            ),
            "order": 1,
        },
        {
            "icon":  "lucide:badge-check",
            "title": "Hanya Barang Original",
            "desc": (
                "Kami menjamin 100% keaslian perangkat (Hikvision, Dahua, dll). "
                "Firmware bisa di-update resmi, anti-hack, dan bergaransi pabrik."
            ),
            "order": 2,
        },
        {
            "icon":  "lucide:smartphone",
            "title": "Pantau Dari Genggaman",
            "desc": (
                "Kami pastikan sistem terhubung ke HP Anda sebelum teknisi pulang. "
                "Pantau aset berharga Anda dari mana saja, kapan saja."
            ),
            "order": 3,
        },
    ],
}


# Gallery alt texts – satu gambar lokal dipakai semua slot
GALLERY_ITEMS = [
    {"alt": "Setup NVR Server Ruang Kontrol",  "order": 0},
    {"alt": "Penarikan Kabel Estetik",         "order": 1},
    {"alt": "Quality Control Tampilan",        "order": 2},
    {"alt": "Pemasangan Area Outdoor",         "order": 3},
    {"alt": "Instalasi Fasilitas Kesehatan",   "order": 4},
]


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def log(msg: str, level: str = "INFO") -> None:
    icons = {
        "INFO": "ℹ️ ",
        "OK":   "✅",
        "WARN": "⚠️ ",
        "ERR":  "❌",
        "SEED": "🌱",
    }
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

async def check_existing_page(client: httpx.AsyncClient) -> dict | None:
    """Cek apakah sudah ada halaman aktif di DB."""
    resp = await client.get(f"{BASE_URL}/about")
    if resp.status_code == 200:
        return resp.json()
    return None


async def seed_about_page(client: httpx.AsyncClient) -> dict | None:
    """
    POST /about
    Buat halaman About baru (+ stats & values sekaligus via nested JSON).
    Kalau sudah ada, tanya user apakah mau di-overwrite.
    """
    existing = await check_existing_page(client)
    if existing:
        log("Halaman About Us sudah ada (is_active=True).", "WARN")
        answer = input("   Buat ulang (overwrite)? [y/N] ").strip().lower()
        if answer != "y":
            log("Lewati pembuatan halaman. Data lama dipertahankan.", "INFO")
            return existing
        log("Membuat halaman baru (halaman lama akan dinonaktifkan)...", "INFO")

    resp = await client.post(f"{BASE_URL}/about", json=ABOUT_PAGE)

    if resp.status_code not in (200, 201):
        log(f"Gagal membuat halaman About: {resp.status_code}", "ERR")
        log(resp.text, "ERR")
        return None

    page = resp.json()
    log(f"Halaman About dibuat: id={page['id'][:8]}…", "OK")
    log(f"  Stats  : {len(page.get('stats', []))} item", "INFO")
    log(f"  Values : {len(page.get('values', []))} item", "INFO")
    return page


async def seed_gallery(
    client: httpx.AsyncClient,
    image_ok: bool,
) -> None:
    """
    POST /about/gallery  (multipart: file + alt)
    Upload setiap gambar gallery satu per satu karena endpoint menerima 1 file + 1 alt.
    """
    if not image_ok:
        log("Lewati upload gallery — file gambar tidak ada.", "WARN")
        return

    img_bytes = Path(IMAGE_PATH).read_bytes()
    ct = mimetypes.guess_type(IMAGE_PATH)[0] or "image/jpeg"

    log(f"\n📸 Mengupload {len(GALLERY_ITEMS)} gambar gallery...", "SEED")

    for item in GALLERY_ITEMS:
        resp = await client.post(
            f"{BASE_URL}/about/gallery",
            files={"file": ("cctv.jpg", img_bytes, ct)},
            data={"alt": item["alt"]},
        )
        if resp.status_code not in (200, 201):
            log(
                f"  Gagal upload '{item['alt']}': {resp.status_code} {resp.text}",
                "ERR",
            )
        else:
            result = resp.json()
            log(f"  Uploaded [{result['id'][:8]}…] '{item['alt']}'", "OK")


async def seed_reorder_gallery(client: httpx.AsyncClient) -> None:
    """
    PATCH /about/gallery/reorder
    Setelah upload, pastikan urutan sesuai GALLERY_ITEMS.
    Perlu ambil dulu id dari GET /about.
    """
    resp = await client.get(f"{BASE_URL}/about")
    if resp.status_code != 200:
        log("Tidak bisa ambil data gallery untuk reorder.", "WARN")
        return

    gallery = resp.json().get("gallery", [])
    if not gallery:
        log("Gallery kosong, lewati reorder.", "WARN")
        return

    # Urutkan berdasarkan alt (cocokkan dengan GALLERY_ITEMS)
    alt_order = {item["alt"]: item["order"] for item in GALLERY_ITEMS}
    items = []
    for g in gallery:
        order = alt_order.get(g["alt"], 99)
        items.append({"id": g["id"], "order": order})

    resp = await client.patch(
        f"{BASE_URL}/about/gallery/reorder",
        json={"items": items},
    )
    if resp.status_code == 200:
        log(f"Gallery reorder berhasil ({len(items)} item).", "OK")
    else:
        log(f"Gagal reorder gallery: {resp.status_code} {resp.text}", "WARN")


async def print_summary(client: httpx.AsyncClient) -> None:
    """Tampilkan ringkasan data yang sudah terseed."""
    resp = await client.get(f"{BASE_URL}/about")
    if resp.status_code != 200:
        log("Tidak dapat mengambil data untuk summary.", "WARN")
        return

    page = resp.json()
    log("\n" + "─" * 60, "INFO")
    log("SUMMARY DATA TERSEED:", "SEED")
    log(f"  Page ID      : {page['id']}", "INFO")
    log(f"  Hero Badge   : {page['hero_badge_text']}", "INFO")
    log(f"  Hero Heading : {page['hero_heading'][:60]}…", "INFO")
    log(f"  CTA Heading  : {page['cta_heading']}", "INFO")
    log(f"  Stats        : {len(page.get('stats', []))} item", "INFO")
    log(f"  Values       : {len(page.get('values', []))} item", "INFO")
    log(f"  Gallery      : {len(page.get('gallery', []))} gambar", "INFO")
    log("─" * 60, "INFO")
    log(f"\n  GET  {BASE_URL}/about", "INFO")
    log(f"  POST {BASE_URL}/about/gallery", "INFO")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

async def main() -> None:
    log("=" * 60, "SEED")
    log("About Us Seeder dimulai", "SEED")
    log("=" * 60, "SEED")

    image_ok = check_image_file()

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:

        # ── 0. Cek koneksi server ──────────────────────────────────
        try:
            ping = await client.get(f"{BASE_URL.rsplit('/api', 1)[0]}/docs")
            if ping.status_code != 200:
                log(f"Server merespons tapi bukan 200 di /docs: {ping.status_code}", "WARN")
        except httpx.ConnectError:
            log(f"Tidak dapat terhubung ke server di {BASE_URL}", "ERR")
            log("Pastikan server FastAPI sudah berjalan.", "WARN")
            sys.exit(1)

        log(f"Server terhubung → {BASE_URL}", "OK")

        # ── 1. Seed halaman + stats + values ──────────────────────
        log("\n📄 Membuat halaman About Us...", "SEED")
        page = await seed_about_page(client)
        if page is None:
            log("Seeding dibatalkan karena halaman gagal dibuat.", "ERR")
            sys.exit(1)

        # ── 2. Upload gallery images ───────────────────────────────
        await seed_gallery(client, image_ok)

        # ── 3. Reorder gallery ────────────────────────────────────
        if image_ok:
            log("\n🔃 Menyusun urutan gallery...", "SEED")
            await seed_reorder_gallery(client)

        # ── 4. Summary ────────────────────────────────────────────
        await print_summary(client)

        log("\n🎉 Seeding About Us selesai!", "SEED")
        log("=" * 60, "SEED")


if __name__ == "__main__":
    asyncio.run(main())