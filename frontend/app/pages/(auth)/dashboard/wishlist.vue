<script setup lang="ts">
import { ref, computed } from 'vue'
import { useWishlistStore } from '~/stores/wishlist'

// Pastikan komponen CardPerItems dan AccountSidebar auto-import
// import CardPerItems from '~/components/CardPerItems.vue'
// import AccountSidebar from '~/components/AccountSidebar.vue'

const wishlist = useWishlistStore()
const toast = useToast()

// ==========================================
// 🚀 FETCH DATA (KATEGORI)
// ==========================================
const { data: categories } = await useFetch<any>('/api/category', {
  lazy: true,
  transform: (res) => {
    return Array.isArray(res) ? res : res?.data || []
  }
})

// ==========================================
// 🎛️ STATE FILTER & SORTING
// ==========================================
const sortOptions = ['Terbaru Disimpan', 'Harga Tertinggi', 'Harga Terendah']
const selectedSort = ref(sortOptions[0])

const selectedCategories = ref<string[]>([])
const filterDiscount = ref(false)
const filterPromo = ref(false)
const promoCode = ref('')

// ==========================================
// 🧠 LOGIKA FILTER & SORTING (COMPUTED)
// ==========================================
const filteredAndSortedWishlist = computed(() => {
  let itemsCopy = [...wishlist.items]

  if (filterDiscount.value) {
    itemsCopy = itemsCopy.filter(item => {
      return item.stock?.discount_percentage && item.stock.discount_percentage > 0
    })
  }

  if (selectedCategories.value.length > 0) {
    itemsCopy = itemsCopy.filter(item => {
      const itemCategory = item.stock?.category_slug || ''
      return selectedCategories.value.includes(itemCategory)
    })
  }

  if (selectedSort.value === 'Harga Tertinggi') {
    return itemsCopy.sort((a, b) => (b.stock?.online_price || 0) - (a.stock?.online_price || 0))
  }
  else if (selectedSort.value === 'Harga Terendah') {
    return itemsCopy.sort((a, b) => (a.stock?.online_price || 0) - (b.stock?.online_price || 0))
  }
  else {
    return itemsCopy.reverse()
  }
})

// ==========================================
// 🖱️ ACTIONS
// ==========================================
const applyPromoCode = () => {
  if (!promoCode.value.trim()) return
  toast.add({
    title: 'Kode Promo',
    description: `Mencari kode promo: ${promoCode.value.toUpperCase()}...`,
    icon: 'i-heroicons-ticket',
    color: 'black'
  })
}

// Helper untuk Toggle Kategori (Pills UI)
const toggleCategory = (slug: string) => {
  const index = selectedCategories.value.indexOf(slug)
  if (index > -1) {
    selectedCategories.value.splice(index, 1)
  } else {
    selectedCategories.value.push(slug)
  }
}

const isCategorySelected = (slug: string) => selectedCategories.value.includes(slug)
const clearCategories = () => selectedCategories.value = []
</script>

<template>
  <main class="bg-[#F4F5F7] min-h-screen py-8">
    <div class="max-w-[1400px] mx-auto px-4 md:px-6 lg:px-8">

      <!-- Layout Dashboard Modern -->
      <div class="flex flex-col lg:flex-row gap-6 lg:gap-8 items-start">

        <!-- ── Sidebar Akun (Kiri) ───────────────────────────────── -->
        <AccountSidebar />

        <!-- ── Konten Utama Wishlist (Kanan) ─────────────────────── -->
        <div class="flex-1 min-w-0 w-full space-y-6">

          <!-- ── Horizontal Filter Bar ────────────────────────────── -->
          <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 sm:p-6">
            
            <!-- Header & Sort -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5 pb-5 border-b border-gray-100">
              <div>
                <h1 class="text-xl font-bold text-gray-900 tracking-tight">Wishlist Saya</h1>
                <p class="text-sm font-medium text-gray-500 mt-1">Kamu memiliki <span class="font-bold text-gray-900">{{ filteredAndSortedWishlist.length }}</span> barang impian</p>
              </div>
              <div class="flex items-center gap-3">
                <span class="hidden sm:inline-block text-sm text-gray-500 font-bold uppercase tracking-wider">Urutkan</span>
                <select v-model="selectedSort" class="border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-bold text-gray-700 outline-none focus:border-green-600 focus:ring-1 focus:ring-green-600 cursor-pointer bg-gray-50 hover:bg-white transition-all w-full sm:w-auto">
                  <option v-for="opt in sortOptions" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </div>
            </div>

            <!-- Kategori Pills -->
            <div class="mb-4">
              <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Filter Kategori</p>
              <div v-if="categories?.length" class="flex flex-wrap gap-2">
                <button 
                  @click="clearCategories"
                  class="px-4 py-1.5 rounded-full text-sm font-semibold border transition-all duration-200"
                  :class="selectedCategories.length === 0 ? 'bg-green-600 text-white border-green-600 shadow-sm' : 'bg-white text-gray-600 border-gray-200 hover:border-green-500 hover:text-green-600'"
                >
                  Semua
                </button>
                <button 
                  v-for="cat in categories" :key="cat.slug || cat.id"
                  @click="toggleCategory(cat.slug || cat.id)"
                  class="px-4 py-1.5 rounded-full text-sm font-semibold border transition-all duration-200"
                  :class="isCategorySelected(cat.slug || cat.id) ? 'bg-green-50 text-green-700 border-green-600 ring-1 ring-green-600' : 'bg-white text-gray-600 border-gray-200 hover:border-green-500 hover:text-green-600'"
                >
                  {{ cat.name || cat.title }}
                </button>
              </div>
              <div v-else class="text-sm font-medium text-gray-400 animate-pulse">Memuat kategori...</div>
            </div>

            <!-- Penawaran & Promo -->
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pt-4 border-t border-gray-100">
              <div class="flex flex-wrap gap-3">
                <button 
                  @click="filterDiscount = !filterDiscount"
                  class="flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-semibold border transition-all duration-200"
                  :class="filterDiscount ? 'bg-red-50 text-red-600 border-red-500 ring-1 ring-red-500' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'"
                >
                  <UIcon name="i-heroicons-receipt-percent" class="w-4 h-4" />
                  Harga Diskon
                </button>
                <button 
                  @click="filterPromo = !filterPromo"
                  class="flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-semibold border transition-all duration-200"
                  :class="filterPromo ? 'bg-amber-50 text-amber-700 border-amber-500 ring-1 ring-amber-500' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'"
                >
                  <UIcon name="i-heroicons-sparkles" class="w-4 h-4" />
                  Promo Spesial
                </button>
              </div>

              <div class="flex items-center gap-2">
                <div class="relative w-full sm:w-64">
                  <UIcon name="i-heroicons-ticket" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input 
                    v-model="promoCode" 
                    type="text" 
                    placeholder="Masukkan kode promo" 
                    class="w-full bg-gray-50 border border-gray-200 rounded-xl pl-9 pr-3 py-2 text-sm font-semibold outline-none focus:border-green-600 focus:bg-white focus:ring-1 focus:ring-green-600 transition-all uppercase placeholder:normal-case placeholder:font-medium" 
                    @keyup.enter="applyPromoCode" 
                  />
                </div>
                <button 
                  @click="applyPromoCode" 
                  class="bg-gray-900 text-white px-4 py-2 rounded-xl text-sm font-bold hover:bg-green-600 transition-colors shadow-sm"
                >
                  Cek
                </button>
              </div>
            </div>

          </div>

          <!-- ── Wishlist Grid / Empty State ──────────────────────── -->
          <div v-if="filteredAndSortedWishlist.length === 0" class="flex flex-col items-center justify-center py-24 text-center border border-gray-200 rounded-3xl bg-white shadow-sm">
            <div class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mb-5">
              <UIcon name="i-heroicons-heart" class="w-10 h-10 text-gray-300" />
            </div>
            <h2 class="text-lg font-bold text-gray-900 mb-2">Belum ada barang impian</h2>
            <p class="text-gray-500 font-medium text-sm mb-6 max-w-sm">Cari produk CCTV incaranmu atau ubah filter di atas untuk menemukan barang yang tepat.</p>
            <NuxtLink to="/">
              <button class="bg-green-600 text-white px-8 py-3 rounded-xl font-bold text-sm hover:bg-green-700 transition-all shadow-sm shadow-green-600/20 active:scale-95">
                Mulai Belanja
              </button>
            </NuxtLink>
          </div>

          <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <CardPerItems
              v-for="item in filteredAndSortedWishlist"
              :key="item.wishlist_uuid"
              :uuid="item.stock?.uuid"
              :slug="item.stock?.slug"
              :title="item.stock?.title"
              :image="item.stock?.cover_image_url || '/placeholder.webp'"
              :price="item.stock?.online_price || 0"
              :original_price="item.stock?.original_price"
              :discount_percentage="item.stock?.discount_percentage"
              :brand="item.stock?.brand"
              :category="item.stock?.category_slug"
              :subcategory="item.stock?.subcategory_slug"
              :specs="item.stock?.specs"
            />
          </div>

        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

main {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
</style>