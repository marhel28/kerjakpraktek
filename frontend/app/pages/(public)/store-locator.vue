<script setup lang="ts">
import { ref, shallowRef, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

definePageMeta({ ssr: false })

useSeoMeta({
  title: 'Lokasi Toko & Showroom CCTV | PasarCCTV',
  description: 'Kunjungi Showroom PasarCCTV Bogor. Coba langsung kamera CCTV, konsultasi teknis keamanan gratis, dan ambil pesanan di toko.',
  ogTitle: 'Lokasi Showroom PasarCCTV',
  ogDescription: 'Temukan lokasi showroom PasarCCTV. Panduan rute Google Maps, Waze, dan info jam operasional.',
  ogType: 'website'
})

useHead({
  link: [{ rel: 'canonical', href: 'https://pasarcctv.com/store-locator' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ElectronicsStore',
      name: 'PasarCCTV Showroom & Service Center',
      description: 'Pusat penjualan, uji coba unit, dan instalasi perangkat keamanan CCTV.',
      url: 'https://pasarcctv.com',
      telephone: '+6282117779003',
      address: {
        '@type': 'PostalAddress',
        streetAddress: 'Jl. Tumenggung Wiradireja No.29A',
        addressLocality: 'Bogor',
        addressRegion: 'Jawa Barat',
        postalCode: '16155',
        addressCountry: 'ID'
      },
      geo: {
        '@type': 'GeoCoordinates',
        latitude: -6.5510,
        longitude: 106.8185
      },
      openingHoursSpecification: [
        { '@type': 'OpeningHoursSpecification', dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], opens: '08:00', closes: '17:00' }
      ]
    })
  }]
})

interface StoreFacility {
  icon: string
  label: string
}

const storeData = {
  name: 'Showroom Utama PasarCCTV Bogor',
  type: 'Flagship Store & Service Center',
  address: 'Jl. Tumenggung Wiradireja No.29A, Cimahpar, Bogor Utara, Kota Bogor, Jawa Barat 16155',
  coords: [-6.5510, 106.8185] as [number, number],
  phone: '0821-1777-9003',
  phoneRaw: '6282117779003',
  hoursWeekday: '08.00 - 17.00 WIB',
  hoursSunday: 'Tutup (Emergency WA On)',
  facilities: [
    { icon: 'i-heroicons-video-camera', label: 'Live Demo Unit & Night Vision' },
    { icon: 'i-heroicons-wrench-screwdriver', label: 'Service Center & Garansi' },
    { icon: 'i-heroicons-user-group', label: 'Konsultasi Teknis Gratis' },
    { icon: 'i-heroicons-shopping-bag', label: 'Pengambilan Pesanan (Pick-up)' }
  ] as StoreFacility[]
}

const activeTab = ref<'info' | 'map'>('info')
const mapRef = ref<any>(null)
const mapReady = ref(false)
const zoom = ref(15)
const center = ref<[number, number]>(storeData.coords)
const userLocation = ref<[number, number] | null>(null)
const routeLine = shallowRef<any>(null)
const leafletInstance = shallowRef<any>(null)
const searchQuery = ref('')
const loading = ref(false)
const locating = ref(false)
const geoError = ref('')
const copySuccess = ref(false)

if (import.meta.client) {
  import('leaflet').then(m => {
    leafletInstance.value = m.default || m
  })
}

const isOpenNow = computed(() => {
  const now = new Date()
  const day = now.getDay()
  if (day === 0) return false
  const hours = now.getHours()
  return hours >= 8 && hours < 17
})

// Haversine distance calculation (independent of Leaflet loading state)
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371
  const dLat = (lat2 - lat1) * (Math.PI / 180)
  const dLon = (lon2 - lon1) * (Math.PI / 180)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

const distanceToStore = computed(() => {
  if (!userLocation.value) return null
  const d = calculateDistance(
    userLocation.value[0],
    userLocation.value[1],
    storeData.coords[0],
    storeData.coords[1]
  )
  return d.toFixed(2)
})

const invalidateMap = () => {
  nextTick(() => {
    mapRef.value?.leafletObject?.invalidateSize()
  })
}

const onMapReady = () => {
  mapReady.value = true
  invalidateMap()
}

const handleMapClick = (e: any) => {
  if (e?.latlng) {
    userLocation.value = [e.latlng.lat, e.latlng.lng]
  }
}

const recenterStore = () => {
  center.value = [storeData.coords[0], storeData.coords[1]]
  zoom.value = 16
  mapRef.value?.leafletObject?.setView(storeData.coords, 16)
}

const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    geoError.value = 'Peramban tidak mendukung geolokasi.'
    return
  }
  locating.value = true
  geoError.value = ''

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      userLocation.value = [pos.coords.latitude, pos.coords.longitude]
      center.value = userLocation.value
      zoom.value = 15
      locating.value = false
    },
    (err) => {
      locating.value = false
      if (err.code === 1) geoError.value = 'Akses lokasi ditolak. Buka izin lokasi di pengaturan browser.'
      else if (err.code === 2) geoError.value = 'Lokasi GPS tidak ditemukan.'
      else if (err.code === 3) geoError.value = 'Waktu permintaan lokasi habis.'
      else geoError.value = 'Gagal mendeteksi lokasi.'
    },
    { enableHighAccuracy: true, timeout: 12000 }
  )
}

const searchLocation = async () => {
  if (!searchQuery.value.trim()) return
  loading.value = true
  geoError.value = ''
  try {
    const data = await $fetch<any[]>('https://nominatim.openstreetmap.org/search', {
      params: { q: searchQuery.value, format: 'json', limit: 1, countrycodes: 'id' },
      headers: { 'Accept-Language': 'id' }
    })
    if (data && data.length > 0) {
      userLocation.value = [parseFloat(data[0].lat), parseFloat(data[0].lon)]
      center.value = userLocation.value
      zoom.value = 14
    } else {
      geoError.value = 'Alamat tidak ditemukan. Gunakan nama jalan atau wilayah yang lebih spesifik.'
    }
  } catch {
    geoError.value = 'Gagal menghubungi server pencarian lokasi.'
  } finally {
    loading.value = false
  }
}

const drawRoute = async () => {
  const L = leafletInstance.value
  if (!userLocation.value || !mapRef.value?.leafletObject || !L) return

  if (routeLine.value) {
    routeLine.value.remove()
    routeLine.value = null
  }

  const [uLat, uLng] = userLocation.value
  const [sLat, sLng] = storeData.coords

  try {
    const data: any = await $fetch(
      `https://router.project-osrm.org/route/v1/driving/${uLng},${uLat};${sLng},${sLat}?overview=full&geometries=geojson`
    )
    if (data?.routes?.length) {
      const coords = data.routes[0].geometry.coordinates.map(([lng, lat]: number[]) => [lat, lng])
      const line = L.polyline(coords, {
        color: '#03AC0E',
        weight: 4,
        opacity: 0.85,
        lineCap: 'round',
        lineJoin: 'round'
      }).addTo(mapRef.value.leafletObject)
      routeLine.value = line
      mapRef.value.leafletObject.fitBounds(line.getBounds(), { padding: [50, 50] })
    }
  } catch {
    // ponytail: fallback to straight line if OSRM unavailable
  }
}

const resetLocation = () => {
  userLocation.value = null
  searchQuery.value = ''
  geoError.value = ''
  recenterStore()
  routeLine.value?.remove()
  routeLine.value = null
}

const copyAddress = async () => {
  try {
    await navigator.clipboard.writeText(storeData.address)
    copySuccess.value = true
    setTimeout(() => { copySuccess.value = false }, 2500)
  } catch {
    // fallback
  }
}

const openGoogleMaps = () => {
  const dest = `${storeData.coords[0]},${storeData.coords[1]}`
  const origin = userLocation.value ? `&origin=${userLocation.value[0]},${userLocation.value[1]}` : ''
  window.open(`https://www.google.com/maps/dir/?api=1&destination=${dest}${origin}&travelmode=driving`, '_blank')
}

const openWaze = () => {
  window.open(`https://waze.com/ul?ll=${storeData.coords[0]},${storeData.coords[1]}&navigate=yes`, '_blank')
}

watch(userLocation, () => {
  drawRoute()
})

watch(activeTab, (tab) => {
  if (tab === 'map') {
    invalidateMap()
  }
})

let resizeHandler: (() => void) | null = null

onMounted(() => {
  resizeHandler = () => invalidateMap()
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  if (routeLine.value) {
    routeLine.value.remove()
    routeLine.value = null
  }
})
</script>

<template>
  <main class="min-h-screen bg-gray-50 flex flex-col font-sans">
    <!-- Breadcrumb Header -->
    <div class="bg-white border-b border-gray-200">
      <div class="max-w-[1400px] mx-auto px-4 py-3 sm:px-6">
        <nav class="flex items-center gap-2 text-xs text-gray-500" aria-label="Breadcrumb">
          <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
          <span>/</span>
          <span class="text-gray-900 font-medium">Lokasi Toko & Showroom</span>
        </nav>
      </div>
    </div>

    <!-- Mobile Segmented View Switcher -->
    <div class="lg:hidden px-4 pt-4 pb-1">
      <div class="flex bg-gray-200/80 p-1 rounded-xl text-xs font-medium">
        <button
          type="button"
          @click="activeTab = 'info'"
          class="flex-1 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all"
          :class="activeTab === 'info' ? 'bg-white text-gray-900 shadow-xs font-semibold' : 'text-gray-600'"
        >
          <UIcon name="i-heroicons-information-circle" class="w-4 h-4" />
          <span>Informasi Showroom</span>
        </button>
        <button
          type="button"
          @click="activeTab = 'map'"
          class="flex-1 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all"
          :class="activeTab === 'map' ? 'bg-white text-gray-900 shadow-xs font-semibold' : 'text-gray-600'"
        >
          <UIcon name="i-heroicons-map" class="w-4 h-4 text-[#03AC0E]" />
          <span>Peta & Rute</span>
        </button>
      </div>
    </div>

    <!-- Main Container: Master-Detail Amazon Split View -->
    <div class="flex-1 flex flex-col lg:flex-row max-w-[1400px] w-full mx-auto p-4 sm:p-6 gap-6">
      
      <!-- LEFT PANEL: Store Info, Search, Facilities, Actions (Amazon Hub Sidebar Style) -->
      <aside
        class="w-full lg:w-[420px] shrink-0 flex flex-col gap-4"
        :class="activeTab === 'info' ? 'flex' : 'hidden lg:flex'"
      >
        
        <!-- Search & GPS Card -->
        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-xs">
          <label for="store-search-input" class="block text-xs font-semibold text-gray-900 mb-2">
            Cari Jarak Dari Alamat Anda
          </label>
          <div class="flex gap-2">
            <div class="relative flex-1">
              <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                id="store-search-input"
                v-model="searchQuery"
                type="text"
                placeholder="Ketik nama jalan / kecamatan..."
                class="w-full pl-9 pr-3 py-2 text-xs bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-[#03AC0E] focus:outline-none transition-colors"
                @keyup.enter="searchLocation"
              />
            </div>
            <button
              type="button"
              @click="searchLocation"
              :disabled="loading || !searchQuery.trim()"
              class="bg-[#03AC0E] hover:bg-[#028C0B] disabled:opacity-50 text-white text-xs font-medium px-3.5 py-2 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <span v-else>Cari</span>
            </button>
            <button
              type="button"
              @click="getCurrentLocation"
              :disabled="locating"
              title="Gunakan Lokasi GPS Saya"
              class="border border-gray-200 bg-white hover:bg-[#E6F7E9] hover:border-[#03AC0E] text-gray-700 hover:text-[#03AC0E] text-xs font-medium px-2.5 py-2 rounded-lg transition-colors flex items-center justify-center cursor-pointer"
            >
              <UIcon v-if="locating" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin text-[#03AC0E]" />
              <UIcon v-else name="i-heroicons-map-pin" class="w-4 h-4" />
            </button>
          </div>

          <!-- GPS Error Alert -->
          <div v-if="geoError" class="mt-2.5 p-2 bg-red-50 border border-red-200 rounded-md text-[11px] text-red-700 flex items-start gap-1.5">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
            <span>{{ geoError }}</span>
          </div>

          <!-- Distance Calculation Badge -->
          <div v-if="distanceToStore" class="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
            <div class="flex items-center gap-1.5">
              <UIcon name="i-heroicons-arrow-trending-up" class="w-4 h-4 text-[#03AC0E]" />
              <span class="text-xs text-gray-600">Perkiraan Jarak:</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold text-gray-900">{{ distanceToStore }} km</span>
              <button
                type="button"
                @click="resetLocation"
                class="text-[11px] text-gray-400 hover:text-red-600 transition-colors"
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        <!-- Store Detail Card -->
        <div class="bg-white rounded-xl border border-gray-200 p-5 shadow-xs flex flex-col gap-4">
          <!-- Title & Open Status -->
          <div class="flex items-start justify-between gap-2 border-b border-gray-100 pb-3.5">
            <div>
              <span class="inline-block text-[10px] font-semibold text-[#03AC0E] bg-[#E6F7E9] px-2 py-0.5 rounded uppercase tracking-wider mb-1">
                {{ storeData.type }}
              </span>
              <h1 class="text-base font-semibold text-gray-900 leading-snug">
                {{ storeData.name }}
              </h1>
            </div>
            <div class="shrink-0 flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-md" :class="isOpenNow ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'">
              <span class="w-2 h-2 rounded-full" :class="isOpenNow ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'"></span>
              <span>{{ isOpenNow ? 'Buka Sekarang' : 'Tutup' }}</span>
            </div>
          </div>

          <!-- Address & Copy -->
          <div class="flex flex-col gap-1.5 text-xs">
            <span class="text-gray-500 font-medium flex items-center gap-1">
              <UIcon name="i-heroicons-map-pin" class="w-3.5 h-3.5 text-[#03AC0E]" />
              Alamat Lengkap:
            </span>
            <p class="text-gray-800 leading-relaxed pl-4">
              {{ storeData.address }}
            </p>
            <div class="pl-4 pt-1">
              <button
                type="button"
                @click="copyAddress"
                class="inline-flex items-center gap-1 text-[11px] text-gray-600 hover:text-[#03AC0E] transition-colors cursor-pointer"
              >
                <UIcon :name="copySuccess ? 'i-heroicons-check' : 'i-heroicons-clipboard-document'" class="w-3.5 h-3.5" />
                <span>{{ copySuccess ? 'Alamat Tersalin!' : 'Salin Alamat Toko' }}</span>
              </button>
            </div>
          </div>

          <!-- Operating Hours -->
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-100 flex flex-col gap-1.5 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-gray-600 flex items-center gap-1">
                <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5 text-gray-400" />
                Senin - Sabtu:
              </span>
              <span class="font-medium text-gray-900">{{ storeData.hoursWeekday }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-600 flex items-center gap-1">
                <UIcon name="i-heroicons-calendar" class="w-3.5 h-3.5 text-gray-400" />
                Minggu & Hari Libur:
              </span>
              <span class="font-medium text-gray-500">{{ storeData.hoursSunday }}</span>
            </div>
          </div>

          <!-- Showroom Facilities Badges -->
          <div class="border-t border-gray-100 pt-3">
            <span class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider block mb-2">
              Fasilitas & Layanan Showroom
            </span>
            <div class="grid grid-cols-2 gap-2">
              <div
                v-for="facility in storeData.facilities"
                :key="facility.label"
                class="flex items-center gap-2 p-2 rounded-lg bg-gray-50 border border-gray-100 text-[11px] text-gray-700 font-medium"
              >
                <UIcon :name="facility.icon" class="w-4 h-4 text-[#03AC0E] shrink-0" />
                <span class="leading-tight">{{ facility.label }}</span>
              </div>
            </div>
          </div>

          <!-- Navigation Action Buttons -->
          <div class="border-t border-gray-100 pt-4 flex flex-col gap-2">
            <div class="grid grid-cols-2 gap-2">
              <button
                type="button"
                @click="openGoogleMaps"
                class="bg-gray-900 hover:bg-gray-800 text-white text-xs font-medium py-2.5 px-3 rounded-lg transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-4 h-4" />
                <span>Google Maps</span>
              </button>
              <button
                type="button"
                @click="openWaze"
                class="bg-[#33CCFF] hover:bg-[#28BFEF] text-white text-xs font-medium py-2.5 px-3 rounded-lg transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <UIcon name="i-heroicons-paper-airplane" class="w-4 h-4" />
                <span>Navigasi Waze</span>
              </button>
            </div>

            <div class="grid grid-cols-2 gap-2">
              <a
                :href="`https://wa.me/${storeData.phoneRaw}?text=Halo%20PasarCCTV,%20saya%20ingin%20berkunjung%20ke%20showroom`"
                target="_blank"
                class="bg-[#25D366] hover:bg-[#20BE5C] text-white text-xs font-medium py-2.5 px-3 rounded-lg transition-colors flex items-center justify-center gap-1.5"
              >
                <UIcon name="i-heroicons-chat-bubble-left-right" class="w-4 h-4" />
                <span>Chat WhatsApp</span>
              </a>
              <a
                :href="`tel:${storeData.phoneRaw}`"
                class="border border-gray-200 bg-white hover:bg-gray-50 text-gray-800 text-xs font-medium py-2.5 px-3 rounded-lg transition-colors flex items-center justify-center gap-1.5"
              >
                <UIcon name="i-heroicons-phone" class="w-4 h-4 text-gray-500" />
                <span>{{ storeData.phone }}</span>
              </a>
            </div>
          </div>
        </div>

      </aside>

      <!-- RIGHT PANEL: Full Height Leaflet Map Container -->
      <section
        class="flex-1 bg-white rounded-xl border border-gray-200 overflow-hidden shadow-xs relative flex flex-col min-h-[460px] lg:min-h-[640px]"
        :class="activeTab === 'map' ? 'flex' : 'hidden lg:flex'"
      >
        
        <!-- Map Overlay Header / Recenter Toolbar -->
        <div class="absolute top-3 left-3 right-3 z-10 flex items-center justify-between pointer-events-none">
          <div class="pointer-events-auto bg-white/95 backdrop-blur-xs border border-gray-200 shadow-sm rounded-lg px-3 py-1.5 text-xs text-gray-700 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-[#03AC0E]"></span>
            <span class="font-medium text-gray-900">Showroom PasarCCTV</span>
          </div>

          <div class="pointer-events-auto flex items-center gap-1.5">
            <button
              type="button"
              @click="recenterStore"
              class="bg-white border border-gray-200 hover:border-[#03AC0E] hover:text-[#03AC0E] text-gray-700 p-2 rounded-lg shadow-sm text-xs font-medium transition-colors flex items-center gap-1 cursor-pointer"
              title="Pusatkan ke Showroom PasarCCTV"
            >
              <UIcon name="i-heroicons-viewfinder-circle" class="w-4 h-4" />
              <span class="hidden sm:inline">Pusatkan Peta</span>
            </button>
          </div>
        </div>

        <!-- Skeleton loader -->
        <div v-if="!mapReady" class="absolute inset-0 flex flex-col items-center justify-center bg-gray-100 text-gray-400 z-5">
          <UIcon name="i-heroicons-map" class="w-10 h-10 animate-pulse text-gray-300 mb-2" />
          <span class="text-xs font-medium">Memuat peta lokasi...</span>
        </div>

        <!-- Leaflet Map Instance -->
        <ClientOnly>
          <l-map
            ref="mapRef"
            :zoom="zoom"
            :center="center"
            :options="{ attributionControl: false, zoomControl: false }"
            class="w-full h-full flex-1 z-0 cursor-crosshair"
            @ready="onMapReady"
            @click="handleMapClick"
          >
            <l-tile-layer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              layer-type="base"
              name="OSM"
            />

            <l-control-zoom position="bottomright" />

            <!-- Store Marker -->
            <l-marker :lat-lng="storeData.coords" :z-index-offset="100">
              <l-icon :icon-size="[40, 48]" :icon-anchor="[20, 48]" class-name="bg-transparent border-none">
                <div class="flex flex-col items-center">
                  <div class="w-10 h-10 bg-[#03AC0E] text-white rounded-full shadow-lg flex items-center justify-center border-2 border-white">
                    <UIcon name="i-heroicons-building-storefront" class="w-5 h-5" />
                  </div>
                  <div class="w-3 h-3 -mt-1.5 bg-[#03AC0E] rotate-45 border-r border-b border-white"></div>
                </div>
              </l-icon>
              <l-popup :options="{ maxWidth: 280 }">
                <div class="p-3 font-sans text-xs">
                  <span class="text-[10px] font-semibold text-[#03AC0E] uppercase tracking-wider block mb-0.5">
                    Showroom & Service
                  </span>
                  <strong class="text-sm text-gray-900 block font-semibold mb-1">
                    {{ storeData.name }}
                  </strong>
                  <p class="text-gray-600 mb-3 leading-relaxed">
                    {{ storeData.address }}
                  </p>
                  <button
                    type="button"
                    @click="openGoogleMaps"
                    class="w-full bg-[#03AC0E] text-white font-medium py-1.5 px-3 rounded text-center text-xs hover:bg-[#028C0B] transition-colors"
                  >
                    Buka Petunjuk Arah
                  </button>
                </div>
              </l-popup>
            </l-marker>

            <!-- User Marker -->
            <l-marker v-if="userLocation" :lat-lng="userLocation">
              <l-icon :icon-size="[30, 30]" :icon-anchor="[15, 15]" class-name="bg-transparent border-none">
                <div class="relative w-7 h-7 flex items-center justify-center">
                  <div class="absolute inset-0 bg-blue-500 rounded-full animate-ping opacity-35"></div>
                  <div class="relative w-6 h-6 bg-white rounded-full border-2 border-blue-600 shadow-md flex items-center justify-center">
                    <div class="w-2.5 h-2.5 bg-blue-600 rounded-full"></div>
                  </div>
                </div>
              </l-icon>
              <l-popup>
                <div class="p-2 font-sans text-xs font-semibold text-blue-700 flex items-center gap-1.5">
                  <UIcon name="i-heroicons-user" class="w-4 h-4" />
                  <span>Lokasi Anda</span>
                </div>
              </l-popup>
            </l-marker>

          </l-map>
        </ClientOnly>

        <!-- Map Footer Legend / Information -->
        <div class="bg-gray-50 border-t border-gray-200 px-4 py-2.5 flex flex-wrap items-center justify-between text-xs text-gray-500 gap-2">
          <div class="flex items-center gap-3">
            <span class="flex items-center gap-1">
              <span class="w-2.5 h-2.5 rounded-full bg-[#03AC0E]"></span> Showroom Toko
            </span>
            <span v-if="userLocation" class="flex items-center gap-1">
              <span class="w-2.5 h-2.5 rounded-full bg-blue-600"></span> Titik Anda
            </span>
          </div>
          <span class="text-[11px] text-gray-400">© PasarCCTV Maps Platform</span>
        </div>

      </section>

    </div>
  </main>
</template>

<style scoped>
main {
  font-family: 'Plus Jakarta Sans', sans-serif;
}

:deep(.leaflet-pane) {
  z-index: 1 !important;
}

:deep(.leaflet-control-zoom) {
  border: none !important;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
  border-radius: 8px !important;
  overflow: hidden;
  margin-right: 12px !important;
  margin-bottom: 12px !important;
}

:deep(.leaflet-control-zoom a) {
  border: none !important;
  color: #374151 !important;
  background-color: #ffffff !important;
}

:deep(.leaflet-control-zoom a:hover) {
  background-color: #f3f4f6 !important;
  color: #03AC0E !important;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

:deep(.leaflet-popup-content) {
  margin: 0;
}
</style>