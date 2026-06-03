# Panduan Pengelolaan Popup, Modal & Toast Dashboard Admin

Dokumen ini menjelaskan standar implementasi dan panduan interaksi untuk jendela sembul (Popup), dialog konfirmasi (Modal), dan pemberitahuan mengambang (Toast) di dalam dasbor Admin PasarCCTV.

## 1. Filosofi Desain (UX Guidelines)
Untuk memberikan pengalaman pengguna yang profesional, ramah sentuhan (*touch-friendly*), dan berkinerja tinggi, ikuti aturan berikut:
* **Hindari `alert()` Bawaan Peramban**: Jangan pernah menggunakan fungsi bawaan `alert()` karena memutus fokus kerja pengguna secara kasar dan terlihat amatir.
* **Hindari Pergeseran Tata Letak (*Layout Shifting*)**: Jangan gunakan kotak pesan statis yang muncul di tengah konten utama dan menggeser elemen lainnya ke bawah. Gunakan Toast overlay.
* **Gunakan Animasi Lembut**: Dialog modal harus muncul dengan transisi perlahan pada lapisan latar belakang (*backdrop blur*) dan efek perbesaran pegas (*spring scaling*) pada kartu konten.

---

## 2. Pola Implementasi Modal (Custom Modal Pattern)

Setiap jendela modal harus menggunakan komponen `<Transition>` dengan nama `modal-fade` dan memisahkan transisi lapisan latar belakang (*backdrop*) dari kartu modal utama (`modal-card`).

### Contoh Struktur HTML Vue:
```html
<Transition name="modal-fade">
  <div v-if="isModalOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
    <!-- Lapisan Latar Belakang (Backdrop) -->
    <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeModal"></div>

    <!-- Kartu Konten Modal (Modal Card) -->
    <div class="modal-card relative bg-white rounded-2xl shadow-xl w-full max-w-2xl border border-gray-100 flex flex-col overflow-hidden max-h-[90vh] z-10">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
        <h3 class="text-lg font-semibold text-gray-900">Judul Modal</h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600 focus:outline-none">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Konten Form / Isi -->
      <div class="p-6 overflow-y-auto">
        <!-- Input Form di sini -->
      </div>

      <!-- Aksi / Tombol Bawah -->
      <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-end space-x-3 rounded-b-2xl">
        <button type="button" @click="closeModal" class="px-4 py-2.5 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 active:scale-95 transition-all">
          Batal
        </button>
        <button @click="confirmAction" class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 active:scale-95 transition-all">
          Konfirmasi
        </button>
      </div>
    </div>
  </div>
</Transition>
```

### Animasi CSS (Scoped Styles):
```css
<style scoped>
/* Modal Animation */
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.25s ease;
}
.modal-fade-enter-active .modal-card, .modal-fade-leave-active .modal-card {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .modal-card {
  transform: scale(0.95) translateY(12px);
  opacity: 0;
}
.modal-fade-leave-to .modal-card {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}
</style>
```

---

## 3. Pola Pemberitahuan Toast (Reactive Toast Pattern)

Untuk memunculkan pesan sukses atau gagal tanpa mengganggu alur kerja admin, terapkan modul Toast reaktif secara lokal pada halaman terkait.

### Contoh Logika Setup (Vue Script):
```javascript
import { reactive } from 'vue'

const toast = reactive({ show: false, message: '', type: 'success' })
let toastTimer = null

const showToast = (message, type = 'success') => {
  clearTimeout(toastTimer)
  toast.message = message
  toast.type = type
  toast.show = true
  toastTimer = setTimeout(() => {
    toast.show = false
  }, 4000)
}
```

### Template HTML Toast:
```html
<Transition name="toast">
  <div v-if="toast.show" :class="[
    'fixed bottom-6 right-6 z-[10000] flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-xl text-sm font-semibold transition-all border font-sans',
    toast.type === 'success' ? 'bg-gray-900 border-gray-800 text-white' : 'bg-red-50 border-red-200 text-red-700'
  ]">
    <div :class="['w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold', toast.type === 'success' ? 'bg-indigo-500 text-white' : 'bg-red-200 text-red-700']">
      {{ toast.type === 'success' ? '✓' : '✕' }}
    </div>
    <span>{{ toast.message }}</span>
  </div>
</Transition>
```

### Animasi CSS Toast:
```css
<style scoped>
/* Toast Animation */
.toast-enter-active, .toast-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}
</style>
```
