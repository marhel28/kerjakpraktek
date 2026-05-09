<template>
  <section
    aria-labelledby="sbb-heading"
    itemscope
    itemtype="https://schema.org/Service"
    class="w-full px-4 sm:px-6 py-12 sm:py-20 bg-white"
  >
    <meta itemprop="name" content="Layanan CCTV Padjajaran" />
    <meta itemprop="areaServed" content="Bandung, Cimahi, Jawa Barat" />
    <meta itemprop="serviceType" content="CCTV Installation, Maintenance, Consultation" />
    <meta
      itemprop="description"
      content="Jasa pasang dan servis CCTV profesional area Bandung."
    />

    <div class="max-w-[1100px] mx-auto">
      <header class="mb-12 sm:mb-16 human-animate">
        <div class="flex items-center gap-2.5 mb-4">
          <span class="w-2 h-2 rounded-full bg-[#00AA5B]"></span>
          <span class="text-[14px] font-medium text-zinc-600"
            >Teknisi standby area Bandung & Cimahi</span
          >
        </div>
        <h2
          id="sbb-heading"
          class="text-3xl sm:text-[42px] font-extrabold text-zinc-900 tracking-tight leading-[1.15] mb-5 max-w-2xl"
        >
          Beresin masalah CCTV kamu tanpa ribet.
        </h2>
        <p class="text-[16px] sm:text-[17px] leading-[1.7] text-zinc-600 max-w-2xl">
          Biaya kami jelasin di depan. Nggak ada tambahan aneh-aneh pas teknisi datang ke
          rumah atau tempat usahamu.
        </p>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-[1.2fr_1fr] gap-12 lg:gap-24">
        <div class="flex flex-col human-animate" style="animation-delay: 0.1s">
          <div class="mb-8">
            <h3 class="text-[18px] font-bold text-zinc-900 mb-5">
              Mau dibantu apa hari ini?
            </h3>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2">
              <label v-for="svc in SERVICES" :key="svc.id" class="cursor-pointer group">
                <input
                  type="radio"
                  :value="svc.id"
                  v-model="selectedService"
                  class="sr-only"
                />
                <div
                  class="flex items-start gap-3.5 p-4 rounded-2xl transition-colors duration-200"
                  :class="
                    selectedService === svc.id ? 'bg-[#F2FBF5]' : 'hover:bg-zinc-50/80'
                  "
                >
                  <UIcon
                    :name="svc.icon"
                    class="w-6 h-6 mt-0.5 transition-colors"
                    :class="
                      selectedService === svc.id
                        ? 'text-[#00AA5B]'
                        : 'text-zinc-400 group-hover:text-zinc-700'
                    "
                  />
                  <div>
                    <div
                      class="text-[15px] font-semibold transition-colors"
                      :class="
                        selectedService === svc.id ? 'text-[#00AA5B]' : 'text-zinc-900'
                      "
                    >
                      {{ svc.label }}
                    </div>
                    <div class="text-[13px] text-zinc-500 mt-0.5 leading-relaxed">
                      {{ svc.desc }}
                    </div>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <div class="mt-auto pt-6 border-t border-zinc-100">
            <div class="flex flex-col sm:flex-row sm:items-center gap-5 mb-5">
              <NuxtLink
                :to="bookingUrl"
                class="inline-flex items-center justify-center px-7 py-3.5 rounded-xl font-bold text-[15px] transition-all duration-200"
                :class="
                  canBook
                    ? 'bg-[#00AA5B] text-white hover:bg-[#00904d]'
                    : 'bg-zinc-100 text-zinc-400 cursor-not-allowed pointer-events-none'
                "
              >
                {{ ctaText }}
              </NuxtLink>

              <NuxtLink
                :to="estimateUrl"
                class="text-[14px] font-semibold text-zinc-500 hover:text-zinc-900 transition-colors underline underline-offset-4 decoration-zinc-200 hover:decoration-zinc-400"
              >
                Cek estimasi biaya
              </NuxtLink>
            </div>

            <div class="flex items-center gap-4 text-[13px] font-medium text-zinc-500">
              <span>Datang hari ini</span>
              <span class="w-1 h-1 rounded-full bg-zinc-300"></span>
              <span>Garansi resmi</span>
            </div>
          </div>
        </div>

        <aside class="flex flex-col human-animate" style="animation-delay: 0.2s">
          <h4 class="text-[18px] font-bold text-zinc-900 mb-6">Paket Paling Laris</h4>

          <div class="flex flex-col gap-5">
            <template v-if="pending">
              <div class="py-8 text-zinc-400 text-[14px]">Mencari paket...</div>
            </template>

            <div v-else-if="!packages.length" class="py-8 text-[14px] text-zinc-500">
              Paket sedang diperbarui. Hubungi teknisi kami untuk harga terbaru.
            </div>

            <NuxtLink
              v-for="(pkg, idx) in packages"
              :key="pkg.uuid"
              :to="`/layanan/booking?package=${pkg.uuid}&category=${pkg.category}`"
              class="group flex items-start gap-4 p-3 -mx-3 rounded-[20px] hover:bg-zinc-50 transition-colors duration-200"
            >
              <div
                class="w-20 h-20 rounded-[14px] bg-zinc-100 overflow-hidden shrink-0 mt-1"
              >
                <NuxtImg
                  v-if="pkg.thumbnail_url"
                  :src="pkg.thumbnail_url"
                  :alt="pkg.name"
                  class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                  loading="lazy"
                />
              </div>

              <div class="flex-1 min-w-0 pt-1">
                <div v-if="idx === 0" class="text-[11px] font-bold text-[#00AA5B] mb-1.5">
                  Pilihan Favorit
                </div>
                <h5
                  class="text-[15px] font-bold text-zinc-900 leading-snug mb-1 group-hover:text-[#00AA5B] transition-colors"
                >
                  {{ pkg.name }}
                </h5>
                <p class="text-[13px] text-zinc-500 mb-2">
                  {{ pkg.camera_count }} Kamera &middot; {{ pkg.default_brand }}
                </p>
                <div class="flex items-baseline gap-2">
                  <span class="text-[14px] font-bold text-zinc-900">
                    DP {{ fmt(pkg.dp_amount) }}
                  </span>
                  <span class="text-[12px] text-zinc-400 line-through">
                    {{ fmt(pkg.total_estimated) }}
                  </span>
                </div>
              </div>
            </NuxtLink>

            <div class="mt-6 pt-6 border-t border-zinc-100">
              <a
                href="https://wa.me/6281234567890?text=Halo%2C%20saya%20mau%20tanya-tanya%20soal%20pasang%20CCTV"
                target="_blank"
                class="inline-flex flex-col"
              >
                <span class="text-[14px] text-zinc-600 mb-1"
                  >Masih bingung pilih yang mana?</span
                >
                <span
                  class="text-[15px] font-bold text-[#00AA5B] hover:text-[#00904d] transition-colors"
                >
                  Chat teknisi kami sekarang &rarr;
                </span>
              </a>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

const { data: packagesData, pending } = await useFetch("/api/proxy/services/packages", {
  key: "service-packages:home",
  server: true,
  lazy: false,
  getCachedData: (key, nuxtApp) => nuxtApp.payload.data[key] ?? nuxtApp.static.data[key],
});

const packages = computed(() => (packagesData.value as any[] | null)?.slice(0, 3) ?? []);

const selectedService = ref<string>("installation"); // Default active untuk memperjelas state awal

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
  // Format ala manusia, hilangkan desimal nol di belakang
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  })
    .format(n)
    .replace("Rp", "Rp ");
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap");

section {
  font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* ── Editorial Smooth Animation (Subtle & Natural) ── */
@keyframes humanFadeUp {
  0% {
    opacity: 0;
    transform: translateY(12px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.human-animate {
  animation: humanFadeUp 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) both;
  will-change: transform, opacity;
}

@media (prefers-reduced-motion: reduce) {
  .human-animate {
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}
</style>
