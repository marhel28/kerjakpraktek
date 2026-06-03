# PasarCCTV — Design System v2
> Tema: **Forest Green Premium** · Filosofi: *Industrial Trust meets Modern Marketplace*

---

## 1. Filosofi & Prinsip Desain

PasarCCTV v2 mengusung tema **Forest Green Premium** — jauh dari kesan "marketplace hijau cerah" yang generik. Palet baru berbasis hijau tua yang dalam (`#03AC0E`, `#0D1B12`) memberi kesan **otoritatif, terpercaya, dan profesional** — sesuai dengan industri keamanan yang dijual.

**Tiga prinsip utama:**

1. **Authority First** — Desain harus terasa seperti distributor resmi, bukan reseller biasa.
2. **Lugas & Efisien** — Tidak ada dekorasi yang tidak berfungsi. Setiap elemen punya peran.
3. **Mobile-Native** — Didesain dari layar 375px ke atas, bukan sebaliknya.

---

## 2. Color Tokens

### Brand Palette

| Token | Hex | Penggunaan |
|---|---|---|
| `--color-brand-night` | `#0D1B12` | Navbar, dark shell, store locator panel |
| `--color-brand-green` | `#03AC0E` | CTA utama, harga, link aktif, border hover |
| `--color-brand-mint` | `#03AC0E` | Aksen pada dark background, ikon aktif |
| `--color-brand-surface` | `#E6F7E9` | Background ikon USP, tag garansi |
| `--color-brand-surface-border` | `#C8E6CC` | Border pada surface hijau |

### Semantic Palette

| Token | Hex | Penggunaan |
|---|---|---|
| `--color-danger` | `#B91C1C` | Badge diskon, flash sale, retur |
| `--color-promo` | `#B45309` | Tag promo, promo amber |
| `--color-info` | `#185FA5` | Produk baru (kategori tertentu) |

### Neutral Palette

| Token | Tailwind Equiv. | Penggunaan |
|---|---|---|
| `--color-bg-page` | `bg-gray-50` | Background halaman |
| `--color-bg-card` | `bg-white` | Card produk, panel utama |
| `--color-text-primary` | `text-gray-900` | Judul, harga |
| `--color-text-secondary` | `text-gray-500` | Deskripsi, spesifikasi |
| `--color-text-muted` | `text-gray-400` | Label form, placeholder |

### Dark Shell Palette (Navbar & Store Locator)

| Token | Hex | Penggunaan |
|---|---|---|
| `--dark-bg` | `#0D1B12` | Container utama |
| `--dark-surface` | `#1A2E1E` | Input, button secondary |
| `--dark-border` | `#2A4A30` | Border elemen dark |
| `--dark-text` | `#C8E6CC` | Teks utama on dark |
| `--dark-muted` | `#4A6E52` | Teks sekunder on dark |

---

## 3. Typography

**Font:** Plus Jakarta Sans / Inter (via `@nuxt/fonts`)

### Scale

| Peran | Size | Weight | Keterangan |
|---|---|---|---|
| Harga (detail page) | `32px` | 500 | Color `--color-brand-green` |
| Judul produk (detail) | `26px` | 500 | `line-height: 1.3` |
| Section heading | `18px` | 500 | |
| Body / deskripsi | `14px` | 400 | `line-height: 1.6` |
| Label kecil / kategori | `12px` | 500 | `letter-spacing: 0.1em`, uppercase |
| Harga kartu produk | `17px` | 500 | Color `--color-brand-green` |
| Judul kartu produk | `13px` | 500 | `line-height: 1.4` |
| Spesifikasi kartu | `11px` | 400 | Color text-muted |

### Aturan Typography

- **Tidak ada `font-black` (900)** — terlalu agresif, pakai 500 untuk bold.
- Harga menonjol lewat **ukuran dan warna**, bukan ketebalan ekstrem.
- Gunakan `font-weight: 500` sebagai satu-satunya "bold" di seluruh UI.
- Teks uppercase hanya untuk label kategori dan section divider.

---

## 4. Spacing & Layout

### Container

| Konteks | Max Width |
|---|---|
| Halaman produk, search | `1200px` |
| Homepage (grid-heavy) | `1400px` |
| Checkout, booking form | `800px` |

### Spacing Scale

| Token | Value | Penggunaan |
|---|---|---|
| `--space-xs` | `4px` | Gap antar badge |
| `--space-sm` | `8px` | Gap dalam card body |
| `--space-md` | `12px` | Gap antar card |
| `--space-lg` | `16px` | Padding card body |
| `--space-xl` | `24px` | Section internal padding |
| `--space-2xl` | `40px` | Antar section (desktop) |
| `--space-section-mobile` | `24px` | Antar section (mobile) |

### Border Radius

| Token | Value | Digunakan pada |
|---|---|---|
| `--radius-sm` | `6px` | Badge, tag kecil |
| `--radius-md` | `8px` | Button, input, icon container |
| `--radius-lg` | `12px` | Navbar, panel, USP bar |
| `--radius-xl` | `14px` | Product card |
| `--radius-pill` | `100px` | Tag pill, store locator CTA |

### Shadow Tokens

| Token | Value | Digunakan pada |
|---|---|---|
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.08)` | Card default, input focus |
| `--shadow-card-hover` | `0 20px 40px -15px rgba(15,122,60,0.12)` | Product card saat hover |
| `--shadow-navbar` | `0 2px 12px rgba(0,0,0,0.08)` | Sticky navbar saat scroll |

> Navbar light menggunakan shadow saat di-scroll. Tidak ada dark shell lagi di navbar.

---

## 5. Component Library

### 5.1 Navbar (AppNavbar.vue)

Navbar PasarCCTV menggunakan struktur 3 baris yang dioptimalkan untuk desktop dan mode kompak untuk mobile:

**1. Top Bar (Dark/Black)**
- Background: `#000000` (atau `#171717` pada halaman Compare). Tersembunyi saat di-scroll ke bawah.
- Height: `34px`.
- Kiri: Teks "Pengiriman Seluruh Indonesia!" dengan ikon truk.
- Kanan: Link utilitas operasional (`Masuk | Daftar`, `Lokasi Toko`, `Lacak Pesanan`, `Bantuan`) dan penanda regional (Flag Indonesia).

**2. Main Navbar (White)**
- Background: `#FFFFFF` dengan `padding-y` longgar.
- Kiri: Logo PasarCCTV.
- Tengah: Search bar interaktif dengan dropdown tipe pencarian (Kategori/Brand/Produk). Tombol *submit* utama berwarna hijau cerah `bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm` sebagai aksen. *Dropdown autocomplete* dengan *Trending Searches* dan *Suggestion* terintegrasi.
- Kanan: Dropdown Akun Pengguna, Notifikasi Lonceng (dengan *badge* unread count warna merah), Wishlist, dan Cart.

**3. Sub-Navigation Bar (White)**
- Layout: Berada di bawah Main Navbar, menempel saat di-scroll jika diperlukan.
- Kiri: Tombol "Semua Kategori" (memunculkan `CategoryMenu`).
- Kanan (Menu Navigasi Horizontal): `Brand`, `Tentang Kami`, `Belanja`, `Paket Project`, `Maintenense & Service`, `Kontak`, dan `Diskon Unggulan` (dengan ikon promo).

**Mobile Behavior:**
- Top Bar disembunyikan seluruhnya.
- Tampilan Main Navbar diubah menjadi *single-line*: Tombol Hamburger (membuka menu sidebar lengkap), Logo berukuran kecil, Input Search tersembunyi menjadi tombol *icon* (membuka modal full-screen), Notifikasi, dan Cart.
- Menu-menu dari Sub-Nav Bar dipindahkan menjadi *list* vertikal di dalam menu Sidebar kiri.

---

### 5.2 BannerUtama (Hero Carousel)

Carousel utama di homepage, full-width.

```
Aspek rasio:
  Desktop: 21/9
  Tablet:  16/9
  Mobile:  4/3

Struktur slide:
  ├── Background image (NuxtImg, webp, eager load untuk slide 1)
  ├── Overlay gelap: bg-black/40 untuk keterbacaan teks
  ├── Teks kiri: Headline (32px, white, weight 500) + Subheadline (16px, white/80)
  └── CTA Button: bg #03AC0E, white, border-radius 8px

Kontrol carousel:
  ├── Prev/Next arrow: bg #0D1B12/70, color white, border-radius 50%
  └── Dot indicator: bawah-tengah, active dot bg #03AC0E, inactive bg white/40

Auto-play: 5 detik, pause on hover
Transition: slide atau crossfade, 400ms ease
```

---

### 5.3 Product Card

**Struktur:**

```
[Image Container 130px height]
  └── Badge Diskon (top-left): bg #D32F2F, text white, 11px, 500
  └── Badge Baru (top-right): bg #03AC0E, text white, 11px, 500
[Card Body padding: 12px]
  ├── Brand Label: 11px, #03AC0E, uppercase, letter-spacing 0.06em
  ├── Judul: 13px, 500, line-height 1.4
  ├── Spesifikasi: 11px, text-muted (hidden di mobile)
  ├── Price Row: harga utama (17px, #03AC0E) + harga coret (12px, text-muted)
  └── CTA Button: full-width, bg #03AC0E, white, 13px, 500
```

**Interaksi:**
- `hover: border-color → #03AC0E` + `transform: translateY(-2px)`
- `hover: box-shadow → var(--shadow-card-hover)`
- `hover: image scale → scale(1.04)`, `transition: 0.3s ease`
- Transition border & transform: `0.15s ease`
- Border default: `0.5px solid var(--color-border-tertiary)`

**Floating Action Buttons (desktop only, muncul saat hover card):**

```
Posisi: top-right image container, flex column, gap 6px
Visibility: opacity 0 → 1 saat hover, transition 0.15s

Wishlist button:
  Icon: ti-heart, 16px
  bg white, border 0.5px #E6F7E9, border-radius 8px, padding 7px
  hover: bg #FEE8E8, color #B91C1C

Compare button:
  Icon: ti-arrows-diff, 16px
  bg white, border 0.5px #E6F7E9, border-radius 8px, padding 7px
  hover: bg #E6F7E9, color #03AC0E
```

**Mobile:** Sembunyikan spesifikasi dan floating action buttons. Tampilkan hanya image, brand, judul, harga, dan tombol beli.

---

### 5.4 Price Display (Detail Page)

```
Harga coret: 14px, text-muted, text-decoration: line-through
Harga utama: 32px, #03AC0E, font-weight: 500
Penghematan: 13px, #B91C1C, font-weight: 500 — "Hemat Rp X.XXX (XX%)"

CTA Utama "Beli Langsung": bg #03AC0E, white, 14px, 500, border-radius 8px
CTA Sekunder (Cart): bg var(--color-bg-secondary), border 0.5px, border-radius 8px
```

---

### 5.5 Badge & Tag System

| Varian | Background | Text Color | Penggunaan |
|---|---|---|---|
| `tag-green` | `#E6F7E9` | `#03AC0E` | Garansi resmi, stok tersedia |
| `tag-red` | `#FEE8E8` | `#B91C1C` | Flash sale, diskon |
| `tag-amber` | `#FFF7E6` | `#B45309` | Promo aktif |
| `tag-dark` | `#0D1B12` | `#03AC0E` | Distributor resmi, partner |
| `tag-neutral` | `var(--bg-secondary)` | `var(--text-secondary)` | Status umum (tersedia, dll) |

Semua tag menggunakan `border-radius: 100px` (pill), `font-size: 12px`, `font-weight: 500`, `padding: 5px 12px`.

---

### 5.6 USP Bar

4 kolom responsif (`repeat(auto-fit, minmax(140px, 1fr))`), background `var(--bg-secondary)`, border `0.5px solid var(--border-tertiary)`, `border-radius: 12px`.

**Tiap item:**
```
Icon container: 36x36px, bg #E6F7E9, border-radius 10px
Icon: Tabler outline, 18px, color #03AC0E
Label: 12px, font-weight 500
Sublabel: 11px, text-muted
```

**Konten USP default:**

| Icon | Label | Sub |
|---|---|---|
| `ti-truck` | Gratis Ongkir | Min. Rp 500rb |
| `ti-headset` | Support 24/7 | Chat & Telepon |
| `ti-shield-check` | Garansi Resmi | 1–3 Tahun |
| `ti-refresh` | Retur 30 Hari | Tanpa Ribet |

---

### 5.7 Category Grid (Dark Mode)

Grid `3 kolom`, tiap item: `bg #0D1B12`, `border-radius: 10px`, `padding: 16px`.

```
Icon container: 32x32px, bg #1A2E1E, border-radius 8px
Icon: Tabler outline, 16px, color #03AC0E
Nama kategori: 13px, 500, color #C8E6CC
Jumlah produk: 11px, color #4A6E52
```

**Hover:** `background → #132314` (subtle lightening).

---

### 5.8 Store Locator Panel (Dark Premium)

```
Background: #0D1B12, border-radius: 12px, padding: 20px
Layout: flex row, space-between

Kiri:
  Judul: 16px, 500, color white
  Subjudul: 13px, color #4A6E52

Kanan:
  Icon ti-map-pin: 20px, color #03AC0E
  CTA Pill: bg #1A2E1E, border 0.5px #2A4A30, color #03AC0E, border-radius 100px
```

---

### 5.9 Footer

Footer menggunakan **skema warna ganda** tergantung rute:

#### Light Footer (halaman umum: home, search, produk)

```
Background: white, border-top 0.5px var(--border-tertiary)
Padding: 48px 0 24px

Struktur:
  ├── Service Features Row (5 pilar)
  │     Icon besar (32px, #03AC0E) + Label (13px, 500) + Sub (12px, text-muted)
  │     Layout: 5 kolom equal-width, centered
  │     Border-bottom 0.5px var(--border-tertiary), padding-bottom 32px
  │
  ├── Link Columns (4 kolom):
  │     Tentang PasarCCTV / Layanan / Kategori / Bantuan
  │     Heading: 13px, 500, text-primary
  │     Links: 13px, 400, text-secondary, hover color #03AC0E
  │
  └── Bottom Bar:
        Logo kiri + Copyright tengah + Social icons kanan
        Border-top 0.5px var(--border-tertiary), padding-top 20px
        Social icons: ti-brand-instagram, ti-brand-whatsapp, ti-brand-youtube
```

**5 Pilar Layanan (Service Features):**

| Icon | Label | Sub |
|---|---|---|
| `ti-truck` | Pengiriman Cepat | Ke seluruh Indonesia |
| `ti-shield-check` | Garansi Resmi | Produk bergaransi |
| `ti-headset` | Support 24/7 | Siap bantu kapanpun |
| `ti-tool` | Instalasi Profesional | Tim teknisi berpengalaman |
| `ti-refresh` | Retur Mudah | 30 hari tanpa syarat |

#### Dark Footer (rute: `/store-locator`)

```
Background: #0D1B12
Semua teks: #C8E6CC (utama), #4A6E52 (sekunder)
Link hover: #03AC0E
Border-color: #2A4A30
Icon: #03AC0E
```

---

### 5.10 FloatingChat

Widget chat mengambang, selalu tersedia di semua halaman untuk meningkatkan retensi dan konversi.

```
Posisi: fixed, bottom-right, margin 20px
z-index: 1000

Tombol trigger (collapsed):
  Ukuran: 52x52px, border-radius 50%
  Background: #03AC0E
  Icon: ti-message-circle, 24px, white
  Pulse animation: ring hijau tipis 0.5px, animasi expand 2s infinite
  Shadow: 0 4px 16px rgba(15,122,60,0.35)

Panel chat (expanded):
  Width: 320px, height: 420px
  Background: white, border-radius 16px
  Shadow: 0 8px 32px rgba(0,0,0,0.15)

  Header:
    bg #0D1B12, border-radius 16px 16px 0 0, padding 14px 16px
    Avatar bot: 32px, bg #03AC0E, icon ti-robot, color #03AC0E
    Nama: "PasarBot", 14px, 500, white
    Sub: "Online · Balas dalam hitungan detik", 11px, #4A6E52

  Body: overflow-y scroll, padding 12px
  Input area: border-top 0.5px var(--border-tertiary), padding 10px 12px
    Input text + tombol kirim bg #03AC0E

Mobile:
  Tombol trigger tetap ada di bottom-right
  Panel expanded: full-screen bottom sheet (border-radius 16px 16px 0 0)
```

---

## 6. UX Patterns

### Trust & Konversi

- **Brandrunning:** Marquee logo brand (Hikvision, Dahua, dll.) untuk menunjukkan otoritas.
- **Review & Terjual:** Tampil prominnen di card dan detail — rating + "Terjual X unit".
- **Garansi badge** selalu terlihat di card produk (bukan hanya di detail).

### Low-Friction Checkout

- **Beli Langsung** → langsung ke payment, satu klik.
- **AddonPicker** → beli aksesori (kabel, konektor, HDD) di halaman produk tanpa pindah halaman.
- **HDD Variant Selector** → update harga real-time saat pilih kapasitas.

### Mobile Optimizations

- Spesifikasi di product card disembunyikan di mobile.
- Touch target minimum `44px` (button, nav item).
- Bottom navigation untuk akses kategori, cart, akun.

---

## 7. Route-Specific Design & Component Architecture

### 7.1 Beranda (`/` atau `index.vue`)
Komposisi halaman beranda (Home) dibangun secara berurutan (*top-to-bottom*) menggunakan tumpukan komponen untuk menjaga alur *discovery* produk:

1. **`<BannerUtama />`**: Hero carousel dinamis yang menampilkan penawaran terbaik di area atas.
2. **`<Brandrunning />`**: Pita animasi logo (*marquee*) bergerak yang menampilkan merek mitra (Hikvision, Dahua, dll) untuk meningkatkan impresi *trust*.
3. **`<HomeBanner />`**: Banner statis promosi spesifik (e.g. flash sale atau bundling) dengan *spacing* `my-8`.
4. **`<PopularItems />`**: Grid baris produk terlaris atau populer yang paling dicari pembeli.
5. **`<ServiceBookingBanner />`**: Panel ajakan (CTA) yang menonjol untuk mempromosikan jasa pemasangan dan teknisi CCTV profesional kami.
6. **`<BannerSection />`**: Carousel banner interaktif lapis kedua.
7. **`<CategoryGrid />`**: Grid 4 kolom visual di bagian bawah untuk menyoroti kategori aksesori / produk niche.
8. **`<KeunggulanBar />`**: Bar horizontal pilar layanan (seperti Gratis Ongkir, Support 24/7, Garansi Resmi) yang menjadi jangkar penutup halaman.

### 7.2 Halaman Lainnya

| Route | Karakteristik |
|---|---|
| `/product/[id]` | Gallery zoom, tabel spesifikasi lengkap, panel detail produk, dan `<ProductRecommendation />` untuk cross-selling. |
| `/search` | Filter panel interaktif, grid produk dinamis yang adaptif dengan *infinite scroll*. |
| `/store-locator` | Tema antarmuka bernuansa peta satelit yang menonjolkan profesionalisme cabang fisik. |
| `/services/booking` | Form *wizard* langkah-demi-langkah (step-by-step) untuk penjadwalan layanan teknisi. |
| `/checkout` | Layout minimalis (`max-width 800px`), distraksi navbar ditekan seminimal mungkin untuk fokus pada penyelesaian transaksi (termasuk fitur *Snap Payment Midtrans*). |

---

## 8. Aksesibilitas & Teknis

- **SEO:** JSON-LD `Product`, `BreadcrumbList` di setiap halaman produk.
- **Images:** `NuxtImg` + format `webp/avif` + `lazy loading` otomatis.
- **Schema.org:** `itemscope` + `itemtype` pada elemen produk untuk indexing.
- **Page Transition:** `blur(1rem)` fade antar halaman untuk feel yang smooth.
- **Color Contrast:** Semua teks pada dark background minimum ratio 4.5:1 (WCAG AA).
- **Focus Ring:** Semua interactive element punya `outline` yang visible saat keyboard nav.

---

## 9. Icon System

Gunakan **Tabler Icons (outline)** secara konsisten — jangan campur dengan icon set lain.

| Konteks | Icon | Tabler Name |
|---|---|---|
| IP Camera | Kamera | `ti-camera` |
| NVR / DVR | Server | `ti-server` |
| Aksesori | Colokan | `ti-plug` |
| Wireless | Wifi | `ti-wifi` |
| Access Door | Gembok | `ti-lock` |
| Store Locator | Pin | `ti-map-pin` |
| Wishlist | Hati | `ti-heart` |
| Cart | Keranjang | `ti-shopping-cart` |
| Search | Kaca pembesar | `ti-search` |
| Support | Headset | `ti-headset` |
| Garansi | Shield | `ti-shield-check` |
| Pengiriman | Truk | `ti-truck` |

---

*Design System PasarCCTV v2 — Forest Green Premium*
*Terakhir diperbarui: Mei 2026 · Versi 2.1 (lengkap)*