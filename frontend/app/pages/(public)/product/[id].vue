<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useWishlistStore } from "~/stores/wishlist";
import { useCheckoutStore } from "~/stores/checkout";
import { usePesanStore } from "~/stores/UsePesanStore";
import { useCompareStore } from "~/stores/compare";
import AddChartButton from "~/components/AddChartButton.vue";
import AddonPicker from "~/components/product/AddonPicker.vue";
import ProductRecommendation from "~/components/ProductRecommendation.vue";

const route = useRoute();
const router = useRouter();
const wishlist = useWishlistStore();
const checkout = useCheckoutStore();
const pesanStore = usePesanStore();
const compareStore = useCompareStore();
const uuid = route.params.id as string;

// ─── Parallel fetch ───────────────────────────────────────────────
const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(uuid);

const [{ data: apiResponse, pending, error }, { data: recResponse }] = await Promise.all([
  useFetch<any>("/api/peritems", {
    query: isUuid ? { uuid } : { slug: uuid },
    key: `p_${uuid.slice(0, 8)}`,
  }),
  useFetch<any>("/api/recommendations", {
    query: isUuid ? { uuid } : { slug: uuid },
    key: `r_${uuid.slice(0, 8)}`,
    lazy: true,
  }),
]);

// ─── Fetch Addons ────────────────────────────────────────────────
const addonUrl = computed(() => {
  const realUuid = apiResponse.value?.data?.uuid;
  return realUuid ? `/api/addons/bundle/${realUuid}` : '/api/addons/bundle/placeholder';
});

const { data: addonResponse } = await useFetch<any>(addonUrl, {
  query: { category_slug: computed(() => apiResponse.value?.data?.category) },
  key: computed(() => `addons_${apiResponse.value?.data?.uuid || uuid.slice(0, 8)}`),
  immediate: !!apiResponse.value?.data?.uuid,
  watch: [apiResponse],
});

// ─── 404 guard ───────────────────────────────────────────────────
if (!apiResponse.value?.data && !pending.value) {
  throw createError({
    statusCode: 404,
    statusMessage: "Produk tidak ditemukan",
    fatal: true,
  });
}

// ─── Mapping ─────────────────────────────────────────────────────
const product = computed(() => {
  const d = apiResponse.value?.data;
  if (!d) return null;
  return {
    id: d.uuid,
    slug: d.slug,
    brand: d.brand || "OFFICIAL",
    title: d.title,
    price: d.price,
    originalPrice: d.original_price || d.price,
    discountPercentage: d.discount_percentage || 0,
    sold: d.terjual || 0,
    stock: d.stok || 0,
    category: d.category || "cctv",
    subcategory: d.subcategory || "",
    type: d.type || "Kamera CCTV",
    images: d.images?.length ? d.images : ["/cctv.jpg"],
    description: d.description || "Belum ada deskripsi untuk produk ini.",
    specs: d.specs || {},
    weight: Number(d.weight ?? 0),
    stockUuid: d.stock_uuid || d.uuid,
  };
});

const recommendations = computed(() =>
  (recResponse.value?.data || []).filter((p: any) => p.uuid !== product.value?.id)
);

// ─── SEO ─────────────────────────────────────────────────────────
const siteUrl = useRuntimeConfig().public.siteUrl ?? "https://pasarcctv.com";
const siteName = "PasarCCTV Cimahi Bandung";

const seoTitle = computed(() => {
  if (!product.value) return siteName;
  const p = product.value;
  return `${p.brand} ${p.title} - Garansi Resmi | ${siteName}`;
});

const seoDescription = computed(() => {
  if (!product.value) return "";
  const p = product.value;
  const harga = formatPrice(p.price);
  return `Beli ${p.brand} ${p.title} harga ${harga}. Stok resmi ready di Bandung & Cimahi. Garansi resmi 1-2 tahun. Layanan teknisi profesional.`;
});

const canonicalUrl = computed(() => `${siteUrl}/product/${product.value?.slug || uuid}`);

useSeoMeta({
  title: seoTitle,
  description: seoDescription,
  robots: "index, follow",
  ogTitle: seoTitle,
  ogDescription: seoDescription,
  ogImage: () => product.value?.images[0] || "",
  ogUrl: canonicalUrl,
  ogSiteName: siteName,
  ogLocale: "id_ID",
});

// ─── Canonical URL Sync ──────────────────────────────────────────
watch(apiResponse, (newVal) => {
  if (import.meta.client && newVal?.data?.slug && newVal.data.slug !== route.params.id) {
    window.history.replaceState({}, "", `/product/${newVal.data.slug}`);
  }
}, { immediate: true });

// ─── Galeri & Thumbnail ──────────────────────────────────────────
const activeImageIndex = ref(0);
const activeImage = computed(() => {
  if (!product.value?.images?.length) return "/cctv.jpg";
  return product.value.images[activeImageIndex.value] || product.value.images[0];
});

const isZoomed = ref(false);
const zoomStyle = ref({ transformOrigin: "center center", transform: "scale(1)" });

const handleMouseMove = (e: MouseEvent) => {
  if (!isZoomed.value) return;
  const el = e.currentTarget as HTMLElement;
  const { left, top, width, height } = el.getBoundingClientRect();
  const x = Math.max(0, Math.min(100, ((e.clientX - left) / width) * 100));
  const y = Math.max(0, Math.min(100, ((e.clientY - top) / height) * 100));
  zoomStyle.value = {
    transformOrigin: `${x}% ${y}%`,
    transform: "scale(1.75)",
  };
};

const handleMouseEnter = () => (isZoomed.value = true);
const handleMouseLeave = () => {
  isZoomed.value = false;
  zoomStyle.value = { transformOrigin: "center center", transform: "scale(1)" };
};

// ─── Quantity & Addons ───────────────────────────────────────────
const quantity = ref(1);
const selectedAddons = ref<Record<string, { uuid: string; quantity: number; price: number; name: string; weight: number }>>({});

const unitPrice = computed(() => product.value?.price ?? 0);
const addonTotalPrice = computed(() => {
  return Object.values(selectedAddons.value).reduce((acc, curr) => acc + (curr.price * curr.quantity), 0);
});

const totalWeight = computed(() => {
  const baseWeight = (product.value?.weight ?? 0) * quantity.value;
  const addonWeight = Object.values(selectedAddons.value).reduce(
    (acc, curr) => acc + (curr.weight * curr.quantity),
    0
  );
  return baseWeight + addonWeight;
});

const totalPrice = computed(() => (unitPrice.value * quantity.value) + addonTotalPrice.value);

function formatPrice(value: number) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function formatWeight(value?: number) {
  if (!value || value <= 0) return "-";
  if (value >= 1000) {
    const kg = value / 1000;
    return `${kg % 1 === 0 ? kg.toFixed(0) : kg.toFixed(1)} kg`;
  }
  return `${value} gram`;
}

// ─── Cart & Direct Buy ───────────────────────────────────────────
const cartItem = computed(() => {
  if (!product.value) return null;
  const p = product.value;
  return {
    id: p.id,
    title: p.title,
    price: unitPrice.value,
    image: p.images[0],
    quantity: quantity.value,
    weight: totalWeight.value,
    options: {
      addons: Object.values(selectedAddons.value),
    },
    stock_uuid: p.stockUuid,
  };
});

function beliLangsung() {
  if (!product.value || product.value.stock === 0) return;
  const item = cartItem.value;
  if (!item) return;
  checkout.setCheckoutData([item], 0, "");
  router.push("/payment");
}

function openChat() {
  if (!product.value) return;
  const p = product.value;
  pesanStore.setPendingContext({
    uuid: p.id,
    title: p.title,
    url: canonicalUrl.value,
    image: p.images[0],
    price: unitPrice.value,
    brand: p.brand,
  });
  router.push("/contact");
}

// ─── Wishlist & Compare ──────────────────────────────────────────
const isWishlisted = computed(() =>
  product.value ? wishlist.isInWishlist(product.value.id) : false
);

function toggleWishlist() {
  if (!product.value) return;
  const p = product.value;
  wishlist.toggle({
    id: p.id,
    image: p.images[0],
    brand: p.brand,
    title: p.title,
    price: p.price,
    originalPrice: p.originalPrice,
    soldCount: p.sold,
    weight: p.weight,
  });
}

const isCompare = computed(() =>
  product.value ? compareStore.isInCompare(product.value.id) : false
);

function toggleCompare() {
  if (!product.value) return;
  const p = product.value;
  compareStore.toggle({
    id: p.id,
    image: p.images[0],
    brand: p.brand,
    title: p.title,
    price: p.price,
    type: p.type,
    originalPrice: p.originalPrice,
    soldCount: p.sold,
    specs: p.specs,
  });
}

const activeTab = ref<"deskripsi" | "spesifikasi" | "garansi">("spesifikasi");
</script>

<template>
  <main class="bg-[#F8F9FA] min-h-screen pb-24 lg:pb-16 font-['Plus_Jakarta_Sans',sans-serif] text-gray-900">
    <!-- Loading Screen -->
    <div v-if="pending" class="flex justify-center items-center h-[70vh]">
      <div class="flex flex-col items-center gap-3">
        <div class="w-10 h-10 border-3 border-gray-200 border-t-[#03AC0E] rounded-full animate-spin" />
        <p class="text-xs font-semibold text-gray-500">Memuat rincian produk...</p>
      </div>
    </div>

    <!-- Error Screen -->
    <div v-else-if="error || !product" class="max-w-[800px] mx-auto py-20 px-4 text-center">
      <div class="bg-white border border-gray-200 rounded-2xl p-10 shadow-xs">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h1 class="text-xl font-bold text-gray-900 mb-2">Produk Tidak Ditemukan</h1>
        <p class="text-xs sm:text-sm text-gray-500 mb-6">
          Kamera atau paket CCTV yang Anda cari mungkin sedang restock atau tautan telah diperbarui.
        </p>
        <NuxtLink
          to="/search"
          class="inline-flex items-center gap-2 bg-[#03AC0E] hover:bg-[#028b0b] text-white font-bold text-xs px-5 py-2.5 rounded-lg transition-colors"
        >
          <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
          Telusuri Katalog CCTV
        </NuxtLink>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 pt-4 sm:pt-6">
      <!-- Breadcrumb Bar Amazon/Tokopedia Style -->
      <nav aria-label="Breadcrumb" class="flex items-center gap-1.5 text-xs text-gray-500 mb-4 overflow-x-auto whitespace-nowrap pb-1">
        <NuxtLink to="/" class="hover:text-gray-900 transition-colors">Beranda</NuxtLink>
        <span class="text-gray-300">/</span>
        <NuxtLink :to="`/category/${product.category}`" class="hover:text-gray-900 capitalize transition-colors">
          {{ product.category.replace(/-/g, ' ') }}
        </NuxtLink>
        <template v-if="product.subcategory">
          <span class="text-gray-300">/</span>
          <NuxtLink :to="`/category/${product.subcategory}`" class="hover:text-gray-900 capitalize transition-colors">
            {{ product.subcategory.replace(/-/g, ' ') }}
          </NuxtLink>
        </template>
        <span class="text-gray-300">/</span>
        <span class="text-gray-900 font-semibold truncate max-w-[280px] sm:max-w-md">{{ product.title }}</span>
      </nav>

      <!-- 3-Column PDP Grid (Amazon Style: Gallery Left, Info Middle, BuyBox Right) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
        <!-- 1. LEFT: Product Gallery (Desktop: Thumbnails + Viewport) -->
        <div class="lg:col-span-5 bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 shadow-2xs sticky top-20">
          <div class="flex flex-col-reverse sm:flex-row gap-3">
            <!-- Vertical Thumbnails (Amazon standard) -->
            <div
              v-if="product.images.length > 1"
              class="flex sm:flex-col gap-2 overflow-x-auto sm:overflow-y-auto max-h-[460px] pb-1 sm:pb-0 shrink-0 select-none"
            >
              <button
                v-for="(img, idx) in product.images"
                :key="idx"
                type="button"
                :aria-label="`Pilih gambar ${idx + 1}`"
                class="w-14 h-14 rounded-lg border-2 p-1 bg-white flex items-center justify-center transition-all shrink-0 overflow-hidden"
                :class="activeImageIndex === idx ? 'border-[#03AC0E] ring-2 ring-[#03AC0E]/20' : 'border-gray-200 hover:border-gray-400'"
                @mouseenter="activeImageIndex = idx"
                @click="activeImageIndex = idx"
              >
                <img :src="img" :alt="`Thumbnail ${idx + 1}`" class="w-full h-full object-contain" />
              </button>
            </div>

            <!-- Main Viewport with Smooth Precision Zoom -->
            <div
              class="flex-1 aspect-square bg-[#FAFAFA] rounded-xl border border-gray-200 overflow-hidden relative cursor-crosshair group flex items-center justify-center"
              @mousemove="handleMouseMove"
              @mouseenter="handleMouseEnter"
              @mouseleave="handleMouseLeave"
            >
              <img
                :src="activeImage"
                :alt="product.title"
                class="w-full h-full object-contain p-4 transition-transform duration-150 ease-out pointer-events-none"
                :style="zoomStyle"
              />

              <!-- Discount / Status Badges -->
              <div class="absolute top-3 left-3 flex flex-col gap-1.5 pointer-events-none">
                <span
                  v-if="product.discountPercentage > 0"
                  class="bg-[#CC0C39] text-white text-[11px] font-bold px-2 py-0.5 rounded shadow-2xs font-mono"
                >
                  -{{ product.discountPercentage }}%
                </span>
                <span class="bg-gray-900 text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">
                  Original 100%
                </span>
              </div>

              <!-- Zoom prompt hint -->
              <span class="absolute bottom-3 right-3 bg-black/60 text-white text-[10px] font-semibold px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none flex items-center gap-1">
                <UIcon name="i-heroicons-magnifying-glass-plus" class="w-3.5 h-3.5" />
                Hover untuk perbesar
              </span>
            </div>
          </div>

          <!-- Trust Bar Under Gallery -->
          <div class="grid grid-cols-3 gap-2 mt-5 pt-4 border-t border-gray-100 text-center text-[11px] text-gray-600">
            <div class="p-2 rounded-lg bg-gray-50 border border-gray-100">
              <UIcon name="i-heroicons-shield-check" class="w-4 h-4 text-[#03AC0E] mx-auto mb-1" />
              <span class="font-bold block text-gray-900">Garansi 2 Thn</span>
              <span>Resmi Distributor</span>
            </div>
            <div class="p-2 rounded-lg bg-gray-50 border border-gray-100">
              <UIcon name="i-heroicons-wrench-screwdriver" class="w-4 h-4 text-blue-600 mx-auto mb-1" />
              <span class="font-bold block text-gray-900">Siap Pasang</span>
              <span>Teknisi Bandung</span>
            </div>
            <div class="p-2 rounded-lg bg-gray-50 border border-gray-100">
              <UIcon name="i-heroicons-truck" class="w-4 h-4 text-amber-600 mx-auto mb-1" />
              <span class="font-bold block text-gray-900">Packing Aman</span>
              <span>Bubble Wrap Tebal</span>
            </div>
          </div>
        </div>

        <!-- 2. MIDDLE: Core Product Specs, Price, & Bundling (Amazon/Tokopedia Center Layout) -->
        <div class="lg:col-span-4 space-y-6">
          <div class="bg-white border border-gray-200 rounded-2xl p-5 sm:p-6 shadow-2xs space-y-4">
            <!-- Brand, Type, & Badges with Interactive Navigation Links -->
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex flex-wrap items-center gap-2">
                <!-- Link Brand -->
                <NuxtLink
                  :to="`/brands/${encodeURIComponent(product.brand.toLowerCase())}`"
                  class="inline-flex items-center gap-1 bg-emerald-50 hover:bg-emerald-100 text-[#03AC0E] border border-emerald-200 text-xs font-bold px-2.5 py-1 rounded-md uppercase tracking-wider transition-colors group cursor-pointer"
                  :title="`Kunjungi Official Store ${product.brand}`"
                >
                  <UIcon name="i-heroicons-check-badge" class="w-4 h-4 text-[#03AC0E]" />
                  <span>{{ product.brand }} Official</span>
                  <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                </NuxtLink>

                <!-- Link Jenis / Type Produk -->
                <NuxtLink
                  :to="`/search?type=${encodeURIComponent(product.type)}`"
                  class="inline-flex items-center gap-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold px-2.5 py-1 rounded-md capitalize transition-colors"
                  :title="`Lihat semua kategori ${product.type}`"
                >
                  <UIcon name="i-heroicons-tag" class="w-3.5 h-3.5 text-gray-500" />
                  <span>{{ product.type }}</span>
                </NuxtLink>
              </div>

              <span class="text-xs text-gray-400 font-mono">SKU: {{ product.id.slice(0, 8) }}</span>
            </div>

            <!-- Title -->
            <h1 class="text-lg sm:text-xl font-extrabold text-gray-900 leading-snug">
              {{ product.title }}
            </h1>

            <!-- Rating & Sold Stats -->
            <div class="flex items-center gap-3 text-xs text-gray-500 pb-3 border-b border-gray-100">
              <div class="flex items-center gap-1 text-amber-500 font-bold">
                <UIcon name="i-heroicons-star-solid" class="w-4 h-4" />
                <span>4.9</span>
              </div>
              <span class="text-gray-300">•</span>
              <span>Terjual <strong class="text-gray-900">{{ product.sold }}</strong> unit</span>
              <span class="text-gray-300">•</span>
              <span class="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold">Stok Ready ({{ product.stock }})</span>
            </div>

            <!-- Price Structure (Amazon Style Price Box) -->
            <div class="p-3.5 bg-gray-50 rounded-xl border border-gray-150 space-y-1">
              <div v-if="product.discountPercentage > 0" class="flex items-center gap-2">
                <span class="text-xs text-gray-400 line-through font-mono">
                  {{ formatPrice(product.originalPrice) }}
                </span>
                <span class="text-xs font-bold text-[#CC0C39] bg-[#FFEAEA] px-2 py-0.5 rounded font-mono">
                  Hemat {{ product.discountPercentage }}%
                </span>
              </div>
              <div class="text-2xl sm:text-3xl font-black text-[#CC0C39] font-mono tracking-tight">
                {{ formatPrice(unitPrice) }}
              </div>
              <p class="text-[11px] text-gray-500 pt-1">
                Harga termasuk PPN. Belum termasuk ongkos pasang di luar paket bundling.
              </p>
            </div>

            <!-- Addon Picker / Bundling Services -->
            <div v-if="addonResponse?.data?.length" class="pt-2">
              <div class="flex items-center justify-between mb-3">
                <label class="text-xs font-bold text-gray-900 flex items-center gap-1.5">
                  <span class="w-1.5 h-4 bg-[#03AC0E] rounded-full" />
                  Paket Tambahan & Instalasi
                </label>
                <span class="text-[11px] text-gray-400 font-medium">Opsional</span>
              </div>
              <AddonPicker
                v-model="selectedAddons"
                :bundle="addonResponse.data"
                variant="chips"
              />
            </div>
          </div>

          <!-- Tab Nav (Spesifikasi, Deskripsi, Garansi) -->
          <div class="bg-white border border-gray-200 rounded-2xl shadow-2xs overflow-hidden">
            <div class="flex border-b border-gray-200 bg-gray-50/70 text-xs font-bold">
              <button
                type="button"
                class="flex-1 py-3 px-4 text-center transition-colors border-b-2"
                :class="activeTab === 'spesifikasi' ? 'border-[#03AC0E] text-[#03AC0E] bg-white' : 'border-transparent text-gray-600 hover:text-gray-900'"
                @click="activeTab = 'spesifikasi'"
              >
                Spesifikasi Teknis
              </button>
              <button
                type="button"
                class="flex-1 py-3 px-4 text-center transition-colors border-b-2"
                :class="activeTab === 'deskripsi' ? 'border-[#03AC0E] text-[#03AC0E] bg-white' : 'border-transparent text-gray-600 hover:text-gray-900'"
                @click="activeTab = 'deskripsi'"
              >
                Deskripsi
              </button>
              <button
                type="button"
                class="flex-1 py-3 px-4 text-center transition-colors border-b-2"
                :class="activeTab === 'garansi' ? 'border-[#03AC0E] text-[#03AC0E] bg-white' : 'border-transparent text-gray-600 hover:text-gray-900'"
                @click="activeTab = 'garansi'"
              >
                Garansi & Layanan
              </button>
            </div>

            <div class="p-5">
              <!-- Tab 1: Spesifikasi Teknis Table (Clean Tokopedia Zebra) -->
              <div v-if="activeTab === 'spesifikasi'" class="space-y-3">
                <table class="w-full text-xs border border-gray-150 rounded-lg overflow-hidden">
                  <tbody>
                    <tr class="border-b border-gray-150 bg-gray-50/70">
                      <th class="py-2.5 px-3.5 text-gray-500 font-medium w-1/3 text-left">Brand</th>
                      <td class="py-2.5 px-3.5 font-bold text-[#03AC0E] hover:underline text-left">
                        <NuxtLink :to="`/brands/${encodeURIComponent(product.brand.toLowerCase())}`">
                          {{ product.brand }}
                        </NuxtLink>
                      </td>
                    </tr>
                    <tr class="border-b border-gray-150 bg-white">
                      <th class="py-2.5 px-3.5 text-gray-500 font-medium text-left">Kategori</th>
                      <td class="py-2.5 px-3.5 font-bold text-[#03AC0E] hover:underline capitalize text-left">
                        <NuxtLink :to="`/category/${product.category}`">
                          {{ product.category.replace(/-/g, ' ') }}
                        </NuxtLink>
                      </td>
                    </tr>
                    <tr class="border-b border-gray-150 bg-gray-50/70">
                      <th class="py-2.5 px-3.5 text-gray-500 font-medium text-left">Tipe / Jenis</th>
                      <td class="py-2.5 px-3.5 font-bold text-[#03AC0E] hover:underline capitalize text-left">
                        <NuxtLink :to="`/search?type=${encodeURIComponent(product.type)}`">
                          {{ product.type }}
                        </NuxtLink>
                      </td>
                    </tr>
                    <tr class="border-b border-gray-150 bg-gray-50/70">
                      <th class="py-2.5 px-3.5 text-gray-500 font-medium text-left">Berat Pengiriman</th>
                      <td class="py-2.5 px-3.5 font-bold text-gray-900 text-left">{{ formatWeight(product.weight) }}</td>
                    </tr>
                    <tr
                      v-for="(val, key, i) in product.specs"
                      :key="key"
                      class="border-b border-gray-150 last:border-0"
                      :class="i % 2 === 0 ? 'bg-white' : 'bg-gray-50/70'"
                    >
                      <th class="py-2.5 px-3.5 text-gray-500 font-medium capitalize text-left">
                        {{ String(key).replace(/_/g, ' ') }}
                      </th>
                      <td class="py-2.5 px-3.5 font-bold text-gray-900 text-left">{{ val }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Tab 2: Deskripsi -->
              <div v-else-if="activeTab === 'deskripsi'" class="text-xs sm:text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                {{ product.description }}
              </div>

              <!-- Tab 3: Garansi -->
              <div v-else-if="activeTab === 'garansi'" class="space-y-3 text-xs text-gray-700">
                <div class="flex items-start gap-3 p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                  <UIcon name="i-heroicons-shield-check" class="w-5 h-5 text-[#03AC0E] shrink-0 mt-0.5" />
                  <div>
                    <h4 class="font-bold text-gray-900">Garansi Toko & Pabrikan</h4>
                    <p class="text-gray-600 mt-0.5">Penggantian unit baru bila cacat produksi dalam 7 hari pertama, dilanjutkan garansi service 12-24 bulan.</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 bg-blue-50 rounded-xl border border-blue-100">
                  <UIcon name="i-heroicons-map-pin" class="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                  <div>
                    <h4 class="font-bold text-gray-900">Jangkauan Teknisi Lokal</h4>
                    <p class="text-gray-600 mt-0.5">Melayani kunjungan survey, instalasi, dan maintenance untuk Kota Bandung, Cimahi, dan sekitarnya.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. RIGHT: Amazon Sticky Buy Box (Desktop Only) -->
        <div class="hidden lg:block lg:col-span-3 sticky top-20 space-y-4">
          <div class="bg-white border-2 border-gray-200 rounded-2xl p-5 shadow-xs space-y-4">
            <h3 class="text-sm font-bold text-gray-900 border-b border-gray-100 pb-2.5">
              Atur Pembelian
            </h3>

            <!-- Quantity Counter -->
            <div class="flex items-center justify-between gap-2">
              <span class="text-xs font-semibold text-gray-600">Jumlah</span>
              <div class="flex items-center border border-gray-300 rounded-lg overflow-hidden bg-gray-50">
                <button
                  type="button"
                  :disabled="quantity <= 1"
                  class="w-8 h-8 flex items-center justify-center font-bold text-gray-700 hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed"
                  @click="quantity > 1 && quantity--"
                >
                  −
                </button>
                <input
                  v-model.number="quantity"
                  type="number"
                  :min="1"
                  :max="product.stock"
                  class="w-10 text-center text-xs font-bold bg-white outline-none border-none py-1"
                />
                <button
                  type="button"
                  :disabled="quantity >= product.stock"
                  class="w-8 h-8 flex items-center justify-center font-bold text-gray-700 hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed"
                  @click="quantity < product.stock && quantity++"
                >
                  +
                </button>
              </div>
            </div>

            <!-- Subtotal Box -->
            <div class="pt-3 border-t border-gray-100 flex items-baseline justify-between">
              <span class="text-xs text-gray-500 font-medium">Total Harga</span>
              <span class="text-lg font-black text-gray-900 font-mono">
                {{ formatPrice(totalPrice) }}
              </span>
            </div>

            <!-- Action Buttons (Tokopedia Green #03AC0E + Tokopedia Secondary) -->
            <div class="space-y-2.5 pt-1">
              <!-- Tombol + Keranjang (Menggunakan Komponen Standar AddChartButton) -->
              <AddChartButton
                v-if="cartItem"
                :product="cartItem"
                class="w-full !bg-[#03AC0E] hover:!bg-[#028b0b] !text-white !border-[#03AC0E]"
                :disabled="product.stock === 0"
              />

              <!-- Tombol Beli Langsung (Outline Hijau Tebal Tokopedia) -->
              <button
                type="button"
                :disabled="product.stock === 0"
                class="w-full bg-white hover:bg-emerald-50 active:bg-emerald-100 border-2 border-[#03AC0E] text-[#03AC0E] font-extrabold py-2.5 px-4 rounded-xl text-xs sm:text-sm uppercase tracking-wider transition-all shadow-2xs disabled:border-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                @click="beliLangsung"
              >
                <UIcon name="i-heroicons-bolt" class="w-4 h-4 text-[#03AC0E]" />
                Beli Langsung
              </button>
            </div>

            <!-- Quick Features -->
            <div class="pt-3 border-t border-gray-100 flex justify-between text-xs font-bold text-gray-600">
              <button
                type="button"
                class="flex items-center gap-1 hover:text-[#03AC0E] transition-colors"
                @click="openChat"
              >
                <UIcon name="i-heroicons-chat-bubble-left-ellipsis" class="w-4 h-4" />
                Chat
              </button>
              <button
                type="button"
                class="flex items-center gap-1 transition-colors"
                :class="isWishlisted ? 'text-red-600' : 'hover:text-red-600'"
                @click="toggleWishlist"
              >
                <UIcon :name="isWishlisted ? 'i-heroicons-heart-solid' : 'i-heroicons-heart'" class="w-4 h-4" />
                Favorit
              </button>
              <button
                type="button"
                class="flex items-center gap-1 transition-colors"
                :class="isCompare ? 'text-[#03AC0E]' : 'hover:text-[#03AC0E]'"
                @click="toggleCompare"
              >
                <UIcon name="i-heroicons-arrows-right-left" class="w-4 h-4" />
                Bandingkan
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Rekomendasi Produk -->
      <section class="mt-12" aria-label="Rekomendasi Terkait">
        <ProductRecommendation :items="recommendations" />
      </section>
    </div>

    <!-- 4. MOBILE: Floating Bottom Action Bar (Tokopedia Style) -->
    <aside aria-label="Menu Pesan Cepat" class="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 p-3 px-4 shadow-lg flex items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <button
          type="button"
          aria-label="Konsultasi Produk"
          class="w-10 h-10 border border-gray-300 rounded-xl flex items-center justify-center text-gray-600 active:bg-gray-100"
          @click="openChat"
        >
          <UIcon name="i-heroicons-chat-bubble-left-ellipsis" class="w-5 h-5" />
        </button>
        <button
          type="button"
          aria-label="Simpan ke Favorit"
          class="w-10 h-10 border border-gray-300 rounded-xl flex items-center justify-center text-gray-600 active:bg-gray-100"
          :class="isWishlisted ? 'text-red-600 border-red-200 bg-red-50' : ''"
          @click="toggleWishlist"
        >
          <UIcon :name="isWishlisted ? 'i-heroicons-heart-solid' : 'i-heroicons-heart'" class="w-5 h-5" />
        </button>
      </div>

      <div class="flex-1 flex items-center gap-2 max-w-[280px]">
        <AddChartButton
          v-if="cartItem"
          :product="cartItem"
          class="flex-1 !bg-[#03AC0E] hover:!bg-[#028b0b] !text-white !border-[#03AC0E] !py-2"
          :disabled="product?.stock === 0"
        />
        <button
          type="button"
          :disabled="product?.stock === 0"
          class="flex-1 bg-white border-2 border-[#03AC0E] text-[#03AC0E] font-black py-2 px-2.5 rounded-xl text-xs uppercase tracking-wider active:bg-emerald-50 disabled:border-gray-200 disabled:text-gray-400"
          @click="beliLangsung"
        >
          Beli
        </button>
      </div>
    </aside>
  </main>
</template>

<style scoped>
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  appearance: textfield;
  -moz-appearance: textfield;
}
</style>