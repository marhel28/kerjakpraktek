<script setup lang="ts">
import { ref, computed } from "vue";
import { useWishlistStore } from "~/stores/wishlist";

const wishlist = useWishlistStore();
const toast = useToast();
definePageMeta({ layout: "auth" });

const { data: categories } = await useFetch<any>("/api/category", {
  lazy: true,
  transform: (res) => Array.isArray(res) ? res : res?.data || [],
});

const tabs = [
  { label: "Biodata Diri", to: "/dashboard" },
  { label: "Daftar Alamat", to: "/dashboard/address" },
  { label: "Keamanan", to: "/dashboard/change-password" },
  { label: "Notifikasi", to: "/dashboard/notifications" },
  { label: "Pesanan Saya", to: "/dashboard/orders" },
  { label: "Layanan Jasa", to: "/dashboard/jasa" },
];

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
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- TABS -->
    <div class="border-b border-gray-200 overflow-x-auto no-scrollbar">
      <div class="flex px-8">
        <NuxtLink
          v-for="tab in tabs"
          :key="tab.to"
          :to="tab.to"
          class="px-6 py-4 text-sm font-bold whitespace-nowrap transition-colors relative"
          :class="[
            $route.path === tab.to 
              ? 'text-[#03AC0E]' 
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          {{ tab.label }}
          <div v-if="$route.path === tab.to" class="absolute bottom-0 left-0 right-0 h-1 bg-[#03AC0E] rounded-t-full"></div>
        </NuxtLink>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="p-8">
      <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-6 mb-8">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Wishlist Saya</h2>
          <p class="text-xs text-gray-400 mt-1 uppercase tracking-widest font-bold">{{ wishlist.count }} Produk Tersimpan</p>
        </div>
      </header>

      <!-- CATEGORY FILTERS -->
      <section v-if="categories?.length" class="mb-8">
        <div class="flex items-center gap-2 overflow-x-auto no-scrollbar">
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
            class="bg-white border border-gray-200 rounded-xl p-4 sm:p-5 hover:border-[#03AC0E] transition-all flex items-center gap-4 sm:gap-6 group"
          >
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

            <div class="flex flex-col sm:flex-row items-center gap-4">
              <button @click="navigateTo(`/p/${item.stock?.slug}`)" class="px-8 py-2.5 bg-[#03AC0E] text-white text-xs font-bold rounded-lg hover:bg-[#028a0b] transition-all shadow-sm">
                Beli
              </button>
              <button @click="removeItem(item.stock?.uuid)" class="p-2 text-gray-300 hover:text-red-600 transition-colors">
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
