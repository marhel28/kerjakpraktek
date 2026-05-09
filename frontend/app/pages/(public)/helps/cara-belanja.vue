<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900 selection:bg-green-500 selection:text-white pb-24">
    
    <div class="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2 text-sm">
          <NuxtLink to="/" class="text-gray-500 hover:text-green-600 transition-colors flex items-center gap-1">
            <UIcon name="i-lucide-home" class="w-4 h-4" /> Beranda
          </NuxtLink>
          <UIcon name="i-lucide-chevron-right" class="w-4 h-4 text-gray-300" />
          <span class="font-bold text-gray-900">Panduan Transaksi</span>
        </div>
      </div>
    </div>

    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-16">
      
      <div class="text-center mb-12 animate-fade-in-up">
        <h1 class="text-3xl md:text-4xl font-black uppercase tracking-tight mb-4">
          Cara Transaksi di <span class="text-green-600">Pasar CCTV</span>
        </h1>
        <p class="text-sm md:text-base text-gray-500 max-w-2xl mx-auto leading-relaxed">
          Sistem kami dirancang untuk memudahkan Anda. Apakah Anda ingin membeli perangkat saja atau sekalian memesan jasa instalasi? Pilih panduannya di bawah ini.
        </p>
      </div>

      <div class="flex justify-center mb-16 animate-fade-in-up" style="animation-delay: 100ms;">
        <div class="inline-flex bg-white border border-gray-200 p-1.5 rounded-2xl shadow-sm">
          <button 
            @click="activeTab = 'barang'"
            class="relative flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold uppercase tracking-wider transition-all duration-300"
            :class="activeTab === 'barang' ? 'text-white shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'"
          >
            <div v-if="activeTab === 'barang'" class="absolute inset-0 bg-green-500 rounded-xl z-0"></div>
            <UIcon name="i-lucide-shopping-bag" class="w-5 h-5 relative z-10" />
            <span class="relative z-10">Beli Perangkat</span>
          </button>
          
          <button 
            @click="activeTab = 'jasa'"
            class="relative flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold uppercase tracking-wider transition-all duration-300"
            :class="activeTab === 'jasa' ? 'text-white shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'"
          >
            <div v-if="activeTab === 'jasa'" class="absolute inset-0 bg-black rounded-xl z-0"></div>
            <UIcon name="i-lucide-wrench" class="w-5 h-5 relative z-10" />
            <span class="relative z-10">Booking Jasa</span>
          </button>
        </div>
      </div>

      <div class="relative">
        <div class="hidden md:block absolute left-1/2 top-0 bottom-0 w-0.5 bg-gray-200 -translate-x-1/2"></div>

        <Transition name="fade-slide" mode="out-in">
          
          <div v-if="activeTab === 'barang'" :key="'barang'" class="space-y-8 md:space-y-12 relative z-10">
            <div 
              v-for="(step, index) in barangSteps" :key="index"
              class="flex flex-col md:flex-row items-center justify-between w-full group animate-fade-in-up"
              :style="{ animationDelay: `${index * 150}ms` }"
            >
              <div class="w-full md:w-[45%] order-2" :class="index % 2 === 0 ? 'md:order-1 md:text-right' : 'md:order-3 md:text-left'">
                <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl hover:border-green-200 transition-all duration-300 group-hover:-translate-y-1">
                  <div class="w-12 h-12 rounded-xl mb-4 flex items-center justify-center" :class="index % 2 === 0 ? 'bg-green-50 text-green-600 md:ml-auto' : 'bg-green-50 text-green-600'">
                    <UIcon :name="step.icon" class="w-6 h-6" />
                  </div>
                  <h3 class="text-lg font-black uppercase tracking-tight mb-2">{{ step.title }}</h3>
                  <p class="text-sm text-gray-500 leading-relaxed">{{ step.desc }}</p>
                </div>
              </div>

              <div class="order-1 md:order-2 w-10 h-10 rounded-full bg-white border-4 border-gray-50 shadow-md flex items-center justify-center font-black text-sm z-10 my-4 md:my-0 transition-colors duration-300 group-hover:bg-green-500 group-hover:text-white group-hover:border-green-100">
                {{ index + 1 }}
              </div>
              
              <div class="hidden md:block w-[45%] order-3" :class="index % 2 === 0 ? '' : 'md:order-1'"></div>
            </div>
          </div>

          <div v-else :key="'jasa'" class="space-y-8 md:space-y-12 relative z-10">
            <div 
              v-for="(step, index) in jasaSteps" :key="index"
              class="flex flex-col md:flex-row items-center justify-between w-full group animate-fade-in-up"
              :style="{ animationDelay: `${index * 150}ms` }"
            >
              <div class="w-full md:w-[45%] order-2" :class="index % 2 === 0 ? 'md:order-1 md:text-right' : 'md:order-3 md:text-left'">
                <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl hover:border-gray-300 transition-all duration-300 group-hover:-translate-y-1">
                  <div class="w-12 h-12 rounded-xl mb-4 flex items-center justify-center" :class="index % 2 === 0 ? 'bg-gray-100 text-black md:ml-auto' : 'bg-gray-100 text-black'">
                    <UIcon :name="step.icon" class="w-6 h-6" />
                  </div>
                  <h3 class="text-lg font-black uppercase tracking-tight mb-2">{{ step.title }}</h3>
                  <p class="text-sm text-gray-500 leading-relaxed">{{ step.desc }}</p>
                </div>
              </div>

              <div class="order-1 md:order-2 w-10 h-10 rounded-full bg-white border-4 border-gray-50 shadow-md flex items-center justify-center font-black text-sm z-10 my-4 md:my-0 transition-colors duration-300 group-hover:bg-black group-hover:text-white group-hover:border-gray-200">
                {{ index + 1 }}
              </div>
              
              <div class="hidden md:block w-[45%] order-3" :class="index % 2 === 0 ? '' : 'md:order-1'"></div>
            </div>
          </div>

        </Transition>
      </div>

      <div class="mt-32">
        <div class="text-center mb-10">
          <h2 class="text-2xl md:text-3xl font-black uppercase tracking-tight">Pertanyaan Umum (FAQ)</h2>
          <div class="w-16 h-1 bg-green-500 mx-auto mt-4 rounded-full"></div>
        </div>

        <div class="max-w-3xl mx-auto space-y-3">
          <div 
            v-for="(faq, i) in activeFaqs" :key="i"
            class="bg-white border border-gray-200 rounded-xl overflow-hidden transition-all duration-300 hover:shadow-md"
          >
            <button 
              class="w-full flex items-center justify-between p-5 md:p-6 text-left focus:outline-none"
              @click="toggleFaq(i)"
            >
              <span class="font-bold text-gray-900 pr-4">{{ faq.q }}</span>
              <div class="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center flex-shrink-0 transition-transform duration-300" :class="openFaq === i ? 'rotate-180 bg-green-50 text-green-600' : 'text-gray-400'">
                <UIcon name="i-lucide-chevron-down" class="w-5 h-5" />
              </div>
            </button>
            <div 
              class="px-5 md:px-6 overflow-hidden transition-all duration-300 ease-in-out bg-gray-50"
              :class="openFaq === i ? 'max-h-40 py-5 border-t border-gray-100' : 'max-h-0 py-0'"
            >
              <p class="text-sm text-gray-600 leading-relaxed">
                {{ faq.a }}
              </p>
            </div>
          </div>
        </div>
      </div>

    </main>

    <div class="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-gray-200 p-4 pb-safe z-50 shadow-[0_-10px_30px_rgba(0,0,0,0.05)]">
      <div class="max-w-5xl mx-auto flex items-center justify-between gap-4">
        <div class="hidden sm:block">
          <p class="text-xs font-black uppercase tracking-widest text-gray-900 mb-0.5">Sudah Paham Caranya?</p>
          <p class="text-[10px] font-semibold text-gray-500">Mulai penuhi kebutuhan keamanan Anda.</p>
        </div>
        
        <div class="flex flex-1 sm:flex-none gap-3 w-full sm:w-auto">
          <NuxtLink 
            v-if="activeTab === 'barang'"
            to="/products"
            class="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-green-500 hover:bg-green-600 text-white px-8 py-3.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all active:scale-95 shadow-lg shadow-green-500/20"
          >
            <UIcon name="i-lucide-shopping-cart" class="w-4 h-4" />
            Mulai Belanja
          </NuxtLink>
          
          <NuxtLink 
            v-else
            to="/service/booking"
            class="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white px-8 py-3.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all active:scale-95 shadow-lg shadow-black/20"
          >
            <UIcon name="i-lucide-calendar-plus" class="w-4 h-4" />
            Booking Teknisi
          </NuxtLink>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

useSeoMeta({
  title: 'Panduan Belanja & Booking - Pasar CCTV',
  description: 'Langkah mudah bertransaksi aman di Pasar CCTV. Temukan panduan membeli produk dan memesan jasa instalasi profesional.',
})

const activeTab = ref<'barang' | 'jasa'>('barang')
const openFaq = ref<number | null>(0)

const toggleFaq = (index: number) => {
  openFaq.value = openFaq.value === index ? null : index
}

// ─── DATA: FLOW BELI BARANG ───
const barangSteps = [
  {
    icon: 'i-lucide-search',
    title: 'Cari & Pilih Produk',
    desc: 'Gunakan kolom pencarian atau telusuri kategori untuk menemukan kamera, NVR, kabel, atau aksesoris CCTV yang Anda butuhkan.'
  },
  {
    icon: 'i-lucide-shopping-cart',
    title: 'Masukkan Keranjang',
    desc: 'Klik tombol "Keranjang" untuk menyimpan barang, atau klik "Beli Langsung" untuk langsung menuju ke halaman pembayaran.'
  },
  {
    icon: 'i-lucide-map-pin',
    title: 'Isi Alamat & Kurir',
    desc: 'Masukkan alamat pengiriman lengkap Anda. Sistem kami akan otomatis menampilkan pilihan kurir dan kalkulasi ongkos kirim.'
  },
  {
    icon: 'i-lucide-credit-card',
    title: 'Pilih Metode Pembayaran',
    desc: 'Kami mendukung Transfer Bank (VA), E-Wallet, hingga Kartu Kredit melalui sistem payment gateway (Midtrans) yang dijamin aman 100%.'
  },
  {
    icon: 'i-lucide-package-check',
    title: 'Pantau Resi & Terima Barang',
    desc: 'Nomor resi akan otomatis masuk ke dashboard Anda setelah barang dikirim. Pesanan selesai saat barang Anda terima.'
  }
]

// ─── DATA: FLOW PESAN JASA ───
const jasaSteps = [
  {
    icon: 'i-lucide-settings-2',
    title: 'Konfigurasi Sistem',
    desc: 'Masuk ke menu Service Booking. Pilih mau pasang baru atau perbaikan. Tentukan jumlah titik kamera dan brand perangkat yang Anda inginkan.'
  },
  {
    icon: 'i-lucide-calendar-clock',
    title: 'Pilih Waktu Kedatangan',
    desc: 'Sistem kami akan menampilkan slot teknisi yang tersedia. Pilih tanggal dan jam (Pagi/Siang/Sore) sesuai kenyamanan Anda.'
  },
  {
    icon: 'i-lucide-map-pinned',
    title: 'Validasi Lokasi',
    desc: 'Masukkan alamat lengkap. Sistem otomatis menghitung jarak dari Hub kami untuk menentukan biaya akomodasi teknisi secara transparan.'
  },
  {
    icon: 'i-lucide-wallet',
    title: 'Bayar DP (Down Payment)',
    desc: 'Lakukan pembayaran DP (biasanya 30%) untuk mengunci jadwal teknisi. Sisa pembayaran bisa dilunasi setelah pekerjaan selesai.'
  },
  {
    icon: 'i-lucide-shield-check',
    title: 'Instalasi & Garansi',
    desc: 'Teknisi profesional kami akan datang, memasang sistem dengan rapi, melakukan setting ke HP Anda, dan memberikan garansi resmi.'
  }
]

// ─── DATA: FAQS ───
const faqsBarang = [
  { q: 'Apakah barang yang dijual bergaransi resmi?', a: 'Ya! Semua perangkat seperti Dahua, Hikvision, Ezviz, dan Imou yang kami jual memiliki garansi resmi pabrik mulai dari 1 hingga 3 tahun.' },
  { q: 'Bagaimana cara melacak pesanan saya?', a: 'Anda bisa masuk ke menu "Status Pesanan" atau Dashboard Akun Anda. Nomor resi JNT/JNE/Kurir Lainnya akan terupdate otomatis di sana.' },
  { q: 'Apakah aman bayar transfer?', a: 'Sangat aman. Pembayaran diproses otomatis oleh Midtrans. Uang Anda aman dan invoice akan langsung diterbitkan secara digital.' }
]

const faqsJasa = [
  { q: 'Apakah biaya transport teknisi sudah termasuk?', a: 'Biaya transport dihitung terpisah secara otomatis oleh sistem saat Anda memasukkan alamat, sehingga sangat transparan tanpa biaya siluman di lokasi.' },
  { q: 'Bagaimana jika saat teknisi datang butuh kabel tambahan?', a: 'Jika di lapangan ternyata butuh material tambahan di luar paket (misal: kabel kurang panjang), teknisi akan menginfokan harganya terlebih dahulu untuk persetujuan Anda.' },
  { q: 'Apakah saya bisa mengubah jadwal booking?', a: 'Bisa. Silakan hubungi Customer Service kami via WhatsApp maksimal H-1 sebelum jadwal kedatangan teknisi yang telah Anda pilih.' }
]

const activeFaqs = computed(() => activeTab.value === 'barang' ? faqsBarang : faqsJasa)
</script>

<style scoped>
.pb-safe { padding-bottom: calc(1rem + env(safe-area-inset-bottom)); }

/* Transisi Halus antar Tab */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.fade-slide-enter-from { opacity: 0; transform: translateY(10px) scale(0.98); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-10px) scale(0.98); }

/* Animasi Muncul Per Step */
.animate-fade-in-up {
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>