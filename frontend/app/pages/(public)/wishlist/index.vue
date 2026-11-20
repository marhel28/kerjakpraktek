<script setup lang="ts">
import { ref, computed } from "vue";
import { useWishlistStore } from "~/stores/wishlist";
import { useCartStore } from "~/stores/cart";
import CardPerItems from "~/components/CardPerItems.vue";
import ProductRecommendation from "~/components/ProductRecommendation.vue";

const wishlist = useWishlistStore();
const cartStore = useCartStore();
const toast = useToast();

const isMobileFilterOpen = ref(false);

// ─── Fetch Categories & Recommendations ──────────────────────────
const [{ data: categories }, { data: recResponse }] = await Promise.all([
  useFetch<any>("/api/category", {
    lazy: true,
    transform: (res) => (Array.isArray(res) ? res : res?.data || []),
  }),
  useFetch<any>("/api/smartsearchbar", {
    params: { q: "cctv", type: "all" },
    lazy: true,
  }),
]);

const recommendations = computed(() => {
  return recResponse.value?.items || [];
});

const sortOptions = ["Terbaru Disimpan", "Harga Tertinggi", "Harga Terendah"];
const selectedSort = ref(sortOptions[0]);

const selectedCategories = ref<string[]>([]);
const filterDiscount = ref(false);
const filterPromo = ref(false);
const promoCode = ref("");

// ─── Filter & Sort ───────────────────────────────────────────────
const filteredAndSortedWishlist = computed(() => {
  let itemsCopy = [...wishlist.items] as any[];

  if (filterDiscount.value) {
    itemsCopy = itemsCopy.filter((item) => {
      const stock = item.stock || {};
      return (stock.discount_percentage || item.discountPercentage || 0) > 0;
    });
  }

  if (selectedCategories.value.length > 0) {
    itemsCopy = itemsCopy.filter((item) => {
      const itemCategory = item.stock?.category_slug || item.category || "";
      return selectedCategories.value.includes(itemCategory);
    });
  }

  if (selectedSort.value === "Harga Tertinggi") {
    return itemsCopy.sort(
      (a, b) => (b.stock?.online_price || b.price || 0) - (a.stock?.online_price || a.price || 0)
    );
  } else if (selectedSort.value === "Harga Terendah") {
    return itemsCopy.sort(
      (a, b) => (a.stock?.online_price || a.price || 0) - (b.stock?.online_price || b.price || 0)
    );
  } else {
    return itemsCopy.reverse();
  }
});

// ─── Batch Actions ───────────────────────────────────────────────
const isMovingAll = ref(false);
const moveAllToCart = () => {
  if (!wishlist.items.length) return;
  isMovingAll.value = true;
  let count = 0;
  wishlist.items.forEach((item: any) => {
    const p = {
      id: item.stock?.uuid || item.id,
      title: item.stock?.title || item.title,
      price: item.stock?.online_price || item.price || 0,
      image: item.stock?.cover_image_url || item.image || "/cctv.jpg",
      quantity: 1,
      weight: item.stock?.weight || item.weight || 500,
    };
    (cartStore as any).add(p);
    count++;
  });
  isMovingAll.value = false;
  toast.add({
    title: "Berhasil Dipindahkan",
    description: `${count} produk dipindahkan ke keranjang belanja Anda.`,
    color: "success",
    icon: "i-heroicons-check-circle",
  });
};

const applyPromoCode = () => {
  if (!promoCode.value.trim()) return;
  toast.add({
    title: "Kupon Promo",
    description: `Kupon ${promoCode.value.toUpperCase()} berhasil disimpan untuk checkout.`,
    icon: "i-heroicons-ticket",
    color: "success",
  });
};
</script>

<template>
  <main class="bg-[#F8F9FA] min-h-screen pb-24 md:py-8 font-['Plus_Jakarta_Sans',sans-serif] text-gray-900">
    <!-- Mobile Top Navigation Header -->
    <div
      class="md:hidden sticky top-14 z-30 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-2xs"
    >
      <div class="flex items-center gap-2">
        <h1 class="font-extrabold text-base text-gray-900 tracking-tight">
          Wishlist Saya
        </h1>
        <span class="text-xs bg-emerald-50 text-[#03AC0E] border border-emerald-200 font-bold px-2 py-0.5 rounded-full">
          {{ filteredAndSortedWishlist.length }}
        </span>
      </div>
      <button
        type="button"
        @click="isMobileFilterOpen = true"
        class="flex items-center gap-1.5 bg-gray-100 px-3 py-1.5 rounded-lg text-xs font-bold text-gray-700 hover:bg-gray-200 transition-colors"
      >
        <UIcon name="i-heroicons-adjustments-horizontal" class="w-4 h-4" />
        Filter
      </button>
    </div>

    <div class="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 pt-4 md:pt-0">
      <!-- Breadcrumbs -->
      <nav aria-label="Breadcrumb" class="hidden md:flex items-center gap-1.5 text-xs text-gray-500 mb-6">
        <NuxtLink to="/" class="hover:text-gray-900 transition-colors">Beranda</NuxtLink>
        <span class="text-gray-300">/</span>
        <span class="text-gray-900 font-semibold">Wishlist & Favorit</span>
      </nav>

      <div class="flex flex-col md:flex-row gap-6 lg:gap-8 items-start">
        <!-- 1. SIDEBAR FILTER: Amazon Facet Standard -->
        <aside class="hidden md:block w-[260px] shrink-0 sticky top-24 space-y-4">
          <div class="border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-2xs">
            <div class="p-4 border-b border-gray-100 flex items-center justify-between">
              <h2 class="font-bold text-xs uppercase tracking-wider text-gray-500">Filter Wishlist</h2>
              <button
                v-if="selectedCategories.length || filterDiscount || filterPromo"
                type="button"
                class="text-[11px] text-[#03AC0E] font-bold hover:underline"
                @click="selectedCategories = []; filterDiscount = false; filterPromo = false"
              >
                Reset
              </button>
            </div>

            <!-- Penawaran -->
            <div class="p-4 border-b border-gray-100">
              <h3 class="font-bold text-xs uppercase tracking-wider text-gray-900 mb-3">Penawaran</h3>
              <div class="space-y-2.5">
                <label class="flex items-center gap-2.5 cursor-pointer group select-none">
                  <input
                    v-model="filterDiscount"
                    type="checkbox"
                    class="checkbox-custom"
                  />
                  <span class="text-xs font-semibold text-gray-700 group-hover:text-[#03AC0E] transition-colors">
                    Sedang Diskon
                  </span>
                </label>
                <label class="flex items-center gap-2.5 cursor-pointer group select-none">
                  <input
                    v-model="filterPromo"
                    type="checkbox"
                    class="checkbox-custom"
                  />
                  <span class="text-xs font-semibold text-gray-700 group-hover:text-[#03AC0E] transition-colors">
                    Promo Spesial
                  </span>
                </label>
              </div>
            </div>

            <!-- Kategori -->
            <div class="p-4 border-b border-gray-100">
              <h3 class="font-bold text-xs uppercase tracking-wider text-gray-900 mb-3">Kategori Produk</h3>
              <div v-if="categories?.length" class="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                <label
                  v-for="cat in categories"
                  :key="cat.slug || cat.id"
                  class="flex items-center gap-2.5 cursor-pointer group select-none"
                >
                  <input
                    type="checkbox"
                    :value="cat.slug || cat.id"
                    v-model="selectedCategories"
                    class="checkbox-custom"
                  />
                  <span class="text-xs font-semibold text-gray-700 group-hover:text-[#03AC0E] capitalize transition-colors">
                    {{ (cat.name || cat.title || '').replace(/-/g, ' ') }}
                  </span>
                </label>
              </div>
              <div v-else class="text-xs text-gray-400 font-medium">
                Memuat kategori...
              </div>
            </div>

            <!-- Promo Voucher Box -->
            <div class="p-4 bg-gray-50/70">
              <h3 class="font-bold text-xs uppercase tracking-wider text-gray-900 mb-2">Punya Voucher?</h3>
              <div class="flex gap-1.5">
                <input
                  v-model="promoCode"
                  type="text"
                  placeholder="KODE PROMO"
                  class="w-full text-xs font-bold border border-gray-300 rounded-lg px-2.5 py-1.5 outline-none focus:border-[#03AC0E] uppercase placeholder:normal-case placeholder:font-normal bg-white"
                  @keyup.enter="applyPromoCode"
                />
                <button
                  type="button"
                  @click="applyPromoCode"
                  class="bg-[#03AC0E] hover:bg-[#028b0b] text-white px-3 py-1.5 rounded-lg text-xs font-bold transition-colors shrink-0"
                >
                  Terapkan
                </button>
              </div>
            </div>
          </div>
        </aside>

        <!-- 2. MAIN CONTENT AREA -->
        <div class="flex-1 min-w-0 w-full space-y-6">
          <!-- Action Control Bar (Tokopedia Style) -->
          <div
            class="hidden md:flex flex-wrap justify-between items-center gap-4 bg-white p-4 sm:p-5 rounded-2xl border border-gray-200 shadow-2xs"
          >
            <div class="flex items-center gap-3">
              <h1 class="text-base sm:text-lg font-extrabold text-gray-900 tracking-tight">
                Wishlist & Barang Impian
              </h1>
              <span class="text-xs bg-emerald-50 text-[#03AC0E] border border-emerald-200 font-bold px-2.5 py-0.5 rounded-full">
                {{ filteredAndSortedWishlist.length }} Produk
              </span>
            </div>

            <div class="flex items-center gap-3">
              <!-- Move all to cart button -->
              <button
                v-if="filteredAndSortedWishlist.length > 0"
                type="button"
                class="bg-[#03AC0E] hover:bg-[#028b0b] active:bg-[#027509] text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-all shadow-xs active:scale-95"
                @click="moveAllToCart"
              >
                <UIcon name="i-heroicons-shopping-bag" class="w-4 h-4" />
                + Keranjang Semua
              </button>

              <!-- Sorting Dropdown -->
              <div class="flex items-center gap-2">
                <span class="text-xs text-gray-500 font-bold uppercase tracking-wider">Urutkan:</span>
                <select
                  v-model="selectedSort"
                  class="border border-gray-300 rounded-xl px-3 py-1.5 text-xs font-bold text-gray-800 outline-none focus:border-[#03AC0E] cursor-pointer bg-white hover:bg-gray-50 transition-colors"
                >
                  <option v-for="opt in sortOptions" :key="opt" :value="opt">
                    {{ opt }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- Wishlist Empty State Premium (Tokopedia / Amazon Hybrid) -->
          <div
            v-if="filteredAndSortedWishlist.length === 0"
            class="space-y-8"
          >
            <div class="bg-white border border-gray-200 rounded-3xl p-10 sm:p-16 text-center shadow-2xs max-w-2xl mx-auto">
              <div class="w-16 h-16 sm:w-20 sm:h-20 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-emerald-100">
                <UIcon name="i-heroicons-heart" class="w-8 h-8 sm:w-10 sm:h-10 text-[#03AC0E]" />
              </div>
              <h2 class="text-lg sm:text-xl font-extrabold text-gray-900 mb-2 tracking-tight">
                Wishlist Anda Masih Kosong
              </h2>
              <p class="text-xs sm:text-sm text-gray-500 mb-6 max-w-md mx-auto leading-relaxed">
                Simpan produk CCTV, IP camera, dan paket instalasi favorit Anda dengan menekan ikon hati agar mudah dibeli kapan saja.
              </p>
              <NuxtLink to="/search">
                <button
                  type="button"
                  class="bg-[#03AC0E] hover:bg-[#028b0b] active:bg-[#027509] text-white px-8 py-3 rounded-xl font-bold text-xs sm:text-sm transition-all shadow-md shadow-emerald-600/20 active:scale-95 inline-flex items-center gap-2"
                >
                  <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
                  Eksplor Katalog Produk
                </button>
              </NuxtLink>
            </div>

            <!-- In-place Recommendations When Wishlist is Empty -->
            <div v-if="recommendations?.length" class="pt-6 border-t border-gray-200">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h3 class="text-base font-extrabold text-gray-900 tracking-tight">
                    Rekomendasi Pilihan Teknisi
                  </h3>
                  <p class="text-xs text-gray-500">Paket dan kamera CCTV paling populer di Bandung & Cimahi</p>
                </div>
                <NuxtLink to="/search" class="text-xs font-bold text-[#03AC0E] hover:underline flex items-center gap-1">
                  Lihat Semua
                  <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" />
                </NuxtLink>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4">
                <CardPerItems
                  v-for="prod in recommendations.slice(0, 8)"
                  :key="prod.uuid"
                  :uuid="prod.uuid"
                  :slug="prod.slug"
                  :title="prod.title"
                  :image="prod.image || '/cctv.jpg'"
                  :price="prod.price || 0"
                  :brand="prod.brand"
                />
              </div>
            </div>
          </div>

          <!-- 3. Grid Daftar Wishlist (Item Card Tokopedia Style) -->
          <div
            v-else
            class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4"
          >
            <div
              v-for="item in filteredAndSortedWishlist"
              :key="item.wishlist_uuid || item.id"
              class="relative group"
            >
              <CardPerItems
                :uuid="item.stock?.uuid || item.id"
                :slug="item.stock?.slug || item.slug"
                :title="item.stock?.title || item.title"
                :image="item.stock?.cover_image_url || item.image || '/cctv.jpg'"
                :price="item.stock?.online_price || item.price || 0"
                :original_price="item.stock?.original_price || item.originalPrice"
                :discount_percentage="item.stock?.discount_percentage || item.discountPercentage"
                :brand="item.stock?.brand || item.brand"
                :category="item.stock?.category_slug || item.category"
                :subcategory="item.stock?.subcategory_slug || item.subcategory"
                :specs="item.stock?.specs || item.specs"
              />

              <!-- Tombol Hapus Cepat (Quick Remove Floating Button) -->
              <button
                type="button"
                aria-label="Hapus dari wishlist"
                class="absolute top-2.5 right-2.5 z-20 w-8 h-8 rounded-full bg-white/95 backdrop-blur-xs border border-gray-200 text-gray-400 hover:text-red-600 hover:border-red-200 hover:bg-red-50 flex items-center justify-center transition-all shadow-xs"
                :title="`Hapus ${item.stock?.title || item.title} dari wishlist`"
                @click.stop.prevent="(wishlist as any).toggle(item.stock || item)"
              >
                <UIcon name="i-heroicons-trash" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. Mobile Bottom Sheet Filter -->
    <div
      v-if="isMobileFilterOpen"
      class="fixed inset-0 z-50 flex flex-col justify-end md:hidden"
    >
      <div
        class="absolute inset-0 bg-black/60 transition-opacity"
        @click="isMobileFilterOpen = false"
      />

      <div
        class="relative bg-white w-full max-h-[85vh] rounded-t-3xl flex flex-col animate-slide-up shadow-2xl"
      >
        <div class="flex flex-col items-center pt-3 pb-3 border-b border-gray-100">
          <div class="w-10 h-1 bg-gray-300 rounded-full mb-3" />
          <div class="w-full px-5 flex items-center justify-between">
            <h3 class="font-extrabold text-base text-gray-900 tracking-tight">
              Filter Wishlist
            </h3>
            <button
              type="button"
              @click="isMobileFilterOpen = false"
              class="p-1.5 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
            >
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5 text-gray-700" />
            </button>
          </div>
        </div>

        <div class="p-5 overflow-y-auto flex-1 space-y-6">
          <div>
            <h4 class="font-bold text-xs uppercase tracking-wider text-gray-500 mb-2.5">
              Urutan
            </h4>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="opt in sortOptions"
                :key="opt"
                type="button"
                @click="selectedSort = opt"
                :class="
                  selectedSort === opt
                    ? 'bg-[#03AC0E] text-white border-[#03AC0E]'
                    : 'bg-white text-gray-700 border-gray-200'
                "
                class="px-3.5 py-1.5 rounded-lg text-xs font-bold border transition-colors"
              >
                {{ opt }}
              </button>
            </div>
          </div>

          <div>
            <h4 class="font-bold text-xs uppercase tracking-wider text-gray-500 mb-2.5">
              Promo & Diskon
            </h4>
            <div class="space-y-3">
              <label class="flex items-center justify-between cursor-pointer">
                <span class="text-xs font-semibold text-gray-800">Sedang Diskon</span>
                <input v-model="filterDiscount" type="checkbox" class="checkbox-custom" />
              </label>
              <label class="flex items-center justify-between cursor-pointer">
                <span class="text-xs font-semibold text-gray-800">Promo Spesial</span>
                <input v-model="filterPromo" type="checkbox" class="checkbox-custom" />
              </label>
            </div>
          </div>

          <div>
            <h4 class="font-bold text-xs uppercase tracking-wider text-gray-500 mb-2.5">Kategori</h4>
            <div v-if="categories?.length" class="space-y-3">
              <label
                v-for="cat in categories"
                :key="cat.slug || cat.id"
                class="flex items-center justify-between cursor-pointer"
              >
                <span class="text-xs font-semibold text-gray-800 capitalize">{{
                  (cat.name || cat.title || '').replace(/-/g, ' ')
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

        <div class="p-4 border-t border-gray-100 bg-white flex gap-2">
          <button
            type="button"
            class="flex-1 bg-gray-100 text-gray-700 font-bold py-3 rounded-xl text-xs"
            @click="selectedCategories = []; filterDiscount = false; filterPromo = false; isMobileFilterOpen = false"
          >
            Reset
          </button>
          <button
            type="button"
            @click="isMobileFilterOpen = false"
            class="flex-2 bg-[#03AC0E] text-white font-bold py-3 rounded-xl text-xs shadow-xs"
          >
            Terapkan ({{ filteredAndSortedWishlist.length }})
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.checkbox-custom {
  appearance: none;
  -webkit-appearance: none;
  width: 1.125rem;
  height: 1.125rem;
  min-width: 1.125rem;
  border: 1.5px solid #d1d5db;
  border-radius: 4px;
  background-color: #ffffff;
  cursor: pointer;
  position: relative;
  transition: border-color 0.15s, background-color 0.15s;
  flex-shrink: 0;
}

.checkbox-custom:hover {
  border-color: #03AC0E;
}

.checkbox-custom:checked {
  background-color: #03AC0E;
  border-color: #03AC0E;
}

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

.checkbox-custom:focus-visible {
  outline: 2px solid #03AC0E;
  outline-offset: 2px;
}

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