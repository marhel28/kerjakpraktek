# UML Sequence Diagram - Penanganan Validasi Jasa oleh Admin

```mermaid
sequenceDiagram
    autonumber
    
    actor Admin
    participant AdminUI as Dashboard Admin (Frontend)
    participant API as API Backend (FastAPI)
    participant DB as Basis Data (PostgreSQL)
    participant Realtime as WebSocket + Redis pub/sub (FastAPI)
    participant App as Aplikasi Pengguna & Teknisi
    
    Admin->>AdminUI: Melihat daftar pesanan jasa baru
    Admin->>AdminUI: Menyetujui pesanan, menentukan Jadwal & memilih Teknisi
    AdminUI->>API: Mengirim Data Persetujuan (Validasi)
    
    API->>DB: Memeriksa Bentrok Jadwal & Ketersediaan Teknisi
    
    alt Jadwal Bentrok / Teknisi Tidak Tersedia
        DB-->>API: Status Gagal (Slot Terisi)
        API-->>AdminUI: Mengembalikan Pesan Error "Jadwal Penuh"
        AdminUI-->>Admin: Menampilkan Peringatan Gagal
    else Jadwal Tersedia
        API->>DB: Memperbarui Status Pesanan menjadi "Disetujui"
        API->>DB: Mengaitkan Data Teknisi ke Pesanan (Assignment)
        DB-->>API: Konfirmasi Pembaruan Berhasil
        
        API->>DB: Memasukkan Rekaman Notifikasi ke tabel `notification`
        Note right of Realtime: Service publish ke Redis pub/sub.<br/>Tiap worker API meneruskan ke<br/>socket user yang terhubung.
        Realtime-->>App: Mendorong Peringatan (Push Notification) ke Layar Pengguna & Teknisi
        
        API-->>AdminUI: Mengembalikan Respon Sukses
        AdminUI-->>Admin: Menampilkan Pesan "Berhasil Disetujui" & Memperbarui Daftar
    end
```
