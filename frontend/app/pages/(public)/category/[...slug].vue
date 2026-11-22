<script setup lang="ts">
import { ref, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AmazonCategoryBanner from '~/components/category/AmazonCategoryBanner.vue'
import AmazonCategoryBubbles from '~/components/category/AmazonCategoryBubbles.vue'
import AmazonFacetSidebar from '~/components/category/AmazonFacetSidebar.vue'
import AmazonActiveFilters, { type FilterChip } from '~/components/category/AmazonActiveFilters.vue'
import CategoryFilter from '~/components/category/CategoryFilter.vue'
import CardPerItem from '~/components/CardPerItems.vue'
import SkeletonProductCard from '~/components/SkeletonProductCard.vue'

const route = useRoute()
const router = useRouter()
const siteUrl = useRuntimeConfig().public.siteUrl ?? 'https://yourdomain.com'

// ─── Slug & URL Logic ─────────────────────────────────────────────
const rawSlug = route.params.slug as string | string[] | undefined
const slugArray = Array.isArray(rawSlug)
  ? rawSlug.filter(Boolean)
  : rawSlug ? [rawSlug] : []

const activeSlug = computed(() => {
  if (slugArray.length > 0 && slugArray[slugArray.length - 1]) {
    return slugArray[slugArray.length - 1]!.toLowerCase()
  }
  return 'semua-kategori'
})

const parentSlug = computed(() => {
  if (slugArray.length > 1 && slugArray[0]) {
    return slugArray[0]!.toLowerCase()
  }
  return null
})

const canonicalUrl = computed(() => `${siteUrl}/category/${slugArray.join('/')}`)

// ─── Product State ────────────────────────────────────────────────
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

// ─── Filter & Facet State ─────────────────────────────────────────
const filterState = ref({
  categories: [] as string[],
  subcategories: [] as string[],
  brands: [] as string[],
  priceRange: [0, 10000000] as [number, number],
  rating: 0,
  discount: [] as number[],
  inStockOnly: false,
  sortBy: (route.query.sort as string) || 'newest',
})

const searchQuery = ref('')
const isFilterOpen = ref(false)

const sortOptions = [
  { label: 'Terbaru', value: 'newest' },
  { label: 'Harga: Rendah ke Tinggi', value: 'price_asc' },
  { label: 'Harga: Tinggi ke Rendah', value: 'price_desc' },
  { label: 'Ulasan & Terlaris', value: 'popular_sort' },
]

// ─── Fetch Categories for Menus & Bubbles ─────────────────────────
const { data: rawCategories } = await useFetch('/api/category', {
  default: () => [],
})

const categoryMenu = computed(() => {
  const arr = Array.isArray(rawCategories.value) ? rawCategories.value : (rawCategories.value as any)?.data || []
  return arr.map((cat: any) => ({
    id: cat.slug,
    label: cat.name,
    icon: cat.icon_name || 'i-heroicons-folder',
    subs: (cat.subcategories || []).map((s: any) => ({ id: s.slug, label: s.name })),
  }))
})

// Subcategory Bubbles mapped for current active category
const bubbles = computed(() => {
  const currentCat = categoryMenu.value.find((c: any) => c.id === activeSlug.value || c.subs?.some((s: any) => s.id === activeSlug.value))
  if (!currentCat) {
    return categoryMenu.value.map((c: any) => ({
      slug: c.id,
      name: c.label,
      count: c.subs?.length,
    }))
  }
  const list = [
    { slug: currentCat.id, name: 'Semua ' + currentCat.label, dealLabel: 'DEAL' },
    ...(currentCat.subs || []).map((s: any) => ({
      slug: s.id,
      name: s.label,
    }))
  ]
  return list
})

// ─── Active Filter Chips ──────────────────────────────────────────
const activeFilterChips = computed<FilterChip[]>(() => {
  const chips: FilterChip[] = []
  
  filterState.value.categories.forEach(c => {
    if (c !== activeSlug.value) {
      chips.push({ key: `cat-${c}`, label: 'Kategori', displayValue: c })
    }
  })
  
  filterState.value.subcategories.forEach(s => {
    chips.push({ key: `sub-${s}`, label: 'Subkategori', displayValue: s })
  })

  filterState.value.brands.forEach(b => {
    chips.push({ key: `brand-${b}`, label: 'Merek', displayValue: b })
  })

  if (filterState.value.priceRange[0] > 0 || filterState.value.priceRange[1] < 10000000) {
    chips.push({
      key: 'price',
      label: 'Harga',
      displayValue: `Rp ${filterState.value.priceRange[0].toLocaleString('id-ID')} - Rp ${filterState.value.priceRange[1].toLocaleString('id-ID')}`
    })
  }

  if (filterState.value.rating > 0) {
    chips.push({
      key: 'rating',
      label: 'Rating',
      displayValue: `${filterState.value.rating}★ & ke atas`
    })
  }

  filterState.value.discount.forEach(d => {
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
    filterState.value.categories = filterState.value.categories.filter(x => x !== val)
  } else if (chip.key.startsWith('sub-')) {
    const val = chip.key.replace('sub-', '')
    filterState.value.subcategories = filterState.value.subcategories.filter(x => x !== val)
  } else if (chip.key.startsWith('brand-')) {
    const val = chip.key.replace('brand-', '')
    filterState.value.brands = filterState.value.brands.filter(x => x !== val)
  } else if (chip.key === 'price') {
    filterState.value.priceRange = [0, 10000000]
  } else if (chip.key === 'rating') {
    filterState.value.rating = 0
  } else if (chip.key.startsWith('disc-')) {
    const val = Number(chip.key.replace('disc-', ''))
    filterState.value.discount = filterState.value.discount.filter(x => x !== val)
  } else if (chip.key === 'stock') {
    filterState.value.inStockOnly = false
  }
  fetchProducts(false)
}

const clearAllFilters = () => {
  filterState.value.categories = activeSlug.value !== 'semua-kategori' ? [activeSlug.value] : []
  filterState.value.subcategories = []
  filterState.value.brands = []
  filterState.value.priceRange = [0, 10000000]
  filterState.value.rating = 0
  filterState.value.discount = []
  filterState.value.inStockOnly = false
  searchQuery.value = ''
  fetchProducts(false)
}

// ─── API Query ────────────────────────────────────────────────────
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

  const activeCats = [...filterState.value.categories, ...filterState.value.subcategories]
  if (activeSlug.value !== 'semua-kategori' && !activeCats.includes(activeSlug.value)) {
    activeCats.push(activeSlug.value)
  }

  try {
    const res = await $fetch<any>('/api/search', {
      query: {
        q: searchQuery.value || undefined,
        cat: activeCats.length > 0 ? activeCats : undefined,
        brand: filterState.value.brands.length > 0 ? filterState.value.brands[0] : undefined,
        min_price: filterState.value.priceRange[0],
        max_price: filterState.value.priceRange[1],
        sort: filterState.value.sortBy,
        page: page.value,
        size: 16,
      },
    })

    if (res.status === 'success') {
      const newItems = res.items || []
      if (!isLoadMore) products.value = newItems
      else products.value.push(...newItems)

      totalProducts.value = res.total || 0
      suggestion.value = res.suggestion || null
      hasMore.value = products.value.length < totalProducts.value
      if (res.facets?.popular_terms) popularSearchesDynamic.value = res.facets.popular_terms
    }
  } catch {
    /* silent */
  } finally {
    pending.value = false
    isFetchingMore.value = false
  }
}

// Watchers
watch(
  () => [filterState.value, searchQuery.value],
  () => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => fetchProducts(false), 350)
  },
  { deep: true }
)

const onBubbleSelect = (slug: string) => {
  router.push(`/category/${slug}`)
}

// ─── Title & SEO ──────────────────────────────────────────────────
const pageTitle = computed(() => {
  const f = activeSlug.value.replace(/-/g, ' ').toUpperCase()
  if (f === 'SEMUA KATEGORI') return 'Katalog Produk CCTV'
  if (f === 'POPULAR') return 'Produk Terpopuler & Terlaris'
  return `Jual ${f} Terbaik`
})

useSeoMeta({
  title: computed(() => `${pageTitle.value} | PasarCctv Official`),
  description: computed(() => `Beli ${pageTitle.value} garansi resmi distributor. Cek diskon & stok terlengkap sekarang.`),
  ogTitle: computed(() => `${pageTitle.value} | PasarCctv Official`),
})

const setupObserver = () => {
  if (!loadMoreTrigger.value) return
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0] && entries[0].isIntersecting && hasMore.value && !pending.value && !isFetchingMore.value) {
        page.value++
        fetchProducts(true)
      }
    },
    { rootMargin: '350px' }
  )
  if (loadMoreTrigger.value) {
    observer.observe(loadMoreTrigger.value)
  }
}

onMounted(() => {
  if (activeSlug.value !== 'semua-kategori') {
    filterState.value.categories = [activeSlug.value]
  }
  fetchProducts(false)
  nextTick(() => setTimeout(setupObserver, 600))
})

onBeforeUnmount(() => {
  observer?.disconnect()
  clearTimeout(debounceTimer)
})
</script>

<template>
  <main class="min-h-screen bg-[#EAEDED] font-sans text-[#0F1111] overflow-x-hidden pb-20">

    <!-- ── 1. Category Hero Banner (Amazon Department Style) ── -->
    <AmazonCategoryBanner
      :category-title="pageTitle"
      :parent-category="parentSlug"
      :active-slug="activeSlug"
    />

    <!-- ── 2. Amazon Subcategory Bubble Pills Rail ── -->
    <AmazonCategoryBubbles
      :items="bubbles"
      :active-slug="activeSlug"
      @select="onBubbleSelect"
    />

    <!-- ── 3. Breadcrumbs Bar ── -->
    <div class="bg-white border-b border-neutral-200">
      <div class="max-w-[1400px] mx-auto px-4 md:px-6 py-2.5 text-xs text-neutral-500">
        <nav aria-label="Breadcrumb" class="flex items-center gap-1.5">
          <NuxtLink to="/" class="hover:text-blue-700 hover:underline">Beranda</NuxtLink>
          <span class="text-neutral-400">›</span>
          <NuxtLink to="/category" class="hover:text-blue-700 hover:underline">Kategori</NuxtLink>
          <template v-if="parentSlug">
            <span class="text-neutral-400">›</span>
            <NuxtLink :to="`/category/${parentSlug}`" class="hover:text-blue-700 hover:underline capitalize">
              {{ parentSlug.replace(/-/g, ' ') }}
            </NuxtLink>
          </template>
          <span class="text-neutral-400">›</span>
          <span class="font-bold text-neutral-800">{{ pageTitle }}</span>
        </nav>
      </div>
    </div>

    <!-- ── 4. Main Body: Amazon 2-Column Catalog ── -->
    <div class="max-w-[1400px] mx-auto px-4 md:px-6 pt-4">
      <div class="flex flex-col lg:flex-row gap-5 items-start">

        <!-- Left Rail: Amazon Multi-Facet Filter Sidebar -->
        <AmazonFacetSidebar
          v-model="filterState"
          :category-menu="categoryMenu"
          :total-products="totalProducts"
          @apply="() => fetchProducts(false)"
        />

        <!-- Right Column: Results & Products -->
        <div class="flex-1 min-w-0 w-full flex flex-col gap-3">

          <!-- Results Header Toolbar -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white px-4 py-2.5 rounded-lg border border-neutral-200 shadow-sm">
            <div class="flex items-center gap-2">
              <span class="text-xs md:text-sm text-neutral-700">
                <span v-if="pending" class="font-medium text-neutral-500">Memuat katalog...</span>
                <span v-else>
                  Menampilkan <strong class="text-neutral-900">{{ products.length }}</strong> dari <strong class="text-neutral-900">{{ totalProducts }}</strong> hasil
                </span>
              </span>
            </div>

            <div class="flex items-center gap-2 self-end sm:self-auto">
              <!-- Mobile Filter Trigger -->
              <button
                type="button"
                class="lg:hidden inline-flex items-center gap-1.5 px-3 py-1.5 bg-neutral-100 border border-neutral-300 rounded text-xs font-semibold text-neutral-800 hover:bg-neutral-200"
                @click="isFilterOpen = true"
              >
                <UIcon name="i-heroicons-adjustments-horizontal" class="w-4 h-4" />
                Filter
                <span v-if="activeFilterChips.length" class="w-4 h-4 bg-amber-500 text-neutral-950 rounded-full text-[10px] font-bold flex items-center justify-center">
                  {{ activeFilterChips.length }}
                </span>
              </button>

              <!-- Sort Dropdown -->
              <div class="flex items-center gap-1.5 text-xs text-neutral-600">
                <span class="hidden sm:inline">Urutkan:</span>
                <select
                  v-model="filterState.sortBy"
                  class="bg-neutral-50 border border-neutral-300 rounded px-2.5 py-1 text-xs font-semibold text-neutral-800 outline-none focus:border-amber-500 cursor-pointer"
                  @change="() => fetchProducts(false)"
                >
                  <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- Active Filter Tags Bar -->
          <AmazonActiveFilters
            :chips="activeFilterChips"
            :total-products="totalProducts"
            @remove="removeFilterChip"
            @clear="clearAllFilters"
          />

          <!-- Product Grid -->
          <div
            v-if="pending || products.length > 0"
            class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-3.5"
            role="list"
          >
            <template v-if="pending">
              <SkeletonProductCard :count="8" />
            </template>
            <template v-else>
              <div
                v-for="item in products"
                :key="item.uuid"
                class="h-full flex flex-col"
                role="listitem"
              >
                <CardPerItem v-bind="item" class="h-full" />
              </div>
            </template>
            <template v-if="isFetchingMore">
              <SkeletonProductCard :count="4" />
            </template>
          </div>

          <!-- Empty State -->
          <div v-if="!pending && products.length === 0" class="bg-white rounded-lg border border-neutral-200 p-8 text-center flex flex-col items-center gap-3 mt-2">
            <UIcon name="i-heroicons-magnifying-glass" class="w-12 h-12 text-neutral-300" />
            <h2 class="text-base font-bold text-neutral-900">Tidak ada produk yang cocok dengan filter Anda</h2>
            <p class="text-xs text-neutral-500 max-w-sm">
              Coba kurangi filter yang dipilih atau reset filter untuk melihat semua stok produk yang tersedia.
            </p>
            <button
              type="button"
              class="mt-2 px-4 py-2 bg-amber-400 hover:bg-amber-500 text-neutral-950 font-bold text-xs rounded border border-amber-500 transition-colors"
              @click="clearAllFilters"
            >
              Reset Semua Filter
            </button>
          </div>

          <!-- Infinite Scroll Trigger -->
          <div
            v-show="!pending && hasMore && products.length > 0"
            ref="loadMoreTrigger"
            class="h-10 w-full"
            aria-hidden="true"
          />

          <!-- Loading More -->
          <div v-if="isFetchingMore" class="flex justify-center py-4">
            <span class="text-xs text-neutral-500 font-medium">Memuat lebih banyak produk...</span>
          </div>

        </div>
      </div>
    </div>

    <!-- ── Mobile Filter Drawer ── -->
    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="isFilterOpen"
          class="fixed inset-0 bg-black/60 z-[180] lg:hidden"
          @click="isFilterOpen = false"
        />
      </Transition>
      <Transition name="slide-up">
        <div
          v-if="isFilterOpen"
          class="fixed inset-x-0 bottom-0 z-[185] lg:hidden bg-white rounded-t-xl max-h-[85vh] flex flex-col shadow-xl"
        >
          <div class="flex items-center justify-between px-4 py-3 border-b border-neutral-200">
            <span class="font-bold text-sm text-neutral-900">Filter Katalog</span>
            <button type="button" class="p-1 text-neutral-500" @click="isFilterOpen = false">
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-4">
            <CategoryFilter
              v-model:search="searchQuery"
              v-model:selected="filterState.categories"
              v-model:price="filterState.priceRange"
              :dynamic-suggests="popularSearchesDynamic"
            />
          </div>
          <div class="p-3 border-t border-neutral-200 bg-neutral-50">
            <button
              type="button"
              class="w-full py-2.5 bg-amber-400 hover:bg-amber-500 text-neutral-950 font-bold text-xs rounded border border-amber-500"
              @click="isFilterOpen = false"
            >
              Terapkan Filter ({{ totalProducts }} Produk)
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>

  </main>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.25s ease-out; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); }
</style>