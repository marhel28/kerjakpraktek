<template>
  <ClientOnly>
    <div v-if="isVisible" class="fixed inset-0 z-[999] flex items-center justify-center p-4">
      <!-- Backdrop with blur -->
      <div 
        class="absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity duration-500"
        :class="isAnimating ? 'opacity-100' : 'opacity-0'"
        @click="close"
      ></div>

      <!-- Modal Card -->
      <div 
        class="relative max-w-lg w-full bg-transparent transition-all duration-500 transform flex flex-col items-center"
        :class="isAnimating ? 'scale-100 opacity-100' : 'scale-95 opacity-0'"
      >
        <!-- Close Button (Premium hover effect) -->
        <button 
          @click="close"
          class="absolute -top-12 right-0 bg-white/10 hover:bg-white/20 text-white rounded-full p-2.5 backdrop-blur-md border border-white/15 transition-all hover:scale-110 active:scale-95 cursor-pointer flex items-center justify-center focus:outline-none"
          aria-label="Tutup promo"
        >
          <UIcon name="i-heroicons-x-mark" class="w-6 h-6" />
        </button>

        <!-- Banner Content -->
        <NuxtLink 
          :to="promoData.route || '#'" 
          @click="handleNavigate"
          class="block w-full max-h-[75vh] rounded-3xl overflow-hidden border border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.3)] relative group cursor-pointer"
        >
          <img 
            :src="promoData.image_url" 
            alt="Promo Utama" 
            class="w-full h-auto object-contain select-none group-hover:scale-[1.015] transition-transform duration-500 rounded-3xl"
          />
          <!-- Hover overlay -->
          <div v-if="promoData.route" class="absolute inset-0 bg-black/10 group-hover:bg-black/0 transition-colors duration-300" />
        </NuxtLink>
      </div>
    </div>
  </ClientOnly>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isVisible = ref(false)
const isAnimating = ref(false)
const promoData = ref({
  image_url: '',
  route: '',
  is_active: false
})

onMounted(async () => {
  // Check session cache
  const closedInSession = sessionStorage.getItem('promo_popup_closed')
  if (closedInSession === 'true') return

  try {
    const res: any = await $fetch('/api/settings/promo-popup')
    if (res && res.success && res.data && res.data.is_active && res.data.image_url) {
      promoData.value = res.data
      
      // Delay slightly for smooth page entrance
      setTimeout(() => {
        isVisible.value = true
        // Animate entrance
        setTimeout(() => {
          isAnimating.value = true
        }, 50)
      }, 1000)
    }
  } catch (err) {
    console.error('Gagal mengambil promo popup:', err)
  }
})

const close = () => {
  isAnimating.value = false
  sessionStorage.setItem('promo_popup_closed', 'true')
  setTimeout(() => {
    isVisible.value = false
  }, 400)
}

const handleNavigate = (e: MouseEvent) => {
  if (!promoData.value.route) {
    e.preventDefault()
    return
  }
  
  // Close the popup when navigating
  close()
}
</script>
