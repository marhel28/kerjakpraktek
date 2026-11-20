<script setup lang="ts">
/**
 * Component: HomeBanner (Amazon Style Category Bar)
 * Style: Amazon Department Carousel / Category Grid with High-Resolution Studio Photography
 * Tokopedia Color Identity: Forest Green (#03AC0E) Accent
 */

const categories = [
  {
    name: 'Paket CCTV',
    sub: 'Komplit & Hemat',
    image: '/images/showcase/bundle.jpg',
    link: '/category/paket-cctv',
    badge: 'Best Value'
  },
  {
    name: 'Kamera Outdoor',
    sub: 'Weatherproof IP67',
    image: '/images/showcase/bullet.jpg',
    link: '/category/kamera-cctv',
    badge: 'Outdoor'
  },
  {
    name: 'Kamera Dome',
    sub: 'Plafon Interior',
    image: '/images/showcase/dome.jpg',
    link: '/category/kamera-cctv',
    badge: 'Indoor'
  },
  {
    name: 'Kamera PTZ 360°',
    sub: 'Auto Patrol HD',
    image: '/images/showcase/ptz.jpg',
    link: '/category/kamera-cctv',
    badge: 'Smart'
  },
  {
    name: 'ColorVu Malam',
    sub: 'Warna 24 Jam',
    image: '/images/showcase/colorvu.jpg',
    link: '/category/kamera-cctv',
    badge: '24h Color'
  },
  {
    name: 'DVR & NVR',
    sub: '4 - 32 Channel',
    image: '/images/showcase/dvr.jpg',
    link: '/category/dvr-nvr',
    badge: 'Perekam 4K'
  },
  {
    name: 'Storage Harddisk',
    sub: 'WD & Seagate',
    image: '/images/showcase/harddrive.jpg',
    link: '/category/storage',
    badge: 'Surveillance'
  },
  {
    name: 'Jasa & Teknisi',
    sub: 'Pasang & Servis',
    image: '/images/showcase/technician.jpg',
    link: '/layanan/booking',
    badge: 'Standby'
  }
]

const popularSearches = [
  { label: 'Paket 4 Kamera Hikvision', link: '/search?q=paket+hikvision' },
  { label: 'IP Camera 5MP ColorVu', link: '/search?q=colorvu' },
  { label: 'HDD Surveillance 2TB', link: '/search?q=hdd+2tb' },
  { label: 'Kamera WiFi PTZ', link: '/search?q=ptz' },
  { label: 'Jasa Pasang Bandung', link: '/layanan/booking' }
]
</script>

<template>
  <section class="w-full bg-transparent" aria-labelledby="amazon-category-heading">
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      
      <!-- Amazon Style Category Card Container -->
      <div class="bg-white rounded-xl sm:rounded-3xl p-5 sm:p-6 lg:p-7 border border-gray-200/90 shadow-xs">
        
        <!-- Header Section -->
        <div class="flex items-center justify-between pb-3.5 mb-5 border-b border-gray-100">
          <div class="flex items-center gap-2.5">
            <span class="w-1.5 h-5 bg-[#03AC0E] rounded-full" aria-hidden="true" />
            <h2 id="amazon-category-heading" class="text-base sm:text-lg lg:text-xl font-bold text-gray-900 tracking-tight">
              Belanja Berdasarkan Kategori
            </h2>
            <span class="hidden md:inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 bg-[#F0FBF2] px-2.5 py-0.5 rounded-full border border-[#D5EED9]">
              Hardware Resmi
            </span>
          </div>

          <NuxtLink
            to="/category/kamera-cctv"
            class="text-xs sm:text-sm font-bold text-[#03AC0E] hover:underline flex items-center gap-1 group"
          >
            Lihat Semua Kategori
            <UIcon name="i-heroicons-arrow-right-20-solid" class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </NuxtLink>
        </div>

        <!-- 8 Columns Grid of Real Hardware Products (Amazon Style) -->
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 sm:gap-4 lg:gap-5">
          <NuxtLink
            v-for="cat in categories"
            :key="cat.name"
            :to="cat.link"
            class="flex flex-col items-center text-center group cursor-pointer"
          >
            <!-- Product Image Frame (Clean Amazon Squircle Style) -->
            <div class="w-full aspect-square rounded-xl bg-[#F8F9FA] p-3 border border-gray-200/80 group-hover:border-[#03AC0E] group-hover:bg-[#F0FBF2]/30 group-hover:shadow-sm transition-all duration-300 flex items-center justify-center overflow-hidden relative">
              <img
                :src="cat.image"
                :alt="cat.name"
                class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                loading="lazy"
              />
              
              <!-- Category Label -->
              <span class="absolute top-1.5 right-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded bg-white/90 text-gray-700 border border-gray-200/60 shadow-2xs group-hover:bg-[#03AC0E] group-hover:text-white group-hover:border-[#03AC0E] transition-colors">
                {{ cat.name }}
              </span>
            </div>

            <!-- Subtitle -->
            <span class="text-xs sm:text-[13px] font-medium text-gray-500 mt-2.5 line-clamp-1">
              {{ cat.sub }}
            </span>
          </NuxtLink>
        </div>

        <!-- Bottom Quick Filter & Trust Bar (Amazon Style) -->
        <div class="mt-6 pt-4 border-t border-gray-100 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div class="flex flex-wrap items-center gap-2">
            <span class="font-bold text-gray-400 mr-1 flex items-center gap-1 text-[11px]">
              <UIcon name="i-heroicons-magnifying-glass" class="w-3.5 h-3.5 text-gray-400" />
              Sering Dicari:
            </span>
            <NuxtLink
              v-for="s in popularSearches"
              :key="s.label"
              :to="s.link"
              class="text-[11px] font-medium text-gray-700 hover:text-[#03AC0E] bg-gray-100 hover:bg-[#F0FBF2] hover:border-[#D5EED9] px-2.5 py-1 rounded-full border border-gray-200/70 transition-all hover:scale-105"
            >
              {{ s.label }}
            </NuxtLink>
          </div>

          <div class="hidden lg:flex items-center gap-4 text-[11px] text-gray-500 font-medium">
            <span class="flex items-center gap-1.5 text-[#03AC0E] font-semibold">
              <UIcon name="i-heroicons-shield-check" class="w-4 h-4" />
              Garansi distributor resmi
            </span>
            <span class="text-gray-300">&bull;</span>
            <span class="flex items-center gap-1.5 text-gray-600 font-semibold">
              <UIcon name="i-heroicons-truck" class="w-4 h-4 text-[#03AC0E]" />
              Pengiriman Cepat Seluruh Wilayah Bandung
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>