<script setup lang="ts">
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
    desc: "Instalasi perangkat dari nol",
  },
  {
    id: "maintenance",
    label: "Servis Berkala",
    icon: "i-heroicons-wrench-screwdriver",
    desc: "Perawatan dan pembersihan",
  },
  {
    id: "troubleshoot",
    label: "Cek Kendala",
    icon: "i-heroicons-magnifying-glass",
    desc: "Cari tahu error dan perbaikan",
  },
  {
    id: "consultation",
    label: "Konsultasi",
    icon: "i-heroicons-chat-bubble-left-right",
    desc: "Tanya-tanya dulu ke ahlinya",
  },
];

const canBook = computed(() => !!selectedService.value);

const ctaText = computed(() => {
  if (!selectedService.value) return "Pilih Layanan Dulu";
  const textMap: Record<string, string> = {
    installation: "Jadwalkan Pemasangan",
    maintenance: "Panggil Teknisi Servis",
    consultation: "Mulai Konsultasi Gratis",
    troubleshoot: "Panggil Teknisi Cek",
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
    aria-labelledby="sbb-heading"
    itemscope
    itemtype="https://schema.org/Service"
    class="relative w-full px-4 sm:px-6 py-16 sm:py-24 bg-[#FCFCFD] overflow-hidden"
  >
    <!-- Dekorasi Background -->
    <div class="absolute top-0 right-0 -translate-y-1/2 translate-x-1/4 w-[600px] h-[600px] bg-green-50/50 rounded-full blur-3xl pointer-events-none opacity-50"></div>
    
    <div class="max-w-[1200px] mx-auto relative z-10">
      <!-- Grid 8:4 untuk keseimbangan layout -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 xl:gap-16 items-start">
        
        <!-- Sisi Kiri: Konten & Seleksi (Lebih Luas) -->
        <div class="lg:col-span-8 flex flex-col human-animate">
          <header class="mb-10">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-green-100 shadow-sm mb-6">
              <span class="flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-green-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span class="text-[11px] font-black text-green-700 uppercase tracking-widest">Teknisi Area Bandung & Cimahi</span>
            </div>
            
            <h2
              id="sbb-heading"
              class="text-3xl sm:text-[44px] font-black text-zinc-900 tracking-tight leading-[1.1] mb-6"
            >
              CCTV bermasalah? <br/>
              <span class="text-green-600">Beresin tanpa ribet.</span>
            </h2>
            <p class="text-lg text-zinc-500 max-w-2xl leading-relaxed">
              Booking jasa profesional dengan biaya transparan. Nggak ada biaya siluman, semua dijelasin di depan sebelum teknisi datang.
            </p>
          </header>

          <div class="mb-10">
            <h3 class="text-sm font-black text-zinc-400 uppercase tracking-widest mb-6 flex items-center gap-2">
              Pilih Layanan Jasa
            </h3>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <label v-for="svc in SERVICES" :key="svc.id" class="relative cursor-pointer group">
                <input
                  type="radio"
                  :value="svc.id"
                  v-model="selectedService"
                  class="sr-only"
                />
                <div
                  class="h-full flex items-start gap-4 p-5 rounded-[24px] border-2 transition-all duration-300 bg-white shadow-sm"
                  :class="
                    selectedService === svc.id 
                      ? 'border-green-500 ring-4 ring-green-50 shadow-md transform -translate-y-1' 
                      : 'border-zinc-100 hover:border-zinc-200 hover:shadow-md'
                  "
                >
                  <div 
                    class="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 transition-colors"
                    :class="selectedService === svc.id ? 'bg-green-500 text-white' : 'bg-zinc-50 text-zinc-400 group-hover:bg-zinc-100'"
                  >
                    <UIcon :name="svc.icon" class="w-6 h-6" />
                  </div>
                  <div>
                    <div
                      class="text-base font-bold transition-colors"
                      :class="selectedService === svc.id ? 'text-green-700' : 'text-zinc-900'"
                    >
                      {{ svc.label }}
                    </div>
                    <div class="text-[13px] text-zinc-500 mt-1 leading-snug">
                      {{ svc.desc }}
                    </div>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row items-center gap-6 mt-2 pt-8 border-t border-zinc-100">
            <NuxtLink
              :to="bookingUrl"
              class="w-full sm:w-auto inline-flex items-center justify-center px-10 py-4 rounded-2xl font-black text-base transition-all duration-300 shadow-lg"
              :class="
                canBook
                  ? 'bg-green-600 text-white hover:bg-green-700 hover:shadow-green-200 active:scale-95'
                  : 'bg-zinc-100 text-zinc-400 cursor-not-allowed'
              "
            >
              {{ ctaText }}
              <UIcon name="i-heroicons-arrow-right" class="ml-2 w-5 h-5" />
            </NuxtLink>

            <NuxtLink
              :to="estimateUrl"
              class="text-sm font-bold text-zinc-400 hover:text-zinc-900 transition-colors flex items-center gap-2 group"
            >
              <UIcon name="i-heroicons-calculator" class="w-5 h-5 group-hover:text-green-600" />
              Lihat Estimasi Biaya
            </NuxtLink>
          </div>
        </div>

        <!-- Sisi Kanan: Paket Favorit (Lebih Ramping & Compact) -->
        <aside class="lg:col-span-4 flex flex-col human-animate" style="animation-delay: 0.1s">
          <div class="bg-white rounded-[28px] border border-zinc-100 p-6 shadow-xl shadow-zinc-200/40">
            <h4 class="text-base font-black text-zinc-900 mb-6 flex items-center justify-between">
              Paket Favorit
              <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest bg-zinc-50 px-2 py-0.5 rounded border border-zinc-100">Hot</span>
            </h4>

            <div class="flex flex-col gap-3">
              <template v-if="pending">
                <div v-for="i in 3" :key="i" class="flex gap-3 p-3 animate-pulse">
                  <div class="w-14 h-14 bg-zinc-100 rounded-xl"></div>
                  <div class="flex-1 space-y-2 py-1">
                    <div class="h-3 bg-zinc-100 rounded w-3/4"></div>
                    <div class="h-2.5 bg-zinc-100 rounded w-1/2"></div>
                  </div>
                </div>
              </template>

              <NuxtLink
                v-for="(pkg, idx) in packages"
                :key="pkg.uuid"
                :to="`/layanan/booking?package=${pkg.uuid}&category=${pkg.category}`"
                class="group flex items-center gap-3 p-3 rounded-2xl border border-transparent hover:border-green-100 hover:bg-green-50/40 transition-all duration-300"
              >
                <div class="w-16 h-16 rounded-xl bg-zinc-50 overflow-hidden shrink-0 border border-zinc-100 group-hover:border-green-200">
                  <NuxtImg
                    v-if="pkg.thumbnail_url"
                    :src="pkg.thumbnail_url"
                    :alt="pkg.name"
                    class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                    loading="lazy"
                  />
                </div>

                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-1.5 mb-0.5">
                    <span v-if="idx === 0" class="text-[8px] font-black bg-orange-500 text-white px-1.5 py-0.5 rounded uppercase tracking-tighter">Bestseller</span>
                    <span class="text-[9px] font-bold text-zinc-400 uppercase tracking-wider">{{ pkg.default_brand }}</span>
                  </div>
                  <h5 class="text-sm font-bold text-zinc-900 leading-tight mb-0.5 group-hover:text-green-700 transition-colors truncate">
                    {{ pkg.name }}
                  </h5>
                  <div class="flex items-baseline gap-1.5">
                    <span class="text-[14px] font-black text-green-600">{{ fmt(pkg.dp_amount) }}</span>
                    <span class="text-[10px] text-zinc-300 line-through">{{ fmt(pkg.total_estimated) }}</span>
                  </div>
                </div>
              </NuxtLink>
            </div>

            <div class="mt-6 pt-6 border-t border-zinc-50 space-y-3">
              <NuxtLink
                to="/layanan/booking#packages"
                class="flex items-center justify-center w-full py-3 rounded-xl border border-zinc-200 text-[13px] font-bold text-zinc-500 hover:bg-zinc-50 transition-colors"
              >
                Semua Paket
              </NuxtLink>
              
              <a
                href="https://wa.me/6281234567890"
                class="flex items-center justify-center gap-3 w-full py-3.5 rounded-xl bg-[#25D366]/10 text-[#075E54] hover:bg-[#25D366]/20 transition-all group"
              >
                <Icon name="logos:whatsapp-icon" class="w-4 h-4" />
                <div class="text-left">
                  <div class="text-[12px] font-black">Chat Teknisi</div>
                </div>
                <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5 ml-auto mr-2 translate-x-0 group-hover:translate-x-1 transition-transform" />
              </a>
            </div>
          </div>
          
          <!-- Trust Badges (Compact) -->
          <div class="mt-4 grid grid-cols-2 gap-3">
            <div class="flex items-center gap-2 p-3 bg-white rounded-xl border border-zinc-100">
              <UIcon name="i-heroicons-shield-check" class="w-4 h-4 text-green-500" />
              <span class="text-[10px] font-black text-zinc-500 uppercase tracking-wider">Garansi</span>
            </div>
            <div class="flex items-center gap-2 p-3 bg-white rounded-xl border border-zinc-100">
              <UIcon name="i-heroicons-clock" class="w-4 h-4 text-green-500" />
              <span class="text-[10px] font-black text-zinc-500 uppercase tracking-wider">Sameday</span>
            </div>
          </div>
        </aside>

      </div>
    </div>
  </section>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&display=swap");

section {
  font-family: "Plus Jakarta Sans", sans-serif;
  -webkit-font-smoothing: antialiased;
}

@keyframes humanFadeUp {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

.human-animate {
  animation: humanFadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}
</style>
