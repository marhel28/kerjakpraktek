<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useWishlistStore } from "~/stores/wishlist";
import { useCheckoutStore } from "~/stores/checkout";
import { usePesanStore } from "~/stores/usePesanStore";
import AddChartButton from "~/components/AddChartButton.vue";
import ProductRecommendation from "~/components/ProductRecommendation.vue";

const route = useRoute();
const router = useRouter();
const wishlist = useWishlistStore();
const checkout = useCheckoutStore();
const pesanStore = usePesanStore(); // ✅ import store pesan
const uuid = route.params.id as string;

// ─── Parallel fetch ───────────────────────────────────────────────
const [{ data: apiResponse, pending, error }, { data: recResponse }] = await Promise.all([
  useFetch("/api/peritems", {
    query: { uuid },
    key: `product:${uuid}`,
    getCachedData: (key, nuxtApp) =>
      nuxtApp.payload.data[key] ?? nuxtApp.static.data[key],
  }),
  useFetch("/api/recommendations", {
    query: { uuid },
    key: `rec:${uuid}`,
    lazy: true,
  }),
]);

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
    brand: d.brand || "NO BRAND",
    title: d.title,
    price: d.price,
    originalPrice: d.original_price || d.price,
    discountPercentage: d.discount_percentage || 0,
    sold: d.terjual || 0,
    stock: d.stok || 0,
    category: d.category || "uncategorized",
    subcategory: d.subcategory || "",
    type: d.type || "General",
    images: d.images?.length ? d.images : ["/images/no-image.webp"],
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
const siteUrl = useRuntimeConfig().public.siteUrl ?? "https://yourdomain.com";
const siteName = "Toko CCTV";

const seoTitle = computed(() => {
  if (!product.value) return siteName;
  const p = product.value;
  return `${p.brand} ${p.title} - ${p.category.replace(/-/g, " ")} | ${siteName}`;
});

const seoDescription = computed(() => {
  if (!product.value) return "";
  const p = product.value;
  const harga = formatPrice(p.price);
  const desc = `Beli ${p.brand} ${p.title} harga ${harga}. ${p.description
    .slice(0, 100)
    .replace(/\n/g, " ")}... Stok tersedia, pengiriman cepat.`;
  return desc.slice(0, 160);
});

const canonicalUrl = computed(() => `${siteUrl}/product/${product.value?.slug || uuid}`);

useSeoMeta({
  title: seoTitle,
  description: seoDescription,
  robots: "index, follow",
  ogType: "product",
  ogTitle: seoTitle,
  ogDescription: seoDescription,
  ogImage: () => product.value?.images[0] || "",
  ogImageWidth: "800",
  ogImageHeight: "800",
  ogImageAlt: () => `Foto ${product.value?.title || ""}`,
  ogUrl: canonicalUrl,
  ogSiteName: siteName,
  ogLocale: "id_ID",
  twitterCard: "summary_large_image",
  twitterTitle: seoTitle,
  twitterDescription: seoDescription,
  twitterImage: () => product.value?.images[0] || "",
  twitterImageAlt: () => `Foto ${product.value?.title || ""}`,
  ogPriceAmount: () => String(product.value?.price || ""),
  ogPriceCurrency: "IDR",
});

useHead({
  link: [
    { rel: "canonical", href: canonicalUrl },
    {
      rel: "preload",
      as: "image",
      href: () => product.value?.images[0] || "",
      fetchpriority: "high",
    },
  ],
});

const jsonLd = computed(() => {
  if (!product.value) return null;
  const p = product.value;
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: `${p.brand} ${p.title}`,
    description: p.description.slice(0, 500),
    image: p.images,
    sku: p.id,
    mpn: p.id,
    brand: { "@type": "Brand", name: p.brand },
    category: p.category.replace(/-/g, " "),
    offers: {
      "@type": "Offer",
      url: canonicalUrl.value,
      priceCurrency: "IDR",
      price: p.price,
      priceValidUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split("T")[0],
      availability:
        p.stock > 0 ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
      seller: { "@type": "Organization", name: siteName },
      ...(p.discountPercentage > 0 && {
        priceSpecification: {
          "@type": "UnitPriceSpecification",
          price: p.originalPrice,
          priceCurrency: "IDR",
        },
      }),
    },
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: "5",
      reviewCount: String(Math.max(p.sold, 1)),
      bestRating: "5",
      worstRating: "1",
    },
    additionalProperty: Object.entries(p.specs).map(([name, value]) => ({
      "@type": "PropertyValue",
      name: name.replace(/_/g, " "),
      value,
    })),
  };
});

useHead({
  script: computed(() =>
    jsonLd.value
      ? [
          {
            type: "application/ld+json",
            innerHTML: JSON.stringify(jsonLd.value),
            key: `jsonld-product-${uuid}`,
          },
        ]
      : []
  ),
});

const breadcrumbLd = computed(() => {
  if (!product.value) return null;
  const p = product.value;
  const items: any[] = [
    { "@type": "ListItem", position: 1, name: "Beranda", item: siteUrl },
    {
      "@type": "ListItem",
      position: 2,
      name: p.category.replace(/-/g, " "),
      item: `${siteUrl}/category/${p.category}`,
    },
  ];
  if (p.subcategory) {
    items.push({
      "@type": "ListItem",
      position: 3,
      name: p.subcategory.replace(/-/g, " "),
      item: `${siteUrl}/category/${p.subcategory}`,
    });
  }
  items.push({
    "@type": "ListItem",
    position: items.length + 1,
    name: `${p.brand} ${p.title}`,
    item: canonicalUrl.value,
  });
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items,
  };
});

useHead({
  script: computed(() =>
    breadcrumbLd.value
      ? [
          {
            type: "application/ld+json",
            innerHTML: JSON.stringify(breadcrumbLd.value),
            key: `jsonld-breadcrumb-${uuid}`,
          },
        ]
      : []
  ),
});

// ─── Gambar & Zoom ───────────────────────────────────────────────
const activeImage = ref("");
watch(
  product,
  (p) => {
    if (p?.images[0]) activeImage.value = p.images[0];
  },
  { immediate: true }
);

const isZoomed = ref(false);
const zoomStyle = ref({ transformOrigin: "center center", transform: "scale(1)" });

const handleMouseMove = (e: MouseEvent) => {
  if (!isZoomed.value) return;
  const el = e.currentTarget as HTMLElement;
  const { left, top, width, height } = el.getBoundingClientRect();
  zoomStyle.value = {
    transformOrigin: `${((e.clientX - left) / width) * 100}% ${
      ((e.clientY - top) / height) * 100
    }%`,
    transform: "scale(2.5)",
  };
};
const handleMouseEnter = () => (isZoomed.value = true);
const handleMouseLeave = () => {
  isZoomed.value = false;
  zoomStyle.value = { transformOrigin: "center center", transform: "scale(1)" };
};

// ─── Harga & Varian ──────────────────────────────────────────────
const quantity = ref(1);
const selectedHdd = ref({ label: "Tanpa HDD", price: 0 });
const isPaket = computed(() => product.value?.category === "paket-cctv");
const unitPrice = computed(
  () => (product.value?.price ?? 0) + (isPaket.value ? selectedHdd.value.price : 0)
);
const totalPrice = computed(() => unitPrice.value * quantity.value);

function formatPrice(value: number) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  })
    .format(value || 0)
    .replace("Rp", "Rp ");
}

const hddOptions = [
  { label: "Tanpa HDD", price: 0 },
  { label: "HDD 1TB (Surveillance)", price: 550000 },
  { label: "HDD 2TB (Surveillance)", price: 950000 },
];

// ─── Wishlist ────────────────────────────────────────────────────
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

function formatWeight(value?: number) {
  if (!value || value <= 0) return "-";
  if (value >= 1000) {
    const kg = value / 1000;
    return `${kg % 1 === 0 ? kg.toFixed(0) : kg.toFixed(1)} kg`;
  }
  return `${value} g`;
}

// ─── Share ───────────────────────────────────────────────────────
async function handleShare() {
  const p = product.value;
  if (!p) return;
  const shareData = {
    title: `${p.brand} ${p.title}`,
    text: `Cek produk ini: ${p.brand} ${p.title} - ${formatPrice(p.price)}`,
    url: canonicalUrl.value,
  };
  if (navigator.share) await navigator.share(shareData);
  else {
    await navigator.clipboard.writeText(canonicalUrl.value);
    alert("Link disalin ke clipboard!");
  }
}

// ─── Cart ────────────────────────────────────────────────────────
const cartItem = computed(() => {
  if (!product.value) return null;
  const p = product.value;
  return {
    id: p.id,
    title: p.title,
    price: unitPrice.value,
    image: p.images[0],
    quantity: quantity.value,
    weight: p.weight,
    options: { hdd: isPaket.value ? selectedHdd.value.label : null },
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

// ─── ✅ Chat — the real implementation ───────────────────────────
/**
 * Klik "Chat" di halaman produk:
 *  1. Simpan konteks produk ke pesanStore.pendingContext
 *  2. Navigate ke home
 *  3. FloatingChat (di layout) mendeteksi perubahan pendingContext
 *     → auto-open dengan banner produk
 *
 * Kenapa navigate ke home?
 *  FloatingChat ada di layouts/default.vue (bukan di halaman ini).
 *  Saat masih di /product/[uuid], component sudah ada tapi
 *  dengan navigate ke home kita memastikan user fokus ke chat
 *  dan tidak ada scroll conflic dengan halaman produk.
 */
function openChat() {
  if (!product.value) return;
  const p = product.value;

  // 1. Set konteks produk ke store — persist lintas navigasi
  pesanStore.setPendingContext({
    uuid: p.id,
    title: p.title,
    url: canonicalUrl.value,
    image: p.images[0],
    price: unitPrice.value, // pakai unitPrice (sudah include HDD jika paket)
    brand: p.brand,
  });

  // 2. Navigasi ke home — FloatingChat di layout akan auto-open via watch
  router.push("/");
}
</script>

<template>
  <main class="bg-gray-50 min-h-screen pb-10 font-jakarta overflow-x-hidden">
    <!-- Loading -->
    <div v-if="pending" class="flex justify-center items-center h-[60vh]">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500" />
    </div>

    <!-- Error / not found -->
    <div
      v-else-if="error || !product"
      class="flex flex-col justify-center items-center h-[60vh] text-center"
    >
      <UIcon name="i-heroicons-archive-box-x-mark" class="w-20 h-20 text-gray-300 mb-4" />
      <h1 class="text-2xl font-bold text-gray-800">Produk Tidak Ditemukan</h1>
      <p class="text-gray-500 mt-2">Mungkin URL salah atau produk sudah dihapus.</p>
      <NuxtLink
        to="/"
        class="mt-6 px-6 py-2.5 bg-black text-white font-bold rounded-xl hover:bg-gray-800 transition-colors"
      >
        Kembali ke Beranda
      </NuxtLink>
    </div>

    <div v-else class="max-w-[1200px] mx-auto px-4 pt-6">
      <!-- ── Breadcrumb ────────────────────────────────────────── -->
      <nav
        aria-label="Breadcrumb"
        class="flex flex-wrap items-center gap-2 text-[13px] text-gray-500 mb-6"
      >
        <ol
          class="flex flex-wrap items-center gap-2 list-none p-0 m-0"
          itemscope
          itemtype="https://schema.org/BreadcrumbList"
        >
          <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <NuxtLink
              to="/"
              itemprop="item"
              class="hover:text-green-600 font-semibold transition-colors"
            >
              <span itemprop="name">Beranda</span>
            </NuxtLink>
            <meta itemprop="position" content="1" />
          </li>
          <li aria-hidden="true">
            <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5" />
          </li>
          <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <NuxtLink
              :to="`/category/${product.category}`"
              itemprop="item"
              class="hover:text-green-600 font-semibold transition-colors capitalize"
            >
              <span itemprop="name">{{ product.category.replace(/-/g, " ") }}</span>
            </NuxtLink>
            <meta itemprop="position" content="2" />
          </li>
          <template v-if="product.subcategory">
            <li aria-hidden="true">
              <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5" />
            </li>
            <li
              itemprop="itemListElement"
              itemscope
              itemtype="https://schema.org/ListItem"
            >
              <NuxtLink
                :to="`/category/${product.subcategory}`"
                itemprop="item"
                class="hover:text-green-600 font-semibold transition-colors capitalize"
              >
                <span itemprop="name">{{ product.subcategory.replace(/-/g, " ") }}</span>
              </NuxtLink>
              <meta itemprop="position" content="3" />
            </li>
          </template>
          <li aria-hidden="true">
            <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5" />
          </li>
          <li>
            <span
              class="text-gray-900 font-bold truncate max-w-[220px] block"
              aria-current="page"
            >
              {{ product.title }}
            </span>
          </li>
        </ol>
      </nav>

      <!-- ── Konten utama ──────────────────────────────────────── -->
      <div
        class="flex flex-col lg:flex-row gap-8 items-start bg-white p-6 rounded-3xl shadow-sm border border-gray-100"
        itemscope
        itemtype="https://schema.org/Product"
      >
        <!-- Galeri gambar -->
        <div class="w-full lg:w-[380px] shrink-0 sticky top-24">
          <div
            class="rounded-2xl border border-gray-200 overflow-hidden mb-4 relative aspect-square bg-[#f9fafb] cursor-zoom-in group"
            @mousemove="handleMouseMove"
            @mouseenter="handleMouseEnter"
            @mouseleave="handleMouseLeave"
          >
            <NuxtImg
              :src="activeImage"
              :alt="`Foto ${product.brand} ${product.title}`"
              class="w-full h-full object-contain p-4 transition-transform duration-200 ease-out will-change-transform"
              :style="zoomStyle"
              width="600"
              height="600"
              format="webp"
              quality="85"
              loading="eager"
              fetchpriority="high"
              itemprop="image"
            />
            <div
              class="absolute bottom-3 right-3 bg-black/60 text-white text-[11px] font-bold px-2.5 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none flex items-center gap-1.5"
            >
              <UIcon name="i-heroicons-magnifying-glass-plus" class="w-4 h-4" /> Zoom
            </div>
          </div>

          <div
            class="flex gap-3 overflow-x-auto pb-2 custom-scrollbar"
            role="list"
            aria-label="Galeri produk"
          >
            <button
              v-for="(img, idx) in product.images"
              :key="idx"
              :aria-label="`Lihat gambar ${idx + 1}`"
              :aria-pressed="activeImage === img"
              role="listitem"
              class="w-16 h-16 shrink-0 rounded-xl border-2 overflow-hidden bg-[#f9fafb] transition-all p-1.5"
              :class="
                activeImage === img
                  ? 'border-green-500'
                  : 'border-transparent hover:border-gray-300'
              "
              @click="activeImage = img"
            >
              <NuxtImg
                :src="img"
                :alt="`${product.title} gambar ${idx + 1}`"
                class="w-full h-full object-contain rounded-md"
                width="64"
                height="64"
                format="webp"
                quality="70"
                loading="lazy"
              />
            </button>
          </div>
        </div>

        <!-- Info produk -->
        <div class="flex-1 min-w-0">
          <p
            class="sr-only"
            itemprop="brand"
            itemscope
            itemtype="https://schema.org/Brand"
          >
            <span itemprop="name">{{ product.brand }}</span>
          </p>
          <meta itemprop="sku" :content="product.id" />
          <meta itemprop="mpn" :content="product.id" />

          <h1
            class="text-[26px] font-black text-gray-900 leading-snug mb-3"
            itemprop="name"
          >
            {{ product.brand }} {{ product.title }}
          </h1>

          <div
            class="flex flex-wrap items-center gap-4 text-sm mb-5 border-b border-gray-100 pb-5"
          >
            <span
              class="bg-gray-100 text-gray-800 px-2.5 py-1 rounded-md text-xs font-black uppercase tracking-wider"
            >
              {{ product.brand }}
            </span>
            <div
              class="flex items-center gap-1 text-yellow-400"
              itemprop="aggregateRating"
              itemscope
              itemtype="https://schema.org/AggregateRating"
            >
              <UIcon name="i-heroicons-star-solid" class="w-4 h-4" aria-hidden="true" />
              <span class="font-bold text-gray-700" itemprop="ratingValue">5.0</span>
              <meta itemprop="reviewCount" :content="String(Math.max(product.sold, 1))" />
              <meta itemprop="bestRating" content="5" />
            </div>
            <div class="w-1 h-1 bg-gray-300 rounded-full" aria-hidden="true" />
            <span class="text-gray-500"
              >Terjual
              <span class="text-gray-900 font-bold">{{ product.sold }}</span></span
            >
          </div>

          <!-- Harga -->
          <div
            class="mb-8"
            itemprop="offers"
            itemscope
            itemtype="https://schema.org/Offer"
          >
            <link itemprop="url" :href="canonicalUrl" />
            <meta itemprop="priceCurrency" content="IDR" />
            <meta itemprop="price" :content="String(unitPrice)" />
            <link
              itemprop="availability"
              :href="
                product.stock > 0
                  ? 'https://schema.org/InStock'
                  : 'https://schema.org/OutOfStock'
              "
            />
            <div
              v-if="product.discountPercentage > 0"
              class="flex items-center gap-2.5 mb-1.5"
            >
              <span
                class="bg-red-100 text-red-600 text-xs font-black px-2 py-0.5 rounded-md"
                >Diskon {{ product.discountPercentage }}%</span
              >
              <span class="text-sm font-semibold text-gray-400 line-through">{{
                formatPrice(product.originalPrice)
              }}</span>
            </div>
            <p
              class="text-4xl font-black tracking-tight"
              :class="product.discountPercentage > 0 ? 'text-red-600' : 'text-gray-900'"
            >
              {{ formatPrice(unitPrice) }}
            </p>
          </div>

          <!-- Varian HDD -->
          <div
            v-if="isPaket"
            class="mb-8 p-4 rounded-xl border border-gray-100 bg-gray-50"
          >
            <h2 class="font-bold text-gray-900 mb-3 text-base">
              Pilih Penyimpanan:
              <span class="text-green-600">{{ selectedHdd.label }}</span>
            </h2>
            <div class="flex flex-wrap gap-2.5">
              <button
                v-for="opt in hddOptions"
                :key="opt.label"
                :aria-pressed="selectedHdd.label === opt.label"
                class="px-4 py-2 border-2 rounded-xl text-sm font-bold transition-all"
                :class="
                  selectedHdd.label === opt.label
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-200 text-gray-600 hover:border-gray-300 bg-white'
                "
                @click="selectedHdd = opt"
              >
                {{ opt.label }}
                <span
                  v-if="opt.price > 0"
                  class="block text-[10px] font-medium mt-0.5 opacity-70"
                  >+ {{ formatPrice(opt.price) }}</span
                >
              </button>
            </div>
          </div>

          <!-- Spesifikasi & Deskripsi -->
          <div>
            <h2
              class="pb-2 border-b-2 border-green-500 text-gray-900 font-bold text-sm tracking-wide inline-block mb-5"
            >
              Spesifikasi &amp; Deskripsi
            </h2>
            <div class="text-sm text-gray-700 leading-relaxed">
              <div
                v-if="product.specs && Object.keys(product.specs).length > 0"
                class="mb-6 border border-gray-100 rounded-xl overflow-hidden"
              >
                <table class="w-full text-left text-sm">
                  <caption class="sr-only">
                    Spesifikasi
                    {{
                      product.brand
                    }}
                    {{
                      product.title
                    }}
                  </caption>
                  <tbody>
                    <tr class="border-b border-gray-100 bg-gray-50/50">
                      <th
                        scope="row"
                        class="py-2.5 px-4 text-gray-500 font-semibold w-1/3"
                      >
                        Kategori
                      </th>
                      <td class="py-2.5 px-4 font-bold text-gray-900 capitalize">
                        {{ product.category.replace(/-/g, " ") }}
                      </td>
                    </tr>
                    <tr v-if="product.weight" class="border-b border-gray-100">
                      <th
                        scope="row"
                        class="py-2.5 px-4 text-gray-500 font-semibold w-1/3"
                      >
                        Berat
                      </th>
                      <td class="py-2.5 px-4 font-bold text-gray-900">
                        {{ formatWeight(product.weight) }}
                      </td>
                    </tr>
                    <tr
                      v-for="(val, key) in product.specs"
                      :key="key"
                      class="border-b border-gray-100 last:border-0 hover:bg-gray-50/50 transition-colors"
                      itemprop="additionalProperty"
                      itemscope
                      itemtype="https://schema.org/PropertyValue"
                    >
                      <th
                        scope="row"
                        class="py-2.5 px-4 text-gray-500 font-semibold w-1/3 capitalize font-normal"
                        itemprop="name"
                      >
                        {{ String(key).replace(/_/g, " ") }}
                      </th>
                      <td
                        class="py-2.5 px-4 font-bold text-gray-900 capitalize"
                        itemprop="value"
                      >
                        {{ val }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div
                class="whitespace-pre-line text-gray-600 text-[15px]"
                itemprop="description"
              >
                {{ product.description }}
              </div>
            </div>
          </div>
        </div>

        <!-- ── Sidebar keranjang ─────────────────────────────────── -->
        <div class="w-full lg:w-[320px] shrink-0">
          <div
            class="sticky top-24 border border-gray-200 rounded-2xl p-5 shadow-sm bg-white"
          >
            <h2 class="font-bold text-gray-900 mb-4 text-base">Atur Jumlah</h2>

            <div class="flex items-center gap-3 mb-5">
              <div class="flex items-center border-2 border-gray-200 rounded-xl p-1">
                <button
                  :disabled="quantity <= 1"
                  aria-label="Kurangi jumlah"
                  class="w-8 h-8 flex items-center justify-center font-black text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-30"
                  @click="quantity > 1 && quantity--"
                >
                  −
                </button>
                <input
                  v-model.number="quantity"
                  type="number"
                  :min="1"
                  :max="product.stock"
                  aria-label="Jumlah produk"
                  class="w-12 text-center text-sm font-bold outline-none border-none focus:ring-0"
                />
                <button
                  :disabled="quantity >= product.stock"
                  aria-label="Tambah jumlah"
                  class="w-8 h-8 flex items-center justify-center font-black text-green-600 hover:bg-green-50 rounded-lg disabled:opacity-30"
                  @click="quantity < product.stock && quantity++"
                >
                  +
                </button>
              </div>
              <p class="text-[13px] text-gray-500 font-medium">
                Stok:
                <span v-if="product.stock > 0" class="font-black text-gray-900">{{
                  product.stock
                }}</span>
                <span v-else class="font-black text-red-600 bg-red-50 px-2 py-0.5 rounded"
                  >Habis</span
                >
              </p>
            </div>

            <div
              class="flex justify-between items-center mb-6 pt-4 border-t border-gray-100"
            >
              <span class="text-gray-500 text-sm font-bold">Subtotal</span>
              <span class="text-xl font-black text-gray-900">{{
                formatPrice(totalPrice)
              }}</span>
            </div>

            <div class="space-y-3 mb-6">
              <AddChartButton
                v-if="cartItem"
                :product="cartItem"
                class="w-full"
                :disabled="product.stock === 0"
              />
              <button
                :disabled="product.stock === 0"
                @click="beliLangsung"
                class="w-full border border-black text-white bg-black font-bold py-3 rounded-xl hover:bg-gray-800 transition-all text-sm disabled:bg-gray-200 disabled:text-gray-400 disabled:border-gray-200 disabled:cursor-not-allowed"
              >
                Beli Langsung
              </button>
            </div>

            <div
              class="flex justify-around pt-4 text-xs font-bold text-gray-500 border-t border-gray-100"
            >
              <!-- ✅ Chat button — set context + navigate ke home -->
              <button
                class="flex flex-col items-center gap-1.5 hover:text-green-600 transition-colors group"
                aria-label="Chat dengan penjual tentang produk ini"
                @click="openChat"
              >
                <div class="relative">
                  <UIcon
                    name="i-heroicons-chat-bubble-left-ellipsis"
                    class="w-5 h-5"
                    aria-hidden="true"
                  />
                  <!-- dot indicator — ada unread -->
                  <span
                    v-if="pesanStore.unreadCount > 0"
                    class="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full border border-white"
                  />
                </div>
                Chat
              </button>

              <button
                class="flex flex-col items-center gap-1.5 transition-colors"
                :class="isWishlisted ? 'text-red-600' : 'hover:text-red-600'"
                :aria-label="isWishlisted ? 'Hapus dari wishlist' : 'Tambah ke wishlist'"
                @click="toggleWishlist"
              >
                <UIcon
                  :name="isWishlisted ? 'i-heroicons-heart-solid' : 'i-heroicons-heart'"
                  class="w-5 h-5"
                  aria-hidden="true"
                />
                Wishlist
              </button>

              <button
                class="flex flex-col items-center gap-1.5 hover:text-blue-600 transition-colors"
                aria-label="Bagikan produk"
                @click="handleShare"
              >
                <UIcon name="i-heroicons-share" class="w-5 h-5" aria-hidden="true" />
                Share
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Rekomendasi -->
      <section class="mt-12" aria-label="Produk serupa">
        <ProductRecommendation :items="recommendations" />
      </section>
    </div>
  </main>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap");
.font-jakarta {
  font-family: "Plus Jakarta Sans", sans-serif;
}

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  appearance: textfield;
  -moz-appearance: textfield;
}

.custom-scrollbar::-webkit-scrollbar {
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 10px;
}
</style>
