<script setup>
import Brandrunning from "@/components/brandrunning.vue";
import CategoryGrid from "@/components/images/CategoryGrid.vue";
import BannerSection from "@/components/BannerSection.vue";
import ServiceBookingBanner from "@/components/ServiceBookingBanner.vue";

const { data: homeBannerData } = await useFetch(
  `/api/banner/${encodeURIComponent("home:hero-carousel")}`,
  {
    key: "banner-home-hero-carousel",
    transform: (r) => r?.data ?? null,
    server: true,
  }
);

const { data: bottomBannerData } = await useFetch("/api/main-bottom", {
  key: "main-bottom-banners",
  transform: (res) => res?.data ?? [],
  server: true,
});

useHead({
  title: "Padjajaran CCTV - Marketplace Keamanan No 1",
  meta: [
    {
      name: "description",
      content:
        "Belanja perlengkapan CCTV terlengkap, paket instalasi, dan NVR untuk rumah dan bisnis.",
    },
  ],
});
</script>

<template>
  <main class="w-full bg-white">
    <BannerUtama />
    <Brandrunning />
    <HomeBanner class="my-8" />
    <PopularItems class="my-8" />
    <ServiceBookingBanner class="mt-2 mb-2" />

    <BannerSection
      identifier="home:hero-carousel"
      :autoplay-delay="5000"
      :show-title="false"
      class="mb-6"
    />

    <!-- Bottom Banner Grid (maks 4) -->
    <CategoryGrid :categories="bottomBannerData" class="my-10" />

    <KeunggulanBar />
  </main>
</template>
