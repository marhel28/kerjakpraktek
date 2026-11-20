<script setup lang="ts">
import { ref, computed } from 'vue'

useSeoMeta({
  title: 'Pusat Bantuan & Kontak Layanan — PasarCCTV',
  description: 'Hubungi tim sales dan teknisi resmi PasarCCTV. Bantuan pemesanan CCTV, jadwal survei instalasi lapangan, hingga klaim garansi.',
  ogTitle: 'Pusat Bantuan & Layanan Pelanggan PasarCCTV',
  ogDescription: 'Layanan WhatsApp Sales, Teknisi Resmi, Showroom Bogor, dan Workshop Bandung Cimahi.',
})

// ── Quick issue cards ala Amazon Customer Service Hub ──────────────
const quickHelpCards = [
  {
    title: 'Lacak Status Pesanan',
    desc: 'Periksa pengiriman paket barang atau status pesanan aktif',
    to: '/helps/shipping',
    icon: 'i-lucide-package-search'
  },
  {
    title: 'Jadwalkan Teknisi',
    desc: 'Survei lokasi gratis & booking jasa instalasi profesional',
    to: '/services/booking',
    icon: 'i-lucide-calendar-check-2'
  },
  {
    title: 'Panduan & Cara Belanja',
    desc: 'Langkah pemesanan, metode bayar, dan garansi resmi',
    to: '/helps/cara-belanja',
    icon: 'i-lucide-book-open'
  },
  {
    title: 'Lokasi Toko & Workshop',
    desc: 'Alamat showroom fisik Bogor & workshop teknisi Bandung',
    to: '/store-locator',
    icon: 'i-lucide-store'
  }
]

// ── Jalur Kontak Langsung ──────────────────────────────────────────
const waSales = {
  name: 'WhatsApp Sales & Pengadaan Perangkat',
  phoneDisplay: '+62 821-1777-9003',
  phoneNumber: '6282117779003',
  badge: 'Respon Cepat',
  desc: 'Konsultasi katalog resmi Dahua, Hikvision, Ezviz, Tiandy, Imou, cek stok real-time, dan penawaran retail/B2B.',
  defaultText: 'Halo PasarCCTV, saya ingin konsultasi pemilihan produk CCTV dan ketersediaan stok.',
  icon: 'i-lucide-shopping-cart'
}

const waSupport = {
  name: 'WhatsApp Teknisi & Instalasi Lapangan',
  phoneDisplay: '+62 822-1882-8108',
  phoneNumber: '6282218828108',
  badge: 'Divisi Lapangan',
  desc: 'Pemasangan rapi pipa conduit, setting online smartphone (DMSS/Hik-Connect), maintenance, dan klaim garansi.',
  defaultText: 'Halo Tim Teknisi PasarCCTV, saya ingin konsultasi jadwal pemasangan dan survei lokasi.',
  icon: 'i-lucide-wrench'
}

const waSalesLink = computed(() => {
  return `https://wa.me/${waSales.phoneNumber}?text=${encodeURIComponent(waSales.defaultText)}`
})

const waSupportLink = computed(() => {
  return `https://wa.me/${waSupport.phoneNumber}?text=${encodeURIComponent(waSupport.defaultText)}`
})

const additionalContacts = [
  {
    name: 'Email Dukungan Resmi',
    value: 'cs@pasarcctv.com',
    link: 'mailto:cs@pasarcctv.com',
    desc: 'Surat penawaran proyek, tender instansi, dan kerja sama korporat',
    icon: 'i-lucide-mail'
  },
  {
    name: 'Telepon Kantor',
    value: '(022) 8600-9003',
    link: 'tel:02286009003',
    desc: 'Panggilan suara selama jam operasional kerja',
    icon: 'i-lucide-phone'
  }
]

// ── Data Showroom & Workshop ──────────────────────────────────────
const showroomAddress = 'Jl. Tumenggung Wiradireja No.29A, Cimahpar, Bogor Utara, Kota Bogor, Jawa Barat 16155'
const mapsUrl = 'https://www.google.com/maps/search/?api=1&query=-6.5510,106.8185'

const copied = ref(false)
const copyAddress = async () => {
  try {
    await navigator.clipboard.writeText(showroomAddress)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch {
    copied.value = false
  }
}

// ── State Formulir Permintaan Penawaran ───────────────────────────
const form = ref({
  fullName: '',
  whatsapp: '',
  category: 'Pemasangan Baru Rumah / Ruko',
  cameraCount: '2-4 Titik',
  locationCity: '',
  message: '',
})

const formError = ref('')
const isSubmitting = ref(false)
const submitSuccess = ref(false)

const handleFormSubmit = () => {
  formError.value = ''
  if (!form.value.fullName.trim()) {
    formError.value = 'Silakan isi nama lengkap Anda.'
    return
  }
  if (!form.value.whatsapp.trim()) {
    formError.value = 'Nomor WhatsApp wajib diisi untuk konfirmasi estimasi.'
    return
  }

  isSubmitting.value = true

  const textMsg = `Halo Tim PasarCCTV,

Saya ingin konsultasi proyek sistem keamanan:

• Nama: ${form.value.fullName}
• WhatsApp: ${form.value.whatsapp}
• Kebutuhan: ${form.value.category}
• Estimasi Kamera: ${form.value.cameraCount}
• Kota / Lokasi: ${form.value.locationCity || '-'}
• Catatan: ${form.value.message || '-'}

Mohon informasi estimasi biaya dan jadwal survei. Terima kasih.`

  const targetWa = `https://wa.me/${waSupport.phoneNumber}?text=${encodeURIComponent(textMsg)}`

  setTimeout(() => {
    isSubmitting.value = false
    submitSuccess.value = true
    if (typeof window !== 'undefined') {
      window.open(targetWa, '_blank')
    }
  }, 400)
}

// ── FAQ ───────────────────────────────────────────────────────────
const faqs = [
  {
    q: 'Berapa lama estimasi respon customer service?',
    a: 'Chat WhatsApp dijawab dalam rata-rata kurang dari 5 menit selama jam operasional kerja (Senin sampai Sabtu, 08.00 - 17.00 WIB).'
  },
  {
    q: 'Apakah survei lokasi dikenakan biaya?',
    a: 'Survei lokasi wilayah Jabodetabek dan Bandung Raya tidak dikenakan biaya komitmen awal untuk konsultasi rancangan tata letak kamera.'
  },
  {
    q: 'Bagaimana prosedur klaim garansi kamera?',
    a: 'Kirimkan foto nomor nota pembelian ke WhatsApp Teknisi. Unit dengan kendala cacat produksi pada tahun pertama mendapat fasilitas penggantian unit baru.'
  },
  {
    q: 'Apakah bisa datang langsung untuk melihat demo kamera?',
    a: 'Bisa. Showroom kami di Bogor dan workshop Bandung buka Senin hingga Sabtu pukul 08.00 - 17.00 WIB untuk uji coba fitur kamera secara langsung.'
  }
]
</script>

<template>
  <main class="bg-[#F7F8F9] min-h-screen pb-16 font-sans text-gray-900">
    <!-- ══════════════════════════════════════════════════════════
         TOP HEADER (Amazon Customer Service Style + Forest Green)
    ══════════════════════════════════════════════════════════════ -->
    <header class="bg-white border-b border-gray-200 pt-8 pb-10 px-4 sm:px-6 lg:px-8">
      <div class="max-w-6xl mx-auto">
        <!-- Breadcrumb -->
        <nav aria-label="Breadcrumb" class="mb-4 flex items-center gap-2 text-xs font-medium text-gray-500">
          <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
          <span class="text-gray-300">/</span>
          <span class="text-gray-800">Layanan Pelanggan & Kontak</span>
        </nav>

        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#E6F7E9] text-[#03AC0E] border border-[#C8E6CC] mb-3">
              <UIcon name="i-lucide-shield-check" class="w-3.5 h-3.5 shrink-0" />
              <span>Pusat Layanan Resmi PasarCCTV</span>
            </span>
            <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-gray-900">
              Ada yang bisa kami bantu?
            </h1>
            <p class="text-sm text-gray-600 mt-1 max-w-2xl leading-relaxed">
              Pilih bantuan mandiri di bawah ini atau hubungi langsung divisi teknisi dan sales resmi kami.
            </p>
          </div>

          <!-- Operasional Bar Info -->
          <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 text-xs text-gray-700 bg-gray-50 border border-gray-200 p-3.5 rounded-xl self-start md:self-center">
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-clock" class="w-4 h-4 text-[#03AC0E] shrink-0" />
              <span>Senin - Sabtu: <strong class="font-semibold text-gray-900">08.00 - 17.00 WIB</strong></span>
            </div>
            <span class="hidden sm:inline text-gray-300">|</span>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-message-circle" class="w-4 h-4 text-[#03AC0E] shrink-0" />
              <span>Respon WhatsApp: <strong class="font-semibold text-[#03AC0E]">< 5 Menit</strong></span>
            </div>
          </div>
        </div>

        <!-- ── Amazon-Style Problem Solver Grid ────────────────── -->
        <div class="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <NuxtLink
            v-for="item in quickHelpCards"
            :key="item.title"
            :to="item.to"
            class="group bg-white border border-gray-200 hover:border-[#03AC0E] p-4 rounded-xl shadow-xs transition-all hover:shadow-sm flex items-start gap-3.5"
          >
            <div class="w-10 h-10 rounded-lg bg-[#E6F7E9] text-[#03AC0E] flex items-center justify-center shrink-0 group-hover:bg-[#03AC0E] group-hover:text-white transition-colors">
              <UIcon :name="item.icon" class="w-5 h-5" />
            </div>
            <div class="min-w-0 flex-1">
              <h2 class="text-xs font-semibold text-gray-900 group-hover:text-[#03AC0E] transition-colors leading-snug">
                {{ item.title }}
              </h2>
              <p class="text-[11px] text-gray-500 mt-0.5 leading-normal">
                {{ item.desc }}
              </p>
            </div>
            <UIcon name="i-lucide-chevron-right" class="w-4 h-4 text-gray-400 group-hover:text-[#03AC0E] group-hover:translate-x-0.5 transition-all mt-1 shrink-0" />
          </NuxtLink>
        </div>

      </div>
    </header>

    <!-- ══════════════════════════════════════════════════════════
         MAIN CONTENT (Layout Berjenjang & Fungsional)
    ══════════════════════════════════════════════════════════════ -->
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">

      <!-- ── SECTION: 2 KANAL KOMUNIKASI RESMI WHATSAPP ───────── -->
      <section aria-labelledby="direct-channels-heading">
        <div class="flex items-center justify-between mb-3">
          <h2 id="direct-channels-heading" class="text-sm font-bold uppercase tracking-wider text-gray-600">
            Jalur Komunikasi Langsung
          </h2>
          <span class="text-xs text-gray-400">Terhubung langsung ke staf resmi</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- WhatsApp Sales -->
          <div class="bg-white rounded-xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between hover:border-[#03AC0E] transition-colors">
            <div>
              <div class="flex items-center justify-between gap-2 mb-3">
                <div class="flex items-center gap-2.5">
                  <div class="w-9 h-9 rounded-lg bg-[#E6F7E9] text-[#03AC0E] flex items-center justify-center shrink-0">
                    <UIcon name="i-lucide-shopping-cart" class="w-4 h-4" />
                  </div>
                  <div>
                    <h3 class="text-sm font-bold text-gray-900 leading-snug">
                      {{ waSales.name }}
                    </h3>
                    <p class="text-[11px] text-gray-500">Divisi Penjualan & Stok Perangkat</p>
                  </div>
                </div>
                <span class="text-[11px] font-medium bg-[#E6F7E9] text-[#03AC0E] border border-[#C8E6CC] px-2.5 py-0.5 rounded-full shrink-0">
                  {{ waSales.badge }}
                </span>
              </div>
              <p class="text-xs text-gray-600 leading-relaxed mb-4">
                {{ waSales.desc }}
              </p>
            </div>

            <div class="pt-3 border-t border-gray-100 flex items-center justify-between gap-2">
              <div>
                <span class="block text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Nomor WhatsApp</span>
                <span class="text-xs font-bold text-gray-900 font-mono">{{ waSales.phoneDisplay }}</span>
              </div>
              <a
                :href="waSalesLink"
                target="_blank"
                rel="noopener"
                class="inline-flex items-center gap-1.5 text-xs font-medium text-white bg-[#03AC0E] hover:bg-[#028C0B] px-4 py-2 rounded-lg transition-colors shadow-xs"
              >
                <span>Hubungi Sales</span>
                <UIcon name="i-lucide-arrow-right" class="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          <!-- WhatsApp Teknisi -->
          <div class="bg-white rounded-xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between hover:border-gray-400 transition-colors">
            <div>
              <div class="flex items-center justify-between gap-2 mb-3">
                <div class="flex items-center gap-2.5">
                  <div class="w-9 h-9 rounded-lg bg-gray-100 text-gray-800 flex items-center justify-center shrink-0">
                    <UIcon name="i-lucide-wrench" class="w-4 h-4" />
                  </div>
                  <div>
                    <h3 class="text-sm font-bold text-gray-900 leading-snug">
                      {{ waSupport.name }}
                    </h3>
                    <p class="text-[11px] text-gray-500">Divisi Instalasi & Konfigurasi</p>
                  </div>
                </div>
                <span class="text-[11px] font-medium bg-gray-100 text-gray-700 border border-gray-200 px-2.5 py-0.5 rounded-full shrink-0">
                  {{ waSupport.badge }}
                </span>
              </div>
              <p class="text-xs text-gray-600 leading-relaxed mb-4">
                {{ waSupport.desc }}
              </p>
            </div>

            <div class="pt-3 border-t border-gray-100 flex items-center justify-between gap-2">
              <div>
                <span class="block text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Nomor WhatsApp</span>
                <span class="text-xs font-bold text-gray-900 font-mono">{{ waSupport.phoneDisplay }}</span>
              </div>
              <a
                :href="waSupportLink"
                target="_blank"
                rel="noopener"
                class="inline-flex items-center gap-1.5 text-xs font-medium text-white bg-gray-900 hover:bg-gray-800 px-4 py-2 rounded-lg transition-colors shadow-xs"
              >
                <span>Hubungi Teknisi</span>
                <UIcon name="i-lucide-arrow-right" class="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      </section>

      <!-- ── SECTION: FORM ESTIMASI & PUSAT KANTOR FISIK ──────── -->
      <section class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

        <!-- Sisi Kiri: Form Estimasi Proyek (7 Kolom) -->
        <div class="lg:col-span-7 bg-white rounded-xl border border-gray-200 p-6 shadow-xs">
          <div class="flex items-center gap-2 mb-1">
            <UIcon name="i-lucide-file-spreadsheet" class="w-5 h-5 text-[#03AC0E]" />
            <h2 class="text-base font-bold text-gray-900">
              Formulir Permintaan Penawaran & Survei
            </h2>
          </div>
          <p class="text-xs text-gray-500 mb-6">
            Kirim rincian kebutuhan sistem keamanan Anda untuk mendapatkan estimasi cepat dari tim lapangan kami.
          </p>

          <!-- Error Alert -->
          <div v-if="formError" class="mb-4 p-3.5 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center gap-2">
            <UIcon name="i-lucide-alert-circle" class="w-4 h-4 shrink-0 text-red-600" />
            <span>{{ formError }}</span>
          </div>

          <!-- Success Alert -->
          <div v-if="submitSuccess" class="mb-4 p-4 bg-[#E6F7E9] border border-[#C8E6CC] rounded-lg text-xs text-[#03AC0E] flex items-start gap-3">
            <UIcon name="i-lucide-check-circle-2" class="w-5 h-5 shrink-0 mt-0.5 text-[#03AC0E]" />
            <div>
              <p class="font-bold text-sm text-gray-900 mb-0.5">Draf Pesan Telah Disiapkan</p>
              <p class="text-gray-700">Tab obrolan WhatsApp telah dibuka otomatis dengan ringkasan rincian kebutuhan proyek Anda.</p>
            </div>
          </div>

          <form @submit.prevent="handleFormSubmit" class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label for="input-fullname" class="block text-xs font-semibold text-gray-700 mb-1">
                  Nama Lengkap / Perusahaan <span class="text-red-500">*</span>
                </label>
                <input
                  id="input-fullname"
                  v-model="form.fullName"
                  type="text"
                  required
                  placeholder="Contoh: Bpk. Budi Santoso"
                  class="w-full px-3 py-2 text-xs bg-white border border-gray-300 rounded-lg focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none text-gray-900 placeholder:text-gray-400"
                />
              </div>

              <div>
                <label for="input-wa" class="block text-xs font-semibold text-gray-700 mb-1">
                  Nomor WhatsApp Aktif <span class="text-red-500">*</span>
                </label>
                <input
                  id="input-wa"
                  v-model="form.whatsapp"
                  type="tel"
                  required
                  placeholder="Contoh: 08123456789"
                  class="w-full px-3 py-2 text-xs bg-white border border-gray-300 rounded-lg focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none text-gray-900 placeholder:text-gray-400 font-mono"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label for="select-category" class="block text-xs font-semibold text-gray-700 mb-1">
                  Jenis Properti / Kebutuhan
                </label>
                <select
                  id="select-category"
                  v-model="form.category"
                  class="w-full px-3 py-2 text-xs bg-white border border-gray-300 rounded-lg focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none text-gray-900"
                >
                  <option>Pemasangan Baru Rumah / Ruko</option>
                  <option>Instalasi Pabrik / Gudang / Kantor</option>
                  <option>Upgrade Kamera & NVR Lama</option>
                  <option>Maintenance & Perbaikan Jaringan</option>
                  <option>Pengadaan Perangkat Saja</option>
                </select>
              </div>

              <div>
                <label for="select-camera" class="block text-xs font-semibold text-gray-700 mb-1">
                  Perkiraan Jumlah Titik
                </label>
                <select
                  id="select-camera"
                  v-model="form.cameraCount"
                  class="w-full px-3 py-2 text-xs bg-white border border-gray-300 rounded-lg focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none text-gray-900"
                >
                  <option>2 - 4 Titik (Rumah Tinggal / Warung)</option>
                  <option>5 - 8 Titik (Ruko / Restoran / Kantor)</option>
                  <option>9 - 16 Titik (Gudang / Kawasan Bisnis)</option>
                  <option>> 16 Titik (Industrial & Project)</option>
                  <option>Perlu Survei Lokasi Terlebih Dahulu</option>
                </select>
              </div>
            </div>

            <div>
              <label for="input-city" class="block text-xs font-semibold text-gray-700 mb-1">
                Kota / Wilayah Lokasi
              </label>
              <input
                id="input-city"
                v-model="form.locationCity"
                type="text"
                placeholder="Contoh: Bandung, Cimahi, Bogor, Jakarta Selatan"
                class="w-full px-3 py-2 text-xs bg-white border border-gray-300 rounded-lg focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none text-gray-900 placeholder:text-gray-400"
              />
            </div>

            <div>
              <label for="input-notes" class="block text-xs font-semibold text-gray-700 mb-1">
                Catatan Tambahan (Opsional)
              </label>
              <textarea
                id="input-notes"
                v-model="form.message"
                rows="3"
                placeholder="Misal: Kebutuhan kamera yang bisa rekam audio dan berwarna pada malam hari."
                class="w-full px-3 py-2 text-xs bg-white border border-gray-300 rounded-lg focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none text-gray-900 placeholder:text-gray-400 leading-relaxed"
              ></textarea>
            </div>

            <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full bg-[#03AC0E] hover:bg-[#028C0B] text-white text-xs font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 shadow-xs"
            >
              <UIcon v-if="isSubmitting" name="i-lucide-loader-2" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-lucide-send" class="w-4 h-4" />
              <span>{{ isSubmitting ? 'Mempersiapkan Rincian...' : 'Kirim Permintaan Estimasi via WhatsApp' }}</span>
            </button>
            <p class="text-[11px] text-gray-400 text-center">
              Informasi yang Anda masukkan terjaga kerahasiaannya dan hanya digunakan untuk komunikasi survei CCTV.
            </p>
          </form>
        </div>

        <!-- Sisi Kanan: Showroom Fisik & Jalur Tambahan (5 Kolom) -->
        <div class="lg:col-span-5 space-y-6">

          <!-- Kartu Showroom & Kantor Fisik -->
          <div class="bg-white rounded-xl border border-gray-200 p-5 shadow-xs">
            <div class="flex items-center gap-2 mb-2">
              <UIcon name="i-lucide-map-pin" class="w-4 h-4 text-[#03AC0E]" />
              <h3 class="text-sm font-bold text-gray-900">Showroom & Kantor Resmi</h3>
            </div>

            <p class="text-xs text-gray-700 font-medium leading-relaxed mb-3">
              {{ showroomAddress }}
            </p>

            <div class="space-y-1.5 text-xs text-gray-600 pb-4 border-b border-gray-100">
              <div class="flex items-center gap-1.5">
                <UIcon name="i-lucide-check-circle" class="w-3.5 h-3.5 text-[#03AC0E] shrink-0" />
                <span><strong>Workshop Lapangan:</strong> Bandung Raya & Cimahi</span>
              </div>
              <div class="flex items-center gap-1.5">
                <UIcon name="i-lucide-check-circle" class="w-3.5 h-3.5 text-[#03AC0E] shrink-0" />
                <span><strong>Jangkauan Layanan:</strong> Jabodetabek & Jawa Barat</span>
              </div>
            </div>

            <div class="pt-3 flex flex-wrap items-center gap-2">
              <button
                type="button"
                @click="copyAddress"
                class="inline-flex items-center gap-1 text-xs font-medium px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-700 transition-colors"
              >
                <UIcon :name="copied ? 'i-lucide-check' : 'i-lucide-copy'" class="w-3.5 h-3.5 text-gray-500" />
                <span>{{ copied ? 'Tersalin' : 'Salin Alamat' }}</span>
              </button>
              <a
                :href="mapsUrl"
                target="_blank"
                rel="noopener"
                class="inline-flex items-center gap-1 text-xs font-medium px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-700 transition-colors"
              >
                <UIcon name="i-lucide-external-link" class="w-3.5 h-3.5 text-gray-500" />
                <span>Buka Google Maps</span>
              </a>
              <NuxtLink
                to="/store-locator"
                class="inline-flex items-center gap-1 text-xs font-medium px-3 py-1.5 rounded-lg bg-gray-900 hover:bg-gray-800 text-white transition-colors ml-auto"
              >
                <span>Lihat Peta Cabang</span>
              </NuxtLink>
            </div>
          </div>

          <!-- Jalur Email & Telepon Resmi -->
          <div class="bg-white rounded-xl border border-gray-200 p-5 shadow-xs space-y-3">
            <h3 class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
              Kontak Surat & Telepon
            </h3>

            <a
              v-for="c in additionalContacts"
              :key="c.name"
              :href="c.link"
              class="flex items-start gap-3 p-3 rounded-lg border border-gray-100 hover:border-gray-300 hover:bg-gray-50/70 transition-colors group"
            >
              <div class="w-8 h-8 rounded-lg bg-gray-100 text-gray-700 flex items-center justify-center shrink-0 group-hover:bg-[#E6F7E9] group-hover:text-[#03AC0E] transition-colors">
                <UIcon :name="c.icon" class="w-4 h-4" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-[10px] text-gray-400 uppercase font-semibold">{{ c.name }}</p>
                <p class="text-xs font-bold text-gray-900 group-hover:text-[#03AC0E] transition-colors">{{ c.value }}</p>
                <p class="text-[11px] text-gray-500 truncate">{{ c.desc }}</p>
              </div>
            </a>
          </div>

        </div>
      </section>

      <!-- ── SECTION: PERTANYAAN UMUM (FAQ) ──────────────────── -->
      <section class="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 shadow-xs">
        <div class="mb-6">
          <span class="text-[11px] font-medium text-[#03AC0E] uppercase tracking-wider block mb-1">Pertanyaan Umum</span>
          <h2 class="text-lg font-bold text-gray-900">Pertanyaan yang Sering Diajukan</h2>
          <p class="text-xs text-gray-500 mt-0.5">Informasi praktis seputar survei lokasi, garansi, dan jadwal teknisi.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(item, idx) in faqs"
            :key="idx"
            class="p-4 rounded-lg bg-gray-50 border border-gray-200/70"
          >
            <h3 class="text-xs font-semibold text-gray-900 mb-1.5 flex items-start gap-2">
              <span class="w-4 h-4 rounded-full bg-[#E6F7E9] text-[#03AC0E] text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">Q</span>
              <span>{{ item.q }}</span>
            </h3>
            <p class="text-xs text-gray-600 leading-relaxed pl-6">
              {{ item.a }}
            </p>
          </div>
        </div>
      </section>

    </div>
  </main>
</template>