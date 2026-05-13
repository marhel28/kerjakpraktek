<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  src?: string | null
  alt?: string
  aspectClass?: string
}>()

const isOpen = ref(false)
</script>

<template>
  <div>
    <!-- Thumbnail -->
    <div 
      class="relative overflow-hidden bg-gray-100 group cursor-pointer flex items-center justify-center rounded border border-gray-100"
      :class="aspectClass || 'aspect-video w-full'"
      @click="src ? isOpen = true : null"
      @click.stop
    >
      <img v-if="src" :src="src" :alt="alt || 'Preview'" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy" />
      <div v-else class="text-gray-400 flex flex-col items-center justify-center gap-1">
        <UIcon name="i-heroicons-photo" class="w-8 h-8 opacity-40" />
        <span class="text-[9px] font-bold tracking-widest uppercase opacity-40">No Image</span>
      </div>
      
      <!-- Hover Overlay -->
      <div v-if="src" class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
        <UIcon name="i-heroicons-arrows-pointing-out" class="w-6 h-6 text-white drop-shadow" />
      </div>
    </div>

    <!-- Modal Lightbox -->
    <Teleport to="body">
      <transition name="fade-lightbox">
        <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 p-4 sm:p-8 backdrop-blur-sm" @click.self="isOpen = false">
          <button @click="isOpen = false" class="absolute top-4 right-4 sm:top-6 sm:right-6 w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-colors">
            <UIcon name="i-heroicons-x-mark" class="w-6 h-6" />
          </button>
          
          <img v-if="src" :src="src" :alt="alt" class="max-w-full max-h-full object-contain rounded-lg shadow-2xl" />
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<style scoped>
.fade-lightbox-enter-active,
.fade-lightbox-leave-active {
  transition: opacity 0.3s ease;
}
.fade-lightbox-enter-from,
.fade-lightbox-leave-to {
  opacity: 0;
}
</style>
