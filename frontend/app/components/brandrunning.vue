<script setup lang="ts">
import { computed } from 'vue'

const { data: brandsData } = await useFetch<any[]>('/api/logobanner', {
  server: false,
  lazy: true,
  key: 'brands:showcase', // Gunakan key baru untuk memastikan cache bersih
  transform: (res) => {
    if (!res) return []
    return res.map(brand => ({
      id: brand.id,
      name: brand.n,
      image: brand.img,
      route: brand.r 
    }))
  }
})

interface Props {
  // Nilai lebih kecil = lebih cepat (misal: 15 atau 20)
  speed?: number 
}

const props = withDefaults(defineProps<Props>(), {
  speed: 20 // Dipercepat dari 30s ke 20s
})

const duplicatedBrands = computed(() => {
  const data = brandsData.value || []
  if (data.length === 0) return []
  // Kita gandakan 3x agar pada layar ultra-wide tidak ada celah kosong (gap)
  return [...data, ...data, ...data]
})
</script>

<template>
  <section v-if="brandsData && brandsData.length > 0" class="relative flex w-full overflow-hidden bg-white py-8 border-y border-gray-100 group">

    <div class="pointer-events-none absolute inset-y-0 left-0 z-10 w-20 bg-gradient-to-r from-white to-transparent sm:w-40"></div>
    <div class="pointer-events-none absolute inset-y-0 right-0 z-10 w-20 bg-gradient-to-l from-white to-transparent sm:w-40"></div>

    <div
      class="animate-marquee flex w-max items-center hover:[animation-play-state:paused]"
      :style="{ '--marquee-duration': `${speed}s` }"
    >
      <div
        v-for="(brand, index) in duplicatedBrands"
        :key="`${brand.id}-${index}`"
        class="flex w-32 items-center justify-center px-6 sm:w-48 sm:px-10"
      >
        <NuxtLink :to="brand.route" class="block transition-transform duration-300 hover:scale-110">
          
          <NuxtImg
  :src="brand.image"
  :alt="brand.name"
  loading="lazy"
  width="160"
  height="60"
  class="h-8 md:h-12 w-auto object-contain grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all duration-300"
/>

        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
@keyframes marquee {
  0% {
    /* Menggunakan translate3d untuk memaksa GPU rendering (hardware acceleration) */
    transform: translate3d(0, 0, 0);
  }
  100% {
    /* Geser sepertiga karena kita gandakan 3x, atau -50% jika gandakan 2x */
    transform: translate3d(-33.333%, 0, 0);
  }
}

.animate-marquee {
  display: flex;
  /* linear memastikan kecepatan konstan tanpa jeda */
  animation: marquee var(--marquee-duration, 20s) linear infinite;
  /* Hint ke browser untuk optimasi layer */
  will-change: transform;
}

/* Mengurangi beban CPU saat tab tidak aktif */
@media (prefers-reduced-motion: reduce) {
  .animate-marquee {
    animation-play-state: paused;
  }
}
</style>