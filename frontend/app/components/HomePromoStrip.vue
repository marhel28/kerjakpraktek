<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import BannerImageLink from '~/components/banner/BannerImageLink.vue'

interface BannerItem {
  uuid: string
  image_url: string
  target_url?: string | null
  alt_text?: string
  order?: number
}

interface BannerSectionData {
  uuid: string
  identifier: string
  title: string
  mode: string
  is_active: boolean
  items: BannerItem[]
}

const props = withDefaults(
  defineProps<{
    identifier?: string
  }>(),
  {
    identifier: 'home:promo-strip',
  }
)

// Fetch data dari backend image-sections melalui BFF Nuxt
const { data: sectionData, pending } = await useFetch<BannerSectionData>(
  () => `/api/banner/${encodeURIComponent(props.identifier)}`,
  {
    key: `banner-${props.identifier}`,
    transform: (res: any) => res?.data ?? null,
    server: true,
  }
)

const activeIndex = ref(0)
let timer: any = null

const items = computed(() => {
  if (sectionData.value && sectionData.value.items && sectionData.value.items.length > 0) {
    return sectionData.value.items
  }
  // Fallback lokal jika database/koneksi kosong
  return [
    {
      uuid: 'fallback-1',
      image_url: '/images/promo_exclusive_banner.jpg',
      target_url: '/promo',
      alt_text: 'Jangan Lewatkan Penawaran Eksklusif Untuk Produk Access Control & CCTV'
    }
  ]
})

const currentBanner = computed(() => items.value[activeIndex.value] || items.value[0])

const nextSlide = () => {
  if (items.value.length > 1) {
    activeIndex.value = (activeIndex.value + 1) % items.value.length
  }
}

const prevSlide = () => {
  if (items.value.length > 1) {
    activeIndex.value = (activeIndex.value - 1 + items.value.length) % items.value.length
  }
}

onMounted(() => {
  if (items.value.length > 1) {
    timer = setInterval(nextSlide, 6000)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <section class="w-full" aria-label="Penawaran Eksklusif Promo Produk">
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      
      <!-- Container Promo Strip -->
      <div class="relative w-full rounded-2xl md:rounded-3xl overflow-hidden shadow-sm border border-gray-200/80 bg-white group">
        
        <!-- Link Wrapper -->
        <BannerImageLink
          :target-url="currentBanner?.target_url || '/promo'"
          :image-url="currentBanner?.image_url || '/images/promo_exclusive_banner.jpg'"
          :alt-text="currentBanner?.alt_text || 'Penawaran Eksklusif Produk'"
          aspect-ratio-class="aspect-[21/9] sm:aspect-[24/9] md:aspect-[32/10] lg:aspect-[1920/540]"
        >
          <!-- Interactive Content Overlay (Desain Eksklusif Tegas Amazon Style) -->
          <div class="absolute inset-0 bg-gradient-to-r from-black/60 via-black/20 to-transparent flex items-center p-5 sm:p-8 md:p-12 lg:p-14 pointer-events-none">
            <div class="max-w-xl md:max-w-2xl text-white space-y-2 sm:space-y-3 md:space-y-4 pointer-events-auto">
              
              <!-- Badge Kategori Promo -->
              <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/15 backdrop-blur-md border border-white/25 text-white text-[11px] sm:text-xs font-bold tracking-wide uppercase">
                <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                Penawaran Spesial Terbatas
              </div>

              <!-- Judul Utama (Sesuai Referensi Gambar) -->
              <h3 class="text-lg sm:text-2xl md:text-3xl lg:text-4xl font-extrabold tracking-tight text-white leading-tight drop-shadow-sm uppercase">
                JANGAN LEWATKAN PENAWARAN EKSKLUSIF UNTUK PRODUK INI!
              </h3>

              <!-- Pill Tombol Subheading Merah (Sesuai Referensi Gambar) -->
              <div class="pt-1">
                <div class="inline-block px-4 py-1.5 sm:py-2 rounded-full bg-[#E51E2B] text-white font-bold text-xs sm:text-sm md:text-base shadow-md border border-white/20">
                  Hanya sekarang, dapatkan promo menarik untuk Anda!
                </div>
              </div>

              <!-- Fitur Produk Ringkas & CTA -->
              <div class="pt-2 flex flex-wrap items-center gap-3">
                <span class="inline-flex items-center gap-1 text-[11px] sm:text-xs font-semibold text-white/90 bg-black/40 px-2.5 py-1 rounded-lg backdrop-blur-sm">
                  <UIcon name="i-heroicons-shield-check" class="w-3.5 h-3.5 text-[#03AC0E]" />
                  Garansi Resmi 2 Tahun
                </span>
                <span class="inline-flex items-center gap-1 text-[11px] sm:text-xs font-semibold text-white/90 bg-black/40 px-2.5 py-1 rounded-lg backdrop-blur-sm">
                  <UIcon name="i-heroicons-wrench-screwdriver" class="w-3.5 h-3.5 text-amber-400" />
                  Gratis Setting & Training
                </span>
              </div>
            </div>
          </div>

          <!-- Hotspot Pointer Tooltips Overlay (Dekorasi Spesifikasi Perangkat ala Gambar Referensi) -->
          <div class="hidden lg:block absolute inset-0 pointer-events-none">
            <!-- Pointer 1: Access Control Fingerprint -->
            <div class="absolute top-[32%] right-[32%] pointer-events-auto group/pin">
              <div class="relative flex items-center">
                <div class="w-3 h-3 rounded-full bg-white ring-4 ring-cyan-400/60 animate-ping absolute" />
                <div class="w-3 h-3 rounded-full bg-cyan-500 ring-2 ring-white relative z-10" />
                <div class="ml-2 px-2.5 py-1 rounded-md bg-black/75 backdrop-blur-md border border-white/20 text-[10px] font-bold text-white shadow-lg whitespace-nowrap opacity-90 group-hover/pin:opacity-100 transition-opacity">
                  Hikvision Biometric DS-K1A802F
                </div>
              </div>
            </div>

            <!-- Pointer 2: Face Recognition Terminal -->
            <div class="absolute top-[18%] right-[20%] pointer-events-auto group/pin">
              <div class="relative flex items-center">
                <div class="w-3 h-3 rounded-full bg-cyan-500 ring-2 ring-white relative z-10" />
                <div class="ml-2 px-2.5 py-1 rounded-md bg-black/75 backdrop-blur-md border border-white/20 text-[10px] font-bold text-white shadow-lg whitespace-nowrap opacity-90 group-hover/pin:opacity-100 transition-opacity">
                  Face Terminal DS-K1T606MF
                </div>
              </div>
            </div>

            <!-- Pointer 3: Dome Camera -->
            <div class="absolute bottom-[28%] right-[10%] pointer-events-auto group/pin">
              <div class="relative flex items-center">
                <div class="w-3 h-3 rounded-full bg-cyan-500 ring-2 ring-white relative z-10" />
                <div class="ml-2 px-2.5 py-1 rounded-md bg-black/75 backdrop-blur-md border border-white/20 text-[10px] font-bold text-white shadow-lg whitespace-nowrap opacity-90 group-hover/pin:opacity-100 transition-opacity">
                  IP Dome 5MP Ultra HD
                </div>
              </div>
            </div>
          </div>
        </BannerImageLink>

        <!-- Slider Controls jika item > 1 dari Admin -->
        <template v-if="items.length > 1">
          <button
            @click.stop="prevSlide"
            class="absolute left-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-white/80 hover:bg-white text-gray-800 flex items-center justify-center shadow-md transition-all opacity-0 group-hover:opacity-100 focus:outline-none"
            aria-label="Banner Sebelumnya"
          >
            <UIcon name="i-heroicons-chevron-left-20-solid" class="w-5 h-5" />
          </button>
          <button
            @click.stop="nextSlide"
            class="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-white/80 hover:bg-white text-gray-800 flex items-center justify-center shadow-md transition-all opacity-0 group-hover:opacity-100 focus:outline-none"
            aria-label="Banner Selanjutnya"
          >
            <UIcon name="i-heroicons-chevron-right-20-solid" class="w-5 h-5" />
          </button>

          <!-- Dots Indicator -->
          <div class="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-1.5 z-10">
            <button
              v-for="(_, idx) in items"
              :key="idx"
              @click.stop="activeIndex = idx"
              class="h-1.5 rounded-full transition-all"
              :class="activeIndex === idx ? 'w-6 bg-white' : 'w-2 bg-white/50'"
              :aria-label="`Pilih slide ${idx + 1}`"
            />
          </div>
        </template>

      </div>
    </div>
  </section>
</template>
