<template>
  <button
    @click.prevent="handleAddToCart"
    :disabled="loading"
    class="w-full flex items-center justify-center gap-2 py-2.5 border-2 border-gray-900 rounded-xl text-gray-900 font-bold text-xs uppercase tracking-widest transition-all active:scale-[0.98]"
    :class="[
      loading 
        ? 'bg-gray-100 border-gray-300 text-gray-400 cursor-wait' 
        : 'hover:bg-gray-900 hover:text-white bg-white'
    ]"
  >
    <Icon v-if="loading" name="lucide:loader-2" size="14" class="animate-spin" />
    <Icon v-else name="lucide:shopping-cart" size="14" />
    {{ loading ? 'Memproses...' : '+ Keranjang' }}
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useCartStore } from '~/stores/cart'

const props = defineProps<{
  product: {
    id: any
    title: string
    price: number
    image: string
    quantity: number
    options?: any
    weight: number
  }
}>()

const cartStore = useCartStore()
const loading = ref(false)
const toast = useToast()

const handleAddToCart = () => {
  loading.value = true

  // Simulasi proses delay agar UX terasa seperti ada request ke server
  setTimeout(() => {
    cartStore.add(props.product)
    loading.value = false

    toast.add({
      title: 'Berhasil Masuk Keranjang!',
      description: `${props.product.title} telah ditambahkan.`,
      icon: 'i-heroicons-check-circle',
      color: 'green'
    })
  }, 300)
  
}
</script>