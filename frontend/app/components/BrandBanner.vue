<template>
  <section id="brands-section" class="py-16 bg-neutral-50 overflow-hidden">
    <div class="container mx-auto px-4">
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-10 brand-header opacity-0 translate-y-6">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <span class="w-8 h-1 bg-red-600 rounded-full"></span>
            <span class="text-red-600 font-bold text-sm uppercase tracking-widest">Official Partners</span>
          </div>
          <h2 class="text-3xl md:text-4xl font-black text-neutral-900 tracking-tight">
            Brand Mitra Resmi
          </h2>
          <p class="text-neutral-500 mt-2 max-w-xl">
            Kami bekerja sama langsung dengan produsen teknologi keamanan ternama untuk menjamin keaslian produk.
          </p>
        </div>
      </div>

      <div v-if="pending" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        <div v-for="i in 5" :key="i" class="h-80 bg-neutral-200 animate-pulse rounded-2xl"></div>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        <article
          v-for="brand in brands"
          :key="brand.id"
          class="brand-card opacity-0 translate-y-10 flex flex-col h-full bg-white rounded-2xl border border-neutral-200 overflow-hidden hover:shadow-2xl hover:border-red-100 transition-all duration-500 group"
        >
          <NuxtLink :to="`/brands/${brand.route}`" class="relative w-full aspect-square flex items-center justify-center p-8 bg-white overflow-hidden border-b border-neutral-100">
            <NuxtImg
              :src="brand.image"
              :alt="`Logo Resmi ${brand.name}`"
              format="webp"
              width="240"
              height="240"
              loading="lazy"
              class="relative z-10 w-full h-full object-contain filter grayscale group-hover:grayscale-0 group-hover:scale-110 transition-all duration-700 ease-out"
            />
            <div class="absolute inset-0 bg-neutral-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          </NuxtLink> <div class="flex flex-col p-5 flex-1 bg-white">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-1.5">
                <UIcon name="i-heroicons-check-badge-20-solid" class="text-red-600 w-5 h-5" />
                <span class="text-[11px] font-bold text-neutral-400 uppercase tracking-wider">Authorized</span>
              </div>
              <span v-if="brand.featured" class="px-2 py-0.5 bg-amber-100 text-amber-700 text-[9px] font-bold rounded-full uppercase">Top</span>
            </div>

            <h3 class="text-xl font-extrabold text-neutral-900 tracking-tight leading-none mb-4 group-hover:text-red-600 transition-colors">
              {{ brand.name }}
            </h3>

            <div class="mt-auto">
              <a
                :href="`https://wa.me/6281234567890?text=Halo,%20saya%20ingin%20konsultasi%20paket%20${brand.name}`"
                target="_blank"
                class="w-full bg-neutral-900 text-white hover:bg-red-600 font-bold text-xs py-3 rounded-xl flex items-center justify-center gap-2 transition-all duration-300 active:scale-95 shadow-lg shadow-neutral-200"
              >
                Konsultasi Gratis
                <UIcon name="i-heroicons-chat-bubble-left-right-20-solid" class="w-4 h-4" />
              </a>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

interface APIBrand {
  id: string; n: string; s: string; r: string; f: boolean; img: string;
}

interface Brand {
  id: string; name: string; slug: string; route: string; featured: boolean; image: string;
}

const { data: brands, pending } = await useFetch<Brand[]>('/api/logobanner', {
  lazy: true,
  transform: (res: any) => {
    return res.map((b: APIBrand) => ({
      id: b.id,
      name: b.n,
      slug: b.s,
      route: b.r,
      featured: b.f,
      image: b.img
    }))
  }
})

onMounted(() => {
  if (process.client) {
    gsap.registerPlugin(ScrollTrigger)

    const ctx = gsap.context(() => {
      gsap.to('.brand-header', {
        opacity: 1,
        y: 0,
        duration: 1,
        ease: 'expo.out',
        scrollTrigger: {
          trigger: '#brands-section',
          start: 'top 85%',
        }
      })

      gsap.to('.brand-card', {
        opacity: 1,
        y: 0,
        duration: 0.8,
        stagger: 0.1,
        ease: 'back.out(1.2)',
        scrollTrigger: {
          trigger: '#brands-section',
          start: 'top 75%',
        }
      })
    })
  }
})
</script>

<style scoped>
.brand-card {
  will-change: transform, opacity;
}
</style>
