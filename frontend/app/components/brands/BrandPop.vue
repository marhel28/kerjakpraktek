<script setup lang="ts">
import { useRuntimeConfig } from '#app'

// Menerima status buka/tutup dari Header parent
defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits(['mouseenter', 'mouseleave'])
const config = useRuntimeConfig()

// ==========================================
// 🛡️ TYPESCRIPT INTERFACES
// ==========================================
interface BrandLogo {
  name: string
  image: string
  link: string
}

interface CollectionItem {
  brand: string
  brand_raw: string
  items: string[]
  seeAllLink: string
}

interface MegamenuResponse {
  status: string
  source: string
  data: CollectionItem[]
}

// ==========================================
// 1. FETCH LOGO BRANDS (Non-Blocking)
// ==========================================
const { data: brandLogos, pending: pendingBrands } = useFetch<BrandLogo[]>('/api/logobanner', {
  lazy: true, // 🔥 PENTING: Mencegah render blocking pada halaman utama
  transform: (apiData: any) => {
    // Sesuaikan jika apiData terbungkus { data: [...] }
    const rawData = Array.isArray(apiData) ? apiData : apiData?.data || []
    
    return rawData
      .filter((b: any) => b.f === true)
      .map((b: any) => ({
        name: b.n,
        image: b.img,
        link: b.r || `/brands/${b.s}`
      }))
      .slice(0, 6)
  },
  default: () => []
})

// ==========================================
// 2. FETCH TOP COLLECTIONS (Non-Blocking)
// ==========================================
// Menggunakan URL backend secara langsung atau proxy sesuai setup Anda
const { data: topCollections, pending: pendingCollections } = useFetch<CollectionItem[]>(`${config.public.apiBase}/stok/public/megamenu-collections`, {
  lazy: true, // 🔥 PENTING: Biarkan skeleton UI bekerja sementara data ditarik (terutama dari Redis)
  transform: (res: MegamenuResponse | any) => {
    return res.data || []
  },
  default: () => []
})
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform -translate-y-4 opacity-0 pointer-events-none"
    enter-to-class="transform translate-y-0 opacity-100 pointer-events-auto"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100 pointer-events-auto"
    leave-to-class="transform -translate-y-2 opacity-0 pointer-events-none"
  >
    <div
      v-show="isOpen"
      class="absolute top-full left-0 w-full bg-white border-b border-gray-200 shadow-xl z-50 origin-top"
      @mouseenter="emit('mouseenter')"
      @mouseleave="emit('mouseleave')"
    >
      <div class="max-w-7xl mx-auto px-4 lg:px-10 py-8 md:py-10 flex flex-col md:flex-row gap-10 lg:gap-16">

        <div class="w-full md:w-[40%] lg:w-[35%]">
          <h3 class="text-base font-bold text-[#1d1d1f] mb-6 tracking-tight">Shop by Brands</h3>

          <div class="grid grid-cols-2 lg:grid-cols-3 gap-2">
            <template v-if="pendingBrands">
              <USkeleton v-for="i in 6" :key="`skel-brand-${i}`" class="h-[70px] w-full rounded-xl bg-gray-100" />
            </template>

            <template v-else>
              <NuxtLink
                v-for="brand in brandLogos"
                :key="brand.name"
                :to="brand.link"
                class="group flex items-center justify-center border border-gray-200 rounded-xl p-4 h-[70px] transition-all duration-300 hover:border-green-600 hover:shadow-[0_4px_12px_rgba(22,163,74,0.1)]"
              >
                <NuxtImg
                  :src="brand.image"
                  :alt="`Logo ${brand.name}`"
                  loading="lazy"
                  format="webp"
                  quality="80"
                  class="max-h-full max-w-full object-contain filter grayscale group-hover:grayscale-0 transition-all duration-300"
                />
              </NuxtLink>
            </template>
          </div>
        </div>

        <div class="w-full md:w-[60%] lg:w-[65%] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">

          <template v-if="pendingCollections">
            <div v-for="i in 3" :key="`skel-col-${i}`" class="flex flex-col">
              <USkeleton class="h-5 w-3/4 mb-5 bg-gray-200" />
              <div class="flex flex-col gap-3.5 mb-6">
                <USkeleton v-for="j in 3" :key="j" class="h-4 w-full bg-gray-100" />
              </div>
              <USkeleton class="h-4 w-1/2 mt-auto bg-gray-200" />
            </div>
          </template>

          <template v-else>
            <div v-for="collection in topCollections" :key="collection.brand" class="flex flex-col">
              <h4 class="text-[15px] font-bold text-[#1d1d1f] mb-5">{{ collection.brand }}</h4>

              <ul class="flex flex-col gap-3.5 mb-6 flex-1">
                <li v-for="item in collection.items" :key="item">
                  <NuxtLink
                    :to="`${collection.seeAllLink}?q=${encodeURIComponent(item)}`"
                    class="text-sm text-gray-500 hover:text-green-600 hover:font-bold transition-colors duration-200 capitalize line-clamp-1"
                    :title="item"
                  >
                    {{ item }}
                  </NuxtLink>
                </li>
              </ul>

              <NuxtLink
                :to="collection.seeAllLink"
                class="group inline-flex items-center gap-1 text-sm font-bold text-[#1d1d1f] mt-auto hover:text-green-600 transition-colors"
              >
                See All {{ collection.brand_raw }}
                <UIcon
                  name="i-heroicons-chevron-right"
                  class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1"
                />
              </NuxtLink>
            </div>
          </template>

        </div>

      </div>
    </div>
  </Transition>
</template>

<style scoped>
div {
  font-family: var(--font-sans);
}
</style>