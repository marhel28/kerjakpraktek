<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useCartStore } from "~/stores/cart";
import { useCheckoutStore } from "~/stores/checkout";

const cartStore = useCartStore();
const checkoutStore = useCheckoutStore();
const toast = useToast();

onMounted(async () => {
  await cartStore.fetchCartFromAPI();
});

const { data: categories } = await useFetch<any>("/api/category", {
  lazy: true,
  transform: (res) => (Array.isArray(res) ? res : res?.data || []),
});

const filterDiscount = ref(false);
const selectedCategories = ref<string[]>([]);
const promoCode = ref("");
const discountPromo = ref(0);

const filteredCartItems = computed(() => {
  let items = [...cartStore.items];

  if (filterDiscount.value) {
    items = items.filter(
      (item) => item.discount_percentage && item.discount_percentage > 0
    );
  }

  if (selectedCategories.value.length > 0) {
    items = items.filter((item) => {
      const slug = item.category_slug || "";
      return selectedCategories.value.includes(slug);
    });
  }

  return items;
});

const selectedKeys = ref<string[]>([]);

onMounted(() => {
  selectedKeys.value = filteredCartItems.value.map((item) => item.stock_uuid);
});

watch(
  () => cartStore.items.length,
  () => {
    selectedKeys.value = selectedKeys.value.filter((uuid) =>
      cartStore.items.some((item) => item.stock_uuid === uuid)
    );
  }
);

const isAllSelected = computed({
  get: () => {
    const visibleUuids = filteredCartItems.value.map((i) => i.stock_uuid);
    return (
      visibleUuids.length > 0 &&
      visibleUuids.every((uuid) => selectedKeys.value.includes(uuid))
    );
  },
  set: (val) => {
    const visibleUuids = filteredCartItems.value.map((i) => i.stock_uuid);
    if (val) {
      const newSelections = new Set([...selectedKeys.value, ...visibleUuids]);
      selectedKeys.value = Array.from(newSelections);
    } else {
      selectedKeys.value = selectedKeys.value.filter(
        (uuid) => !visibleUuids.includes(uuid)
      );
    }
  },
});

const totalSelectedPrice = computed(() => {
  return cartStore.items
    .filter((item) => selectedKeys.value.includes(item.stock_uuid))
    .reduce((total, item) => {
      const base = item.price * item.quantity;
      const addons = (item.options?.addons || []).reduce(
        (acc: number, a: any) => acc + (a.price * a.quantity),
        0
      );
      return total + base + addons;
    }, 0);
});

const totalSelectedWeight = computed(() => {
  return cartStore.items
    .filter((item) => selectedKeys.value.includes(item.stock_uuid))
    .reduce((total, item) => {
      const base = (item.weight || 0) * item.quantity;
      const addons = (item.options?.addons || []).reduce(
        (acc: number, a: any) => acc + (a.weight * a.quantity),
        0
      );
      return total + base + addons;
    }, 0);
});

const finalPrice = computed(() =>
  Math.max(0, totalSelectedPrice.value - discountPromo.value)
);

const totalSelectedQuantity = computed(() => {
  return cartStore.items
    .filter((item) => selectedKeys.value.includes(item.stock_uuid))
    .reduce((total, item) => total + item.quantity, 0);
});

const isValidatingCoupon = ref(false);
const couponError = ref("");
const couponData = ref<any>(null);

const applyPromoCode = async () => {
  if (!promoCode.value.trim()) {
    discountPromo.value = 0;
    couponData.value = null;
    return;
  }

  isValidatingCoupon.value = true;
  couponError.value = "";

  try {
    const config = useRuntimeConfig();
    const res: any = await $fetch(`${config.public.apiBase}/stok/public/coupon/validate`, {
      method: "POST",
      body: {
        code: promoCode.value,
        cart_total: totalSelectedPrice.value
      }
    });

    if (res.success) {
      discountPromo.value = res.data.discount_amount;
      couponData.value = res.data;
      toast.add({
        title: "Kupon Berhasil",
        description: res.message,
        icon: "i-heroicons-check-circle",
        color: "green",
      });
    } else {
      discountPromo.value = 0;
      couponData.value = null;
      couponError.value = res.message;
      toast.add({
        title: "Kupon Gagal",
        description: res.message,
        icon: "i-heroicons-x-circle",
        color: "red",
      });
    }
  } catch (err: any) {
    discountPromo.value = 0;
    couponData.value = null;
    couponError.value = err.data?.message || "Terjadi kesalahan";
  } finally {
    isValidatingCoupon.value = false;
  }
};

const removeCoupon = () => {
  promoCode.value = "";
  discountPromo.value = 0;
  couponData.value = null;
  couponError.value = "";
};

const increaseQty = (stock_uuid: string) => cartStore.updateQuantity(stock_uuid, 1);
const decreaseQty = (item: any) => {
  if (item.quantity > 1) cartStore.updateQuantity(item.stock_uuid, -1);
};

const removeItem = (stock_uuid: string, title: string) => {
  cartStore.remove(stock_uuid);
  toast.add({
    title: "Dihapus dari Keranjang",
    description: `${title} telah dihapus.`,
    icon: "i-heroicons-trash",
    color: "red",
  });
};

function formatPrice(value: number) {
  if (!value) return "Rp 0";
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  })
    .format(value)
    .replace("Rp", "Rp ");
}

const formatWeight = (grams: number | undefined) => {
  if (!grams) return "0 gr";
  return grams >= 1000
    ? `${(grams / 1000).toFixed(2).replace(/\.00$/, "")} kg`
    : `${grams} gr`;
};

const handleCheckout = () => {
  if (selectedKeys.value.length === 0) {
    toast.add({
      title: "Pilih Barang",
      description: "Silakan centang barang yang ingin dibeli.",
      icon: "i-heroicons-exclamation-circle",
      color: "red",
    });
    return;
  }

  const itemsToCheckout = cartStore.items.filter((item) =>
    selectedKeys.value.includes(item.stock_uuid)
  );
  checkoutStore.setCheckoutData(itemsToCheckout, discountPromo.value, promoCode.value);
  navigateTo("/payment");
};
</script>

<template>
  <main class="bg-[#F8F8F8] min-h-screen py-10">
    <div class="max-w-[1400px] mx-auto px-4 md:px-6">
      <h1 class="text-2xl font-black text-black uppercase tracking-tight mb-8">
        Keranjang Belanja
      </h1>

      <div
        v-if="cartStore.items.length === 0"
        class="bg-white border border-gray-200 rounded-2xl p-16 flex flex-col items-center justify-center text-center shadow-sm"
      >
        <UIcon name="i-heroicons-shopping-bag" class="w-16 h-16 text-gray-300 mb-6" />
        <h2 class="text-2xl font-bold text-black mb-2">Keranjangmu masih kosong</h2>
        <p class="text-gray-500 mb-8 max-w-md">
          Ayo mulai belanja! Temukan berbagai produk CCTV dan perlengkapan lainnya.
        </p>
        <NuxtLink to="/">
          <button
            class="bg-black text-white px-8 py-3.5 rounded-xl font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors shadow-lg"
          >
            Mulai Belanja
          </button>
        </NuxtLink>
      </div>

      <div v-else class="flex flex-col lg:flex-row gap-8 items-start">
        <aside class="hidden lg:block w-[260px] shrink-0 sticky top-24">
          <h2 class="font-black text-lg mb-4 text-gray-900 tracking-tight">
            Filter Keranjang
          </h2>
          <div
            class="border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-sm"
          >
            <div class="p-5 border-b border-gray-100">
              <h3 class="font-bold text-sm tracking-wide mb-4">PENAWARAN</h3>
              <label class="flex items-center gap-3 cursor-pointer group">
                <input v-model="filterDiscount" type="checkbox" class="checkbox-custom" />
                <span class="text-sm font-semibold text-gray-600 group-hover:text-black"
                  >Harga Diskon</span
                >
              </label>
            </div>
            <div class="p-5 border-b border-gray-100">
              <h3 class="font-bold text-sm tracking-wide mb-4">KATEGORI</h3>
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
                    class="text-sm font-semibold text-gray-600 group-hover:text-black line-clamp-1"
                    >{{ cat.name || cat.title }}</span
                  >
                </label>
              </div>
            </div>
          </div>
        </aside>

        <div class="flex-1 min-w-0 space-y-4">
          <!-- Pilih Semua -->
          <div
            class="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between shadow-sm"
          >
            <label class="flex items-center gap-3 cursor-pointer group">
              <input
                type="checkbox"
                v-model="isAllSelected"
                class="checkbox-custom checkbox-custom--lg"
              />
              <span class="font-bold text-gray-800 group-hover:text-black"
                >Pilih Semua (Tampil)</span
              >
            </label>
            <button
              v-if="selectedKeys.length > 0"
              @click="selectedKeys = []"
              class="text-sm font-bold text-red-600 hover:text-red-800 transition-colors"
            >
              Hapus Pilihan
            </button>
          </div>

          <div
            v-if="filteredCartItems.length === 0"
            class="p-10 text-center text-gray-500 font-bold border-2 border-dashed border-gray-200 rounded-xl bg-white"
          >
            Tidak ada produk yang sesuai dengan filter.
          </div>

          <div
            v-for="item in filteredCartItems"
            :key="item.stock_uuid"
            class="bg-white border border-gray-200 rounded-2xl p-4 md:p-5 shadow-sm transition-all hover:border-green-500/40 hover:shadow-[0_10px_30px_-15px_rgba(22,163,74,0.12)] flex gap-4 md:gap-5 relative group"
          >
            <input
              type="checkbox"
              :value="item.stock_uuid"
              v-model="selectedKeys"
              class="checkbox-custom checkbox-custom--lg mt-2.5 shrink-0"
            />

            <NuxtLink
              :to="`/product/${item.stock_uuid}`"
              class="relative w-24 h-24 md:w-28 md:h-28 shrink-0 rounded-xl border border-gray-100 bg-gradient-to-b from-gray-50 to-[#f9fafb] overflow-hidden block"
            >
              <div
                v-if="item.discount_percentage && item.discount_percentage > 0"
                class="absolute top-1.5 left-1.5 z-20"
              >
                <div
                  class="bg-gradient-to-r from-red-500 to-rose-600 text-white text-[9px] font-black px-2 py-0.5 rounded shadow-sm shadow-red-500/30 flex items-center gap-1"
                >
                  <UIcon name="i-heroicons-arrow-trending-down" class="w-3 h-3" />
                  {{ item.discount_percentage }}%
                </div>
              </div>

              <NuxtImg
                :src="item.image"
                :alt="item.title"
                loading="lazy"
                format="webp"
                class="w-full h-full object-contain p-2 transition-transform duration-500 group-hover:scale-110"
              />
            </NuxtLink>

            <div class="flex-1 flex flex-col min-w-0">
              <div class="flex justify-between items-start gap-4">
                <div>
                  <div class="mb-1.5 flex items-center flex-wrap gap-2">
                    <span
                      class="text-[9px] font-black uppercase tracking-wider text-green-700 bg-green-50 px-2 py-0.5 rounded-md border border-green-200/60 truncate max-w-[120px]"
                    >
                      {{ item.brand || "NO BRAND" }}
                    </span>
                    <span
                      v-if="item.category_slug"
                      class="text-[9px] font-bold text-gray-400 uppercase tracking-widest truncate"
                    >
                      {{ item.category_slug.replace(/-/g, " ") }}
                    </span>
                    <span
                      v-if="item.weight"
                      class="text-[9px] font-bold text-gray-500 uppercase tracking-widest bg-gray-100 px-1.5 py-0.5 rounded border border-gray-200"
                    >
                      {{ formatWeight(item.weight) }}
                    </span>
                  </div>

                  <NuxtLink :to="`/product/${item.stock_uuid}`">
                    <h3
                      class="text-[14px] md:text-[15px] font-bold text-gray-800 line-clamp-2 leading-snug group-hover:text-green-600 transition-colors"
                    >
                      {{ item.title }}
                    </h3>
                  </NuxtLink>

                  <div
                    v-if="item.specs && Object.keys(item.specs).length > 0"
                    class="mt-2 space-y-1"
                  >
                    <div
                      v-for="[key, value] in Object.entries(item.specs).slice(0, 2)"
                      :key="key"
                      class="flex items-center gap-1.5 text-gray-500"
                    >
                      <div class="w-1 h-1 rounded-full bg-gray-300"></div>
                      <p class="text-[11px] truncate leading-none">
                        <span class="font-bold text-gray-600 capitalize"
                          >{{ key.replace(/_/g, " ") }}:</span
                        >
                        <span class="capitalize"> {{ value }}</span>
                      </p>
                    </div>
                  </div>

                  <!-- Addons Display -->
                  <div v-if="item.options?.addons?.length" class="mt-3 space-y-2 border-l-2 border-green-500 pl-3 py-0.5">
                    <div v-for="addon in item.options.addons" :key="addon.uuid || addon.addon_uuid" class="flex justify-between items-center text-[11px]">
                      <span class="text-gray-600 font-medium line-clamp-1">↳ {{ addon.name }} (x{{ addon.quantity }})</span>
                      <span class="text-green-600 font-black whitespace-nowrap ml-2">+ {{ formatPrice(addon.price * addon.quantity) }}</span>
                    </div>
                  </div>
                </div>

                <button
                  @click="removeItem(item.stock_uuid, item.title)"
                  class="text-gray-400 hover:text-red-500 hover:bg-red-50 p-1.5 rounded-lg transition-colors flex shrink-0"
                  title="Hapus Barang"
                >
                  <UIcon name="i-heroicons-trash" class="w-5 h-5" />
                </button>
              </div>

              <div class="flex flex-wrap items-end justify-between mt-auto pt-4 md:pt-2">
                <div class="flex flex-col">
                  <div
                    v-if="item.original_price && item.original_price > item.price"
                    class="text-[11px] font-medium text-gray-400 line-through decoration-gray-300 mb-0.5"
                  >
                    {{ formatPrice(item.original_price) }}
                  </div>
                  <div
                    class="text-[16px] md:text-[18px] font-black tracking-tight"
                    :class="{
                      'text-red-600':
                        item.discount_percentage && item.discount_percentage > 0,
                      'text-gray-900': !item.discount_percentage,
                    }"
                  >
                    {{ formatPrice(item.price) }}
                  </div>
                </div>

                <div
                  class="flex items-center border border-gray-200 rounded-lg p-0.5 bg-gray-50/50 shadow-sm"
                >
                  <button
                    @click="decreaseQty(item)"
                    :disabled="item.quantity <= 1"
                    class="w-8 h-8 flex items-center justify-center font-bold text-gray-600 hover:bg-white hover:shadow-sm rounded-md transition-all disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:shadow-none"
                  >
                    <UIcon name="i-heroicons-minus" class="w-4 h-4" />
                  </button>
                  <input
                    type="number"
                    v-model.number="item.quantity"
                    readonly
                    class="w-10 text-center text-sm font-bold bg-transparent outline-none border-none focus:ring-0 p-0 cursor-default text-gray-800"
                  />
                  <button
                    @click="increaseQty(item.stock_uuid)"
                    class="w-8 h-8 flex items-center justify-center font-bold text-green-600 hover:bg-white hover:shadow-sm hover:text-green-700 rounded-md transition-all"
                  >
                    <UIcon name="i-heroicons-plus" class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="w-full lg:w-[360px] shrink-0">
          <div
            class="sticky top-24 bg-white border-2 border-black rounded-2xl p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
          >
            <h3
              class="font-black text-black uppercase tracking-wider mb-6 pb-4 border-b-2 border-black"
            >
              Ringkasan Belanja
            </h3>

            <div class="mb-6">
              <div 
                class="group relative overflow-hidden bg-white border border-gray-100 rounded-2xl p-5 shadow-sm transition-all hover:shadow-md active:scale-[0.99]"
                :class="{ 'ring-2 ring-indigo-500 ring-offset-2': couponData }"
              >
                <!-- Decorative background -->
                <div class="absolute -right-4 -top-4 w-20 h-20 bg-indigo-50 rounded-full opacity-50 group-hover:scale-125 transition-transform duration-700"></div>
                
                <div class="relative">
                  <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-2.5">
                      <div class="w-9 h-9 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-200">
                        <UIcon name="i-heroicons-ticket" class="w-5 h-5" />
                      </div>
                      <div>
                        <p class="text-[10px] font-black text-indigo-600 uppercase tracking-[0.15em] leading-none mb-1">Promo & Voucher</p>
                        <h4 class="text-sm font-black text-gray-900 tracking-tight">Makin Hemat</h4>
                      </div>
                    </div>
                  </div>

                  <div v-if="!couponData" class="flex gap-2">
                    <div class="relative flex-1">
                      <input
                        v-model="promoCode"
                        type="text"
                        placeholder="Masukkan kode..."
                        class="w-full text-sm font-bold bg-gray-50 border-2 border-transparent rounded-xl px-4 py-3 outline-none focus:bg-white focus:border-indigo-600 focus:ring-4 focus:ring-indigo-500/10 uppercase transition-all placeholder:normal-case placeholder:font-medium placeholder:text-gray-400"
                        @keyup.enter="applyPromoCode"
                      />
                      <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center" v-if="isValidatingCoupon">
                         <div class="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                      </div>
                    </div>
                    <button
                      @click="applyPromoCode"
                      :disabled="isValidatingCoupon || !promoCode"
                      class="bg-gray-900 text-white px-6 py-3 rounded-xl text-[11px] font-black hover:bg-black disabled:opacity-30 transition-all uppercase tracking-widest shadow-lg shadow-gray-200 active:translate-y-0.5"
                    >
                      Gunakan
                    </button>
                  </div>

                  <div v-else class="flex items-center justify-between bg-indigo-600 p-3.5 rounded-xl shadow-inner border border-indigo-400/30 overflow-hidden relative">
                    <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-white/20 to-transparent"></div>
                    <div class="flex items-center gap-3 relative z-10">
                      <div class="w-8 h-8 bg-white/20 backdrop-blur-md rounded-lg flex items-center justify-center text-white border border-white/30">
                        <UIcon name="i-heroicons-sparkles" class="w-5 h-5" />
                      </div>
                      <div>
                        <div class="flex items-center gap-2">
                           <span class="text-xs font-black text-white uppercase tracking-widest font-mono">{{ couponData.coupon_code }}</span>
                           <span class="text-[10px] font-bold text-indigo-100 bg-black/20 px-2 py-0.5 rounded">Aktif</span>
                        </div>
                        <p class="text-[11px] text-white/90 font-medium">Hemat {{ formatPrice(couponData.discount_amount) }}</p>
                      </div>
                    </div>
                    <button @click="removeCoupon" class="relative z-10 bg-white/10 hover:bg-white/20 text-white p-2 rounded-lg transition-all active:scale-90">
                      <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                    </button>
                  </div>

                  <transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-2 opacity-0" enter-to-class="transform translate-y-0 opacity-100">
                    <p v-if="couponError" class="mt-3 text-[11px] text-red-500 font-bold flex items-center gap-1.5 bg-red-50 p-2 rounded-lg border border-red-100">
                      <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4" />
                      {{ couponError }}
                    </p>
                  </transition>
                </div>
              </div>
            </div>

            <div class="space-y-3 mb-6 bg-gray-50 p-4 rounded-xl border border-gray-100">
              <div class="flex justify-between text-gray-600 font-bold text-sm">
                <span>Total Harga ({{ totalSelectedQuantity }} brg)</span>
                <span>{{ formatPrice(totalSelectedPrice) }}</span>
              </div>

              <div class="flex justify-between text-gray-500 font-medium text-xs">
                <span>Total Berat</span>
                <span>{{ formatWeight(totalSelectedWeight) }}</span>
              </div>

              <div
                v-if="discountPromo > 0"
                class="flex justify-between text-green-600 font-bold text-sm mt-2"
              >
                <span>Diskon Promo</span>
                <span>-{{ formatPrice(discountPromo) }}</span>
              </div>
              <div
                class="flex justify-between items-end pt-3 border-t border-gray-200 mt-2"
              >
                <span class="font-black text-black text-sm uppercase tracking-wide"
                  >Total Belanja</span
                >
                <span class="text-2xl font-black text-red-600 leading-none">{{
                  formatPrice(finalPrice)
                }}</span>
              </div>
            </div>

            <button
              @click="handleCheckout"
              class="w-full bg-black text-white font-black py-4 rounded-xl text-sm uppercase tracking-widest hover:bg-gray-800 transition-all active:scale-[0.98]"
              :class="{
                'opacity-50 cursor-not-allowed active:scale-100':
                  selectedKeys.length === 0,
              }"
            >
              Beli ({{ totalSelectedQuantity }})
            </button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,600;0,700;0,800;0,900;1,400&display=swap");

main {
  font-family: "Plus Jakarta Sans", sans-serif;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ✅ FIX: Custom checkbox — background putih, centang hijau, konsisten semua browser */
.checkbox-custom {
  appearance: none;
  -webkit-appearance: none;
  width: 1.125rem; /* 18px — setara w-4 */
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

/* Varian lebih besar (w-5) untuk "Pilih Semua" & item list */
.checkbox-custom--lg {
  width: 1.25rem; /* 20px — setara w-5 */
  height: 1.25rem;
  min-width: 1.25rem;
}

.checkbox-custom:hover {
  border-color: #16a34a;
}

.checkbox-custom:checked {
  background-color: #16a34a;
  border-color: #16a34a;
}

/* Centang putih */
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

/* Centang putih varian lg — sedikit lebih besar */
.checkbox-custom--lg:checked::after {
  left: 5px;
  top: 1px;
  width: 6px;
  height: 10px;
}

.checkbox-custom:focus-visible {
  outline: 2px solid #16a34a;
  outline-offset: 2px;
}

/* Hilangkan spinner number input */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  appearance: textfield;
  -moz-appearance: textfield;
}
</style>
