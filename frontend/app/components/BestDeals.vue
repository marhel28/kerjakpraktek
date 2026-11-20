<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Navigation, A11y, FreeMode } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/free-mode";
import CardPerItems from "./CardPerItems.vue";

const modules = [Navigation, A11y, FreeMode];

const { data, pending } = await useFetch("/api/bestdeals", {
  key: "best-deals-home",
  query: { limit: 16 },
  server: true,
  lazy: true,
});

// ─── Countdown Timer ke Tengah Malam (Amazon Flash Deal Style) ───
const timeLeft = ref({ hours: '08', minutes: '45', seconds: '20' })
let countdownTimer: any = null

const updateCountdown = () => {
  const now = new Date()
  const midnight = new Date(now)
  midnight.setHours(24, 0, 0, 0)
  const diff = midnight.getTime() - now.getTime()
  
  if (diff > 0) {
    const h = Math.floor(diff / (1000 * 60 * 60))
    const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    const s = Math.floor((diff % (1000 * 60)) / 1000)
    timeLeft.value = {
      hours: String(h).padStart(2, '0'),
      minutes: String(m).padStart(2, '0'),
      seconds: String(s).padStart(2, '0')
    }
  }
}

onMounted(() => {
  updateCountdown()
  countdownTimer = setInterval(updateCountdown, 1000)
})

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})

// ─── Filter Kategori Deals ───
const activeFilter = ref('all')
const dealFilters = [
  { id: 'all', label: 'Semua Deals' },
  { id: 'paket', label: 'Paket Komplit' },
  { id: 'kamera', label: 'Kamera CCTV' },
  { id: 'dvr', label: 'Perekam & Storage' }
]

const dealProducts = computed(() => {
  if (!data.value?.items) return [];
  return data.value.items.map((item: any) => ({
    uuid: item.uuid,
    slug: item.slug,
    image: item.image || "/images/no-image.webp",
    brand: item.brand ?? "NO BRAND",
    title: item.title,
    price: item.price,
    original_price: item.original_price ?? item.price,
    discount_percentage: item.discount_percentage ?? 0,
    terjual: item.terjual ?? 0,
    type: item.type ?? "",
    category: item.category ?? "",
    subcategory: item.subcategory ?? "",
    specs: item.specs ?? {},
  }));
});

const filteredProducts = computed(() => {
  if (activeFilter.value === 'all') return dealProducts.value
  const f = activeFilter.value.toLowerCase()
  return dealProducts.value.filter((item: any) => {
    const title = (item.title || '').toLowerCase()
    const cat = (item.category || '').toLowerCase()
    const sub = (item.subcategory || '').toLowerCase()
    if (f === 'paket') return title.includes('paket') || cat.includes('paket') || sub.includes('paket')
    if (f === 'kamera') return title.includes('kamera') || title.includes('camera') || cat.includes('kamera')
    if (f === 'dvr') return title.includes('dvr') || title.includes('nvr') || title.includes('hdd') || cat.includes('storage')
    return true
  })
})

const hasDeals = computed(() => dealProducts.value.length > 0);

// Hemat terbesar untuk highlight badge
const topDiscount = computed(() =>
  dealProducts.value.length > 0
    ? Math.max(...dealProducts.value.map((p: any) => p.discount_percentage || 0))
    : 0
);
</script>

<template>
  <section
    v-if="pending || hasDeals"
    aria-labelledby="deals-heading"
    itemscope
    itemtype="https://schema.org/ItemList"
    class="w-full py-4 sm:py-6"
  >
    <meta itemprop="name" content="Deals Terbaik & Flash Sale" />

    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      
      <!-- Container Kartu Amazon Deals Utama -->
      <div class="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-6 border border-gray-200/90 shadow-xs">
        
        <!-- ── Header Section ── -->
        <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
          
          <!-- Sisi Kiri: Judul, Badge Diskon, & Countdown Timer -->
          <div class="flex flex-wrap items-center gap-3 sm:gap-4">
            <div class="flex items-center gap-2">
              <span class="w-1.5 h-6 bg-red-600 rounded-full" aria-hidden="true" />
              <h2
                id="deals-heading"
                class="text-lg sm:text-xl font-extrabold text-gray-900 tracking-tight flex items-center gap-2"
              >
                Flash Sale & Deals Terbaik
              </h2>
            </div>

            <!-- Top Discount Badge -->
            <span
              v-if="topDiscount > 0"
              class="inline-flex items-center gap-1 bg-red-50 text-red-600 text-xs font-bold px-2.5 py-0.5 rounded-full border border-red-200"
            >
              <UIcon name="i-heroicons-fire" class="w-3.5 h-3.5" aria-hidden="true" />
              Diskon s.d {{ topDiscount }}%
            </span>

            <!-- Amazon Style Countdown Box -->
            <div class="flex items-center gap-1.5 bg-gray-900 text-white px-2.5 py-1 rounded-lg text-xs font-bold tracking-wider shadow-2xs">
              <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5 text-amber-400" />
              <span class="text-gray-400 text-[10px] uppercase mr-0.5">Berakhir:</span>
              <span class="bg-gray-800 px-1.5 py-0.5 rounded text-amber-300 font-mono">{{ timeLeft.hours }}</span>
              <span class="text-gray-400">:</span>
              <span class="bg-gray-800 px-1.5 py-0.5 rounded text-amber-300 font-mono">{{ timeLeft.minutes }}</span>
              <span class="text-gray-400">:</span>
              <span class="bg-gray-800 px-1.5 py-0.5 rounded text-amber-300 font-mono">{{ timeLeft.seconds }}</span>
            </div>
          </div>

          <!-- Sisi Kanan: Quick Category Filters & Slider Controls -->
          <div class="flex items-center justify-between md:justify-end gap-3 w-full md:w-auto">
            
            <!-- Category Filter Tabs -->
            <div class="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
              <button
                v-for="flt in dealFilters"
                :key="flt.id"
                @click="activeFilter = flt.id"
                class="text-xs font-semibold px-2.5 py-1 rounded-full transition-all shrink-0 border"
                :class="activeFilter === flt.id 
                  ? 'bg-[#03AC0E] text-white border-[#03AC0E] shadow-2xs' 
                  : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'"
              >
                {{ flt.label }}
              </button>
            </div>

            <!-- Navigation Controls (Desktop) -->
            <div class="hidden sm:flex items-center gap-1.5 shrink-0 pl-2 border-l border-gray-200">
              <button
                aria-label="Previous deals"
                class="deals-prev w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-[#03AC0E] hover:text-white hover:border-[#03AC0E] disabled:opacity-30 transition-all shadow-2xs"
              >
                <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
              </button>
              <button
                aria-label="Next deals"
                class="deals-next w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-[#03AC0E] hover:text-white hover:border-[#03AC0E] disabled:opacity-30 transition-all shadow-2xs"
              >
                <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
              </button>
            </div>

          </div>
        </header>

        <!-- ── Skeleton loading ── -->
        <div v-if="pending" class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 mt-5">
          <div
            v-for="i in 6"
            :key="i"
            class="bg-white rounded-xl border border-gray-100 p-3 space-y-2 animate-pulse"
          >
            <div class="h-36 bg-gray-100 rounded-lg w-full" />
            <div class="h-3 bg-gray-100 rounded w-1/3" />
            <div class="h-4 bg-gray-100 rounded w-full" />
            <div class="h-4 bg-gray-100 rounded w-1/2" />
          </div>
        </div>

        <!-- ── Carousel Produk Deals ── -->
        <div v-else class="relative mt-4">
          <Swiper
            :modules="modules"
            :navigation="{ prevEl: '.deals-prev', nextEl: '.deals-next' }"
            :free-mode="{ enabled: true, sticky: false }"
            :slides-per-view="2.1"
            :space-between="12"
            :breakpoints="{
              480: { slidesPerView: 2.3, spaceBetween: 12 },
              640: { slidesPerView: 3.2, spaceBetween: 14 },
              768: { slidesPerView: 4.2, spaceBetween: 16 },
              1024: { slidesPerView: 5.2, spaceBetween: 16 },
              1280: { slidesPerView: 6.2, spaceBetween: 18 },
            }"
            class="!py-2"
          >
            <SwiperSlide
              v-for="(item, index) in filteredProducts"
              :key="item.uuid"
              :itemprop="'itemListElement'"
            >
              <meta itemprop="position" :content="String(index + 1)" />
              <CardPerItems v-bind="item" />
            </SwiperSlide>
          </Swiper>
        </div>

        <!-- ── Footer Micro-link ── -->
        <div class="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs">
          <span class="text-gray-400 font-medium">
            *Promo harga berlaku selama stok unit & slot diskon masih tersedia
          </span>
          <NuxtLink
            to="/search?sort=discount"
            class="font-bold text-[#03AC0E] hover:underline flex items-center gap-1"
          >
            Lihat Semua Produk Diskon
            <UIcon name="i-heroicons-arrow-small-right" class="w-4 h-4" />
          </NuxtLink>
        </div>

      </div>
    </div>
  </section>
</template>

<style scoped>
:deep(.swiper-slide) {
  height: auto !important;
  display: flex !important;
}
:deep(.swiper-slide > *) {
  width: 100% !important;
  height: 100% !important;
}
</style>
