<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import CardPerItems from "~/components/CardPerItems.vue";

const route = useRoute();
const brandSlug = computed(() => (route.params.brand as string) || "");
const siteUrl = useRuntimeConfig().public.siteUrl ?? "https://yourdomain.com";

const { data: brandList } = await useFetch<any[]>("/api/brands", {
  key: "brands:collections:list",
  lazy: true,
});

const currentBrand = computed(() => {
  if (!brandList.value) return null;
  return brandList.value.find(
    (b: any) => (b.brand_slug || "").toLowerCase() === brandSlug.value.toLowerCase()
  );
});

const brandName = computed(() => {
  if (currentBrand.value?.brand_name) return currentBrand.value.brand_name;
  return brandSlug.value
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
});

useSeoMeta({
  title: () => `Koleksi Unggulan ${brandName.value} — Official Store | PasarCctv`,
  description: () =>
    `Jelajahi koleksi kategori dan seri CCTV unggulan dari ${brandName.value}. Produk original dengan garansi resmi dan diskon terbaik.`,
  ogTitle: () => `Koleksi ${brandName.value} — PasarCctv`,
  ogUrl: () => `${siteUrl}/brands/${brandSlug.value}/collections`,
});

// Search & Sort filter state
const searchQuery = ref("");
const selectedSort = ref("popular");

interface SearchResponse {
  items: any[];
  total: number;
}

const { data: searchResult, pending } = await useFetch<SearchResponse>("/api/search", {
  lazy: true,
  server: true,
  watch: [searchQuery, selectedSort],
  query: computed(() => ({
    brand: brandSlug.value,
    q: searchQuery.value || undefined,
    sort: selectedSort.value,
    size: 24,
    page: 1,
  })),
});

const products = computed(() => searchResult.value?.items || currentBrand.value?.products || []);
const totalCount = computed(() => searchResult.value?.total || products.value.length || 0);
</script>

<template>
  <main class="min-h-screen bg-[#F7F8F9] text-slate-800 pb-16">
    <!-- Header: Tokopedia Official Store Style -->
    <header class="bg-white border-b border-slate-200/80 pt-6 pb-8">
      <div class="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Breadcrumb -->
        <nav aria-label="Breadcrumb" class="flex items-center gap-2 text-xs text-slate-500 mb-4 font-medium">
          <NuxtLink to="/" class="hover:text-emerald-600 transition-colors">Beranda</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-slate-400" />
          <NuxtLink to="/brands" class="hover:text-emerald-600 transition-colors">Brand Resmi</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-slate-400" />
          <NuxtLink :to="`/brands/${brandSlug}`" class="hover:text-emerald-600 transition-colors">{{ brandName }}</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-slate-400" />
          <span class="text-[#03AC0E] font-semibold">Koleksi</span>
        </nav>

        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 sm:w-20 sm:h-20 bg-white rounded-2xl border border-slate-200 p-2.5 flex items-center justify-center shadow-xs shrink-0">
              <NuxtImg
                v-if="currentBrand?.brand_logo"
                :src="currentBrand.brand_logo"
                :alt="brandName"
                class="max-h-full max-w-full object-contain"
              />
              <span v-else class="text-2xl font-black text-slate-400">{{ brandName.charAt(0) }}</span>
            </div>
            <div>
              <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-emerald-50 text-[#03AC0E] border border-emerald-200 text-xs font-bold mb-1">
                <UIcon name="i-heroicons-check-badge" class="w-3.5 h-3.5" />
                <span>Official Brand Collection</span>
              </div>
              <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                Koleksi {{ brandName }}
              </h1>
              <p class="text-xs sm:text-sm text-slate-500 mt-0.5">
                Katalog resmi lengkap terkurasi langsung dari prinsipal resmi {{ brandName }}.
              </p>
            </div>
          </div>

          <NuxtLink
            :to="`/brands/${brandSlug}`"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 hover:bg-[#03AC0E] text-white text-xs font-bold transition shadow-xs self-start md:self-auto"
          >
            <span>Kembali ke Storefront</span>
            <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- Toolbar Filters -->
    <div class="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 mt-6">
      <div class="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-xs flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <!-- Search within brand -->
        <div class="relative flex-1 max-w-md">
          <UIcon name="i-heroicons-magnifying-glass" class="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="`Cari produk di koleksi ${brandName}...`"
            class="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#03AC0E] focus:bg-white text-slate-800 transition"
          />
        </div>

        <!-- Counter & Sort -->
        <div class="flex items-center justify-between sm:justify-end gap-3 text-xs">
          <span class="text-slate-500 font-medium">Total: <strong class="text-slate-900">{{ totalCount }}</strong> Produk</span>
          <select
            v-model="selectedSort"
            class="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 outline-none focus:ring-2 focus:ring-[#03AC0E]"
          >
            <option value="popular">Paling Populer</option>
            <option value="newest">Terbaru</option>
            <option value="price_asc">Harga Terendah</option>
            <option value="price_desc">Harga Tertinggi</option>
          </select>
        </div>
      </div>

      <!-- Products Grid (Amazon/Tokopedia clean dense card) -->
      <div v-if="pending" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4 mt-6">
        <USkeleton v-for="i in 10" :key="i" class="h-80 rounded-2xl" />
      </div>

      <div
        v-else-if="products.length > 0"
        class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4 mt-6"
      >
        <div v-for="p in products" :key="p.uuid || p.slug" class="h-full">
          <CardPerItems
            :uuid="p.uuid"
            :slug="p.slug"
            :title="p.title"
            :image="p.image || '/images/no-image.webp'"
            :price="p.price || p.online_price || 0"
            :original_price="p.original_price || 0"
            :discount_percentage="p.discount_percentage || 0"
            :brand="p.brand || brandName"
            :type="p.type || ''"
            :category="p.category || 'cctv'"
            :terjual="p.terjual || 0"
            :specs="p.specs || {}"
            class="h-full"
          />
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="bg-white border border-slate-200 rounded-2xl p-12 text-center my-8 shadow-xs">
        <div class="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3 text-slate-400">
          <UIcon name="i-heroicons-cube-transparent" class="w-7 h-7" />
        </div>
        <h3 class="text-base font-bold text-slate-900">Produk Koleksi Tidak Ditemukan</h3>
        <p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
          Belum ada produk yang sesuai dengan pencarian "{{ searchQuery }}" pada koleksi ini.
        </p>
        <button
          v-if="searchQuery"
          @click="searchQuery = ''"
          class="mt-4 px-4 py-1.5 rounded-xl bg-[#03AC0E] text-white text-xs font-bold hover:bg-[#02930c] transition"
        >
          Reset Pencarian
        </button>
      </div>
    </div>
  </main>
</template>