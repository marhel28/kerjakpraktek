<script setup lang="ts">
/**
 * Generic Skeleton Components for Index Page Sections
 * Used for CategoryGrid, BannerSection, ServiceBookingBanner
 * Matches the layout structure of each component
 */
interface Props {
  /** Type of skeleton to render */
  type: 'category-grid' | 'banner-section' | 'service-booking-banner'
}

const props = defineProps<Props>()
</script>

<template>
  <!-- Category Grid Skeleton -->
  <div v-if="type === 'category-grid'" role="status" aria-live="polite" aria-label="Loading categories" class="space-y-4">
    <div class="flex items-center justify-between">
      <div class="h-6 w-40 bg-gray-300 rounded skeleton-shimmer" />
      <div class="h-6 w-24 bg-gray-200 rounded skeleton-shimmer" />
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="group relative rounded-xl overflow-hidden bg-white border border-gray-100">
        <div class="aspect-[4/3] w-full bg-gray-100 relative overflow-hidden">
          <div class="skeleton-shimmer absolute inset-0 bg-gray-200" />
          <!-- Overlay gradient -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent skeleton-shimmer" />
        </div>
        <div class="absolute bottom-0 left-0 right-0 p-4">
          <div class="h-5 w-3/4 bg-white/90 rounded skeleton-shimmer" />
          <div class="h-4 w-1/2 bg-white/70 rounded skeleton-shimmer mt-1" />
        </div>
      </div>
    </div>
  </div>

  <!-- Banner Section Skeleton -->
  <div v-else-if="type === 'banner-section'" role="status" aria-live="polite" aria-label="Loading banners" class="space-y-6">
    <div class="flex items-center justify-between">
      <div class="h-7 w-48 bg-gray-300 rounded skeleton-shimmer" />
      <div class="h-7 w-20 bg-gray-200 rounded skeleton-shimmer" />
    </div>
    <div class="relative aspect-[16/5] w-full rounded-xl overflow-hidden bg-gray-100">
      <div class="skeleton-shimmer absolute inset-0 bg-gray-200" />
      <!-- Navigation arrows -->
      <div class="absolute left-4 top-1/2 -translate-y-1/2 h-12 w-12 rounded-full bg-gray-300 skeleton-shimmer" />
      <div class="absolute right-4 top-1/2 -translate-y-1/2 h-12 w-12 rounded-full bg-gray-300 skeleton-shimmer" />
      <!-- Dots -->
      <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
        <div v-for="i in 5" :key="i" class="h-2 w-2 rounded-full bg-gray-300 skeleton-shimmer" />
      </div>
    </div>
  </div>

  <!-- Service Booking Banner Skeleton -->
  <div v-else-if="type === 'service-booking-banner'" role="status" aria-live="polite" aria-label="Loading service booking banner" class="rounded-2xl bg-gradient-to-r from-primary-500 to-primary-600 p-6 md:p-8 text-white overflow-hidden relative">
    <div class="relative z-10 max-w-xl space-y-4">
      <div class="h-5 w-32 bg-white/20 rounded skeleton-shimmer" />
      <div class="h-8 w-3/4 bg-white/30 rounded skeleton-shimmer" />
      <div class="h-5 w-1/2 bg-white/20 rounded skeleton-shimmer" />
      <div class="flex flex-wrap gap-2">
        <div v-for="i in 3" :key="i" class="h-8 w-20 bg-white/20 rounded-full skeleton-shimmer" />
      </div>
      <div class="h-12 w-40 bg-white/30 rounded-lg skeleton-shimmer mt-2" />
    </div>
    <!-- Right side illustration placeholder -->
    <div class="absolute right-4 bottom-0 top-0 w-1/2 hidden lg:block">
      <div class="absolute right-0 bottom-0 h-3/4 w-3/4 bg-white/10 rounded-full blur-3xl skeleton-shimmer" />
    </div>
  </div>
</template>

<style scoped>
.skeleton-shimmer {
  animation: shimmer 1.5s infinite linear;
  will-change: opacity;
}

@keyframes shimmer {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

/* CLS Prevention */
.aspect-\[16\/5\] {
  contain-intrinsic-size: 800px 250px;
  content-visibility: auto;
}

.aspect-\[4\/3\] {
  contain-intrinsic-size: 300px 225px;
  content-visibility: auto;
}

div[role="status"] {
  contain-intrinsic-size: auto 300px;
  content-visibility: auto;
}
</style>