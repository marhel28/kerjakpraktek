<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  category?: string | null
  cameraCount?: number
  brandName?: string | null
}>()

// State Logic
const isIdle = ref(false)
let idleTimer: ReturnType<typeof setTimeout>

onMounted(() => {
  // Munculkan CTA jika user diam di halaman selama 10 detik
  idleTimer = setTimeout(() => {
    isIdle.value = true
  }, 10000)
})

onUnmounted(() => {
  clearTimeout(idleTimer)
})

// Logika Tampil: Tampil jika config belum selesai ATAU sudah idle
const isConfigIncomplete = computed(() => {
  return !props.category || !props.cameraCount || !props.brandName
})

const isVisible = computed(() => {
  return isConfigIncomplete.value || isIdle.value
})

// Dynamic WhatsApp Message Link
const whatsappLink = computed(() => {
  const cat = props.category ? props.category.toUpperCase() : 'Belum pasti'
  const cam = props.cameraCount ? `${props.cameraCount} Titik` : 'Belum tahu'
  const brand = props.brandName || 'Belum ada preferensi'

  const message = `Halo Teknisi PasarCctv, saya sedang mencoba merakit paket instalasi di website namun butuh bantuan konsultasi:\n\n*Draft Konfigurasi:*\n- Area: ${cat}\n- Kebutuhan: ${cam}\n- Brand: ${brand}\n\nBisa bantu berikan rekomendasi terbaik untuk saya?`
  
  // Ganti dengan nomor WhatsApp CS / Sales asli
  const phoneNumber = '6281234567890' 
  return `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`
})
</script>

<template>
  <Transition name="fade-slide">
    <div 
      v-if="isVisible" 
      class="relative overflow-hidden bg-zinc-900 rounded-2xl p-6 md:p-8 shadow-2xl ring-1 ring-white/10 mt-8 group"
    >
      <div class="absolute -top-24 -right-24 w-64 h-64 bg-green-500/10 rounded-full blur-[80px] pointer-events-none transition-transform duration-1000 group-hover:scale-125"></div>
      <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-emerald-500/10 rounded-full blur-[80px] pointer-events-none transition-transform duration-1000 group-hover:scale-125"></div>

      <div class="absolute inset-0 opacity-[0.03] mix-blend-overlay pointer-events-none" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>

      <div class="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 md:gap-8">
        
        <div class="flex items-start md:items-center gap-5">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-zinc-800 to-zinc-950 ring-1 ring-white/5 flex items-center justify-center flex-shrink-0 shadow-inner group-hover:shadow-green-500/10 transition-shadow duration-500">
            <Icon name="lucide:headset" class="w-6 h-6 text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]" />
          </div>
          
          <div>
            <div class="flex flex-wrap items-center gap-3 mb-1.5">
              <h3 class="text-base font-black text-white uppercase tracking-tight">Butuh Bantuan Teknisi?</h3>
              <span class="px-2.5 py-1 rounded-md text-[9px] font-black uppercase tracking-widest bg-green-500/10 text-green-400 ring-1 ring-green-500/20 flex items-center gap-1.5">
                <span class="relative flex w-1.5 h-1.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full w-1.5 h-1.5 bg-green-500"></span>
                </span>
                Online
              </span>
            </div>
            <p class="text-sm font-medium text-zinc-400 leading-relaxed max-w-md">
              Tim spesialis kami siap membantu menghitung kebutuhan titik kamera dan merekomendasikan spesifikasi terbaik untuk area Anda.
            </p>
          </div>
        </div>

        <a 
          :href="whatsappLink" 
          target="_blank"
          rel="noopener noreferrer"
          class="w-full md:w-auto flex items-center justify-center gap-2.5 bg-[#25D366] hover:bg-[#20bd5a] text-white px-7 py-4 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-300 shadow-[0_8px_20px_rgba(37,211,102,0.2)] hover:shadow-[0_12px_25px_rgba(37,211,102,0.35)] hover:-translate-y-0.5 active:scale-95 active:translate-y-0 flex-shrink-0"
        >
          <Icon name="bi:whatsapp" class="w-4 h-4" />
          Tanya Spesialis
        </a>

      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Transisi masuk yang elegan seperti Apple / Vercel */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}
</style>