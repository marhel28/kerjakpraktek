<script setup lang="ts">
import { computed } from 'vue'
import { useCompareStore } from '~/stores/compare'
import { useWishlistStore } from '~/stores/wishlist'

const compareStore = useCompareStore()
const wishlistStore = useWishlistStore()

// ==========================================
// 🚀 DYNAMIC SPECS EXTRACTOR
// ==========================================
const allSpecKeys = computed(() => {
  const keys = new Set<string>()
  compareStore.items.forEach(item => {
    if (item.specs && typeof item.specs === 'object') {
      Object.keys(item.specs).forEach(k => keys.add(k))
    }
  })
  return Array.from(keys).sort() 
})

// ==========================================
// ⚡ ACTIONS & FORMATTERS
// ==========================================
const removeItem = (item: any) => {
  compareStore.toggle(item)
}

const clearAll = () => {
  compareStore.clear()
}

const toggleWishlist = (item: any) => {
  wishlistStore.toggle(item)
}

const isWishlist = (id: string | number) => {
  return wishlistStore.isInWishlist(id)
}

const formatPrice = (value: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value).replace('Rp', 'Rp ')
}

// ==========================================
// 🔍 SEO META
// ==========================================
useSeoMeta({
  title: 'Bandingkan Spesifikasi CCTV & Keamanan | Padjajaran CCTV',
  description: 'Bandingkan harga, fitur, dan spesifikasi teknis dari berbagai kamera CCTV secara berdampingan. Temukan produk yang paling sesuai dengan kebutuhan keamanan Anda.',
  ogTitle: 'Bandingkan Produk Keamanan | Padjajaran CCTV',
  ogDescription: 'Analisis produk CCTV secara detail dan berdampingan.',
})
</script>

<template>
  <main class="min-h-screen overflow-x-hidden bg-[#f8f9fa] relative py-10 lg:py-16 selection:bg-green-100">
    
    <div class="absolute top-0 right-0 w-[600px] h-[600px] bg-green-500/5 rounded-full blur-3xl -translate-y-1/3 translate-x-1/4 pointer-events-none" aria-hidden="true"></div>

    <div class="container mx-auto px-4 max-w-[1400px] relative z-10">

      <header class="mb-8 lg:mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-gray-200/60 pb-6">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <UIcon name="i-heroicons-scale" class="w-6 h-6 text-green-600" />
            <span class="text-sm font-bold uppercase tracking-widest text-green-600">Komparasi</span>
          </div>
          <h1 class="text-3xl lg:text-4xl font-black text-gray-900 tracking-tight mb-2">
            Bandingkan Produk
          </h1>
          <p class="text-sm lg:text-base text-gray-500 max-w-2xl font-medium">
            Analisis detail harga dan spesifikasi teknis secara berdampingan untuk memastikan Anda memilih solusi keamanan yang tepat.
          </p>
        </div>
        
        <button 
          v-if="compareStore.items.length > 0"
          @click="clearAll"
          class="group flex items-center gap-2 text-sm font-bold text-red-500 bg-red-50 hover:bg-red-500 hover:text-white transition-all px-5 py-2.5 rounded-full shadow-sm"
          aria-label="Hapus semua produk dari daftar perbandingan"
        >
          <UIcon name="i-heroicons-trash" class="w-4 h-4 group-hover:scale-110 transition-transform" />
          Bersihkan Daftar
        </button>
      </header>

      <ClientOnly>
        
        <section
          v-if="compareStore.items.length === 0"
          aria-labelledby="empty-heading"
          class="bg-white rounded-3xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-10 lg:p-20 text-center flex flex-col items-center justify-center"
        >
          <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6 border border-gray-100 shadow-inner">
            <UIcon name="i-heroicons-archive-box-x-mark" class="w-12 h-12 text-gray-300" />
          </div>
          <h2 id="empty-heading" class="text-xl lg:text-2xl font-black text-gray-900 mb-3">Daftar Komparasi Kosong</h2>
          <p class="text-gray-500 text-sm mb-8 max-w-md mx-auto leading-relaxed">
            Anda belum menambahkan produk untuk dibandingkan. Silakan kembali ke katalog dan klik ikon timbangan pada produk pilihan Anda.
          </p>
          <NuxtLink
            to="/category/semua-kategori"
            class="px-8 py-3.5 bg-gray-900 text-white text-sm font-bold uppercase tracking-wider rounded-xl hover:bg-green-600 hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
          >
            Mulai Belanja
          </NuxtLink>
        </section>

        <section v-else class="bg-white rounded-3xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] overflow-hidden relative">
          
          <div class="overflow-x-auto custom-scrollbar pb-4">
            <table class="w-full text-left border-collapse">

              <thead>
                <tr>
                  <th scope="col" class="p-6 border-b-2 border-gray-100 w-[200px] min-w-[200px] bg-white sticky left-0 z-20 shadow-[4px_0_15px_rgba(0,0,0,0.03)] align-bottom">
                    <span class="text-xs font-black text-gray-400 uppercase tracking-widest block mb-2">
                      Informasi Produk
                    </span>
                  </th>

                  <th
                    v-for="item in compareStore.items"
                    :key="item.id"
                    scope="col"
                    class="p-4 border-b-2 border-l border-gray-100 w-[280px] min-w-[280px] max-w-[280px] bg-white align-top font-normal"
                  >
                    <div class="relative flex flex-col h-[400px] bg-white rounded-2xl border border-gray-200 hover:border-green-500 hover:shadow-xl transition-all duration-300 overflow-hidden group">
                      
                      <button
                        @click="removeItem(item)"
                        class="absolute top-2 right-2 z-10 w-8 h-8 flex items-center justify-center bg-white/90 backdrop-blur border border-gray-200 rounded-full shadow-sm text-gray-400 hover:text-white hover:border-red-500 hover:bg-red-500 transition-all cursor-pointer"
                        title="Hapus dari daftar"
                      >
                        <UIcon name="i-heroicons-x-mark-20-solid" class="w-4 h-4" />
                      </button>

                      <NuxtLink :to="`/product/${item.id}`" class="relative h-[180px] w-full bg-[#f9fafb] p-4 flex items-center justify-center flex-shrink-0 overflow-hidden">
                        <NuxtImg
                          :src="item.image"
                          :alt="item.title"
                          format="webp"
                          class="w-full h-full object-contain mix-blend-multiply group-hover:scale-105 transition-transform duration-500"
                        />
                      </NuxtLink>

                      <div class="p-4 flex flex-col flex-1">
                        <span class="self-start text-[10px] font-black uppercase tracking-wider text-green-700 bg-green-50 px-2 py-0.5 rounded mb-2 border border-green-100/50">
                          {{ item.brand || 'NO BRAND' }}
                        </span>

                        <NuxtLink :to="`/product/${item.id}`" class="text-sm font-bold text-gray-800 line-clamp-2 leading-tight mb-2 hover:text-green-600 transition-colors">
                          {{ item.title }}
                        </NuxtLink>

                        <div class="mt-auto flex flex-col mb-4">
                          <span v-if="item.originalPrice > item.price" class="text-[11px] text-gray-400 line-through mb-0.5">
                            {{ formatPrice(item.originalPrice) }}
                          </span>
                          <span v-else class="h-4 mb-0.5"></span>
                          <span class="text-base font-black text-gray-900 tracking-tight">
                            {{ formatPrice(item.price) }}
                          </span>
                        </div>

                        <div class="flex gap-2 mt-auto">
                          <button class="flex-1 bg-gray-900 text-white text-xs font-bold uppercase tracking-wider py-2 rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-1 shadow-sm">
                            <UIcon name="i-heroicons-shopping-bag" class="w-3.5 h-3.5" />
                            Beli
                          </button>
                          <button 
                            @click="toggleWishlist(item)"
                            class="w-8 h-8 flex items-center justify-center bg-white border border-gray-200 rounded-lg hover:bg-red-50 hover:border-red-200 transition-colors shadow-sm"
                          >
                            <UIcon 
                              :name="isWishlist(item.id) ? 'i-heroicons-heart-solid' : 'i-heroicons-heart'" 
                              class="w-4 h-4 transition-colors"
                              :class="isWishlist(item.id) ? 'text-red-500' : 'text-gray-400'"
                            />
                          </button>
                        </div>
                      </div>
                    </div>
                  </th>
                  
                  <th class="w-full bg-white border-b-2 border-gray-100"></th>
                </tr>
              </thead>

              <tbody>
                <tr class="hover:bg-green-50/30 transition-colors">
                  <th scope="row" class="p-4 lg:p-5 border-b border-gray-100 bg-white sticky left-0 z-10 shadow-[4px_0_15px_rgba(0,0,0,0.03)] text-sm font-bold text-gray-800">
                    Kategori / Tipe
                  </th>
                  <td
                    v-for="item in compareStore.items"
                    :key="`type-${item.id}`"
                    class="p-4 lg:p-5 border-b border-l border-gray-100 text-sm text-gray-600 font-medium uppercase tracking-tight w-[280px] min-w-[280px] max-w-[280px]"
                  >
                    {{ item.type || '-' }}
                  </td>
                  <td class="w-full border-b border-gray-100 bg-white"></td>
                </tr>

                <tr v-for="(key, index) in allSpecKeys" :key="key" class="hover:bg-green-50/30 transition-colors group">
                  <th scope="row" class="p-4 lg:p-5 border-b border-gray-100 bg-white sticky left-0 z-10 shadow-[4px_0_15px_rgba(0,0,0,0.03)] text-sm font-bold text-gray-800 capitalize flex items-center gap-2">
                    <div class="w-1.5 h-1.5 rounded-full bg-gray-300 group-hover:bg-green-500 transition-colors"></div>
                    {{ key }}
                  </th>
                  <td
                    v-for="item in compareStore.items"
                    :key="`${key}-${item.id}`"
                    class="p-4 lg:p-5 border-b border-l border-gray-100 text-sm leading-relaxed w-[280px] min-w-[280px] max-w-[280px]"
                    :class="(item.specs && item.specs[key]) ? 'text-gray-700 font-medium' : 'text-gray-300'"
                  >
                    {{ (item.specs && item.specs[key]) ? item.specs[key] : '-' }}
                  </td>
                  <td class="w-full border-b border-gray-100 bg-white"></td>
                </tr>
              </tbody>

            </table>
          </div>
        </section>

        <template #fallback>
          <div class="flex flex-col items-center justify-center min-h-[400px] gap-4">
            <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-green-600 animate-spin" />
            <span class="text-sm font-bold text-gray-500 tracking-widest uppercase animate-pulse">Menyiapkan Tabel...</span>
          </div>
        </template>
      </ClientOnly>

    </div>
  </main>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  height: 10px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 10px;
  margin: 0 24px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 10px;
  border: 2px solid #f3f4f6; 
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #16a34a; 
}
</style>