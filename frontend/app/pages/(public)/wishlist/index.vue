<script setup lang="ts">
import { ref, computed } from "vue";
import { useWishlistStore } from "~/stores/wishlist";

const wishlist = useWishlistStore();
const toast = useToast();

const isMobileFilterOpen = ref(false);

const { data: categories } = await useFetch<any>("/api/category", {
  lazy: true,
  transform: (res) => {
    return Array.isArray(res) ? res : res?.data || [];
  },
});

const sortOptions = ["Terbaru Disimpan", "Harga Tertinggi", "Harga Terendah"];
const selectedSort = ref(sortOptions[0]);

const selectedCategories = ref<string[]>([]);
const filterDiscount = ref(false);
const filterPromo = ref(false);
const promoCode = ref("");

const filteredAndSortedWishlist = computed(() => {
  let itemsCopy = [...wishlist.items];

  if (filterDiscount.value) {
    itemsCopy = itemsCopy.filter((item) => {
      return item.stock?.discount_percentage && item.stock.discount_percentage > 0;
    });
  }

  if (selectedCategories.value.length > 0) {
    itemsCopy = itemsCopy.filter((item) => {
      const itemCategory = item.stock?.category_slug || "";
      return selectedCategories.value.includes(itemCategory);
    });
  }

  if (selectedSort.value === "Harga Tertinggi") {
    return itemsCopy.sort(
      (a, b) => (b.stock?.online_price || 0) - (a.stock?.online_price || 0)
    );
  } else if (selectedSort.value === "Harga Terendah") {
    return itemsCopy.sort(
      (a, b) => (a.stock?.online_price || 0) - (b.stock?.online_price || 0)
    );
  } else {
    return itemsCopy.reverse();
  }
});

const applyPromoCode = () => {
  if (!promoCode.value.trim()) return;
  toast.add({
    title: "Kode Promo",
    description: `Mencari kode promo: ${promoCode.value.toUpperCase()}...`,
    icon: "i-heroicons-ticket",
    color: "black",
  });
};
</script>

<template>
  <main class="bg-gray-50 min-h-screen pb-24 md:py-8">
    <div
      class="md:hidden sticky top-0 z-30 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm"
    >
      <h1 class="font-black text-lg text-gray-900 tracking-tight">
        Wishlist ({{ filteredAndSortedWishlist.length }})
      </h1>
      <button
        @click="isMobileFilterOpen = true"
        class="flex items-center gap-1.5 bg-gray-100 px-3 py-1.5 rounded-full text-xs font-bold text-gray-700 hover:bg-gray-200 transition-colors"
      >
        <UIcon name="i-heroicons-adjustments-horizontal" class="w-4 h-4" />
        Filter & Urutkan
      </button>
    </div>

    <div class="max-w-[1400px] mx-auto px-4 md:px-6 pt-4 md:pt-0">
      <div class="flex flex-col md:flex-row gap-8 items-start">
        <aside class="hidden md:block w-[260px] shrink-0 sticky top-24">
          <h2 class="font-black text-xl mb-4 text-gray-900 tracking-tight">Filter</h2>

          <div
            class="border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-sm"
          >
            <div class="p-5 border-b border-gray-100">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-sm tracking-wide">PENAWARAN</h3>
              </div>
              <div class="space-y-3">
                <label class="flex items-center gap-3 cursor-pointer group">
                  <input
                    v-model="filterDiscount"
                    type="checkbox"
                    class="checkbox-custom"
                  />
                  <span
                    class="text-sm font-semibold text-gray-600 group-hover:text-black transition-colors"
                    >Harga Diskon</span
                  >
                </label>
                <label class="flex items-center gap-3 cursor-pointer group">
                  <input v-model="filterPromo" type="checkbox" class="checkbox-custom" />
                  <span
                    class="text-sm font-semibold text-gray-600 group-hover:text-black transition-colors"
                    >Promo Spesial</span
                  >
                </label>
              </div>
            </div>

            <div class="p-5 border-b border-gray-100">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-sm tracking-wide">KATEGORI</h3>
              </div>

              <div v-if="categories?.length" class="space-y-3">
                <label
                  v-for="cat in categories"
                  :key="cat.slug || cat.id"
                  class="flex items-center gap-3 cursor-pointer group"
                >
                  <input
                    type="checkbox"
                    :value="cat.slug || cat.id"
                    v-model="selectedCategories"
                    class="checkbox-custom"
                  />
                  <span
                    class="text-sm font-semibold text-gray-600 group-hover:text-black transition-colors"
                  >
                    {{ cat.name || cat.title }}
                  </span>
                </label>
              </div>
              <div v-else class="text-xs text-gray-400 font-medium">
                Memuat kategori...
              </div>
            </div>

            <div class="p-5 bg-gray-50/50">
              <h3 class="font-bold text-sm tracking-wide mb-3">PUNYA KODE PROMO?</h3>
              <div class="flex gap-2">
                <input
                  v-model="promoCode"
                  type="text"
                  placeholder="Masukkan kode"
                  class="w-full text-sm font-semibold border border-gray-300 rounded-lg px-3 py-2 outline-none focus:border-green-600 uppercase placeholder:normal-case placeholder:font-normal"
                  @keyup.enter="applyPromoCode"
                />
                <button
                  @click="applyPromoCode"
                  class="bg-black text-white px-3 py-2 rounded-lg text-sm font-bold hover:bg-green-600 transition-colors"
                >
                  Cek
                </button>
              </div>
            </div>
          </div>
        </aside>

        <div class="flex-1 min-w-0 w-full">
          <div
            class="hidden md:flex flex-wrap justify-between items-center mb-6 gap-4 bg-white p-4 rounded-2xl border border-gray-200 shadow-sm"
          >
            <div class="flex items-center gap-4">
              <h1 class="text-lg font-black text-gray-900 tracking-tight">
                {{ filteredAndSortedWishlist.length }} Barang Disimpan
              </h1>
            </div>

            <div class="flex items-center gap-3">
              <span class="text-sm text-gray-500 font-bold uppercase tracking-wider"
                >Urutkan:</span
              >
              <select
                v-model="selectedSort"
                class="border border-gray-200 rounded-xl px-4 py-2 text-sm font-bold text-gray-700 outline-none focus:border-green-600 cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <option v-for="opt in sortOptions" :key="opt" :value="opt">
                  {{ opt }}
                </option>
              </select>
            </div>
          </div>

          <div
            v-if="filteredAndSortedWishlist.length === 0"
            class="flex flex-col items-center justify-center py-16 md:py-24 text-center border-2 border-dashed border-gray-200 rounded-3xl bg-white mx-auto"
          >
            <div
              class="w-16 h-16 md:w-20 md:h-20 bg-gray-50 rounded-full flex items-center justify-center mb-4"
            >
              <UIcon
                name="i-heroicons-heart"
                class="w-8 h-8 md:w-10 md:h-10 text-gray-300"
              />
            </div>
            <h2 class="text-lg md:text-xl font-black text-gray-900 tracking-tight mb-2">
              Belum ada barang impian
            </h2>
            <p class="text-gray-500 font-medium text-sm mb-6 max-w-sm px-4">
              Cari produk CCTV incaranmu atau ubah filter untuk menemukan barang impianmu.
            </p>
            <NuxtLink to="/">
              <button
                class="bg-black text-white px-8 py-3 rounded-xl font-bold text-sm hover:bg-green-600 transition-colors shadow-lg shadow-black/10 hover:-translate-y-0.5 active:translate-y-0"
              >
                Mulai Belanja
              </button>
            </NuxtLink>
          </div>

          <div
            v-else
            class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4"
          >
            <CardPerItems
              v-for="item in filteredAndSortedWishlist"
              :key="item.wishlist_uuid"
              :uuid="item.stock?.uuid"
              :slug="item.stock?.slug"
              :title="item.stock?.title"
              :image="item.stock?.cover_image_url || '/placeholder.webp'"
              :price="item.stock?.online_price || 0"
              :original_price="item.stock?.original_price"
              :discount_percentage="item.stock?.discount_percentage"
              :brand="item.stock?.brand"
              :category="item.stock?.category_slug"
              :subcategory="item.stock?.subcategory_slug"
              :specs="item.stock?.specs"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Bottom Sheet Filter -->
    <div
      v-if="isMobileFilterOpen"
      class="fixed inset-0 z-50 flex flex-col justify-end md:hidden"
    >
      <div
        class="absolute inset-0 bg-black/60 transition-opacity"
        @click="isMobileFilterOpen = false"
      ></div>

      <div
        class="relative bg-white w-full max-h-[90vh] rounded-t-3xl flex flex-col animate-slide-up shadow-2xl"
      >
        <div class="flex flex-col items-center pt-3 pb-4 border-b border-gray-100">
          <div class="w-12 h-1.5 bg-gray-300 rounded-full mb-4"></div>
          <div class="w-full px-5 flex items-center justify-between">
            <h3 class="font-black text-lg text-gray-900 tracking-tight">
              Filter & Urutkan
            </h3>
            <button
              @click="isMobileFilterOpen = false"
              class="p-2 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
            >
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5 text-gray-700" />
            </button>
          </div>
        </div>

        <div class="p-5 overflow-y-auto flex-1 space-y-8">
          <div>
            <h4 class="font-bold text-sm tracking-wide mb-3 text-gray-900">
              URUTKAN BERDASARKAN
            </h4>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="opt in sortOptions"
                :key="opt"
                @click="selectedSort = opt"
                :class="
                  selectedSort === opt
                    ? 'bg-black text-white border-black'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'
                "
                class="px-4 py-2 rounded-full text-sm font-bold border transition-colors"
              >
                {{ opt }}
              </button>
            </div>
          </div>

          <div>
            <h4 class="font-bold text-sm tracking-wide mb-3 text-gray-900">
              PENAWARAN SPESIAL
            </h4>
            <div class="space-y-4">
              <label class="flex items-center justify-between cursor-pointer group">
                <span class="text-sm font-semibold text-gray-700">Harga Diskon</span>
                <input v-model="filterDiscount" type="checkbox" class="checkbox-custom" />
              </label>
              <label class="flex items-center justify-between cursor-pointer group">
                <span class="text-sm font-semibold text-gray-700">Promo Khusus</span>
                <input v-model="filterPromo" type="checkbox" class="checkbox-custom" />
              </label>
            </div>
          </div>

          <div>
            <h4 class="font-bold text-sm tracking-wide mb-3 text-gray-900">KATEGORI</h4>
            <div v-if="categories?.length" class="space-y-4">
              <label
                v-for="cat in categories"
                :key="cat.slug || cat.id"
                class="flex items-center justify-between cursor-pointer group"
              >
                <span class="text-sm font-semibold text-gray-700">{{
                  cat.name || cat.title
                }}</span>
                <input
                  type="checkbox"
                  :value="cat.slug || cat.id"
                  v-model="selectedCategories"
                  class="checkbox-custom"
                />
              </label>
            </div>
          </div>
        </div>

        <div class="p-4 border-t border-gray-100 bg-white">
          <button
            @click="isMobileFilterOpen = false"
            class="w-full bg-green-600 text-white font-bold py-3.5 rounded-xl text-sm shadow-lg shadow-green-600/20 active:scale-[0.98] transition-transform"
          >
            Tampilkan {{ filteredAndSortedWishlist.length }} Produk
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap");

main {
  font-family: "Plus Jakarta Sans", sans-serif;
}

/* ✅ FIX: Custom checkbox — background putih, centang hijau, konsisten di semua browser & mobile */
.checkbox-custom {
  appearance: none;
  -webkit-appearance: none;
  width: 1.125rem; /* 18px */
  height: 1.125rem;
  min-width: 1.125rem;
  border: 1.5px solid #d1d5db; /* border-gray-300 */
  border-radius: 4px;
  background-color: #ffffff; /* putih selalu */
  cursor: pointer;
  position: relative;
  transition: border-color 0.15s, background-color 0.15s;
  flex-shrink: 0;
}

/* Hover state */
.checkbox-custom:hover {
  border-color: #16a34a;
}

/* Checked state — background hijau, centang putih */
.checkbox-custom:checked {
  background-color: #16a34a;
  border-color: #16a34a;
}

/* Centang putih via SVG pseudo-element */
.checkbox-custom:checked::after {
  content: "";
  position: absolute;
  left: 4px;
  top: 1px;
  width: 5px;
  height: 9px;
  border: 2px solid #ffffff;
  border-top: none;
  border-left: none;
  transform: rotate(45deg);
}

/* Focus ring aksesibilitas */
.checkbox-custom:focus-visible {
  outline: 2px solid #16a34a;
  outline-offset: 2px;
}

/* Animasi Drawer Bottom Sheet */
@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
