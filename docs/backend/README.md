# Panduan Backend (FastAPI)

Selamat datang di repositori arsitektur tulang punggung (*Backend*) PasarCCTV. Backend ini dirancang asinkron murni (non-blocking) untuk menangani ribuan transaksi *marketplace* simultan secara *realtime* dengan tumpukan teknologi (*tech stack*) kelas *enterprise*.

## Tech Stack Utama
* **Web Framework**: FastAPI (Python)
* **Database & ORM**: PostgreSQL, SQLAlchemy (Asynchronous via `asyncpg`)
* **Caching & Broker**: DragonflyDB (Redis API Compatible)
* **Mesin Pencari (Search Engine)**: Elasticsearch
* **Task Queue (Background Workers)**: Celery

## Menjalankan Proyek (Getting Started)

### Prasyarat Lingkungan
1. Python v3.12 atau lebih baru.
2. Mesin PostgreSQL berjalan (Lokal atau via *Docker Compose*).
3. DragonflyDB/Redis berjalan.
4. Instance Elasticsearch.

### Menyiapkan Environment Python
1. Buat dan masuk ke *Virtual Environment* lokal:
   ```bash
   python -m venv venv
   # Di Windows: venv\Scripts\activate
   # Di Linux/Mac: source venv/bin/activate
   ```
2. Instal semua dependensi pustaka Python:
   ```bash
   pip install -r requirements.txt
   ```
3. Sesuaikan *environment variables* lokal Anda di file `.env`.

### Migrasi Basis Data (Alembic)
Karena kita secara ketat memodelkan struktur *database* menggunakan SQLAlchemy ORM, setiap skema *database* harus bermigrasi dan sinkron sebelum menjalankan *server*:
```bash
alembic upgrade head
```

### Navigasi Lanjutan
* [Referensi API (Gambaran Umum Modul)](./api-reference.md)
* [📘 Spesifikasi API Detail (Swagger/Input Format)](./openapi-reference.md)
* [Sistem Elasticsearch & DragonflyDB](./elasticsearch-search.md)
* [Skema ERD Database](./database-schema.md)

### Menjalankan Server Utama
Sistem menggunakan peladen ASGI. Jalankan dengan perintah berikut:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Akses dokumentasi antarmuka API interaktif (Swagger/OpenAPI) bawaan FastAPI di `http://localhost:8000/docs`.
