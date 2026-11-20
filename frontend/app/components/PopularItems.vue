<script setup lang="ts">
import { computed } from "vue";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Navigation, A11y, FreeMode } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/free-mode";
import CardPerItems from "./CardPerItems.vue";

const modules = [Navigation, A11y, FreeMode];

const { data, pending } = await useFetch("/api/getpopular", {
  query: { limit: 18 }, // Increase limit for more density
  server: true,
  lazy: true,
});

const popularProducts = computed(() => {
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

const hasProducts = computed(() => popularProducts.value.length > 0);
</script>

<template>
  <section
    v-if="pending || hasProducts"
    aria-labelledby="popular-heading"
    itemscope
    itemtype="https://schema.org/ItemList"
    class="w-full py-6 lg:py-10"
  >
    <meta itemprop="name" content="Produk Populer" />
    
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      <!-- ── Compact Header ── -->
      <header class="flex items-end justify-between mb-6 border-b border-gray-100 pb-4">
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-6 bg-[#03AC0E] rounded-full" aria-hidden="true" />
            <h2 id="popular-heading" class="text-lg lg:text-xl font-bold text-gray-900 tracking-tight">
              Produk Populer
            </h2>
          </div>
          <p class="text-xs text-gray-500 font-medium">
            Pilihan Terbaik Keamanan Pro
          </p>
        </div>

        <div class="flex items-center gap-3">
          <NuxtLink
            to="/category/popular"
            class="flex items-center gap-1 text-xs font-bold text-[#03AC0E] hover:text-[#028C0B] transition-colors"
          >
            Lihat Semua
            <UIcon name="i-heroicons-arrow-small-right" class="w-4 h-4" />
          </NuxtLink>

          <!-- Navigation Controls (Desktop) -->
          <div class="hidden sm:flex items-center gap-1.5">
            <button
              aria-label="Previous"
              class="pop-prev w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-500 hover:bg-[#03AC0E] hover:text-white hover:border-[#03AC0E] disabled:opacity-30 transition-all shadow-xs"
            >
              <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
            </button>
            <button
              aria-label="Next"
              class="pop-next w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-500 hover:bg-[#03AC0E] hover:text-white hover:border-[#03AC0E] disabled:opacity-30 transition-all shadow-xs"
            >
              <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <!-- ── Content ── -->
      <div v-if="pending" class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        <div v-for="i in 6" :key="i" class="bg-white rounded-xl border border-gray-50 overflow-hidden h-40">
          <USkeleton class="h-40 w-full rounded-none" />
          <div class="p-3 space-y-2">
            <USkeleton class="h-2 w-1/3" />
            <USkeleton class="h-3 w-full" />
            <USkeleton class="h-4 w-1/2" />
          </div>
        </div>
      </div>

      <div v-else class="relative">
        <Swiper
          :modules="modules"
          :navigation="{ prevEl: '.pop-prev', nextEl: '.pop-next' }"
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
          <SwiperSlide v-for="item in popularProducts" :key="item.uuid">
            <CardPerItems v-bind="item" />
          </SwiperSlide>
        </Swiper>
      </div>
    </div>
  </section>
</template>

<style scoped>
.pop-swiper-wrap :deep(.swiper) {
  overflow: visible !important;
}
:deep(.swiper-slide) {
  height: auto !important;
  display: flex !important;
}
:deep(.swiper-slide > *) {
  width: 100% !important;
  height: 100% !important;
}
</style>
