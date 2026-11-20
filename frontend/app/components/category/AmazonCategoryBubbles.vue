<script setup lang="ts">
import { ref } from 'vue'

interface BubbleItem {
  slug: string
  name: string
  count?: number
  dealLabel?: string
}

const props = defineProps<{
  items: BubbleItem[]
  activeSlug: string
}>()

const emit = defineEmits<{
  (e: 'select', slug: string): void
}>()

const scrollContainer = ref<HTMLElement | null>(null)

const scroll = (direction: 'left' | 'right') => {
  if (!scrollContainer.value) return
  const offset = direction === 'left' ? -240 : 240
  scrollContainer.value.scrollBy({ left: offset, behavior: 'smooth' })
}
</script>

<template>
  <nav
    v-if="items.length"
    class="relative w-full bg-white border-y border-neutral-200 py-2.5 px-3 md:px-6 select-none"
    aria-label="Filter subkategori cepat"
  >
    <div class="max-w-[1400px] mx-auto relative flex items-center">
      <!-- Left scroll control -->
      <button
        type="button"
        class="hidden md:flex absolute -left-2 z-10 w-8 h-8 rounded-full bg-white border border-neutral-300 shadow-sm items-center justify-center text-neutral-700 hover:bg-neutral-50 active:scale-95 transition-all"
        aria-label="Scroll subkategori ke kiri"
        @click="scroll('left')"
      >
        <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
      </button>

      <!-- Scrollable pills rail -->
      <div
        ref="scrollContainer"
        class="flex items-center gap-2 overflow-x-auto no-scrollbar scroll-smooth snap-x py-0.5 px-1 w-full"
      >
        <button
          v-for="item in items"
          :key="item.slug"
          type="button"
          class="shrink-0 snap-start inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold border transition-all"
          :class="[
            activeSlug === item.slug
              ? 'bg-[#0F1111] text-white border-[#0F1111] shadow-none'
              : 'bg-neutral-50 text-neutral-800 border-neutral-300 hover:bg-neutral-100 hover:border-neutral-400'
          ]"
          @click="emit('select', item.slug)"
        >
          <span>{{ item.name }}</span>
          <span
            v-if="item.dealLabel"
            class="px-1.5 py-0.2 text-[10px] font-bold uppercase rounded tracking-tight"
            :class="activeSlug === item.slug ? 'bg-amber-400 text-neutral-950' : 'bg-red-600 text-white'"
          >
            {{ item.dealLabel }}
          </span>
          <span
            v-else-if="item.count !== undefined"
            class="text-[11px] opacity-70"
          >
            ({{ item.count }})
          </span>
        </button>
      </div>

      <!-- Right scroll control -->
      <button
        type="button"
        class="hidden md:flex absolute -right-2 z-10 w-8 h-8 rounded-full bg-white border border-neutral-300 shadow-sm items-center justify-center text-neutral-700 hover:bg-neutral-50 active:scale-95 transition-all"
        aria-label="Scroll subkategori ke kanan"
        @click="scroll('right')"
      >
        <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
      </button>
    </div>
  </nav>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>