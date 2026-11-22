# Panduan Frontend (Nuxt 4)

Selamat datang di direktori dokumentasi *Frontend*. Aplikasi ini merupakan wajah utama dari PasarCCTV yang melayani pelanggan ritel maupun klien proyek B2B secara masif.

## Tech Stack Utama
* **Kerangka Kerja (Framework)**: Nuxt 4 (Vue 3, Composition API)
* **Styling & Komponen**: Tailwind CSS v4, Nuxt UI
* **State Management**: Pinia
* **Animasi & Interaksi**: GSAP, VueUse Motion
* **Integrasi Lanjutan**: WebSocket FastAPI native (chat & notifikasi), Leaflet (untuk Pemetaan Lokasi)

## Menjalankan Proyek (Getting Started)

### Prasyarat Instalasi
* Node.js v20 atau lebih baru.
* Pengelola paket (NPM, Yarn, atau Bun).

### Langkah-langkah Memulai
1. Arahkan terminal Anda ke dalam direktori `frontend`.
2. Instal semua dependensi ekosistem:
   ```bash
   npm install
   ```
3. Salin konfigurasi *environment variables*:
   ```bash
   cp .env.example .env
   ```
   *(Pastikan URL Backend API telah disetel dengan benar).*
4. Nyalakan peladen (*development server*):
   ```bash
   npm run dev
   ```

Aplikasi web sekarang dapat diakses secara lokal di `http://localhost:3000`. Pastikan server *backend* dan *database* PostgreSQL Anda juga berjalan agar semua katalog produk dan API pemesanan dapat dimuat.
