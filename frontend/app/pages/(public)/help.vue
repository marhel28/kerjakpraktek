<script setup lang="ts">
useSeoMeta({
  title: 'Pusat Bantuan - PasarCCTV',
  description: 'Temukan jawaban seputar cara belanja, pengiriman, pembayaran, jasa instalasi, dan garansi produk di PasarCCTV.',
})

const searchQuery = ref('')
const searchInput = ref<HTMLInputElement | null>(null)

const categories = [
  {
    id: 'transaksi',
    icon: 'i-heroicons-shopping-bag',
    color: '#03AC0E',
    bg: '#f0fef0',
    title: 'Cara Transaksi',
    desc: 'Panduan langkah demi langkah untuk berbelanja dan memesan jasa instalasi.',
    link: '/helps/cara-belanja',
    topics: ['Cara beli produk', 'Booking jasa pasang', 'Cara batalkan pesanan'],
    keywords: ['beli', 'belanja', 'transaksi', 'pesan', 'order', 'keranjang', 'checkout', 'booking', 'batal'],
  },
  {
    id: 'pengiriman',
    icon: 'i-heroicons-truck',
    color: '#2563EB',
    bg: '#eff6ff',
    title: 'Pengiriman & Lacak Resi',
    desc: 'Jadwal cut-off pengiriman, mitra kurir, dan cara melacak posisi paket Anda.',
    link: '/helps/shipping',
    topics: ['Jadwal operasional', 'Lacak resi', 'Estimasi tiba'],
    keywords: ['kirim', 'pengiriman', 'resi', 'kurir', 'lacak', 'ekspedisi', 'paket', 'jne', 'jnt', 'sicepat', 'estimasi'],
  },
  {
    id: 'pembayaran',
    icon: 'i-heroicons-credit-card',
    color: '#7C3AED',
    bg: '#f5f3ff',
    title: 'Pembayaran',
    desc: 'Metode pembayaran yang tersedia, keamanan transaksi, dan cara konfirmasi bayar.',
    link: '/helps/cara-belanja',
    topics: ['Transfer Bank', 'E-Wallet', 'Kartu Kredit'],
    keywords: ['bayar', 'pembayaran', 'transfer', 'bank', 'ewallet', 'kartu', 'kredit', 'midtrans', 'gopay', 'ovo', 'konfirmasi'],
  },
  {
    id: 'jasa',
    icon: 'i-heroicons-wrench-screwdriver',
    color: '#D97706',
    bg: '#fffbeb',
    title: 'Jasa Instalasi',
    desc: 'Cara booking teknisi, area layanan, biaya transport, dan garansi pasang.',
    link: '/helps/cara-belanja',
    topics: ['Area coverage', 'Biaya teknisi', 'Garansi instalasi'],
    keywords: ['jasa', 'instalasi', 'pasang', 'teknisi', 'booking', 'area', 'biaya', 'transport', 'garansi', 'dp'],
  },
  {
    id: 'produk',
    icon: 'i-heroicons-shield-check',
    color: '#0891B2',
    bg: '#ecfeff',
    title: 'Garansi & Produk',
    desc: 'Informasi garansi resmi, proses klaim, dan kebijakan pengembalian barang.',
    link: '/helps/cara-belanja',
    topics: ['Garansi resmi', 'Klaim garansi', 'Return & refund'],
    keywords: ['garansi', 'produk', 'klaim', 'return', 'refund', 'rusak', 'cacat', 'retur', 'resmi'],
  },
  {
    id: 'akun',
    icon: 'i-heroicons-user-circle',
    color: '#6B7280',
    bg: '#f9fafb',
    title: 'Akun & Keamanan',
    desc: 'Kelola profil, ganti password, verifikasi email, dan proteksi akun Anda.',
    link: '/dashboard',
    topics: ['Ubah profil', 'Ganti password', 'Keamanan akun'],
    keywords: ['akun', 'profil', 'password', 'keamanan', 'email', 'verifikasi', 'login', 'daftar', 'register'],
  },
]

const faqs = [
  {
    q: 'Bagaimana cara melacak pesanan saya?',
    a: 'Masuk ke Dashboard → Status Pesanan. Nomor resi akan muncul otomatis setelah barang dikirim oleh tim gudang kami.',
    keywords: ['lacak', 'resi', 'pesanan', 'status', 'kirim'],
  },
  {
    q: 'Apakah produk yang dijual bergaransi resmi?',
    a: 'Ya. Semua perangkat seperti Hikvision, Dahua, dan Ezviz memiliki garansi resmi pabrik 1–3 tahun.',
    keywords: ['garansi', 'resmi', 'produk', 'hikvision', 'dahua'],
  },
  {
    q: 'Berapa lama proses pengiriman?',
    a: 'Pesanan yang masuk sebelum cut-off (15.00 WIB) akan dikirim hari yang sama. Estimasi tiba 1–3 hari kerja untuk Pulau Jawa.',
    keywords: ['pengiriman', 'lama', 'estimasi', 'hari', 'kirim', 'cutoff'],
  },
  {
    q: 'Apakah bisa konsultasi sebelum membeli?',
    a: 'Bisa! Gunakan fitur Chat yang tersedia di setiap halaman produk atau hubungi CS kami via WhatsApp.',
    keywords: ['konsultasi', 'chat', 'tanya', 'whatsapp', 'cs'],
  },
  {
    q: 'Bagaimana jika ada kendala saat instalasi?',
    a: 'Teknisi kami memberikan garansi pekerjaan. Jika ada masalah dalam 30 hari setelah instalasi, kami akan kembali tanpa biaya tambahan.',
    keywords: ['kendala', 'instalasi', 'masalah', 'garansi', 'teknisi'],
  },
]

// ── Search logic ──
const q = computed(() => searchQuery.value.trim().toLowerCase())

const filteredCategories = computed(() => {
  if (!q.value) return categories
  return categories.filter(cat => {
    const haystack = [cat.title, cat.desc, ...cat.topics, ...cat.keywords].join(' ').toLowerCase()
    return haystack.includes(q.value)
  })
})

const filteredFaqs = computed(() => {
  if (!q.value) return faqs
  return faqs.filter(faq => {
    const haystack = [faq.q, faq.a, ...faq.keywords].join(' ').toLowerCase()
    return haystack.includes(q.value)
  })
})

const hasNoResult = computed(() =>
  q.value.length > 0 && filteredCategories.value.length === 0 && filteredFaqs.value.length === 0
)

const isSearching = computed(() => q.value.length > 0)

function clearSearch() {
  searchQuery.value = ''
  searchInput.value?.focus()
}

// ── FAQ accordion ──
const openFaq = ref<number | null>(null)
const toggleFaq = (i: number) => {
  openFaq.value = openFaq.value === i ? null : i
}

// Reset FAQ open state when filter changes
watch(filteredFaqs, () => { openFaq.value = null })
</script>

<template>
  <main class="bg-[#f5f5f5] min-h-screen pb-16">

    <!-- ── Hero Banner ── -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-[1200px] mx-auto px-4 lg:px-8 py-10 lg:py-14">
        <div class="flex flex-col lg:flex-row lg:items-center gap-6 lg:gap-12">
          <div class="flex-1">
            <!-- Breadcrumb -->
            <nav class="flex items-center gap-1.5 text-[12px] text-gray-400 mb-4">
              <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
              <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
              <span class="text-gray-700 font-semibold">Pusat Bantuan</span>
            </nav>
            <h1 class="text-2xl lg:text-3xl font-black text-gray-900 tracking-tight mb-2">
              Ada yang bisa kami bantu?
            </h1>
            <p class="text-[14px] text-gray-500 leading-relaxed max-w-lg">
              Temukan jawaban seputar belanja, pengiriman, pembayaran, dan layanan instalasi CCTV kami.
            </p>
          </div>

          <!-- ── Search Box ── -->
          <div class="lg:w-[420px] shrink-0">
            <div class="relative">
              <UIcon
                name="i-heroicons-magnifying-glass"
                class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none"
                aria-hidden="true"
              />
              <input
                ref="searchInput"
                v-model="searchQuery"
                type="search"
                placeholder="Cari topik bantuan... (misal: resi, garansi, bayar)"
                autocomplete="off"
                class="w-full pl-12 pr-10 py-3.5 bg-white border-2 border-gray-200 rounded-xl text-[14px] font-medium text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#03AC0E] transition-colors"
              />
              <!-- Clear button -->
              <button
                v-if="searchQuery"
                class="absolute right-3 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                aria-label="Hapus pencarian"
                @click="clearSearch"
              >
                <UIcon name="i-heroicons-x-mark" class="w-3.5 h-3.5 text-gray-500" />
              </button>
            </div>

            <!-- Search hint -->
            <p v-if="!isSearching" class="text-[11px] text-gray-400 mt-2 text-center">
              Atau pilih kategori di bawah untuk panduan lengkap
            </p>
            <p v-else class="text-[11px] text-gray-500 mt-2">
              Menampilkan hasil untuk
              <strong class="text-gray-800">"{{ searchQuery }}"</strong>
              &mdash;
              <span class="text-[#03AC0E] font-semibold">
                {{ filteredCategories.length }} topik, {{ filteredFaqs.length }} FAQ
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-[1200px] mx-auto px-4 lg:px-8 py-8">

      <!-- ── No Result ── -->
      <div
        v-if="hasNoResult"
        class="bg-white rounded-2xl border border-gray-100 p-10 text-center mb-8"
      >
        <div class="w-14 h-14 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <UIcon name="i-heroicons-magnifying-glass" class="w-7 h-7 text-gray-300" />
        </div>
        <p class="text-[15px] font-black text-gray-900 mb-1">Tidak ada hasil ditemukan</p>
        <p class="text-[13px] text-gray-400 mb-5">
          Coba kata kunci lain atau hubungi CS kami langsung.
        </p>
        <button
          class="inline-flex items-center gap-2 bg-[#03AC0E] text-white text-[12px] font-black px-5 py-2.5 rounded-xl hover:bg-[#028C0B] transition-colors"
          @click="clearSearch"
        >
          <UIcon name="i-heroicons-arrow-uturn-left" class="w-4 h-4" />
          Tampilkan Semua Topik
        </button>
      </div>

      <!-- ── Kategori Bantuan ── -->
      <div v-if="filteredCategories.length > 0" class="mb-10">
        <div class="flex items-center gap-2 mb-5">
          <span class="w-1 h-5 bg-[#03AC0E] rounded-full shrink-0" aria-hidden="true" />
          <h2 class="text-[15px] font-black text-gray-900">
            {{ isSearching ? 'Topik yang cocok' : 'Topik Bantuan' }}
          </h2>
          <span
            v-if="isSearching"
            class="text-[11px] font-bold text-[#03AC0E] bg-green-50 px-2 py-0.5 rounded-full"
          >
            {{ filteredCategories.length }} hasil
          </span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <NuxtLink
            v-for="cat in filteredCategories"
            :key="cat.id"
            :to="cat.link"
            class="group bg-white border border-gray-100 rounded-2xl p-5 hover:border-gray-200 hover:shadow-[0_4px_16px_-4px_rgba(0,0,0,0.08)] transition-all duration-200"
          >
            <div class="flex items-start gap-4">
              <div
                class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
                :style="{ background: cat.bg }"
              >
                <UIcon :name="cat.icon" class="w-5 h-5" :style="{ color: cat.color }" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1">
                  <h3 class="text-[14px] font-black text-gray-900">{{ cat.title }}</h3>
                  <UIcon
                    name="i-heroicons-chevron-right"
                    class="w-4 h-4 text-gray-300 group-hover:text-[#03AC0E] group-hover:translate-x-0.5 transition-all shrink-0"
                  />
                </div>
                <p class="text-[12px] text-gray-500 leading-relaxed mb-3">{{ cat.desc }}</p>
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="topic in cat.topics"
                    :key="topic"
                    class="text-[10px] font-semibold text-gray-500 bg-gray-50 border border-gray-100 px-2 py-0.5 rounded-full"
                  >
                    {{ topic }}
                  </span>
                </div>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- ── FAQ ── -->
      <div v-if="filteredFaqs.length > 0" class="bg-white rounded-2xl border border-gray-100 overflow-hidden mb-8">
        <div class="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 bg-[#f0fef0] rounded-lg flex items-center justify-center">
              <UIcon name="i-heroicons-chat-bubble-bottom-center-text" class="w-4 h-4 text-[#03AC0E]" />
            </div>
            <div>
              <h2 class="text-[14px] font-black text-gray-900 leading-none">
                {{ isSearching ? 'FAQ yang cocok' : 'Pertanyaan Umum (FAQ)' }}
              </h2>
              <p class="text-[11px] text-gray-400 mt-0.5">
                {{ isSearching ? `${filteredFaqs.length} pertanyaan ditemukan` : 'Jawaban cepat untuk pertanyaan yang sering ditanyakan' }}
              </p>
            </div>
          </div>
          <span
            v-if="isSearching"
            class="text-[11px] font-bold text-[#03AC0E] bg-green-50 px-2 py-0.5 rounded-full"
          >
            {{ filteredFaqs.length }} hasil
          </span>
        </div>

        <div class="divide-y divide-gray-50">
          <div v-for="(faq, i) in filteredFaqs" :key="faq.q">
            <button
              class="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-gray-50/50 transition-colors"
              @click="toggleFaq(i)"
            >
              <span class="text-[13px] font-semibold text-gray-800 pr-4 leading-snug">{{ faq.q }}</span>
              <div
                class="w-6 h-6 rounded-full flex items-center justify-center shrink-0 transition-all duration-200"
                :class="openFaq === i ? 'bg-[#03AC0E] rotate-180' : 'bg-gray-100'"
              >
                <UIcon
                  name="i-heroicons-chevron-down"
                  class="w-3.5 h-3.5 transition-colors"
                  :class="openFaq === i ? 'text-white' : 'text-gray-400'"
                />
              </div>
            </button>
            <div
              class="overflow-hidden transition-all duration-200"
              :class="openFaq === i ? 'max-h-48' : 'max-h-0'"
            >
              <p class="px-6 pb-4 text-[13px] text-gray-500 leading-relaxed">{{ faq.a }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Kontak CS ── -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6">
        <div class="flex items-center gap-2 mb-5">
          <span class="w-1 h-5 bg-[#03AC0E] rounded-full shrink-0" aria-hidden="true" />
          <h2 class="text-[15px] font-black text-gray-900">Masih butuh bantuan?</h2>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <a
            href="https://wa.me/6281234567890"
            target="_blank"
            rel="noopener noreferrer"
            class="group flex items-center gap-3 p-4 bg-[#f0fef0] border border-green-100 rounded-xl hover:border-[#03AC0E]/30 hover:bg-green-50 transition-all"
          >
            <div class="w-10 h-10 bg-[#03AC0E] rounded-xl flex items-center justify-center shrink-0">
              <UIcon name="i-heroicons-chat-bubble-left-ellipsis" class="w-5 h-5 text-white" />
            </div>
            <div class="min-w-0">
              <p class="text-[13px] font-black text-gray-900">WhatsApp CS</p>
              <p class="text-[11px] text-gray-500">Respon cepat &lt; 5 menit</p>
            </div>
            <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3.5 h-3.5 text-gray-300 group-hover:text-[#03AC0E] ml-auto shrink-0 transition-colors" />
          </a>

          <NuxtLink
            to="/"
            class="group flex items-center gap-3 p-4 bg-blue-50 border border-blue-100 rounded-xl hover:border-blue-300 transition-all"
          >
            <div class="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center shrink-0">
              <UIcon name="i-heroicons-cpu-chip" class="w-5 h-5 text-white" />
            </div>
            <div class="min-w-0">
              <p class="text-[13px] font-black text-gray-900">Live Chat AI</p>
              <p class="text-[11px] text-gray-500">Tersedia 24/7</p>
            </div>
            <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5 text-gray-300 group-hover:text-blue-500 ml-auto shrink-0 transition-colors" />
          </NuxtLink>

          <a
            href="mailto:cs@pasarcctv.id"
            class="group flex items-center gap-3 p-4 bg-gray-50 border border-gray-100 rounded-xl hover:border-gray-200 transition-all"
          >
            <div class="w-10 h-10 bg-gray-700 rounded-xl flex items-center justify-center shrink-0">
              <UIcon name="i-heroicons-envelope" class="w-5 h-5 text-white" />
            </div>
            <div class="min-w-0">
              <p class="text-[13px] font-black text-gray-900">Email Support</p>
              <p class="text-[11px] text-gray-500">Balasan 1×24 jam</p>
            </div>
            <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3.5 h-3.5 text-gray-300 group-hover:text-gray-600 ml-auto shrink-0 transition-colors" />
          </a>
        </div>
      </div>

    </div>
  </main>
</template>