<script setup lang="ts">
/**
 * Skeleton for Product Detail Page
 * Matches exact dimensions of ProductDetail.vue to prevent CLS
 * - Gallery area: aspect-[4/5] with thumbnails
 * - Title, price, rating, description sections
 * - Addon picker area
 * - Recommendation carousel area
 */
</script>

<template>
  <div role="status" aria-live="polite" aria-label="Loading product details" class="space-y-6 md:space-y-8">
    <!-- Gallery Section -->
    <div class="grid md:grid-cols-12 gap-4 md:gap-6">
      <!-- Main Image -->
      <div class="md:col-span-7">
        <div class="relative aspect-[4/5] w-full rounded-xl bg-gray-100 overflow-hidden">
          <div class="skeleton-shimmer absolute inset-0 bg-gray-200" />
        </div>
        <!-- Thumbnails -->
        <div class="flex gap-2 mt-3 overflow-x-auto pb-2">
          <div v-for="i in 5" :key="i" class="flex-shrink-0 w-20 h-20 rounded-lg bg-gray-100 overflow-hidden">
            <div class="skeleton-shimmer absolute inset-0 bg-gray-200" />
          </div>
        </div>
      </div>

      <!-- Info Panel -->
      <div class="md:col-span-5 space-y-4">
        <!-- Category breadcrumb -->
        <div class="h-4 w-48 bg-gray-200 rounded skeleton-shimmer" />

        <!-- Title (2-3 lines) -->
        <div class="space-y-2">
          <div class="h-6 w-full bg-gray-300 rounded skeleton-shimmer" />
          <div class="h-6 w-3/4 bg-gray-200 rounded skeleton-shimmer" />
          <div class="h-6 w-1/2 bg-gray-200 rounded skeleton-shimmer" />
        </div>

        <!-- Rating + Reviews -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1">
            <div v-for="i in 5" :key="i" class="h-5 w-5 bg-amber-100 rounded skeleton-shimmer" />
          </div>
          <div class="h-5 w-24 bg-gray-200 rounded skeleton-shimmer" />
          <div class="h-5 w-20 bg-gray-200 rounded skeleton-shimmer" />
        </div>

        <!-- Price Block -->
        <div class="space-y-2 p-4 rounded-xl bg-gray-50 border border-gray-100">
          <div class="flex items-baseline gap-3">
            <div class="h-8 w-32 bg-gray-300 rounded skeleton-shimmer" />
            <div class="h-5 w-20 bg-gray-200 rounded skeleton-shimmer" />
          </div>
          <div class="h-4 w-40 bg-gray-200 rounded skeleton-shimmer" />
        </div>

        <!-- Stock / Badge -->
        <div class="h-6 w-36 bg-green-50 rounded skeleton-shimmer" />

        <!-- Quantity Selector -->
        <div class="h-12 w-48 bg-gray-100 rounded-lg skeleton-shimmer" />

        <!-- Action Buttons -->
        <div class="grid grid-cols-2 gap-3">
          <div class="h-12 bg-primary-500 rounded-lg skeleton-shimmer" />
          <div class="h-12 bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
        </div>

        <!-- Meta info -->
        <div class="space-y-2 pt-2 border-t border-gray-100">
          <div class="flex items-center gap-2">
            <div class="h-4 w-4 bg-gray-200 rounded skeleton-shimmer" />
            <div class="h-4 w-28 bg-gray-200 rounded skeleton-shimmer" />
          </div>
          <div class="flex items-center gap-2">
            <div class="h-4 w-4 bg-gray-200 rounded skeleton-shimmer" />
            <div class="h-4 w-32 bg-gray-200 rounded skeleton-shimmer" />
          </div>
        </div>
      </div>
    </div>

    <!-- Description / Specs Tabs Area -->
    <div class="space-y-4">
      <div class="flex gap-4 border-b border-gray-200">
        <div class="h-8 w-24 bg-gray-100 rounded-t-lg skeleton-shimmer" />
        <div class="h-8 w-28 bg-gray-100 rounded-t-lg skeleton-shimmer" />
        <div class="h-8 w-32 bg-gray-100 rounded-t-lg skeleton-shimmer" />
      </div>
      <div class="space-y-3 pt-4">
        <div class="h-5 w-full bg-gray-200 rounded skeleton-shimmer" />
        <div class="h-5 w-full bg-gray-200 rounded skeleton-shimmer" />
        <div class="h-5 w-3/4 bg-gray-200 rounded skeleton-shimmer" />
        <div class="h-5 w-1/2 bg-gray-200 rounded skeleton-shimmer" />
        <div class="h-5 w-full bg-gray-200 rounded skeleton-shimmer" />
        <div class="h-5 w-full bg-gray-200 rounded skeleton-shimmer" />
        <div class="h-5 w-2/3 bg-gray-200 rounded skeleton-shimmer" />
      </div>
    </div>

    <!-- Addon Picker Section -->
    <div class="space-y-4 p-4 rounded-xl bg-gray-50 border border-gray-100">
      <div class="flex items-center justify-between">
        <div class="h-5 w-36 bg-gray-300 rounded skeleton-shimmer" />
        <div class="h-5 w-24 bg-gray-200 rounded skeleton-shimmer" />
      </div>
      <div class="space-y-3 mt-4">
        <div v-for="i in 3" :key="i" class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100">
          <div class="space-y-1">
            <div class="h-4 w-40 bg-gray-200 rounded skeleton-shimmer" />
            <div class="h-3 w-32 bg-gray-100 rounded skeleton-shimmer" />
          </div>
          <div class="flex items-center gap-2">
            <div class="h-6 w-6 bg-gray-200 rounded skeleton-shimmer" />
            <div class="h-5 w-16 bg-gray-300 rounded skeleton-shimmer" />
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendations Carousel -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="h-6 w-40 bg-gray-300 rounded skeleton-shimmer" />
        <div class="h-6 w-20 bg-gray-200 rounded skeleton-shimmer" />
      </div>
      <div class="flex gap-4 overflow-x-auto pb-4">
        <div v-for="i in 4" :key="i" class="flex-shrink-0 w-64 flex flex-col">
          <div class="aspect-[4/5] w-full rounded-lg bg-gray-100 overflow-hidden">
            <div class="skeleton-shimmer absolute inset-0 bg-gray-200" />
          </div>
          <div class="space-y-1.5 mt-2">
            <div class="h-3.5 w-full bg-gray-200 rounded skeleton-shimmer" />
            <div class="h-3.5 w-3/4 bg-gray-200 rounded skeleton-shimmer" />
            <div class="h-5 w-24 bg-gray-300 rounded skeleton-shimmer" />
          </div>
        </div>
      </div>
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

/* CLS Prevention: Reserve exact space */
div {
  contain-intrinsic-size: auto 400px;
  content-visibility: auto;
}

/* Specific intrinsic sizes for major sections */
.aspect-\[4\/5\] {
  contain-intrinsic-size: 400px 500px;
}

.flex-shrink-0.w-64 {
  contain-intrinsic-size: 256px 400px;
}
</style>