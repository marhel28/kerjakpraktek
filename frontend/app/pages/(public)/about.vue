<script setup lang="ts">
import { computed } from "vue";
// Import Swiper Vue Components & Modules
import { Swiper, SwiperSlide } from "swiper/vue";
import { Pagination, Autoplay } from "swiper/modules";

// Import Swiper styles
import "swiper/css";
import "swiper/css/pagination";

const siteUrl = useRuntimeConfig().public.siteUrl ?? "https://padjajarancctv.com";
const swiperModules = [Pagination, Autoplay];

// ─── 1. SEO & META TAGS (High Intent SEO) ─────────────────────────────
useSeoMeta({
  title: "Tentang Padjajaran CCTV | Spesialis Pemasangan CCTV Premium",
  description:
    "Berhenti bertaruh pada keamanan aset Anda. Padjajaran CCTV memberikan instalasi standar enterprise, rapi, tanpa blind-spot, dan bergaransi ganti baru.",
  ogTitle: "Investasi Ketenangan Pikiran bersama Padjajaran CCTV",
  ogDescription:
    "Lebih dari 1,200 titik terpasang sempurna. Kami mendesain sistem keamanan yang bekerja 24/7 tanpa henti.",
  ogImage: "/images/about-og.jpg",
  robots: "index, follow",
});

useHead({
  link: [{ rel: "canonical", href: `${siteUrl}/about-us` }],
  script: [
    {
      type: "application/ld+json",
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        name: "Padjajaran CCTV",
        description:
          "Layanan instalasi sistem keamanan dan CCTV profesional standar enterprise.",
        url: `${siteUrl}/about-us`,
        telephone: "+6281234567890",
        priceRange: "$$",
        address: {
          "@type": "PostalAddress",
          addressLocality: "Indonesia",
          addressCountry: "ID",
        },
      }),
    },
  ],
});

// ─── 2. DATA BUKTI SOSIAL & NILAI (Trust Builders) ─────────────────────
const stats = [
  { value: "1,200+", label: "Kamera Aktif" },
  { value: "500+", label: "Klien Terlindungi" },
  { value: "100%", label: "Kabel Dalam Pipa" },
  { value: "1 Tahun", label: "Garansi Ganti Baru" },
];

const values = [
  {
    icon: "lucide:shield-alert",
    title: "Zero Blind-Spot Design",
    desc:
      "Kami tidak asal pasang. Tim kami mensimulasikan sudut pandang kamera untuk memastikan tidak ada celah bagi penyusup yang luput dari pantauan.",
  },
  {
    icon: "lucide:zap",
    title: "Kelistrikan Anti-Sabotase",
    desc:
      "Instalasi kabel menggunakan jalur tertutup (conduit) yang mustahil dipotong sembarangan, lengkap dengan sentralisasi power supply yang aman.",
  },
  {
    icon: "lucide:badge-check",
    title: "Hanya Barang Original",
    desc:
      "Kami menjamin 100% keaslian perangkat (Hikvision, Dahua, dll). Firmware bisa di-update resmi, anti-hack, dan bergaransi pabrik.",
  },
  {
    icon: "lucide:smartphone",
    title: "Pantau Dari Genggaman",
    desc:
      "Kami pastikan sistem terhubung ke HP Anda sebelum teknisi pulang. Pantau aset berharga Anda dari mana saja, kapan saja.",
  },
];

const gallery = [
  {
    img:
      "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&q=80&w=600",
    alt: "Setup NVR Server Ruang Kontrol",
  },
  {
    img:
      "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&q=80&w=600",
    alt: "Penarikan Kabel Estetik",
  },
  {
    img:
      "https://images.unsplash.com/photo-1557597774-9d273605dfa9?auto=format&fit=crop&q=80&w=600",
    alt: "Quality Control Tampilan",
  },
  {
    img:
      "https://images.unsplash.com/photo-1541888049618-208182cb0b82?auto=format&fit=crop&q=80&w=600",
    alt: "Pemasangan Area Outdoor",
  },
  {
    img:
      "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80&w=600",
    alt: "Instalasi Fasilitas Kesehatan",
  },
];
</script>

<template>
  <main
    class="bg-gray-50 min-h-screen pb-24 md:pb-0 font-sans selection:bg-red-600 selection:text-white"
  >
    <section
      class="relative pt-24 pb-32 md:pt-36 md:pb-40 px-4 bg-black text-white overflow-hidden"
    >
      <div
        class="absolute inset-0 opacity-40 mix-blend-overlay"
        style="
          background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');
        "
      ></div>
      <div
        class="absolute top-0 right-0 w-[600px] h-[600px] bg-red-600/30 rounded-full blur-[150px] -translate-y-1/2 translate-x-1/4"
      ></div>

      <div class="max-w-4xl mx-auto text-center relative z-10">
        <div
          class="inline-flex items-center gap-2 py-1.5 px-4 bg-white/10 border border-white/20 backdrop-blur-sm text-[10px] font-black uppercase tracking-widest rounded-full mb-8 text-red-400"
        >
          <Icon name="lucide:shield-check" class="w-4 h-4" /> Partner Keamanan Anda
        </div>

        <h1
          class="text-4xl md:text-6xl font-black uppercase tracking-tight mb-6 leading-tight"
        >
          Jangan Pertaruhkan Aset Anda Pada
          <span class="text-red-500 line-through decoration-4">Instalasi Amatir</span>.
        </h1>
        <p
          class="text-base md:text-xl text-gray-300 font-medium max-w-3xl mx-auto leading-relaxed"
        >
          Kami bukan sekadar tukang tarik kabel. Padjajaran CCTV mendesain, memasang, dan
          memastikan sistem keamanan Anda beroperasi prima untuk investasi ketenangan
          bertahun-tahun.
        </p>
      </div>
    </section>

    <section class="px-4 relative z-20 -mt-20 md:-mt-24 mb-16">
      <div class="max-w-5xl mx-auto">
        <div
          class="grid grid-cols-2 md:grid-cols-4 gap-4 bg-white p-6 md:p-10 rounded-2xl shadow-2xl border border-gray-100 divide-x-0 md:divide-x divide-gray-100"
        >
          <div
            v-for="(stat, idx) in stats"
            :key="idx"
            class="flex flex-col items-center justify-center p-2 text-center"
          >
            <span
              class="text-3xl md:text-5xl font-black text-black tracking-tighter mb-1"
              >{{ stat.value }}</span
            >
            <span
              class="text-[10px] md:text-xs font-bold text-gray-400 uppercase tracking-widest"
              >{{ stat.label }}</span
            >
          </div>
        </div>
      </div>
    </section>

    <section class="py-12 md:py-20 px-4 max-w-6xl mx-auto">
      <div class="mb-14 text-center md:text-left">
        <h2 class="text-2xl md:text-4xl font-black uppercase tracking-tight text-black">
          Mengapa Memilih Kami?
        </h2>
        <p class="text-gray-500 text-sm md:text-base font-medium mt-2">
          1x Pemasangan yang benar menghemat jutaan rupiah biaya perbaikan di masa depan.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-10">
        <div
          v-for="val in values"
          :key="val.title"
          class="flex gap-5 p-6 md:p-8 bg-white border border-gray-200 rounded-2xl hover:border-black hover:shadow-xl transition-all duration-300 group cursor-default"
        >
          <div class="flex-shrink-0">
            <div
              class="w-14 h-14 bg-gray-50 rounded-xl flex items-center justify-center group-hover:bg-black group-hover:scale-110 transition-all duration-300"
            >
              <Icon :name="val.icon" class="w-7 h-7 text-black group-hover:text-white" />
            </div>
          </div>
          <div>
            <h3
              class="text-lg font-black uppercase tracking-tight mb-2 group-hover:text-red-600 transition-colors"
            >
              {{ val.title }}
            </h3>
            <p class="text-sm text-gray-500 font-medium leading-relaxed">
              {{ val.desc }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-black text-white overflow-hidden relative">
      <div class="max-w-6xl mx-auto px-4 mb-10 text-center md:text-left">
        <h2 class="text-2xl md:text-4xl font-black uppercase tracking-tight">
          Kualitas Di Lapangan
        </h2>
        <p class="text-gray-400 text-sm md:text-base mt-2">
          Transparan. Rapi. Estetik. Bukti nyata hasil kerja tim spesialis kami.
        </p>
      </div>

      <div class="w-full">
        <Swiper
          :modules="swiperModules"
          :slides-per-view="1.2"
          :space-between="16"
          :centered-slides="true"
          :loop="true"
          :autoplay="{ delay: 3500, disableOnInteraction: false }"
          :pagination="{ clickable: true, dynamicBullets: true }"
          :breakpoints="{
            640: { slidesPerView: 2, spaceBetween: 20, centeredSlides: false },
            1024: { slidesPerView: 3.5, spaceBetween: 24, centeredSlides: false },
          }"
          class="w-full pb-14 px-4 md:px-0 max-w-[1400px] mx-auto swiper-container-custom"
        >
          <SwiperSlide v-for="(img, idx) in gallery" :key="idx" class="h-auto">
            <div
              class="w-full aspect-[4/5] md:aspect-square rounded-2xl overflow-hidden relative group bg-gray-900 border border-gray-800"
            >
              <NuxtImg
                :src="img.img"
                :alt="img.alt"
                class="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110 opacity-80 group-hover:opacity-100"
                loading="lazy"
                format="webp"
              />
              <div
                class="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent opacity-90 group-hover:opacity-100 transition-opacity"
              ></div>
              <div class="absolute bottom-5 left-5 right-5 flex items-center gap-3">
                <div class="w-2 h-2 rounded-full bg-red-600 animate-pulse"></div>
                <span
                  class="text-xs font-black text-white uppercase tracking-widest leading-tight"
                  >{{ img.alt }}</span
                >
              </div>
            </div>
          </SwiperSlide>
        </Swiper>
      </div>
    </section>

    <section class="bg-red-600 text-white py-16 md:py-24 px-4 text-center">
      <div class="max-w-3xl mx-auto">
        <Icon name="lucide:shield-check" class="w-16 h-16 mx-auto mb-6 opacity-90" />
        <h2 class="text-3xl md:text-5xl font-black uppercase tracking-tight mb-6">
          Garansi Ganti Baru Tanpa Debat
        </h2>
        <p class="text-red-100 text-sm md:text-lg font-medium leading-relaxed mb-10">
          Kamera mati tiba-tiba? NVR rusak? Kami berikan jaminan ganti unit baru (bukan
          servis) di tahun pertama. Kami yang repot urus ke pabrik, Anda tetap tenang
          memantau.
        </p>

        <div class="flex flex-col sm:flex-row justify-center gap-4 hidden md:flex">
          <button
            class="bg-black text-white px-8 py-4 text-xs font-black uppercase tracking-widest hover:bg-gray-900 transition-transform hover:scale-105 active:scale-95 rounded-lg shadow-xl"
          >
            Jadwalkan Survey Gratis
          </button>
          <NuxtLink
            to="/services/booking"
            class="bg-white text-red-600 px-8 py-4 text-xs font-black uppercase tracking-widest hover:bg-gray-100 transition-transform hover:scale-105 active:scale-95 rounded-lg shadow-xl"
          >
            Lihat Harga Paket
          </NuxtLink>
        </div>
      </div>
    </section>

    <div
      class="md:hidden fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-gray-200 p-3 z-50 shadow-[0_-10px_30px_rgb(0,0,0,0.08)] safe-area-pb flex gap-3"
    >
      <button
        class="flex-1 bg-red-600 text-white py-3.5 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-red-600/20 active:scale-95 transition-transform"
      >
        <Icon name="lucide:calendar-check" class="w-4 h-4" />
        <span class="text-[10px] font-black uppercase tracking-widest"
          >Survey Gratis</span
        >
      </button>
      <NuxtLink
        to="/services/booking"
        class="flex-1 bg-black text-white py-3.5 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-black/20 active:scale-95 transition-transform text-center"
      >
        <Icon name="lucide:shopping-cart" class="w-4 h-4" />
        <span class="text-[10px] font-black uppercase tracking-widest">Pilih Paket</span>
      </NuxtLink>
    </div>
  </main>
</template>

<style scoped>
/* Dukungan area aman untuk perangkat iOS dengan notch/home indicator */
.safe-area-pb {
  padding-bottom: calc(0.75rem + env(safe-area-inset-bottom));
}

/* Custom Swiper Pagination Styling (Sleek & Modern) */
:deep(.swiper-pagination-bullet) {
  background-color: rgba(255, 255, 255, 0.4);
  width: 6px;
  height: 6px;
  transition: all 0.3s ease;
}
:deep(.swiper-pagination-bullet-active) {
  background-color: #ef4444; /* Tailwind Red 500 */
  width: 24px;
  border-radius: 4px;
}
</style>
