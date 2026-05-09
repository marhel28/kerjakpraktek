<script setup lang="ts">
import { computed } from 'vue'
import { useWishlistStore } from '~/stores/wishlist'
import { useCookie } from '#app'

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

// Reaktif mengecek status wishlist
const isWishlist = computed(() => wishlistStore.isInWishlist(props.product.id))

const handleToggle = () => {
  const token = useCookie('token').value
  if (!token) {
    // Opsional: Panggil notifikasi/modal login di sini
    alert('Silakan login terlebih dahulu untuk menambah ke wishlist')
    return
  }

  // Trigger action store (Optimistic UI akan langsung berjalan)
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