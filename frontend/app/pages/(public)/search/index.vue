<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '#imports'
import AmazonSearchBanner from '~/components/search/AmazonSearchBanner.vue'
import AmazonFacetSidebar from '~/components/category/AmazonFacetSidebar.vue'
import AmazonActiveFilters, { type FilterChip } from '~/components/category/AmazonActiveFilters.vue'
import CategoryFilter from '~/components/category/CategoryFilter.vue'
import CardPerItems from '~/components/CardPerItems.vue'
import SkeletonProductCard from '~/components/SkeletonProductCard.vue'

const route = useRoute()
const router = useRouter()

// ─── Query & URL State ─────────────────────────────────────────────
const searchQuery = ref((route.query.q as string) || '')
const isFilterOpen = ref(false)

const parseArrayParam = (val: any): string[] => {
  if (!val) return []
  if (Array.isArray(val)) return val as string[]
  return [val as string]
}

const filterState = ref({
  categories: parseArrayParam(route.query.category || route.query.cat),
  subcategories: parseArrayParam(route.query.subcat),
  brands: parseArrayParam(route.query.brand),
  priceRange: [
    route.query.min_price ? Number(route.query.min_price) : 0,
    route.query.max_price ? Number(route.query.max_price) : 10000000,
  ] as [number, number],
  rating: route.query.rating ? Number(route.query.rating) : 0,
  discount: parseArrayParam(route.query.disc).map(Number).filter(Boolean),
  inStockOnly: route.query.ready === 'true',
  sortBy: (route.query.sort as string) || 'newest',
})

const sortOptions = [
  { label: 'Terbaru', value: 'newest' },
  { label: 'Paling Laris', value: 'popular_sort' },
  { label: 'Harga: Rendah ke Tinggi', value: 'price_asc' },
  { label: 'Harga: Tinggi ke Rendah', value: 'price_desc' },
]

// ─── Categories & Menu for Facets ──────────────────────────────────
const { data: rawCategories } = await useFetch('/api/category', {
  default: () => [],
})

const categoryMenu = computed(() => {
  const arr = Array.isArray(rawCategories.value)
    ? rawCategories.value
    : (rawCategories.value as any)?.data || []
  return arr.map((cat: any) => ({
    id: cat.slug,
    label: cat.name,
    icon: cat.icon_name || 'i-heroicons-folder',
    subs: (cat.subcategories || []).map((s: any) => ({ id: s.slug, label: s.name })),
  }))
})

// ─── Active Filter Chips ───────────────────────────────────────────
const activeFilterChips = computed<FilterChip[]>(() => {
  const chips: FilterChip[] = []

  filterState.value.categories.forEach((c) => {
    chips.push({ key: `cat-${c}`, label: 'Kategori', displayValue: c })
  })

  filterState.value.subcategories.forEach((s) => {
    chips.push({ key: `sub-${s}`, label: 'Subkategori', displayValue: s })
  })

  filterState.value.brands.forEach((b) => {
    chips.push({ key: `brand-${b}`, label: 'Merek', displayValue: b })
  })

  if (filterState.value.priceRange[0] > 0 || filterState.value.priceRange[1] < 10000000) {
    chips.push({
      key: 'price',
      label: 'Harga',
      displayValue: `Rp ${filterState.value.priceRange[0].toLocaleString('id-ID')} - Rp ${filterState.value.priceRange[1].toLocaleString('id-ID')}`,
    })
  }

  if (filterState.value.rating > 0) {
    chips.push({
      key: 'rating',
      label: 'Rating',
      displayValue: `${filterState.value.rating}★ & ke atas`,
    })
  }

  filterState.value.discount.forEach((d) => {
    chips.push({ key: `disc-${d}`, label: 'Diskon', displayValue: `≥ ${d}%` })
  })

  if (filterState.value.inStockOnly) {
    chips.push({ key: 'stock', label: 'Stok', displayValue: 'Ready Stock' })
  }

  return chips
})

const removeFilterChip = (chip: FilterChip) => {
  if (chip.key.startsWith('cat-')) {
    const val = chip.key.replace('cat-', '')
    filterState.value.categories = filterState.value.categories.filter((x) => x !== val)
  } else if (chip.key.startsWith('sub-')) {
    const val = chip.key.replace('sub-', '')
    filterState.value.subcategories = filterState.value.subcategories.filter((x) => x !== val)
  } else if (chip.key.startsWith('brand-')) {
    const val = chip.key.replace('brand-', '')
    filterState.value.brands = filterState.value.brands.filter((x) => x !== val)
  } else if (chip.key === 'price') {
    filterState.value.priceRange = [0, 10000000]
  } else if (chip.key === 'rating') {
    filterState.value.rating = 0
  } else if (chip.key.startsWith('disc-')) {
    const val = Number(chip.key.replace('disc-', ''))
    filterState.value.discount = filterState.value.discount.filter((x) => x !== val)
  } else if (chip.key === 'stock') {
    filterState.value.inStockOnly = false
  }
  fetchProducts(false)
}

const clearAllFilters = () => {
  filterState.value.categories = []
  filterState.value.subcategories = []
  filterState.value.brands = []
  filterState.value.priceRange = [0, 10000000]
  filterState.value.rating = 0
  filterState.value.discount = []
  filterState.value.inStockOnly = false
  fetchProducts(false)
}

// ─── Products & Infinite Scroll ────────────────────────────────────
const products = ref<any[]>([])
const page = ref(1)
const hasMore = ref(true)
const isFetchingMore = ref(false)
const pending = ref(true)
const totalResults = ref(0)
const suggestion = ref<string | null>(null)
const popularTerms = ref<string[]>([])
const loadMoreTrigger = ref<HTMLElement | null>(null)

let urlTimeout: ReturnType<typeof setTimeout>
let debounceTimer: ReturnType<typeof setTimeout>
let observer: IntersectionObserver | null = null

// URL synchronization
watch(
  [searchQuery, filterState],
  () => {
    clearTimeout(urlTimeout)
    urlTimeout = setTimeout(() => {
      router.replace({
        query: {
          ...route.query,
          q: searchQuery.value || undefined,
          cat: filterState.value.categories.length > 0 ? filterState.value.categories : undefined,
          subcat: filterState.value.subcategories.length > 0 ? filterState.value.subcategories : undefined,
          brand: filterState.value.brands.length > 0 ? filterState.value.brands : undefined,
          min_price: filterState.value.priceRange[0] > 0 ? filterState.value.priceRange[0] : undefined,
          max_price: filterState.value.priceRange[1] < 10000000 ? filterState.value.priceRange[1] : undefined,
          rating: filterState.value.rating > 0 ? filterState.value.rating : undefined,
          disc: filterState.value.discount.length > 0 ? filterState.value.discount : undefined,
          ready: filterState.value.inStockOnly ? 'true' : undefined,
          sort: filterState.value.sortBy !== 'newest' ? filterState.value.sortBy : undefined,
        },
      })
    }, 300)
  },
  { deep: true }
)

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
        cat: filterState.value.categories.length > 0 ? filterState.value.categories : undefined,
        min_price: filterState.value.priceRange[0] ?? 0,
        max_price: filterState.value.priceRange[1] ?? 10000000,
        sort: filterState.value.sortBy,
        page: page.value,
        size: 24,
      },
    })

    if (res?.status === 'success') {
      const newItems = res.items || []
      if (!isLoadMore) products.value = newItems
      else products.value.push(...newItems)

      totalResults.value = res.total || 0
      suggestion.value = res.suggestion || null
      hasMore.value = products.value.length < totalResults.value
      if (res.facets?.popular_terms) popularTerms.value = res.facets.popular_terms
    }
  } catch {
    /* silent */
  } finally {
    pending.value = false
    isFetchingMore.value = false
  }
}

// Watch query change from external navigation (e.g. search navbar input)
watch(
  () => route.query.q,
  (newQ) => {
    if (newQ !== searchQuery.value) {
      searchQuery.value = (newQ as string) || ''
      fetchProducts(false)
    }
  }
)

watch(
  [filterState],
  () => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => fetchProducts(false), 400)
  },
  { deep: true }
)

const setupObserver = () => {
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

  observer.observe(loadMoreTrigger.value)
}

onMounted(() => {
  fetchProducts(false)
  nextTick(() => setTimeout(setupObserver, 800))
})

onBeforeUnmount(() => {
  observer?.disconnect()
  clearTimeout(debounceTimer)
  clearTimeout(urlTimeout)
})

const applySuggestion = (sug: string) => {
  searchQuery.value = sug
  fetchProducts(false)
}

useHead({
  title: computed(() =>
    searchQuery.value
      ? `Hasil Pencarian: "${searchQuery.value}" | Enterprise CCTV`
      : 'Katalog Pencarian Global | Enterprise CCTV'
  ),
  meta: [{ name: 'robots', content: 'noindex, follow' }],
})
</script>

<template>
  <main class="min-h-screen bg-[#EAEDED] font-sans text-[#0F1111] overflow-x-hidden pb-20">
    <!-- Amazon Search Header Banner -->
    <AmazonSearchBanner
      :query="searchQuery"
      :total-results="totalResults"
      :selected-category="filterState.categories[0] || null"
      :selected-brand="filterState.brands[0] || null"
    />

    <!-- Breadcrumbs Bar -->
    <nav aria-label="Breadcrumb" class="bg-white border-b border-neutral-200 text-xs py-2 px-4 md:px-6">
      <div class="max-w-[1400px] mx-auto flex items-center gap-1.5 text-neutral-500 overflow-x-auto no-scrollbar">
        <NuxtLink to="/" class="hover:text-[#007185] transition-colors whitespace-nowrap">Beranda</NuxtLink>
        <UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-neutral-400 shrink-0" />
        <span class="text-[#0F1111] font-semibold truncate">Pencarian</span>
        <template v-if="searchQuery">
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-neutral-400 shrink-0" />
          <span class="text-[#007185] font-semibold truncate">"{{ searchQuery }}"</span>
        </template>
      </div>
    </nav>

    <!-- Did You Mean / Suggestion Box -->
    <div v-if="suggestion" class="max-w-[1400px] mx-auto px-4 md:px-6 pt-4">
      <div class="bg-white border border-[#FF9900]/40 rounded-lg p-3.5 flex items-center gap-3 shadow-xs">
        <div class="w-8 h-8 rounded-full bg-[#FF9900]/10 flex items-center justify-center shrink-0">
          <UIcon name="i-heroicons-light-bulb" class="w-4 h-4 text-[#C45500]" />
        </div>
        <p class="text-xs md:text-sm text-[#0F1111]">
          Maksud Anda:
          <button
            type="button"
            class="font-bold text-[#007185] hover:text-[#C45500] hover:underline ml-1 cursor-pointer"
            @click="applySuggestion(suggestion)"
          >
            {{ suggestion }}
          </button>?
        </p>
      </div>
    </div>

    <!-- Main 2-Column Catalog -->
    <div class="max-w-[1400px] mx-auto px-4 md:px-6 pt-5">
      <div class="flex gap-6 items-start">
        <!-- Desktop Sticky Facet Sidebar -->
        <aside class="hidden lg:block w-[260px] shrink-0 sticky top-24">
          <AmazonFacetSidebar
            v-model="filterState"
            :category-menu="categoryMenu"
            :total-products="totalResults"
            @apply="fetchProducts(false)"
          />
        </aside>

        <!-- Right Column: Products & Controls -->
        <section class="flex-1 min-w-0 w-full" aria-label="Daftar Produk">
          <!-- Results Header Toolbar -->
          <div class="bg-white rounded-lg border border-neutral-200/90 shadow-xs px-3.5 py-2.5 mb-3 flex flex-wrap items-center justify-between gap-3 text-xs">
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="lg:hidden inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-neutral-300 font-semibold text-[#0F1111] bg-white hover:bg-neutral-50"
                @click="isFilterOpen = true"
              >
                <UIcon name="i-heroicons-adjustments-horizontal" class="w-4 h-4 text-[#007185]" />
                Filter
                <span v-if="activeFilterChips.length > 0" class="w-4 h-4 rounded-full bg-[#007185] text-white text-[10px] flex items-center justify-center">
                  {{ activeFilterChips.length }}
                </span>
              </button>

              <span class="text-neutral-600">
                Menampilkan <strong class="text-[#0F1111] font-semibold">{{ products.length }}</strong> dari <strong class="text-[#0F1111] font-semibold">{{ totalResults }}</strong> hasil
              </span>
            </div>

            <!-- Sort Select -->
            <div class="flex items-center gap-2 ml-auto">
              <label for="search-sort-select" class="text-neutral-500 hidden sm:inline">Urutkan:</label>
              <select
                id="search-sort-select"
                v-model="filterState.sortBy"
                class="bg-neutral-50 border border-neutral-300 text-[#0F1111] rounded-md px-2.5 py-1 text-xs font-medium focus:ring-1 focus:ring-[#FF9900] focus:border-[#FF9900] outline-hidden cursor-pointer"
                @change="fetchProducts(false)"
              >
                <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
          </div>

          <!-- Active Filters Bar -->
          <AmazonActiveFilters
            :chips="activeFilterChips"
            :total-products="totalResults"
            @remove="removeFilterChip"
            @clear="clearAllFilters"
          />

          <!-- Loading Skeleton Grid -->
          <div
            v-if="pending"
            class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4"
          >
            <SkeletonProductCard :count="12" />
          </div>

          <!-- Empty State -->
          <div
            v-else-if="products.length === 0"
            class="bg-white rounded-lg border border-neutral-200 p-8 md:p-12 text-center"
          >
            <div class="w-14 h-14 rounded-full bg-neutral-100 flex items-center justify-center mx-auto mb-3 text-neutral-400">
              <UIcon name="i-heroicons-magnifying-glass" class="w-7 h-7" />
            </div>
            <h2 class="text-base md:text-lg font-bold text-[#0F1111] mb-1">
              Tidak ada produk yang cocok dengan pencarian
            </h2>
            <p class="text-xs md:text-sm text-neutral-500 max-w-md mx-auto mb-5">
              Periksa ejaan kata kunci Anda atau coba hapus filter kategori dan rentang harga yang aktif.
            </p>
            <button
              type="button"
              class="inline-flex items-center gap-2 px-5 py-2 bg-[#FFD814] hover:bg-[#F7CA00] border border-[#FCD200] rounded-lg text-xs font-semibold text-[#0F1111] transition-colors shadow-xs"
              @click="clearAllFilters"
            >
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
              Reset Semua Filter
            </button>
          </div>

          <!-- Product Grid -->
          <div
            v-else
            class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4 items-stretch"
          >
            <div v-for="item in products" :key="item.uuid" class="h-full">
              <CardPerItems v-bind="item" />
            </div>

            <!-- Fetch more skeletons -->
            <template v-if="isFetchingMore">
              <SkeletonProductCard :count="4" />
            </template>
          </div>

          <!-- Infinite scroll sentinel -->
          <div
            v-show="!pending && hasMore && products.length > 0"
            ref="loadMoreTrigger"
            class="h-10 w-full"
            aria-hidden="true"
          />

          <!-- End of Results Indicator -->
          <div v-if="!pending && !hasMore && products.length > 0" class="mt-10 text-center pb-6">
            <span class="inline-block px-4 py-1.5 bg-white border border-neutral-200 text-neutral-400 text-[11px] font-medium rounded-full shadow-xs">
              Akhir hasil pencarian
            </span>
          </div>
        </section>
      </div>
    </div>

    <!-- Mobile Drawer for Filters -->
    <Teleport to="body">
      <div
        v-if="isFilterOpen"
        class="fixed inset-0 z-50 lg:hidden flex"
        role="dialog"
        aria-modal="true"
      >
        <div class="fixed inset-0 bg-black/50 transition-opacity" @click="isFilterOpen = false" />
        <div class="relative ml-auto w-full max-w-xs bg-white h-full shadow-xl flex flex-col z-10">
          <div class="flex items-center justify-between px-4 py-3 border-b border-neutral-200 bg-[#131A22] text-white">
            <h3 class="font-bold text-sm">Filter Pencarian</h3>
            <button
              type="button"
              class="w-8 h-8 rounded flex items-center justify-center text-neutral-300 hover:text-white"
              @click="isFilterOpen = false"
            >
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-4">
            <CategoryFilter
              v-model:search="searchQuery"
              v-model:selected="filterState.categories"
              v-model:price="filterState.priceRange"
              :dynamic-suggests="popularTerms"
            />
          </div>
          <div class="p-3 border-t border-neutral-200 bg-neutral-50 flex gap-2">
            <button
              type="button"
              class="flex-1 py-2 text-xs font-semibold rounded border border-neutral-300 text-neutral-700 bg-white"
              @click="clearAllFilters"
            >
              Reset
            </button>
            <button
              type="button"
              class="flex-1 py-2 text-xs font-bold rounded bg-[#FFD814] text-[#0F1111] hover:bg-[#F7CA00]"
              @click="isFilterOpen = false; fetchProducts(false)"
            >
              Terapkan
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </main>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>