<script setup lang="ts">
/**
 * Component: HomeQuadrantGrid
 * Philosophy: Amazon-style 2x2 Quadrant Navigation + Tokopedia Forest Green & Trust
 * Purpose: Instant scanning of high-intent security hardware and services without cognitive load.
 */

const cameraCategories = [
  {
    title: 'Indoor Dome',
    desc: 'Untuk Rumah & Ruko',
    image: '/images/showcase/dome.jpg',
    link: '/category/kamera-cctv?type=indoor'
  },
  {
    title: 'Outdoor Bullet',
    desc: 'Tahan Air & Cuaca',
    image: '/images/showcase/bullet.jpg',
    link: '/category/kamera-cctv?type=outdoor'
  },
  {
    title: 'Smart PTZ WiFi',
    desc: 'Bisa Putar 360°',
    image: '/images/showcase/ptz.jpg',
    link: '/category/kamera-cctv?type=ptz'
  },
  {
    title: 'ColorVu 24 Jam',
    desc: 'Malam Berwarna',
    image: '/images/showcase/colorvu.jpg',
    link: '/category/kamera-cctv?type=colorvu'
  }
]

const storageComponents = [
  {
    title: 'DVR / NVR',
    desc: 'Perekam 4-16 CH',
    image: '/images/showcase/dvr.jpg',
    link: '/category/dvr-nvr'
  },
  {
    title: 'Harddisk Khusus',
    desc: 'Surveillance 24/7',
    image: '/images/showcase/harddrive.jpg',
    link: '/category/storage'
  },
  {
    title: 'IP Camera PoE',
    desc: 'Kabel Praktis',
    image: '/images/showcase/bullet.jpg',
    link: '/category/kamera-cctv?spec=poe'
  },
  {
    title: 'Wireless Camera',
    desc: 'Tanpa DVR',
    image: '/images/showcase/ptz.jpg',
    link: '/category/kamera-cctv?type=wireless'
  }
]

const packageHighlights = [
  { name: 'Rumah (2 Cam)', tag: 'Mulai 1.2 Juta' },
  { name: 'Ruko (4 Cam)', tag: 'Terlaris' },
  { name: 'Usaha (8 Cam)', tag: 'Komplit' }
]
</script>

<template>
  <section class="w-full my-6 sm:my-8" aria-label="Eksplorasi Katalog Unggulan">
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      
      <!-- Grid 4 Kolom Amazon (Desktop: 4 Cards, Tablet: 2 Cards, Mobile: 1-2 Cards) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-5">
        
        <!-- CARD 1: Tipe Kamera CCTV (Amazon 2x2 Grid) -->
        <div class="bg-white rounded-2xl p-4 sm:p-5 border border-gray-200/90 shadow-xs flex flex-col justify-between hover:border-green-500/50 transition-colors">
          <div>
            <h3 class="text-base font-bold text-gray-900 tracking-tight mb-1">
              Pilihan Kamera CCTV
            </h3>
            <p class="text-xs text-gray-500 mb-3.5">
              Sesuaikan dengan posisi pasang
            </p>

            <div class="grid grid-cols-2 gap-2.5">
              <NuxtLink
                v-for="item in cameraCategories"
                :key="item.title"
                :to="item.link"
                class="group flex flex-col focus:outline-none"
              >
                <div class="aspect-square w-full rounded-xl bg-gray-50 border border-gray-100 overflow-hidden relative mb-1.5 p-1">
                  <NuxtImg
                    :src="item.image"
                    :alt="item.title"
                    class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                    width="200"
                    height="200"
                    loading="lazy"
                    format="webp"
                    quality="80"
                  />
                </div>
                <span class="text-xs font-semibold text-gray-800 leading-snug group-hover:text-[#03AC0E] transition-colors truncate">
                  {{ item.title }}
                </span>
                <span class="text-[11px] text-gray-400 leading-none truncate">
                  {{ item.desc }}
                </span>
              </NuxtLink>
            </div>
          </div>

          <div class="pt-3 mt-3 border-t border-gray-100">
            <NuxtLink
              to="/category/kamera-cctv"
              class="inline-flex items-center gap-1 text-xs font-bold text-[#03AC0E] hover:text-[#028C0B] transition-colors"
            >
              Lihat Semua Kamera
              <UIcon name="i-heroicons-arrow-small-right" class="w-4 h-4" />
            </NuxtLink>
          </div>
        </div>

        <!-- CARD 2: Paket Lengkap Siap Pasang (Amazon Hero Deal Focus) -->
        <div class="bg-white rounded-2xl p-4 sm:p-5 border border-gray-200/90 shadow-xs flex flex-col justify-between hover:border-green-500/50 transition-colors">
          <div>
            <div class="flex items-center justify-between mb-1">
              <h3 class="text-base font-bold text-gray-900 tracking-tight">
                Paket Siap Pasang
              </h3>
              <span class="text-[10px] font-bold text-[#D62828] bg-[#FFF0F2] border border-[#FCD5D8] px-2 py-0.5 rounded-full">
                Hemat s.d 25%
              </span>
            </div>
            <p class="text-xs text-gray-500 mb-3.5">
              Termasuk kamera, DVR, kabel &amp; setting
            </p>

            <NuxtLink
              to="/category/paket-cctv"
              class="block group focus:outline-none"
            >
              <div class="aspect-[4/3] w-full rounded-xl bg-gray-50 border border-gray-100 overflow-hidden relative mb-3 p-2 flex items-center justify-center">
                <NuxtImg
                  src="/images/showcase/bundle.jpg"
                  alt="Paket CCTV Komplit"
                  class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                  width="400"
                  height="300"
                  loading="lazy"
                  format="webp"
                  quality="85"
                />
              </div>

              <!-- Quick Tag Options -->
              <div class="flex flex-wrap gap-1.5 mb-2">
                <span
                  v-for="pkg in packageHighlights"
                  :key="pkg.name"
                  class="text-[11px] font-medium bg-gray-50 text-gray-700 px-2 py-0.5 rounded-md border border-gray-200/60"
                >
                  {{ pkg.name }}
                </span>
              </div>
            </NuxtLink>
          </div>

          <div class="pt-3 mt-1 border-t border-gray-100">
            <NuxtLink
              to="/category/paket-cctv"
              class="inline-flex items-center gap-1 text-xs font-bold text-[#03AC0E] hover:text-[#028C0B] transition-colors"
            >
              Bandingkan Paket CCTV
              <UIcon name="i-heroicons-arrow-small-right" class="w-4 h-4" />
            </NuxtLink>
          </div>
        </div>

        <!-- CARD 3: Perekam & Komponen (Amazon 2x2 Grid) -->
        <div class="bg-white rounded-2xl p-4 sm:p-5 border border-gray-200/90 shadow-xs flex flex-col justify-between hover:border-green-500/50 transition-colors">
          <div>
            <h3 class="text-base font-bold text-gray-900 tracking-tight mb-1">
              Perekam &amp; Storage
            </h3>
            <p class="text-xs text-gray-500 mb-3.5">
              DVR, NVR, &amp; Harddisk resmi
            </p>

            <div class="grid grid-cols-2 gap-2.5">
              <NuxtLink
                v-for="item in storageComponents"
                :key="item.title"
                :to="item.link"
                class="group flex flex-col focus:outline-none"
              >
                <div class="aspect-square w-full rounded-xl bg-gray-50 border border-gray-100 overflow-hidden relative mb-1.5 p-1">
                  <NuxtImg
                    :src="item.image"
                    :alt="item.title"
                    class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                    width="200"
                    height="200"
                    loading="lazy"
                    format="webp"
                    quality="80"
                  />
                </div>
                <span class="text-xs font-semibold text-gray-800 leading-snug group-hover:text-[#03AC0E] transition-colors truncate">
                  {{ item.title }}
                </span>
                <span class="text-[11px] text-gray-400 leading-none truncate">
                  {{ item.desc }}
                </span>
              </NuxtLink>
            </div>
          </div>

          <div class="pt-3 mt-3 border-t border-gray-100">
            <NuxtLink
              to="/category/storage"
              class="inline-flex items-center gap-1 text-xs font-bold text-[#03AC0E] hover:text-[#028C0B] transition-colors"
            >
              Eksplor Komponen &amp; Storage
              <UIcon name="i-heroicons-arrow-small-right" class="w-4 h-4" />
            </NuxtLink>
          </div>
        </div>

        <!-- CARD 4: Layanan Teknisi Siap Pasang (High Conversion Trust Card) -->
        <div class="bg-gradient-to-b from-[#F0FBF2] via-white to-white rounded-2xl p-4 sm:p-5 border border-[#D5EED9] shadow-xs flex flex-col justify-between hover:border-[#03AC0E] transition-colors">
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <span class="inline-flex items-center gap-1 text-[10px] font-bold text-[#03AC0E] bg-white px-2 py-0.5 rounded-full border border-[#D5EED9]">
                <UIcon name="i-heroicons-check-badge" class="w-3.5 h-3.5" /> Teknisi Resmi
              </span>
              <span class="text-[11px] text-gray-400 font-medium">Bandung &amp; Cimahi</span>
            </div>

            <h3 class="text-base font-bold text-gray-900 tracking-tight mb-2">
              Jasa Pasang &amp; Servis
            </h3>

            <div class="aspect-[16/10] w-full rounded-xl overflow-hidden relative mb-3 border border-[#E1F5E4]">
              <NuxtImg
                src="/images/showcase/technician.jpg"
                alt="Teknisi PasarCCTV Berpengalaman"
                class="w-full h-full object-cover object-top"
                width="400"
                height="250"
                loading="lazy"
                format="webp"
                quality="85"
              />
            </div>

            <p class="text-xs text-gray-600 leading-relaxed">
              Teknisi siap datang ke lokasi. Garansi resmi pengerjaan 1 tahun &amp; panduan setting HP gratis.
            </p>
          </div>

          <div class="pt-3 mt-2">
            <NuxtLink
              to="/layanan/booking"
              class="w-full inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-[#03AC0E] hover:bg-[#028C0B] active:scale-98 text-white font-bold text-xs shadow-xs transition-all"
            >
              Jadwalkan Teknisi
              <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" />
            </NuxtLink>
          </div>
        </div>

      </div>

    </div>
  </section>
</template>
