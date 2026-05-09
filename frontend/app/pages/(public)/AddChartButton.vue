<script setup lang="ts">
import { ref } from 'vue'
import { useCartStore } from '~/stores/cart'

// 1. 🔥 STRICT TYPING: Definisikan interface yang jelas agar tidak ada properti yang terlewat
interface ProductProp {
  uuid?: string
  id?: string
  title: string
  price: number
  original_price?: number
  discount_percentage?: number
  image?: string
  cover_image_url?: string
  brand?: string
  category_slug?: string
  category?: string
  specs?: Record<string, any>
  quantity?: number
}

const props = defineProps<{
  product: ProductProp
}>()

const cartStore = useCartStore()
const loading = ref(false)
const toast = useToast()

const handleAddToCart = async () => {
  loading.value = true

  try {
    // Normalisasi ID/UUID
    const stock_uuid = props.product.uuid || props.product.id

    if (!stock_uuid) {
      console.error('UUID TIDAK ADA!', props.product)
      toast.add({
        title: 'Gagal',
        description: 'Data produk tidak valid atau belum dimuat sepenuhnya.',
        icon: 'i-heroicons-x-circle',
        color: 'red'
      })
      loading.value = false
      return
    }

    // 2. 🔥 PAYLOAD LENGKAP: Kirim semua data agar UI Cart bisa langsung me-render pill brand & diskon
    await cartStore.add({
      stock_uuid: String(stock_uuid),
      title: props.product.title,
      price: Number(props.product.price),
      original_price: props.product.original_price || 0,
      discount_percentage: props.product.discount_percentage || 0,
      
      // Mengatasi perbedaan nama key dari backend vs frontend
      image: props.product.image || props.product.cover_image_url || '/placeholder.webp',
      brand: props.product.brand || 'NO BRAND',
      category_slug: props.product.category_slug || props.product.category || 'uncategorized',
      specs: props.product.specs || {},
      
      quantity: Math.max(1, Number(props.product.quantity) || 1),
    })

    toast.add({
      title: 'Berhasil Masuk Keranjang!',
      description: `${props.product.title} ditambahkan.`,
      icon: 'i-heroicons-check-circle',
      color: 'green' // Tema success warna hijau (menyesuaikan UI keranjang sebelumnya)
    })

  } catch (err) {
    console.error('ADD CART ERROR:', err)
    toast.add({
      title: 'Terjadi Kesalahan',
      description: 'Gagal memasukkan barang ke keranjang.',
      icon: 'i-heroicons-x-circle',
      color: 'red'
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UButton
    size="lg"
    color="white"
    variant="outline"
    icon="i-heroicons-shopping-cart"
    class="w-full flex justify-center rounded-xl border-gray-300 text-gray-700 hover:border-green-600 hover:text-green-600 hover:bg-green-50 font-bold py-3 transition-all duration-300"
    :loading="loading"
    @click.prevent="handleAddToCart"
  >
    + Keranjang
  </UButton>
</template>