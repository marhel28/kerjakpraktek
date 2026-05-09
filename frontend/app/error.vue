<template>
  <div class="min-h-screen bg-white flex flex-col font-sans selection:bg-green-500 selection:text-white">
    
    <header class="bg-white border-b border-gray-100 h-16 flex items-center px-6">
      <div class="max-w-7xl mx-auto w-full flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded bg-[#10B981] flex items-center justify-center text-white">
            <UIcon name="i-lucide-cctv" class="w-4 h-4" />
          </div>
          <span class="font-black tracking-tighter text-xl text-gray-900 uppercase">Pasar CCTV</span>
        </div>
      </div>
    </header>

    <main class="flex-1 flex flex-col items-center justify-center p-6 text-center">
      <div class="max-w-lg w-full flex flex-col items-center">
        
        <div class="relative w-64 h-64 md:w-80 md:h-80 mb-10 animate-float">
          <img 
            src="https://cdn.desa-sidomukti.com/error/Gemini_Generated_Image_hp3fujhp3fujhp3f.png" 
            alt="404 Not Found"
            class="w-full h-full object-contain"
          />
        </div>

        <h1 class="text-3xl md:text-5xl font-black text-[#171717] uppercase tracking-tighter mb-4">
          Waduh, Area Luar Jangkauan!
        </h1>
        <p class="text-sm md:text-base text-gray-500 leading-relaxed mb-10 max-w-md">
          Kamera kami sudah berputar 360 derajat, tapi halaman yang Anda cari tidak ditemukan.
        </p>

        <div class="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
          
          <UButton
            size="xl"
            @click="handleError"
            class="!bg-[#10B981] hover:!bg-[#059669] !text-white px-10 py-4 rounded-2xl font-bold flex items-center justify-center gap-2 shadow-xl shadow-green-500/20 transition-all active:scale-95 w-full sm:w-auto"
          >
            <UIcon name="i-lucide-home" class="w-5 h-5" />
            Kembali ke Beranda
          </UButton>

          <UButton
            size="xl"
            to="/products"
            class="!bg-[#171717] hover:!bg-black !text-white px-10 py-4 rounded-2xl font-bold flex items-center justify-center gap-2 shadow-xl shadow-black/10 transition-all active:scale-95 w-full sm:w-auto"
          >
            <UIcon name="i-lucide-shopping-bag" class="w-5 h-5" />
            Lihat Produk
          </UButton>

        </div>

      </div>
    </main>

    <footer class="py-8 text-center text-[10px] font-bold text-gray-300 uppercase tracking-[0.2em]">
      &copy; {{ new Date().getFullYear() }} Pasar CCTV Marketplace.
    </footer>

  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  error: Object
})

const handleError = () => {
  clearError({ redirect: '/' })
}

useSeoMeta({
  title: '404 - Halaman Tidak Ditemukan | Pasar CCTV',
  robots: 'noindex, nofollow'
})
</script>

<style scoped>
.animate-float {
  animation: float 6s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}
</style>