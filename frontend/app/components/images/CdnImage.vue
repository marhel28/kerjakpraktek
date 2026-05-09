<script setup lang="ts">
/**
 * Komponen khusus untuk merender gambar dari CDN Eksternal.
 * Wajib mendefinisikan domain CDN di nuxt.config.ts agar NuxtImg mengizinkannya.
 */

interface Props {
  src: string
  alt: string
  width?: number | string
  height?: number | string
  // Default sizes diset responsif agar HP tidak mendownload gambar resolusi PC
  sizes?: string
  // 'cover' untuk banner, 'contain' untuk produk utuh
  fit?: 'cover' | 'contain' | 'fill' | 'inside' | 'outside'
  // Matikan lazy loading HANYA untuk gambar paling atas (Hero/Banner utama)
  priority?: boolean
  // Custom class dari parent
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  sizes: 'sm:100vw md:50vw lg:33vw xl:25vw', // Responsif default
  fit: 'contain',
  priority: false,
  class: ''
})

// Emit event jika gambar selesai dimuat atau error (opsional untuk skeleton loading di parent)
const emit = defineEmits(['load', 'error'])
</script>

<template>
  <NuxtImg
    :src="props.src"
    :alt="props.alt"
    :width="props.width"
    :height="props.height"
    :sizes="props.sizes"
    :fit="props.fit"
    :loading="props.priority ? 'eager' : 'lazy'"
    :fetchpriority="props.priority ? 'high' : 'auto'"
    format="webp"
    quality="80"
    :class="[
      'block object-center transition-opacity duration-300 ease-in-out',
      props.fit === 'cover' ? 'object-cover' : 'object-contain',
      props.class
    ]"
    @load="emit('load')"
    @error="emit('error')"
  />
</template>
