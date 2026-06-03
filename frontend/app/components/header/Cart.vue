<template>
  <div class="relative group h-full flex items-center z-[100]">

    <NuxtLink
      to="/cart"
      class="flex items-center gap-2 hover:scale-105 transition-transform p-1.5 cursor-pointer"
      aria-label="Keranjang Belanja"
    >
      <div class="relative flex items-center justify-center">
        <Icon name="lucide:shopping-cart" class="text-2xl lg:text-[26px] text-gray-700 group-hover:text-[#03AC0E] transition-colors" />
        <span class="absolute -top-1.5 -right-2 bg-red-600 text-white text-[10px] font-bold min-w-[18px] h-[18px] flex items-center justify-center rounded-full border-2 border-white px-1">
          {{ count }}
        </span>
      </div>

      <div class="hidden lg:flex flex-col leading-none ml-1">
        <span class="text-[12px] text-gray-400 font-medium mb-0.5">Total</span>
        <span class="text-[14px] font-bold text-gray-900 tracking-tight">
          Rp{{ totalPrice.toLocaleString('id-ID') }}
        </span>
      </div>
    </NuxtLink>

    <div class="absolute right-0 top-full opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform origin-top-right scale-95 group-hover:scale-100 w-[340px]">
      <div class="bg-white border border-gray-200 shadow-[0_20px_40px_rgba(0,0,0,0.1)] rounded-xl overflow-hidden flex flex-col font-sans mt-2">

        <div class="p-4 border-b border-gray-100 bg-gray-50/80 flex items-center justify-between">
          <div class="flex flex-col">
            <span class="text-xs font-black text-black uppercase tracking-widest">Keranjang</span>
            <span class="text-[9px] font-bold text-gray-500 uppercase tracking-wider mt-0.5">{{ count }} Barang</span>
          </div>
          <Icon name="lucide:shopping-bag" class="w-4 h-4 text-gray-400" />
        </div>

        <div v-if="cartStore.items.length > 0" class="max-h-[350px] overflow-y-auto py-2 px-2 custom-scrollbar">
          <div v-for="item in cartStore.items" :key="item.stock_uuid" class="p-2 hover:bg-gray-50 rounded-lg transition-colors group/item flex gap-3 relative">
            <div class="w-16 h-16 bg-gray-100 rounded-md overflow-hidden shrink-0 border border-gray-100 relative">
              <NuxtImg :src="item.image" class="w-full h-full object-cover group-hover/item:scale-110 transition-transform duration-500" />
            </div>

            <div class="flex flex-col flex-1 min-w-0 justify-center">
              <span v-if="item.brand" class="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">{{ item.brand }}</span>
              <span class="text-[11px] font-black text-black uppercase tracking-tight line-clamp-1 mb-1">{{ item.title }}</span>
              
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-bold text-red-600 uppercase tracking-widest">Rp {{ item.price?.toLocaleString('id-ID') }}</span>
                <span v-if="item.original_price && item.original_price > item.price" class="text-[9px] text-gray-400 line-through">
                  Rp{{ item.original_price.toLocaleString('id-ID') }}
                </span>
              </div>
              <span class="text-[9px] text-gray-400 font-bold uppercase mt-1 tracking-tighter">Qty: {{ item.quantity }}</span>
            </div>

            <button @click.prevent="cartStore.remove(item.stock_uuid)" class="absolute top-2 right-2 opacity-0 group-hover/item:opacity-100 transition-opacity p-1 hover:text-red-600">
              <Icon name="lucide:x" class="w-3 h-3" />
            </button>
          </div>
        </div>

        <div v-else class="p-8 flex flex-col items-center justify-center text-center">
          <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-4 border border-gray-100">
            <Icon name="lucide:shopping-cart" class="w-5 h-5 text-gray-300" />
          </div>
          <span class="text-xs font-black uppercase tracking-widest text-black mb-1">Keranjang Kosong</span>
          <p class="text-[9px] font-bold text-gray-500 uppercase tracking-wider leading-relaxed">Belum ada produk di keranjang Anda.</p>
        </div>

        <div v-if="cartStore.items.length > 0" class="p-4 border-t border-gray-100 bg-gray-50/50 flex flex-col gap-3">
          <div class="flex items-center justify-between px-1">
            <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Total Estimasi</span>
            <span class="text-sm font-black text-black uppercase tracking-tight">Rp {{ totalPrice.toLocaleString('id-ID') }}</span>
          </div>

          <NuxtLink to="/cart" class="w-full bg-black text-white py-3 flex items-center justify-center gap-2 text-[11px] font-black uppercase tracking-widest rounded-lg hover:bg-gray-800 transition-all duration-300 shadow-lg shadow-black/5 active:scale-[0.98]">
            Lihat Keranjang
            <Icon name="lucide:arrow-right" class="w-4 h-4" />
          </NuxtLink>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useCartStore } from '~/stores/cart'
import { useCookie } from '#app'

const cartStore = useCartStore()
const token = useCookie('token')

const count = computed(() => cartStore.count)

const totalPrice = computed(() => {
  return cartStore.items.reduce((acc, item) => {
    return acc + ((item.price || 0) * (item.quantity || 1))
  }, 0)
})

onMounted(async () => {
  if (token.value) {
    await cartStore.fetchCartFromAPI()
  }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #f1f1f1; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #e5e7eb; }
</style>