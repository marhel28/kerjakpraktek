<template>
  <div class="max-w-[1200px] mx-auto my-8 border border-gray-200 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] rounded-2xl overflow-hidden bg-white font-sans text-gray-800">

    <header class="bg-white border-b border-gray-100 px-6 py-5 md:px-8 md:py-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 relative z-10">
      <div class="flex items-center gap-4">
        <div class="bg-[#e5f7ed] p-3 rounded-xl border border-[#b3e5cb] text-[#00AA5B] shadow-sm">
          <Icon name="lucide:map-pin" class="w-7 h-7" aria-hidden="true" />
        </div>
        <div class="flex flex-col">
          <h1 class="text-xl md:text-2xl font-extrabold tracking-tight text-gray-900 leading-none">Lokasi Toko</h1>
          <div class="flex items-center gap-2 mt-2">
            <span class="text-sm font-semibold text-gray-500">PasarCCTV Store Locator</span>
            <span class="text-[10px] bg-gray-900 text-white font-black px-2 py-0.5 rounded uppercase tracking-widest shadow-sm">Spesialis Keamanan</span>
          </div>
        </div>
      </div>

      <div class="flex items-center">
        <div class="flex items-center gap-2.5 bg-gray-50 border border-gray-200 px-4 py-2 rounded-xl font-bold text-[11px] text-gray-600 uppercase tracking-widest shadow-sm">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00AA5B] opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#00AA5B]"></span>
          </span>
          Sistem Navigasi Aktif
        </div>
      </div>
    </header>

    <div class="bg-white p-6 border-b border-gray-100 relative z-10">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 items-end">

        <div class="lg:col-span-7 space-y-2">
          <label for="location-search" class="text-[11px] font-extrabold uppercase tracking-widest text-gray-500 ml-1">Cari Titik Jemput / Lokasi Anda</label>
          <div class="relative group">
            <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-gray-400 group-focus-within:text-[#00AA5B] transition-colors">
              <Icon name="lucide:search" class="w-5 h-5" aria-hidden="true" />
            </span>
            <input
              id="location-search"
              type="search"
              placeholder="Masukkan alamat, jalan, atau nama daerah..."
              class="w-full pl-11 pr-4 py-3.5 bg-gray-50 border border-gray-200 text-sm font-semibold text-gray-800 focus:bg-white focus:border-[#00AA5B] focus:ring-4 focus:ring-[#00AA5B]/10 outline-none transition-all rounded-xl"
              v-model="searchQuery"
              @keyup.enter="searchLocation"
            />
          </div>
        </div>

        <div class="lg:col-span-5 flex flex-wrap sm:flex-nowrap gap-3">
          <button
            @click="searchLocation"
            :disabled="loading || !searchQuery"
            class="flex-1 sm:flex-none bg-[#00AA5B] text-white px-8 py-3.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center justify-center gap-2 hover:bg-[#008f4c] hover:shadow-md hover:shadow-green-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon v-if="loading" name="lucide:loader-2" class="w-4 h-4 animate-spin" />
            Cari
          </button>

          <button
            @click="getCurrentLocation"
            :disabled="locating"
            class="flex-1 sm:flex-none bg-white border border-gray-200 text-gray-700 hover:border-[#00AA5B] hover:text-[#00AA5B] hover:bg-[#e5f7ed] px-6 py-3.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
          >
            <Icon v-if="locating" name="lucide:loader-2" class="w-4 h-4 animate-spin" />
            <Icon v-else name="lucide:crosshair" class="w-4 h-4" />
            GPS Saya
          </button>

          <button
            v-if="userLocation || searchQuery"
            @click="clearUserLocation"
            class="px-4 text-gray-400 hover:text-red-500 text-sm font-bold transition-colors rounded-xl hover:bg-red-50"
            aria-label="Reset lokasi"
          >
            Reset
          </button>
        </div>
      </div>

      <div class="mt-6 flex flex-col sm:flex-row items-center justify-between border-t border-gray-100 pt-5 gap-4">
        <div v-if="userLocation" class="flex items-center bg-[#e5f7ed] border border-[#b3e5cb] px-5 py-3 rounded-xl w-full sm:w-auto">
          <Icon name="lucide:route" class="w-5 h-5 text-[#00AA5B] mr-3" aria-hidden="true" />
          <span class="text-[11px] font-extrabold text-gray-600 uppercase tracking-widest mr-2">Estimasi Jarak:</span>
          <span class="text-base font-black text-gray-900">{{ distanceToStore }} KM</span>
        </div>
        <div v-else class="flex items-center text-xs font-semibold text-gray-500 bg-gray-50 px-4 py-3 rounded-xl w-full sm:w-auto">
          <Icon name="lucide:info" class="w-4 h-4 mr-2 text-gray-400" />
          Ketuk pada peta atau gunakan GPS untuk melihat rute otomatis ke toko kami.
        </div>

        <button
          v-if="userLocation"
          @click="openInGoogleMaps"
          class="bg-white border-2 border-gray-900 text-gray-900 px-6 py-3 rounded-xl hover:bg-gray-900 hover:text-white transition-all font-bold text-xs flex items-center gap-2 justify-center w-full sm:w-auto shadow-sm"
        >
          <Icon name="logos:google-maps" class="w-4 h-4" />
          Buka di Google Maps
        </button>
      </div>
    </div>

    <div class="map-area w-full h-[500px] relative bg-[#e5e5e5] z-0 isolation-auto">
      <ClientOnly>
        <template #fallback>
          <div class="w-full h-full flex flex-col items-center justify-center text-gray-400">
            <Icon name="lucide:map" class="w-12 h-12 mb-4 animate-pulse text-gray-300" />
            <span class="text-sm font-bold text-gray-500">Memuat Peta Interaktif...</span>
          </div>
        </template>

        <l-map
          ref="mapRef"
          :zoom="zoom"
          :center="center"
          :options="{ attributionControl: false, zoomControl: true }"
          @click="handleMapClick"
          @ready="onMapReady"
        >
          <l-tile-layer
            :url="googleMapsUrl"
            layer-type="base"
            name="Google Maps"
          />

          <l-marker :lat-lng="storeLocation">
            <l-icon :icon-size="[48, 48]" :icon-anchor="[24, 48]" class-name="bg-transparent border-none">
              <div class="relative flex items-center justify-center w-12 h-12 bg-white rounded-full border-[3px] border-[#00AA5B] shadow-lg transition-transform hover:scale-110">
                <Icon name="lucide:store" class="w-6 h-6 text-[#00AA5B]" />
                <div class="absolute -bottom-2 w-3.5 h-3.5 bg-white rotate-45 border-r-[3px] border-b-[3px] border-[#00AA5B]"></div>
              </div>
            </l-icon>
            <l-popup>
              <div class="p-3.5 font-sans min-w-[220px]">
                <div class="bg-gray-900 text-white inline-block mb-2 rounded font-extrabold text-[10px] px-2.5 py-1 uppercase tracking-widest">Spesialis Keamanan</div>
                <strong class="text-gray-900 text-sm block mb-1 font-extrabold">Padjajaran CCTV</strong>
                <p class="text-[12px] leading-relaxed text-gray-600 font-medium">{{ storeAddress }}</p>
              </div>
            </l-popup>
          </l-marker>

          <l-marker v-if="userLocation" :lat-lng="userLocation">
            <l-icon :icon-size="[36, 36]" :icon-anchor="[18, 36]" class-name="bg-transparent border-none">
              <div class="relative flex items-center justify-center w-9 h-9">
                <div class="absolute inset-0 bg-blue-500 rounded-full animate-ping opacity-40"></div>
                <div class="relative flex items-center justify-center w-full h-full bg-white rounded-full border-[3px] border-blue-500 shadow-md z-10">
                  <div class="w-2.5 h-2.5 bg-blue-500 rounded-full"></div>
                </div>
              </div>
            </l-icon>
            <l-popup>
              <div class="p-2 font-sans font-extrabold text-[11px] text-blue-600 flex items-center tracking-wide">
                <Icon name="lucide:user" class="w-4 h-4 mr-2" />Lokasi Anda
              </div>
            </l-popup>
          </l-marker>

        </l-map>
      </ClientOnly>
    </div>

    <footer class="px-6 py-5 md:px-8 bg-gray-50 border-t border-gray-200 flex flex-col sm:flex-row justify-between items-center gap-4 relative z-10">
      <span class="text-[11px] text-gray-500 font-bold tracking-wide">
        © {{ new Date().getFullYear() }} Padjajaran CCTV — Semua Hak Dilindungi.
      </span>
      <div class="flex items-center gap-6">
        <a href="tel:0812XXXXXXXX" class="flex items-center gap-2 group cursor-pointer text-gray-600 hover:text-[#00AA5B] transition-colors">
          <Icon name="lucide:phone" class="w-4 h-4 group-hover:animate-bounce" />
          <span class="text-xs font-extrabold">0812-XXXX-XXXX</span>
        </a>
        <div class="flex items-center gap-2 text-gray-600">
          <Icon name="lucide:map-pin" class="w-4 h-4 text-[#00AA5B]" />
          <span class="text-xs font-extrabold">Bogor, Jawa Barat</span>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useHead } from '#imports';

definePageMeta({
  ssr: false
})

useHead({
  title: 'Lokasi & Navigasi Toko - Padjajaran CCTV',
  meta: [
    { name: 'description', content: 'Kunjungi showroom Padjajaran CCTV. Dapatkan rute tercepat, estimasi jarak, dan panduan arah langsung via Google Maps.' },
    { property: 'og:title', content: 'Lokasi Toko Padjajaran CCTV' },
    { property: 'og:type', content: 'place' }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "ElectronicsStore",
        "name": "Padjajaran CCTV",
        "description": "Marketplace spesialis perangkat keamanan dan CCTV.",
        "address": {
          "@type": "PostalAddress",
          "streetAddress": "Jl. Tumenggung Wiradireja No.29A",
          "addressLocality": "Bogor",
          "addressRegion": "Jawa Barat",
          "postalCode": "16155",
          "addressCountry": "ID"
        },
        "geo": {
          "@type": "GeoCoordinates",
          "latitude": -6.5510,
          "longitude": 106.8185
        },
        "telephone": "0812-XXXX-XXXX"
      })
    }
  ]
});

let L = null;
if (import.meta.client) {
  import("leaflet").then((module) => {
    L = module.default || module;
  });
}

const storeLocation = ref([-6.5510, 106.8185]);
const storeAddress = ref("Jl. Tumenggung Wiradireja No.29A, RT.04/RW.06, Cimahpar, Kec. Bogor Utara, Kota Bogor, Jawa Barat 16155");

const userLocation = ref(null);
const searchQuery = ref("");
const zoom = ref(15);
const center = ref([-6.5510, 106.8185]);
const loading = ref(false);
const locating = ref(false);
const mapRef = ref(null);
const routeLine = ref(null);

const googleMapsUrl = `https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}`;

const onMapReady = () => {
  nextTick(() => {
    if (mapRef.value?.leafletObject) {
      mapRef.value.leafletObject.invalidateSize();
    }
  });
};

const distanceToStore = computed(() => {
  if (!userLocation.value || !L) return 0;
  const d = L.latLng(userLocation.value).distanceTo(L.latLng(storeLocation.value));
  return (d / 1000).toFixed(2);
});

const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    alert("Browser Anda tidak mendukung fitur Geolocation.");
    return;
  }

  locating.value = true;

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;

      userLocation.value = [lat, lng];
      center.value = [lat, lng];
      zoom.value = 16;
      locating.value = false;
    },
    (err) => {
      locating.value = false;
      let errorMessage = "Gagal mendapatkan lokasi.";
      if (err.code === 1) errorMessage = "Izin lokasi ditolak. Silakan izinkan akses lokasi di pengaturan browser Anda.";
      if (err.code === 2) errorMessage = "Posisi GPS saat ini tidak tersedia.";
      if (err.code === 3) errorMessage = "Waktu permintaan lokasi habis (Timeout). Coba pastikan sinyal internet stabil.";
      alert(errorMessage);
    },
    {
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 60000
    }
  );
};

const drawRoute = async () => {
  if (!userLocation.value || !mapRef.value || !L) return;

  if (routeLine.value) {
    routeLine.value.remove();
  }

  const [uLat, uLng] = userLocation.value;
  const [sLat, sLng] = storeLocation.value;

  try {
    const url = `https://router.project-osrm.org/route/v1/driving/${uLng},${uLat};${sLng},${sLat}?overview=full&geometries=geojson`;
    const data = await $fetch(url);

    if (data.routes?.length > 0) {
      const coords = data.routes[0].geometry.coordinates.map(([lng, lat]) => [lat, lng]);

      routeLine.value = L.polyline(coords, {
        color: "#00AA5B",
        weight: 6,
        opacity: 0.85,
        lineCap: 'round',
        lineJoin: 'round',
        className: 'animate-draw-route'
      }).addTo(mapRef.value.leafletObject);

      mapRef.value.leafletObject.fitBounds(routeLine.value.getBounds(), { padding: [60, 60] });
    }
  } catch (err) {
    console.error("Gagal menarik data rute navigasi:", err);
  }
};

const searchLocation = async () => {
  if (!searchQuery.value.trim()) return;
  loading.value = true;
  try {
    const data = await $fetch("https://nominatim.openstreetmap.org/search", {
      params: { 
        q: searchQuery.value, 
        format: "json", 
        limit: 1,
        countrycodes: "id"
      }
    });

    if (data.length) {
      userLocation.value = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
      center.value = userLocation.value;
      zoom.value = 15;
    } else {
      alert("Lokasi tidak ditemukan. Coba gunakan nama kota atau jalan yang lebih spesifik.");
    }
  } catch(e) {
    console.error("Geocoding Error:", e);
  } finally {
    loading.value = false;
  }
};

const handleMapClick = (e) => {
  userLocation.value = [e.latlng.lat, e.latlng.lng];
};

const clearUserLocation = () => {
  userLocation.value = null;
  searchQuery.value = "";
  center.value = storeLocation.value;
  zoom.value = 15;
  if (routeLine.value) {
    routeLine.value.remove();
    routeLine.value = null;
  }
};

const openInGoogleMaps = () => {
  if (!userLocation.value) return;
  const [uLat, uLng] = userLocation.value;
  const [sLat, sLng] = storeLocation.value;
  
  const url = `https://www.google.com/maps/dir/?api=1&origin=${uLat},${uLng}&destination=${sLat},${sLng}&travelmode=driving`;
  window.open(url, '_blank');
};

watch(userLocation, () => {
  drawRoute();
});
</script>

<style scoped>
/* Import Leaflet CSS langsung di komponen untuk menghindari error 404 */
@import 'leaflet/dist/leaflet.css';

.map-area { z-index: 1; }
:deep(.leaflet-pane) { z-index: 1 !important; }

:deep(.leaflet-div-icon.bg-transparent) {
  background: transparent !important;
  border: none !important;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 16px;
  border: 1px solid #f3f4f6;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
}
:deep(.leaflet-popup-content) { margin: 0; }
:deep(.leaflet-container a.leaflet-popup-close-button) {
  top: 10px;
  right: 10px;
  color: #9ca3af;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  font-weight: normal;
  transition: all 0.2s;
}
:deep(.leaflet-container a.leaflet-popup-close-button:hover) {
  color: #ef4444;
  background: #fee2e2;
}

:deep(.animate-draw-route) {
  stroke-dasharray: 2000;
  stroke-dashoffset: 2000;
  animation: draw 1.5s linear forwards;
}
@keyframes draw {
  to {
    stroke-dashoffset: 0;
  }
}
</style>