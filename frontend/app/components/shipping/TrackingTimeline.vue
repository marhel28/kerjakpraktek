<template>
  <div class="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-200">
    <div
      v-for="(item, idx) in manifests"
      :key="idx"
      class="relative"
    >
      <!-- Dot indicator -->
      <span
        class="absolute -left-6 top-1.5 w-4 h-4 rounded-full border-2 flex items-center justify-center bg-white"
        :class="idx === 0 ? 'border-[#03AC0E] ring-4 ring-[#E6F7E9]' : 'border-gray-300'"
      >
        <span
          v-if="idx === 0"
          class="w-2 h-2 rounded-full bg-[#03AC0E]"
        />
      </span>

      <!-- Content -->
      <div class="bg-white border border-gray-100 rounded-lg p-3.5 shadow-xs">
        <div class="flex flex-wrap items-center justify-between gap-2 text-xs mb-1">
          <span class="font-bold text-gray-900 font-['Plus_Jakarta_Sans',sans-serif]">
            {{ item.city || 'Transit Hub' }}
          </span>
          <span class="text-gray-400 font-mono text-[11px]">
            {{ item.date }} {{ item.time }}
          </span>
        </div>
        <p class="text-xs text-gray-600 leading-relaxed font-['Open_Sans',sans-serif]">
          {{ item.description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  manifests: Array<{
    date: string
    time: string
    city?: string
    description: string
  }>
}>()
</script>