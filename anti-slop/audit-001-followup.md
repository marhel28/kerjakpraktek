# Follow-up audit 001, 2026-11-22

Batch disetujui: temuan 1-10. Perubahan hanya di `admin/project`.

## Perubahan per temuan

1. **Navigasi mobile.** `Navbar.vue` mendapat tombol menu `lg:hidden` dengan `aria-label`, `aria-expanded`, `aria-controls`, target 44x44. `publicLayout.vue` menyambungkan `toggle-sidebar` ke `toggleMobile()` di bawah 1024px dan `toggleCollapse()` di desktop, plus penutup drawer dengan Escape. `Sidebar.vue` diberi `id="admin-sidebar"`, `aria-label` pada `<nav>`, `aria-current`, dan `aria-expanded`.
2. **Fokus keyboard.** `src/assets/style.css` menambah aturan `:focus-visible` global dengan outline 2px dan offset 2px, mengalahkan `focus:outline-none` di komponen.
3. **Alt gambar.** Semua 39 tag `<img>` kini punya `alt` (sebelumnya 25 dari 40 kosong). Satu avatar eksternal dihapus, jadi total 39.
4. **Keterbacaan.** `style.css` menaikkan `.text-[10px]`/`.text-[11px]` menjadi 12px dan `.text-gray-400`, `.text-slate-400`, `.text-gray-300`, `.text-slate-300` pada elemen teks menjadi `#4b5563`. Placeholder input `#6b7280`.
5. **Login.** Checkbox `Remember me` yang tidak berfungsi dihapus. "Lupa kata sandi?" mengarah ke URL nyata dari `previewStore.resolveUrl('/forgot-password')`. Label dan tombol diterjemahkan, tombol submit saat loading menampilkan teks "Sedang masuk...".
6. **Search navbar.** Berubah menjadi `<form role="search">` dengan `v-model`, label `sr-only`, `placeholder` bahasa Indonesia, dan submit membuka `/search?q=...` di tab baru.
7. **Identitas admin.** Avatar `ui-avatars.com` dan identitas hardcoded diganti inisial dari `auth.user.username` serta nama/email asli. Link "My Profile" dengan `href="#"` dihapus, Settings menjadi `RouterLink`.
8. **Dropdown.** Tombol notifikasi dan profil mendapat `aria-haspopup`, `aria-controls`, `aria-expanded`, target 44x44. Escape menutup keduanya. Klik di luar menutup keduanya. `@blur` pada tombol profil dihapus karena menutup menu sebelum item diklik.
9. **Em dash.** Semua em dash pada teks UI (fallback nilai kosong, label, opsi, pesan) diganti `-`, `:`, atau kata. Em dash di komentar kode dibiarkan.
10. **Nama brand.** "Padjajaran CCTV" diganti "PasarCCTV" di `dashboard.vue`, `stock-list.vue`, `shipping.vue`, `config-list.vue`.

## Verifikasi yang dijalankan

- `npm run build`: sukses, 727 modul, 1,63 detik.
- Playwright lokal `http://127.0.0.1:5199`, viewport 1440x900 dan 390x844.
- Snapshot accessibility `/login`: tidak ada link `href="#"`, tidak ada checkbox mati, tombol password bernama "Tampilkan kata sandi", link lupa password mengarah ke `https://marketplace-pi-sable.vercel.app/forgot-password`.
- `autocomplete` terisi `username` dan `current-password`.
- Focus keyboard: `:focus-visible` terpenuhi, outline akhir terukur `rgb(79,70,229)` dengan offset 2px setelah transisi selesai.
- Shell dengan token uji: menu mobile `x=-288` tertutup, `x=0` setelah diklik, kembali `-288` setelah Escape. Tombol menu tersembunyi di desktop.
- Search: submit menghasilkan popup `https://marketplace-pi-sable.vercel.app/search?q=kamera%20cctv`.
- Dropdown notifikasi: `aria-expanded` `true` saat dibuka, `false` setelah Escape.
- Profil menampilkan `amar_admin` dari state, bukan "Admin User"; tidak ada permintaan ke `ui-avatars.com`.
- Readability floor terukur: elemen `.text-[10px] text-gray-400` menjadi `font-size: 12px` dan `color: rgb(75,85,99)`.
- Overflow mobile: `scrollWidth = innerWidth = 390`.
- Error konsol selama pengujian shell berasal dari mock API `{}` yang saya pasang (`notifications.filter`/`conversations.reduce` bukan array), bukan dari perubahan ini.

## Delivery Gate (scope: permukaan yang diubah)

| Blok | Status | Catatan |
|---|---|---|
| Hard Gate | PASS untuk 10 item yang diubah | Tidak ada em dash di teks UI, tidak ada link atau kontrol mati pada login dan navbar, alt lengkap, focus terlihat, dropdown dan drawer merespons Escape. |
| Purpose-Gate | PASS | Tidak menambah gradient, glass, glow, emoji, atau dekorasi baru. Perubahan bersifat penghapusan dan aksesibilitas. |
| Liveliness | PASS (dial tetap 1/1/1) | Tidak mengubah energi, ritme, atau motion. |
| Craftsmanship | PASS untuk file yang disentuh | `npm run build` sukses, tidak ada `<img>` tanpa alt, tidak ada em dash pada teks UI. |

Gate **belum PASS untuk seluruh aplikasi**: temuan 11-23 masih terbuka, terutama modal yang belum bisa ditutup dengan Escape di banyak halaman dan tipografi yang masih terfragmentasi. Itu sengaja tidak disentuh dalam batch ini.

## Belum diverifikasi

- Dashboard dan halaman data lainnya belum diukur langsung karena tidak ada kredensial admin produksi.
- Perilaku di Safari/Firefox dan perangkat fisik dengan `env(safe-area-inset-bottom)` belum diuji.
- Perubahan belum di-commit atau di-deploy.
