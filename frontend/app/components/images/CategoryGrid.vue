<script setup lang="ts">
import CdnImage from '~/components/images/CdnImage.vue'

interface BannerItem {
  uuid?: string
  title: string
  image_url?: string
  route_link?: string
  sort_order?: number
}

const props = defineProps<{
  categories?: BannerItem[]
}>()

// Default fallback showcase jika backend tidak mengirim data
const defaultSolutions = [
  {
    title: 'Rumah Tinggal',
    subtitle: 'Pantau Anak & Rumah 24/7',
    link: '/category/kamera-cctv?type=indoor',
    image: '/images/showcase/dome.jpg',
    tag: 'Hunian'
  },
  {
    title: 'Toko & Kasir Ruko',
    subtitle: 'Cegah Kehilangan & Pantau Kasir',
    link: '/category/paket-cctv?tag=ruko',
    image: '/images/showcase/bullet.jpg',
    tag: 'Usaha'
  },
  {
    title: 'Gudang & Industri',
    subtitle: 'CCTV Night Color Area Luas',
    link: '/category/kamera-cctv?type=colorvu',
    image: '/images/showcase/colorvu.jpg',
    tag: 'Industri'
  },
  {
    title: 'Paket Usaha Komplit',
    subtitle: 'Include DVR & Harddisk Siap Rekam',
    link: '/category/paket-cctv',
    image: '/images/showcase/bundle.jpg',
    tag: 'Terlaris'
  }
]

const displayItems = computed(() => {
  if (props.categories && props.categories.length > 0) {
    return props.categories.map((banner, idx) => ({
      title: banner.title,
      subtitle: 'Katalog Produk Resmi',
      link: banner.route_link || '/category/kamera-cctv',
      image: banner.image_url || defaultSolutions[idx % defaultSolutions.length].image,
      tag: 'Solusi'
    }))
  }
  return defaultSolutions
})
</script>

<template>
  <section class="w-full my-8 sm:my-10" aria-label="Solusi Keamanan Berdasarkan Kebutuhan">
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      
      <!-- Section Header -->
      <div class="flex items-end justify-between mb-5 border-b border-gray-100 pb-3">
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-5 bg-[#03AC0E] rounded-full" aria-hidden="true" />
            <h2 class="text-base sm:text-lg font-bold text-gray-900 tracking-tight">
              Solusi Keamanan Sesuai Kebutuhan
            </h2>
          </div>
          <p class="text-xs text-gray-500 font-medium">
            Pilih paket yang telah dioptimalkan untuk lokasi Anda
          </p>
        </div>

        <NuxtLink
          to="/category/paket-cctv"
          class="flex items-center gap-1 text-xs font-bold text-[#03AC0E] hover:text-[#028C0B] transition-colors"
        >
          Semua Solusi
          <UIcon name="i-heroicons-arrow-small-right" class="w-4 h-4" />
        </NuxtLink>
      </div>

      <!-- Grid 4 Card Modern -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <NuxtLink
          v-for="(item, index) in displayItems"
          :key="index"
          :to="item.link"
          class="group relative h-[220px] sm:h-[260px] rounded-2xl overflow-hidden bg-gray-100 border border-gray-200/80 shadow-xs flex flex-col justify-end p-5 transition-all duration-300 hover:shadow-md hover:border-[#03AC0E]/50"
        >
          <!-- Image -->
          <NuxtImg
            :src="item.image"
            :alt="item.title"
            class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            width="400"
            height="300"
            loading="lazy"
            format="webp"
            quality="80"
          />

          <!-- Gradient Overlay Halus untuk Keterbacaan Teks -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/40 to-transparent" />

          <!-- Content -->
          <div class="relative z-10 flex flex-col">
            <span class="inline-block self-start text-[10px] font-bold uppercase tracking-wider text-white/90 bg-white/20 backdrop-blur-xs px-2 py-0.5 rounded-full mb-1.5">
              {{ item.tag }}
            </span>
            <h3 class="text-base font-bold text-white leading-snug group-hover:text-green-300 transition-colors">
              {{ item.title }}
            </h3>
            <p class="text-xs text-white/80 mt-0.5 font-normal leading-snug">
              {{ item.subtitle }}
            </p>

            <div class="mt-3 flex items-center gap-1 text-[11px] font-bold text-white group-hover:translate-x-1 transition-transform">
              <span>Eksplorasi Paket</span>
              <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5 text-[#03AC0E]" />
            </div>
          </div>
        </NuxtLink>
      </div>

    </div>
  </section>
</template>