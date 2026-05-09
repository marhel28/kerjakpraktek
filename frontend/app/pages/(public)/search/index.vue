<template>
  <main class="bg-[#F4F5F7] min-h-screen pb-16 font-sans pt-6 selection:bg-green-100 selection:text-green-900">
    <div class="max-w-[1400px] mx-auto px-4 lg:px-6">
      <BannerSection
      :identifier="bannerIdentifier"
      :mode="bannerMode"
      :autoplay-delay="4500"
      :show-title="false"
      :variant="bannerVariant"
    />

      
      <div class="mb-6 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
        <div class="flex items-center gap-2 text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider">
          <NuxtLink to="/" class="hover:text-green-600 transition-colors">Beranda</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span class="text-green-600">Pencarian Global</span>
        </div>
        
        <h1 class="text-2xl lg:text-3xl font-black text-gray-900 tracking-tight">
          <span v-if="searchQuery">
            Hasil: "<span class="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-[#32cd32]">{{ searchQuery }}</span>"
          </span>
          <span v-else-if="selectedCategories.length > 0">Menampilkan Filter Kategori</span>
          <span v-else>Semua Katalog Produk</span>
        </h1>
        <p class="text-gray-500 mt-2 font-medium text-sm">Menemukan <span class="font-bold text-gray-800">{{ totalResults }}</span> produk relevan</p>
      </div>

      <div v-if="suggestion" class="mb-6 bg-gradient-to-r from-amber-50 to-yellow-50 border border-yellow-200 p-4 rounded-xl flex items-center gap-3 shadow-sm">
        <div class="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
          <UIcon name="i-heroicons-light-bulb" class="w-5 h-5 text-yellow-600" />
        </div>
        <p class="text-yellow-800 text-sm font-medium">
          Pencarian Anda mungkin kurang tepat. Coba: 
          <button @click="applySuggestion(suggestion)" class="font-black text-amber-600 hover:text-amber-700 hover:underline text-base ml-1 transition-colors">
            {{ suggestion }}
          </button>?
        </p>
      </div>

      <div class="flex flex-col lg:flex-row gap-6 lg:gap-8 items-start">
        
        <aside class="w-full lg:w-[280px] shrink-0">
          <CategoryFilter
            v-model:search="searchQuery"
            v-model:selected="selectedCategories"
            v-model:price="priceRange"
            :dynamicSuggests="popularTerms"
          />
        </aside>

        <div class="flex-1 min-w-0 w-full">
          
          <div class="bg-white p-3 rounded-2xl border border-gray-200 shadow-sm mb-6 flex flex-wrap items-center justify-between gap-4">
            <div class="hidden md:flex items-center gap-2 px-3 border-l-4 border-green-600">
              <h2 class="text-sm font-black text-gray-900 uppercase tracking-widest">Urutkan</h2>
            </div>
            
            <div class="flex gap-2 w-full md:w-auto overflow-x-auto hide-scrollbar">
              <button @click="setSort('newest')" :class="sortQuery === 'newest' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-transparent text-gray-500 border-transparent hover:bg-gray-50 hover:text-gray-800'" class="px-5 py-2 rounded-xl text-sm font-bold border transition-all whitespace-nowrap">
                Terbaru
              </button>
              <button @click="setSort('popular_sort')" :class="sortQuery === 'popular_sort' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-transparent text-gray-500 border-transparent hover:bg-gray-50 hover:text-gray-800'" class="px-5 py-2 rounded-xl text-sm font-bold border transition-all whitespace-nowrap">
                Paling Laris
              </button>
              <button @click="setSort('price_asc')" :class="sortQuery === 'price_asc' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-transparent text-gray-500 border-transparent hover:bg-gray-50 hover:text-gray-800'" class="px-5 py-2 rounded-xl text-sm font-bold border transition-all whitespace-nowrap">
                Termurah
              </button>
              <button @click="setSort('price_desc')" :class="sortQuery === 'price_desc' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-transparent text-gray-500 border-transparent hover:bg-gray-50 hover:text-gray-800'" class="px-5 py-2 rounded-xl text-sm font-bold border transition-all whitespace-nowrap">
                Termahal
              </button>
            </div>
          </div>

          <div v-if="pending" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-5">
            <div v-for="i in 8" :key="i" class="bg-white rounded-2xl border border-gray-100 p-4 flex flex-col h-[380px] shadow-sm">
              <USkeleton class="w-full aspect-square rounded-xl mb-4 bg-gray-100" />
              <USkeleton class="h-4 w-1/4 mb-3 bg-gray-100" />
              <USkeleton class="h-5 w-full mb-1 bg-gray-100" />
              <USkeleton class="h-5 w-3/4 mb-4 bg-gray-100" />
              <div class="mt-auto">
                <USkeleton class="h-6 w-1/2 bg-gray-100" />
              </div>
            </div>
          </div>

          <div v-else-if="products.length === 0" class="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border-2 border-dashed border-gray-200 shadow-sm text-center px-4">
            <div class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mb-6">
              <UIcon name="i-heroicons-archive-box-x-mark" class="w-10 h-10 text-gray-300" />
            </div>
            <h2 class="text-2xl font-black text-gray-900 mb-2 tracking-tight">Produk Tidak Ditemukan</h2>
            <p class="text-gray-500 text-sm font-medium max-w-md">Silakan coba kata kunci lain, sesuaikan rentang harga, atau hapus filter kategori.</p>
            <button @click="resetFilters" class="mt-8 bg-black hover:bg-gray-800 text-white font-bold py-3.5 px-8 rounded-xl transition-colors shadow-md text-sm uppercase tracking-widest">
              Reset Semua Filter
            </button>
          </div>

          <div v-else class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-5 items-stretch">
            <div v-for="item in products" :key="item.uuid" class="h-full">
              <CardPerItems v-bind="item" />
            </div>
          </div>

          <div v-if="!pending && products.length > 0" class="mt-12 text-center pb-8">
            <span class="inline-block px-5 py-2.5 bg-white border border-gray-200 text-gray-400 text-xs font-bold rounded-full shadow-sm uppercase tracking-widest">
              ~ Akhir dari Hasil Pencarian ~
            </span>
          </div>

        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '#imports'

import CategoryFilter from '~/components/category/CategoryFilter.vue'
import CardPerItems from '~/components/CardPerItems.vue'

const route = useRoute()
const router = useRouter()

// ==========================================
// 🔗 STATE SINKRONISASI (UI <-> URL)
// ==========================================
const searchQuery = ref((route.query.q as string) || '')
const bannerIdentifier = "search"
const bannerMode = computed(() =>
   'auto'
)
const bannerVariant=computed(()=>'market')
// Logika Parsing URL Kategori yang Aman
const parseCategories = (catQuery: any): string[] => {
  if (!catQuery) return []
  if (Array.isArray(catQuery)) return catQuery as string[]
  return [catQuery as string]
}

const selectedCategories = ref<string[]>(parseCategories(route.query.category))

const priceRange = ref<number[]>([
  route.query.min_price ? Number(route.query.min_price) : 0,
  route.query.max_price ? Number(route.query.max_price) : 10000000
])

const sortQuery = ref((route.query.sort as string) || 'newest')

// ==========================================
// 🔄 WATCHER: UPDATE URL SAAT STATE BERUBAH
// ==========================================
// Gunakan debounce kecil manual agar tidak nge-spam history browser
let urlTimeout: NodeJS.Timeout
watch([searchQuery, selectedCategories, priceRange, sortQuery], () => {
  clearTimeout(urlTimeout)
  urlTimeout = setTimeout(() => {
    router.replace({
      query: {
        ...route.query,
        q: searchQuery.value || undefined,
        category: selectedCategories.value.length > 0 ? selectedCategories.value : undefined,
        min_price: priceRange.value[0] > 0 ? priceRange.value[0] : undefined,
        max_price: priceRange.value[1] < 10000000 ? priceRange.value[1] : undefined,
        sort: sortQuery.value !== 'newest' ? sortQuery.value : undefined
      }
    })
  }, 300) // Delay 300ms
}, { deep: true })


// ==========================================
// 🚀 FETCH DATA API (ELASTICSEARCH VIA NITRO)
// ==========================================
const { data: apiResponse, pending } = await useFetch('/api/search', {
  query: computed(() => ({
    q: searchQuery.value || undefined,
    cat: selectedCategories.value.length > 0 ? selectedCategories.value : undefined, // Kirim Array
    sort: sortQuery.value,
    min_price: priceRange.value[0],
    max_price: priceRange.value[1],
    size: 24 
  })),
  watch: [searchQuery, selectedCategories, priceRange, sortQuery] 
})

// ==========================================
// 🧮 COMPUTED DATA (MAPPING KE UI)
// ==========================================
const products = computed(() => {
  if (!apiResponse.value?.items) return []
  return apiResponse.value.items
})

const totalResults = computed(() => apiResponse.value?.total || 0)
const suggestion = computed(() => apiResponse.value?.suggestion || null)
const popularTerms = computed(() => apiResponse.value?.facets?.popular_terms || [])

// ==========================================
// ⚡ ACTIONS
// ==========================================
const applySuggestion = (sug: string) => {
  searchQuery.value = sug
}

const setSort = (sortType: string) => {
  sortQuery.value = sortType
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategories.value = []
  priceRange.value = [0, 10000000]
  sortQuery.value = 'newest'
}

// ==========================================
// 🌐 SEO META
// ==========================================
useHead({
  title: computed(() => searchQuery.value ? `Hasil Pencarian: ${searchQuery.value} | Enterprise CCTV` : 'Katalog Pencarian Global | Enterprise CCTV'),
  meta: [
    { name: 'robots', content: 'noindex, follow' } // Halaman pencarian disarankan noindex agar google tidak mengindex ribuan kombinasi URL filter
  ]
})
</script>

<style scoped>
/* Sembunyikan scrollbar pada navigasi sort */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>