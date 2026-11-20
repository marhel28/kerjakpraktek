<script setup lang="ts">
import { computed } from "vue";
import { useCompareStore } from "~/stores/compare";
import { useCartStore } from "~/stores/cart";

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
  rating?: number;
  warranty?: string;
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
const cartStore = useCartStore();
const toast = useToast();

const isCompare = computed(() => compareStore.isInCompare(props.uuid));

// ponytail: product API has no rating/warranty fields yet; never synthesize trust claims.
const warrantyLabel = computed(() => typeof props.warranty === "string" ? props.warranty.trim() : "");
const ratingLabel = computed(() => typeof props.rating === "number" &&
  Number.isFinite(props.rating) && props.rating >= 1 && props.rating <= 5
  ? props.rating.toFixed(1) : "");

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

const handleQuickAdd = () => {
  cartStore.add({
    id: props.uuid,
    title: props.title,
    price: props.price,
    original_price: props.original_price,
    discount_percentage: props.discount_percentage,
    image: props.image,
    brand: props.brand,
    category: props.category,
    specs: props.specs,
    weight: 1,
    quantity: 1,
  });
  toast.add({
    title: "Berhasil Ditambahkan!",
    description: `${props.title} masuk ke keranjang.`,
    icon: "i-heroicons-check-circle",
    color: "green",
  });
};

const priceFormatter = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  minimumFractionDigits: 0,
});
const formatPrice = (value: number) => priceFormatter.format(value);
const productUrl = computed(() => `/product/${props.slug || props.uuid}`);
const soldLabel = computed(() => {
  if (!Number.isFinite(props.terjual) || props.terjual <= 0) return "";
  return props.terjual >= 1000
    ? `${(props.terjual / 1000).toFixed(1)}rb`
    : String(props.terjual);
});
const imageAlt = computed(() => `${props.brand} ${props.title}`);

// Smart Hardware Image Resolver untuk menampilkan foto produk CCTV yang sesuai spesifikasi
const resolvedImage = computed(() => {
  const t = (props.title || "").toLowerCase();
  const c = (props.category || "").toLowerCase();
  const sc = (props.subcategory || "").toLowerCase();
  const tp = (props.type || "").toLowerCase();

  if (c.includes("paket") || t.includes("paket") || tp.includes("paket")) {
    return "/images/showcase/bundle.jpg";
  }
  if (c.includes("storage") || t.includes("hdd") || t.includes("harddisk") || t.includes("seagate") || t.includes("purple")) {
    return "/images/showcase/harddrive.jpg";
  }
  if (c.includes("dvr") || t.includes("dvr") || t.includes("nvr") || t.includes("channel")) {
    return "/images/showcase/dvr.jpg";
  }
  if (t.includes("colorvu") || t.includes("starlight") || t.includes("full color") || t.includes("audio mic")) {
    return "/images/showcase/colorvu.jpg";
  }
  if (sc.includes("ptz") || sc.includes("wireless") || t.includes("ptz") || t.includes("wireless") || t.includes("wifi")) {
    return "/images/showcase/ptz.jpg";
  }
  if (sc.includes("outdoor") || t.includes("outdoor") || t.includes("bullet") || t.includes("poe")) {
    return "/images/showcase/bullet.jpg";
  }
  if (sc.includes("indoor") || t.includes("indoor") || t.includes("dome")) {
    return "/images/showcase/dome.jpg";
  }

  return props.image || "/images/showcase/dome.jpg";
});

// Technical specs pills (Amazon Hardware Details)
const keySpecs = computed(() => {
  const list: string[] = [];
  if (props.specs && typeof props.specs === 'object') {
    if (props.specs.resolution) list.push(String(props.specs.resolution));
    if (props.specs.poe === "yes") list.push("PoE");
    if (props.specs.audio) list.push("Audio Mic");
    if (props.specs.starlight) list.push("Starlight");
    if (props.specs.night_vision) list.push("ColorVu");
    if (props.specs.dvr) list.push(String(props.specs.dvr));
    if (props.specs.hdd) list.push(String(props.specs.hdd));
  }
  return list.slice(0, 2);
});
</script>

<template>
  <article
    itemscope
    itemtype="https://schema.org/Product"
    class="product-card group relative flex flex-col h-full min-w-0 select-none bg-transparent border-0 shadow-none"
  >
    <!-- Media Container (Thumbnail) -->
    <div class="relative aspect-[4/5] w-full rounded-lg bg-[#f7f8f8] overflow-hidden">
      <NuxtLink
        :to="productUrl"
        :title="`${brand} ${title}`"
        class="block w-full h-full focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-green-700"
      >
        <NuxtImg
          :src="resolvedImage"
          :alt="imageAlt"
          itemprop="image"
          width="400"
          height="400"
          format="webp"
          quality="80"
          loading="lazy"
          sizes="xs:50vw sm:50vw md:33vw lg:25vw xl:25vw"
          class="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-300"
        />
      </NuxtLink>

      <!-- Wishlist & Compare in Top-Right -->
      <div class="absolute top-2.5 right-2.5 flex flex-col gap-1.5 z-10">
        <AddButtonWishlist data-action="wishlist" :product="{ id: uuid, image, title, price, brand }" />
        <button
          type="button"
          data-action="compare"
          :aria-label="isCompare ? 'Hapus dari perbandingan' : 'Bandingkan produk'"
          :aria-pressed="isCompare"
          :disabled="compareStore.isFull && !isCompare"
          class="w-8 h-8 rounded-full bg-white/90 backdrop-blur-md shadow-xs flex items-center justify-center text-gray-600 hover:text-[#03AC0E] hover:bg-white active:scale-95 transition-all disabled:cursor-not-allowed disabled:opacity-50"
          :class="{ 'bg-green-50 text-[#03AC0E] ring-1 ring-[#03AC0E]': isCompare }"
          @click="toggleCompare"
        >
          <UIcon name="i-heroicons-arrows-right-left" class="w-4 h-4 shrink-0" aria-hidden="true" />
        </button>
      </div>

      <!-- Quick Add Button (+) Tokopedia Green Style in Bottom-Right -->
      <button
        type="button"
        aria-label="Tambah ke keranjang"
        class="absolute bottom-2.5 right-2.5 w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-[#03AC0E] hover:bg-[#028C0B] active:scale-95 text-white shadow-xs flex items-center justify-center transition-all z-10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#03AC0E]"
        @click.stop="handleQuickAdd"
      >
        <UIcon name="i-heroicons-plus" class="w-4 h-4 sm:w-5 sm:h-5 stroke-[2.5]" aria-hidden="true" />
      </button>
    </div>

    <!-- Details Body -->
    <div class="flex flex-1 flex-col pt-3">
      <!-- Tag Promo / Deal (di bawah gambar) -->
      <div v-if="discount_percentage > 0 && original_price > price" class="flex items-center gap-1.5 mb-1">
        <span class="inline-flex items-center justify-center bg-[#FFF0F2] text-[#D62828] border border-[#FCD5D8] text-[10px] sm:text-[11px] font-bold px-1.5 py-0.5 rounded leading-none">
          {{ discount_percentage }}%
        </span>
        <span class="text-[#D62828] text-[11px] font-semibold leading-none">
          Hemat
        </span>
      </div>

      <!-- Price Lockup Amazon Ergo + Tokopedia Boldness -->
      <div class="flex items-baseline gap-1.5 flex-wrap" itemprop="offers" itemscope itemtype="https://schema.org/Offer">
        <meta itemprop="priceCurrency" content="IDR" />
        <meta itemprop="price" :content="String(price)" />
        <p data-test="price-main" class="flex items-baseline text-gray-900 tracking-tight">
          <span class="text-xs font-semibold mr-0.5 text-gray-800">Rp</span>
          <span class="text-base sm:text-lg font-bold text-gray-900">{{ new Intl.NumberFormat("id-ID").format(price) }}</span>
        </p>
        <span v-if="original_price > price" class="text-[11px] text-gray-400 line-through truncate">
          {{ formatPrice(original_price) }}
        </span>
      </div>

      <!-- Judul Produk -->
      <NuxtLink
        :to="productUrl"
        :title="`${brand} ${title}`"
        class="focus-visible:outline-2 focus-visible:outline-[#03AC0E] mt-1 hover:text-[#03AC0E] transition-colors"
      >
        <h3 itemprop="name" class="text-xs sm:text-sm font-normal text-gray-800 line-clamp-2 leading-snug group-hover:text-[#03AC0E] hover:text-[#03AC0E] transition-colors">
          {{ title }}
        </h3>
      </NuxtLink>

      <!-- Key Technical Specs (Amazon Spec Tag) -->
      <div v-if="keySpecs.length > 0" class="flex flex-wrap gap-1 mt-1">
        <span
          v-for="spec in keySpecs"
          :key="spec"
          class="text-[10px] font-semibold bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded leading-none"
        >
          {{ spec }}
        </span>
      </div>

      <!-- Trust Badges (Warranty) -->
      <div data-test="trust-badges" v-if="warrantyLabel" class="flex items-center gap-1 text-[11px] text-[#03AC0E] font-medium mt-1">
        <UIcon name="i-heroicons-shield-check" class="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
        <span class="truncate">{{ warrantyLabel }}</span>
      </div>

      <!-- Social Proof / Terjual / Rating -->
      <div class="flex items-center gap-1.5 text-[11px] text-gray-500 mt-1.5">
        <span v-if="ratingLabel" :aria-label="`Rating ${ratingLabel} dari 5`" class="inline-flex items-center gap-0.5 font-medium text-gray-700">
          <UIcon name="i-heroicons-star-solid" class="h-3.5 w-3.5 text-[#FFB703]" aria-hidden="true" />
          {{ ratingLabel }}
        </span>
        <span v-if="ratingLabel && soldLabel" aria-hidden="true" class="text-gray-300">·</span>
        <span v-if="soldLabel" class="text-gray-500">Terjual {{ soldLabel }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  .product-card { transition: none; }
}
</style>
