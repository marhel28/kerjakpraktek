<script setup lang="ts">
import { computed } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, A11y, FreeMode } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/free-mode'
// Pastikan path import CardPerItems.vue sesuai dengan struktur folder kamu
import CardPerItem from './CardPerItems.vue'

const modules = [Navigation, A11y, FreeMode]

// 🔥 SSR + smart cache
const { data, pending, error } = await useFetch('/api/getpopular', {
  key: 'popular:home:v2',
  query: { limit: 10 },

  server: true,
  lazy: true, // 🔥 UBAH KE TRUE: Agar skeleton langsung render tanpa menunggu API selesai

  // 🔥 dedupe request
  dedupe: 'defer',

  // 🔥 cache reuse
  getCachedData: (key, nuxtApp) =>
    nuxtApp.payload.data[key] ?? nuxtApp.static.data[key],
})

// 🔥 transform langsung (lebih efisien dari computed besar)
const popularProducts = computed(() => {
  if (!data.value?.items) return []

  return data.value.items.map((item: any) => ({
    uuid: item.uuid,
    slug: item.slug,
    image: item.image || '/images/no-image.webp',
    brand: item.brand ?? 'NO BRAND',
    title: item.title,
    price: item.price,
    original_price: item.original_price ?? item.price,
    discount_percentage: item.discount_percentage ?? 0,
    terjual: item.terjual ?? 0,
    type: item.type ?? '',
    category: item.category ?? '',
    subcategory: item.subcategory ?? '',
    specs: item.specs ?? {},
  }))
})

const hasProducts = computed(() => popularProducts.value.length > 0)

// 🔥 format lebih clean
const formatTerjual = (n: number): string => {
  if (!n) return '0'
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}jt`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}rb`
  return `${n}`
}
</script>

<template>
  <!--
    Schema.org ItemList → Google carousel product di SERP
    aria-labelledby → aksesibilitas heading hierarchy
  -->
  <section
    v-if="pending || hasProducts"
    aria-labelledby="popular-heading"
    itemscope
    itemtype="https://schema.org/ItemList"
    class="w-full py-6 sm:py-10"
  >
    <meta itemprop="name" content="Produk Populer" />
    <meta itemprop="description" content="Produk CCTV terlaris minggu ini" />

    <div class="max-w-[1400px] overflow-x-hidden mx-auto px-3 sm:px-6">

      <!-- ── Header ──────────────────────────────────────────────── -->
      <header class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2.5">
          <!-- Flame icon + label -->
          <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-orange-50 shrink-0" aria-hidden="true">
            <UIcon name="i-heroicons-fire-solid" class="w-5 h-5 text-orange-500" />
          </div>
          <div>
            <h2
              id="popular-heading"
              class="text-base sm:text-xl font-extrabold text-gray-900 leading-tight tracking-tight"
            >
              Produk Populer
            </h2>
            <p class="hidden sm:block text-xs text-gray-400 font-medium mt-0.5">
              Paling banyak dibeli minggu ini
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Desktop: lihat semua -->
          <NuxtLink
            to="/category/popular"
            class="hidden sm:inline-flex items-center gap-1.5 text-xs font-bold text-green-600 hover:text-green-700 bg-green-50 hover:bg-green-100 px-4 py-2 rounded-full transition-colors whitespace-nowrap"
            aria-label="Lihat semua produk populer"
          >
            Lihat Semua
            <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" aria-hidden="true" />
          </NuxtLink>

          <!-- Nav arrows -->
          <div
            class="flex items-center gap-1.5"
            role="group"
            aria-label="Kontrol slider produk populer"
          >
            <button
              aria-label="Produk sebelumnya"
              class="pop-prev flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-500 hover:bg-green-600 hover:border-green-600 hover:text-white shadow-sm transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <UIcon name="i-heroicons-chevron-left-20-solid" class="w-4 h-4" aria-hidden="true" />
            </button>
            <button
              aria-label="Produk selanjutnya"
              class="pop-next flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-500 hover:bg-green-600 hover:border-green-600 hover:text-white shadow-sm transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <UIcon name="i-heroicons-chevron-right-20-solid" class="w-4 h-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </header>

      <!-- ── Skeleton (Langsung muncul berkat lazy: true) ────────── -->
      <div
        v-if="pending"
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2.5"
        role="status"
        aria-busy="true"
        aria-label="Memuat produk populer"
      >
        <div
          v-for="i in 5"
          :key="i"
          class="bg-white rounded-xl border border-gray-100 overflow-hidden"
          aria-hidden="true"
        >
          <USkeleton class="h-40 w-full rounded-none" />
          <div class="p-3 space-y-2">
            <USkeleton class="h-3 w-1/3" />
            <USkeleton class="h-3.5 w-full" />
            <USkeleton class="h-3.5 w-4/5" />
            <USkeleton class="h-5 w-1/2 mt-2" />
            <USkeleton class="h-3 w-2/3" />
          </div>
        </div>
      </div>

      <!-- ── Swiper ──────────────────────────────────────────────── -->
      <div v-else class="pop-swiper-wrap">
        <Swiper
          :modules="modules"
          :navigation="{ prevEl: '.pop-prev', nextEl: '.pop-next' }"
          :free-mode="{ enabled: true, sticky: false }"
          :slides-per-view="2.2"
          :space-between="10"
          :grab-cursor="true"
          :breakpoints="{
            480:  { slidesPerView: 2.4, spaceBetween: 10 },
            640:  { slidesPerView: 3.2, spaceBetween: 12 },
            768:  { slidesPerView: 3.5, spaceBetween: 12 },
            1024: { slidesPerView: 4.5, spaceBetween: 14 },
            1280: { slidesPerView: 5,   spaceBetween: 14 },
          }"
          class="!pb-1 !pt-0.5"
        >
          <SwiperSlide
            v-for="(item, index) in popularProducts"
            :key="item.uuid"
            itemprop="itemListElement"
            itemscope
            itemtype="https://schema.org/ListItem"
            :style="{ animationDelay: `${index * 45}ms` }"
            class="pop-card-slide"
          >
            <meta itemprop="position" :content="String(index + 1)" />

            <NuxtLink
              :to="`/product/${item.uuid}`"
              itemprop="url"
              class="pop-card group block bg-white rounded-xl border border-gray-100 overflow-hidden hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:outline-none"
              :aria-label="`${item.title} — Rp ${item.price?.toLocaleString('id-ID')}`"
            >
              <!-- Gambar + badge diskon -->
              <div class="relative overflow-hidden bg-gray-50">
                <NuxtImg
                  :src="item.image"
                  :alt="item.title"
                  width="280"
                  height="280"
                  class="w-full aspect-square object-contain p-2 group-hover:scale-105 transition-transform duration-300"
                  loading="lazy"
                  itemprop="image"
                />

                <!-- Badge diskon -->
                <span
                  v-if="item.discount_percentage > 0"
                  class="absolute top-2 left-2 bg-red-500 text-white text-[10px] font-extrabold px-1.5 py-0.5 rounded-md leading-none"
                  aria-label="Diskon {{ item.discount_percentage }}%"
                >
                  {{ item.discount_percentage }}%
                </span>

                <!-- Badge terjual -->
                <span
                  v-if="item.terjual > 0"
                  class="absolute bottom-2 left-2 bg-black/60 backdrop-blur-sm text-white text-[10px] font-semibold px-1.5 py-0.5 rounded-md leading-none"
                >
                  {{ formatTerjual(item.terjual) }}+ terjual
                </span>
              </div>

              <!-- Info produk -->
              <div class="p-2.5 sm:p-3" itemprop="offers" itemscope itemtype="https://schema.org/Offer">
                <meta itemprop="priceCurrency" content="IDR" />
                <meta itemprop="price" :content="String(item.price)" />
                <meta itemprop="availability" content="https://schema.org/InStock" />

                <!-- Brand -->
                <p class="text-[10px] sm:text-xs text-gray-400 font-semibold uppercase tracking-wide truncate mb-0.5" itemprop="brand">
                  {{ item.brand }}
                </p>

                <!-- Judul -->
                <h3
                  class="text-xs sm:text-sm text-gray-800 font-medium leading-snug line-clamp-2 mb-2"
                  itemprop="name"
                >
                  {{ item.title }}
                </h3>

                <!-- Harga -->
                <div class="space-y-0.5">
                  <p class="text-sm sm:text-base font-extrabold text-gray-900 leading-none">
                    Rp{{ item.price?.toLocaleString('id-ID') }}
                  </p>
                  <p
                    v-if="item.discount_percentage > 0"
                    class="text-[11px] text-gray-400 line-through leading-none"
                  >
                    Rp{{ item.original_price?.toLocaleString('id-ID') }}
                  </p>
                </div>
              </div>
            </NuxtLink>
          </SwiperSlide>
        </Swiper>
      </div>

      <!-- Lihat semua — mobile -->
      <div class="mt-4 sm:hidden">
        <NuxtLink
          to="/category/popular"
          class="flex items-center justify-center gap-1.5 w-full py-2.5 rounded-xl border border-green-200 text-green-600 text-sm font-bold bg-green-50 hover:bg-green-100 transition-colors"
          aria-label="Lihat semua produk populer"
        >
          Lihat Semua Produk
          <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" aria-hidden="true" />
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ── Slide stagger masuk ──────────────────────────────────────────── */
@keyframes popIn {
  from { opacity: 0; transform: translateY(12px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0)  scale(1); }
}

.pop-card-slide {
  opacity: 0;
  animation: popIn 0.35s ease-out forwards;
  will-change: transform, opacity;
}

/* ── Swiper: overflow visible agar shadow card tidak crop ─────────── */
.pop-swiper-wrap :deep(.swiper) {
  overflow: visible !important;
  clip-path: inset(-20px -100vw -20px -100vw);
}

/* Hide default Swiper arrows — kita pakai custom buttons */
.pop-swiper-wrap :deep(.swiper-button-next),
.pop-swiper-wrap :deep(.swiper-button-prev) {
  display: none !important;
}

/* ── Reduced motion ──────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .pop-card-slide {
    animation: none;
    opacity: 1;
  }
}
</style>