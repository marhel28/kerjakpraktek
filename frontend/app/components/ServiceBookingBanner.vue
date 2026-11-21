<script setup lang="ts">
/**
 * Component: ServiceBookingBanner (Refactored)
 * Philosophy: Amazon Home Services Ergonomics + Tokopedia Trust & Green Palette
 * Target: Field technicians, homeowners, shop owners (30-55yo) needing fast, transparent booking without confusion.
 */
import { ref, computed } from "vue";

const { data: packagesData, pending } = await useFetch("/api/proxy/services/packages", {
  key: "service-packages:home",
  server: true,
  lazy: false,
  getCachedData: (key, nuxtApp) => nuxtApp.payload.data[key] ?? nuxtApp.static.data[key],
});

const packages = computed(() => (packagesData.value as any[] | null)?.slice(0, 3) ?? []);

const selectedService = ref<string>("installation");

const SERVICES = [
  {
    id: "installation",
    label: "Pasang Baru",
    icon: "i-heroicons-home-modern",
    desc: "Instalasi paket kamera & DVR/NVR dari nol",
  },
  {
    id: "troubleshoot",
    label: "Cek Kendala & Error",
    icon: "i-heroicons-magnifying-glass",
    desc: "CCTV mati, DVR bunyi, gambar buram/hilang",
  },
  {
    id: "maintenance",
    label: "Servis & Perawatan",
    icon: "i-heroicons-wrench-screwdriver",
    desc: "Cleaning lensa, rapikan kabel & cek harddisk",
  },
  {
    id: "consultation",
    label: "Konsultasi Online",
    icon: "i-heroicons-chat-bubble-left-right",
    desc: "Tanya spesifikasi & kebutuhan gratis",
  },
];

const canBook = computed(() => !!selectedService.value);

const ctaText = computed(() => {
  const textMap: Record<string, string> = {
    installation: "Jadwalkan Pemasangan Baru",
    troubleshoot: "Panggil Teknisi Cek Kendala",
    maintenance: "Jadwalkan Servis Berkala",
    consultation: "Mulai Konsultasi Gratis",
  };
  return textMap[selectedService.value] || "Lanjutkan Booking";
});

const bookingUrl = computed(() => {
  const p = new URLSearchParams();
  if (selectedService.value) p.set("category", selectedService.value);
  return `/layanan/booking?${p.toString()}`;
});

const estimateUrl = computed(() => {
  const p = new URLSearchParams();
  if (selectedService.value) p.set("category", selectedService.value);
  return `/layanan/booking?${p.toString()}&step=estimate`;
});

const fmt = (n: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(n).replace("Rp", "Rp ");
};
</script>

<template>
  <section
    aria-labelledby="service-heading"
    itemscope
    itemtype="https://schema.org/Service"
    class="w-full my-8 sm:my-10"
  >
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      
      <!-- Container Bersih Tanpa Glow & Tanpa Shadow Hitam Tebal -->
      <div class="bg-white rounded-2xl border border-gray-200/90 shadow-xs p-5 sm:p-7 lg:p-8">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-start">
          
          <!-- Sisi Kiri: Selector Layanan (Amazon Home Services Style) -->
          <div class="lg:col-span-8 flex flex-col">
            
            <!-- Header Ringkas & Terpercaya -->
            <div class="mb-6">
              <h2
                id="service-heading"
                class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight leading-snug"
              >
                CCTV Bermasalah atau Butuh Pasang Baru?
              </h2>
              <p class="text-xs sm:text-sm text-gray-600 mt-2 max-w-2xl leading-relaxed">
                Teknisi di Bandung dan Cimahi datang ke rumah, ruko, atau kantor. Biaya transparan dan pengerjaan bergaransi resmi.
              </p>
            </div>

            <!-- 4 Opsi Layanan (Radio Card Grid Amazon) -->
            <div class="mb-6">
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-3">
                Pilih Jenis Layanan:
              </label>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label
                  v-for="svc in SERVICES"
                  :key="svc.id"
                  class="relative cursor-pointer select-none"
                >
                  <input
                    type="radio"
                    name="cctv_service"
                    :value="svc.id"
                    v-model="selectedService"
                    class="sr-only"
                  />
                  <div
                    class="h-full flex items-start gap-3.5 p-4 rounded-xl border-2 transition-all"
                    :class="
                      selectedService === svc.id
                        ? 'border-[#03AC0E] bg-[#F0FBF2] shadow-xs'
                        : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50/50'
                    "
                  >
                    <!-- Icon Container -->
                    <div
                      class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors"
                      :class="
                        selectedService === svc.id
                          ? 'bg-[#03AC0E] text-white'
                          : 'bg-gray-100 text-gray-600'
                      "
                    >
                      <UIcon :name="svc.icon" class="w-5 h-5" />
                    </div>

                    <!-- Label & Desc -->
                    <div class="flex-1 min-w-0">
                      <div class="mb-0.5">
                        <span
                          class="text-sm font-bold transition-colors block truncate"
                          :class="selectedService === svc.id ? 'text-[#027A08]' : 'text-gray-900'"
                        >
                          {{ svc.label }}
                        </span>
                      </div>
                      <p class="text-xs text-gray-500 leading-snug">
                        {{ svc.desc }}
                      </p>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            <!-- Action Buttons Row -->
            <div class="flex flex-col sm:flex-row items-center gap-3 pt-5 border-t border-gray-100">
              <NuxtLink
                :to="bookingUrl"
                class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3 rounded-xl font-bold text-sm text-white bg-[#027A08] hover:bg-[#026A07] active:scale-98 shadow-xs transition-all"
              >
                {{ ctaText }}
              </NuxtLink>

              <NuxtLink
                :to="estimateUrl"
                class="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-5 py-3 rounded-xl font-semibold text-xs text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
              >
                <UIcon name="i-heroicons-calculator" class="w-4 h-4 text-gray-500" />
                Kalkulator Estimasi Biaya
              </NuxtLink>

              <span class="text-[11px] text-gray-400 font-medium sm:ml-auto">
                *Tanpa biaya pendaftaran
              </span>
            </div>

          </div>

          <!-- Sisi Kanan: Ringkasan paket pemasangan -->
          <aside class="lg:col-span-4 w-full">
            <div class="bg-gray-50/80 rounded-xl border border-gray-200/80 p-5 flex flex-col">
              
              <div class="pb-3 mb-3 border-b border-gray-200">
                <h3 class="text-sm font-bold text-gray-900 tracking-tight">
                  Paket pemasangan
                </h3>
              </div>

              <!-- Daftar paket -->
              <div class="space-y-2.5">
                <template v-if="pending">
                  <div v-for="i in 3" :key="i" class="flex gap-3 p-2 bg-white rounded-lg animate-pulse">
                    <div class="w-12 h-12 bg-gray-200 rounded-md" />
                    <div class="flex-1 space-y-1.5 py-1">
                      <div class="h-3 bg-gray-200 rounded w-3/4" />
                      <div class="h-2.5 bg-gray-200 rounded w-1/2" />
                    </div>
                  </div>
                </template>

                <NuxtLink
                  v-for="pkg in packages"
                  :key="pkg.uuid"
                  :to="`/layanan/booking?package=${pkg.uuid}&category=${pkg.category}`"
                  class="group flex items-center gap-3 p-2.5 rounded-xl bg-white border border-gray-200 hover:border-[#03AC0E] transition-all"
                >
                  <div class="w-12 h-12 rounded-lg bg-gray-50 overflow-hidden shrink-0 border border-gray-100 p-1 flex items-center justify-center">
                    <NuxtImg
                      v-if="pkg.thumbnail_url"
                      :src="pkg.thumbnail_url"
                      :alt="pkg.name"
                      class="w-full h-full object-contain group-hover:scale-105 transition-transform"
                      loading="lazy"
                    />
                    <UIcon v-else name="i-heroicons-video-camera" class="w-6 h-6 text-gray-400" />
                  </div>

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-1">
                      <span class="text-[10px] text-gray-400 truncate">{{ pkg.default_brand || 'Hikvision / Dahua' }}</span>
                    </div>
                    <h4 class="text-xs font-bold text-gray-900 group-hover:text-[#027A08] transition-colors truncate">
                      {{ pkg.name }}
                    </h4>
                    <p v-if="(pkg.dp_amount || pkg.total_estimated || 0) > 0" class="text-xs font-bold text-[#027A08]">
                      {{ fmt(pkg.dp_amount || pkg.total_estimated) }}
                    </p>
                  </div>
                </NuxtLink>
              </div>

              <!-- Chat WhatsApp Teknisi & Trust Points -->
              <div class="mt-4 pt-3.5 border-t border-gray-200 space-y-2.5">
                <a
                  href="https://wa.me/6281234567890"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-[#25D366]/15 hover:bg-[#25D366]/25 text-[#075E54] font-bold text-xs transition-colors"
                >
                  <Icon name="logos:whatsapp-icon" class="w-4 h-4" />
                  Konsultasi / Tanya Teknisi via WA
                </a>

              </div>

            </div>
          </aside>

        </div>
      </div>

    </div>
  </section>
</template>
