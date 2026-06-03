# Referensi API Terpusat (API Reference)

Sistem *Backend* PasarCCTV dibangun menggunakan kerangka kerja **FastAPI** yang secara otomatis menggenerasi spesifikasi antarmuka *OpenAPI/Swagger* secara langsung (*Live*). Anda dapat selalu menguji *endpoint* secara visual melalui peramban di rute `http://localhost:8000/docs` ketika peladen lokal Anda menyala.

Berikut adalah peta tata ruang (*Routing Map*) seluruh modul titik akhir (*endpoints*) yang diekspos oleh layanan *backend* ini:

## 1. Domain Pengguna & Autentikasi (Auth & User)
*Prefix Induk:* `/auth/user`, `/cart`, `/wishlist`
* **Tujuan**: Menangani sesi masuk, registrasi, sinkronisasi token dengan keranjang, dan manajemen akun.
* **Cakupan Kunci**: Penggabungan autentikasi JWT pihak ketiga (seperti integrasi OTP/Supabase) dan interaksi data *session-based* (*Cart* & *Wishlist*).

## 2. Domain Katalog & Manajemen Stok (Catalog & Stock)
*Prefix Induk:* `/stok`, `/category`, `/brands`, `/addon`
* **Tujuan**: Menyajikan daftar etalase produk ke *Frontend* pengunjung dan memfasilitasi Dasbor Admin mengubah harga/stok.
* **Cakupan Kunci**: Modul `/stok` secara transparan telah terhubung ke *Elasticsearch* di bawah tenda (*under the hood*) untuk kueri pencarian teks canggih dan *DragonflyDB Cache* untuk *Response Time* <50ms.

## 3. Domain Transaksi Fisik (Transactions & Shipping)
*Prefix Induk:* `/transaksi`, `/cek/shipping`, `/recap`
* **Tujuan**: Menangani siklus hidup pesanan pembelian keranjang barang fisik.
* **Cakupan Kunci**: Alur *Checkout* yang ketat dengan perlindungan ganda (reservasi kuantitas *Database*) serta kalkulasi berat/volume ongkos kirim. Modul `/recap` tertutup secara eksklusif untuk Admin.

## 4. Domain Jasa & Pemesanan Teknisi (Service Bookings)
*Prefix Induk:* `/jasa`, `/booking`
* **Tujuan**: Modul otonom yang dikhususkan untuk produk yang bukan barang, melainkan *waktu* (seperti Jasa Instalasi, Perawatan, Pemasangan).
* **Cakupan Kunci**: Mengandung logika rumit untuk menghindari insiden pemesanan ganda di tanggal yang sama (*Time-Collision Handling*) oleh admin.

## 5. Domain Promosi & Konten Visual Publik (CMS & Promos)
*Prefix Induk:* `/promos`, `/banner`, `/image-sections`, `/about`
* **Tujuan**: Pemasaran (*Marketing*) dan manipulasi tampilan konten CMS dari Dasbor Admin tanpa menyentuh *database* secara manual.
* **Cakupan Kunci**: Rute `/promos/validate` sangat krusial dan memiliki gerbang pembatasan limit kuota (*Rate Limiter* & *Usage Quota*) agar satu pengguna/perangkat tidak bisa menyedot (*abuse*) sisa kuota diskon secara brutal.

## 6. Domain Konfigurasi & Opsi Admin (System Settings)
*Prefix Induk:* `/settings`, `/admin/coupon`, `/activity`
* **Tujuan**: Manajemen operasional tingkat tinggi (Pembuatan Voucher, Konfigurasi Pajak Global, Pencatatan Log Aktivitas Staf).

> [!NOTE]  
> **CORS Security Constraint**: Harap diingat bahwa struktur API ini diawasi oleh tembok *CORS Middleware* ketat yang disetel di dalam berkas `__init__.py`. Jika Anda mencoba memanggil API ini dari *domain* luar yang tidak dikenal (selain `localhost:3000` atau *domain* Vercel kita), semua permintaan (*requests*) akan ditolak di level proksi.
