<script setup lang="ts">
import { ref, computed } from 'vue'

useSeoMeta({
  title: 'Pusat Bantuan & Kontak Resmi — PasarCctv × Padjajaran CCTV',
  description: 'Hubungi tim sales dan teknisi resmi PasarCctv & Padjajaran CCTV. Konsultasi pemilihan kamera, jadwal survei lokasi, dan dukungan teknis instalasi.',
  ogTitle: 'Pusat Bantuan & Kontak Operasional PasarCctv',
  ogDescription: 'Layanan cepat WhatsApp Sales, Teknisi Lapangan, Showroom Bogor & Workshop Cimahi/Bandung.',
})

// ── Jalur Prioritas WhatsApp (Nomor Riil Terverifikasi) ─────────────
const waSales = {
  name: 'WhatsApp Sales & Pembelian Perangkat',
  phoneDisplay: '+62 821-1777-9003',
  phoneNumber: '6282117779003',
  badge: 'Fast Response (< 5 Mnt)',
  desc: 'Konsultasi pemilihan brand (Dahua, Hikvision, Ezviz, Tiandy, Imou), cek ketersediaan stok produk, pengiriman logistik, dan penawaran harga grosir/retail.',
  defaultText: 'Halo PasarCCTV, saya ingin konsultasi pemilihan produk CCTV dan ketersediaan stok barang.',
  icon: 'i-lucide-shopping-cart'
}

const waSupport = {
  name: 'WhatsApp Teknisi & Instalasi Lapangan',
  phoneDisplay: '+62 822-1882-8108',
  phoneNumber: '6282218828108',
  badge: 'Padjajaran CCTV Divisi Teknisi',
  desc: 'Jadwal kunjungan survei lokasi gratis, instalasi pipa conduit rapi, konfigurasi online HP (DMSS/Hik-Connect/Ezviz), klaim garansi ganti baru, dan maintenance.',
  defaultText: 'Halo Tim Teknisi Padjajaran CCTV, saya ingin konsultasi jadwal survei lokasi dan jasa pemasangan.',
  icon: 'i-lucide-wrench'
}

// ── Link WA Dinamis ──────────────────────────────────────────────
const waSalesLink = computed(() => {
  return `https://wa.me/${waSales.phoneNumber}?text=${encodeURIComponent(waSales.defaultText)}`
})

const waSupportLink = computed(() => {
  return `https://wa.me/${waSupport.phoneNumber}?text=${encodeURIComponent(waSupport.defaultText)}`
})

// ── Data Kontak Tambahan ──────────────────────────────────────────
const otherContacts = [
  {
    name: 'Email Dukungan Resmi',
    value: 'cs@pasarcctv.com',
    link: 'mailto:cs@pasarcctv.com',
    desc: 'Untuk surat penawaran resmi, tender, dan kerja sama korporat',
    icon: 'i-lucide-mail'
  },
  {
    name: 'Telepon Kantor & CS',
    value: '(022) 8600-9003',
    link: 'tel:02286009003',
    desc: 'Layanan panggilan suara jam operasional kerja',
    icon: 'i-lucide-phone'
  }
]

// ── Data Showroom & Workshop ──────────────────────────────────────
const showroomAddress = 'Jl. Tumenggung Wiradireja No.29A, Cimahpar, Bogor Utara, Kota Bogor, Jawa Barat 16155'
const mapsUrl = 'https://www.google.com/maps/search/?api=1&query=-6.5510,106.8185'

// ── State Formulir Konsultasi Proyek ──────────────────────────────
const form = ref({
  fullName: '',
  whatsapp: '',
  category: 'Pemasangan Baru Rumah / Ruko',
  cameraCount: '2-4 Titik',
  message: '',
})

const isSubmitting = ref(false)
const submitSuccess = ref(false)

const handleFormSubmit = () => {
  if (!form.value.fullName.trim() || !form.value.whatsapp.trim()) {
    alert('Mohon lengkapi Nama dan Nomor WhatsApp aktif Anda.')
    return
  }

  isSubmitting.value = true

  // Buat draft pesan WhatsApp terstruktur
  const textMsg = `Halo Tim PasarCctv & Padjajaran CCTV,\n\nSaya ingin konsultasi proyek sistem keamanan melalui formulir website:\n\n👤 *Nama:* ${form.value.fullName}\n📱 *No. WhatsApp:* ${form.value.whatsapp}\n🏷️ *Kebutuhan:* ${form.value.category}\n🎥 *Estimasi Kamera:* ${form.value.cameraCount}\n💬 *Catatan/Lokasi:* ${form.value.message || '-'}\n\nMohon bantuannya untuk informasi estimasi dan jadwalnya. Terima kasih!`

  const targetWa = `https://wa.me/${waSupport.phoneNumber}?text=${encodeURIComponent(textMsg)}`

  setTimeout(() => {
    isSubmitting.value = false
    submitSuccess.value = true
    if (typeof window !== 'undefined') {
      window.open(targetWa, '_blank')
    }
  }, 500)
}

// ── FAQ Cepat ─────────────────────────────────────────────────────
const faqs = [
  {
    q: 'Berapa lama respon tim customer service?',
    a: 'Chat melalui WhatsApp direspons dalam rata-rata < 5 menit pada jam operasional (Senin-Sabtu, 08.00 - 17.00 WIB).'
  },
  {
    q: 'Apakah survei lokasi dikenakan biaya?',
    a: 'Survei lokasi wilayah Jabodetabek dan Bandung Raya tidak dikenakan biaya komitmen (Gratis konsultasi rancangan tata letak kamera).'
  },
  {
    q: 'Bagaimana prosedur klaim garansi kamera?',
    a: 'Cukup kirimkan foto barcode/nota pembelian ke WhatsApp Teknisi Padjajaran CCTV. Unit yang rusak akibat cacat pabrik di tahun pertama mendapat jaminan ganti baru.'
  },
  {
    q: 'Apakah bisa berkunjung langsung ke showroom?',
    a: 'Bisa, showroom kami di Bogor dan workshop Bandung/Cimahi buka Senin s/d Sabtu pukul 08.00 - 17.00 WIB untuk demo produk dan konsultasi langsung.'
  }
]
</script>

<template>
  <main class="bg-gray-50 min-h-screen pb-20 font-sans text-gray-800">
    <!-- ══════════════════════════════════════════════════════════
         HERO SECTION (Slate Enterprise Theme)
    ══════════════════════════════════════════════════════════════ -->
    <header class="bg-gradient-to-br from-slate-900 via-slate-850 to-slate-800 text-white pt-10 pb-24 px-4 sm:px-6 lg:px-8 relative overflow-hidden border-b border-slate-700/50">
      <!-- Ambient Lighting -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
      <div class="absolute bottom-0 left-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20"></div>

      <div class="max-w-5xl mx-auto relative z-10 text-center">
        <!-- Breadcrumb -->
        <nav aria-label="Breadcrumb" class="mb-4 flex items-center justify-center gap-2 text-xs font-semibold text-slate-400">
          <NuxtLink to="/" class="hover:text-emerald-400 transition-colors">Beranda</NuxtLink>
          <span>/</span>
          <span class="text-slate-200">Kontak &amp; Pusat Bantuan</span>
        </nav>

        <!-- Partner Badge -->
        <div class="inline-flex items-center gap-2 bg-slate-800/80 border border-slate-700/80 px-3.5 py-1.5 rounded-full text-xs font-semibold text-emerald-400 mb-4 shadow-sm backdrop-blur-md">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span>Layanan Resmi PasarCCTV × Padjajaran CCTV</span>
        </div>

        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-white mb-4">
          Pusat Bantuan &amp; Kontak Operasional
        </h1>
        <p class="text-slate-300 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
          Pilih jalur komunikasi yang Anda butuhkan. Tim sales dan teknisi bersertifikasi kami siap membantu pengadaan, survei lokasi, hingga pemeliharaan sistem keamanan Anda.
        </p>

        <!-- Operasional Bar -->
        <div class="mt-6 inline-flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-xs text-slate-300 bg-white/5 border border-white/10 px-4 py-2.5 rounded-xl backdrop-blur-sm">
          <div class="flex items-center gap-1.5">
            <UIcon name="i-lucide-clock" class="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Senin – Sabtu: <strong>08.00 – 17.00 WIB</strong></span>
          </div>
          <span class="hidden sm:inline text-slate-600">|</span>
          <div class="flex items-center gap-1.5">
            <UIcon name="i-lucide-zap" class="w-4 h-4 text-amber-400 shrink-0" />
            <span>Respon WhatsApp Rata-rata: <strong>&lt; 5 Menit</strong></span>
          </div>
        </div>
      </div>
    </header>

    <!-- ══════════════════════════════════════════════════════════
         MAIN CONTENT CONTAINER
    ══════════════════════════════════════════════════════════════ -->
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 -mt-12 relative z-20 space-y-10">

      <!-- ── SECTION 1: 2 JALUR WHATSAPP PRIORITAS ────────────── -->
      <section aria-labelledby="wa-channels-heading">
        <h2 id="wa-channels-heading" class="sr-only">Jalur Komunikasi WhatsApp Cepat</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          
          <!-- WA Sales Card -->
          <a
            :href="waSalesLink"
            target="_blank"
            rel="noopener"
            class="bg-white rounded-2xl shadow-sm border border-gray-200/90 p-6 transition-all duration-200 hover:border-emerald-500 hover:shadow-md hover:-translate-y-0.5 group flex flex-col justify-between"
          >
            <div>
              <div class="flex items-start justify-between gap-3 mb-4">
                <div class="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center shrink-0 group-hover:bg-emerald-500 group-hover:border-emerald-500 transition-colors">
                  <UIcon name="i-lucide-shopping-cart" class="w-6 h-6 text-emerald-600 group-hover:text-white transition-colors" />
                </div>
                <span class="text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200/60 px-2.5 py-1 rounded-full uppercase tracking-wider">
                  {{ waSales.badge }}
                </span>
              </div>

              <h3 class="text-base font-bold text-gray-900 group-hover:text-emerald-700 transition-colors leading-snug mb-1">
                {{ waSales.name }}
              </h3>
              <p class="text-xs text-gray-500 leading-relaxed mb-5">
                {{ waSales.desc }}
              </p>
            </div>

            <div class="pt-4 border-t border-gray-100 flex items-center justify-between mt-auto">
              <div>
                <span class="block text-[10px] uppercase font-bold tracking-wider text-gray-400">Nomor WhatsApp</span>
                <span class="text-sm font-black text-emerald-600 tracking-tight">{{ waSales.phoneDisplay }}</span>
              </div>
              <span class="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-emerald-600 px-3.5 py-2 rounded-xl group-hover:bg-emerald-700 transition-colors shadow-sm">
                <span>Chat Sales</span>
                <UIcon name="i-lucide-arrow-right" class="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </span>
            </div>
          </a>

          <!-- WA Teknisi Padjajaran CCTV Card -->
          <a
            :href="waSupportLink"
            target="_blank"
            rel="noopener"
            class="bg-white rounded-2xl shadow-sm border border-gray-200/90 p-6 transition-all duration-200 hover:border-emerald-500 hover:shadow-md hover:-translate-y-0.5 group flex flex-col justify-between"
          >
            <div>
              <div class="flex items-start justify-between gap-3 mb-4">
                <div class="w-12 h-12 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center shrink-0 group-hover:bg-slate-900 group-hover:border-slate-900 transition-colors">
                  <UIcon name="i-lucide-wrench" class="w-6 h-6 text-slate-800 group-hover:text-white transition-colors" />
                </div>
                <span class="text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200 px-2.5 py-1 rounded-full uppercase tracking-wider">
                  {{ waSupport.badge }}
                </span>
              </div>

              <h3 class="text-base font-bold text-gray-900 group-hover:text-slate-900 transition-colors leading-snug mb-1">
                {{ waSupport.name }}
              </h3>
              <p class="text-xs text-gray-500 leading-relaxed mb-5">
                {{ waSupport.desc }}
              </p>
            </div>

            <div class="pt-4 border-t border-gray-100 flex items-center justify-between mt-auto">
              <div>
                <span class="block text-[10px] uppercase font-bold tracking-wider text-gray-400">Teknisi Lapangan</span>
                <span class="text-sm font-black text-slate-900 tracking-tight">{{ waSupport.phoneDisplay }}</span>
              </div>
              <span class="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-slate-900 px-3.5 py-2 rounded-xl group-hover:bg-slate-800 transition-colors shadow-sm">
                <span>Chat Teknisi</span>
                <UIcon name="i-lucide-arrow-right" class="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </span>
            </div>
          </a>

        </div>
      </section>

      <!-- ── SECTION 2: FORMULIR KONSULTASI & LOKASI TOKO ──────── -->
      <section class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

        <!-- Kiri: Formulir Permintaan Penawaran / Pesan (7 Kolom) -->
        <div class="lg:col-span-7 bg-white rounded-2xl shadow-sm border border-gray-200/90 p-6 sm:p-8">
          <div class="flex items-center gap-2.5 mb-1">
            <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <UIcon name="i-lucide-file-text" class="w-4 h-4" />
            </div>
            <h2 class="text-lg font-bold text-gray-900">Formulir Konsultasi &amp; Penawaran</h2>
          </div>
          <p class="text-xs text-gray-500 mb-6">
            Punya kebutuhan pemasangan CCTV untuk rumah, ruko, kantor, atau pabrik? Isi data di bawah ini untuk estimasi cepat dari tim kami.
          </p>

          <!-- Success Alert -->
          <div v-if="submitSuccess" class="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-start gap-3">
            <UIcon name="i-lucide-check-circle-2" class="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <p class="font-bold text-sm text-emerald-900 mb-0.5">Pesan Berhasil Disiapkan!</p>
              <p>Tab obrolan WhatsApp resmi teknisi telah dibuka dengan ringkasan kebutuhan Anda. Anda juga dapat mengirim pesan tambahan kapan saja.</p>
            </div>
          </div>

          <form @submit.prevent="handleFormSubmit" class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Nama -->
              <div>
                <label for="form-name" class="block text-xs font-bold text-gray-700 mb-1.5">
                  Nama Lengkap / Perusahaan <span class="text-red-500">*</span>
                </label>
                <input
                  id="form-name"
                  v-model="form.fullName"
                  type="text"
                  required
                  placeholder="Contoh: Bpk. Hendra"
                  class="w-full px-3.5 py-2.5 text-xs bg-gray-50/70 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/10 outline-none transition-all font-medium text-gray-800"
                />
              </div>

              <!-- No WhatsApp -->
              <div>
                <label for="form-wa" class="block text-xs font-bold text-gray-700 mb-1.5">
                  Nomor WhatsApp Aktif <span class="text-red-500">*</span>
                </label>
                <input
                  id="form-wa"
                  v-model="form.whatsapp"
                  type="tel"
                  required
                  placeholder="Contoh: 08123456789"
                  class="w-full px-3.5 py-2.5 text-xs bg-gray-50/70 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/10 outline-none transition-all font-medium text-gray-800"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Kategori Kebutuhan -->
              <div>
                <label for="form-category" class="block text-xs font-bold text-gray-700 mb-1.5">
                  Jenis Kebutuhan
                </label>
                <select
                  id="form-category"
                  v-model="form.category"
                  class="w-full px-3 py-2.5 text-xs bg-gray-50/70 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/10 outline-none transition-all font-medium text-gray-800"
                >
                  <option>Pemasangan Baru Rumah / Ruko</option>
                  <option>Instalasi Pabrik / Gudang / Kantor</option>
                  <option>Upgrade Kamera &amp; DVR/NVR Lama</option>
                  <option>Maintenance &amp; Perbaikan Rusak</option>
                  <option>Pembelian Paket Perangkat Saja</option>
                </select>
              </div>

              <!-- Jumlah Titik Kamera -->
              <div>
                <label for="form-camera" class="block text-xs font-bold text-gray-700 mb-1.5">
                  Estimasi Jumlah Kamera
                </label>
                <select
                  id="form-camera"
                  v-model="form.cameraCount"
                  class="w-full px-3 py-2.5 text-xs bg-gray-50/70 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/10 outline-none transition-all font-medium text-gray-800"
                >
                  <option>2 - 4 Titik (Paket Hemat/Rumah)</option>
                  <option>5 - 8 Titik (Ruko / Bisnis Menengah)</option>
                  <option>9 - 16 Titik (Gudang / Kantor)</option>
                  <option>&gt; 16 Titik (Kawasan Industri / Enterprise)</option>
                  <option>Belum Tahu (Butuh Survei Lokasi)</option>
                </select>
              </div>
            </div>

            <!-- Detail Pesan / Lokasi -->
            <div>
              <label for="form-msg" class="block text-xs font-bold text-gray-700 mb-1.5">
                Lokasi Kota / Catatan Tambahan (Opsional)
              </label>
              <textarea
                id="form-msg"
                v-model="form.message"
                rows="3"
                placeholder="Contoh: Lokasi ruko di Buah Batu Bandung, ingin kamera yang ada mic audio dan hasil rekam berwarna di malam hari."
                class="w-full px-3.5 py-2.5 text-xs bg-gray-50/70 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/10 outline-none transition-all font-medium text-gray-800 leading-relaxed"
              ></textarea>
            </div>

            <!-- Tombol Submit -->
            <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold uppercase tracking-wider py-3.5 px-4 rounded-xl transition-all shadow-sm hover:shadow flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
            >
              <UIcon v-if="isSubmitting" name="i-lucide-loader-2" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-lucide-send" class="w-4 h-4" />
              <span>{{ isSubmitting ? 'Menyiapkan Pesan...' : 'Kirim Permintaan Konsultasi' }}</span>
            </button>
            <p class="text-[11px] text-gray-400 text-center">
              Data Anda aman dan hanya digunakan oleh tim kami untuk estimasi kebutuhan CCTV.
            </p>
          </form>
        </div>

        <!-- Kanan: Info Showroom, Workshop & Bantuan Cepat (5 Kolom) -->
        <div class="lg:col-span-5 space-y-6">

          <!-- Kartu Showroom & Workshop -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200/90 p-6">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
                <UIcon name="i-lucide-map-pin" class="w-4 h-4" />
              </div>
              <h3 class="text-sm font-bold text-gray-900">Showroom &amp; Kantor Resmi</h3>
            </div>

            <p class="text-xs text-gray-700 font-semibold leading-relaxed mb-3">
              {{ showroomAddress }}
            </p>

            <div class="space-y-2 text-xs text-gray-500 pb-4 border-b border-gray-100">
              <div class="flex items-start gap-2">
                <UIcon name="i-lucide-check-circle" class="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Workshop Lapangan:</strong> Bandung Raya &amp; Kota Cimahi (Padjajaran CCTV)</span>
              </div>
              <div class="flex items-start gap-2">
                <UIcon name="i-lucide-navigation" class="w-3.5 h-3.5 text-blue-600 shrink-0 mt-0.5" />
                <span><strong>Jangkauan Layanan:</strong> Jabodetabek, Bandung, Cimahi, dan sekitarnya</span>
              </div>
            </div>

            <!-- Tombol Navigasi Maps -->
            <div class="pt-4 flex flex-col sm:flex-row gap-2.5">
              <NuxtLink
                to="/store-locator"
                class="flex-1 inline-flex items-center justify-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold py-2.5 px-3 rounded-xl transition-colors shadow-sm"
              >
                <UIcon name="i-lucide-map" class="w-3.5 h-3.5" />
                <span>Peta Toko &amp; GPS</span>
              </NuxtLink>
              <a
                :href="mapsUrl"
                target="_blank"
                rel="noopener"
                class="inline-flex items-center justify-center gap-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold py-2.5 px-3 rounded-xl transition-colors"
              >
                <UIcon name="i-lucide-external-link" class="w-3.5 h-3.5" />
                <span>Google Maps</span>
              </a>
            </div>
          </div>

          <!-- Jalur Bantuan Lainnya (Email & Telepon) -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200/90 p-6 space-y-3.5">
            <h3 class="text-sm font-bold text-gray-900 mb-1 flex items-center gap-2">
              <UIcon name="i-lucide-headphones" class="w-4 h-4 text-emerald-600" />
              <span>Jalur Bantuan Tambahan</span>
            </h3>

            <a
              v-for="c in otherContacts"
              :key="c.name"
              :href="c.link"
              class="flex items-start gap-3.5 p-3 rounded-xl bg-gray-50 hover:bg-emerald-50/60 border border-gray-100 hover:border-emerald-200 transition-colors group"
            >
              <div class="w-9 h-9 rounded-lg bg-white border border-gray-200 flex items-center justify-center text-gray-500 group-hover:text-emerald-600 shrink-0">
                <UIcon :name="c.icon" class="w-4 h-4" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-0.5">{{ c.name }}</p>
                <p class="text-xs font-bold text-gray-900 group-hover:text-emerald-700">{{ c.value }}</p>
                <p class="text-[11px] text-gray-500 truncate">{{ c.desc }}</p>
              </div>
            </a>
          </div>

          <!-- Pintasan Bantuan Mandiri -->
          <div class="bg-gradient-to-br from-emerald-50 to-teal-50/60 rounded-2xl border border-emerald-100 p-5">
            <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-800 mb-2.5 flex items-center gap-1.5">
              <UIcon name="i-lucide-help-circle" class="w-4 h-4" />
              <span>Butuh Bantuan Langsung?</span>
            </h4>
            <div class="space-y-1.5 text-xs font-semibold">
              <NuxtLink to="/services/booking" class="flex items-center justify-between text-slate-700 hover:text-emerald-700 py-1 transition-colors">
                <span>• Jadwalkan Teknisi Lapangan</span>
                <UIcon name="i-lucide-chevron-right" class="w-3.5 h-3.5 text-gray-400" />
              </NuxtLink>
              <NuxtLink to="/helps/cara-belanja" class="flex items-center justify-between text-slate-700 hover:text-emerald-700 py-1 transition-colors">
                <span>• Panduan Cara Belanja &amp; Pembayaran</span>
                <UIcon name="i-lucide-chevron-right" class="w-3.5 h-3.5 text-gray-400" />
              </NuxtLink>
              <NuxtLink to="/dashboard/orders" class="flex items-center justify-between text-slate-700 hover:text-emerald-700 py-1 transition-colors">
                <span>• Cek Riwayat &amp; Status Pesanan</span>
                <UIcon name="i-lucide-chevron-right" class="w-3.5 h-3.5 text-gray-400" />
              </NuxtLink>
            </div>
          </div>

        </div>

      </section>

      <!-- ── SECTION 3: FAQ TERKAIT KONTAK & LAYANAN ────────── -->
      <section class="bg-white rounded-2xl shadow-sm border border-gray-200/90 p-6 sm:p-8">
        <div class="text-center max-w-xl mx-auto mb-8">
          <div class="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full uppercase tracking-wider mb-2">
            Pertanyaan Umum
          </div>
          <h2 class="text-xl font-bold text-gray-900">Sering Ditanyakan Seputar Layanan</h2>
          <p class="text-xs text-gray-500 mt-1">Jawaban cepat untuk pertanyaan yang paling sering diajukan pelanggan.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div
            v-for="(item, idx) in faqs"
            :key="idx"
            class="p-4 rounded-xl bg-gray-50/70 border border-gray-100 flex flex-col justify-between"
          >
            <h3 class="text-xs font-bold text-gray-900 mb-2 flex items-start gap-2">
              <span class="w-4 h-4 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-black flex items-center justify-center shrink-0 mt-0.5">Q</span>
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
