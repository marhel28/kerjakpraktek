<template>
  <main class="bg-[#F7F8F9] min-h-screen pb-16 font-['Open_Sans',sans-serif] text-gray-900">
    <!-- ════════════════════════════════════════════════════════════
         HERO SEARCH: Amazon Customer Service Hub layout
         ════════════════════════════════════════════════════════════ -->
    <header class="bg-white border-b border-gray-200 pt-8 pb-10 px-4 sm:px-6 lg:px-8">
      <div class="max-w-5xl mx-auto">
        <!-- Breadcrumb -->
        <nav aria-label="Breadcrumb" class="mb-4 flex items-center gap-2 text-xs font-medium text-gray-500 font-['Plus_Jakarta_Sans',sans-serif]">
          <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
          <span class="text-gray-300">/</span>
          <span class="text-gray-800">Pusat Bantuan</span>
        </nav>

        <div class="text-center max-w-2xl mx-auto mb-6">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#E6F7E9] text-[#03AC0E] border border-[#C8E6CC] mb-3 font-['Plus_Jakarta_Sans',sans-serif]">
            <UIcon name="i-heroicons-shield-check" class="w-4 h-4 shrink-0" />
            <span>PasarCCTV Care</span>
          </span>
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-gray-900 font-['Plus_Jakarta_Sans',sans-serif]">
            Ada yang bisa kami bantu?
          </h1>
          <p class="text-xs sm:text-sm text-gray-600 mt-2 leading-relaxed">
            Cari solusi kendala teknis, lacak pesanan, atau konsultasi langsung dengan tim teknisi dan sales resmi kami.
          </p>
        </div>

        <!-- Search Input with Real-time Filter -->
        <div class="max-w-2xl mx-auto relative mb-4">
          <div class="relative flex items-center">
            <span class="absolute left-4 text-gray-400" aria-hidden="true">
              <UIcon name="i-heroicons-magnifying-glass" class="w-5 h-5" />
            </span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Ketik kendala Anda (contoh: garansi, pairing DMSS, lacak resi, reset DVR)..."
              class="w-full pl-12 pr-10 py-3.5 bg-white border border-gray-300 focus:border-[#03AC0E] focus:ring-2 focus:ring-[#03AC0E]/20 rounded-xl text-sm text-gray-900 outline-none shadow-xs transition-all placeholder:text-gray-400 font-['Open_Sans',sans-serif]"
              aria-label="Pencarian pusat bantuan"
            />
            <button
              v-if="searchQuery"
              type="button"
              class="absolute right-3.5 text-gray-400 hover:text-gray-700 p-1"
              aria-label="Hapus kata kunci pencarian"
              @click="searchQuery = ''"
            >
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Tokopedia Care Popular Search Chips -->
        <div class="max-w-2xl mx-auto flex flex-wrap items-center justify-center gap-2">
          <span class="text-xs text-gray-400 font-semibold font-['Plus_Jakarta_Sans',sans-serif]">Sering Dicari:</span>
          <button
            v-for="chip in popularChips"
            :key="chip"
            type="button"
            class="px-2.5 py-1 bg-gray-100 hover:bg-[#E6F7E9] hover:text-[#03AC0E] border border-gray-200 hover:border-[#C8E6CC] rounded-full text-xs text-gray-700 transition-colors font-medium cursor-pointer"
            @click="searchQuery = chip"
          >
            {{ chip }}
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-10">
      <!-- ════════════════════════════════════════════════════════════
           AMAZON QUICK ACTIONS: 4 Solusi Cepat
           ════════════════════════════════════════════════════════════ -->
      <section aria-labelledby="quick-actions-heading">
        <h2 id="quick-actions-heading" class="text-sm font-bold uppercase tracking-wider text-gray-500 mb-3 font-['Plus_Jakarta_Sans',sans-serif]">
          Solusi Cepat
        </h2>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <NuxtLink
            v-for="action in quickActions"
            :key="action.title"
            :to="action.to"
            class="bg-white border border-gray-200 hover:border-[#03AC0E] p-4 rounded-xl shadow-xs hover:shadow-sm transition-all group flex flex-col justify-between"
          >
            <div>
              <div class="w-10 h-10 rounded-lg bg-[#E6F7E9] text-[#03AC0E] flex items-center justify-center mb-3 group-hover:bg-[#03AC0E] group-hover:text-white transition-colors">
                <UIcon :name="action.icon" class="w-5 h-5" />
              </div>
              <h3 class="text-xs font-bold text-gray-900 group-hover:text-[#03AC0E] transition-colors leading-snug font-['Plus_Jakarta_Sans',sans-serif]">
                {{ action.title }}
              </h3>
              <p class="text-[11px] text-gray-500 mt-1 leading-normal">
                {{ action.desc }}
              </p>
            </div>
            <div class="pt-3 mt-3 border-t border-gray-100 flex items-center justify-between text-xs font-semibold text-[#03AC0E]">
              <span>{{ action.cta }}</span>
              <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </NuxtLink>
        </div>
      </section>

      <!-- ════════════════════════════════════════════════════════════
           TOKOPEDIA CARE CATEGORY PILLS
           ════════════════════════════════════════════════════════════ -->
      <section aria-labelledby="faq-section-heading">
        <div class="flex items-center justify-between mb-4">
          <h2 id="faq-section-heading" class="text-sm font-bold uppercase tracking-wider text-gray-500 font-['Plus_Jakarta_Sans',sans-serif]">
            Kategori Kendala & Pertanyaan
          </h2>
          <span v-if="filteredFaqs.length" class="text-xs text-gray-400">
            Menampilkan {{ filteredFaqs.length }} topik
          </span>
        </div>

        <!-- Horizontal Scrollable Tabs -->
        <div class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <button
            type="button"
            class="px-3.5 py-2 rounded-lg text-xs font-bold shrink-0 transition-colors cursor-pointer font-['Plus_Jakarta_Sans',sans-serif]"
            :class="activeCategory === 'all' ? 'bg-[#03AC0E] text-white shadow-xs' : 'bg-white border border-gray-200 text-gray-700 hover:border-gray-300'"
            @click="activeCategory = 'all'"
          >
            Semua Topik
          </button>
          <button
            v-for="cat in categories"
            :key="cat.id"
            type="button"
            class="px-3.5 py-2 rounded-lg text-xs font-bold shrink-0 transition-colors cursor-pointer flex items-center gap-1.5 font-['Plus_Jakarta_Sans',sans-serif]"
            :class="activeCategory === cat.id ? 'bg-[#03AC0E] text-white shadow-xs' : 'bg-white border border-gray-200 text-gray-700 hover:border-gray-300'"
            @click="activeCategory = cat.id"
          >
            <UIcon :name="cat.icon" class="w-3.5 h-3.5" />
            <span>{{ cat.name }}</span>
          </button>
        </div>

        <!-- ════════════════════════════════════════════════════════════
             ACCORDION FAQ LIST
             ════════════════════════════════════════════════════════════ -->
        <div class="mt-4 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-xs divide-y divide-gray-100">
          <div
            v-for="item in filteredFaqs"
            :key="item.id"
            class="transition-colors"
          >
            <button
              type="button"
              class="w-full px-5 py-4 text-left flex items-center justify-between gap-4 hover:bg-gray-50 transition-colors cursor-pointer"
              :aria-expanded="expandedFaq === item.id"
              @click="toggleFaq(item.id)"
            >
              <div class="flex items-center gap-3 min-w-0">
                <span class="w-6 h-6 rounded-full bg-[#E6F7E9] text-[#03AC0E] text-xs font-bold flex items-center justify-center shrink-0 font-['Plus_Jakarta_Sans',sans-serif]">
                  Q
                </span>
                <span class="text-xs sm:text-sm font-bold text-gray-900 leading-snug font-['Plus_Jakarta_Sans',sans-serif]">
                  {{ item.q }}
                </span>
              </div>
              <UIcon
                name="i-heroicons-chevron-down"
                class="w-4 h-4 text-gray-400 shrink-0 transition-transform duration-200"
                :class="{ 'rotate-180 text-[#03AC0E]': expandedFaq === item.id }"
              />
            </button>

            <!-- Accordion Body -->
            <div
              v-show="expandedFaq === item.id"
              class="px-5 pb-5 pt-1 text-xs sm:text-sm text-gray-600 leading-relaxed pl-14 font-['Open_Sans',sans-serif]"
            >
              <div class="space-y-2">
                <p v-for="(paragraph, pIdx) in item.a" :key="pIdx">
                  {{ paragraph }}
                </p>
              </div>

              <!-- Action Link if provided -->
              <div v-if="item.action" class="mt-3 pt-3 border-t border-gray-100">
                <NuxtLink
                  :to="item.action.to"
                  class="inline-flex items-center gap-1.5 text-xs font-bold text-[#03AC0E] hover:underline font-['Plus_Jakarta_Sans',sans-serif]"
                >
                  <span>{{ item.action.text }}</span>
                  <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" />
                </NuxtLink>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="filteredFaqs.length === 0" class="p-10 text-center text-gray-500">
            <UIcon name="i-heroicons-question-mark-circle" class="w-10 h-10 mx-auto text-gray-300 mb-2" />
            <p class="text-sm font-bold text-gray-800 font-['Plus_Jakarta_Sans',sans-serif]">
              Tidak menemukan jawaban untuk "{{ searchQuery }}"
            </p>
            <p class="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
              Silakan hubungi tim teknisi atau sales kami langsung melalui WhatsApp untuk konsultasi kendala spesifik.
            </p>
          </div>
        </div>
      </section>

      <!-- ════════════════════════════════════════════════════════════
           DIRECT CHANNELS: Tokopedia Care Direct Support Cards
           ════════════════════════════════════════════════════════════ -->
      <section aria-labelledby="direct-support-heading">
        <h2 id="direct-support-heading" class="text-sm font-bold uppercase tracking-wider text-gray-500 mb-3 font-['Plus_Jakarta_Sans',sans-serif]">
          Masih Butuh Bantuan? Hubungi Langsung
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- WhatsApp Sales -->
          <div class="bg-white border border-gray-200 rounded-xl p-5 shadow-xs hover:border-[#03AC0E] transition-colors flex flex-col justify-between">
            <div>
              <div class="flex items-center gap-2.5 mb-2">
                <div class="w-9 h-9 rounded-lg bg-[#E6F7E9] text-[#03AC0E] flex items-center justify-center shrink-0">
                  <UIcon name="i-heroicons-shopping-bag" class="w-4 h-4" />
                </div>
                <div>
                  <h3 class="text-xs font-bold text-gray-900 font-['Plus_Jakarta_Sans',sans-serif]">
                    WhatsApp Divisi Sales
                  </h3>
                  <p class="text-[11px] text-gray-500">Cek stok, faktur pajak, dan pemesanan ritel/B2B</p>
                </div>
              </div>
              <p class="text-xs text-gray-600 leading-relaxed mb-4">
                Layanan konsultasi pemilihan kamera, DVR, NVR, switch PoE, dan diskon kuantitas proyek.
              </p>
            </div>
            <div class="pt-3 border-t border-gray-100 flex items-center justify-between">
              <span class="text-xs font-mono font-bold text-gray-900">+62 821-1777-9003</span>
              <a
                href="https://wa.me/6282117779003?text=Halo%20PasarCCTV%20Sales,%20saya%20butuh%20bantuan%20pemesanan."
                target="_blank"
                rel="noopener"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#03AC0E] hover:bg-[#028C0B] text-white text-xs font-bold rounded-lg transition-colors font-['Plus_Jakarta_Sans',sans-serif]"
              >
                <span>Chat Sales</span>
                <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          <!-- WhatsApp Teknisi -->
          <div class="bg-white border border-gray-200 rounded-xl p-5 shadow-xs hover:border-gray-400 transition-colors flex flex-col justify-between">
            <div>
              <div class="flex items-center gap-2.5 mb-2">
                <div class="w-9 h-9 rounded-lg bg-gray-100 text-gray-800 flex items-center justify-center shrink-0">
                  <UIcon name="i-heroicons-wrench-screwdriver" class="w-4 h-4" />
                </div>
                <div>
                  <h3 class="text-xs font-bold text-gray-900 font-['Plus_Jakarta_Sans',sans-serif]">
                    WhatsApp Divisi Teknisi
                  </h3>
                  <p class="text-[11px] text-gray-500">Klaim garansi, konfigurasi online, dan survei lapangan</p>
                </div>
              </div>
              <p class="text-xs text-gray-600 leading-relaxed mb-4">
                Bantuan setting aplikasi DMSS, Hik-Connect, reset kata sandi, dan perbaikan perangkat.
              </p>
            </div>
            <div class="pt-3 border-t border-gray-100 flex items-center justify-between">
              <span class="text-xs font-mono font-bold text-gray-900">+62 822-1882-8108</span>
              <a
                href="https://wa.me/6282218828108?text=Halo%20Teknisi%20PasarCCTV,%20saya%20butuh%20panduan%20teknis%20perangkat."
                target="_blank"
                rel="noopener"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-900 hover:bg-black text-white text-xs font-bold rounded-lg transition-colors font-['Plus_Jakarta_Sans',sans-serif]"
              >
                <span>Chat Teknisi</span>
                <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

// ─── SEO ─────────────────────────────────────────────────────────
useSeoMeta({
  title: "Pusat Bantuan & Panduan Teknis — PasarCCTV",
  description:
    "Pusat bantuan resmi PasarCCTV. Panduan instalasi kamera CCTV, pairing aplikasi DMSS dan Hik-Connect, klaim garansi resmi distributor, dan jadwal teknisi.",
});

// ─── Search & State ──────────────────────────────────────────────
const searchQuery = ref("");
const activeCategory = ref("all");
const expandedFaq = ref<string | null>("g1");

const popularChips = [
  "Klaim Garansi",
  "Lacak Resi",
  "Setting DMSS",
  "Survei Lokasi",
  "Reset Password DVR",
];

const toggleFaq = (id: string) => {
  expandedFaq.value = expandedFaq.value === id ? null : id;
};

// ─── Quick Actions Data ──────────────────────────────────────────
const quickActions = [
  {
    title: "Lacak Pesanan",
    desc: "Cek progres pengiriman paket dan nomor resi ekspedisi kurir.",
    to: "/helps/shipping",
    icon: "i-heroicons-truck",
    cta: "Cek Status",
  },
  {
    title: "Booking Teknisi",
    desc: "Jadwalkan survei lokasi gratis dan pemasangan rapi pipa conduit.",
    to: "/services/booking",
    icon: "i-heroicons-calendar-days",
    cta: "Atur Jadwal",
  },
  {
    title: "Klaim Garansi & RMA",
    desc: "Prosedur penggantian unit baru untuk cacat produksi tahun ke-1.",
    to: "/contact",
    icon: "i-heroicons-shield-check",
    cta: "Ajukan Klaim",
  },
  {
    title: "Showroom & Lokasi",
    desc: "Kunjungi showroom fisik Bogor dan workshop teknisi Bandung.",
    to: "/store-locator",
    icon: "i-heroicons-building-storefront",
    cta: "Lihat Peta",
  },
];

// ─── Categories ──────────────────────────────────────────────────
const categories = [
  { id: "garansi", name: "Garansi & RMA", icon: "i-heroicons-shield-check" },
  { id: "teknis", name: "Bantuan Teknis", icon: "i-heroicons-wrench-screwdriver" },
  { id: "pemasangan", name: "Jasa Instalasi", icon: "i-heroicons-bolt" },
  { id: "pembelian", name: "Pemesanan & Bayar", icon: "i-heroicons-credit-card" },
  { id: "pengiriman", name: "Pengiriman", icon: "i-heroicons-truck" },
];

// ─── FAQ Data: Real CCTV troubleshooting, No AI Slop ─────────────
const faqs = [
  {
    id: "g1",
    categoryId: "garansi",
    q: "Berapa lama masa garansi resmi kamera CCTV yang dibeli di PasarCCTV?",
    a: [
      "Seluruh unit kamera, DVR, dan NVR resmi distributor (Dahua, Hikvision, Ezviz, Tiandy, Imou) bergaransi 1 hingga 3 tahun tergantung tipe produk.",
      "Tahun pertama mencakup fasilitas penggantian unit baru (replacement) bila ditemukan cacat produksi perangkat keras. Garansi tidak mencakup kerusakan fisik luar, kemasukan air pada tipe non-waterproof, atau tersambar petir (overvoltage).",
    ],
    action: {
      text: "Konsultasikan Klaim Garansi via WhatsApp",
      to: "/contact",
    },
  },
  {
    id: "g2",
    categoryId: "garansi",
    q: "Bagaimana alur pengajuan klaim garansi perangkat yang bermasalah?",
    a: [
      "Langkah 1: Siapkan foto serial number (SN) yang tertera di stiker unit atau dus, beserta nomor nota pembelian.",
      "Langkah 2: Kirim data ke WhatsApp Teknisi Resmi PasarCCTV (+62 822-1882-8108).",
      "Langkah 3: Teknisi akan memandu pengecekan awal secara remote. Jika unit terkonfirmasi rusak, Anda dapat membawa atau mengirimkan unit ke showroom Bogor atau workshop Bandung.",
    ],
  },
  {
    id: "t1",
    categoryId: "teknis",
    q: "Kamera IP tidak muncul online di aplikasi DMSS atau Hik-Connect?",
    a: [
      "Periksa tiga hal mendasar berikut:",
      "1. Pastikan kabel LAN tercolok sempurna pada port PoE switch dan lampu indikator oranye/hijau berkedip aktif.",
      "2. Cek apakah IP DVR/NVR berada dalam subnet yang sama dengan modem internet ISP (misal 192.168.1.xxx).",
      "3. Masuk ke menu Jaringan (Network) DVR/NVR, aktifkan fitur DHCP sekali lalu simpan, kemudian periksa status Cloud P2P harus tertera 'Online'.",
    ],
  },
  {
    id: "t2",
    categoryId: "teknis",
    q: "Bagaimana cara mereset kata sandi DVR atau NVR yang lupa?",
    a: [
      "Demi keamanan, reset password DVR/NVR Dahua atau Hikvision memerlukan validasi kode QR GUID atau file reset XML resmi dari SADP Tool.",
      "Buka layar login DVR, klik 'Forgot Password', lalu scan QR code yang muncul menggunakan aplikasi akun terdaftar, atau hubungi teknisi kami untuk mendapatkan security code harian distributor resmi.",
    ],
  },
  {
    id: "p1",
    categoryId: "pemasangan",
    q: "Apakah survei lokasi sebelum pemasangan CCTV dikenakan biaya?",
    a: [
      "Survei lokasi di wilayah Kota/Kabupaten Bogor, Depok, Bandung Raya, dan Cimahi tidak dikenakan biaya komitmen awal.",
      "Teknisi kami akan datang mengukur jalur kabel, menentukan blind spot, menghitung kebutuhan pipa conduit, dan memberikan penawaran tertulis transparan sebelum Anda menyetujui pengerjaan.",
    ],
    action: {
      text: "Jadwalkan Survei Teknisi Sekarang",
      to: "/services/booking",
    },
  },
  {
    id: "p2",
    categoryId: "pemasangan",
    q: "Apa perbedaan instalasi standar dengan pipa conduit protector?",
    a: [
      "Instalasi pipa conduit membungkus seluruh bentangan kabel UTP/RG59 di dalam pipa PVC khusus kelistrikan (clipsal/high impact).",
      "Hal ini melindungi kabel dari gigitan tikus, paparan sinar UV matahari, gesekan sudut plafon, dan membuat jalur kabel terlihat rapi standar gedung perkantoran dan industri.",
    ],
  },
  {
    id: "b1",
    categoryId: "pembelian",
    q: "Apakah PasarCCTV melayani faktur pajak dan pengadaan B2B perusahaan?",
    a: [
      "Ya. Kami menerbitkan Faktur Pajak PPN resmi dan dokumen penawaran resmi (Surat Penawaran Harga, Invoice, Kwitansi Bermaterai) untuk instansi pemerintah, BUMN, pabrik, dan korporat.",
      "Kirimkan NPWP perusahaan dan daftar kebutuhan perangkat ke email cs@pasarcctv.com atau hubungi WhatsApp Sales kami.",
    ],
  },
  {
    id: "b2",
    categoryId: "pembelian",
    q: "Metode pembayaran apa saja yang didukung?",
    a: [
      "Kami menerima Transfer Bank (BCA, Mandiri, BNI, BRI), Virtual Account otomatis, QRIS untuk transaksi ritel, serta termin pembayaran (Term of Payment) khusus proyek korporasi yang lolos verifikasi legalitas.",
    ],
  },
  {
    id: "s1",
    categoryId: "pengiriman",
    q: "Berapa lama pesanan unit CCTV diproses dan dikirim?",
    a: [
      "Pesanan barang jadi sebelum pukul 15.00 WIB dikirim pada hari kerja yang sama menggunakan JNE, J&T, SiCepat, atau kurir instan GoSend/GrabExpress untuk wilayah Bogor dan Bandung.",
      "Pengiriman luar pulau menggunakan packing kayu dan asuransi penuh untuk melindungi sensor lensa kaca kamera dan hard disk rekaman.",
    ],
  },
];

// ─── Computed FAQ Filter ─────────────────────────────────────────
const filteredFaqs = computed(() => {
  let result = faqs;

  if (activeCategory.value !== "all") {
    result = result.filter((item) => item.categoryId === activeCategory.value);
  }

  const query = searchQuery.value.trim().toLowerCase();
  if (query) {
    result = result.filter(
      (item) =>
        item.q.toLowerCase().includes(query) ||
        item.a.some((p) => p.toLowerCase().includes(query))
    );
  }

  return result;
});
</script>