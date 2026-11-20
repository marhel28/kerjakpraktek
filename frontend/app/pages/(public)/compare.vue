<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCompareStore, type CompareItem } from '~/stores/compare'
import { useWishlistStore } from '~/stores/wishlist'
import { useCheckoutStore } from '~/stores/checkout'
import { useCartStore } from '~/stores/cart'

const compareStore = useCompareStore() as any
const wishlistStore = useWishlistStore() as any
const checkoutStore = useCheckoutStore() as any
const cartStore = useCartStore() as any
const router = useRouter()
const toast = useToast()

const highlightDiff = ref(false)

// ==========================================
// 📐 SPECIFICATION DICTIONARY & GROUPING
// ==========================================
interface SpecGroup {
  id: string
  name: string
  icon: string
  keys: string[]
}

const SPEC_DICTIONARY: { id: string; name: string; icon: string; patterns: RegExp[] }[] = [
  {
    id: 'sensor',
    name: 'Kualitas Gambar & Sensor',
    icon: 'i-heroicons-camera',
    patterns: [/resolusi|resolution|sensor|megapixel|mp|pixel|fps|framerate|shutter|wdr|dnr/i]
  },
  {
    id: 'lens',
    name: 'Lensa & Bidang Pandang',
    icon: 'i-heroicons-eye',
    patterns: [/lensa|lens|focal|fov|sudut|angle|aperture|zoom|focus/i]
  },
  {
    id: 'night',
    name: 'Penglihatan Malam (Night Vision)',
    icon: 'i-heroicons-moon',
    patterns: [/night|malam|ir|infra|colorvu|fullcolor|illuminat|lux/i]
  },
  {
    id: 'network',
    name: 'Konektivitas & Kompresi',
    icon: 'i-heroicons-wifi',
    patterns: [/kompresi|compression|codec|h\.264|h\.265|network|lan|ethernet|wifi|wi-fi|poe|port|protokol|protocol/i]
  },
  {
    id: 'smart',
    name: 'Fitur Pintar & Audio',
    icon: 'i-heroicons-cpu-chip',
    patterns: [/ai|smart|deteksi|detection|motion|human|vehicle|audio|mic|speaker|alarm/i]
  },
  {
    id: 'physical',
    name: 'Daya & Ketahanan Fisik',
    icon: 'i-heroicons-shield-check',
    patterns: [/ip|weather|waterproof|outdoor|daya|power|volt|casing|dimensi|dimension|berat|weight|suhu|temp|operat/i]
  }
]

const allSpecKeys = computed(() => {
  const keys = new Set<string>()
  compareStore.items.forEach((item: CompareItem) => {
    if (item.specs && typeof item.specs === 'object') {
      Object.keys(item.specs).forEach(k => keys.add(k))
    }
  })
  return Array.from(keys)
})

const groupedSpecs = computed<SpecGroup[]>(() => {
  const categorized = new Set<string>()
  const groups: SpecGroup[] = []

  SPEC_DICTIONARY.forEach(dict => {
    const matchedKeys = allSpecKeys.value.filter(k => {
      if (categorized.has(k)) return false
      const match = dict.patterns.some(p => p.test(k))
      if (match) categorized.add(k)
      return match
    })

    if (matchedKeys.length > 0) {
      groups.push({
        id: dict.id,
        name: dict.name,
        icon: dict.icon,
        keys: matchedKeys.sort()
      })
    }
  })

  const remainingKeys = allSpecKeys.value.filter(k => !categorized.has(k)).sort()
  if (remainingKeys.length > 0) {
    groups.push({
      id: 'others',
      name: 'Spesifikasi Tambahan',
      icon: 'i-heroicons-adjustments-horizontal',
      keys: remainingKeys
    })
  }

  return groups
})

const isSpecDifferent = (key: string) => {
  if (compareStore.items.length <= 1) return false
  const firstVal = normalizeSpecValue(compareStore.items[0]?.specs?.[key])
  return compareStore.items.some((item: CompareItem) => {
    const currentVal = normalizeSpecValue(item?.specs?.[key])
    return currentVal !== firstVal
  })
}

function normalizeSpecValue(val: any): string {
  if (val === null || val === undefined || val === '') return '-'
  return String(val).trim().toLowerCase()
}

// ==========================================
// ⚡ ACTIONS & FORMATTERS
// ==========================================
const removeItem = (item: CompareItem) => {
  compareStore.toggle(item)
}

const clearAll = () => {
  compareStore.clear()
}

const toggleWishlist = (item: CompareItem) => {
  wishlistStore.toggle(item)
}

const isWishlist = (id: string | number) => {
  return wishlistStore.isInWishlist(id)
}

const formatPrice = (value: number) => {
  if (!value) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value).replace('Rp', 'Rp ')
}

const addToCart = (item: CompareItem) => {
  cartStore.add({
    stock_uuid: String(item.id),
    title: item.title,
    price: item.price,
    original_price: item.originalPrice || 0,
    discount_percentage: 0,
    image: item.image,
    quantity: 1,
    weight: 1000,
    brand: item.brand,
    category_slug: '',
    options: null,
    specs: item.specs || {}
  })

  toast.add({
    title: 'Berhasil Ditambahkan',
    description: `${item.title} telah masuk ke keranjang belanja.`,
    icon: 'i-heroicons-check-circle',
    color: 'success'
  })
}

const beliLangsung = (item: CompareItem) => {
  checkoutStore.setCheckoutData([
    {
      id: item.id,
      title: item.title,
      price: item.price,
      image: item.image,
      quantity: 1,
      weight: 1000,
      options: null,
      stock_uuid: item.id
    }
  ], 0, '')
  router.push('/payment')
}

// ==========================================
// 🔍 SEO META
// ==========================================
useSeoMeta({
  title: 'Bandingkan Spesifikasi Kamera CCTV | PasarCCTV',
  description: 'Matriks perbandingan spesifikasi teknis kamera pengawas, resolusi sensor, lensa, kemampuan malam, dan sertifikasi proteksi cuaca.',
  ogTitle: 'Komparasi Produk CCTV | PasarCCTV',
  ogDescription: 'Perbandingan detail spesifikasi teknis perangkat CCTV secara berdampingan.'
})
</script>

<template>
  <main class="min-h-screen bg-gray-50 py-6 md:py-10">
    <div class="max-w-[1400px] mx-auto px-4 md:px-6">
      
      <!-- Breadcrumbs -->
      <nav class="flex items-center gap-2 text-xs text-gray-500 mb-4" aria-label="Breadcrumb">
        <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
        <span>/</span>
        <NuxtLink to="/produk" class="hover:text-[#03AC0E] transition-colors">Katalog</NuxtLink>
        <span>/</span>
        <span class="text-gray-900 font-medium">Perbandingan Produk</span>
      </nav>

      <!-- Header Section -->
      <header class="mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4 pb-5 border-b border-gray-200">
        <div>
          <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#E6F7E9] text-[#03AC0E] text-xs font-medium mb-2">
            <UIcon name="i-heroicons-scale" class="w-4 h-4" />
            <span>Matriks Spesifikasi Teknis</span>
          </div>
          <h1 class="text-2xl md:text-3xl font-medium text-gray-900 tracking-tight">
            Perbandingan Produk
          </h1>
          <p class="text-xs md:text-sm text-gray-600 mt-1 max-w-2xl">
            Tinjau perbedaan sensor, lensa, jangkauan inframerah, dan sertifikasi lingkungan antar perangkat sebelum memutuskan pembelian.
          </p>
        </div>

        <div v-if="compareStore.items.length > 0" class="flex flex-wrap items-center gap-3">
          <!-- Diff Highlight Toggle -->
          <button
            type="button"
            @click="highlightDiff = !highlightDiff"
            class="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium border transition-colors cursor-pointer"
            :class="highlightDiff 
              ? 'bg-[#E6F7E9] border-[#C8E6CC] text-[#03AC0E]' 
              : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'"
            :aria-pressed="highlightDiff"
          >
            <UIcon :name="highlightDiff ? 'i-heroicons-eye' : 'i-heroicons-eye-slash'" class="w-4 h-4 shrink-0" />
            <span>{{ highlightDiff ? 'Sorotan Aktif' : 'Sorot Perbedaan' }}</span>
          </button>

          <!-- Clear All Button -->
          <button
            type="button"
            @click="clearAll"
            class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium text-red-600 bg-red-50 border border-red-100 hover:bg-red-100 transition-colors cursor-pointer"
          >
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            <span>Hapus Semua</span>
          </button>
        </div>
      </header>

      <ClientOnly>
        <!-- State: Empty List -->
        <section
          v-if="compareStore.items.length === 0"
          aria-labelledby="empty-compare-heading"
          class="bg-white rounded-xl border border-gray-200 p-8 md:p-14 text-center max-w-xl mx-auto my-8 shadow-xs"
        >
          <div class="w-14 h-14 rounded-full bg-gray-100 text-gray-400 flex items-center justify-center mx-auto mb-4">
            <UIcon name="i-heroicons-scale" class="w-7 h-7" />
          </div>
          <h2 id="empty-compare-heading" class="text-lg md:text-xl font-medium text-gray-900 mb-2">
            Belum Ada Produk yang Dibandingkan
          </h2>
          <p class="text-xs md:text-sm text-gray-500 mb-6 leading-relaxed">
            Pilih hingga 4 produk CCTV dari katalog dengan menekan tombol perbandingan untuk menganalisis spesifikasi secara berdampingan.
          </p>
          <NuxtLink
            to="/produk"
            class="inline-flex items-center gap-2 bg-[#03AC0E] text-white px-5 py-2.5 rounded-lg text-xs md:text-sm font-medium hover:bg-[#028C0B] transition-colors"
          >
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            Jelajahi Katalog Produk
          </NuxtLink>
        </section>

        <!-- State: 1 Item Prompt -->
        <div
          v-else-if="compareStore.items.length === 1"
          class="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start gap-3 text-xs text-amber-900"
        >
          <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div class="flex-1">
            <p class="font-medium text-amber-950">Dibutuhkan minimal 2 produk untuk komparasi</p>
            <p class="mt-0.5 text-amber-800">
              Anda baru memilih 1 produk. Tambahkan setidaknya 1 produk lagi dari katalog agar perbandingan spesifikasi dapat berjalan.
            </p>
          </div>
          <NuxtLink
            to="/produk"
            class="inline-flex items-center gap-1 text-xs font-medium text-amber-900 hover:underline shrink-0"
          >
            Tambah Produk
            <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" />
          </NuxtLink>
        </div>

        <!-- State: Matrix Table -->
        <div v-if="compareStore.items.length > 0" class="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
          <div class="overflow-x-auto custom-scrollbar">
            <table class="w-full text-left border-collapse min-w-[760px]">
              
              <!-- Sticky Product Card Headers -->
              <thead>
                <tr class="bg-white border-b border-gray-200">
                  <!-- Top Left Sticky Cell -->
                  <th
                    scope="col"
                    class="p-4 w-[240px] min-w-[240px] max-w-[240px] bg-white sticky left-0 z-30 align-bottom border-r border-gray-200"
                  >
                    <div class="pb-2">
                      <span class="text-[11px] font-medium text-gray-500 uppercase tracking-wider block">
                        Perangkat Terpilih
                      </span>
                      <span class="text-xs text-gray-700 font-medium">
                        {{ compareStore.items.length }} dari 4 slot terisi
                      </span>
                    </div>
                  </th>

                  <!-- Product Columns -->
                  <th
                    v-for="item in compareStore.items"
                    :key="item.id"
                    scope="col"
                    class="p-4 w-[280px] min-w-[280px] max-w-[280px] bg-white align-top font-normal border-r border-gray-200 last:border-r-0"
                  >
                    <div class="flex flex-col h-[340px] bg-white rounded-lg border border-gray-200 p-3.5 relative hover:border-[#03AC0E] transition-colors">
                      
                      <!-- Remove Button -->
                      <button
                        type="button"
                        @click="removeItem(item)"
                        class="absolute top-2 right-2 z-10 w-7 h-7 flex items-center justify-center bg-white border border-gray-200 rounded-full text-gray-400 hover:text-red-600 hover:border-red-200 transition-colors cursor-pointer"
                        title="Hapus kolom ini"
                        aria-label="Hapus dari komparasi"
                      >
                        <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
                      </button>

                      <!-- Product Image Thumbnail -->
                      <NuxtLink
                        :to="`/product/${item.id}`"
                        class="h-[140px] w-full bg-gray-50 rounded-md p-2 flex items-center justify-center overflow-hidden shrink-0 mb-3"
                      >
                        <NuxtImg
                          :src="item.image"
                          :alt="item.title"
                          loading="lazy"
                          format="webp"
                          class="w-full h-full object-contain"
                        />
                      </NuxtLink>

                      <!-- Brand Badge & Title -->
                      <div class="flex flex-col flex-1 min-w-0">
                        <span
                          v-if="item.brand"
                          class="self-start text-[10px] font-medium uppercase tracking-wider text-[#03AC0E] bg-[#E6F7E9] px-2 py-0.5 rounded mb-1.5"
                        >
                          {{ item.brand }}
                        </span>
                        
                        <NuxtLink
                          :to="`/product/${item.id}`"
                          class="text-xs font-medium text-gray-900 line-clamp-2 hover:text-[#03AC0E] transition-colors leading-snug"
                        >
                          {{ item.title }}
                        </NuxtLink>

                        <!-- Price Section -->
                        <div class="mt-auto pt-2">
                          <p
                            v-if="item.originalPrice && item.originalPrice > item.price"
                            class="text-[11px] text-gray-400 line-through leading-none mb-0.5"
                          >
                            {{ formatPrice(item.originalPrice) }}
                          </p>
                          <p class="text-base font-medium text-[#03AC0E]">
                            {{ formatPrice(item.price) }}
                          </p>
                        </div>
                      </div>

                      <!-- Action Buttons -->
                      <div class="flex items-center gap-1.5 mt-3 pt-2.5 border-t border-gray-100">
                        <button
                          type="button"
                          @click="addToCart(item)"
                          class="flex-1 bg-white border border-[#03AC0E] text-[#03AC0E] hover:bg-[#E6F7E9] py-1.5 px-2 rounded text-xs font-medium transition-colors flex items-center justify-center gap-1 cursor-pointer"
                          title="Tambah ke Keranjang"
                        >
                          <UIcon name="i-heroicons-shopping-cart" class="w-3.5 h-3.5" />
                          <span>+ Keranjang</span>
                        </button>

                        <button
                          type="button"
                          @click="beliLangsung(item)"
                          class="bg-[#03AC0E] text-white hover:bg-[#028C0B] py-1.5 px-3 rounded text-xs font-medium transition-colors flex items-center justify-center cursor-pointer"
                          title="Beli Langsung"
                        >
                          Beli
                        </button>

                        <button
                          type="button"
                          @click="toggleWishlist(item)"
                          class="w-7 h-7 flex items-center justify-center bg-white border border-gray-200 rounded hover:border-red-200 hover:bg-red-50 transition-colors cursor-pointer"
                          :title="isWishlist(item.id) ? 'Hapus dari Wishlist' : 'Tambah ke Wishlist'"
                        >
                          <UIcon
                            :name="isWishlist(item.id) ? 'i-heroicons-heart-solid' : 'i-heroicons-heart'"
                            class="w-4 h-4"
                            :class="isWishlist(item.id) ? 'text-red-500' : 'text-gray-400'"
                          />
                        </button>
                      </div>
                    </div>
                  </th>

                  <!-- Placeholder Empty Slot if less than 4 -->
                  <th
                    v-if="compareStore.items.length < 4"
                    scope="col"
                    class="p-4 w-[280px] min-w-[280px] max-w-[280px] bg-white align-top font-normal border-r border-gray-200"
                  >
                    <NuxtLink
                      to="/produk"
                      class="flex flex-col h-[340px] bg-gray-50/50 rounded-lg border-2 border-dashed border-gray-200 hover:border-[#03AC0E] hover:bg-[#E6F7E9]/20 transition-all p-4 items-center justify-center text-center group cursor-pointer"
                    >
                      <div class="w-10 h-10 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-400 group-hover:text-[#03AC0E] group-hover:border-[#03AC0E] transition-colors mb-2">
                        <UIcon name="i-heroicons-plus" class="w-5 h-5" />
                      </div>
                      <span class="text-xs font-medium text-gray-900 group-hover:text-[#03AC0E] transition-colors">
                        Tambah Produk Lain
                      </span>
                      <span class="text-[11px] text-gray-500 mt-1 max-w-[180px]">
                        Pilih kamera atau aksesori dari katalog untuk dibandingkan
                      </span>
                    </NuxtLink>
                  </th>

                  <!-- Trailing empty spacing -->
                  <th class="w-full bg-white"></th>
                </tr>
              </thead>

              <!-- Specifications Body Grouped -->
              <tbody>
                <!-- Quick Overview Section -->
                <tr class="bg-gray-100/70 border-b border-gray-200">
                  <td colspan="100" class="py-2.5 px-4 text-xs font-medium text-gray-900 uppercase tracking-wide bg-gray-100/90">
                    <div class="flex items-center gap-1.5">
                      <UIcon name="i-heroicons-tag" class="w-4 h-4 text-[#03AC0E]" />
                      <span>Ringkasan Produk</span>
                    </div>
                  </td>
                </tr>

                <tr class="border-b border-gray-100 hover:bg-gray-50/50 transition-colors">
                  <th scope="row" class="p-3.5 text-xs font-medium text-gray-700 bg-white sticky left-0 z-20 border-r border-gray-200">
                    Merek
                  </th>
                  <td
                    v-for="item in compareStore.items"
                    :key="`brand-${item.id}`"
                    class="p-3.5 text-xs text-gray-800 border-r border-gray-200 last:border-r-0"
                  >
                    {{ item.brand || '-' }}
                  </td>
                  <td v-if="compareStore.items.length < 4" class="p-3.5 text-xs text-gray-400 border-r border-gray-200">-</td>
                  <td class="w-full"></td>
                </tr>

                <tr class="border-b border-gray-100 hover:bg-gray-50/50 transition-colors">
                  <th scope="row" class="p-3.5 text-xs font-medium text-gray-700 bg-white sticky left-0 z-20 border-r border-gray-200">
                    Kategori / Tipe
                  </th>
                  <td
                    v-for="item in compareStore.items"
                    :key="`type-${item.id}`"
                    class="p-3.5 text-xs text-gray-800 border-r border-gray-200 last:border-r-0"
                  >
                    {{ item.type || '-' }}
                  </td>
                  <td v-if="compareStore.items.length < 4" class="p-3.5 text-xs text-gray-400 border-r border-gray-200">-</td>
                  <td class="w-full"></td>
                </tr>

                <!-- Grouped Technical Specifications -->
                <template v-for="group in groupedSpecs" :key="group.id">
                  <!-- Section Group Banner -->
                  <tr class="bg-gray-100/80 border-t-2 border-b border-gray-200">
                    <td colspan="100" class="py-2.5 px-4 text-xs font-medium text-gray-900 uppercase tracking-wide bg-gray-100/90">
                      <div class="flex items-center gap-1.5">
                        <UIcon :name="group.icon" class="w-4 h-4 text-[#03AC0E]" />
                        <span>{{ group.name }}</span>
                      </div>
                    </td>
                  </tr>

                  <!-- Specification Rows in Group -->
                  <tr
                    v-for="key in group.keys"
                    :key="key"
                    class="border-b border-gray-100 transition-colors"
                    :class="[
                      highlightDiff && isSpecDifferent(key) ? 'bg-[#E6F7E9]/40' : 'hover:bg-gray-50/50'
                    ]"
                  >
                    <!-- Spec Label Column -->
                    <th
                      scope="row"
                      class="p-3.5 text-xs font-medium text-gray-700 sticky left-0 z-20 border-r border-gray-200 capitalize"
                      :class="highlightDiff && isSpecDifferent(key) ? 'bg-[#F2FBF4]' : 'bg-white'"
                    >
                      <div class="flex items-center justify-between gap-2">
                        <span>{{ key }}</span>
                        <span
                          v-if="highlightDiff && isSpecDifferent(key)"
                          class="w-1.5 h-1.5 rounded-full bg-[#03AC0E] shrink-0"
                          title="Terdapat perbedaan nilai"
                        ></span>
                      </div>
                    </th>

                    <!-- Product Spec Value Columns -->
                    <td
                      v-for="item in compareStore.items"
                      :key="`${key}-${item.id}`"
                      class="p-3.5 text-xs border-r border-gray-200 last:border-r-0 leading-relaxed"
                      :class="[
                        item.specs?.[key] ? 'text-gray-800' : 'text-gray-400',
                        highlightDiff && isSpecDifferent(key) ? 'font-medium' : ''
                      ]"
                    >
                      {{ item.specs?.[key] || '-' }}
                    </td>

                    <!-- Empty Slot Column Filler -->
                    <td
                      v-if="compareStore.items.length < 4"
                      class="p-3.5 text-xs text-gray-400 border-r border-gray-200"
                    >
                      -
                    </td>

                    <td class="w-full"></td>
                  </tr>
                </template>

                <!-- Fallback when no specs JSON exists -->
                <tr v-if="allSpecKeys.length === 0" class="border-b border-gray-200">
                  <td colspan="100" class="p-8 text-center text-xs text-gray-500">
                    Spesifikasi detail belum dicantumkan pada produk terpilih.
                  </td>
                </tr>
              </tbody>

            </table>
          </div>
        </div>

        <template #fallback>
          <div class="flex flex-col items-center justify-center min-h-[360px] gap-3">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-[#03AC0E] animate-spin" />
            <span class="text-xs font-medium text-gray-500">Memuat matriks perbandingan...</span>
          </div>
        </template>
      </ClientOnly>

    </div>
  </main>
</template>

<style scoped>
main {
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #03AC0E;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>