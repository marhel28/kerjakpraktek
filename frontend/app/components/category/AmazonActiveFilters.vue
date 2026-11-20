<script setup lang="ts">
export interface FilterChip {
  key: string
  label: string
  displayValue: string
}

defineProps<{
  chips: FilterChip[]
  totalProducts: number
}>()

const emit = defineEmits<{
  (e: 'remove', chip: FilterChip): void
  (e: 'clear'): void
}>()
</script>

<template>
  <div
    v-if="chips.length > 0"
    class="flex flex-wrap items-center gap-2 py-2 px-1 text-xs text-neutral-800"
    aria-label="Filter aktif"
  >
    <span class="font-semibold text-neutral-600 mr-1">Filter Aktif:</span>

    <button
      v-for="chip in chips"
      :key="chip.key"
      type="button"
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white border border-slate-200 rounded-lg hover:border-[#03AC0E] hover:bg-[#E6F7E9]/40 transition-colors group shadow-xs"
      @click="emit('remove', chip)"
    >
      <span class="text-slate-500 font-medium">{{ chip.label }}:</span>
      <span class="font-bold text-slate-900">{{ chip.displayValue }}</span>
      <UIcon name="i-heroicons-x-mark" class="w-3.5 h-3.5 text-slate-400 group-hover:text-red-600 transition-colors" />
    </button>

    <button
      type="button"
      class="text-xs font-semibold text-[#03AC0E] hover:text-[#02930C] hover:underline ml-2"
      @click="emit('clear')"
    >
      Hapus Semua
    </button>
  </div>
</template>