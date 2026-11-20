<script setup lang="ts">
/**
 * Component: HomeBigDealEvent
 * Inspired by: Amazon Prime Big Deal Days / Featured Deals Event Banner (as requested by User)
 * Adapted to: Tokopedia Forest Green Trust + Industrial Security Hardware Focus
 * Target: Field technicians, contractors, shop owners, looking for high-spec deals with warranty.
 */
import { Swiper, SwiperSlide } from "swiper/vue";
import { Navigation, A11y, FreeMode } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/free-mode";

const modules = [Navigation, A11y, FreeMode];

const featuredDeals = [
  {
    uuid: 'deal-tiandy-5mp',
    slug: 'tiandy-super-starlight-5mp-poe-ip-camera',
    brand: 'Tiandy',
    title: 'Super Starlight 5MP PoE IP Camera',
    image: '/images/showcase/colorvu.jpg',
    price: 585000,
    original_price: 780000,
    discount: 25,
    specs: ['5MP 3K', 'PoE 48V', 'Starlight 0.002 Lux', 'IP67 Metal'],
    badge: 'Limited Time Deal',
    sold: 142,
    rating: 4.9
  },
  {
    uuid: 'deal-dahua-8cam',
    slug: 'paket-cctv-dahua-8-titik-4k-audio-mic-pasang',
    brand: 'Dahua',
    title: 'Paket CCTV 8 Titik 4K Audio Mic + Pasang',
    image: '/images/showcase/bundle.jpg',
    price: 4350000,
    original_price: 5800000,
    discount: 25,
    specs: ['8 Kamera 4K', 'DVR 8CH AI', 'HDD 2TB', 'Free Pasang'],
    badge: 'Paket Komplit',
    sold: 88,
    rating: 5.0
  },
  {
    uuid: 'deal-hikvision-colorvu',
    slug: 'hikvision-colorvu-4mp-dome-kamera-audio-mic',
    brand: 'Hikvision',
    title: 'ColorVu 4MP Full Color Night Vision',
    image: '/images/showcase/bullet.jpg',
    price: 520000,
    original_price: 650000,
    discount: 20,
    specs: ['4MP Quad HD', '24/7 Berwarna', 'Built-in Mic', 'H.265+'],
    badge: 'Best Seller',
    sold: 215,
    rating: 4.9
  },
  {
    uuid: 'deal-wd-purple-4tb',
    slug: 'harddisk-cctv-wd-purple-4tb-surveillance',
    brand: 'WD Purple',
    title: 'Surveillance 4TB Internal Hard Drive 24/7',
    image: '/images/showcase/harddrive.jpg',
    price: 1450000,
    original_price: 1770000,
    discount: 18,
    specs: ['4TB SATA 6Gb/s', 'AllFrame AI', 'Rekam 24/7', 'Garansi 3 Thn'],
    badge: 'Khusus CCTV',
    sold: 320,
    rating: 5.0
  },
  {
    uuid: 'deal-ptz-wifi',
    slug: 'kamera-cctv-ptz-outdoor-wifi-dual-lens-360',
    brand: 'Ezviz / Tapo',
    title: 'Smart PTZ Outdoor WiFi Dual Lens 360°',
    image: '/images/showcase/ptz.jpg',
    price: 4250000,
    original_price: 545000,
    discount: 22,
    specs: ['Dual Lens 360°', 'Auto Tracking', 'Alarm Sirine', 'MicroSD Slot'],
    badge: 'Wireless Praktis',
    sold: 175,
    rating: 4.8
  },
  {
    uuid: 'deal-indoor-dome',
    slug: 'kamera-cctv-indoor-dome-2mp-audio-recording',
    brand: 'Dahua',
    title: 'Indoor Dome Camera 2MP Audio Mic',
    image: '/images/showcase/dome.jpg',
    price: 245000,
    original_price: 290000,
    discount: 15,
    specs: ['2MP 1080P', 'Audio Mic', 'Plafon Ramping', 'Smart IR 20M'],
    badge: 'Hemat Budget',
    sold: 410,
    rating: 4.9
  }
];

const priceFormatter = new Intl.NumberFormat("id-ID");
const formatPrice = (val: number) => `Rp ${priceFormatter.format(val)}`;
</script>

<template>
  <section class="w-full my-8 sm:my-10" aria-label="Iklan Event Mega Deal Keamanan">
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      
      <!-- ══ 1. AMAZON EVENT HERO BANNER (Big Deal Days) ══ -->
      <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#003B15] via-[#025E23] to-[#03AC0E] text-white p-6 sm:p-8 lg:p-10 shadow-sm border border-[#028C0B]/40">
        <!-- Background Subtle Circuit / Grid Accent -->
        <div class="pointer-events-none absolute inset-0 opacity-10 bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px]" />

        <div class="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div class="max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 backdrop-blur-xs text-xs font-bold text-white border border-white/20 mb-3">
              <span class="w-2 h-2 rounded-full bg-[#FFD814] animate-pulse" />
              BIG DEAL DAYS · SPESIAL TEKNISI &amp; DISTRIBUTOR 2026
            </div>
            
            <h2 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight leading-tight">
              Super Deal Keamanan &amp; CCTV Bandung
            </h2>
            
            <p class="text-xs sm:text-sm text-green-100/90 mt-2 leading-relaxed">
              Diskon hingga 40% untuk kamera 5MP Starlight, DVR/NVR AI, dan Harddisk pengawasan 24/7. 
              Semua unit bergaransi distributor resmi + gratis konsultasi teknisi.
            </p>

            <div class="flex flex-wrap items-center gap-4 mt-4 text-xs font-semibold text-green-100">
              <span class="flex items-center gap-1">
                <UIcon name="i-heroicons-shield-check" class="w-4 h-4 text-[#FFD814]" />
                Garansi Resmi 1-2 Tahun
              </span>
              <span class="flex items-center gap-1">
                <UIcon name="i-heroicons-truck" class="w-4 h-4 text-[#FFD814]" />
                Sameday Delivery Bandung
              </span>
              <span class="flex items-center gap-1">
                <UIcon name="i-heroicons-wrench-screwdriver" class="w-4 h-4 text-[#FFD814]" />
                Bisa Sekalian Pasang
              </span>
            </div>
          </div>

          <!-- Right Action Box -->
          <div class="flex flex-col sm:flex-row lg:flex-col gap-3 shrink-0">
            <NuxtLink
              to="/category/paket-cctv"
              class="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-[#FFD814] hover:bg-[#F7CA00] active:scale-98 text-gray-900 font-extrabold text-sm shadow-sm transition-all"
            >
              Klaim Promo Paket
              <UIcon name="i-heroicons-arrow-right" class="w-4 h-4 stroke-[2.5]" />
            </NuxtLink>

            <NuxtLink
              to="/search?sort=discount"
              class="inline-flex items-center justify-center gap-1.5 px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs border border-white/20 transition-colors"
            >
              Lihat Semua Diskon
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- ══ 2. FEATURED DEALS CAROUSEL (Amazon Layout) ══ -->
      <div class="mt-4 bg-white rounded-2xl border border-gray-200 p-4 sm:p-6 shadow-xs">
        
        <!-- Header Row -->
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-100">
          <div class="flex items-center gap-2">
            <span class="w-1.5 h-5 bg-[#D62828] rounded-full" />
            <h3 class="text-base sm:text-lg font-bold text-gray-900 tracking-tight">
              Featured Deals — Spesifikasi Hardware Pilihan
            </h3>
          </div>

          <!-- Slider Nav Controls -->
          <div class="flex items-center gap-2">
            <button
              aria-label="Slide Sebelumnya"
              class="deal-prev w-8 h-8 rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-[#03AC0E] hover:text-white hover:border-[#03AC0E] disabled:opacity-30 transition-all flex items-center justify-center shadow-xs"
            >
              <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
            </button>
            <button
              aria-label="Slide Selanjutnya"
              class="deal-next w-8 h-8 rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-[#03AC0E] hover:text-white hover:border-[#03AC0E] disabled:opacity-30 transition-all flex items-center justify-center shadow-xs"
            >
              <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Deals Swiper -->
        <Swiper
          :modules="modules"
          :navigation="{ prevEl: '.deal-prev', nextEl: '.deal-next' }"
          :free-mode="{ enabled: true, sticky: false }"
          :slides-per-view="1.8"
          :space-between="12"
          :breakpoints="{
            480: { slidesPerView: 2.2, spaceBetween: 12 },
            640: { slidesPerView: 3.2, spaceBetween: 14 },
            768: { slidesPerView: 4.2, spaceBetween: 16 },
            1024: { slidesPerView: 5.2, spaceBetween: 16 },
            1280: { slidesPerView: 6, spaceBetween: 18 },
          }"
          class="!py-1"
        >
          <SwiperSlide v-for="deal in featuredDeals" :key="deal.uuid">
            <div class="group h-full flex flex-col bg-white rounded-xl border border-gray-100 hover:border-[#03AC0E] p-3 transition-all">
              
              <!-- Image Container -->
              <NuxtLink :to="`/product/${deal.slug}`" class="block aspect-square w-full rounded-lg bg-gray-50 overflow-hidden mb-2.5 p-2">
                <NuxtImg
                  :src="deal.image"
                  :alt="deal.title"
                  class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                  width="220"
                  height="220"
                  loading="lazy"
                  format="webp"
                  quality="85"
                />
              </NuxtLink>

              <!-- Deal Badge (Amazon Style) -->
              <div class="flex items-center gap-1.5 mb-1.5">
                <span class="inline-flex items-center justify-center bg-[#CC0C39] text-white text-[10px] font-extrabold px-1.5 py-0.5 rounded leading-none">
                  {{ deal.discount }}% off
                </span>
                <span class="text-[#CC0C39] text-[11px] font-bold leading-none truncate">
                  {{ deal.badge }}
                </span>
              </div>

              <!-- Price Lockup -->
              <div class="flex items-baseline gap-1.5 flex-wrap mb-1">
                <p class="text-sm sm:text-base font-extrabold text-gray-900 tracking-tight">
                  {{ formatPrice(deal.price) }}
                </p>
                <span class="text-[10px] text-gray-400 line-through">
                  {{ formatPrice(deal.original_price) }}
                </span>
              </div>

              <!-- Brand & Title -->
              <NuxtLink :to="`/product/${deal.slug}`" class="hover:text-[#03AC0E] transition-colors">
                <span class="text-[10px] uppercase font-bold text-gray-400 block">{{ deal.brand }}</span>
                <h4 class="text-xs font-semibold text-gray-800 line-clamp-2 leading-snug">
                  {{ deal.title }}
                </h4>
              </NuxtLink>

              <!-- Technical Specs Matrix Pills -->
              <div class="mt-2 flex flex-wrap gap-1">
                <span
                  v-for="spec in deal.specs.slice(0, 2)"
                  :key="spec"
                  class="text-[9px] font-semibold bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded"
                >
                  {{ spec }}
                </span>
              </div>

              <!-- Social Proof -->
              <div class="mt-auto pt-2 flex items-center justify-between text-[10px] text-gray-500">
                <span class="inline-flex items-center gap-0.5 text-gray-700 font-semibold">
                  <UIcon name="i-heroicons-star-solid" class="w-3 h-3 text-[#FFB703]" />
                  {{ deal.rating }}
                </span>
                <span>Terjual {{ deal.sold }}</span>
              </div>

            </div>
          </SwiperSlide>
        </Swiper>

      </div>

    </div>
  </section>
</template>

<style scoped>
:deep(.swiper-slide) {
  height: auto !important;
  display: flex !important;
}
:deep(.swiper-slide > *) {
  width: 100% !important;
}
</style>
