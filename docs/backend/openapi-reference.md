# 📖 Swagger API Reference (Detailed)

> **Otomatis Dihasilkan**: Dokumen ini ditarik langsung dari kerangka kerja `OpenAPI` FastAPI. Rujukan ini memuat struktur metode (*Methods*), format input (*Payloads*), dan penempatan parameter.

## 🏷️ Tag: About Us

### 🟢 `GET` /abouts
> **Ambil konten halaman About Us (Redis cached)**

---

### 🔵 `POST` /abouts
> **[Admin] Buat halaman About Us baru**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`AboutPageCreate`**

---

### ⚪ `PATCH` /abouts
> **[Admin] Update partial halaman About Us aktif**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`AboutPageUpdate`**

---

### 🔵 `POST` /abouts/gallery
> **[Admin] Upload gambar gallery ke CDN**

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🔴 `DELETE` /abouts/gallery/{gallery_id}
> **[Admin] Hapus gambar gallery**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `gallery_id` | `path` | ✅ Ya | `string` |

---

### ⚪ `PATCH` /abouts/gallery/reorder
> **[Admin] Urutkan ulang gambar swiper gallery**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`GalleryReorderRequest`**

---

## 🏷️ Tag: Addons

### 🟢 `GET` /addons/bundle/{product_id_or_slug}
> **Get Addon Bundle**

Get dynamic addon bundle for a specific product based on identifier (UUID or Slug).
Validated with PostgreSQL and DragonflyDB caching.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `product_id_or_slug` | `path` | ✅ Ya | `string` |
| `category_slug` | `query` | ❌ Opsional | `string` |

---

## 🏷️ Tag: Admin Activities

### 🟢 `GET` /admin/activities
> **Get Activities**

Get unified recent activities for dashboard.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `type` | `query` | ❌ Opsional | `string` |
| `limit` | `query` | ❌ Opsional | `integer` |

---

## 🏷️ Tag: Admin Addons

### 🟢 `GET` /admin/addons/groups
> **List Groups**

---

### 🔵 `POST` /admin/addons/groups
> **Create Group**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`AddonGroupSchema`**

---

### 🟢 `GET` /admin/addons/groups/{group_uuid}/items
> **List Items**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `group_uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /admin/addons/groups/{group_uuid}/categories
> **List Group Categories**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `group_uuid` | `path` | ✅ Ya | `string` |

---

### ⚪ `PATCH` /admin/addons/groups/{group_uuid}
> **Update Group**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `group_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan struktur `JSON` mentah.

---

### 🔴 `DELETE` /admin/addons/groups/{group_uuid}
> **Delete Group**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `group_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/addons/items
> **Create Item**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`AddonItemSchema`**

---

### ⚪ `PATCH` /admin/addons/items/{item_uuid}
> **Update Item**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `item_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan struktur `JSON` mentah.

---

### 🔴 `DELETE` /admin/addons/items/{item_uuid}
> **Delete Item**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `item_uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /admin/addons/stock/{stock_uuid}
> **List Stock Mappings**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `stock_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/addons/stock/{stock_uuid}/sync
> **Sync Stock Mappings**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `stock_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan struktur `JSON` mentah.

---

## 🏷️ Tag: Admin Booking

### 🟢 `GET` /admin/service/bookings
> **Daftar semua booking (paginated)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `status` | `query` | ❌ Opsional | `string` |
| `date_from` | `query` | ❌ Opsional | `string` |
| `date_to` | `query` | ❌ Opsional | `string` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### ⚪ `PATCH` /admin/service/bookings/{booking_uuid}/status
> **Update status booking (state machine validated)**

Validasi transisi status:
PENDING → CONFIRMED / CANCEL
CONFIRMED → DP_PAID / CANCEL   (setelah admin verifikasi DP di Midtrans)
DP_PAID → PROGRESS / CANCEL
PROGRESS → DONE
DONE → LUNAS

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `booking_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`BookingStatusUpdate`**

---

### 🟢 `GET` /admin/service/stats
> **Dashboard statistik booking & revenue**

---

## 🏷️ Tag: Admin Coupon

### 🔵 `POST` /admin/coupon
> **Admin Create Coupon**

Buat kupon baru.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CouponCreateRequest`**

---

### 🟢 `GET` /admin/coupon
> **Admin List Coupons**

List semua kupon (aktif & non-aktif, exclude deleted).

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `include_inactive` | `query` | ❌ Opsional | `boolean` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /admin/coupon/{code}
> **Admin Get Coupon**

Detail satu kupon by code.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `code` | `path` | ✅ Ya | `string` |

---

### ⚪ `PATCH` /admin/coupon/{code}
> **Admin Update Coupon**

Update sebagian field kupon.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `code` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CouponUpdateRequest`**

---

### 🔴 `DELETE` /admin/coupon/{code}
> **Admin Delete Coupon**

Soft delete kupon.
Hard delete dijadwalkan Celery task setelah 30 hari.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `code` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Admin Dashboard Booking

### 🟢 `GET` /admin/dashboard/booking/kpi
> **Dashboard Booking Kpi**

KPI utama dashboard booking:
- total_booking, booking_bulan_ini, booking_hari_ini
- pending_count, confirmed_count, progress_count
- total_revenue (LUNAS + DONE), revenue_bulan_ini
- dp_terkumpul (DP_PAID + PROGRESS + DONE + LUNAS)
- conversion_rate  (confirmed / total × 100)
- cancel_rate      (cancel / total × 100)
TTL Redis: 60 s

---

### 🟢 `GET` /admin/dashboard/booking/revenue
> **Dashboard Booking Revenue**

Data chart revenue:
- mode=daily   → 30 hari terakhir (label: 'DD MMM')
- mode=monthly → 12 bulan terakhir (label: 'MMM YYYY')

Setiap titik: { label, total_revenue, dp_revenue, booking_count }
TTL Redis: 120 s

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `mode` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /admin/dashboard/booking/status
> **Dashboard Booking Status**

Distribusi booking per status (untuk pie / bar chart).
Return: list { status, label, count, percentage }
TTL Redis: 60 s

---

### 🟢 `GET` /admin/dashboard/booking/alerts
> **Dashboard Booking Alerts**

Alert yang perlu tindakan admin:
- pending_lama     : booking PENDING > 24 jam tanpa respons
- slot_penuh_besok : slot besok yang sudah ≥ 3 booking
- dp_expire_soon   : payment DP pending yang < 2 jam expired
- booking_besok    : daftar booking terjadwal besok (reminder teknisi)
TTL Redis: 30 s (fresh, karena operasional)

---

### 🟢 `GET` /admin/dashboard/booking/recent
> **Dashboard Booking Recent**

Booking terbaru (created_at DESC).
Tiap item: uuid, booking_number, contact_name, category,
           status, total_price, scheduled_date, created_at
TTL Redis: 30 s

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `limit` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /admin/dashboard/booking/today
> **Dashboard Booking Today**

Snapshot booking HARI INI:
- bookings   : list booking terjadwal hari ini (semua slot)
- slot_summary: { "08:00-11:00": {count, remaining}, ... }
- total_today, confirmed_today, dp_paid_today
TTL Redis: 30 s

---

### 🟢 `GET` /admin/dashboard/booking/payment
> **Dashboard Booking Payment**

Ringkasan status semua payment Midtrans:
- dp_pending_count / dp_success_count / dp_expire_count
- lunas_pending_count / lunas_success_count
- total_dp_terkumpul, total_lunas_terkumpul
- grand_total_terkumpul
- payment_pending_list: payment yang masih menggantung (butuh follow-up)
TTL Redis: 60 s

---

## 🏷️ Tag: Admin Dashboard Stock

### 🟢 `GET` /admin/dashboard/stock/summary
> **Dashboard Summary**

Kartu KPI utama:
- total_products, active_products, inactive_products
- low_stock_count  (stok ≤ threshold)
- out_of_stock_count (stok = 0)
- total_revenue_potential (sum online_price * stok aktif)
- total_terjual
TTL Redis: 60 detik

---

### 🟢 `GET` /admin/dashboard/stock/low
> **Dashboard Low Stock**

Produk dengan 1 ≤ stok ≤ threshold (default 5), terurut stok ASC.
TTL Redis: 60 detik  (key menyertakan threshold)

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `threshold` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /admin/dashboard/stock/out
> **Dashboard Out Of Stock**

Produk dengan stok = 0, terurut terjual DESC (yang paling laris dulu).
TTL Redis: 60 detik

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /admin/dashboard/stock/distribution
> **Dashboard Distribution**

Data untuk chart distribusi:
- by_category  : {label, count, revenue}
- by_brand     : {label, count, revenue}
- price_buckets: histogram harga
Sumber: Elasticsearch aggregation.
TTL Redis: 5 menit

---

### 🟢 `GET` /admin/dashboard/stock/top-selling
> **Dashboard Top Selling**

Produk dengan terjual tertinggi.
TTL Redis: 2 menit

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `limit` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /admin/dashboard/stock/recent
> **Dashboard Recent**

Produk yang baru ditambahkan (created_at DESC).
Sumber: Elasticsearch.
TTL Redis: 2 menit

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `limit` | `query` | ❌ Opsional | `integer` |

---

## 🏷️ Tag: Admin Dashboard Transaksi

### 🟢 `GET` /admin/dashboard/summary
> **Dashboard Summary**

KPI cards utama dashboard:

Revenue
─────────────────────────────
- total_revenue          : sum gross_amount status settlement/capture
- revenue_today          : revenue hari ini
- revenue_this_week      : revenue 7 hari terakhir
- revenue_this_month     : revenue bulan berjalan

Orders
─────────────────────────────
- total_orders           : semua transaksi
- orders_today           : transaksi hari ini
- pending_payment_count  : status pending_payment (belum bayar)
- settlement_count       : status settlement (sukses)
- cancel_expire_count    : cancel + expire + deny (gagal)

Shipping
─────────────────────────────
- processing_shipment    : shipment status PROCESSING (sudah bayar, belum kirim)
- shipped_count          : shipment status SHIPPED
- delivered_count        : shipment status DELIVERED

Produk
─────────────────────────────
- total_items_sold       : sum quantity dari TransactionItem (settlement saja)
- avg_order_value        : rata-rata gross_amount (settlement)
- total_shipping_cost    : total ongkos kirim terkumpul

TTL Redis: 60 s

---

### 🟢 `GET` /admin/dashboard/revenue-chart
> **Dashboard Revenue Chart**

Data chart revenue berdasarkan rentang:
- 7d  → 7 hari terakhir, label 'Rab 1 Jan'
- 30d → 30 hari terakhir, label '1 Jan'
- 12m → 12 bulan terakhir, label 'Jan 2025'

Setiap titik mengandung:
{ label, period, gross_revenue, net_revenue, order_count, avg_order }

gross_revenue = sum gross_amount (settlement)
net_revenue   = gross_revenue - sum shipping_cost
TTL Redis: 120 s per range

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `range` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /admin/dashboard/activity
> **Dashboard Activity**

Recent activity feed — transaksi terbaru lintas semua status,
diurut created_at DESC.

Tiap item mengandung:
{ order_id, user_id, status, gross_amount, payment_type,
  item_count, first_product_name, shipment_status,
  courier_name, created_at }

TTL Redis: 30 s

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `limit` | `query` | ❌ Opsional | `integer` |

---

## 🏷️ Tag: Admin Operational

### 🟢 `GET` /admin/service/holidays
> **Daftar hari libur layanan**

---

### 🔵 `POST` /admin/service/holidays
> **Tambah hari libur**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`HolidayCreate`**

---

### 🔴 `DELETE` /admin/service/holidays/{uuid}
> **Hapus hari libur**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /admin/service/hours
> **Daftar jam operasional mingguan**

---

### ⚪ `PATCH` /admin/service/hours/{day}
> **Update jam operasional per hari (0-6)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `day` | `path` | ✅ Ya | `integer` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`OperationalHoursCreate`**

---

## 🏷️ Tag: Admin Package

### 🔵 `POST` /admin/service/packages
> **Buat paket CCTV baru beserta item Stock**

Buat paket baru. data = JSON string dari PackageCreate.
thumbnail = File upload opsional.

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🟢 `GET` /admin/service/packages
> **Daftar semua paket (termasuk non-aktif)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `category` | `query` | ❌ Opsional | `string` |

---

### ⚪ `PATCH` /admin/service/packages/{pkg_uuid}
> **Update metadata paket (name, desc, is_active, dll)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `pkg_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🔵 `POST` /admin/service/packages/{pkg_uuid}/recalculate
> **Recalculate device_price dari item terkini**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `pkg_uuid` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Admin Pricing

### 🔵 `POST` /admin/service/pricing
> **Buat versi pricing config baru (append-only, cache invalidated)**

Versi lama TIDAK dihapus (audit trail).
Cache Redis diinvalidate otomatis.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`PricingConfigCreate`**

---

### ⚪ `PATCH` /admin/service/pricing/{uuid}
> **Update konfigurasi pricing yang sudah ada (overwrite)**

Mengupdate record pricing yang sudah ada. 
Gunakan ini jika hanya ingin koreksi tanpa menambah versi baru.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`PricingConfigCreate`**

---

### 🟢 `GET` /admin/service/pricing/active
> **Lihat pricing config aktif saat ini**

---

### 🟢 `GET` /admin/service/pricing/all
> **Daftar semua konfigurasi pricing (aktif & tidak aktif)**

---

### 🟢 `GET` /admin/pricing/{uuid}
> **Ambil konfigurasi pricing tunggal berdasarkan UUID**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/service/pricing/activate
> **Aktifkan konfigurasi pricing tertentu, menonaktifkan yang lain**

**📤 Request Body (Payload):**
- Membutuhkan struktur `JSON` mentah.

---

## 🏷️ Tag: Admin Technician

### 🟢 `GET` /admin/service/technicians
> **Daftar semua teknisi**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `active_only` | `query` | ❌ Opsional | `boolean` |

---

### 🔵 `POST` /admin/service/technicians
> **Tambah teknisi baru**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`TechnicianCreate`**

---

### 🟢 `GET` /admin/service/technicians/{uuid}
> **Detail teknisi + daftar booking**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

---

### ⚪ `PATCH` /admin/service/technicians/{uuid}
> **Update data teknisi**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`TechnicianCreate`**

---

### 🟢 `GET` /admin/service/technicians/{uuid}/validate-assignment
> **Cek ketersediaan teknisi sebelum ditugaskan**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |
| `target_date` | `query` | ✅ Ya | `string` |
| `target_slot` | `query` | ✅ Ya | `string` |
| `exclude_booking` | `query` | ❌ Opsional | `string` |

---

### 🔵 `POST` /admin/service/technicians/upload-picture
> **Upload foto profil teknisi**

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

## 🏷️ Tag: Booking

### 🔵 `POST` /services/booking/draft
> **Simpan step wizard ke Redis draft (TTL 30 menit)**

Frontend panggil setiap berpindah step.
Draft di-merge (bukan replace), jadi aman untuk partial update.
Jika step 1 & 2 sudah ada, estimasi dihitung otomatis.
Session ID: generate di frontend (UUID v4 / random 32 char).

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`DraftSaveRequest`**

---

### 🟢 `GET` /services/booking/draft/{session_id}
> **Ambil draft tersimpan (restore wizard saat reload)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `session_id` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /services/booking/submit
> **Submit booking dari draft (harga dihitung ulang di backend)**

Submit final dari draft wizard.
Backend SELALU hitung ulang harga — frontend tidak bisa inject harga.
Anti double-booking via Redis SETNX (atomic).
Max 3 booking per slot.
Validasi max jarak layanan.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`BookingSubmitRequest`**

---

### 🔵 `POST` /services/booking/direct
> **Booking langsung (tanpa wizard, untuk mobile/integrasi)**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`BookingCreateDirect`**

---

### 🟢 `GET` /services/booking/{booking_uuid}
> **Cek status booking by UUID**

UUID cukup aman sebagai secret URL (128-bit random).

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `booking_uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /services/booking/number/{booking_number}
> **Cek status booking by nomor (BK-YYYYMMDD-XXXXXX)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `booking_number` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Cart

### 🟢 `GET` /cart
> **Get My Cart**

Melihat isi keranjang belanja user.

---

### 🔵 `POST` /cart
> **Add Item To Cart**

Menambahkan barang ke keranjang atau menambah kuantitas jika sudah ada.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CartAddRequest`**

---

### ⚪ `PATCH` /cart/{cart_uuid}
> **Update Cart Item**

Mengubah jumlah barang di dalam keranjang.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `cart_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CartUpdateRequest`**

---

### 🔴 `DELETE` /cart/{cart_uuid}
> **Delete Cart Item**

Menghapus satu barang dari keranjang.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `cart_uuid` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: General

### 🔵 `POST` /test-notification
> **Test Notification**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `tags` | `query` | ❌ Opsional | `string` |

---

## 🏷️ Tag: Image Sections

### 🟢 `GET` /image-sections/public/{identifier}
> **[PUBLIC] Get section by identifier (Redis cached)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `identifier` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /image-sections
> **[ADMIN] Get all sections with items**

---

### 🔵 `POST` /image-sections
> **[ADMIN] Create new section**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ImageSectionCreate`**

---

### 🟠 `PUT` /image-sections/{section_uuid}
> **[ADMIN] Update section title / mode / status**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `section_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ImageSectionUpdate`**

---

### 🔴 `DELETE` /image-sections/{section_uuid}
> **[ADMIN] Delete section + all its items**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `section_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /image-sections/{section_identifier}/upload-banner
> **[ADMIN] Upload image and attach to section**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `section_identifier` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🔴 `DELETE` /image-sections/items/{item_uuid}
> **[ADMIN] Delete single banner item (also removes from CDN)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `item_uuid` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Main Bottom Banner

### 🟢 `GET` /main-bottom/public
> **Get Public Banners**

---

### 🟢 `GET` /main-bottom/admin
> **List All Banners**

---

### 🔵 `POST` /main-bottom/admin
> **Create Banner**

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🟠 `PUT` /main-bottom/admin/{banner_uuid}
> **Update Banner**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `banner_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🔴 `DELETE` /main-bottom/admin/{banner_uuid}
> **Delete Banner**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `banner_uuid` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Messages

### 🔵 `POST` /messages/send
> **[User] Kirim pesan ke admin**

Multipart form: `body` (teks, optional) + `images` (UploadFile, maks 2).

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🟢 `GET` /messages/poll
> **[User] Polling pesan baru**

Kirim `after_sent_at` (ISO 8601) = sent_at pesan terakhir yang sudah diterima FE. Panggil setiap 3–5 detik saat chat terbuka.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `after_sent_at` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /messages/history
> **[User] Load history pesan**

Ambil pesan lama sebelum `before_sent_at`. Untuk load-more saat scroll ke atas.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `before_sent_at` | `query` | ❌ Opsional | `string` |
| `limit` | `query` | ❌ Opsional | `integer` |

---

### ⚪ `PATCH` /messages/read
> **[User] Tandai pesan sebagai dibaca**

Kirim list `message_ids`. Reset unread_by_user counter di conversation.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`MarkReadRequest`**

---

### 🟢 `GET` /messages/unread
> **[User] Jumlah pesan belum dibaca (badge)**

Polling ringan khusus badge notif. Baca dari kolom denormalized — O(1).

---

### 🟢 `GET` /messages/admin/inbox
> **[Admin] Daftar semua percakapan (inbox)**

Diurutkan dari conversation paling baru aktif. Poll setiap 5 detik untuk refresh badge unread di inbox.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `skip` | `query` | ❌ Opsional | `integer` |
| `limit` | `query` | ❌ Opsional | `integer` |

---

### 🔵 `POST` /messages/admin/{conversation_id}/send
> **[Admin] Balas pesan user**

Multipart form: `body` (teks, optional) + `images` (UploadFile, maks 2).

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `conversation_id` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🟢 `GET` /messages/admin/{conversation_id}/poll
> **[Admin] Polling pesan baru dalam satu conversation**

Poll setiap 3 detik saat chat admin terbuka. Kirim `after_sent_at` = timestamp pesan terakhir yang sudah diterima.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `conversation_id` | `path` | ✅ Ya | `string` |
| `after_sent_at` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /messages/admin/{conversation_id}/history
> **[Admin] Load history pesan (scroll ke atas)**

Ambil pesan lama sebelum `before_sent_at`. Untuk fitur load-more.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `conversation_id` | `path` | ✅ Ya | `string` |
| `before_sent_at` | `query` | ❌ Opsional | `string` |
| `limit` | `query` | ❌ Opsional | `integer` |

---

### ⚪ `PATCH` /messages/admin/{conversation_id}/read
> **[Admin] Mark pesan sebagai dibaca**

Kirim list `message_ids`. Reset unread_by_admin counter di conversation.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `conversation_id` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`MarkReadRequest`**

---

### 🟢 `GET` /messages/admin/{conversation_id}/unread
> **[Admin] Unread count satu conversation (badge)**

Baca dari kolom denormalized di conversation — O(1), tidak COUNT query.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `conversation_id` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Payment

### 🟢 `GET` /services/payment/status/{booking_uuid}
> **Cek status payment terkini untuk booking**

Frontend poll endpoint ini setelah user selesai bayar di Midtrans Snap.
Return semua payment record + status booking terkini.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `booking_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /services/payment/create
> **Buat transaksi Midtrans Snap (DP atau Pelunasan)**

Validasi state booking, hitung amount DP/Pelunasan,
buat transaksi Midtrans Snap, simpan ke DB.
Mengembalikan payment_token untuk Midtrans Snap.js di frontend.

Flow DP:   booking CONFIRMED → bayar dp_amount (50%) → status DP_PAID → jadwalkan teknisi
Flow Lunas: booking DONE → bayar remaining_amount (50%) → status LUNAS

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CreatePaymentRequest`**

---

## 🏷️ Tag: Portfolio

### 🟢 `GET` /portfolio/page
> **Halaman portofolio publik (featured + projects + testimonials)**

Satu endpoint untuk semua kebutuhan halaman /portfolio di Nuxt.
- Featured project (case study before/after)
- Grid semua project aktif
- Testimonial aktif
Di-cache Redis 5 menit, otomatis invalidate saat ada perubahan data.

---

### 🟢 `GET` /portfolio/projects/{project_id}
> **Detail satu project (publik)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `project_id` | `path` | ✅ Ya | `string` |

---

### ⚪ `PATCH` /portfolio/projects/{project_id}
> **[Admin] Update project**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `project_id` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ProjectUpdateRequest`**

---

### 🔴 `DELETE` /portfolio/projects/{project_id}
> **[Admin] Hapus project beserta semua gambarnya dari R2**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `project_id` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /portfolio/projects
> **[Admin] List semua project**

---

### 🔵 `POST` /portfolio/projects
> **[Admin] Buat project baru**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ProjectCreateRequest`**

---

### 🔵 `POST` /portfolio/projects/{project_id}/images
> **[Admin] Upload 1–10 gambar ke project**

Upload beberapa gambar sekaligus ke satu project.
- `role=cover`   → gambar utama yang muncul di card grid
- `role=before`  → foto sebelum untuk case study (featured)
- `role=after`   → foto sesudah untuk case study (featured)
- `role=gallery` → foto tambahan

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `project_id` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### ⚪ `PATCH` /portfolio/images/{image_id}
> **[Admin] Update meta gambar (role, alt_text, sort_order)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `image_id` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ImageUpdateRequest`**

---

### 🔴 `DELETE` /portfolio/images/{image_id}
> **[Admin] Hapus satu gambar dari R2 dan DB**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `image_id` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /portfolio/reviews
> **[Admin] List semua review**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `project_id` | `query` | ❌ Opsional | `string` |

---

### 🔵 `POST` /portfolio/reviews
> **[Admin] Tambah review / testimonial**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ReviewCreateRequest`**

---

### ⚪ `PATCH` /portfolio/reviews/{review_id}
> **[Admin] Edit review**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `review_id` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ReviewUpdateRequest`**

---

### 🔴 `DELETE` /portfolio/reviews/{review_id}
> **[Admin] Hapus review**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `review_id` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Public Services

### 🟢 `GET` /services/config
> **Konfigurasi layanan (harga, brand, addon, DP%)**

Endpoint utama untuk inisialisasi form booking.
Di-cache Redis 1 jam.
Berisi: kategori + harga dasar, daftar brand + multiplier,
addon yang tersedia, aturan transport, persentase DP, max jarak.

---

### 🟢 `GET` /services/packages
> **Daftar paket CCTV siap pesan**

Daftar paket CCTV (bundle kamera + estimasi jasa).
Digunakan di halaman beranda / halaman produk.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `category` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /services/packages/{pkg_uuid}
> **Detail paket + breakdown harga**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `pkg_uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /services/packages/slug/{slug}
> **Detail paket by slug (SEO-friendly)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `slug` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /services/distance
> **Cek jarak dari Cimahi + estimasi ongkir**

Hitung jarak haversine dari markas Padjajaran CCTV (Cimahi)
ke koordinat user. Validasi max jarak layanan.
Frontend kirim lat/lon dari Geolocation API atau hasil geocoding.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`DistanceCheckRequest`**

---

### 🔵 `POST` /services/estimate
> **Estimasi harga real-time (no DB write)**

Kalkulasi harga instan tanpa menyimpan data.
Rate-limited: 5 request/menit per IP.
Berisi: harga jasa, addon, transport, total, DP & sisa.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`EstimateRequest`**

---

### 🟢 `GET` /services/slots
> **Cek slot tersedia untuk tanggal tertentu**

Cek sisa slot per time slot untuk satu tanggal.
Frontend pakai ini untuk disable slot yang sudah penuh di date picker.
Max 3 booking per slot.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `target_date` | `query` | ✅ Ya | `string` |

---

## 🏷️ Tag: System Settings

### 🟢 `GET` /settings/couriers
> **Get Courier Settings**

---

### 🟠 `PUT` /settings/couriers
> **Update Courier Settings**

**📤 Request Body (Payload):**
- Membutuhkan struktur `JSON` mentah.

---

## 🏷️ Tag: User Booking

### 🟢 `GET` /user/bookings
> **Dashboard booking user (stats + list + filter + search)**

Dashboard lengkap user:
- Stats (total, aktif, selesai, tagihan pending)
- List booking dengan filter status & sort
- Search by nomor booking / kota / brand / kategori
- Setiap item sudah include `action` (CTA) + link bayar jika ada

Cache Redis per user+filter: 1 menit.
Stats cache: 2 menit.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `status` | `query` | ❌ Opsional | `string` |
| `sort` | `query` | ❌ Opsional | `string` |
| `q` | `query` | ❌ Opsional | `string` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /user/bookings/{booking_uuid}
> **Detail booking lengkap by UUID**

Full detail: pricing breakdown, semua payment, status, CTA.
Jika status CONFIRMED/DONE + ada payment pending → `action.payment_url` sudah terisi.
Cache 15 detik (status aktif) / 30 detik (status final).

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `booking_uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /user/bookings/number/{booking_number}
> **Detail booking by nomor (BK-YYYYMMDD-XXXXXX)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `booking_number` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /user/bookings/{booking_uuid}/pay
> **Buat atau resume payment (DP / Pelunasan)**

Flow:
1. Validasi booking milik user + status sesuai
2. Cek payment pending yang masih valid → kembalikan jika ada (resume)
3. Jika tidak ada / expired → buat transaksi Midtrans baru
4. Return payment_token + payment_url

Frontend buka payment_url di tab baru / Snap popup.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `booking_uuid` | `path` | ✅ Ya | `string` |
| `payment_type` | `query` | ✅ Ya | `string` |

---

### 🟢 `GET` /user/bookings/stats/summary
> **Stats ringkas (untuk badge notifikasi di navbar)**

Endpoint ringan hanya untuk stats.
Dipakai navbar badge: total aktif + total tagihan pending.
Cache 2 menit.

---

## 🏷️ Tag: Buys

### 🟢 `GET` /transaksi/shipping/estimate
> **Estimate Shipping**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `address_uuid` | `query` | ✅ Ya | `string` |
| `stock_uuid` | `query` | ✅ Ya | `string` |
| `quantity` | `query` | ❌ Opsional | `integer` |
| `weight` | `query` | ❌ Opsional | `string` |
| `courier` | `query` | ❌ Opsional | `string` |

---

### 🔵 `POST` /transaksi/checkout
> **Checkout**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CheckoutRequest`**

---

### 🔵 `POST` /transaksi/webhook/midtrans
> **Midtrans Webhook**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`MidtransWebhookPayload`**

---

### 🟢 `GET` /transaksi/my
> **Get My Transactions**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `page` | `query` | ❌ Opsional | `integer` |
| `limit` | `query` | ❌ Opsional | `integer` |
| `sort` | `query` | ❌ Opsional | `string` |
| `sort_by` | `query` | ❌ Opsional | `string` |
| `stock_id` | `query` | ❌ Opsional | `string` |
| `stock_name` | `query` | ❌ Opsional | `string` |
| `status` | `query` | ❌ Opsional | `string` |
| `min_amount` | `query` | ❌ Opsional | `string` |
| `max_amount` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /transaksi/my/all
> **Get All My Transactions**

Mengembalikan semua transaksi user (reguler + promo) digabung,
diurutkan by created_at, dengan pagination.

Tiap item punya field:
  - trx_type: "regular" | "promo"
  - order_id
  - gross_amount
  - transaction_status
  - items: list produk / paket yang dibeli
  - snap_token / payment_url (jika masih pending → bisa dipakai repay)

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `page` | `query` | ❌ Opsional | `integer` |
| `limit` | `query` | ❌ Opsional | `integer` |
| `sort` | `query` | ❌ Opsional | `string` |
| `status` | `query` | ❌ Opsional | `string` |
| `trx_type` | `query` | ❌ Opsional | `string` |
| `min_amount` | `query` | ❌ Opsional | `string` |
| `max_amount` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /transaksi/detail/{order_id}
> **Get Transaction Detail**

Mendukung dua format order_id:
  - ORD-YYYYMMDD-XXXXXXXX  → Transaction biasa
  - PROMO-YYYYMMDD-XXXXXXXX → PromoTransaction

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `order_id` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /transaksi/invoice/{order_id}
> **Download Invoice**

Menghasilkan file PDF invoice untuk transaksi tertentu.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `order_id` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /transaksi/repay/{order_id}
> **Repay Transaction**

Membuat ulang Midtrans Snap token untuk transaksi yang masih pending.
Mendukung transaksi reguler (ORD-) maupun promo (PROMO-).

Response:
  {
    "order_id": "...",
    "snap_token": "...",
    "payment_url": "...",
    "gross_amount": 123456,
    "trx_type": "regular" | "promo"
  }

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `order_id` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Check Transaksi Status

### 🟢 `GET` /cek/shipping/lokasi
> **Find Location**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `q` | `query` | ✅ Ya | `string` |
| `limit` | `query` | ❌ Opsional | `integer` |
| `offset` | `query` | ❌ Opsional | `integer` |

---

### 🔵 `POST` /cek/shipping/ongkir
> **Calculate Shipping**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`OngkirRequest`**

---

### 🟢 `GET` /cek/shipping/address
> **Get User Addresses**

---

### 🔵 `POST` /cek/shipping/address
> **Create User Address**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`UserAddressCreate`**

---

### 🟠 `PUT` /cek/shipping/address/{address_id}
> **Update User Address**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `address_id` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`SaveUserAddressRequest`**

---

### 🔴 `DELETE` /cek/shipping/address/{address_id}
> **Delete User Address**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `address_id` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Promos

### 🟢 `GET` /promos
> **Daftar promo aktif**

Daftar promo yang sedang aktif, diurutkan berdasarkan priority (tertinggi → terendah).
Bisa difilter berdasarkan target: produk, jasa, atau semua.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `target` | `query` | ❌ Opsional | `string` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /promos/flash-sale
> **Daftar flash sale aktif**

Flash sale dengan kuota terbatas. Tampilkan remaining_quota untuk urgency.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /promos/{slug}
> **Detail promo by slug**

Detail promo beserta daftar item yang terikat (produk / paket jasa).

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `slug` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /promos/validate
> **Preview harga + validasi promo (tanpa checkout)**

Gunakan endpoint ini untuk menampilkan estimasi harga di halaman promo
sebelum user menekan tombol 'Checkout'.

Tidak ada perubahan data — murni kalkulasi.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`PromoValidateRequest`**

---

### 🔵 `POST` /promos/checkout
> **Checkout melalui halaman promo**

Checkout produk / jasa yang menggunakan promo.

Flow:
1. Validasi promo (aktif, kuota, periode, user limit)
2. Kalkulasi diskon per item berdasarkan tipe promo
3. Jika ada produk fisik → cek ongkir + lock stok
4. Jika ada jasa → hitung biaya transport + buat ServiceBooking
5. Buat PromoTransaction + charge Midtrans Snap
6. Catat PromoUsage (idempotency + rollback support)

Return: snap_token untuk Midtrans Snap.js di frontend.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`PromoCheckoutRequest`**

---

### 🟢 `GET` /promos/my-orders
> **Riwayat order promo user**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `page` | `query` | ❌ Opsional | `integer` |
| `limit` | `query` | ❌ Opsional | `integer` |
| `status` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /promos/order/{order_id}
> **Detail promo order by order_id**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `order_id` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/promos
> **Buat promo baru (status DRAFT)**

Buat promo dengan status DRAFT.
Publish via endpoint /publish.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`PromoCreate`**

---

### 🟢 `GET` /admin/promos
> **Daftar semua promo (termasuk draft & archived)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `status` | `query` | ❌ Opsional | `string` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /admin/promos/dashboard
> **Data lengkap untuk Dashboard Promo (Summary, Trend 7 Hari, Recent Activity)**

---

### 🟢 `GET` /admin/promos/status
> **Statistik penggunaan promo**

---

### 🟢 `GET` /admin/promos/{promo_uuid}
> **Detail promo by UUID (admin)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `promo_uuid` | `path` | ✅ Ya | `string` |

---

### ⚪ `PATCH` /admin/promos/{promo_uuid}
> **Update metadata promo**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `promo_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`PromoUpdate`**

---

### 🔴 `DELETE` /admin/promos/{promo_uuid}
> **Soft delete / arsip promo**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `promo_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/promos/{promo_uuid}/publish
> **Publish promo (DRAFT/PAUSED → ACTIVE)**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `promo_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/promos/{promo_uuid}/pause
> **Pause promo aktif**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `promo_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/promos/{promo_uuid}/items
> **Tambah item (Stock/ServicePackage) ke promo**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `promo_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`PromoItemCreate`**

---

### 🔴 `DELETE` /admin/promos/{promo_uuid}/items/{item_uuid}
> **Hapus item dari promo**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `promo_uuid` | `path` | ✅ Ya | `string` |
| `item_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/promos/{promo_uuid}/notify
> **Trigger Notify New Promo**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `promo_uuid` | `path` | ✅ Ya | `string` |

---

### 🔵 `POST` /admin/promos/upload-banner
> **Upload banner promo ke CDN R2**

Endpoint khusus untuk mengunggah gambar banner ke Cloudflare R2.
Mengembalikan URL public dari gambar tersebut.

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

## 🏷️ Tag: Public Banner

### 🔵 `POST` /banner/admin/create
> **Create Banner**

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🟢 `GET` /banner/
> **Get Banners**

ENDPOINT PUBLIK: ULTRA FAST
Mengembalikan raw bytes dari Redis tanpa overhead JSON parsing di Python.

---

### 🔴 `DELETE` /banner/admin/{uuid}
> **Delete Banner**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

---

### 🟠 `PUT` /banner/admin/{uuid}
> **Edit Banner**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

## 🏷️ Tag: Public Brands

### 🟢 `GET` /brands/
> **Get Brands**

---

### 🔵 `POST` /brands/admin/create
> **Create Brand**

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🟠 `PUT` /brands/admin/{uuid}
> **Edit Brand**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🔴 `DELETE` /brands/admin/{uuid}
> **Delete Brand**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Public Category

### 🟢 `GET` /category/
> **Get Public Categories**

---

### 🔵 `POST` /category/admin/category
> **Create Cat**

**📤 Request Body (Payload):**
- 📝 Membutuhkan `Form-URLEncoded` (Standar OAuth2/Login).

---

### 🔵 `POST` /category/admin/subcategory
> **Create Sub**

**📤 Request Body (Payload):**
- 📝 Membutuhkan `Form-URLEncoded` (Standar OAuth2/Login).

---

### 🔴 `DELETE` /category/admin/category/{uuid}
> **Delete Cat**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `uuid` | `path` | ✅ Ya | `string` |

---

## 🏷️ Tag: Spesial Admin Rekap

### 🟢 `GET` /recap/transaksi
> **Get All Transaksi Admin**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `page` | `query` | ❌ Opsional | `integer` |
| `limit` | `query` | ❌ Opsional | `integer` |
| `sort_by` | `query` | ❌ Opsional | `string` |
| `sort_order` | `query` | ❌ Opsional | `string` |
| `transaction_status` | `query` | ❌ Opsional | `string` |
| `payment_type` | `query` | ❌ Opsional | `string` |
| `user_id` | `query` | ❌ Opsional | `string` |
| `start_date` | `query` | ❌ Opsional | `string` |
| `end_date` | `query` | ❌ Opsional | `string` |

---

### 🟠 `PUT` /recap/transaksi/{order_id}/waybill
> **Update Transaction Waybill**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `order_id` | `path` | ✅ Ya | `string` |
| `waybill_number` | `query` | ✅ Ya | `string` |
| `courier_name` | `query` | ❌ Opsional | `string` |
| `status` | `query` | ❌ Opsional | `string` |

---

## 🏷️ Tag: Stok

### 🔵 `POST` /stok/admin/create
> **Admin Create Stock**

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🔵 `POST` /stok/public/coupon/validate
> **Validate Coupon Endpoint**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CouponValidateRequest`**

---

### 🟢 `GET` /stok/public/list
> **Public Get Products**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `q` | `query` | ❌ Opsional | `string` |
| `cat` | `query` | ❌ Opsional | `array` |
| `brand` | `query` | ❌ Opsional | `string` |
| `type` | `query` | ❌ Opsional | `string` |
| `min_price` | `query` | ❌ Opsional | `string` |
| `max_price` | `query` | ❌ Opsional | `string` |
| `sort` | `query` | ❌ Opsional | `string` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /stok/admin/stocks
> **Admin Get Products**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `q` | `query` | ❌ Opsional | `string` |
| `cat` | `query` | ❌ Opsional | `array` |
| `brand` | `query` | ❌ Opsional | `string` |
| `type` | `query` | ❌ Opsional | `string` |
| `is_active` | `query` | ❌ Opsional | `string` |
| `stock_status` | `query` | ❌ Opsional | `string` |
| `min_price` | `query` | ❌ Opsional | `string` |
| `max_price` | `query` | ❌ Opsional | `string` |
| `sort` | `query` | ❌ Opsional | `string` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /stok/public/brands
> **Public Get All Brands**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `min_products` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /stok/public/brands/{brand_slug}
> **Public Get Products By Brand**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `brand_slug` | `path` | ✅ Ya | `string` |
| `q` | `query` | ❌ Opsional | `string` |
| `cat` | `query` | ❌ Opsional | `array` |
| `min_price` | `query` | ❌ Opsional | `string` |
| `max_price` | `query` | ❌ Opsional | `string` |
| `sort` | `query` | ❌ Opsional | `string` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🟢 `GET` /stok/public/popular
> **Public Get Popular Items**

---

### 🟢 `GET` /stok/public/detail/{stock_uuid}
> **Public Get Stock Detail**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `stock_uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /stok/public/detail/slug/{slug}
> **Public Get Stock Detail By Slug**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `slug` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /stok/public/recommendations/{stock_uuid}
> **Get Recommendations**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `stock_uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /stok/public/recommendations/slug/{slug}
> **Get Recommendations By Slug**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `slug` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /stok/public/megamenu-collections
> **Get Megamenu Collections**

---

### 🟢 `GET` /stok/public/brand-showcase
> **Get Brand Showcase**

---

### 🟢 `GET` /stok/public/autocomplete
> **Get Autocomplete**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `q` | `query` | ✅ Ya | `string` |
| `type` | `query` | ❌ Opsional | `string` |

---

### 🟢 `GET` /stok/public/trending-searches
> **Get Trending Searches**

---

### ⚪ `PATCH` /stok/admin/update/{stock_uuid}
> **Admin Update Stock**

Update sebagian atau seluruh field stock.

Aturan:
- Hanya field yang dikirim yang diupdate (partial update).
- Jika `images` dikirim (file baru), gambar lama DIHAPUS dan diganti.
- Jika `images` tidak dikirim / kosong, gambar lama TETAP.
- `online_price` dihitung otomatis jika `original_price` dan
  `discount_percentage` dikirim bersamaan.
- `is_active` dikirim sebagai string "true" / "false" karena multipart.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `stock_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).

---

### 🔴 `DELETE` /stok/admin/delete/{stock_uuid}
> **Admin Delete Stock**

Hapus produk.

Mode:
- **Soft delete** (default, `hard=false`):
  Set `is_active = False`. Data tetap di DB, bisa dipulihkan.
  Cocok untuk produk yang mungkin dijual kembali di masa depan.

- **Hard delete** (`hard=true`):
  Hapus permanen dari database + hapus semua aset gambar dari CDN (R2/S3).
  Tidak bisa dibatalkan. Gunakan dengan hati-hati.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `stock_uuid` | `path` | ✅ Ya | `string` |
| `hard` | `query` | ❌ Opsional | `boolean` |

---

### 🟢 `GET` /stok/admin/coupon
> **Admin Get Coupons**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `include_inactive` | `query` | ❌ Opsional | `boolean` |
| `page` | `query` | ❌ Opsional | `integer` |
| `size` | `query` | ❌ Opsional | `integer` |

---

### 🔵 `POST` /stok/admin/coupon
> **Admin Create Coupon**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CouponCreateRequest`**

---

### ⚪ `PATCH` /stok/admin/coupon/{code}
> **Admin Update Coupon**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `code` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`CouponUpdateRequest`**

---

### 🔴 `DELETE` /stok/admin/coupon/{code}
> **Admin Delete Coupon**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `code` | `path` | ✅ Ya | `string` |
| `hard` | `query` | ❌ Opsional | `boolean` |

---

## 🏷️ Tag: User

### 🔵 `POST` /auth/user/auth/register
> **Registrasi akun baru**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`UserCreate`**

---

### 🟢 `GET` /auth/user/auth/verify-email
> **Verifikasi email via link**

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `token` | `query` | ✅ Ya | `string` |

---

### 🔵 `POST` /auth/user/auth/resend-verification
> **Kirim ulang email verifikasi**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`EmailRequest`**

---

### 🔵 `POST` /auth/user/auth/login
> **Login dengan email & password**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`UserLogin`**

---

### 🔵 `POST` /auth/user/auth/google
> **Login atau register via Google**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`GoogleAuthRequest`**

---

### 🔵 `POST` /auth/user/auth/refresh
> **Dapatkan access token baru via refresh token**

---

### 🔵 `POST` /auth/user/auth/logout
> **Logout & revoke token**

---

### 🔵 `POST` /auth/user/auth/forgot-password
> **Request link reset password**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`EmailRequest`**

---

### 🔵 `POST` /auth/user/auth/reset-password
> **Submit password baru**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ResetPasswordRequest`**

---

### 🔵 `POST` /auth/user/users/me/change-password
> **Ganti password (user yang sudah login)**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`ChangePasswordRequest`**

---

### 🟢 `GET` /auth/user/users/me
> **Profil user yang sedang login**

---

### 🔴 `DELETE` /auth/user/users/me
> **Hapus akun permanen**

---

### ⚪ `PATCH` /auth/user/users/me
> **Update profil**

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`UserProfileUpdate`**

---

### 🟢 `GET` /auth/user/users/all
> **[Admin] Daftar semua user**

---

## 🏷️ Tag: Whitlish

### ⚪ `PATCH` /wishlist/{wishlist_uuid}
> **Update Wishlist Item**

Mengupdate informasi tambahan pada item wishlist (seperti notes).

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `wishlist_uuid` | `path` | ✅ Ya | `string` |

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`WishlistUpdateRequest`**

---

### 🔴 `DELETE` /wishlist/{wishlist_uuid}
> **Delete Wishlist Item**

Menghapus barang dari wishlist.

**📥 Parameters:**
| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |
|---|---|---|---|
| `wishlist_uuid` | `path` | ✅ Ya | `string` |

---

### 🟢 `GET` /wishlist
> **Get My Wishlist**

Melihat daftar seluruh wishlist user.

---

### 🔵 `POST` /wishlist
> **Add Item To Wishlist**

Menambahkan barang ke wishlist user.

**📤 Request Body (Payload):**
- Membutuhkan `JSON` dengan struktur skema: **`WishlistAddRequest`**

---
