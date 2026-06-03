# Dokumentasi Pusat PasarCCTV

Selamat datang di repositori dokumentasi teknis PasarCCTV. Proyek ini adalah platform Marketplace B2B terpadu dengan arsitektur *microservice-ready* yang mengutamakan skalabilitas, performa tinggi, dan pengalaman pengguna (*user experience*) kelas produksi.

## Struktur Repositori Dokumentasi

Sesuai dengan standar industri, dokumentasi ini dibagi menjadi beberapa pilar utama berdasarkan lapisan arsitektur aplikasi (Frontend, Backend, dan Admin).

| Lapisan | Direktori | Deskripsi |
|---|---|---|
| **Sistem & Arsitektur** | [`docs/architecture/system-overview.md`](architecture/system-overview.md) | Panduan C4 Model, Database ERD, Topologi, dan UML Alur Kerja |
| **Frontend** | [`docs/frontend/README.md`](frontend/README.md) | Aplikasi Web Publik (Nuxt 4, Vue 3, Pinia, Tailwind v4) |
| **Backend** | [`docs/backend/README.md`](backend/README.md) | API dan Logika Inti (FastAPI, PostgreSQL, Elasticsearch) |
| **Admin** | [`docs/admin/README.md`](admin/README.md) | Dashboard Manajemen Operasional (Vue, Vite) |

## Tentang Diátaxis
Dokumentasi teknis di dalam proyek ini diatur berdasarkan kerangka kerja [Diátaxis](https://diataxis.fr/), yang berarti Anda akan menemukan format berikut:
* **Tutorials**: Panduan terstruktur untuk pembelajaran *onboarding* staf atau pengembang baru.
* **How-To Guides**: Panduan *step-by-step* untuk memecahkan masalah atau melakukan tugas spesifik.
* **Reference**: Informasi teknis akurat (seperti skema API, nama variabel, struktur ERD).
* **Explanation**: Latar belakang teori, pengambilan keputusan arsitektur, dan alasan desain.
