<script setup lang="ts">
import { computed } from 'vue'
import { useWishlistStore } from '~/stores/wishlist'
import { useCookie, navigateTo } from '#app'

// Gunakan Toast bawaan Nuxt UI
const toast = useToast() 

interface Props {
  product: {
    id: string | number
    image: string
    title: string
    price: number
    brand?: string
  }
}

const props = defineProps<Props>()
const wishlistStore = useWishlistStore()

const isWishlist = computed(() => wishlistStore.isInWishlist(props.product.id))

const handleToggle = () => {
  const token = useCookie('token').value
  
  // 🚨 HANDLER JIKA BELUM LOGIN
  if (!token) {
    toast.add({
      title: 'Akses Ditolak',
      description: 'Kamu harus login terlebih dahulu untuk menyimpan wishlist.',
      icon: 'i-heroicons-exclamation-circle',
      color: 'red'
    })
    
    // Redirect ke halaman login (sesuaikan path dengan routemu)
    return navigateTo('/login') 
  }

  // Lanjut eksekusi jika token ada
  wishlistStore.toggle(props.product)
}
</script>

<template>
  <UButton
    color="white"
    variant="solid"
    :icon="isWishlist ? 'i-heroicons-heart-20-solid' : 'i-heroicons-heart'"
    class="rounded-full shadow-md bg-white/90 backdrop-blur-md hover:scale-110 active:scale-95 transition-all"
    :class="isWishlist ? 'text-red-500' : 'text-gray-500 hover:text-red-500'"
    square
    aria-label="Toggle Wishlist"
    @click.prevent.stop="handleToggle"
  />
</template>