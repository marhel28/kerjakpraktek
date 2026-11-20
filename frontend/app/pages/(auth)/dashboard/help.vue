<script setup lang="ts">
import { ref, computed } from "vue";

definePageMeta({
  layout: "auth",
});

const config = useRuntimeConfig();
const searchQuery = ref("");
const activeCategory = ref("all");
const openFaqIndex = ref<number | null>(null);

const categories = [
  { id: "all", label: "Semua Bantuan", icon: "i-heroicons-squares-2x2" },
  { id: "order", label: "Pesanan & Pengiriman", icon: "i-heroicons-truck" },
  { id: "installation", label: "Jasa Teknisi & Pasang", icon: "i-heroicons-wrench-screwdriver" },
  { id: "payment", label: "Pembayaran & Tagihan", icon: "i-heroicons-credit-card" },
  { id: "warranty", label: "Garansi & Retur", icon: "i-heroicons-shield-check" },
];

const faqs = [
  {
    category: "order",
    question: "Bagaimana cara melacak pesanan CCTV saya?",
    answer:
      "Setelah pesanan berhasil dikonfirmasi dan dikirim oleh kurir kami, nomor resi otomatis tersedia di menu 'Pesanan Saya'. Anda juga dapat mengecek timeline pengiriman langsung melalui menu 'Lacak Pesanan' pada top navigation.",
  },
  {
    category: "installation",
    question: "Bagaimana alur pemesanan jasa teknisi & pemasangan CCTV?",
    answer:
      "Pilih paket jasa pemasangan di menu Layanan Booking. Tim admin dan teknisi kami akan menghubungi Anda via WhatsApp dalam waktu maksimal 2 jam untuk survey denah, penentuan titik kabel, dan konfirmasi jadwal kunjungan ke lokasi.",
  },
  {
    category: "installation",
    question: "Berapa lama estimasi pengerjaan instalasi CCTV?",
    answer:
      "Untuk paket 2-4 kamera rumah standar, instalasi biasanya selesai dalam 4-6 jam kerja di hari yang sama. Untuk project perkantoran atau pabrik di atas 8 kamera, teknisi akan memberikan jadwal bertahap 1-2 hari kerja.",
  },
  {
    category: "payment",
    question: "Metode pembayaran apa saja yang didukung PasarCCTV?",
    answer:
      "Kami menerima Transfer Virtual Account (BCA, Mandiri, BNI, BRI), QRIS, GoPay, OVO, ShopeePay, serta Kartu Kredit dengan verifikasi otomatis Midtrans. Kami juga melayani Term of Payment (TOP) khusus instansi dan perusahaan terverifikasi.",
  },
  {
    category: "warranty",
    question: "Berapa lama masa garansi produk dan garansi instalasi?",
    answer:
      "Semua kamera CCTV (Dahua, Hikvision, Ezviz, Imou) bergaransi resmi distributor selama 1-2 tahun untuk pergantian unit atau perbaikan service. Khusus jasa instalasi teknisi kami, kami berikan jaminan garansi setting dan kerapihan kabel selama 30 hari kalender.",
  },
  {
    category: "warranty",
    question: "Bagaimana cara klaim garansi jika kamera mengalami error / offline?",
    answer:
      "Hubungi Customer Care PasarCCTV via Chat atau WhatsApp dengan melampirkan Invoice ID dan video kendala. Tim teknis kami akan melakukan troubleshooting remote terlebih dahulu. Jika kerusakan hardware, kurir pick-up atau teknisi kami siap menjemput unit.",
  },
];

const filteredFaqs = computed(() => {
  return faqs.filter((item) => {
    const matchCat = activeCategory.value === "all" || item.category === activeCategory.value;
    const matchQuery =
      !searchQuery.value.trim() ||
      item.question.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.answer.toLowerCase().includes(searchQuery.value.toLowerCase());
    return matchCat && matchQuery;
  });
});

const toggleFaq = (index: number) => {
  openFaqIndex.value = openFaqIndex.value === index ? null : index;
};
</script>

<template>
  <div class="font-['Plus_Jakarta_Sans',sans-serif] text-gray-900">
    <!-- Header Banner Amazon Help Hub x Tokopedia Care -->
    <div class="bg-gradient-to-r from-emerald-800 to-[#03AC0E] p-6 sm:p-8 text-white rounded-t-xl relative overflow-hidden">
      <div class="relative z-10 max-w-2xl">
        <div class="inline-flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-2 backdrop-blur-xs">
          <UIcon name="i-heroicons-question-mark-circle" class="w-4 h-4" />
          Pusat Bantuan & Layanan Pelanggan
        </div>
        <h1 class="text-xl sm:text-2xl font-bold tracking-tight mb-2">
          Ada yang bisa kami bantu hari ini?
        </h1>
        <p class="text-xs sm:text-sm text-emerald-100 mb-5 leading-relaxed">
          Temukan jawaban cepat seputar kendala pengiriman, pesanan, garansi kamera, hingga panduan panggil teknisi CCTV.
        </p>

        <!-- Search Bar Help -->
        <div class="relative w-full">
          <UIcon
            name="i-heroicons-magnifying-glass"
            class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2"
          />
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Ketik kata kunci (misal: garansi, jasa pasang, lacak resi)..."
            class="w-full bg-white text-gray-900 pl-11 pr-4 py-3 rounded-xl text-xs sm:text-sm font-semibold outline-none shadow-sm focus:ring-2 focus:ring-emerald-300 transition-all placeholder:text-gray-400 placeholder:font-normal"
          />
        </div>
      </div>
    </div>

    <div class="p-5 sm:p-6 space-y-8 bg-gray-50/50">
      <!-- 4 Quick Contact Solution Tiles (Amazon Style) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
        <a
          :href="`https://wa.me/${config.public.waNumber}?text=Halo%20Admin%20PasarCCTV,%20saya%20butuh%20bantuan`"
          target="_blank"
          class="p-4 bg-white rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all group flex items-start gap-3.5"
        >
          <div class="p-2.5 rounded-xl bg-emerald-50 text-[#03AC0E] shrink-0">
            <UIcon name="i-heroicons-phone" class="w-6 h-6" />
          </div>
          <div>
            <h3 class="text-sm font-extrabold text-gray-900 group-hover:text-[#03AC0E] transition-colors">
              WhatsApp CS
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">Respon teknis & konsultasi cepat (08:00 - 21:00)</p>
          </div>
        </a>

        <button
          type="button"
          class="p-4 bg-white rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all group flex items-start gap-3.5 cursor-pointer"
          @click="usePesanStore().onPopupOpen()"
        >
          <div class="p-2.5 rounded-xl bg-blue-50 text-blue-600 shrink-0">
            <UIcon name="i-heroicons-chat-bubble-left-right" class="w-6 h-6" />
          </div>
          <div>
            <h3 class="text-sm font-extrabold text-gray-900 group-hover:text-[#03AC0E] transition-colors">
              Live Chat Internal
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">Terhubung dengan customer care di aplikasi</p>
          </div>
        </button>

        <NuxtLink
          to="/dashboard/orders"
          class="p-4 bg-white rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all group flex items-start gap-3.5"
        >
          <div class="p-2.5 rounded-xl bg-amber-50 text-amber-600 shrink-0">
            <UIcon name="i-heroicons-arrow-path" class="w-6 h-6" />
          </div>
          <div>
            <h3 class="text-sm font-extrabold text-gray-900 group-hover:text-[#03AC0E] transition-colors">
              Komplain Pesanan
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">Pemeriksaan paket rusak, hilang, atau keliru</p>
          </div>
        </NuxtLink>

        <NuxtLink
          to="/dashboard/jasa"
          class="p-4 bg-white rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all group flex items-start gap-3.5"
        >
          <div class="p-2.5 rounded-xl bg-purple-50 text-purple-600 shrink-0">
            <UIcon name="i-heroicons-wrench-screwdriver" class="w-6 h-6" />
          </div>
          <div>
            <h3 class="text-sm font-extrabold text-gray-900 group-hover:text-[#03AC0E] transition-colors">
              Jadwal Teknisi
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">Reschedule atau cek status kedatangan tim pasang</p>
          </div>
        </NuxtLink>
      </div>

      <!-- FAQ Section (Tokopedia Accordion Clean) -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5 sm:p-6 shadow-2xs space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-4">
          <div>
            <h2 class="text-base font-extrabold text-gray-900 tracking-tight">
              Pertanyaan yang Sering Diajukan (FAQ)
            </h2>
            <p class="text-xs text-gray-500 mt-0.5">
              Panduan lengkap panduan pembelian, pemasangan, dan purnajual CCTV.
            </p>
          </div>

          <!-- Category Filter Pills -->
          <div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-1">
            <button
              v-for="cat in categories"
              :key="cat.id"
              type="button"
              @click="activeCategory = cat.id"
              class="px-3 py-1.5 rounded-xl text-xs font-bold shrink-0 transition-all border"
              :class="
                activeCategory === cat.id
                  ? 'bg-[#03AC0E] text-white border-[#03AC0E] shadow-2xs'
                  : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50 hover:text-gray-900'
              "
            >
              {{ cat.label }}
            </button>
          </div>
        </div>

        <!-- FAQ Accordion List -->
        <div class="divide-y divide-gray-200">
          <div
            v-for="(faq, idx) in filteredFaqs"
            :key="idx"
            class="py-3.5"
          >
            <button
              type="button"
              class="w-full text-left flex items-center justify-between gap-3 group py-1"
              @click="toggleFaq(idx)"
            >
              <span
                class="text-xs sm:text-sm font-bold text-gray-800 group-hover:text-[#03AC0E] transition-colors"
                :class="openFaqIndex === idx ? 'text-[#03AC0E]' : ''"
              >
                {{ faq.question }}
              </span>
              <div
                class="w-6 h-6 rounded-full flex items-center justify-center bg-gray-100 group-hover:bg-emerald-50 text-gray-500 group-hover:text-[#03AC0E] transition-all shrink-0"
                :class="openFaqIndex === idx ? 'rotate-180 bg-emerald-50 text-[#03AC0E]' : ''"
              >
                <UIcon name="i-heroicons-chevron-down" class="w-4 h-4" />
              </div>
            </button>

            <Transition
              enter-active-class="transition duration-150 ease-out"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition duration-100 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-1"
            >
              <div
                v-if="openFaqIndex === idx"
                class="mt-2 text-xs sm:text-sm text-gray-600 leading-relaxed bg-gray-50/70 p-4 rounded-xl border border-gray-100"
              >
                {{ faq.answer }}
              </div>
            </Transition>
          </div>

          <div
            v-if="!filteredFaqs.length"
            class="py-10 text-center text-xs text-gray-500 font-semibold"
          >
            Tidak ada jawaban yang cocok dengan kata kunci "{{ searchQuery }}".
          </div>
        </div>
      </div>

      <!-- Jam Operasional & Alamat Toko -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5 sm:p-6 shadow-2xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div class="flex items-center gap-3.5">
          <div class="p-3 rounded-2xl bg-emerald-50 text-[#03AC0E] shrink-0 border border-emerald-100">
            <UIcon name="i-heroicons-map-pin" class="w-6 h-6" />
          </div>
          <div>
            <h3 class="text-sm font-extrabold text-gray-900">
              Workshop & Service Center PasarCCTV
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">
              Melayani konsultasi langsung, pengujian perangkat CCTV, dan klaim garansi di Bandung & Cimahi.
            </p>
          </div>
        </div>
        <NuxtLink
          to="/store-locator"
          class="bg-gray-900 hover:bg-black text-white px-4 py-2.5 rounded-xl text-xs font-bold transition-all shadow-2xs shrink-0 self-start md:self-auto flex items-center gap-1.5"
        >
          <UIcon name="i-heroicons-building-storefront" class="w-4 h-4" />
          Petunjuk Arah Toko
        </NuxtLink>
      </div>
    </div>
  </div>
</template>