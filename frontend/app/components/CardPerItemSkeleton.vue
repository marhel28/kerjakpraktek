<script setup lang="ts">
/**
 * Skeleton Card Produk Optimized (Amazon Borderless / Flat Canvas Style)
 * - SEO: ARIA labels & role status
 * - Performance: GPU Accelerated animation
 * - UX: Fixed aspect ratio prevent Layout Shift
 */
</script>

<template>
  <div
    role="status"
    aria-live="polite"
    aria-label="Loading product"
    class="flex flex-col h-full w-full bg-transparent isolation-auto"
  >
    <!-- Media (Rounded-2xl Flat Canvas) -->
    <div class="relative aspect-[4/5] w-full rounded-lg bg-gray-100 overflow-hidden">
      <div class="skeleton-shimmer absolute inset-0 bg-gray-200"></div>

      <!-- Skeleton Circular Quick Add Button in Bottom-Right -->
      <div class="absolute bottom-2.5 right-2.5 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gray-300 skeleton-shimmer shadow-md"></div>
    </div>

    <!-- Body -->
    <div class="flex flex-1 flex-col pt-2.5">
      <!-- Promo deal badge shimmer -->
      <div class="flex items-center gap-1.5 mb-1">
        <div class="h-4 w-12 bg-red-100 rounded-xs skeleton-shimmer"></div>
        <div class="h-4 w-24 bg-red-50 rounded skeleton-shimmer"></div>
      </div>

      <!-- Harga besar lockup -->
      <div class="flex items-baseline gap-2">
        <div class="h-6 w-28 bg-gray-300 rounded skeleton-shimmer"></div>
        <div class="h-4 w-20 bg-gray-200 rounded skeleton-shimmer"></div>
      </div>

      <!-- Judul 2 baris -->
      <div class="space-y-1.5 mt-1.5">
        <div class="h-3.5 w-full bg-gray-200 rounded skeleton-shimmer"></div>
        <div class="h-3.5 w-3/4 bg-gray-200 rounded skeleton-shimmer"></div>
      </div>

      <!-- Rating / Social proof -->
      <div class="h-4 flex items-center gap-1.5 mt-2">
        <div class="h-3.5 w-3.5 bg-amber-100 rounded-full skeleton-shimmer"></div>
        <div class="h-3 w-10 bg-gray-200 rounded skeleton-shimmer"></div>
        <div class="h-3 w-16 bg-gray-100 rounded skeleton-shimmer"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Performance: Pakai opacity daripada background-color untuk efisiensi render */
.skeleton-shimmer {
  animation: shimmer 1.5s infinite linear;
  will-change: opacity;
}

@keyframes shimmer {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

/* SEO & CLS: Menjaga ukuran tetap stabil sebelum gambar asli load */
div {
  contain-intrinsic-size: 190px 380px;
  content-visibility: auto;
}
</style>