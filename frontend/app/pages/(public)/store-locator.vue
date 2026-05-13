<template>
  <!-- Mobile: full-screen app feel | Desktop: max-width centered card -->
  <div class="min-h-screen bg-gray-50 font-sans lg:py-8 lg:px-4">
    <div class="max-w-[1200px] mx-auto lg:rounded-2xl lg:border lg:border-gray-200 lg:shadow-xl overflow-hidden bg-white">

      <!-- ══ HEADER ══════════════════════════════════════════ -->
      <header class="bg-white border-b border-gray-100 px-4 py-4 md:px-8 md:py-5 flex items-center justify-between sticky top-0 z-30">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 bg-[#e5f7ed] rounded-xl flex items-center justify-center border border-[#b3e5cb]">
            <Icon name="lucide:map-pin" class="w-5 h-5 text-[#00AA5B]" aria-hidden="true" />
          </div>
          <div>
            <h1 class="text-[15px] font-extrabold text-gray-900 leading-none">Lokasi Toko</h1>
            <p class="text-[11px] text-gray-500 font-semibold mt-0.5">PasarCctv — Spesialis Keamanan</p>
          </div>
        </div>

        <!-- Status ping -->
        <div class="flex items-center gap-2 bg-[#e5f7ed] border border-[#b3e5cb] px-3 py-1.5 rounded-full">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00AA5B] opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-[#00AA5B]"></span>
          </span>
          <span class="text-[10px] font-black text-[#00AA5B] uppercase tracking-widest hidden sm:block">Navigasi Aktif</span>
        </div>
      </header>

      <!-- ══ SEARCH BAR — sticky bawah header ══════════════════ -->
      <div class="bg-white border-b border-gray-100 px-4 py-3 md:px-8 md:py-4 sticky top-[61px] z-20">
        <div class="flex gap-2">
          <!-- Search input -->
          <div class="relative flex-1 group">
            <span class="absolute inset-y-0 left-3 flex items-center text-gray-400 group-focus-within:text-[#00AA5B] transition-colors">
              <Icon name="lucide:search" class="w-4 h-4" aria-hidden="true" />
            </span>
            <input
              id="location-search"
              v-model="searchQuery"
              type="search"
              placeholder="Cari lokasi / alamat..."
              autocomplete="off"
              class="w-full pl-9 pr-3 py-2.5 bg-gray-50 border border-gray-200 text-[13px] font-semibold text-gray-800 placeholder-gray-400 focus:bg-white focus:border-[#00AA5B] focus:ring-2 focus:ring-[#00AA5B]/10 outline-none transition-all rounded-xl"
              @keyup.enter="searchLocation"
            />
          </div>

          <!-- Search button -->
          <button
            @click="searchLocation"
            :disabled="loading || !searchQuery.trim()"
            class="bg-[#00AA5B] text-white px-4 py-2.5 rounded-xl text-[13px] font-bold transition-all hover:bg-[#008f4c] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 shrink-0"
          >
            <Icon v-if="loading" name="lucide:loader-2" class="w-4 h-4 animate-spin" />
            <Icon v-else name="lucide:search" class="w-4 h-4" />
            <span class="hidden sm:inline">Cari</span>
          </button>

          <!-- GPS button -->
          <button
            @click="getCurrentLocation"
            :disabled="locating"
            :title="locating ? 'Mencari lokasi...' : 'Gunakan GPS'"
            class="relative bg-white border border-gray-200 text-gray-700 hover:border-[#00AA5B] hover:text-[#00AA5B] hover:bg-[#e5f7ed] px-3.5 py-2.5 rounded-xl text-[13px] font-bold transition-all disabled:opacity-50 flex items-center gap-1.5 shrink-0"
          >
            <Icon v-if="locating" name="lucide:loader-2" class="w-4 h-4 animate-spin" />
            <Icon v-else name="lucide:crosshair" class="w-4 h-4" />
            <span class="hidden sm:inline">GPS</span>
          </button>
        </div>

        <!-- GPS error -->
        <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0 -translate-y-1" enter-to-class="opacity-100">
          <div v-if="geoError" class="mt-2 flex items-start gap-2 p-2.5 bg-red-50 border border-red-100 rounded-xl text-[12px] text-red-600 font-semibold">
            <Icon name="lucide:alert-circle" class="w-4 h-4 shrink-0 mt-0.5" />
            {{ geoError }}
          </div>
        </Transition>

        <!-- Distance info -->
        <div v-if="userLocation" class="mt-2.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div class="flex items-center gap-2 bg-[#e5f7ed] border border-[#b3e5cb] px-3 py-2 rounded-xl">
            <Icon name="lucide:route" class="w-4 h-4 text-[#00AA5B]" />
            <span class="text-[12px] font-bold text-gray-700">Jarak ke toko:</span>
            <span class="text-[14px] font-black text-gray-900">{{ distanceToStore }} km</span>
          </div>
          <div class="flex items-center gap-2 flex-wrap">
            <button
              @click="openInGoogleMaps"
              class="flex items-center gap-1.5 bg-gray-900 text-white text-[12px] font-bold px-3 py-2 rounded-xl hover:bg-gray-700 transition-colors"
            >
              <Icon name="lucide:navigation" class="w-3.5 h-3.5" />
              Google Maps
            </button>
            <button
              @click="openWaze"
              class="flex items-center gap-1.5 bg-[#33ccff] text-white text-[12px] font-bold px-3 py-2 rounded-xl hover:bg-[#00b8e6] transition-colors"
            >
              <Icon name="lucide:car" class="w-3.5 h-3.5" />
              Waze
            </button>
            <button
              @click="clearUserLocation"
              class="text-[11px] font-bold text-gray-400 hover:text-red-500 transition-colors px-2 py-2"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      <!-- ══ MAP ════════════════════════════════════════════════ -->
      <div class="relative bg-[#e8ecef]" style="height: calc(100svh - 180px); min-height: 320px; max-height: 600px;">

        <!-- Skeleton peta sebelum client render -->
        <div v-if="!mapReady" class="absolute inset-0 flex flex-col items-center justify-center text-gray-400 z-10 bg-[#e8ecef]">
          <Icon name="lucide:map" class="w-10 h-10 mb-3 animate-pulse text-gray-300" />
          <span class="text-sm font-bold text-gray-400">Memuat peta...</span>
        </div>

        <ClientOnly>
          <l-map
            ref="mapRef"
            :zoom="zoom"
            :center="center"
            :options="{ attributionControl: false, zoomControl: false }"
            class="w-full h-full z-0"
            @click="handleMapClick"
            @ready="onMapReady"
          >
            <l-tile-layer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              layer-type="base"
              name="OSM"
            />

            <!-- Zoom Control custom posisi -->
            <l-control-zoom position="bottomright" />

            <!-- Marker Toko -->
            <l-marker :lat-lng="storeLocation" :z-index-offset="100">
              <l-icon :icon-size="[44, 44]" :icon-anchor="[22, 44]" class-name="bg-transparent border-none">
                <div class="flex flex-col items-center">
                  <div class="w-11 h-11 bg-white rounded-full border-[3px] border-[#00AA5B] shadow-xl flex items-center justify-center">
                    <Icon name="lucide:store" class="w-5 h-5 text-[#00AA5B]" />
                  </div>
                  <div class="w-3 h-3 -mt-1.5 bg-[#00AA5B] rotate-45 shadow"></div>
                </div>
              </l-icon>
              <l-popup :options="{ maxWidth: 280 }">
                <div class="p-4 font-sans min-w-[220px]">
                  <span class="inline-block bg-gray-900 text-white text-[9px] font-black px-2 py-0.5 rounded uppercase tracking-widest mb-2">Spesialis Keamanan</span>
                  <strong class="text-gray-900 text-sm block font-extrabold mb-1">PasarCctv</strong>
                  <p class="text-[12px] text-gray-500 leading-relaxed mb-3">{{ storeAddress }}</p>
                  <a :href="`https://www.google.com/maps/dir/?api=1&destination=${storeLocation[0]},${storeLocation[1]}&travelmode=driving`" target="_blank"
                    class="block text-center bg-[#00AA5B] text-white text-[12px] font-bold py-2 rounded-lg hover:bg-[#008f4c] transition-colors">
                    Rute ke Sini
                  </a>
                </div>
              </l-popup>
            </l-marker>

            <!-- Marker User -->
            <l-marker v-if="userLocation" :lat-lng="userLocation">
              <l-icon :icon-size="[32, 32]" :icon-anchor="[16, 16]" class-name="bg-transparent border-none">
                <div class="relative w-8 h-8 flex items-center justify-center">
                  <div class="absolute inset-0 bg-blue-500 rounded-full animate-ping opacity-30"></div>
                  <div class="relative w-full h-full bg-white rounded-full border-[3px] border-blue-500 shadow-lg flex items-center justify-center">
                    <div class="w-2.5 h-2.5 bg-blue-500 rounded-full"></div>
                  </div>
                </div>
              </l-icon>
              <l-popup>
                <div class="p-2.5 font-sans flex items-center gap-2 text-[12px] font-extrabold text-blue-600">
                  <Icon name="lucide:user" class="w-4 h-4" /> Lokasi Anda
                </div>
              </l-popup>
            </l-marker>

          </l-map>
        </ClientOnly>

        <!-- FAB GPS mobile -->
        <button
          @click="getCurrentLocation"
          :disabled="locating"
          class="absolute bottom-4 left-4 z-20 w-12 h-12 bg-white rounded-full shadow-xl border border-gray-200 flex items-center justify-center hover:bg-[#e5f7ed] hover:border-[#00AA5B] transition-all active:scale-95 disabled:opacity-60 lg:hidden"
          :title="locating ? 'Mencari lokasi GPS...' : 'Deteksi lokasi GPS'"
        >
          <Icon v-if="locating" name="lucide:loader-2" class="w-5 h-5 text-[#00AA5B] animate-spin" />
          <Icon v-else name="lucide:crosshair" class="w-5 h-5 text-[#00AA5B]" />
        </button>

        <!-- Hint klik peta -->
        <div v-if="!userLocation" class="absolute bottom-4 right-4 z-20 bg-black/60 text-white text-[11px] font-semibold px-3 py-2 rounded-xl backdrop-blur-sm pointer-events-none hidden lg:flex items-center gap-1.5">
          <Icon name="lucide:mouse-pointer-click" class="w-3.5 h-3.5" />
          Klik peta untuk pin lokasi
        </div>
      </div>

      <!-- ══ INFO TOKO ════════════════════════════════════════ -->
      <div class="px-4 py-5 md:px-8 md:py-6 bg-white border-t border-gray-100">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

          <!-- Alamat -->
          <div class="flex items-start gap-3 p-4 rounded-xl bg-gray-50 border border-gray-100">
            <div class="w-9 h-9 bg-[#e5f7ed] rounded-lg flex items-center justify-center shrink-0 border border-[#b3e5cb]">
              <Icon name="lucide:map-pin" class="w-4 h-4 text-[#00AA5B]" />
            </div>
            <div>
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Alamat</p>
              <p class="text-[13px] font-semibold text-gray-800 leading-snug">{{ storeAddress }}</p>
            </div>
          </div>

          <!-- Jam Operasional -->
          <div class="flex items-start gap-3 p-4 rounded-xl bg-gray-50 border border-gray-100">
            <div class="w-9 h-9 bg-[#e5f7ed] rounded-lg flex items-center justify-center shrink-0 border border-[#b3e5cb]">
              <Icon name="lucide:clock" class="w-4 h-4 text-[#00AA5B]" />
            </div>
            <div>
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Jam Buka</p>
              <p class="text-[13px] font-semibold text-gray-800">Senin – Sabtu</p>
              <p class="text-[13px] font-bold text-gray-900">08.00 – 17.00 WIB</p>
              <p class="text-[11px] text-gray-400 font-medium mt-0.5">Minggu / Libur: Tutup</p>
            </div>
          </div>

          <!-- Telepon & WA -->
          <div class="flex items-start gap-3 p-4 rounded-xl bg-gray-50 border border-gray-100">
            <div class="w-9 h-9 bg-[#e5f7ed] rounded-lg flex items-center justify-center shrink-0 border border-[#b3e5cb]">
              <Icon name="lucide:phone" class="w-4 h-4 text-[#00AA5B]" />
            </div>
            <div class="flex flex-col gap-2">
              <div>
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Telepon</p>
                <a href="tel:082117779003" class="text-[13px] font-bold text-gray-900 hover:text-[#00AA5B] transition-colors">0821-1777-9003</a>
              </div>
              <a
                href="https://wa.me/6282117779003?text=Halo%20PasarCctv%2C%20saya%20mau%20tanya-tanya"
                target="_blank"
                class="inline-flex items-center gap-1.5 bg-[#25D366] text-white text-[12px] font-bold px-3 py-1.5 rounded-lg hover:bg-[#1eb859] transition-colors w-fit"
              >
                <Icon name="lucide:message-circle" class="w-3.5 h-3.5" />
                Chat WhatsApp
              </a>
            </div>
          </div>

        </div>
      </div>

      <!-- ══ FOOTER ════════════════════════════════════════════ -->
      <footer class="px-4 py-4 md:px-8 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <span class="text-[11px] text-gray-400 font-bold">© {{ new Date().getFullYear() }} PasarCctv</span>
        <div class="flex items-center gap-1.5 text-gray-500">
          <Icon name="lucide:shield-check" class="w-3.5 h-3.5 text-[#00AA5B]" />
          <span class="text-[11px] font-semibold">Spesialis CCTV Terpercaya</span>
        </div>
      </footer>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

definePageMeta({ ssr: false })

// ── SEO ──────────────────────────────────────────────────────────
useSeoMeta({
  title: 'Lokasi Toko PasarCctv — Showroom CCTV Bandung & Cimahi',
  description: 'Temukan lokasi toko PasarCctv. Dapatkan rute tercepat via GPS, Google Maps, atau Waze. Spesialis CCTV & sistem keamanan di Bandung dan Cimahi.',
  ogTitle: 'Lokasi Toko PasarCctv — Showroom CCTV',
  ogDescription: 'Kunjungi showroom PasarCctv. Stok lengkap, teknisi berpengalaman, dan konsultasi gratis.',
  ogType: 'place',
  twitterCard: 'summary',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://pasarcctv.com/store-locator' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ElectronicsStore',
      name: 'PasarCctv',
      description: 'Marketplace spesialis perangkat keamanan dan CCTV di Bandung & Cimahi.',
      url: 'https://pasarcctv.com',
      telephone: '+6282117779003',
      address: {
        '@type': 'PostalAddress',
        streetAddress: 'Jl. Tumenggung Wiradireja No.29A',
        addressLocality: 'Bogor',
        addressRegion: 'Jawa Barat',
        postalCode: '16155',
        addressCountry: 'ID',
      },
      geo: {
        '@type': 'GeoCoordinates',
        latitude: -6.5510,
        longitude: 106.8185,
      },
      openingHoursSpecification: [
        { '@type': 'OpeningHoursSpecification', dayOfWeek: ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'], opens: '08:00', closes: '17:00' },
      ],
    }),
  }],
})

// ── Store Data ────────────────────────────────────────────────────
const storeLocation = ref<[number, number]>([-6.5510, 106.8185])
const storeAddress  = ref('Jl. Tumenggung Wiradireja No.29A, Cimahpar, Bogor Utara, Kota Bogor, Jawa Barat 16155')

// ── Map State ────────────────────────────────────────────────────
const mapRef      = ref<any>(null)
const mapReady    = ref(false)
const zoom        = ref(15)
const center      = ref<[number, number]>([-6.5510, 106.8185])
const userLocation= ref<[number, number] | null>(null)
const routeLine   = ref<any>(null)
const searchQuery = ref('')
const loading     = ref(false)
const locating    = ref(false)
const geoError    = ref('')

let L: any = null
if (import.meta.client) {
  import('leaflet').then(m => { L = m.default || m })
}

// ── Map ready ────────────────────────────────────────────────────
const onMapReady = () => {
  nextTick(() => {
    mapReady.value = true
    mapRef.value?.leafletObject?.invalidateSize()
  })
}

// ── Distance ─────────────────────────────────────────────────────
const distanceToStore = computed(() => {
  if (!userLocation.value || !L) return '0.00'
  const d = L.latLng(userLocation.value).distanceTo(L.latLng(storeLocation.value))
  return (d / 1000).toFixed(2)
})

// ── GPS ───────────────────────────────────────────────────────────
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    geoError.value = 'Browser kamu tidak mendukung fitur Geolocation.'
    return
  }
  locating.value = true
  geoError.value = ''

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      userLocation.value = [pos.coords.latitude, pos.coords.longitude]
      center.value = userLocation.value
      zoom.value = 16
      locating.value = false
    },
    (err) => {
      locating.value = false
      if (err.code === 1) geoError.value = 'Izin lokasi ditolak. Aktifkan akses lokasi di pengaturan browser.'
      else if (err.code === 2) geoError.value = 'Sinyal GPS tidak tersedia. Coba lagi di tempat terbuka.'
      else if (err.code === 3) geoError.value = 'Permintaan lokasi timeout. Pastikan koneksi internet stabil.'
      else geoError.value = 'Gagal mendapatkan lokasi GPS.'
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
  )
}

// ── Search (Nominatim) ────────────────────────────────────────────
const searchLocation = async () => {
  if (!searchQuery.value.trim()) return
  loading.value = true
  geoError.value = ''
  try {
    const data = await $fetch<any[]>('https://nominatim.openstreetmap.org/search', {
      params: { q: searchQuery.value, format: 'json', limit: 1, countrycodes: 'id' },
      headers: { 'Accept-Language': 'id' },
    })
    if (data.length) {
      userLocation.value = [parseFloat(data[0].lat), parseFloat(data[0].lon)]
      center.value = userLocation.value!
      zoom.value = 15
    } else {
      geoError.value = 'Lokasi tidak ditemukan. Coba nama kota atau jalan yang lebih spesifik.'
    }
  } catch {
    geoError.value = 'Gagal mencari lokasi. Periksa koneksi internet.'
  } finally {
    loading.value = false
  }
}

// ── Draw Route (OSRM) ────────────────────────────────────────────
const drawRoute = async () => {
  if (!userLocation.value || !mapRef.value || !L) return

  routeLine.value?.remove()
  routeLine.value = null

  const [uLat, uLng] = userLocation.value
  const [sLat, sLng] = storeLocation.value

  try {
    const data: any = await $fetch(
      `https://router.project-osrm.org/route/v1/driving/${uLng},${uLat};${sLng},${sLat}?overview=full&geometries=geojson`
    )
    if (data.routes?.length) {
      const coords = data.routes[0].geometry.coordinates.map(([lng, lat]: number[]) => [lat, lng])
      routeLine.value = L.polyline(coords, {
        color: '#00AA5B',
        weight: 5,
        opacity: 0.85,
        lineCap: 'round',
        lineJoin: 'round',
      }).addTo(mapRef.value.leafletObject)
      mapRef.value.leafletObject.fitBounds(routeLine.value.getBounds(), { padding: [60, 60] })
    }
  } catch { /* silent */ }
}

// ── Map click ────────────────────────────────────────────────────
const handleMapClick = (e: any) => {
  userLocation.value = [e.latlng.lat, e.latlng.lng]
}

// ── Clear ─────────────────────────────────────────────────────────
const clearUserLocation = () => {
  userLocation.value = null
  searchQuery.value  = ''
  geoError.value     = ''
  center.value       = storeLocation.value
  zoom.value         = 15
  routeLine.value?.remove()
  routeLine.value = null
}

// ── Open Maps ────────────────────────────────────────────────────
const openInGoogleMaps = () => {
  if (!userLocation.value) return
  const [uLat, uLng] = userLocation.value
  const [sLat, sLng] = storeLocation.value
  window.open(`https://www.google.com/maps/dir/?api=1&origin=${uLat},${uLng}&destination=${sLat},${sLng}&travelmode=driving`, '_blank')
}

const openWaze = () => {
  const [sLat, sLng] = storeLocation.value
  window.open(`https://waze.com/ul?ll=${sLat},${sLng}&navigate=yes`, '_blank')
}

// ── Watcher ────────────────────────────────────────────────────────
watch(userLocation, () => drawRoute())
</script>

<style scoped>
@import 'leaflet/dist/leaflet.css';

:deep(.leaflet-pane) { z-index: 1 !important; }
:deep(.leaflet-control-zoom) { border: none !important; box-shadow: 0 2px 12px -2px rgba(0,0,0,0.15) !important; border-radius: 12px !important; overflow: hidden; }
:deep(.leaflet-control-zoom a) { border: none !important; font-size: 16px; color: #374151 !important; }
:deep(.leaflet-control-zoom a:hover) { background-color: #f3f4f6 !important; color: #00AA5B !important; }
:deep(.leaflet-div-icon.bg-transparent) { background: transparent !important; border: none !important; }

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 16px;
  border: 1px solid #f3f4f6;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 10px 30px -5px rgba(0,0,0,0.12);
}
:deep(.leaflet-popup-content) { margin: 0; }
:deep(.leaflet-container a.leaflet-popup-close-button) {
  top: 8px; right: 8px; color: #9ca3af;
  width: 24px; height: 24px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: #f3f4f6; font-weight: normal;
  transition: all 0.2s;
}
:deep(.leaflet-container a.leaflet-popup-close-button:hover) { color: #ef4444; background: #fee2e2; }
</style>