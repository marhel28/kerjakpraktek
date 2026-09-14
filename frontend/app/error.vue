<template>
  <div class="min-h-screen bg-slate-50/70 flex flex-col font-sans selection:bg-[#03AC0E] selection:text-white">
    
    <!-- Header -->
    <header class="bg-white border-b border-gray-100 h-16 flex items-center px-6 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto w-full flex items-center justify-between">
        <NuxtLink to="/" class="flex items-center gap-2 group transition-transform active:scale-95">
          <img src="/pasarcctv.png" alt="PasarCctv" class="h-8 w-auto object-contain" />
        </NuxtLink>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex items-center justify-center p-4 md:p-8">
      <div class="max-w-4xl w-full bg-white shadow-[0_10px_40px_rgba(0,0,0,0.03)] border border-gray-100 rounded-3xl p-6 md:p-12 flex flex-col md:flex-row items-center gap-8 md:gap-12">
        
        <!-- Illustration Left Side -->
        <div class="w-full md:w-1/2 flex justify-center">
          <div class="relative w-64 h-64 md:w-80 md:h-80 animate-float">
            <img 
              src="/images/error_404.png" 
              alt="404 Not Found"
              class="w-full h-full object-contain mix-blend-multiply"
            />
          </div>
        </div>

        <!-- Info Right Side -->
        <div class="w-full md:w-1/2 flex flex-col items-start text-left">
          
          <!-- Status Badge -->
          <span class="bg-red-50 text-red-600 border border-red-100 px-3 py-1 rounded-full text-[11px] font-black uppercase tracking-widest mb-4">
            Error {{ error?.statusCode || 404 }}
          </span>

          <!-- Heading -->
          <h1 class="text-2xl md:text-3xl font-black text-gray-900 uppercase tracking-tight mb-3">
            {{ error?.statusCode === 404 ? 'Waduh, Area Luar Jangkauan!' : 'Ups, Terjadi Kendala Sistem!' }}
          </h1>
          
          <p class="text-xs md:text-sm text-gray-500 leading-relaxed mb-6">
            {{ error?.statusCode === 404 
              ? 'Kamera kami sudah berputar 360 derajat, tetapi halaman yang Kakak cari tidak dapat ditemukan. Silakan gunakan pencarian di bawah untuk mencari produk.' 
              : 'Sistem kami mendeteksi sedikit kendala teknis. Mohon maaf atas ketidaknyamanan ini Kak.' }}
          </p>

          <!-- Search Widget -->
          <div class="w-full mb-6">
            <div class="relative w-full max-w-md">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Cari CCTV, kabel, DVR, dll..."
                class="w-full bg-gray-50 border border-gray-200 focus:border-[#03AC0E] focus:ring-2 focus:ring-green-100 rounded-xl py-3 px-4 pl-11 text-xs md:text-sm font-semibold transition-all outline-none text-gray-800"
                @keyup.enter="handleSearch"
              />
              <UIcon
                name="i-heroicons-magnifying-glass"
                class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none"
              />
              <button
                @click="handleSearch"
                class="absolute right-2 top-1/2 -translate-y-1/2 bg-[#03AC0E] hover:bg-[#028C0B] text-white px-4 py-1.5 rounded-lg text-xs font-bold transition-colors cursor-pointer border-0"
              >
                Cari
              </button>
            </div>

            <!-- Popular Tags -->
            <div class="flex flex-wrap items-center gap-1.5 mt-3">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wide mr-1">Populer:</span>
              <button
                v-for="tag in popularTags"
                :key="tag"
                @click="handleTagClick(tag)"
                class="text-[10px] bg-gray-50 hover:bg-green-50 hover:text-[#03AC0E] hover:border-green-200 border border-gray-200/60 px-2.5 py-1 rounded-lg text-gray-600 font-bold transition-all cursor-pointer"
              >
                {{ tag }}
              </button>
            </div>
          </div>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row items-center gap-3 w-full max-w-md border-t border-gray-100 pt-6">
            <button
              @click="handleError"
              class="w-full sm:w-auto bg-[#03AC0E] hover:bg-[#028C0B] text-white px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider transition-all hover:scale-102 active:scale-98 shadow-md shadow-green-500/10 flex items-center justify-center gap-2 cursor-pointer border-0"
            >
              <UIcon name="i-heroicons-home" class="w-4 h-4" />
              Ke Beranda
            </button>

            <NuxtLink
              to="/search"
              class="w-full sm:w-auto bg-gray-900 hover:bg-black text-white px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider transition-all hover:scale-102 active:scale-98 shadow-md shadow-black/10 flex items-center justify-center gap-2 cursor-pointer text-center"
            >
              <UIcon name="i-heroicons-shopping-bag" class="w-4 h-4" />
              Semua Produk
            </NuxtLink>
          </div>

        </div>
      </div>
    </main>

    <!-- Help & Footer Links -->
    <div class="bg-white border-t border-gray-100 py-6 px-6">
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-5 text-[11px] font-bold text-gray-500 uppercase tracking-wider">
          <NuxtLink to="/track" class="hover:text-[#03AC0E] transition-colors">Lacak Pesanan</NuxtLink>
          <div class="w-1.5 h-1.5 bg-gray-300 rounded-full"></div>
          <NuxtLink to="/help" class="hover:text-[#03AC0E] transition-colors">Pusat Bantuan</NuxtLink>
          <div class="w-1.5 h-1.5 bg-gray-300 rounded-full"></div>
          <NuxtLink to="/contact" class="hover:text-[#03AC0E] transition-colors">Hubungi Support</NuxtLink>
        </div>
        <p class="text-[9px] font-black text-gray-300 uppercase tracking-[0.2em]">
          &copy; {{ new Date().getFullYear() }} PasarCCTV. All Rights Reserved.
        </p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  error: Object
})

const router = useRouter()
const searchQuery = ref('')
const popularTags = ['Paket CCTV', 'IP Camera', 'Ezviz', 'Dahua', 'Kabel Coaxial']

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  clearError()
  router.push({
    path: '/search',
    query: { q: searchQuery.value.trim() }
  })
}

const handleTagClick = (tag: string) => {
  clearError()
  router.push({
    path: '/search',
    query: { q: tag }
  })
}

const handleError = () => {
  clearError({ redirect: '/' })
}

useSeoMeta({
  title: 'Halaman Tidak Ditemukan | PasarCCTV',
  robots: 'noindex, nofollow'
})
</script>

<style scoped>
.animate-float {
  animation: float 6s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}
</style>