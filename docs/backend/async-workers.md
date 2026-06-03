# Pekerja Latar Belakang Asinkron (Async Background Workers)

Agar API `FastAPI` kita tetap memberikan waktu respon di bawah 100 milidetik, semua operasi komputasi berat, penjadwalan, atau layanan komunikasi I/O eksternal harus dilempar ke sistem **Antrean Pekerja (Message Queue)** menggunakan **Celery**.

## Alur Kerja (Pub/Sub Workflow)
Sistem ini mematuhi arsitektur berbasis pesan (*Message-Driven Architecture*):
1. **Producer**: *Router* FastAPI menerima *request* mutasi pengguna (contoh: *Checkout*), lalu ia memanggil fungsi Celery `.delay()`, dan langsung mengembalikan HTTP `200 OK` secara serentak ke pengguna.
2. **Broker**: Perintah/Pesan tersebut ditampung secara persisten di dalam antrean memori oleh DragonflyDB (yang berkonfigurasi sebagai *Redis Broker*).
3. **Consumer**: Mesin *Worker* Celery terpisah, yang terus memantau *broker* setiap milidetik, akan menarik tugas tersebut lalu mengeksekusinya tanpa campur tangan utas peladen *web* utama.

## Daftar Tugas Terdaftar (Registered Queues)
Beberapa ruang tugas (*tasks*) utama yang dioperasikan pada infrastruktur ini meliputi:
1. **Pengiriman Email Resi**: Mengonversi transaksi menjadi PDF dan mengirimkannya via penyedia SMTP.
2. **Sinkronisasi Elasticsearch**: Memperbarui tabel mesin pencarian sesaat setelah *Dashboard Admin* melakukan pembaruan harga atau penambahan katalog.
3. **Reconciliation Stok**: Sebuah jadwal *Cron-job* yang membersihkan reservasi stok gantung (*Stock Hold*) secara otomatis, jika tagihan tidak dibayar melebihi waktu tenggang/kadaluarsa tagihan.
4. **Jaringan Eksternal**: Menembakkan log aktivitas ke analitik, atau sinkronisasi pembaruan ke penyedia pihak ketiga (misal: kurir pengiriman).
