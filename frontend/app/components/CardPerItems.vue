<script setup lang="ts">
import { computed } from "vue";
import { useCompareStore } from "~/stores/compare";

interface Props {
  uuid: string;
  slug?: string;
  title: string;
  image: string;
  price: number;
  original_price?: number;
  discount_percentage?: number;
  category?: string;
  subcategory?: string;
  brand?: string;
  type?: string;
  specs?: Record<string, any>;
  terjual?: number;
}

const props = withDefaults(defineProps<Props>(), {
  original_price: 0,
  discount_percentage: 0,
  terjual: 0,
  brand: "NO BRAND",
  type: "",
  category: "all",
  subcategory: "",
  specs: () => ({}),
});

const compareStore = useCompareStore();
const isCompare = computed(() => compareStore.isInCompare(props.uuid));

const shortSpecs = computed(() => {
  if (!props.specs || Object.keys(props.specs).length === 0) return [];
  return Object.entries(props.specs).slice(0, 2);
});

const toggleCompare = () => {
  compareStore.toggle({
    id: props.uuid,
    image: props.image,
    brand: props.brand,
    title: props.title,
    price: props.price,
    type: props.type,
    originalPrice: props.original_price,
    soldCount: props.terjual,
    specs: props.specs,
  });
};

const priceFormatter = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  minimumFractionDigits: 0,
});
const formatPrice = (value: number) =>
  value ? priceFormatter.format(value).replace("Rp", "Rp ") : "Rp 0";

const productUrl = computed(() => `/product/${props.slug || props.uuid}`);

const soldLabel = computed(() => {
  if (!props.terjual || props.terjual <= 0) return "";
  return props.terjual >= 1000
    ? `${(props.terjual / 1000).toFixed(1)}rb`
    : String(props.terjual);
});

const imageAlt = computed(
  () =>
    `${props.brand} ${props.title}${
      props.category !== "all" ? ` - ${props.category.replace(/-/g, " ")}` : ""
    }`
);
</script>

<template>
  <article
    itemscope
    itemtype="https://schema.org/Product"
    class="group relative flex flex-col h-full"
  >
    <NuxtLink
      :to="productUrl"
      :title="`${brand} ${title}`"
      class="flex flex-col h-full bg-white transition-all duration-200 rounded-xl sm:rounded-2xl border border-gray-100 hover:border-green-500/30 hover:shadow-[0_8px_24px_-8px_rgba(22,163,74,0.10)] hover:-translate-y-1 overflow-hidden"
    >
      <!-- ── Gambar ─────────────────────────────────────────────── -->
      <div
        class="relative aspect-square w-full overflow-hidden bg-gradient-to-b from-gray-50 to-[#f9fafb] min-h-[150px] sm:min-h-[200px]"
      >
        <!-- Badge diskon -->
        <div
          v-if="discount_percentage > 0"
          class="absolute top-2 left-2 sm:top-3 sm:left-3 z-20"
        >
          <span
            class="bg-gradient-to-r from-red-500 to-rose-600 text-white text-[9px] sm:text-[10px] font-black px-1.5 sm:px-2.5 py-0.5 sm:py-1 rounded-md sm:rounded-lg shadow-sm shadow-red-500/30 flex items-center gap-0.5 sm:gap-1"
            :aria-label="`Diskon ${discount_percentage} persen`"
          >
            <UIcon
              name="i-heroicons-arrow-trending-down"
              class="w-2.5 h-2.5 sm:w-3 sm:h-3"
              aria-hidden="true"
            />
            {{ discount_percentage }}%
          </span>
        </div>

        <!-- Action buttons — hanya tampil di sm ke atas (hover tidak ada di mobile) -->
        <div
          class="hidden sm:flex absolute top-3 right-3 z-20 flex-col gap-2 transform translate-x-12 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 transition-all duration-300 ease-out"
          @click.prevent.stop
        >
          <AddButtonWishlist :product="{ id: uuid, image, title, price, brand }" />
          <UButton
            color="white"
            variant="solid"
            icon="i-heroicons-arrows-right-left"
            :aria-label="isCompare ? 'Hapus dari perbandingan' : 'Bandingkan produk'"
            :aria-pressed="isCompare"
            class="rounded-full shadow-md bg-white/90 backdrop-blur-md transition-colors hover:bg-green-50"
            :class="isCompare ? 'text-green-600 ring-2 ring-green-500' : 'text-gray-500'"
            :disabled="compareStore.isFull && !isCompare"
            @click.prevent.stop="toggleCompare"
          />
        </div>

        <NuxtImg
          :src="image"
          :alt="imageAlt"
          :title="imageAlt"
          itemprop="image"
          width="400"
          height="400"
          format="webp"
          quality="80"
          loading="lazy"
          sizes="xs:50vw sm:50vw md:33vw lg:25vw xl:25vw"
          class="h-full w-full object-contain p-3 sm:p-6 transition-transform duration-300 ease-out group-hover:scale-105"
        />

        <div
          class="absolute inset-0 bg-black/0 group-hover:bg-black/[0.03] transition-colors duration-300"
          aria-hidden="true"
        />
      </div>

      <!-- ── Konten ─────────────────────────────────────────────── -->
      <div class="flex flex-1 flex-col p-2.5 sm:p-4 pt-2 sm:pt-3">
        <!-- Brand + kategori -->
        <div class="mb-2 flex items-center gap-2 overflow-hidden min-h-[22px] sm:min-h-[24px] min-w-0">
          <span
            itemprop="brand"
            class="shrink-0 text-[9px] sm:text-[10px] font-black uppercase tracking-wider text-green-700 bg-green-50 px-1.5 sm:px-2 py-0.5 rounded-md border border-green-200/60"
          >
            {{ brand }}
          </span>
          <span
            v-if="subcategory || category"
            class="hidden sm:block text-[9px] font-bold text-gray-400 uppercase tracking-widest truncate flex-1 border-l border-gray-100 pl-2 min-w-0"
          >
            {{ (subcategory || category).replace(/-/g, " ") }}
          </span>
        </div>

        <h3
          itemprop="name"
          class="text-[12px] sm:text-[13px] font-bold text-gray-800 line-clamp-2 leading-snug min-h-[32px] sm:min-h-[40px] group-hover:text-[#03AC0E] transition-colors"
        >
          {{ title }}
        </h3>

        <!-- Specs singkat — disembunyikan di mobile agar tidak terlalu padat -->
        <div class="hidden sm:block mt-2.5 space-y-1.5 flex-1 min-h-[48px]">
          <div v-if="type" class="flex items-center gap-1.5 text-gray-400">
            <UIcon
              name="i-heroicons-tag"
              class="w-3 h-3 flex-shrink-0"
              aria-hidden="true"
            />
            <p class="text-[10px] truncate font-semibold uppercase tracking-tight">
              {{ type }}
            </p>
          </div>

          <div
            v-for="[key, value] in shortSpecs"
            :key="key"
            class="flex items-center gap-1.5 text-gray-500"
            itemprop="additionalProperty"
            itemscope
            itemtype="https://schema.org/PropertyValue"
          >
            <div class="w-1 h-1 rounded-full bg-gray-300" aria-hidden="true" />
            <p class="text-[10px] truncate leading-none">
              <span itemprop="name" class="font-bold text-gray-600 capitalize">
                {{ key.replace(/_/g, " ") }}:
              </span>
              <span itemprop="value" class="capitalize"> {{ value }}</span>
            </p>
          </div>
        </div>

        <!-- Harga -->
        <div
          class="mt-2 sm:mt-4 flex flex-col justify-end"
          itemprop="offers"
          itemscope
          itemtype="https://schema.org/Offer"
        >
          <meta itemprop="priceCurrency" content="IDR" />
          <meta itemprop="price" :content="String(price)" />
          <link itemprop="availability" href="https://schema.org/InStock" />

          <!-- Harga coret -->
          <div class="h-[13px] sm:h-[14px] mb-0.5 flex items-center">
            <span
              v-if="original_price && original_price > price"
              class="text-[10px] sm:text-[11px] font-medium text-gray-400 line-through decoration-gray-300"
            >
              {{ formatPrice(original_price) }}
            </span>
          </div>

          <!-- Harga final -->
          <p
            itemprop="price"
            class="text-[14px] sm:text-[17px] font-black tracking-tight"
            :class="discount_percentage > 0 ? 'text-red-600' : 'text-gray-900'"
          >
            {{ formatPrice(price) }}
          </p>
        </div>

        <!-- Terjual — tanpa bintang -->
        <div v-if="soldLabel" class="mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-gray-100">
          <span class="text-[10px] font-bold text-gray-400">
            Terjual {{ soldLabel }}
          </span>
        </div>
      </div>
    </NuxtLink>
  </article>
</template>

<style scoped>
* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
