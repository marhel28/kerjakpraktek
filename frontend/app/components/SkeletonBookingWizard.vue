<script setup lang="ts">
/**
 * Skeleton for Booking Wizard Page
 * Matches exact dimensions of the booking wizard steps
 * - Step indicator
 * - Service selection cards
 * - Package selection
 * - Date/time picker
 * - Address form
 * - Summary sidebar
 */
</script>

<template>
  <div role="status" aria-live="polite" aria-label="Loading booking wizard" class="space-y-6">
    <!-- Step Indicator -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div v-for="i in 4" :key="i" class="flex items-center gap-2">
          <div class="h-8 w-8 rounded-full bg-gray-200 skeleton-shimmer flex items-center justify-center" />
          <div class="h-4 w-16 bg-gray-200 rounded skeleton-shimmer hidden sm:block" />
          <div v-if="i < 4" class="h-1 w-16 bg-gray-200 skeleton-shimmer hidden md:block" />
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="grid lg:grid-cols-12 gap-6">
      <!-- Wizard Form -->
      <div class="lg:col-span-8 space-y-6">
        <!-- Step 1: Service Selection -->
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div class="h-6 w-48 bg-gray-300 rounded skeleton-shimmer" />
            <div class="h-6 w-24 bg-gray-200 rounded skeleton-shimmer" />
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div v-for="i in 3" :key="i" class="p-4 rounded-xl border border-gray-200 bg-white">
              <div class="h-10 w-10 rounded-lg bg-gray-100 skeleton-shimmer mx-auto mb-3" />
              <div class="h-4 w-20 bg-gray-300 rounded skeleton-shimmer mx-auto mb-1" />
              <div class="h-3 w-24 bg-gray-200 rounded skeleton-shimmer mx-auto" />
            </div>
          </div>
        </div>

        <!-- Step 2: Package Selection -->
        <div class="space-y-4">
          <div class="h-6 w-48 bg-gray-300 rounded skeleton-shimmer" />
          <div class="space-y-3">
            <div v-for="i in 3" :key="i" class="p-4 rounded-xl border border-gray-200 bg-white">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 space-y-2">
                  <div class="flex items-center justify-between">
                    <div class="h-5 w-32 bg-gray-300 rounded skeleton-shimmer" />
                    <div class="h-6 w-20 bg-gray-300 rounded skeleton-shimmer" />
                  </div>
                  <div class="h-3 w-40 bg-gray-200 rounded skeleton-shimmer" />
                  <div class="flex items-center gap-2">
                    <div class="h-4 w-4 bg-gray-200 rounded skeleton-shimmer" />
                    <div class="h-3 w-24 bg-gray-200 rounded skeleton-shimmer" />
                  </div>
                </div>
                <div class="h-10 w-10 rounded-lg border-2 border-gray-200 skeleton-shimmer flex-shrink-0" />
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Date & Time -->
        <div class="space-y-4">
          <div class="h-6 w-48 bg-gray-300 rounded skeleton-shimmer" />
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <div class="h-4 w-24 bg-gray-300 rounded skeleton-shimmer" />
              <div class="h-12 w-full bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
            </div>
            <div class="space-y-2">
              <div class="h-4 w-24 bg-gray-300 rounded skeleton-shimmer" />
              <div class="h-12 w-full bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <div v-for="i in 6" :key="i" class="h-10 w-20 sm:w-24 rounded-lg border border-gray-200 bg-white skeleton-shimmer" />
          </div>
        </div>

        <!-- Step 4: Address Form -->
        <div class="space-y-4">
          <div class="h-6 w-48 bg-gray-300 rounded skeleton-shimmer" />
          <div class="space-y-3">
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <div class="h-4 w-24 bg-gray-300 rounded skeleton-shimmer" />
                <div class="h-12 w-full bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
              </div>
              <div class="space-y-1.5">
                <div class="h-4 w-24 bg-gray-300 rounded skeleton-shimmer" />
                <div class="h-12 w-full bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
              </div>
            </div>
            <div class="space-y-1.5">
              <div class="h-4 w-24 bg-gray-300 rounded skeleton-shimmer" />
              <div class="h-12 w-full bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <div class="h-4 w-24 bg-gray-300 rounded skeleton-shimmer" />
                <div class="h-12 w-full bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
              </div>
              <div class="space-y-1.5">
                <div class="h-4 w-24 bg-gray-300 rounded skeleton-shimmer" />
                <div class="h-12 w-full bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
              </div>
            </div>
            <div class="space-y-1.5">
              <div class="h-4 w-24 bg-gray-300 rounded skeleton-shimmer" />
              <div class="h-24 w-full bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
            </div>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex justify-between pt-4 border-t border-gray-200">
          <div class="h-12 w-28 bg-gray-100 rounded-lg border border-gray-200 skeleton-shimmer" />
          <div class="h-12 w-28 bg-primary-500 rounded-lg skeleton-shimmer" />
        </div>
      </div>

      <!-- Summary Sidebar -->
      <div class="lg:col-span-4">
        <div class="sticky top-24 space-y-4">
          <!-- Selected Package Summary -->
          <div class="p-4 rounded-xl bg-gray-50 border border-gray-100 space-y-3">
            <div class="h-5 w-32 bg-gray-300 rounded skeleton-shimmer" />
            <div class="flex items-center justify-between">
              <div class="h-4 w-24 bg-gray-200 rounded skeleton-shimmer" />
              <div class="h-6 w-24 bg-gray-300 rounded skeleton-shimmer" />
            </div>
            <div class="flex items-center justify-between">
              <div class="h-4 w-28 bg-gray-200 rounded skeleton-shimmer" />
              <div class="h-6 w-24 bg-gray-300 rounded skeleton-shimmer" />
            </div>
            <div class="flex items-center justify-between pt-2 border-t border-gray-200">
              <div class="h-5 w-20 bg-gray-300 rounded skeleton-shimmer" />
              <div class="h-6 w-24 bg-primary-500 rounded skeleton-shimmer" />
            </div>
          </div>

          <!-- Addons Summary -->
          <div class="p-4 rounded-xl bg-gray-50 border border-gray-100 space-y-3">
            <div class="h-5 w-32 bg-gray-300 rounded skeleton-shimmer" />
            <div v-for="i in 2" :key="i" class="flex items-center justify-between">
              <div class="h-4 w-28 bg-gray-200 rounded skeleton-shimmer" />
              <div class="h-5 w-20 bg-gray-300 rounded skeleton-shimmer" />
            </div>
            <div class="flex items-center justify-between pt-2 border-t border-gray-200">
              <div class="h-5 w-20 bg-gray-300 rounded skeleton-shimmer" />
              <div class="h-6 w-24 bg-gray-300 rounded skeleton-shimmer" />
            </div>
          </div>

          <!-- Total -->
          <div class="p-4 rounded-xl bg-primary-50 border border-primary-100 space-y-3">
            <div class="flex items-center justify-between">
              <div class="h-5 w-24 bg-primary-600 rounded skeleton-shimmer" />
              <div class="h-7 w-28 bg-primary-600 rounded skeleton-shimmer" />
            </div>
            <div class="flex items-center justify-between pt-2 border-t border-primary-100">
              <div class="h-6 w-20 bg-primary-700 rounded skeleton-shimmer" />
              <div class="h-8 w-32 bg-primary-700 rounded skeleton-shimmer" />
            </div>
            <div class="h-12 w-full bg-primary-600 rounded-lg skeleton-shimmer" />
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

/* CLS Prevention */
div[role="status"] > div {
  contain-intrinsic-size: auto 600px;
  content-visibility: auto;
}

.sticky {
  contain-intrinsic-size: 320px 800px;
}
</style>