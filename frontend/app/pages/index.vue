<script setup>
import Brandrunning from "@/components/brandrunning.vue";
import CategoryGrid from "@/components/images/CategoryGrid.vue";
import BannerSection from "@/components/BannerSection.vue";
import ServiceBookingBanner from "@/components/ServiceBookingBanner.vue";
import FlashSaleSection from "@/components/home/FlashSaleSection.vue";
import SkeletonGeneric from "@/components/SkeletonGeneric.vue";

const { data: homeBannerData, pending: homeBannerPending } = await useFetch(
  `/api/banner/${encodeURIComponent("home:hero-carousel")}`,
  {
    key: "banner-home-hero-carousel",
    transform: (r) => r?.data ?? null,
    server: true,
  }
);

const { data: bottomBannerData, pending: bottomBannerPending } = await useFetch("/api/main-bottom", {
  key: "main-bottom-banners",
  transform: (res) => res?.data ?? [],
  server: true,
});

useSeoMeta({
  title: "PasarCctv - Jasa Pasang & Marketplace CCTV Terlengkap di Bandung",
  description: "Pesan layanan instalasi CCTV profesional dan belanja perlengkapan keamanan terlengkap untuk rumah serta bisnis di area Bandung & Cimahi.",
  ogTitle: "PasarCctv - Spesialis Jasa Pasang CCTV Bandung",
  ogDescription: "Beresin masalah CCTV kamu tanpa ribet. Teknisi standby, biaya transparan, garansi resmi.",
  robots: "index, follow",
});
</script>

<template>
  <main class="w-full bg-white">
    <BannerUtama />
    <Brandrunning />
    <HomeBanner class="my-8" />
    <FlashSaleSection class="my-8" />
    <PopularItems class="my-8" />

    <!-- Service Booking Banner with Skeleton -->
    <div class="mt-2 mb-2">
      <SkeletonGeneric v-if="homeBannerPending" type="service-booking-banner" />
      <ServiceBookingBanner v-else class="mt-2 mb-2" />
    </div>

    <!-- Banner Promosi Produk Beranda (Eksklusif, Terpisah dari Hero Atas) -->
    <div class="my-8">
      <SkeletonGeneric v-if="homeBannerPending" type="banner-section" />
      <BannerSection
        v-else
        identifier="home:promo-strip"
        :autoplay-delay="6000"
        :show-title="false"
      />
    </div>

    <!-- Bottom Banner Grid (maks 4) -->
    <div class="my-10">
      <SkeletonGeneric v-if="bottomBannerPending" type="category-grid" />
      <CategoryGrid v-else :categories="bottomBannerData" />
    </div>

    <KeunggulanBar />
  </main>
</template>
