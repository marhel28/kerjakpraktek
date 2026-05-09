<template>
  <div class="w-full max-w-7xl mx-auto  py-8">

    <ul class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <li v-for="item in categories" :key="item.name">
        <NuxtLink
          :to="item.link"
          class="group relative flex flex-col items-center justify-center p-6 bg-white border border-neutral-100 rounded-2xl shadow-sm transition-all duration-300 hover:shadow-xl hover:border-primary-500 hover:-translate-y-1"
        >
          <div class="w-16 h-16 flex items-center justify-center rounded-full bg-neutral-50 group-hover:bg-primary-50 transition-colors duration-300 mb-4">
            <UIcon
              :name="item.icon"
              class="w-10 h-10 text-3xl text-neutral-600 group-hover:text-primary-600 transition-colors duration-300"
            />
          </div>

          <span class="text-sm font-bold text-neutral-800 group-hover:text-primary-700 text-center tracking-tight leading-snug">
            {{ item.name }}
          </span>

          <div class="absolute inset-0 rounded-2xl bg-linear-to-tr from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 pointer-events-none"></div>
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<script setup>
// List kategori dengan icon Lucide (Nuxt Icon)
const categories = [
  {
    name: 'Paket CCTV',
    icon: 'i-lucide-package-check',
    link: '/category/paket-cctv'
  },
  {
    name: 'Kamera CCTV',
    icon: 'i-lucide-camera',
    link: '/category/kamera-cctv'
  },
  {
    name: 'NVR / DVR',
    icon: 'i-lucide-database',
    link: '/category/dvr-nvr'
  },
  {
    name: 'Aksesoris',
    icon: 'i-lucide-cable',
    link: '/category/aksesoris'
  },
  {
    name: 'Hard Drive',
    icon: 'i-lucide-hard-drive',
    link: '/category/storage'
  }
]
</script>

<style scoped>
/* Menyesuaikan tone dengan marketplace Padjajaran */
.text-primary-600 {
  color: #000; /* Menggunakan warna hitam pekat sesuai header Anda */
}
.group:hover .text-primary-600,
.group:hover .text-primary-700 {
  color: #ef4444; /* Warna merah (Red 600) untuk hover agar senada dengan teks 'PROMO' */
}
.bg-primary-50 {
  background-color: #fef2f2; /* Warna merah sangat muda untuk background hover icon */
}
.hover\:border-primary-500:hover {
  border-color: #ef4444;
}
</style>
