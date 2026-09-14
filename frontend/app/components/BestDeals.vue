<script setup lang="ts">
import { computed } from "vue";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Navigation, A11y, FreeMode } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/free-mode";
import CardPerItems from "./CardPerItems.vue";

const modules = [Navigation, A11y, FreeMode];

const { data, pending } = await useFetch("/api/bestdeals", {
  key: "best-deals-home",
  query: { limit: 12 },
  server: true,
  lazy: true,
});

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
    class="w-full py-6 lg:py-10"
  >
    <meta itemprop="name" content="Deals Terbaik" />

    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      <!-- ── Header ── -->
      <header class="flex items-end justify-between mb-6 border-b border-gray-100 pb-4">
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2.5">
            <!-- Aksen warna merah/oranye untuk deals -->
            <div class="flex items-center gap-1" aria-hidden="true">
              <span class="w-1.5 h-6 bg-red-500 rounded-full" />
              <span class="w-1.5 h-4 bg-orange-400 rounded-full" />
            </div>
            <h2
              id="deals-heading"
              class="text-lg lg:text-xl font-black text-gray-900 tracking-tighter uppercase italic"
            >
              Deals Terbaik
            </h2>
            <!-- Badge hemat terbesar -->
            <span
              v-if="topDiscount > 0"
              class="hidden sm:inline-flex items-center gap-1 bg-red-50 text-red-600 text-[10px] font-black px-2 py-0.5 rounded-full border border-red-200/60"
            >
              <UIcon name="i-heroicons-fire" class="w-3 h-3" aria-hidden="true" />
              s.d {{ topDiscount }}% OFF
            </span>
          </div>
          <p class="text-[10px] lg:text-[11px] font-bold text-gray-400 uppercase tracking-[0.2em]">
            Harga Terbaik Hari Ini
          </p>
        </div>

        <div class="flex items-center gap-4">
          <NuxtLink
            to="/search?sort=discount"
            class="hidden lg:flex items-center gap-1.5 text-[10px] font-black text-gray-400 hover:text-red-500 transition-colors uppercase tracking-[0.2em]"
          >
            Lihat Semua
            <UIcon name="i-heroicons-arrow-small-right" class="w-4 h-4" />
          </NuxtLink>

          <!-- Navigation Controls -->
          <div class="flex items-center gap-2">
            <button
              aria-label="Previous deals"
              class="deals-prev w-8 h-8 flex items-center justify-center rounded-lg border border-gray-100 bg-white text-gray-400 hover:bg-red-500 hover:text-white disabled:opacity-30 transition-all shadow-sm"
            >
              <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
            </button>
            <button
              aria-label="Next deals"
              class="deals-next w-8 h-8 flex items-center justify-center rounded-lg border border-gray-100 bg-white text-gray-400 hover:bg-red-500 hover:text-white disabled:opacity-30 transition-all shadow-sm"
            >
              <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <!-- ── Skeleton loading ── -->
      <div v-if="pending" class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        <div
          v-for="i in 6"
          :key="i"
          class="bg-white rounded-xl border border-gray-50 overflow-hidden"
        >
          <USkeleton class="h-36 w-full rounded-none" />
          <div class="p-3 space-y-2">
            <USkeleton class="h-2 w-1/4" />
            <USkeleton class="h-3 w-full" />
            <USkeleton class="h-3 w-3/4" />
            <USkeleton class="h-4 w-1/2 mt-1" />
          </div>
        </div>
      </div>

      <!-- ── Carousel ── -->
      <div v-else class="relative">
        <Swiper
          :modules="modules"
          :navigation="{ prevEl: '.deals-prev', nextEl: '.deals-next' }"
          :free-mode="{ enabled: true, sticky: false }"
          :slides-per-view="2.2"
          :space-between="12"
          :breakpoints="{
            480: { slidesPerView: 2.5, spaceBetween: 12 },
            640: { slidesPerView: 3.5, spaceBetween: 16 },
            768: { slidesPerView: 4.5, spaceBetween: 16 },
            1024: { slidesPerView: 5.5, spaceBetween: 20 },
            1280: { slidesPerView: 6.5, spaceBetween: 20 },
          }"
          class="!py-2"
        >
          <SwiperSlide
            v-for="(item, index) in dealProducts"
            :key="item.uuid"
            :itemprop="'itemListElement'"
          >
            <meta itemprop="position" :content="String(index + 1)" />
            <CardPerItems v-bind="item" />
          </SwiperSlide>
        </Swiper>
      </div>
    </div>
  </section>
</template>
