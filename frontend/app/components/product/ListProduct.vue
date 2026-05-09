<script setup lang="ts">
import { ref, watch, computed } from 'vue'

// Import Banner & Card
import PageBanner from '~/components/PageBanner.vue'
import CardPerItem from '~/components/CardPerItems.vue'

interface Props {
  title?: string
  description?: string
  breadcrumbs?: { label: string; to?: string }[]
  image?: string
  initialSort?: 'terbaru' | 'terlama' | 'harga_rendah' | 'harga_tinggi'
  initialCategories?: string[]
  initialBrands?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Katalog Produk',
  initialSort: 'terbaru',
  initialCategories: () => [],
  initialBrands: () => []
})

// ==========================================
// STATE MANAJEMEN
// ==========================================
const searchQuery = ref('')
const selectedCategories = ref<string[]>([...props.initialCategories])
const selectedBrands = ref<string[]>([...props.initialBrands])
const priceMin = ref<number>(0)
const priceMax = ref<number>(10000000)
const sortBy = ref(props.initialSort)
const currentPage = ref(1)
const itemsPerPage = 8
const isMobileFilterOpen = ref(false)

// ==========================================
// MASTER DATA (Disesuaikan dengan Branding CCTV)
// ==========================================
const categories = [
  { id: 'paket_cctv', label: 'Paket CCTV', count: 120 },
  { id: 'kamera_cctv', label: 'Kamera CCTV', count: 450 },
  { id: 'nvr_dvr', label: 'NVR / DVR', count: 85 },
  { id: 'aksesoris', label: 'Aksesoris', count: 320 },
  { id: 'hard_disk', label: 'Hard Disk', count: 64 },
]

const brands = [
  { id: 'hilook', label: 'HiLook' },
  { id: 'hikvision', label: 'Hikvision' },
  { id: 'dahua', label: 'Dahua' },
  { id: 'ezviz', label: 'Ezviz' },
]

const sortOptions = [
  { value: 'terbaru', label: 'Produk Terbaru' },
  { value: 'harga_rendah', label: 'Harga Terendah' },
  { value: 'harga_tinggi', label: 'Harga Tertinggi' },
]

// Raw Data Produk (Ditambahkan originalPrice agar diskon muncul)
const rawProducts = [
  { 
    id: '1', 
    category: 'kamera_cctv', 
    brand: 'HILOOK', 
    title: 'HiLook IPC-B121H 2MP Bullet IP Camera Night Vision', 
    price: 350000, 
    originalPrice: 450000, 
    date: '2024-01-01', 
    image: 'https://images.unsplash.com/photo-1557862921-37829c790f19?q=80&w=500', 
    rating: 4.8, 
    reviewsCount: 124, 
    soldCount: 850 
  },
  { 
    id: '2', 
    category: 'paket_cctv', 
    brand: 'HIKVISION', 
    title: 'Paket CCTV 4 Kamera Full HD 2MP + DVR High Performance', 
    price: 2450000, 
    originalPrice: 3200000, 
    date: '2024-02-15', 
    image: 'https://images.unsplash.com/photo-1590059345003-8869f8863f6a?q=80&w=500', 
    rating: 4.9, 
    reviewsCount: 320, 
    soldCount: 85 
  },
  { 
    id: '3', 
    category: 'nvr_dvr', 
    brand: 'DAHUA', 
    title: 'Dahua XVR1B04-I 4 Channel DVR WizSense AI', 
    price: 550000, 
    originalPrice: 0, 
    date: '2023-12-20', 
    image: 'https://images.unsplash.com/photo-1528312635001-4be7c8801485?q=80&w=500', 
    rating: 4.7, 
    reviewsCount: 89, 
    soldCount: 340 
  },
  { 
    id: '4', 
    category: 'kamera_cctv', 
    brand: 'EZVIZ', 
    title: 'Ezviz C6N 2MP Smart Wi-Fi Pan & Tilt Security Camera', 
    price: 420000, 
    originalPrice: 500000, 
    date: '2024-03-10', 
    image: 'https://images.unsplash.com/photo-1584432810601-6c7f27d2362b?q=80&w=500', 
    rating: 4.9, 
    reviewsCount: 890, 
    soldCount: 3500 
  },
]

// ==========================================
// FILTERING LOGIC
// ==========================================
const filteredProducts = computed(() => {
  let result = [...rawProducts]
  if (searchQuery.value) {
    result = result.filter(p => p.title.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  if (selectedCategories.value.length > 0) {
    result = result.filter(p => selectedCategories.value.includes(p.category))
  }
  if (selectedBrands.value.length > 0) {
    result = result.filter(p => selectedBrands.value.includes(p.brand.toLowerCase()))
  }
  result = result.filter(p => p.price >= (priceMin.value || 0) && p.price <= (priceMax.value || Infinity))

  if (sortBy.value === 'harga_rendah') result.sort((a, b) => a.price - b.price)
  if (sortBy.value === 'harga_tinggi') result.sort((a, b) => b.price - a.price)
  if (sortBy.value === 'terbaru') result.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  
  return result
})

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredProducts.value.slice(start, start + itemsPerPage)
})

const totalResults = computed(() => filteredProducts.value.length)

watch([searchQuery, selectedCategories, selectedBrands, priceMin, priceMax, sortBy], () => {
  currentPage.value = 1
})

const resetFilters = () => {
  selectedCategories.value = []
  selectedBrands.value = []
  priceMin.value = 0
  priceMax.value = 10000000
  searchQuery.value = ''
}
</script>

<template>
  <div class="w-full bg-[#fbfbfd] pb-24 font-sans">
    <PageBanner
      :title="props.title"
      :description="props.description"
      :breadcrumbs="props.breadcrumbs"
      :image="props.image"
    />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex flex-col lg:flex-row gap-12">
      
      <aside class="hidden lg:flex w-64 shrink-0 flex-col gap-10 sticky top-24 h-fit">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-bold text-[#1d1d1f]">Filter</h2>
            <button @click="resetFilters" class="text-xs font-semibold text-blue-600 hover:underline">Reset</button>
          </div>
          <UInput
            v-model="searchQuery"
            icon="i-heroicons-magnifying-glass"
            placeholder="Cari produk..."
            variant="outline"
            :ui="{ rounded: 'rounded-xl' }"
          />
        </div>

        <div class="space-y-4">
          <h3 class="font-bold text-[15px] text-[#1d1d1f]">Merek CCTV</h3>
          <div class="flex flex-col gap-3">
            <UCheckbox
              v-for="brand in brands"
              :key="brand.id"
              v-model="selectedBrands"
              :value="brand.id"
              color="black"
              :label="brand.label"
            />
          </div>
        </div>

        <div class="space-y-4">
          <h3 class="font-bold text-[15px] text-[#1d1d1f]">Kategori</h3>
          <div class="flex flex-col gap-3">
            <UCheckbox
              v-for="cat in categories"
              :key="cat.id"
              v-model="selectedCategories"
              :value="cat.id"
              color="black"
              :label="cat.label"
            />
          </div>
        </div>

        <div class="space-y-5">
          <h3 class="font-bold text-[15px] text-[#1d1d1f]">Rentang Harga</h3>
          <URange v-model="priceMax" :min="0" :max="10000000" :step="100000" color="black" />
          <div class="grid grid-cols-2 gap-2">
            <UInput v-model.number="priceMin" type="number" size="xs" placeholder="Min" />
            <UInput v-model.number="priceMax" type="number" size="xs" placeholder="Max" />
          </div>
        </div>
      </aside>

      <section class="flex-1 min-w-0">
        <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4 bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
          <div class="flex items-center gap-3">
            <UButton
              class="lg:hidden rounded-xl font-bold"
              icon="i-heroicons-funnel"
              color="black"
              @click="isMobileFilterOpen = true"
            >
              Filter
            </UButton>
            <p class="text-sm font-medium text-gray-500">
              Menampilkan <span class="text-black font-bold">{{ totalResults }}</span> produk
            </p>
          </div>

          <div class="flex items-center gap-2">
            <USelectMenu
              v-model="sortBy"
              :options="sortOptions"
              option-attribute="label"
              value-attribute="value"
              class="w-full sm:w-48"
              :ui="{ rounded: 'rounded-xl' }"
            />
          </div>
        </div>

        <div v-if="paginatedProducts.length > 0" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
          <CardPerItem
            v-for="item in paginatedProducts"
            :key="item.id"
            :id="item.id"
            :image="item.image"
            :brand="item.brand"
            :title="item.title"
            :price="item.price"
            :original-price="item.originalPrice"
            :rating="item.rating"
            :reviews-count="item.reviewsCount"
            :sold-count="item.soldCount"
            :initial-categories="[item.category]" 
          />
        </div>

        <div v-else class="py-20 text-center">
          <UIcon name="i-heroicons-archive-box" class="w-12 h-12 mx-auto text-gray-300" />
          <h3 class="mt-2 text-sm font-semibold text-gray-900">Produk tidak ditemukan</h3>
          <UButton @click="resetFilters" variant="ghost" class="mt-4">Reset Filter</UButton>
        </div>

        <div v-if="totalResults > itemsPerPage" class="mt-16 flex justify-center border-t border-gray-100 pt-8">
          <UPagination
            v-model="currentPage"
            :page-count="itemsPerPage"
            :total="totalResults"
            color="black"
            :ui="{ rounded: 'rounded-full' }"
          />
        </div>
      </section>
    </main>

    <USlideover v-model="isMobileFilterOpen">
      <div class="p-6 flex flex-col h-full">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-xl font-bold">Filter Produk</h2>
          <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" @click="isMobileFilterOpen = false" />
        </div>
        
        <div class="flex-1 overflow-y-auto space-y-8">
           <UInput v-model="searchQuery" placeholder="Cari..." />
           
           <div>
             <h3 class="font-bold mb-4">Kategori</h3>
             <div class="space-y-3">
                <UCheckbox v-for="cat in categories" :key="cat.id" v-model="selectedCategories" :value="cat.id" :label="cat.label" />
             </div>
           </div>
        </div>

        <div class="pt-6 border-t">
          <UButton block color="black" size="lg" @click="isMobileFilterOpen = false">Terapkan Filter</UButton>
        </div>
      </div>
    </USlideover>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

.font-sans {
  font-family: 'Open Sans', sans-serif;
}
</style>