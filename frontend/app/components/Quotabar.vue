<template>
    <div>
      <div class="flex items-center justify-between mb-1">
        <span class="text-[10px] text-gray-400">Terjual</span>
        <span :class="['text-[10px] font-medium', percentage > 80 ? 'text-red-500' : 'text-gray-500']">
          {{ percentage }}%
        </span>
      </div>
      <div class="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
        <div
          :class="['h-full rounded-full transition-all duration-500', barColor]"
          :style="{ width: `${percentage}%` }"
        />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  const props = defineProps<{ used: number; total: number | null }>()
  
  const percentage = computed(() => {
    if (!props.total) return 0
    return Math.min(Math.round((props.used / props.total) * 100), 100)
  })
  
  const barColor = computed(() => {
    if (percentage.value > 80) return 'bg-red-500'
    if (percentage.value > 50) return 'bg-orange-400'
    return 'bg-[#22c55e]'
  })
  </script>