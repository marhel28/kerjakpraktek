<script setup lang="ts">
import { computed, ref } from "vue";

// ─── SEO ─────────────────────────────────────────────────────────
const siteUrl = useRuntimeConfig().public.siteUrl ?? "https://yourdomain.com";

useSeoMeta({
  title: "Brand Resmi CCTV — Dahua, Imou, Ezviz | PasarCctv",
  description:
    "Distributor resmi brand CCTV terpercaya: Dahua, Imou, Ezviz, dan lainnya. Produk original bergaransi, harga terbaik, pengiriman ke seluruh Indonesia.",
  ogTitle: "Brand Resmi CCTV | PasarCctv",
  ogDescription:
    "Katalog brand CCTV original bergaransi resmi. Dahua, Imou, Ezviz, dan lebih banyak lagi.",
  ogUrl: `${siteUrl}/brands`,
  ogType: "website",
  twitterCard: "summary_large_image",
  robots: "index, follow",
});

useHead({
  link: [{ rel: "canonical", href: `${siteUrl}/brands` }],
  script: computed(() => [
    {
      type: "application/ld+json",
      key: "jsonld-brands",
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        name: "Brand Resmi CCTV",
        description: "Katalog brand CCTV resmi dan bergaransi",
        url: `${siteUrl}/brands`,
        publisher: { "@type": "Organization", name: "PasarCctv", url: siteUrl },
      }),
    },
  ]),
});

// ─── Fetch: cache 30 detik, stale 2 menit ─────────────────────────
const { data: brandsData, pending } = await useFetch<any[]>("/api/brands", {
  key: "brands:index",
  lazy: true,
  server: true,
  getCachedData: (key, nuxtApp) => nuxtApp.payload.data[key] ?? nuxtApp.static.data[key],
  transform: (data) => {
    if (!data) return [];
    return data.map((b) => ({
      id: b.brand_slug,
      name: b.brand_name,
      logo: b.brand_logo,
      tagline: `Produk resmi dan bergaransi dari ${b.brand_name}.`,
      total: b.total_items,
      products: (b.products || []).map((p: any) => ({
        uuid: p.uuid,
        slug: p.slug,
        title: p.title,
        brand: b.brand_name,
        price: p.price,
        original_price: p.original_price || p.price,
        discount_percentage: p.discount_percentage || 0,
        image: p.image,
        specs: p.specs || {},
        terjual: p.terjual || 0,
        category: p.category || "",
        subcategory: p.subcategory || "",
        type: p.type || "",
      })),
    }));
  },
});

const brands = computed(() => brandsData.value || []);

// ─── Drag to Scroll Logic (Desktop Mouse) ─────────────────────────
const isDragging = ref(false);
const startX = ref(0);
const scrollLeft = ref(0);
let activeSlider: HTMLElement | null = null;

const startDrag = (e: MouseEvent) => {
  isDragging.value = true;
  activeSlider = e.currentTarget as HTMLElement;
  startX.value = e.pageX - activeSlider.offsetLeft;
  scrollLeft.value = activeSlider.scrollLeft;
};

const stopDrag = () => {
  isDragging.value = false;
  activeSlider = null;
};

const doDrag = (e: MouseEvent) => {
  if (!isDragging.value || !activeSlider) return;
  e.preventDefault();
  const x = e.pageX - activeSlider.offsetLeft;
  const walk = (x - startX.value) * 1.5; // Kecepatan scroll
  activeSlider.scrollLeft = scrollLeft.value - walk;
};
</script>

<template>
  <main class="brands-page min-h-screen bg-gray-100 lg:bg-[#F3F4F5] pb-20 lg:pb-8">
    <header
      class="relative bg-[#212121] px-5 py-8 md:px-8 md:py-12 border-b-[5px] border-red-600"
    >
      <div class="relative max-w-[1400px] mx-auto">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div class="hero-text text-white">
            <p
              class="text-[10px] md:text-xs font-black text-red-500 mb-2 flex items-center gap-1.5 uppercase tracking-widest"
            >
              <UIcon name="i-heroicons-shield-check" class="w-4 h-4" />
              Sistem Keamanan
            </p>
            <h1
              class="text-2xl md:text-4xl font-extrabold mb-3 leading-tight tracking-tight"
            >
              Mitra Resmi <br class="lg:hidden" />
              PasarCctv
            </h1>
            <p
              class="text-xs md:text-sm text-gray-400 max-w-2xl font-medium leading-relaxed"
            >
              Kami bermitra langsung dengan produsen teknologi keamanan ternama — menjamin
              keaslian produk, garansi resmi, dan kualitas terbaik untuk Anda.
            </p>
          </div>

          <div
            class="flex gap-8 shrink-0 border-t border-gray-700/50 pt-5 md:border-none md:pt-0"
          >
            <div class="flex flex-col" v-if="!pending">
              <span class="text-xl md:text-3xl font-black text-white leading-none">{{
                brands.length
              }}</span>
              <span
                class="text-[10px] md:text-xs text-gray-400 font-bold uppercase tracking-wider mt-1"
                >Brand Mitra</span
              >
            </div>
            <div class="flex flex-col" v-if="!pending">
              <span class="text-xl md:text-3xl font-black text-white leading-none">
                {{ brands.reduce((s, b) => s + (b.total || 0), 0) }}+
              </span>
              <span
                class="text-[10px] md:text-xs text-gray-400 font-bold uppercase tracking-wider mt-1"
                >Total Produk</span
              >
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-[1400px] mx-auto lg:px-6 lg:py-8">
      <div
        v-if="pending"
        class="space-y-2 lg:space-y-8"
        aria-busy="true"
        aria-label="Memuat data brand"
      >
        <div
          v-for="i in 3"
          :key="i"
          class="bg-white p-4 lg:p-0 flex flex-col lg:flex-row gap-4 lg:bg-transparent"
        >
          <div class="flex gap-3 lg:hidden items-center mb-2">
            <USkeleton class="w-10 h-10 rounded-full shrink-0" />
            <div class="flex-1">
              <USkeleton class="h-4 w-24 mb-1" />
              <USkeleton class="h-3 w-16" />
            </div>
          </div>
          <USkeleton class="hidden lg:block w-[240px] h-[320px] rounded-xl shrink-0" />
          <div class="flex gap-3 overflow-hidden">
            <USkeleton
              v-for="j in 4"
              :key="j"
              class="w-[140px] md:w-[190px] h-[240px] rounded-lg shrink-0"
            />
          </div>
        </div>
      </div>

      <div
        v-else-if="brands.length"
        class="flex flex-col gap-2.5 lg:gap-8"
        itemscope
        itemtype="https://schema.org/ItemList"
      >
        <meta itemprop="name" content="Brand Resmi CCTV" />

        <section
          v-for="(brand, idx) in brands"
          :key="brand.id"
          class="bg-white lg:bg-transparent border-y lg:border-none border-gray-200/60 py-3 lg:py-0 flex flex-col lg:flex-row lg:items-stretch gap-0 lg:gap-6"
          itemprop="itemListElement"
          itemscope
          itemtype="https://schema.org/ListItem"
          :aria-labelledby="`brand-${brand.id}-heading`"
        >
          <meta itemprop="position" :content="String(idx + 1)" />

          <NuxtLink
            :to="`/brands/${brand.id}`"
            class="group flex flex-row lg:flex-col items-center lg:items-stretch px-4 lg:px-0 lg:w-[260px] shrink-0 lg:p-6 lg:bg-white lg:border lg:border-gray-200 lg:rounded-2xl lg:hover:border-red-500 lg:hover:shadow-lg transition-all duration-300"
            :title="`Lihat semua produk ${brand.name}`"
            itemprop="item"
            itemscope
            itemtype="https://schema.org/Brand"
          >
            <div
              class="w-12 h-12 lg:w-full lg:h-auto lg:aspect-[4/3] shrink-0 border border-gray-100 lg:border-gray-200 rounded-full lg:rounded-xl flex items-center justify-center p-1.5 lg:p-4 bg-white overflow-hidden mb-0 lg:mb-4"
            >
              <NuxtImg
                :src="brand.logo"
                :alt="`Logo resmi ${brand.name}`"
                :title="brand.name"
                itemprop="logo"
                width="160"
                height="120"
                format="webp"
                quality="90"
                loading="lazy"
                class="w-full h-full object-contain"
              />
            </div>

            <div class="flex-1 min-w-0 ml-3 lg:ml-0 flex flex-col justify-center">
              <div class="flex items-center gap-1 mb-0.5 lg:mb-2">
                <UIcon
                  name="i-heroicons-shield-check-solid"
                  class="w-3.5 h-3.5 lg:w-5 lg:h-5 text-blue-500 shrink-0"
                />
                <h2
                  :id="`brand-${brand.id}-heading`"
                  itemprop="name"
                  class="text-sm lg:text-xl font-extrabold text-gray-900 truncate"
                >
                  {{ brand.name }}
                </h2>
              </div>
              <p
                class="hidden lg:block text-xs text-gray-500 line-clamp-2 leading-relaxed"
              >
                {{ brand.tagline }}
              </p>
              <p class="lg:hidden text-[10px] text-gray-500 font-medium">
                Official Store
              </p>

              <div
                class="hidden lg:flex mt-auto pt-4 border-t border-gray-100 items-center justify-between"
              >
                <span class="text-xs font-bold text-gray-400"
                  >{{ brand.total }} Produk</span
                >
                <span
                  class="text-red-600 text-xs font-black uppercase tracking-wider flex items-center gap-1 group-hover:gap-2 transition-all"
                >
                  Lihat <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
                </span>
              </div>
            </div>

            <div class="lg:hidden shrink-0 ml-2">
              <span
                class="inline-block bg-red-50 text-red-600 text-[10px] font-black uppercase tracking-widest px-3 py-1.5 rounded-full active:scale-95 transition-transform"
              >
                Kunjungi
              </span>
            </div>
          </NuxtLink>

          <div class="flex-1 min-w-0 flex flex-col mt-3 lg:mt-0 overflow-hidden">
            <div class="hidden lg:flex items-center justify-between mb-4">
              <h3 class="text-lg font-black text-gray-800">Pilihan Terpopuler</h3>
            </div>

            <div
              class="flex gap-2.5 lg:gap-4 overflow-x-auto px-4 lg:px-1 pb-3 pt-1 snap-x snap-mandatory hide-scrollbar overscroll-x-contain cursor-grab active:cursor-grabbing"
              role="list"
              @mousedown="startDrag"
              @mouseleave="stopDrag"
              @mouseup="stopDrag"
              @mousemove="doDrag"
            >
              <div
                v-for="product in brand.products"
                :key="product.uuid"
                class="w-[140px] md:w-[190px] shrink-0 snap-start pointer-events-none select-none h-full"
                role="listitem"
              >
                <div class="pointer-events-auto h-full">
                  <CardPerItems
                    v-bind="product"
                    class="h-full border border-gray-100 shadow-sm hover:shadow-md hover:border-red-500 transition-all rounded-xl"
                  />
                </div>
              </div>

              <NuxtLink
                :to="`/brands/${brand.id}`"
                class="w-[120px] md:w-[190px] shrink-0 snap-start flex flex-col items-center justify-center bg-gray-50 border border-gray-100 rounded-xl pointer-events-auto active:scale-95 lg:hover:border-red-500 lg:hover:bg-red-50 transition-all group"
                :aria-label="`Jelajahi semua produk ${brand.name}`"
              >
                <div
                  class="w-10 h-10 md:w-14 md:h-14 bg-white shadow-sm text-gray-400 group-hover:text-red-600 rounded-full flex items-center justify-center mb-2 md:mb-3 transition-colors"
                >
                  <UIcon
                    name="i-heroicons-arrow-right-20-solid"
                    class="w-5 h-5 md:w-6 md:h-6"
                    aria-hidden="true"
                  />
                </div>
                <span
                  class="text-[10px] md:text-sm font-black uppercase tracking-wider text-gray-500 group-hover:text-red-600 text-center leading-tight"
                >
                  Lihat <br />
                  Semua
                </span>
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <div
        v-else
        class="flex flex-col items-center justify-center py-20 px-5 mx-4 lg:mx-0 border border-gray-200 rounded-2xl bg-white mt-4"
        role="status"
      >
        <div
          class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mb-4"
        >
          <UIcon
            name="i-heroicons-building-storefront"
            class="w-10 h-10 text-gray-400"
            aria-hidden="true"
          />
        </div>
        <h2 class="text-lg font-black text-gray-800 mb-2">Belum Ada Brand</h2>
        <p class="text-gray-500 text-xs text-center max-w-sm leading-relaxed">
          Sistem sedang memproses data katalog mitra resmi kami. Silakan muat ulang
          halaman.
        </p>
      </div>
    </div>
  </main>
</template>

<style scoped>
/* ── Font ── */
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap");

.brands-page {
  font-family: "Plus Jakarta Sans", sans-serif;
}

/* ── Utilitas Native App Feel ── */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Mencegah highlight biru saat di-tap di mobile */
a,
button {
  -webkit-tap-highlight-color: transparent;
}
</style>
