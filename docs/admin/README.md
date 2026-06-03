# Panduan Dashboard Admin (Vue & Vite)

Selamat datang di repositori tertutup panel kontrol *Admin* PasarCCTV. Aplikasi *Single Page Application* (SPA) ini adalah antarmuka manajemen pusat yang digunakan secara eksklusif oleh staf internal, pengawas lapangan, dan *owner* usaha untuk meracik produk dan mengendalikan mesin *Marketplace*.

## Pilihan Teknologi (Tech Stack)
Aplikasi *Admin* ini sengaja dikembangkan terpisah (*Separation of Concerns*) dari kerangka web publik pembelanja (*Frontend Nuxt*), memastikan peretas yang menemukan titik cacat dari halaman publik tidak dapat menembus basis logika dasbor internal secara serentak.
* **Pembangunan Aplikasi (Bundler)**: Vite (Super-Fast HMR)
* **Kerangka Kerja UI Dasar**: Vue 3 (Composition API)
* **Jalur Arus Navigasi**: Vue Router
* **Otorisasi Terpusat**: Integrasi Supabase Auth dengan protokol Pemeriksaan JWT (*JSON Web Token*) berbasis peran mutlak (*Role-Based Access Control*).

## Memulai Sesi Lokal (Getting Started)

### Instruksi Prasyarat Instalasi
Sama halnya dengan *Frontend* aplikasi publik pembeli, siapkan kerangka dasar Node:
1. Pastikan mesin terminal masuk melalui subdirektori pengerjaan `admin/project/`.
2. Unduh seluruh kumpulan kode (*packages*):
   ```bash
   npm install
   ```

### Alur Pengembangan (Dev Environment)
Sangat sederhana, jalankan skrip lokal Vite:
```bash
npm run dev
```
Peladen Vite ini secara konstan menyajikan (*serve*) file statis super kilat ke *browser*.

### Topologi Modul Proyek
* `src/views/`: Representasi tampilan muka layar penuh (seperti Dasbor, Tabel Pesanan, dan Lembar Penambahan Katalog).
* `src/components/`: Kumpulan pecahan piringan UI tak berwujud (Tabel Data reaktif, atau Kotak Form Input standar).
* `src/services/`: Sekumpulan selubung interkoneksi (*Axios API Wrapper*) spesifik yang menembak jalur konektor khusus Administrator di `FastAPI`.

## Panduan & Standar Koding
* [Panduan Pengelolaan Popup, Modal & Toast](file:///c:/Users/Administrator/Desktop/kp/kerjapraktek/docs/admin/popup-management.md): Standar animasi transisi modal kustom, reactive toast, dan resolusi alert bawaan peramban.

