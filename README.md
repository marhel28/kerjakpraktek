# PasarCCTV — Marketplace & Jasa Instalasi CCTV

Platform marketplace CCTV B2B lengkap dengan sistem **jasa instalasi berkala**, checkout pembayaran, chat real-time customer ↔ admin, dan chatbot AI berbasis RAG. Satu repositori berisi tiga aplikasi: API backend, web publik, dan dashboard admin.

---

## Fitur Utama

| Modul | Deskripsi |
|---|---|
| 🛒 **Katalog & Pencarian** | Produk per kategori/brand, full-text search via Manticore, filter facet, perbandingan produk |
| 💳 **Checkout & Pembayaran** | Keranjang, voucher/kupon, payment gateway Midtrans, riwayat & status pesanan |
| 🚚 **Ongkir & Pengiriman** | Cek ongkir per wilayah, tracking pengiriman dengan timeline |
| 🔧 **Jasa & Booking** | Paket instalasi CCTV, pemeliharaan berkala, troubleshooting — booking dengan teknisi & jadwal |
| 💬 **Chat Real-time** | Chat customer ↔ admin via WebSocket (FastAPI + composable singleton), read receipt, unread badge |
| 🤖 **Chatbot AI (RAG)** | Asisten "PasarBot" dengan knowledge base produk, rekomendasi produk di jawaban, eskalasi ke CS manusia |
| 🎯 **Promo & Flash Sale** | Banner per route, promo eksklusif, flash sale, brand showcase |
| 📊 **Dashboard Admin** | Manajemen produk, stok, transaksi, banner, promo, jasa, kupon, pengaturan sistem, log aktivitas |
| 🔐 **Autentikasi** | Email/password (JWT + refresh token, blacklist Redis) dan Google OAuth, bridge ke Supabase |

## Tech Stack

| Layer | Teknologi |
|---|---|
| **Backend** | Python 3.13, FastAPI, SQLModel (async SQLAlchemy), Pydantic v2 |
| **Database** | PostgreSQL 15 |
| **Cache & Queue** | DragonflyDB (Redis-compatible), Celery worker |
| **Search Engine** | Manticore Search (pengganti Elasticsearch, hemat RAM) |
| **Realtime** | Native WebSocket (FastAPI) — chat & notifikasi, fan-out via Redis pub/sub |
| **AI** | Groq API (LLM inference), knowledge base produk untuk RAG |
| **Storage** | Cloudflare R2 (gambar produk & attachment chat) |
| **Frontend** | Nuxt 4, Vue 3, TypeScript, Tailwind CSS v4, Pinia, Leaflet (store locator) |
| **Admin** | Vue 3 + Vite, Tailwind CSS, D3 (visualisasi) |
| **Infrastruktur** | Docker Compose, Cloudflare Tunnel, Alembic (migrasi) |

## Struktur Proyek

```
kerjakpraktek/
├── backend/          # API FastAPI — router, service, model per modul
│   ├── auth/         # Login, JWT, Google OAuth, Supabase bridge
│   ├── data/         # Produk, transaksi, banner, promo, ongkir, jasa
│   ├── user/         # Cart, wishlist, pesan (chat WS), booking
│   ├── admin/        # Endpoint dashboard admin
│   └── db/           # Engine, Redis, CDN (R2), Manticore client
├── frontend/         # Web publik (Nuxt 4) — pages, components, stores, server proxy
├── admin/project/    # Dashboard admin (Vue 3 + Vite)
├── migration/        # Alembic migrations
├── docs/             # Dokumentasi teknis (C4, ERD, aktivitas, per lapisan)
├── test/             # Seeder & script pengujian endpoint
├── scratch/          # Script utilitas dev (migrasi kolom, dll)
└── docker-compose.yml
```

Dokumentasi mendalam ada di [`docs/README.md`](docs/README.md) — termasuk diagram C4, ERD, dan diagram aktivitas checkout/promo/notifikasi.

## Menjalankan Proyek

### Prasyarat
- Docker + Docker Compose
- Python 3.13 + Node.js 20+ (untuk mode non-Docker)
- File `backend/.env` (jangan pernah di-commit)

### 1. Mode Docker (disarankan)

```bash
docker compose up -d --build
```

Layanan yang berjalan:

| Layanan | Port | Keterangan |
|---|---|---|
| FastAPI backend | `8000` | Swagger di `/docs` |
| PostgreSQL | `5433` → `5432` | DB utama |
| DragonflyDB | `6379` | Cache, blacklist token, broker Celery |
| Manticore Search | `9306` / `9308` | Search engine |
| Celery worker | — | Queue `default,email,auth` |
| Cloudflared | — | Tunnel publik (opsional) |

### 2. Mode Manual (development)

```bash
# Backend
python -m venv venv
venv\Scripts\activate            # Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn backend:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev                      # http://localhost:3000

# Admin
cd admin/project
npm install
npm run dev                      # http://localhost:5173
```

### Variabel Environment (`backend/.env`)

Kunci yang dibutuhkan (nilai disimpan lokal, tidak di-commit):

```
DATABASE_URL=postgresql+asyncpg://user_admin:<password>@localhost:5433/marketplace_db
JWT_SECRET_KEY=<secret>
REDIS_HOST=localhost
REDIS_PORT=6379
MANTICORE_URL=http://localhost:9308
GROQ_API_KEY=<groq key untuk chatbot>
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
```

## API Ringkas

Base URL: `http://localhost:8000` — dokumentasi interaktif: `http://localhost:8000/docs`

| Prefix | Modul |
|---|---|
| `/auth/user` | Login, register, refresh, Google OAuth, reset password |
| `/stok` | Produk & stok |
| `/transaksi` | Checkout, pembayaran, status pesanan |
| `/cek/shipping` | Ongkir & tracking |
| `/cart`, `/wishlist` | Keranjang & wishlist |
| `/messages` | Chat customer ↔ admin (HTTP fallback) |
| `/ws/chat/{user_id}` | WebSocket chat real-time (`?token=<JWT>`) |
| `/category`, `/brands`, `/banner` | Katalog & konten publik |
| `/settings`, `/admin/coupon`, `/recap` | Endpoint admin |

## Kontribusi & Standar Kode

- Commit mengikuti [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`, dst.)
- Backend: semua service async, session DB via dependency injection, tidak menyimpan state global
- Frontend: Pinia store per domain, proxy API lewat `frontend/server/api/` agar token tidak expose di browser
- Secret hanya lewat `.env` — tidak pernah hardcode di source

---

*Proyek Kerja Praktek — PasarCCTV. Untuk arsitektur lengkap dan diagram, lihat folder [`docs/`](docs/README.md).*
