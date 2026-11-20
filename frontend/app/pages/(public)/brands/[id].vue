<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const brandSlug = (route.params.id as string || '').toLowerCase().trim()
const siteUrl = useRuntimeConfig().public.siteUrl ?? 'https://yourdomain.com'

// ========================================================================
// 1. BRAND METADATA & AMAZON STORE CATEGORIES
// ========================================================================
interface BrandMetaItem {
  tagline: string
  badge: string
  subcategories?: string[]
}

const BRAND_METADATA: Record<string, BrandMetaItem> = {
  dahua: {
    tagline: 'Spesialis Kamera Pengawas IP, XVR, dan Teknologi AI WizSense',
    badge: 'Tier-1 Partner',
    subcategories: ['Semua', 'IP Camera', 'HDCVI Camera', 'NVR & XVR', 'PTZ & Speed Dome', 'Aksesoris'],
  },
  hikvision: {
    tagline: 'Sistem Keamanan CCTV ColorVu dan NVR 4K No. 1 Global',
    badge: 'Authorized Distributor',
    subcategories: ['Semua', 'ColorVu', 'IP Network Camera', 'DVR & NVR', 'Turbo HD', 'Aksesoris'],
  },
  ezviz: {
    tagline: 'Smart Home Camera dan Perangkat Keamanan WiFi Praktis',
    badge: 'Official Store',
    subcategories: ['Semua', 'Indoor WiFi', 'Outdoor WiFi', 'Battery Camera', 'Smart Lock'],
  },
  imou: {
    tagline: 'Kamera Pengawas Nirkabel dengan AI Human dan Pet Detection',
    badge: 'Official Partner',
    subcategories: ['Semua', 'Ranger Series', 'Bullet Camera', 'Cruiser PTZ', 'Aksesoris'],
  },
  tapo: {
    tagline: 'Smart Security dan IoT Terkoneksi dari TP-Link',
    badge: 'Official Store',
    subcategories: ['Semua', 'Indoor Pan/Tilt', 'Outdoor Camera', 'Battery Camera', 'Smart Hub'],
  },
  tiandy: {
    tagline: 'Pionir Kamera Pengawas Super Starlight Full Color Malam Hari',
    badge: 'Official Partner',
    subcategories: ['Semua', 'Color Maker', 'Starlight Series', 'NVR', 'Aksesoris'],
  },
  glenz: {
    tagline: 'Power Supply Jaring, Video Balun, dan Aksesori Instalasi CCTV',
    badge: 'Distributor Resmi',
    subcategories: ['Semua', 'Power Supply', 'Video Balun', 'Konektor BNC', 'Kabel'],
  },
  'tp-link': {
    tagline: 'Switch PoE Gigabit, WiFi 6 Router, dan Access Point Komersial',
    badge: 'Networking Partner',
    subcategories: ['Semua', 'PoE Switch', 'Omada Access Point', 'Router', 'Media Converter'],
  },
  seagate: {
    tagline: 'Harddisk Surveillance SkyHawk Tahan Rekam 24/7 Nonstop',
    badge: 'Storage Partner',
    subcategories: ['Semua', 'SkyHawk 1TB - 2TB', 'SkyHawk 4TB - 6TB', 'SkyHawk AI 8TB+'],
  },
  wd: {
    tagline: 'Harddrive CCTV WD Purple dengan Teknologi AllFrame 4K',
    badge: 'Storage Partner',
    subcategories: ['Semua', 'WD Purple 1TB - 2TB', 'WD Purple 4TB - 6TB', 'WD Purple Pro 8TB+'],
  },
  belden: {
    tagline: 'Kabel UTP Cat6 dan Coaxial Tembaga Murni Kualitas USA',
    badge: 'Cabling Partner',
    subcategories: ['Semua', 'UTP Cat6', 'Coaxial RG59', 'Coaxial RG6', 'Konektor'],
  },
}

// ========================================================================
// 2. STATE MANAGEMENT & FILTERS
// ========================================================================
const initialSearch = (route.query.q as string) || ''
const initialSort = (route.query.sort as string) || 'newest'

const localSearchInput = ref(initialSearch) 
const activeSearchQuery = ref(initialSearch) 
const selectedSort = ref(initialSort)
const selectedCategory = ref('Semua')
const filterReadyStockOnly = ref(false)
const currentPage = ref(1)

const handleSearch = () => {
  activeSearchQuery.value = localSearchInput.value.trim()
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

const selectCategory = (cat: string) => {
  selectedCategory.value = cat
  currentPage.value = 1
}

const sortOptions = [
  { label: 'Unggulan & Terbaru', value: 'newest' },
  { label: 'Harga: Rendah ke Tinggi', value: 'price_asc' },
  { label: 'Harga: Tinggi ke Rendah', value: 'price_desc' },
  { label: 'Ulasan & Terlaris', value: 'popular' },
]

// ========================================================================
// 3. SEO & BRAND IDENTITY (Blocking API)
// ========================================================================
const { data: brandProfile } = await useFetch<any>('/api/brands', {
  key: `brand-profile:${brandSlug}`,
  server: true, 
  transform: (data) => {
    if (!data) return null
    return data.find((b: any) => (b.brand_slug || '').toLowerCase() === brandSlug) || null
  },
})

const displayBrandName = computed(() => {
  if (brandProfile.value?.brand_name) return brandProfile.value.brand_name
  return brandSlug.split('-').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
})

const brandMeta = computed(() => {
  return BRAND_METADATA[brandSlug] || {
    tagline: `Solusi perangkat keamanan resmi bergaransi untuk ${displayBrandName.value}`,
    badge: 'Official Partner',
    subcategories: ['Semua', 'CCTV & Kamera', 'Perekam / DVR', 'Aksesoris'],
  }
})

const displayBrandLogo = computed(() => brandProfile.value?.brand_logo || '')

useSeoMeta({
  title: () => `${displayBrandName.value} Official Store: Katalog Resmi & Harga Terbaik | PasarCctv`,
  description: () => `Belanja produk resmi ${displayBrandName.value}. Garansi resmi prinsipal, pengiriman ke seluruh Indonesia.`,
  ogTitle: () => `${displayBrandName.value} Official Store | PasarCctv`,
  ogImage: displayBrandLogo,
  robots: 'index, follow',
})

useHead({
  link: [{ rel: 'canonical', href: `${siteUrl}/brands/${brandSlug}` }]
})

// ========================================================================
// 4. PRODUCT FETCHING (Lazy API)
// ========================================================================
interface SearchApiResponse {
  items: any[]
  total: number
  status?: string
}

const { data: productData, pending } = await useFetch<SearchApiResponse>('/api/search', {
  lazy: true,
  server: true,
  watch: [selectedSort, activeSearchQuery, selectedCategory, currentPage], 
  query: computed(() => {
    const payload: Record<string, any> = {
      brand: brandSlug,
      sort: selectedSort.value,
      size: 24,
      page: currentPage.value,
    }
    const queries: string[] = []
    if (activeSearchQuery.value) {
      queries.push(activeSearchQuery.value)
    }
    if (selectedCategory.value && selectedCategory.value !== 'Semua') {
      queries.push(selectedCategory.value)
    }
    if (queries.length > 0) {
      payload.q = queries.join(' ')
    }
    return payload
  }),
})

const allItems = computed(() => productData.value?.items || [])
const products = computed(() => {
  if (filterReadyStockOnly.value) {
    return allItems.value.filter((p: any) => p.stock_status !== 'out_of_stock')
  }
  return allItems.value
})

const totalProducts = computed(() => productData.value?.total || 0)
const startIndex = computed(() => totalProducts.value === 0 ? 0 : (currentPage.value - 1) * 24 + 1)
const endIndex = computed(() => Math.min(currentPage.value * 24, totalProducts.value))
</script>

<template>
  <main class="brand-page min-h-screen bg-slate-50/70 text-slate-800">
    <!-- 1. Amazon Storefront Brand Header -->
    <header class="bg-white border-b border-slate-200 pt-6 pb-0">
      <div class="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Breadcrumb -->
        <nav aria-label="Breadcrumb" class="flex items-center gap-2 text-xs text-slate-500 mb-4 font-medium">
          <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
          <UIcon name="i-tabler-chevron-right" class="w-3.5 h-3.5 text-slate-400" />
          <NuxtLink to="/brands" class="hover:text-[#03AC0E] transition-colors">Brand Resmi</NuxtLink>
          <UIcon name="i-tabler-chevron-right" class="w-3.5 h-3.5 text-slate-400" />
          <span class="text-slate-900 font-semibold">{{ displayBrandName }}</span>
        </nav>

        <!-- Identity Bar -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-5 pb-6 border-b border-slate-100">
          <div class="flex items-center gap-4">
            <div class="w-20 h-20 bg-white rounded-xl border border-slate-200 p-2 flex items-center justify-center shrink-0 shadow-xs">
              <NuxtImg
                v-if="displayBrandLogo"
                :src="displayBrandLogo"
                :alt="`Logo ${displayBrandName}`"
                width="120"
                height="60"
                format="webp"
                fetchpriority="high"
                loading="eager"
                class="max-w-full max-h-full object-contain"
              />
              <span v-else class="text-2xl font-bold text-slate-400">{{ displayBrandName.charAt(0) }}</span>
            </div>

            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                  {{ displayBrandName }}
                </h1>
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#E6F7E9] text-[#03AC0E] border border-[#C8E6CC] text-xs font-semibold">
                  <UIcon name="i-tabler-circle-check" class="w-3.5 h-3.5" />
                  <span>{{ brandMeta.badge }}</span>
                </span>
              </div>
              <p class="text-xs sm:text-sm text-slate-600 font-normal">
                {{ brandMeta.tagline }}
              </p>
            </div>
          </div>

          <!-- Quick Value Props -->
          <div class="flex items-center gap-2 self-start md:self-auto text-xs text-slate-600">
            <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200">
              <UIcon name="i-tabler-shield-check" class="w-4 h-4 text-[#03AC0E]" />
              <span>Garansi Resmi</span>
            </div>
            <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200">
              <UIcon name="i-tabler-truck" class="w-4 h-4 text-[#03AC0E]" />
              <span>Pengiriman Seluruh RI</span>
            </div>
          </div>
        </div>

        <!-- Amazon-Style Category Navigation Tabs -->
        <div class="flex items-center gap-1 overflow-x-auto pt-2 scrollbar-none">
          <button
            v-for="sub in brandMeta.subcategories"
            :key="sub"
            @click="selectCategory(sub)"
            :class="[
              'px-4 py-3 text-xs sm:text-sm font-semibold border-b-2 whitespace-nowrap transition cursor-pointer',
              selectedCategory === sub
                ? 'border-[#03AC0E] text-[#03AC0E] bg-[#E6F7E9]/30'
                : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
            ]"
          >
            {{ sub }}
          </button>
        </div>
      </div>
    </header>

    <!-- 2. Amazon-Style Search & Facets Control -->
    <div class="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-12">
      <div class="bg-white border border-slate-200 rounded-xl p-4 mb-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <!-- Search bar inside store -->
        <form @submit.prevent="handleSearch" class="relative flex-1 max-w-md">
          <UIcon name="i-tabler-search" class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            v-model="localSearchInput"
            type="text" 
            :placeholder="`Cari produk di toko ${displayBrandName}...`" 
            class="w-full bg-slate-50 border border-slate-200 rounded-lg pl-10 pr-9 py-2 text-xs sm:text-sm font-medium text-slate-800 placeholder-slate-400 focus:bg-white focus:border-[#03AC0E] focus:ring-2 focus:ring-[#03AC0E]/20 outline-none transition"
          >
          <button
            v-if="localSearchInput"
            type="button"
            @click="clearSearch"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            aria-label="Hapus pencarian"
          >
            <UIcon name="i-tabler-x" class="w-4 h-4" />
          </button>
        </form>

        <!-- Filter Pills & Sorting -->
        <div class="flex flex-wrap items-center justify-between md:justify-end gap-3">
          <!-- Ready Stock Toggle Pill -->
          <button
            type="button"
            @click="filterReadyStockOnly = !filterReadyStockOnly"
            :class="[
              'px-3 py-2 rounded-lg text-xs font-semibold border transition flex items-center gap-1.5 cursor-pointer',
              filterReadyStockOnly
                ? 'bg-[#E6F7E9] text-[#03AC0E] border-[#C8E6CC]'
                : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
            ]"
          >
            <UIcon :name="filterReadyStockOnly ? 'i-tabler-check' : 'i-tabler-circle'" class="w-3.5 h-3.5" />
            <span>Ready Stock Saja</span>
          </button>

          <!-- Sort Select -->
          <div class="flex items-center gap-2">
            <label for="sort-select" class="text-xs text-slate-500 font-medium">Urutkan:</label>
            <select
              id="sort-select"
              v-model="selectedSort"
              @change="handleSortChange"
              class="bg-slate-50 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 px-3 py-2 outline-none focus:border-[#03AC0E] focus:ring-2 focus:ring-[#03AC0E]/20 cursor-pointer"
            >
              <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Amazon-Style Result Status Header -->
      <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-200 text-xs sm:text-sm text-slate-600">
        <div>
          <span v-if="pending" class="font-medium">Memuat katalog...</span>
          <span v-else-if="totalProducts > 0">
            Menampilkan <strong>{{ startIndex }}-{{ endIndex }}</strong> dari <strong>{{ totalProducts }}</strong> hasil untuk <strong class="text-slate-900">{{ displayBrandName }}</strong>
            <span v-if="selectedCategory !== 'Semua'"> di kategori <em>"{{ selectedCategory }}"</em></span>
            <span v-if="activeSearchQuery"> dengan kata kunci <em>"{{ activeSearchQuery }}"</em></span>
          </span>
          <span v-else>
            0 hasil ditemukan untuk <strong class="text-slate-900">{{ displayBrandName }}</strong>
          </span>
        </div>
      </div>

      <!-- 3. Products Grid Loading State -->
      <div v-if="pending" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
        <CardPerItemSkeleton v-for="i in 10" :key="`skeleton-${i}`" />
      </div>

      <!-- 4. Products Grid Content -->
      <div v-else-if="products.length" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
        <div
          v-for="product in products"
          :key="product.uuid"
          class="flex flex-col h-full"
        >
          <CardPerItems
            :uuid="product.uuid"
            :slug="product.slug"
            :title="product.title"
            :brand="product.brand || displayBrandName"
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

      <!-- 5. Empty State -->
      <div v-else class="bg-white border border-slate-200 rounded-2xl p-12 text-center my-8 shadow-xs">
        <div class="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3 text-slate-400">
          <UIcon name="i-tabler-search" class="w-6 h-6" />
        </div>
        <h2 class="text-base font-semibold text-slate-900 mb-1">
          {{ activeSearchQuery || selectedCategory !== 'Semua' ? 'Hasil Tidak Ditemukan' : 'Produk Belum Tersedia' }}
        </h2>
        <p class="text-xs sm:text-sm text-slate-500 max-w-sm mx-auto mb-5 leading-relaxed">
          <template v-if="activeSearchQuery || selectedCategory !== 'Semua'">
            Tidak ada produk yang cocok dengan kriteria filter saat ini.
          </template>
          <template v-else>
            Saat ini belum ada produk aktif yang terdaftar untuk brand {{ displayBrandName }}.
          </template>
        </p>
        <button 
          v-if="activeSearchQuery || selectedCategory !== 'Semua' || filterReadyStockOnly" 
          @click="clearSearch(); selectedCategory = 'Semua'; filterReadyStockOnly = false" 
          class="px-4 py-2 rounded-xl bg-[#03AC0E] hover:bg-[#02930c] text-white text-xs font-medium transition shadow-xs cursor-pointer"
        >
          Reset Semua Filter
        </button>
        <NuxtLink v-else to="/brands" class="px-4 py-2 rounded-xl bg-[#03AC0E] hover:bg-[#02930c] text-white text-xs font-medium transition shadow-xs inline-block">
          Kembali ke Daftar Brand
        </NuxtLink>
      </div>

    </div>
  </main>
</template>

<style scoped>
.brand-page {
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.scrollbar-none::-webkit-scrollbar {
  display: none;
}
.scrollbar-none {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>