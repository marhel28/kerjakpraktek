<script setup lang="ts">
import { ref, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import CategoryFilter from '~/components/category/CategoryFilter.vue'
import CardPerItem from '~/components/CardPerItems.vue'
import CardPerItemSkeleton from '~/components/CardPerItemSkeleton.vue'
import BannerSection from '~/components/BannerSection.vue'

const route = useRoute()
const siteUrl = useRuntimeConfig().public.siteUrl ?? 'https://yourdomain.com'

// ─── Product state ────────────────────────────────────────────────
const products = ref<any[]>([])
const totalProducts = ref(0)
const suggestion = ref<string | null>(null)
const popularSearchesDynamic = ref<string[]>([])
const popularProducts = ref<any[]>([])
const isFetchingPopular = ref(false)

const pending = ref(true)
const isFetchingMore = ref(false)
const page = ref(1)
const hasMore = ref(true)
const loadMoreTrigger = ref<HTMLElement | null>(null)

let debounceTimer: ReturnType<typeof setTimeout>
let observer: IntersectionObserver | null = null

// ─── Slug & URL Logic ─────────────────────────────────────────────
const rawSlug = route.params.slug as string | string[] | undefined
const slugArray = Array.isArray(rawSlug)
  ? rawSlug.filter(Boolean)
  : rawSlug ? [rawSlug] : []

// Define activeSlug (last part of the slug or default)
const activeSlug = computed(() => 
  slugArray.length > 0 ? slugArray[slugArray.length - 1].toLowerCase() : 'semua-kategori'
)

// Parent slug for breadcrumb logic
const parentSlug = computed(() =>
  slugArray && slugArray.length > 1 ? slugArray[0].toLowerCase() : null
)

// Single canonical URL declaration
const canonicalUrl = computed(() => `${siteUrl}/category/${slugArray.join('/')}`)

// ─── Title & SEO ─────────────────────────────────────────────────
const pageTitle = computed(() => {
  const f = activeSlug.value.replace(/-/g, ' ').toUpperCase()
  if (f === 'SEMUA KATEGORI') return 'Katalog Produk CCTV'
  if (f === 'POPULAR') return 'Produk Terpopuler & Terlaris'
  return `Jual ${f} Terbaik`
})

const seoTitle = computed(() => `${pageTitle.value} — PasarCctv`)
const seoDesc = computed(() =>
  `Beli ${pageTitle.value} original bergaransi. Harga terbaik, pengiriman ke seluruh Indonesia. Temukan ${totalProducts.value}+ pilihan produk CCTV berkualitas.`
)

useSeoMeta({
  title: seoTitle,
  description: seoDesc,
  ogTitle: seoTitle,
  ogDescription: seoDesc,
  ogUrl: canonicalUrl,
  ogType: 'website',
  robots: 'index, follow',
})

useHead({
  link: [{ rel: 'canonical', href: canonicalUrl }],
  script: computed(() => [{
    type: 'application/ld+json',
    key: `jsonld-category-${activeSlug.value}`,
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: pageTitle.value,
      description: seoDesc.value,
      url: canonicalUrl.value,
      breadcrumb: {
        '@type': 'BreadcrumbList',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: 'Beranda', item: siteUrl },
          { '@type': 'ListItem', position: 2, name: 'Kategori', item: `${siteUrl}/category` },
          ...(parentSlug.value ? [{ '@type': 'ListItem', position: 3, name: parentSlug.value.replace(/-/g, ' '), item: `${siteUrl}/category/${parentSlug.value}` }] : []),
          { '@type': 'ListItem', position: parentSlug.value ? 4 : 3, name: pageTitle.value, item: canonicalUrl.value },
        ],
      },
    }),
  }]),
})

// ─── Banner ───────────────────────────────────────────────────────
const bannerIdentifier = computed(() =>
  activeSlug.value === 'semua-kategori' ? 'homepage-hero' : `category:${activeSlug.value}`
)
const bannerMode = computed(() =>
  activeSlug.value === 'semua-kategori' ? 'single' : 'auto'
)

// ─── Filter state ─────────────────────────────────────────────────
const searchQuery = ref('')
const selectedCategories = ref<string[]>([])
const priceRange = ref([0, 10000000])
const sortBy = ref('newest')

// Mobile filter drawer
const isFilterOpen = ref(false)

const sortOptions = [
  { label: 'Terbaru', value: 'newest' },
  { label: 'Harga ↑', value: 'price_asc' },
  { label: 'Harga ↓', value: 'price_desc' },
  { label: 'Terlaris', value: 'popular_sort' },
]



// ─── API ──────────────────────────────────────────────────────────
const fetchPopularFallback = async () => {
  if (isFetchingPopular.value) return
  isFetchingPopular.value = true
  try {
    const res = await $fetch<any>('/api/getpopular', { query: { limit: 8 } })
    if (res.items) popularProducts.value = res.items
  } catch { /* silent */ }
  finally { isFetchingPopular.value = false }
}

const fetchProducts = async (isLoadMore = false) => {
  if (!isLoadMore) {
    pending.value = true
    page.value = 1
    products.value = []
    hasMore.value = true
  } else {
    if (!hasMore.value || isFetchingMore.value) return
    isFetchingMore.value = true
  }

  try {
    const res = await $fetch<any>('/api/search', {
      query: {
        q: searchQuery.value || undefined,
        cat: selectedCategories.value.length > 0 && !selectedCategories.value.includes('semua-kategori')
          ? selectedCategories.value
          : undefined,
        min_price: priceRange.value[0],
        max_price: priceRange.value[1],
        sort: sortBy.value,
        page: page.value,
        size: 12,
      },
    })

    if (res.status === 'success') {
      const newItems = res.items
      if (!isLoadMore) products.value = newItems
      else products.value.push(...newItems)

      totalProducts.value = res.total || 0
      suggestion.value = res.suggestion || null
      hasMore.value = products.value.length < totalProducts.value
      if (res.facets?.popular_terms) popularSearchesDynamic.value = res.facets.popular_terms
      if (products.value.length === 0 && popularProducts.value.length === 0) fetchPopularFallback()
    }
  } catch { /* silent */ }
  finally { pending.value = false; isFetchingMore.value = false }
}

// ─── Watchers ────────────────────────────────────────────────────
watch([searchQuery, selectedCategories, priceRange, sortBy], () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => fetchProducts(false), 400)
}, { deep: true })

const setupObserver = () => {
  // Jika komponen sudah unmount sebelum timeout selesai, batalkan
  if (!loadMoreTrigger.value) return 

  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasMore.value && !pending.value && !isFetchingMore.value) {
        page.value++
        fetchProducts(true)
      }
    },
    { rootMargin: '300px' }
  )
  
  if (loadMoreTrigger.value) {
    observer.observe(loadMoreTrigger.value)
  }
}

const resetAllFilters = () => {
  searchQuery.value = ''
  selectedCategories.value = activeSlug.value !== 'semua-kategori' ? [activeSlug.value] : []
  priceRange.value = [0, 10000000]
}

const applySuggestion = () => {
  if (suggestion.value) { searchQuery.value = suggestion.value; suggestion.value = null }
}

// Tutup filter drawer saat navigasi
watch(() => route.path, () => { isFilterOpen.value = false })

// ─── SCROLL AUTO CLOSE ───────────────────────────────────────────
const handleScroll = () => {
  if (isFilterOpen.value) {
    // Tutup jika scroll lebih dari 30% tinggi layar
    const threshold = window.innerHeight * 0.3
    if (window.scrollY > threshold) {
      isFilterOpen.value = false
    }
  }
}

onMounted(() => {
  if (activeSlug.value !== 'semua-kategori') {
    selectedCategories.value = [activeSlug.value]
  } else {
    fetchProducts(false)
  }
  nextTick(() => setTimeout(setupObserver, 800))
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onBeforeUnmount(() => {
  observer?.disconnect()
  clearTimeout(debounceTimer)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <main class="min-h-screen bg-[#f4f5f7] font-sans overflow-x-hidden pb-24 lg:pb-10">

    <!-- ── Banner ──────────────────────────────────────────────── -->
    <BannerSection
      :identifier="bannerIdentifier"
      :mode="bannerMode"
      :autoplay-delay="4500"
      :show-title="false"
    />

    <!-- ── Breadcrumb ──────────────────────────────────────────── -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-[1400px] mx-auto px-4 md:px-6 py-4">
        <nav aria-label="Breadcrumb">
          <ol class="flex flex-wrap items-center gap-1.5 text-[11px] font-bold text-gray-400 uppercase tracking-wide list-none p-0 m-0" itemscope itemtype="https://schema.org/BreadcrumbList">
            <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
              <NuxtLink to="/" itemprop="item" class="hover:text-green-600 transition-colors">
                <span itemprop="name">Beranda</span>
              </NuxtLink>
              <meta itemprop="position" content="1" />
            </li>
            <li aria-hidden="true"><UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /></li>
            <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
              <NuxtLink to="/category" itemprop="item" class="hover:text-green-600 transition-colors">
                <span itemprop="name">Kategori</span>
              </NuxtLink>
              <meta itemprop="position" content="2" />
            </li>
            <template v-if="parentSlug">
              <li aria-hidden="true"><UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /></li>
              <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
                <NuxtLink :to="`/category/${parentSlug}`" itemprop="item" class="hover:text-green-600 transition-colors capitalize">
                  <span itemprop="name">{{ parentSlug.replace(/-/g, ' ') }}</span>
                </NuxtLink>
                <meta itemprop="position" content="3" />
              </li>
            </template>
            <li aria-hidden="true"><UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /></li>
            <li>
              <span class="text-gray-800 font-black" aria-current="page">
                {{ activeSlug === 'popular' ? 'Popular' : pageTitle }}
              </span>
            </li>
          </ol>
        </nav>

        <h1 class="text-xl md:text-2xl font-black text-gray-900 tracking-tight mt-2">
          {{ pageTitle }}
        </h1>
      </div>
    </div>

    <!-- ── Body ───────────────────────────────────────────────── -->
    <div class="max-w-[1400px] mx-auto px-4 md:px-6 pt-5">
      <div class="flex flex-col lg:flex-row gap-6">

        <!-- Sidebar filter — desktop only -->
        <aside class="hidden lg:block w-64 shrink-0" aria-label="Filter produk">
          <CategoryFilter
            v-model:search="searchQuery"
            v-model:selected="selectedCategories"
            v-model:price="priceRange"
            :dynamic-suggests="popularSearchesDynamic"
          />
        </aside>

        <!-- Product area -->
        <div class="flex-1 min-w-0 flex flex-col gap-4">

          <!-- ── Toolbar ─────────────────────────────────────── -->
          <div class="flex items-center justify-between gap-3 bg-white px-4 py-3 rounded-2xl border border-gray-200 shadow-sm">
            <div class="flex items-center gap-2.5">
              <!-- Status dot -->
              <span
                class="flex-shrink-0 w-2 h-2 rounded-full"
                :class="pending ? 'bg-orange-400 animate-pulse' : 'bg-green-500'"
                aria-hidden="true"
              />
              <p class="text-sm font-bold text-gray-700">
                <span v-if="pending">Memuat...</span>
                <template v-else>
                  <span class="text-green-600">{{ totalProducts }}</span> produk
                </template>
              </p>
            </div>

            <div class="flex items-center gap-2">
              <!-- Filter button — mobile only -->
              <button
                class="lg:hidden flex items-center gap-1.5 bg-gray-100 border border-gray-200 text-gray-700 font-bold text-xs px-3 py-2 rounded-xl transition-colors active:bg-green-50 active:border-green-300 active:text-green-700"
                aria-label="Buka filter produk"
                @click="isFilterOpen = true"
              >
                <UIcon name="i-heroicons-adjustments-horizontal" class="w-4 h-4" aria-hidden="true" />
                Filter
                <!-- Badge aktif filter -->
                <span
                  v-if="selectedCategories.length || searchQuery || priceRange[0] > 0 || priceRange[1] < 10000000"
                  class="ml-0.5 w-4 h-4 rounded-full bg-green-500 text-white text-[9px] font-black flex items-center justify-center"
                >!</span>
              </button>

              <!-- Sort select -->
              <div class="relative flex items-center">
                <select
                  v-model="sortBy"
                  aria-label="Urutkan produk"
                  class="appearance-none bg-white border border-gray-200 text-gray-700 font-bold text-xs rounded-xl pl-3 pr-8 py-2 outline-none focus:ring-2 focus:ring-green-400 cursor-pointer transition-all font-sans"
                >
                  <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
                <UIcon name="i-heroicons-chevron-down" class="absolute right-2 w-3.5 h-3.5 text-gray-400 pointer-events-none" aria-hidden="true" />
              </div>
            </div>
          </div>

          <!-- Spell suggestion -->
          <div
            v-if="suggestion && !pending && products.length === 0"
            class="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-center gap-3"
            role="alert"
          >
            <UIcon name="i-heroicons-light-bulb" class="w-5 h-5 text-blue-500 flex-shrink-0" aria-hidden="true" />
            <p class="text-sm text-blue-800">
              "<strong>{{ searchQuery }}</strong>" tidak ditemukan. Mungkin:
              <button class="font-bold text-blue-600 hover:underline" @click="applySuggestion">
                {{ suggestion }}
              </button>?
            </p>
          </div>

          <!-- Product grid -->
          <div
            v-if="pending || products.length > 0"
            class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4"
            role="list"
            aria-label="Daftar produk"
          >
            <template v-if="pending">
              <CardPerItemSkeleton v-for="i in 8" :key="`s-${i}`" />
            </template>
            <template v-else>
              <div
                v-for="item in products"
                :key="item.uuid"
                class="product-item"
                role="listitem"
              >
                <CardPerItem v-bind="item" class="h-full" />
              </div>
            </template>
            <template v-if="isFetchingMore">
              <CardPerItemSkeleton v-for="i in 4" :key="`sm-${i}`" />
            </template>
          </div>

          <!-- Empty state -->
          <div v-if="!pending && products.length === 0" class="flex flex-col gap-6 mt-2">
            <div class="flex flex-col items-center justify-center py-14 bg-white rounded-3xl border-2 border-dashed border-gray-200 text-center px-6">
              <UIcon name="i-heroicons-magnifying-glass" class="w-14 h-14 text-gray-200 mb-4" aria-hidden="true" />
              <h2 class="text-lg font-black text-gray-900 mb-1">Produk Tidak Ditemukan</h2>
              <p class="text-sm text-gray-500 mb-6 max-w-xs">
                Coba gunakan kata kunci lain atau hapus filter yang aktif.
              </p>
              <button
                class="inline-flex items-center gap-2 bg-black text-white font-bold text-sm px-6 py-3 rounded-xl hover:bg-gray-800 transition-colors"
                @click="resetAllFilters"
              >
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4" aria-hidden="true" />
                Hapus Semua Filter
              </button>
            </div>

            <!-- Promo banner di empty state -->
            <div class="rounded-2xl overflow-hidden">
              <BannerSection
                identifier="promo:ramadan-sale"
                mode="double"
                variant="dark"
                :show-title="true"
                :autoplay-delay="0"
              />
            </div>

            <!-- Rekomendasi populer -->
            <section class="bg-white p-5 rounded-3xl border border-gray-100 shadow-sm" aria-labelledby="rec-pop-heading">
              <div class="flex items-center gap-2 mb-5">
                <UIcon name="i-heroicons-fire" class="w-5 h-5 text-orange-500" aria-hidden="true" />
                <h2 id="rec-pop-heading" class="text-base font-black text-gray-900">Rekomendasi Untuk Anda</h2>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4">
                <CardPerItemSkeleton v-if="isFetchingPopular" v-for="i in 4" :key="`ps-${i}`" />
                <CardPerItem v-else v-for="item in popularProducts" :key="`pop-${item.uuid}`" v-bind="item" />
              </div>
            </section>
          </div>

          <!-- Infinite scroll trigger -->
          <div
            v-show="!pending && hasMore && products.length > 0"
            ref="loadMoreTrigger"
            class="h-10 w-full"
            aria-hidden="true"
          />

          <!-- Load more indicator -->
          <div v-if="isFetchingMore" class="flex justify-center py-4">
            <div class="flex items-center gap-2 text-sm text-gray-500 font-medium">
              <span class="w-4 h-4 rounded-full border-2 border-green-500 border-t-transparent animate-spin" aria-hidden="true" />
              Memuat lebih banyak...
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         MOBILE FILTER DRAWER
         Slide dari bawah — feel like native app
    ══════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <!-- Backdrop -->
      <Transition name="fade">
        <div
          v-if="isFilterOpen"
          class="fixed inset-0 bg-black/50 z-[180] lg:hidden"
          aria-hidden="true"
          @click="isFilterOpen = false"
        />
      </Transition>

      <!-- Drawer panel -->
      <Transition name="slide-up-drawer">
        <div
          v-if="isFilterOpen"
          class="fixed inset-x-0 bottom-0 z-[185] lg:hidden bg-white rounded-t-[1.5rem] flex flex-col max-h-[88vh] shadow-2xl"
          role="dialog"
          aria-modal="true"
          aria-label="Filter produk"
        >
          <!-- Handle bar -->
          <div class="flex justify-center pt-3 pb-1 flex-shrink-0">
            <div class="w-10 h-1 rounded-full bg-gray-200" aria-hidden="true" />
          </div>

          <!-- Header drawer -->
          <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100 flex-shrink-0">
            <h2 class="text-base font-black text-gray-900">Filter Produk</h2>
            <div class="flex items-center gap-3">
              <button
                class="text-xs font-bold text-green-600 hover:text-green-700 transition-colors"
                @click="resetAllFilters"
              >
                Reset
              </button>
              <button
                class="p-1.5 rounded-full hover:bg-gray-100 transition-colors"
                aria-label="Tutup filter"
                @click="isFilterOpen = false"
              >
                <UIcon name="i-heroicons-x-mark" class="w-5 h-5 text-gray-600" aria-hidden="true" />
              </button>
            </div>
          </div>

          <!-- Filter content — scrollable -->
          <div class="flex-1 overflow-y-auto overscroll-contain px-5 py-4">
            <CategoryFilter
              v-model:search="searchQuery"
              v-model:selected="selectedCategories"
              v-model:price="priceRange"
              :dynamic-suggests="popularSearchesDynamic"
            />
          </div>

          <!-- Apply CTA -->
          <div class="px-5 py-4 border-t border-gray-100 flex-shrink-0 safe-area-bottom">
            <button
              class="w-full bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm hover:bg-green-600 text-white font-black text-sm py-3.5 rounded-2xl transition-colors shadow-lg shadow-green-200"
              @click="isFilterOpen = false"
            >
              Tampilkan {{ totalProducts }} Produk
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>

  </main>
</template>

<style scoped>

.product-item {
  display: flex;
  flex-direction: column;
}

/* ── Backdrop fade ────────────────────────────────────────────────── */
.fade-enter-active { transition: opacity 0.2s ease; }
.fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Drawer slide dari bawah ──────────────────────────────────────── */
.slide-up-drawer-enter-active { transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.slide-up-drawer-leave-active { transition: transform 0.22s cubic-bezier(0.32, 0.72, 0, 1); }
.slide-up-drawer-enter-from  { transform: translateY(100%); }
.slide-up-drawer-leave-to    { transform: translateY(100%); }

/* ── iOS safe area ───────────────────────────────────────────────── */
.safe-area-bottom { padding-bottom: env(safe-area-inset-bottom, 12px); }


</style>