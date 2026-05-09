<script setup lang="ts">
import { useCompareStore } from '~/stores/compare'

const compareStore = useCompareStore()
</script>

<template>
  <ClientOnly>
    <Transition
      enter-active-class="transition duration-500 ease-out"
      enter-from-class="transform translate-x-12 opacity-0"
      enter-to-class="transform translate-x-0 opacity-100"
      leave-active-class="transition duration-300 ease-in"
      leave-from-class="transform translate-x-12 opacity-0"
    >
      <NuxtLink
        v-if="compareStore.count > 0"
        to="/compare"
        class="fixed z-[100] right-0 top-1/2 -translate-y-1/2 bg-white shadow-[0_4px_20px_rgba(0,0,0,0.15)] border border-gray-200 border-r-0 rounded-l-2xl p-3 flex flex-col items-center gap-1 hover:-translate-x-2 transition-transform duration-300 group cursor-pointer"
        aria-label="Lihat Perbandingan Produk"
      >
        <div class="relative">
          <Icon
            name="i-heroicons-scale"
            class="text-2xl text-gray-700 group-hover:text-blue-600 transition-colors"
          />
          <span
            class="absolute -top-2 -right-2 bg-red-500 text-white text-[10px] font-black w-5 h-5 flex items-center justify-center rounded-full border-2 border-white shadow-sm"
          >
            {{ compareStore.count }}
          </span>
        </div>

        <span class="text-[10px] font-bold uppercase tracking-widest text-gray-500 group-hover:text-blue-600 mt-1" style="writing-mode: vertical-rl; text-orientation: mixed;">
          Bandingkan
        </span>
      </NuxtLink>
    </Transition>
  </ClientOnly>
</template>
