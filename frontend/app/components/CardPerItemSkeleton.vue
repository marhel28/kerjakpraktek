<script setup lang="ts">
/**
 * Skeleton Card Produk Optimized
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
    class="flex flex-col h-full w-full bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm isolation-auto"
  >
    <div class="relative aspect-square w-full bg-gray-100 overflow-hidden">
      <div class="skeleton-shimmer absolute inset-0"></div>
      <div class="absolute top-2 left-2 h-4 w-12 bg-gray-200 rounded-sm"></div>
    </div>

    <div class="flex flex-1 flex-col p-2 sm:p-3">
      
      <div class="space-y-2 mb-3">
        <div class="h-3.5 w-full bg-gray-200 rounded-md skeleton-shimmer"></div>
        <div class="h-3.5 w-2/3 bg-gray-200 rounded-md skeleton-shimmer"></div>
      </div>

      <div class="h-5 w-28 bg-gray-300 rounded-md skeleton-shimmer mb-2"></div>

      <div class="flex items-center gap-1.5 mb-3">
        <div class="h-4 w-7 bg-red-50 rounded-sm skeleton-shimmer"></div>
        <div class="h-3 w-16 bg-gray-100 rounded-md skeleton-shimmer"></div>
      </div>

      <div class="mt-auto space-y-2">
        <div class="flex items-center gap-1.5">
          <div class="h-4 w-4 bg-gray-200 rounded-full skeleton-shimmer"></div>
          <div class="h-3 w-20 bg-gray-100 rounded-md skeleton-shimmer"></div>
        </div>
        <div class="flex items-center gap-1">
          <div class="h-3 w-3 bg-yellow-100 rounded-full skeleton-shimmer"></div>
          <div class="h-3 w-24 bg-gray-100 rounded-md skeleton-shimmer"></div>
        </div>
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