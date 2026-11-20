<script setup lang="ts">
import { computed } from 'vue'

const defaultBrands = [
  { id: 'hikvision', name: 'Hikvision', image: '/images/hkvision.webp', route: '/brands/hikvision' },
  { id: 'dahua', name: 'Dahua', image: '/images/dahua.webp', route: '/brands/dahua' },
  { id: 'ezviz', name: 'Ezviz', image: '/images/ezviz.webp', route: '/brands/ezviz' },
  { id: 'imou', name: 'Imou', image: '/images/imou.webp', route: '/brands/imou' },
  { id: 'tapo', name: 'Tapo TP-Link', image: '/images/tapo.webp', route: '/brands/tapo' },
  { id: 'tiandy', name: 'Tiandy', image: '/images/tiandy.webp', route: '/brands/tiandy' }
]

const { data: apiBrands } = await useFetch<any[]>('/api/logobanner', {
  server: true,
  lazy: false,
  key: 'brands:showcase',
  transform: (res) => {
    if (!res || !Array.isArray(res) || res.length === 0) return []
    return res.map(brand => ({
      id: brand.id,
      name: brand.n,
      image: brand.img,
      route: brand.r 
    }))
  }
})

interface Props {
  speed?: number 
}

const props = withDefaults(defineProps<Props>(), {
  speed: 24
})

const activeBrands = computed(() => {
  const list = (apiBrands.value && apiBrands.value.length > 0) ? apiBrands.value : defaultBrands
  return [...list, ...list, ...list]
})
</script>

<template>
  <section class="relative flex w-full overflow-hidden bg-white py-6 sm:py-8 border-y border-gray-100 group" aria-label="Brand Resmi Rekanan">
    <div class="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 sm:w-32 bg-gradient-to-r from-white to-transparent"></div>
    <div class="pointer-events-none absolute inset-y-0 right-0 z-10 w-16 sm:w-32 bg-gradient-to-l from-white to-transparent"></div>

    <div
      class="animate-marquee flex w-max items-center hover:[animation-play-state:paused]"
      :style="{ '--marquee-duration': `${speed}s` }"
    >
      <div
        v-for="(brand, index) in activeBrands"
        :key="`${brand.id}-${index}`"
        class="flex w-32 sm:w-44 items-center justify-center px-4 sm:px-8"
      >
        <NuxtLink :to="brand.route" class="block transition-transform duration-300 hover:scale-110">
          <NuxtImg
            :src="brand.image"
            :alt="brand.name"
            loading="lazy"
            width="140"
            height="45"
            class="h-7 sm:h-9 w-auto object-contain opacity-60 hover:opacity-100 transition-opacity duration-300"
          />
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
@keyframes marquee {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(-33.333%, 0, 0); }
}

.animate-marquee {
  display: flex;
  animation: marquee var(--marquee-duration, 24s) linear infinite;
  will-change: transform;
}

@media (prefers-reduced-motion: reduce) {
  .animate-marquee {
    animation-play-state: paused;
  }
}
</style>