<script setup lang="ts">
/**
 * Component: HomeBanner (Professional & Unified Style)
 * Philosophy: Clean, Professional, Minimal Color Palette
 * Focus: High Information Density, Brand Consistency
 */

const categories = [
  {
    name: 'Paket CCTV',
    icon: 'i-heroicons-rectangle-group',
    link: '/category/paket-cctv'
  },
  {
    name: 'Kamera CCTV',
    icon: 'i-heroicons-video-camera',
    link: '/category/kamera-cctv'
  },
  {
    name: 'DVR / NVR',
    icon: 'i-heroicons-server-stack',
    link: '/category/dvr-nvr'
  },
  {
    name: 'Hard Drive',
    icon: 'i-heroicons-cpu-chip',
    link: '/category/storage'
  },
  {
    name: 'Layanan Jasa',
    icon: 'i-heroicons-wrench-screwdriver',
    link: '/layanan/booking'
  },
  {
    name: 'Aksesoris',
    icon: 'i-heroicons-cog-6-tooth',
    link: '/category/aksesoris'
  },
  {
    name: 'Promo',
    icon: 'i-heroicons-ticket',
    link: '/promo'
  },
  {
    name: 'Bantuan',
    icon: 'i-heroicons-question-mark-circle',
    link: '/help'
  }
]

const highlights = [
  {
    title: 'Instalasi Ahli',
    subtitle: 'Garansi 1 Tahun',
    image: 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?q=80&w=400&auto=format&fit=crop',
    link: '/layanan/booking',
    color: 'from-gray-900/80 to-black/95' // Unified dark professional theme
  },
  {
    title: 'Cek Keamanan',
    subtitle: 'Konsultasi Gratis',
    image: 'https://images.unsplash.com/photo-1521791136064-7986c29596ad?q=80&w=400&auto=format&fit=crop',
    link: '/contact',
    color: 'from-[#03AC0E]/80 to-[#025a07]/95' // Brand green theme
  }
]
</script>

<template>
  <section class="w-full bg-transparent" aria-labelledby="home-banner-unified-heading">
    <h2 id="home-banner-unified-heading" class="sr-only">Navigasi Utama PasarCctv</h2>
    
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      <div class="flex flex-col lg:flex-row gap-4 lg:gap-6">
        
        <!-- Quick Categories (Unified Style) -->
        <nav class="lg:flex-1 bg-white rounded-xl p-4 lg:p-6 border border-gray-100 shadow-sm" aria-label="Kategori">
          <div class="grid grid-cols-4 sm:grid-cols-4 lg:grid-cols-4 gap-y-6 gap-x-2">
            <NuxtLink
              v-for="item in categories"
              :key="item.name"
              :to="item.link"
              class="flex flex-col items-center gap-2 group"
            >
              <!-- Icon Container: Unified Neutral Gray with Brand Hover -->
              <div 
                class="w-12 h-12 lg:w-14 lg:h-14 flex items-center justify-center rounded-2xl bg-gray-50 border border-gray-100 transition-all duration-300 group-hover:bg-green-50 group-hover:border-green-100 group-hover:scale-105"
              >
                <UIcon 
                  :name="item.icon" 
                  class="w-6 h-6 lg:w-7 lg:h-7 text-gray-500 group-hover:text-[#03AC0E] transition-colors" 
                  aria-hidden="true" 
                />
              </div>
              <span class="text-[10px] lg:text-[11px] font-black text-gray-800 tracking-tight text-center leading-tight group-hover:text-[#03AC0E] transition-colors">
                {{ item.name }}
              </span>
            </NuxtLink>
          </div>
        </nav>

        <!-- Highlights (Professional Banners) -->
        <div class="flex lg:w-[400px] gap-3 lg:flex-col">
          <NuxtLink
            v-for="card in highlights"
            :key="card.title"
            :to="card.link"
            class="flex-1 relative group h-28 lg:h-full rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-500"
          >
            <img 
              :src="card.image" 
              :alt="card.title" 
              class="absolute inset-0 w-full h-full object-cover grayscale-[0.5] group-hover:grayscale-0 transition-all duration-700"
            />
            <div class="absolute inset-0 bg-gradient-to-br" :class="card.color"></div>
            
            <div class="relative h-full p-4 lg:p-6 flex flex-col justify-center text-white">
              <h3 class="text-sm lg:text-lg font-black tracking-tighter leading-tight uppercase italic">
                {{ card.title }}
              </h3>
              <p class="text-[9px] lg:text-[11px] font-bold text-white/80 uppercase tracking-widest mt-1">
                {{ card.subtitle }}
              </p>
              
              <div class="mt-3 flex items-center gap-1 group/btn">
                <span class="text-[8px] lg:text-[10px] font-black uppercase tracking-widest text-white/60 group-hover:text-white transition-colors">
                  Detail Layanan
                </span>
                <UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-white/40 group-hover:text-white transition-all group-hover:translate-x-0.5" />
              </div>
            </div>
          </NuxtLink>
        </div>

      </div>
    </div>
  </section>
</template>

<style scoped>
.rounded-3xl {
  border-radius: 1.5rem;
}
</style>
