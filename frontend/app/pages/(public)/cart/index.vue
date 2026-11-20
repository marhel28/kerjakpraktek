<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useCartStore } from "~/stores/cart";
import { useCheckoutStore } from "~/stores/checkout";

const cartStore = useCartStore() as any;
const checkoutStore = useCheckoutStore() as any;
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
const savedForLater = ref<any[]>([]);

const filteredCartItems = computed(() => {
  let items: any[] = [...(cartStore.items || [])];

  if (filterDiscount.value) {
    items = items.filter(
      (item: any) => item.discount_percentage && item.discount_percentage > 0
    );
  }

  if (selectedCategories.value.length > 0) {
    items = items.filter((item: any) => {
      const slug = item.category_slug || "";
      return selectedCategories.value.includes(slug);
    });
  }

  return items;
});

const selectedKeys = ref<string[]>([]);

onMounted(() => {
  selectedKeys.value = filteredCartItems.value.map((item: any) => item.stock_uuid);
  const storedSaved = localStorage.getItem("pasarcctv_saved_for_later");
  if (storedSaved) {
    try {
      savedForLater.value = JSON.parse(storedSaved);
    } catch {
      savedForLater.value = [];
    }
  }
});

watch(
  () => cartStore.items?.length,
  () => {
    selectedKeys.value = selectedKeys.value.filter((uuid: string) =>
      cartStore.items?.some((item: any) => item.stock_uuid === uuid)
    );
  }
);

watch(
  savedForLater,
  (newVal) => {
    localStorage.setItem("pasarcctv_saved_for_later", JSON.stringify(newVal));
  },
  { deep: true }
);

const isAllSelected = computed({
  get: () => {
    const visibleUuids = filteredCartItems.value.map((i: any) => i.stock_uuid);
    return (
      visibleUuids.length > 0 &&
      visibleUuids.every((uuid: string) => selectedKeys.value.includes(uuid))
    );
  },
  set: (val: boolean) => {
    const visibleUuids = filteredCartItems.value.map((i: any) => i.stock_uuid);
    if (val) {
      const newSelections = new Set([...selectedKeys.value, ...visibleUuids]);
      selectedKeys.value = Array.from(newSelections);
    } else {
      selectedKeys.value = selectedKeys.value.filter(
        (uuid: string) => !visibleUuids.includes(uuid)
      );
    }
  },
});

const totalSelectedPrice = computed(() => {
  return (cartStore.items || [])
    .filter((item: any) => selectedKeys.value.includes(item.stock_uuid))
    .reduce((total: number, item: any) => {
      const base = item.price * item.quantity;
      const addons = (item.options?.addons || []).reduce(
        (acc: number, a: any) => acc + (a.price * a.quantity),
        0
      );
      return total + base + addons;
    }, 0);
});

const totalSelectedWeight = computed(() => {
  return (cartStore.items || [])
    .filter((item: any) => selectedKeys.value.includes(item.stock_uuid))
    .reduce((total: number, item: any) => {
      const base = (item.weight || 0) * item.quantity;
      const addons = (item.options?.addons || []).reduce(
        (acc: number, a: any) => acc + (a.weight * a.quantity),
        0
      );
      return total + base + addons;
    }, 0);
});

const freeShippingThreshold = 500000;
const freeShippingRemaining = computed(() => {
  return Math.max(0, freeShippingThreshold - totalSelectedPrice.value);
});
const freeShippingProgress = computed(() => {
  return Math.min(100, (totalSelectedPrice.value / freeShippingThreshold) * 100);
});

const finalPrice = computed(() =>
  Math.max(0, totalSelectedPrice.value - discountPromo.value)
);

const totalSelectedQuantity = computed(() => {
  return (cartStore.items || [])
    .filter((item: any) => selectedKeys.value.includes(item.stock_uuid))
    .reduce((total: number, item: any) => total + item.quantity, 0);
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
        code: promoCode.value.trim(),
        cart_total: totalSelectedPrice.value
      }
    });

    if (res.success) {
      discountPromo.value = res.data.discount_amount;
      couponData.value = res.data;
      toast.add({
        title: "Kupon Diterapkan",
        description: res.message,
        icon: "i-heroicons-check-circle",
        color: "success",
      });
    } else {
      discountPromo.value = 0;
      couponData.value = null;
      couponError.value = res.message;
      toast.add({
        title: "Kupon Tidak Valid",
        description: res.message,
        icon: "i-heroicons-x-circle",
        color: "error",
      });
    }
  } catch (err: any) {
    discountPromo.value = 0;
    couponData.value = null;
    couponError.value = err.data?.message || "Kupon tidak dapat digunakan";
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
    description: `${title} berhasil dihapus.`,
    icon: "i-heroicons-trash",
    color: "neutral",
  });
};

const saveForLaterItem = (item: any) => {
  if (!savedForLater.value.some((s) => s.stock_uuid === item.stock_uuid)) {
    savedForLater.value.push({ ...item });
  }
  cartStore.remove(item.stock_uuid);
  toast.add({
    title: "Disimpan untuk Nanti",
    description: `${item.title} dipindahkan ke daftar simpanan.`,
    icon: "i-heroicons-bookmark",
    color: "success",
  });
};

const moveToCart = (item: any) => {
  cartStore.add({
    stock_uuid: item.stock_uuid,
    title: item.title,
    price: item.price,
    original_price: item.original_price,
    discount_percentage: item.discount_percentage,
    image: item.image,
    quantity: 1,
    weight: item.weight,
    brand: item.brand,
    category_slug: item.category_slug,
    options: item.options,
    specs: item.specs,
  });
  savedForLater.value = savedForLater.value.filter(
    (s) => s.stock_uuid !== item.stock_uuid
  );
  toast.add({
    title: "Dipindahkan ke Keranjang",
    description: `${item.title} kembali ke keranjang belanja.`,
    icon: "i-heroicons-shopping-bag",
    color: "success",
  });
};

const removeSavedItem = (stock_uuid: string) => {
  savedForLater.value = savedForLater.value.filter(
    (s) => s.stock_uuid !== stock_uuid
  );
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
      description: "Centang setidaknya satu barang untuk melanjutkan pesanan.",
      icon: "i-heroicons-exclamation-circle",
      color: "error",
    });
    return;
  }

  const itemsToCheckout = (cartStore.items || []).filter((item: any) =>
    selectedKeys.value.includes(item.stock_uuid)
  );
  checkoutStore.setCheckoutData(itemsToCheckout, discountPromo.value, promoCode.value);
  navigateTo("/payment");
};
</script>

<template>
  <main class="bg-gray-50 min-h-screen py-6 md:py-8">
    <div class="max-w-[1280px] mx-auto px-4 md:px-6">
      <!-- Breadcrumb navigation -->
      <nav class="flex items-center gap-2 text-xs text-gray-500 mb-5">
        <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
        <span>/</span>
        <span class="text-gray-900 font-medium">Keranjang Belanja</span>
      </nav>

      <!-- Empty State -->
      <div
        v-if="cartStore.items.length === 0 && savedForLater.length === 0"
        class="bg-white border border-gray-200 rounded-xl p-10 md:p-14 text-center max-w-2xl mx-auto shadow-sm"
      >
        <div class="w-16 h-16 rounded-full bg-[#E6F7E9] text-[#03AC0E] flex items-center justify-center mx-auto mb-4">
          <UIcon name="i-heroicons-shopping-cart" class="w-8 h-8" />
        </div>
        <h1 class="text-xl font-medium text-gray-900 mb-2">
          Keranjang Belanja Anda Kosong
        </h1>
        <p class="text-sm text-gray-500 mb-6 leading-relaxed max-w-md mx-auto">
          Belum ada produk CCTV atau perlengkapan keamanan yang ditambahkan ke keranjang belanja Anda.
        </p>
        <NuxtLink
          to="/produk"
          class="inline-flex items-center gap-2 bg-[#03AC0E] text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-[#028C0B] transition-colors shadow-sm"
        >
          <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
          Lihat Katalog Produk
        </NuxtLink>
      </div>

      <!-- Main Amazon-Style Layout -->
      <div v-else class="flex flex-col lg:flex-row gap-6 items-start">
        <!-- Left Main Column (Cart List & Saved Items) -->
        <div class="flex-1 w-full min-w-0 space-y-6">
          <div class="bg-white border border-gray-200 rounded-xl p-5 md:p-6 shadow-sm">
            <!-- Header Row -->
            <div class="flex items-end justify-between pb-4 border-b border-gray-200">
              <div>
                <h1 class="text-xl md:text-2xl font-medium text-gray-900 tracking-tight">
                  Keranjang Belanja
                </h1>
                <div class="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  <button
                    type="button"
                    @click="isAllSelected = !isAllSelected"
                    class="text-[#03AC0E] hover:underline font-medium"
                  >
                    {{ isAllSelected ? "Batalkan semua pilihan" : "Pilih semua barang" }}
                  </button>
                  <span>•</span>
                  <span>{{ cartStore.items.length }} barang terdaftar</span>
                </div>
              </div>
              <span class="hidden md:block text-xs font-medium text-gray-400 uppercase tracking-wider">
                Harga
              </span>
            </div>

            <!-- Free Shipping Progress Banner -->
            <div class="mt-4 p-3.5 bg-[#E6F7E9] border border-[#C8E6CC] rounded-lg text-xs">
              <div class="flex items-center gap-2 text-gray-800 font-medium">
                <UIcon name="i-heroicons-truck" class="w-4 h-4 text-[#03AC0E] shrink-0" />
                <span v-if="freeShippingRemaining <= 0" class="text-[#03AC0E]">
                  Selamat, pesanan Anda berhak mendapatkan Gratis Ongkir resmi.
                </span>
                <span v-else>
                  Tambah <span class="font-medium text-gray-900">{{ formatPrice(freeShippingRemaining) }}</span> lagi untuk memenuhi syarat Bebas Biaya Kirim.
                </span>
              </div>
              <div class="w-full bg-white rounded-full h-1.5 mt-2.5 overflow-hidden border border-[#C8E6CC]">
                <div
                  class="bg-[#03AC0E] h-full transition-all duration-300"
                  :style="{ width: `${freeShippingProgress}%` }"
                ></div>
              </div>
            </div>

            <!-- Items List -->
            <div v-if="cartStore.items.length === 0" class="py-10 text-center text-sm text-gray-500">
              Tidak ada produk aktif di keranjang saat ini.
            </div>

            <div v-else class="divide-y divide-gray-100">
              <article
                v-for="item in filteredCartItems"
                :key="item.stock_uuid"
                class="py-5 flex gap-3 md:gap-4 items-start"
              >
                <!-- Selection Checkbox -->
                <div class="pt-1 shrink-0">
                  <input
                    type="checkbox"
                    :value="item.stock_uuid"
                    v-model="selectedKeys"
                    :id="`item-${item.stock_uuid}`"
                    class="w-4 h-4 text-[#03AC0E] border-gray-300 rounded focus:ring-[#03AC0E] cursor-pointer"
                  />
                </div>

                <!-- Product Thumbnail -->
                <NuxtLink
                  :to="`/product/${item.stock_uuid}`"
                  class="w-20 h-20 md:w-28 md:h-28 rounded-lg border border-gray-100 bg-white p-2 shrink-0 flex items-center justify-center overflow-hidden hover:border-[#03AC0E] transition-colors"
                >
                  <NuxtImg
                    :src="item.image"
                    :alt="item.title"
                    loading="lazy"
                    format="webp"
                    class="w-full h-full object-contain"
                  />
                </NuxtLink>

                <!-- Product Details & Actions -->
                <div class="flex-1 min-w-0 flex flex-col justify-between self-stretch">
                  <div>
                    <div class="flex justify-between items-start gap-3">
                      <div class="min-w-0 pr-2">
                        <NuxtLink
                          :to="`/product/${item.stock_uuid}`"
                          class="text-sm md:text-base font-medium text-gray-900 hover:text-[#03AC0E] transition-colors line-clamp-2 leading-snug"
                        >
                          {{ item.title }}
                        </NuxtLink>
                        <div class="flex items-center gap-2 mt-1 flex-wrap text-xs">
                          <span
                            v-if="item.brand"
                            class="text-[11px] font-medium text-[#03AC0E] uppercase tracking-wider"
                          >
                            {{ item.brand }}
                          </span>
                          <span class="text-gray-300">•</span>
                          <span class="text-[#03AC0E] text-xs font-medium">Stok Tersedia</span>
                          <span v-if="item.weight" class="text-gray-400 text-xs">
                            ({{ formatWeight(item.weight) }})
                          </span>
                        </div>
                      </div>

                      <!-- Desktop Price Column -->
                      <div class="hidden md:block text-right shrink-0">
                        <p class="text-base font-medium text-[#03AC0E]">
                          {{ formatPrice(item.price) }}
                        </p>
                        <p
                          v-if="item.original_price && item.original_price > item.price"
                          class="text-xs text-gray-400 line-through mt-0.5"
                        >
                          {{ formatPrice(item.original_price) }}
                        </p>
                      </div>
                    </div>

                    <!-- Addons Row -->
                    <div
                      v-if="item.options?.addons?.length"
                      class="mt-2.5 space-y-1 bg-gray-50 border border-gray-100 rounded-md p-2 text-xs"
                    >
                      <p class="text-[11px] font-medium text-gray-500 uppercase tracking-wide">Tambahan Aksesori:</p>
                      <div
                        v-for="addon in item.options.addons"
                        :key="addon.uuid || addon.addon_uuid"
                        class="flex justify-between items-center text-gray-700"
                      >
                        <span class="truncate">+ {{ addon.name }} (x{{ addon.quantity }})</span>
                        <span class="font-medium text-gray-900 ml-2">
                          {{ formatPrice(addon.price * addon.quantity) }}
                        </span>
                      </div>
                    </div>

                    <!-- Mobile Price -->
                    <div class="md:hidden mt-2">
                      <span class="text-sm font-medium text-[#03AC0E]">
                        {{ formatPrice(item.price) }}
                      </span>
                      <span
                        v-if="item.original_price && item.original_price > item.price"
                        class="text-xs text-gray-400 line-through ml-2"
                      >
                        {{ formatPrice(item.original_price) }}
                      </span>
                    </div>
                  </div>

                  <!-- Amazon-Style Action Row -->
                  <div class="flex flex-wrap items-center gap-y-2 gap-x-4 mt-4 text-xs text-gray-600 pt-2">
                    <!-- Qty Stepper -->
                    <div class="flex items-center border border-gray-200 rounded-md bg-white shadow-xs">
                      <button
                        type="button"
                        @click="decreaseQty(item)"
                        :disabled="item.quantity <= 1"
                        class="w-7 h-7 flex items-center justify-center text-gray-500 hover:text-gray-900 hover:bg-gray-50 disabled:opacity-30 rounded-l-md transition-colors"
                        aria-label="Kurangi jumlah"
                      >
                        <UIcon name="i-heroicons-minus" class="w-3.5 h-3.5" />
                      </button>
                      <span class="w-8 text-center font-medium text-gray-900">
                        {{ item.quantity }}
                      </span>
                      <button
                        type="button"
                        @click="increaseQty(item.stock_uuid)"
                        class="w-7 h-7 flex items-center justify-center text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-r-md transition-colors"
                        aria-label="Tambah jumlah"
                      >
                        <UIcon name="i-heroicons-plus" class="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <span class="text-gray-300">|</span>

                    <button
                      type="button"
                      @click="removeItem(item.stock_uuid, item.title)"
                      class="text-gray-500 hover:text-red-600 transition-colors"
                    >
                      Hapus
                    </button>

                    <span class="text-gray-300">|</span>

                    <button
                      type="button"
                      @click="saveForLaterItem(item)"
                      class="text-gray-500 hover:text-[#03AC0E] transition-colors"
                    >
                      Simpan untuk Nanti
                    </button>

                    <span class="text-gray-300">|</span>

                    <NuxtLink
                      :to="`/compare?add=${item.stock_uuid}`"
                      class="text-gray-500 hover:text-[#03AC0E] transition-colors"
                    >
                      Bandingkan
                    </NuxtLink>
                  </div>
                </div>
              </article>
            </div>

            <!-- Bottom Subtotal Line inside Left Panel -->
            <div
              v-if="cartStore.items.length > 0"
              class="mt-6 pt-4 border-t border-gray-200 flex justify-end items-baseline gap-2 text-right"
            >
              <span class="text-sm text-gray-600">
                Subtotal ({{ totalSelectedQuantity }} barang terpilih):
              </span>
              <span class="text-lg md:text-xl font-medium text-gray-900">
                {{ formatPrice(totalSelectedPrice) }}
              </span>
            </div>
          </div>

          <!-- Amazon-Style Save for Later Section -->
          <div
            v-if="savedForLater.length > 0"
            class="bg-white border border-gray-200 rounded-xl p-5 md:p-6 shadow-sm"
          >
            <div class="pb-3 border-b border-gray-200 mb-4">
              <h2 class="text-lg font-medium text-gray-900">
                Disimpan untuk Nanti ({{ savedForLater.length }} barang)
              </h2>
              <p class="text-xs text-gray-500 mt-1">
                Produk yang Anda tunda pembeliannya tetap tersimpan di sini.
              </p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="item in savedForLater"
                :key="item.stock_uuid"
                class="border border-gray-200 rounded-lg p-3.5 flex flex-col justify-between bg-gray-50/50 hover:border-gray-300 transition-colors"
              >
                <div class="flex gap-3 items-start">
                  <div class="w-16 h-16 rounded bg-white border border-gray-100 p-1 shrink-0 flex items-center justify-center">
                    <NuxtImg
                      :src="item.image"
                      :alt="item.title"
                      loading="lazy"
                      format="webp"
                      class="w-full h-full object-contain"
                    />
                  </div>
                  <div class="min-w-0 flex-1">
                    <NuxtLink
                      :to="`/product/${item.stock_uuid}`"
                      class="text-xs font-medium text-gray-900 line-clamp-2 hover:text-[#03AC0E] transition-colors leading-snug"
                    >
                      {{ item.title }}
                    </NuxtLink>
                    <p class="text-xs font-medium text-[#03AC0E] mt-1">
                      {{ formatPrice(item.price) }}
                    </p>
                  </div>
                </div>

                <div class="flex items-center gap-2 mt-3 pt-2 border-t border-gray-200 text-xs">
                  <button
                    type="button"
                    @click="moveToCart(item)"
                    class="text-[#03AC0E] hover:underline font-medium"
                  >
                    Pindahkan ke Keranjang
                  </button>
                  <span class="text-gray-300">•</span>
                  <button
                    type="button"
                    @click="removeSavedItem(item.stock_uuid)"
                    class="text-gray-400 hover:text-red-600 transition-colors"
                  >
                    Hapus
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Sticky Summary Box -->
        <aside class="w-full lg:w-[340px] shrink-0 sticky top-24 space-y-4">
          <div class="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <!-- Free Shipping Badge in Box -->
            <div class="flex items-center gap-2 text-xs text-gray-700 pb-3 border-b border-gray-100">
              <UIcon name="i-heroicons-shield-check" class="w-4 h-4 text-[#03AC0E] shrink-0" />
              <span>Transaksi Aman dengan Garansi Resmi</span>
            </div>

            <!-- Subtotal Headline -->
            <div class="py-4 border-b border-gray-100">
              <div class="flex justify-between items-baseline text-sm text-gray-600 mb-1">
                <span>Subtotal ({{ totalSelectedQuantity }} barang):</span>
                <span class="text-lg font-medium text-gray-900">
                  {{ formatPrice(totalSelectedPrice) }}
                </span>
              </div>
              <div v-if="discountPromo > 0" class="flex justify-between text-xs text-[#03AC0E] mt-1">
                <span>Potongan Kupon:</span>
                <span>-{{ formatPrice(discountPromo) }}</span>
              </div>
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>Estimasi Total Berat:</span>
                <span>{{ formatWeight(totalSelectedWeight) }}</span>
              </div>
            </div>

            <!-- Final Amount -->
            <div class="py-3 flex justify-between items-baseline">
              <span class="text-sm font-medium text-gray-900">Total Akhir:</span>
              <span class="text-xl font-medium text-[#03AC0E]">
                {{ formatPrice(finalPrice) }}
              </span>
            </div>

            <!-- Primary Checkout CTA -->
            <button
              type="button"
              @click="handleCheckout"
              :disabled="selectedKeys.length === 0"
              class="w-full mt-2 bg-[#03AC0E] text-white py-3 px-4 rounded-lg text-sm font-medium hover:bg-[#028C0B] disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-xs flex items-center justify-center gap-2"
            >
              <UIcon name="i-heroicons-lock-closed" class="w-4 h-4" />
              Lanjut ke Pembayaran
            </button>

            <!-- Promo Code Accordion -->
            <div class="mt-5 pt-4 border-t border-gray-100">
              <label for="promo-input" class="block text-xs font-medium text-gray-700 mb-1.5">
                Kupon & Voucher Promosi
              </label>

              <div v-if="!couponData" class="flex gap-2">
                <input
                  id="promo-input"
                  v-model="promoCode"
                  type="text"
                  placeholder="Masukkan kode kupon"
                  class="flex-1 text-xs border border-gray-300 rounded-md px-3 py-2 uppercase tracking-wide placeholder:normal-case placeholder:tracking-normal focus:outline-none focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E]"
                  @keyup.enter="applyPromoCode"
                />
                <button
                  type="button"
                  @click="applyPromoCode"
                  :disabled="isValidatingCoupon || !promoCode"
                  class="bg-gray-100 text-gray-800 hover:bg-gray-200 disabled:opacity-40 px-3.5 py-2 rounded-md text-xs font-medium transition-colors"
                >
                  Terapkan
                </button>
              </div>

              <div
                v-else
                class="flex items-center justify-between bg-[#E6F7E9] border border-[#C8E6CC] p-2.5 rounded-md text-xs"
              >
                <div>
                  <span class="font-medium text-[#03AC0E] uppercase tracking-wider">
                    {{ couponData.coupon_code }}
                  </span>
                  <p class="text-[11px] text-gray-600 mt-0.5">
                    Hemat {{ formatPrice(couponData.discount_amount) }}
                  </p>
                </div>
                <button
                  type="button"
                  @click="removeCoupon"
                  class="text-gray-400 hover:text-red-600 p-1 transition-colors"
                  aria-label="Hapus kupon"
                >
                  <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                </button>
              </div>

              <p v-if="couponError" class="text-xs text-red-600 mt-2 flex items-center gap-1">
                <UIcon name="i-heroicons-exclamation-circle" class="w-3.5 h-3.5 shrink-0" />
                {{ couponError }}
              </p>
            </div>
          </div>

          <!-- Trust Badges Summary -->
          <div class="bg-white border border-gray-200 rounded-xl p-4 text-xs text-gray-500 space-y-2">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-badge" class="w-4 h-4 text-[#03AC0E] shrink-0" />
              <span>Jaminan produk 100% orisinil dan bergaransi</span>
            </div>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 text-[#03AC0E] shrink-0" />
              <span>Layanan retur mudah hingga 30 hari</span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </main>
</template>

<style scoped>
main {
  font-family: "Plus Jakarta Sans", sans-serif;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>