<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const brandSlug = route.params.id as string
const siteUrl = useRuntimeConfig().public.siteUrl ?? 'https://yourdomain.com'

// ========================================================================
// 1. STATE MANAGEMENT (Silent Fetching Tanpa Ubah URL)
// ========================================================================

const initialSearch = (route.query.q as string) || ''
const initialSort = (route.query.sort as string) || 'newest'

const localSearchInput = ref(initialSearch) 
const activeSearchQuery = ref(initialSearch) 
const selectedSort = ref(initialSort)
const currentPage = ref(1)

const handleSearch = () => {
  activeSearchQuery.value = localSearchInput.value
  currentPage.value = 1 
}

const handleSortChange = () => {
  currentPage.value = 1
}

const clearSearch = () => {
  localSearchInput.value = ''
  activeSearchQuery.value = ''
  currentPage.value = 1
}

const sortOptions = [
  { label: 'Terbaru', value: 'newest' },
  { label: 'Harga Terendah', value: 'price_asc' },
  { label: 'Harga Tertinggi', value: 'price_desc' },
  { label: 'Terlaris', value: 'popular' },
]

// ========================================================================
// 2. SEO & BRAND IDENTITY (Blocking API)
// ========================================================================

const { data: brandProfile } = await useFetch<any>('/api/brands', {
  key: `brand-profile:${brandSlug}`,
  server: true, 
  transform: (data) => {
    if (!data) return null
    return data.find((b: any) => b.brand_slug === brandSlug) || null
  },
})

const displayBrandName = computed(() => {
  if (brandProfile.value?.brand_name) return brandProfile.value.brand_name
  return brandSlug.split('-').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
})
const displayBrandLogo = computed(() => brandProfile.value?.brand_logo || '')
const totalFromProfile = computed(() => brandProfile.value?.total_items || 0)

useSeoMeta({
  title: () => `${displayBrandName.value} Official Store — PasarCctv`,
  description: () => `Katalog produk resmi ${displayBrandName.value}. Harga terbaik, garansi resmi, tersedia pengiriman seluruh Indonesia.`,
  ogTitle: () => `${displayBrandName.value} Official Store`,
  ogImage: displayBrandLogo,
  robots: 'index, follow',
})

useHead({
  link: [{ rel: 'canonical', href: `${siteUrl}/brands/${brandSlug}` }]
})

// ========================================================================
// 3. PRODUCT FETCHING (Lazy API - Reactivity via Watcher)
// ========================================================================

const { data: productData, pending } = await useFetch('/api/search', {
  lazy: true,
  server: true,
  watch: [selectedSort, activeSearchQuery, currentPage], 
  query: computed(() => {
    const payload: Record<string, any> = {
      brand: brandSlug,
      sort: selectedSort.value,
      size: 24,
      page: currentPage.value,
    }
    if (activeSearchQuery.value) {
      payload.q = activeSearchQuery.value
    }
    return payload
  }),
})

const products = computed(() => productData.value?.items || [])
const totalProducts = computed(() => productData.value?.total || 0)
</script>

<template>
  <main class="brand-page min-h-screen bg-[#F4F5F7]">

    <div class="brand-hero">
      <div class="brand-hero__noise" aria-hidden="true" />
      <div class="brand-hero__blob brand-hero__blob--1" aria-hidden="true" />
      <div class="brand-hero__blob brand-hero__blob--2" aria-hidden="true" />

      <div class="brand-hero__inner">
        <nav aria-label="Breadcrumb" class="brand-breadcrumb">
          <ol class="flex items-center gap-1.5 list-none p-0 m-0">
            <li><NuxtLink to="/" class="brand-breadcrumb__link">Beranda</NuxtLink></li>
            <li><UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-gray-400" /></li>
            <li><NuxtLink to="/brands" class="brand-breadcrumb__link">Brand Resmi</NuxtLink></li>
            <li><UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-gray-400" /></li>
            <li><span class="brand-breadcrumb__current">{{ displayBrandName }}</span></li>
          </ol>
        </nav>

        <div class="brand-identity">
          <div class="brand-logo-box">
            <NuxtImg
              v-if="displayBrandLogo"
              :src="displayBrandLogo"
              :alt="`Logo ${displayBrandName}`"
              width="120"
              height="60"
              format="webp"
              fetchpriority="high"
              loading="eager"
              class="max-w-full max-h-full object-contain mix-blend-multiply"
            />
            <span v-else class="brand-logo-box__fallback">{{ displayBrandName.charAt(0) }}</span>
          </div>

          <div class="brand-identity__info">
            <div class="brand-identity__badge">
              <UIcon name="i-heroicons-shield-check" class="w-3.5 h-3.5" /> Official Store
            </div>
            <h1 class="brand-identity__name">{{ displayBrandName }}</h1>
            <p class="brand-identity__sub">Produk original bergaransi resmi · Pengiriman ke seluruh Indonesia</p>
          </div>

          <div class="brand-stat">
            <span class="brand-stat__num">{{ pending ? '—' : totalProducts }}</span>
            <span class="brand-stat__label">Produk<br/>Ditemukan</span>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-[1400px] mx-auto px-4 md:px-6 pt-7 pb-16">

      <div class="toolbar">
        <div class="toolbar__left">
          <span class="toolbar__accent" aria-hidden="true" />
          <h2 class="toolbar__title hidden sm:block">Semua Produk</h2>

          <form @submit.prevent="handleSearch" class="relative flex-grow max-w-xs sm:ml-4">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
            </span>
            <input 
              v-model="localSearchInput"
              type="text" 
              :placeholder="`Cari di ${displayBrandName}...`" 
              class="w-full bg-gray-50 border border-gray-200 rounded-lg pl-9 pr-3 py-1.5 text-sm font-semibold text-black placeholder-gray-400 focus:bg-white focus:border-green-500 focus:ring-1 focus:ring-green-500 outline-none transition-all"
            >
          </form>
        </div>

        <div class="toolbar__right">
          <label for="sort-select" class="toolbar__sort-label">Urutkan:</label>
          <select
            id="sort-select"
            v-model="selectedSort"
            @change="handleSortChange"
            class="toolbar__select"
          >
            <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
      </div>

      <div v-if="pending" class="products-grid">
        <CardPerItemSkeleton v-for="i in 10" :key="`skeleton-${i}`" />
      </div>

      <div v-else-if="products.length" class="products-grid">
        <div
          v-for="(product, index) in products"
          :key="product.uuid"
          class="product-item"
          :style="{ animationDelay: `${(index % 10) * 40}ms` }"
        >
          <CardPerItems
            :uuid="product.uuid"
            :slug="product.slug"
            :title="product.title"
            :brand="product.brand"
            :type="product.type"
            :specs="product.specs || {}"
            :price="product.price"
            :original_price="product.original_price || 0"
            :discount_percentage="product.discount_percentage || 0"
            :terjual="product.terjual || 0"
            :category="product.category || ''"
            :subcategory="product.subcategory || ''"
            :image="product.image || '/images/no-image.webp'"
            class="h-full"
          />
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-state__icon">
          <UIcon name="i-heroicons-magnifying-glass" class="w-9 h-9 text-gray-300" />
        </div>
        <h2 class="empty-state__title">
          {{ activeSearchQuery ? 'Pencarian Tidak Ditemukan' : 'Produk Kosong' }}
        </h2>
        <p class="empty-state__sub">
          <template v-if="activeSearchQuery">
            Kami tidak dapat menemukan produk yang cocok dengan 
            <strong class="text-gray-700">"{{ activeSearchQuery }}"</strong> 
            pada brand {{ displayBrandName }}.
          </template>
          <template v-else>
            Saat ini belum ada produk untuk brand <strong class="text-gray-700">{{ displayBrandName }}</strong>.
          </template>
        </p>
        <button v-if="activeSearchQuery" @click="clearSearch" class="empty-state__btn">
          Hapus Pencarian
        </button>
        <NuxtLink v-else to="/brands" class="empty-state__btn">
          Kembali ke Daftar Brand
        </NuxtLink>
      </div>

    </div>
  </main>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

.brand-page { font-family: 'Plus Jakarta Sans', sans-serif; }

/* ── Hero Styles ── */
.brand-hero { position: relative; background: #fff; border-bottom: 1px solid #f0f0f0; padding: 2rem 0 2.25rem; overflow: hidden; background-image: linear-gradient(135deg, #f7fdf9 0%, #ffffff 60%); }
.brand-hero__noise { position: absolute; inset: 0; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.018'/%3E%3C/svg%3E"); pointer-events: none; }
.brand-hero__blob { position: absolute; border-radius: 50%; pointer-events: none; filter: blur(60px); }
.brand-hero__blob--1 { width: 360px; height: 360px; background: rgba(0, 170, 91, 0.07); top: -120px; right: -60px; }
.brand-hero__blob--2 { width: 200px; height: 200px; background: rgba(66, 181, 73, 0.05); bottom: -60px; left: 10%; }
.brand-hero__inner { position: relative; z-index: 1; max-width: 1400px; margin: 0 auto; padding: 0 1rem; }
@media (min-width: 768px) { .brand-hero__inner { padding: 0 1.5rem; } }

/* ── Typography & Layout ── */
.brand-breadcrumb { margin-bottom: 1.25rem; }
.brand-breadcrumb__link { font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.08em; text-decoration: none; transition: color 0.15s; }
.brand-breadcrumb__link:hover { color: #00aa5b; }
.brand-breadcrumb__current { font-size: 11px; font-weight: 800; color: #374151; text-transform: uppercase; letter-spacing: 0.08em; }
.brand-identity { display: flex; align-items: center; gap: 1.25rem; flex-wrap: wrap; }
.brand-logo-box { width: 80px; height: 80px; background: #fff; border: 1.5px solid #e5e7eb; border-radius: 1rem; display: flex; align-items: center; justify-content: center; padding: 0.875rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06); flex-shrink: 0; }
@media (min-width: 768px) { .brand-logo-box { width: 96px; height: 96px; } }
.brand-logo-box__fallback { font-size: 2rem; font-weight: 900; color: #d1d5db; text-transform: uppercase; }
.brand-identity__info { flex: 1; min-width: 0; }
.brand-identity__badge { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 10px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: #00aa5b; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 3px 8px; margin-bottom: 0.5rem; }
.brand-identity__name { font-size: clamp(1.75rem, 4vw, 2.75rem); font-weight: 900; color: #111827; letter-spacing: -0.025em; line-height: 1; text-transform: uppercase; margin-bottom: 0.4rem; }
.brand-identity__sub { font-size: 0.8rem; color: #9ca3af; font-weight: 600; }
.brand-stat { display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 1rem; padding: 0.875rem 1.25rem; min-width: 90px; text-align: center; margin-left: auto; }
.brand-stat__num { font-size: 1.75rem; font-weight: 900; color: #00aa5b; line-height: 1; }
.brand-stat__label { font-size: 10px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; line-height: 1.3; }

/* ── Toolbar ── */
.toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; background: #fff; border: 1px solid #e5e7eb; border-radius: 1rem; padding: 0.75rem 1rem; margin-bottom: 1.25rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.toolbar__left { display: flex; align-items: center; gap: 0.625rem; width: 100%; }
@media (min-width: 640px) { .toolbar__left { width: auto; flex: 1; } }
.toolbar__accent { display: block; width: 4px; height: 1.2rem; border-radius: 4px; background: linear-gradient(180deg, #42b549 0%, #00aa5b 100%); flex-shrink: 0; }
.toolbar__title { font-size: 0.875rem; font-weight: 800; color: #111827; letter-spacing: -0.01em; white-space: nowrap; }
.toolbar__right { display: flex; align-items: center; gap: 0.5rem; width: 100%; justify-content: flex-end; }
@media (min-width: 640px) { .toolbar__right { width: auto; } }
.toolbar__sort-label { font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.08em; }
.toolbar__select { background: #f9fafb; border: 1.5px solid #e5e7eb; border-radius: 0.625rem; font-size: 0.8rem; font-weight: 700; color: #374151; padding: 0.4rem 0.75rem; outline: none; cursor: pointer; transition: border-color 0.15s; font-family: 'Plus Jakarta Sans', sans-serif; }
.toolbar__select:focus { border-color: #00aa5b; }

/* ── Grids & Animations ── */
.products-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
@media (min-width: 640px)  { .products-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 768px)  { .products-grid { grid-template-columns: repeat(4, 1fr); gap: 0.875rem; } }
@media (min-width: 1280px) { .products-grid { grid-template-columns: repeat(5, 1fr); gap: 1rem; } }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
.product-item { opacity: 0; animation: fadeUp 0.38s ease-out forwards; display: flex; flex-direction: column; }

/* ── Empty State ── */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5rem 2rem; border: 2px dashed #e5e7eb; border-radius: 1.5rem; background: #fff; text-align: center; margin-top: 0.5rem; }
.empty-state__icon { width: 4.5rem; height: 4.5rem; background: #f9fafb; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 1.25rem; }
.empty-state__title { font-size: 1.15rem; font-weight: 900; color: #111827; letter-spacing: -0.01em; margin-bottom: 0.5rem; }
.empty-state__sub { font-size: 0.85rem; color: #6b7280; max-width: 320px; line-height: 1.6; margin-bottom: 1.5rem; }
.empty-state__btn { display: inline-flex; align-items: center; background: #111827; color: #fff; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.75rem 1.5rem; border-radius: 0.75rem; transition: background 0.2s; text-decoration: none; cursor: pointer; border: none; }
.empty-state__btn:hover { background: #00aa5b; }

@media (prefers-reduced-motion: reduce) { .product-item { animation: none; opacity: 1; } }
</style>