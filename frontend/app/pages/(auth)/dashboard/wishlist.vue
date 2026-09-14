<script setup lang="ts">
import { ref, computed } from "vue";
import { useWishlistStore } from "~/stores/wishlist";
import { useCartStore } from "~/stores/cart";

const wishlist = useWishlistStore();
const cart = useCartStore();
const toast = useToast();
definePageMeta({ layout: "auth" });

const { data: categories } = await useFetch<any>("/api/category", {
  lazy: true,
  transform: (res) => Array.isArray(res) ? res : res?.data || [],
});


const selectedCategories = ref<string[]>([]);

const filteredAndSortedWishlist = computed(() => {
  let itemsCopy = [...(wishlist.items || [])];
  if (selectedCategories.value.length > 0) {
    itemsCopy = itemsCopy.filter((item) => selectedCategories.value.includes(item.stock?.category_slug || ""));
  }
  return itemsCopy.reverse();
});

const toggleCategory = (slug: string) => {
  const index = selectedCategories.value.indexOf(slug);
  if (index > -1) selectedCategories.value.splice(index, 1);
  else selectedCategories.value.push(slug);
};

const formatRupiah = (angka: number) =>
  new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(angka || 0);

const removeItem = async (uuid: string) => {
  const success = await wishlist.removeFromWishlist(uuid);
  if (success) toast.add({ title: "Berhasil", description: "Produk dihapus dari wishlist", color: "green" });
};

const addToCart = async (stockItem: any) => {
  if (!stockItem) return;
  await cart.add({
    stock_uuid: stockItem.uuid,
    title: stockItem.title,
    brand: stockItem.brand,
    category_slug: stockItem.category_slug,
    price: stockItem.online_price,
    original_price: stockItem.original_price,
    discount_percentage: stockItem.discount_percentage,
    image: stockItem.cover_image_url,
    quantity: 1,
    weight: stockItem.weight
  });
  toast.add({ title: "Berhasil", description: "Produk ditambahkan ke keranjang", color: "green" });
};
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- MOBILE HEADER -->
    <div class="lg:hidden flex items-center gap-4 px-6 py-4 border-b border-gray-100 bg-white sticky top-0 z-10">
      <button @click="$router.push('/dashboard')" class="p-1 -ml-1 text-gray-400 hover:text-gray-900 transition-colors">
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </button>
      <h1 class="text-base font-black text-gray-900 uppercase tracking-wider">Wishlist Saya</h1>
    </div>

    <!-- DESKTOP HEADER (Tokopedia Style) -->
    <div class="hidden lg:block px-8 py-5 border-b border-gray-200/80 bg-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-lg font-bold text-gray-900">Wishlist & Barang Favorit</h1>
          <p class="text-xs text-gray-500 mt-0.5">{{ wishlist.count }} produk sistem keamanan tersimpan</p>
        </div>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="p-4 sm:p-8">

      <!-- CATEGORY FILTERS -->
      <section v-if="categories?.length" class="mb-8">
        <div class="flex items-center gap-2 overflow-x-auto no-scrollbar pb-2">
          <button v-for="cat in categories" :key="cat.slug" @click="toggleCategory(cat.slug)"
            class="flex-shrink-0 px-5 py-2 rounded-lg text-xs font-bold transition-all border"
            :class="selectedCategories.includes(cat.slug) ? 'bg-zinc-900 text-white border-zinc-900' : 'bg-white text-zinc-500 border-gray-200 hover:border-gray-400'"
          >
            {{ cat.name }}
          </button>
        </div>
      </section>

      <!-- PRODUCT LIST -->
      <main class="space-y-4">
        <div v-if="filteredAndSortedWishlist.length === 0" class="py-24 text-center border-2 border-dashed border-gray-100 rounded-xl">
          <p class="text-sm font-bold text-gray-400">Belum ada wishlist.</p>
          <NuxtLink to="/" class="mt-4 inline-block text-sm font-bold text-[#03AC0E] hover:underline">Cari Produk Sekarang</NuxtLink>
        </div>

        <div v-else class="grid grid-cols-1 gap-4">
          <div v-for="item in filteredAndSortedWishlist" :key="item.wishlist_uuid" 
            class="bg-white border border-gray-200 rounded-xl p-4 sm:p-5 hover:border-[#03AC0E] transition-all flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6 group"
          >
            <!-- Image & Content Group -->
            <div class="flex items-center gap-4 sm:gap-6 flex-1 min-w-0">
              <div class="w-20 h-20 sm:w-24 sm:h-24 flex-shrink-0 bg-gray-50 rounded-lg overflow-hidden border border-gray-100">
                <NuxtImg :src="item.stock?.cover_image_url || '/placeholder.webp'" class="w-full h-full object-cover" />
              </div>
              
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-bold text-[#03AC0E] uppercase tracking-widest mb-1">{{ item.stock?.brand || 'PasarCctv' }}</p>
                <h3 class="text-sm font-bold text-gray-900 truncate tracking-tight group-hover:text-[#03AC0E] transition-colors">{{ item.stock?.title }}</h3>
                <p class="text-sm font-bold text-gray-900 mt-2">{{ formatRupiah(item.stock?.online_price || 0) }}</p>
                <div v-if="item.stock?.original_price > item.stock?.online_price" class="flex items-center gap-2 mt-1">
                  <span class="text-[10px] text-gray-400 line-through">{{ formatRupiah(item.stock?.original_price) }}</span>
                  <span class="text-[10px] font-bold text-red-500">{{ item.stock?.discount_percentage }}% OFF</span>
                </div>
              </div>
            </div>

            <!-- Buttons Group (Bottom on mobile, right on desktop) -->
            <div class="flex items-center justify-end gap-3 pt-3 sm:pt-0 border-t sm:border-0 border-gray-100 w-full sm:w-auto">
              <button @click="addToCart(item.stock)" class="flex-1 sm:flex-initial px-5 py-2.5 border border-[#03AC0E] text-[#03AC0E] hover:bg-emerald-50 text-xs font-bold rounded-lg transition-all shadow-sm text-center">
                + Keranjang
              </button>
              <button @click="navigateTo(`/p/${item.stock?.slug}`)" class="flex-1 sm:flex-initial px-8 py-2.5 bg-[#03AC0E] text-white text-xs font-bold rounded-lg hover:bg-[#028a0b] transition-all shadow-sm text-center">
                Beli
              </button>
              <button @click="removeItem(item.stock?.uuid)" class="p-2.5 text-gray-400 hover:text-red-600 transition-colors border border-gray-200 sm:border-0 rounded-lg flex items-center justify-center">
                <UIcon name="i-heroicons-trash" class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
