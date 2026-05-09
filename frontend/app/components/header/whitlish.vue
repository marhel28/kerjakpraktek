<template>
  <div class="relative group h-full flex items-center">
    
    <NuxtLink
      to="/wishlist"
      class="text-black hover:scale-110 transition-transform flex items-center mb-2 relative p-1"
      aria-label="Wishlist"
    >
      <Icon name="lucide:heart" class="text-xl lg:text-3xl" />

      <span
        v-if="count > 0"
        class="absolute -top-1 -right-1 bg-red-600 text-white text-[9px] font-black min-w-[16px] h-4 flex items-center justify-center rounded-full shadow-sm border border-white px-1"
      >
        {{ count }}
      </span>
    </NuxtLink>

    <div
      class="absolute right-0 top-full opacity-0 invisible
      group-hover:opacity-100 group-hover:visible
      transition-all duration-300 transform origin-top-right
      scale-95 group-hover:scale-100
      w-[300px] z-[100]"
    >
      <div class="bg-white border border-gray-200 shadow-[0_20px_40px_rgba(0,0,0,0.1)] rounded-xl overflow-hidden flex flex-col font-sans mt-1">

        <div class="p-4 border-b border-gray-100 bg-gray-50/80 flex items-center justify-between">
          <div class="flex flex-col">
            <span class="text-xs font-black text-black uppercase tracking-widest">
              Favorit Saya
            </span>
            <span class="text-[9px] font-bold text-gray-400 uppercase tracking-wider mt-0.5">
              {{ count }} Produk Disimpan
            </span>
          </div>
          <Icon name="lucide:bookmark" class="w-4 h-4 text-gray-300" />
        </div>

        <div
          v-if="count > 0"
          class="max-h-[300px] overflow-y-auto py-2 px-2 custom-scrollbar"
        >
          <div
            v-for="item in wishlistStore.items"
            :key="item.wishlist_uuid"
            class="p-2 hover:bg-gray-50 rounded-lg transition-colors group/item flex gap-3 relative"
          >
            <div class="w-14 h-14 bg-gray-100 rounded-md overflow-hidden shrink-0 border border-gray-100">
              <NuxtImg
                :src="item.stock?.cover_image_url || '/placeholder-image.png'"
                class="w-full h-full object-cover group-hover/item:scale-110 transition-transform duration-500"
              />
            </div>

            <div class="flex flex-col flex-1 min-w-0 justify-center">
              <span class="text-[10px] font-black text-black uppercase tracking-tight line-clamp-1 mb-1">
                {{ item.stock?.title }}
              </span>
              <span class="text-[10px] font-bold text-red-600 uppercase tracking-widest">
                Rp {{ item.stock?.online_price?.toLocaleString('id-ID') || 0 }}
              </span>
            </div>

            <button
              @click.prevent="handleRemove(item.stock?.uuid)"
              class="absolute top-2 right-2 opacity-0 group-hover/item:opacity-100 transition-opacity p-1 hover:text-black"
            >
              <Icon name="lucide:x" class="w-3 h-3" />
            </button>
          </div>
        </div>

        <div v-else class="p-8 flex flex-col items-center justify-center text-center">
          <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-4 border border-gray-100">
            <Icon name="lucide:heart" class="w-5 h-5 text-gray-200" />
          </div>
          <span class="text-xs font-black uppercase tracking-widest text-black mb-1">
            Belum Ada Favorit
          </span>
          <p class="text-[9px] font-bold text-gray-500 uppercase tracking-wider leading-relaxed">
            Simpan produk impian Anda untuk memantau harga dan stok.
          </p>
        </div>

        <div class="p-4 border-t border-gray-100 bg-gray-50/50">
          <NuxtLink
            to="/wishlist"
            class="w-full bg-white border border-black text-black py-2.5 flex items-center justify-center gap-2 text-[10px] font-black uppercase tracking-widest rounded-lg hover:bg-black hover:text-white transition-all duration-300 active:scale-[0.98]"
          >
            Buka Wishlist Lengkap
          </NuxtLink>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useWishlistStore } from '~/stores/wishlist'
import { useCookie } from '#app'

const wishlistStore = useWishlistStore()
const count = computed(() => wishlistStore.count)
const token = useCookie('token')

// Fungsi hapus menggunakan store `toggle` (karena toggle sudah mendeteksi jika barang ada, maka akan dihapus secara optimis)
const handleRemove = (stockUuid: string | undefined) => {
  if (!stockUuid) return
  // Kirim object dengan id sesuai dengan yang diharapkan oleh fungsi toggle di Store
  wishlistStore.toggle({ id: stockUuid })
}

// Auto fetch kalau user sudah login & data masih kosong saat komponen dimuat
let loaded = false

await useAsyncData('wishlist', async () => {
  if (!token.value) return []
  return await wishlistStore.fetchWishlist()
}, {
  server: false
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #f1f1f1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #e5e7eb;
}
</style>