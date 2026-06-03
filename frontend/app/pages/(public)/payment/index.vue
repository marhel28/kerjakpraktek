<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useCheckoutStore } from "~/stores/checkout";

definePageMeta({ layout: "public" });

useHead({
  script: [
    {
      src: "https://app.sandbox.midtrans.com/snap/snap.js",
      "data-client-key": "SB-Mid-client-pn3mYe4w4xeY6F0w",
      async: true,
    },
  ],
});
const config = useRuntimeConfig();
const checkoutStore = useCheckoutStore();
const API_TRANSAKSI = `${config.public.apiBase}/transaksi`;
const API_CEK = `${config.public.apiBase}/cek`;

const getToken = () => useCookie("token").value;
const toast = useToast();

const defaultAddress = ref<any>(null);
const shippingOptions = ref<any[]>([]);
const selectedShipping = ref<any>(null);
const selectedPaymentMethod = ref("gopay");

const isLoadingAddress = ref(true);
const isLoadingShipping = ref(false);
const isCheckingOut = ref(false);

// 🎟️ Coupon State
const couponInput = ref("");
const couponData = ref<any>(null);
const isValidatingCoupon = ref(false);
const couponError = ref("");

onMounted(() => {
  if (checkoutStore.items.length === 0) {
    navigateTo("/cart");
    return;
  }
  fetchDefaultAddress();
  
  // Jika sudah ada promo dari keranjang, langsung pasang
  if (checkoutStore.promoCode) {
    couponInput.value = checkoutStore.promoCode;
    handleApplyCoupon();
  }
});

const fetchDefaultAddress = async () => {
  isLoadingAddress.value = true;
  try {
    const response: any = await $fetch(`${API_CEK}/shipping/address`, {
      method: "GET",
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    const addresses = response.data || [];
    defaultAddress.value =
      addresses.find((a: any) => a.is_default) || addresses[0] || null;

    if (defaultAddress.value) {
      await fetchShippingEstimate();
    }
  } catch (err) {
    console.error("Gagal mengambil alamat:", err);
  } finally {
    isLoadingAddress.value = false;
  }
};

const fetchShippingEstimate = async () => {
  isLoadingShipping.value = true;
  try {
    const representativeStockUuid = checkoutStore.items[0].stock_uuid;

    const response: any = await $fetch(`${API_TRANSAKSI}/shipping/estimate`, {
      method: "GET",
      query: {
        address_uuid: defaultAddress.value.uuid,
        stock_uuid: representativeStockUuid,
        quantity: checkoutStore.totalQuantity,
        weight: checkoutStore.totalWeight,
      },
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    shippingOptions.value = response.options || [];
    if (shippingOptions.value.length > 0) {
      selectedShipping.value = shippingOptions.value[0];
    }
  } catch (err) {
    console.error("Gagal memuat estimasi ongkir:", err);
    toast.add({
      title: "Ongkir Gagal",
      description: "Gagal memuat layanan pengiriman.",
      color: "red",
    });
  } finally {
    isLoadingShipping.value = false;
  }
};

const getStandardCourierCode = (rawName: string) => {
  const name = (rawName || "").toLowerCase();
  if (name.includes("jne")) return "jne";
  if (name.includes("j&t") || name.includes("jnt")) return "jnt";
  if (name.includes("sicepat")) return "sicepat";
  if (name.includes("pos")) return "pos";
  if (name.includes("tiki")) return "tiki";
  if (name.includes("wahana")) return "wahana";
  if (name.includes("anteraja")) return "anteraja";
  return "jne";
};

// 🎟️ Validate Coupon
const handleApplyCoupon = async () => {
  if (!couponInput.value) return;
  
  isValidatingCoupon.value = true;
  couponError.value = "";
  
  try {
    const res: any = await $fetch(`${config.public.apiBase}/stok/public/coupon/validate`, {
      method: "POST",
      body: {
        code: couponInput.value,
        cart_total: checkoutStore.subtotal
      }
    });
    
    if (res.success) {
      couponData.value = res.data;
      checkoutStore.setPromo(res.data.discount_amount, res.data.coupon_code);
      toast.add({ title: "Kupon Berhasil!", description: res.message, color: "green" });
    } else {
      couponError.value = res.message;
      couponData.value = null;
      checkoutStore.setPromo(0, "");
    }
  } catch (err: any) {
    couponError.value = err.data?.message || "Kupon tidak valid";
    couponData.value = null;
  } finally {
    isValidatingCoupon.value = false;
  }
};

const removeCoupon = () => {
  couponData.value = null;
  couponInput.value = "";
  checkoutStore.setPromo(0, "");
};

const handleCheckout = async () => {
  if (!defaultAddress.value) {
    alert("Silakan tambahkan alamat pengiriman terlebih dahulu.");
    return;
  }
  if (!selectedShipping.value) {
    alert("Silakan pilih layanan pengiriman.");
    return;
  }

  isCheckingOut.value = true;

  const payload = {
    items: checkoutStore.items.map((item) => ({
      stock_uuid: item.stock_uuid,
      quantity: item.quantity,
      addons: (item.options?.addons || [])
        .filter((a: any) => a.uuid || a.addon_uuid)
        .map((a: any) => ({
          addon_uuid: a.uuid || a.addon_uuid,
          quantity: a.quantity || 1
        }))
    })),
    address_uuid: defaultAddress.value.uuid,
    courier_name: getStandardCourierCode(selectedShipping.value.courier),
    courier_service: selectedShipping.value.service,
    coupon_code: checkoutStore.promoCode || null,
    payment_type: selectedPaymentMethod.value,
  };

  try {
    const response: any = await $fetch(`${API_TRANSAKSI}/checkout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${getToken()}` },
      body: payload,
    });

    checkoutStore.clearCheckoutData();

    if (response.order_id) {
      toast.add({ title: "Pesanan Dibuat", description: "Mengalihkan ke halaman pembayaran...", color: "green" });
      navigateTo(`/payment/${response.order_id}`);
    } else {
      navigateTo(`/dashboard/orders`);
    }
  } catch (err: any) {
    console.error("Checkout Error:", err);
    const errorMsg = err.data?.detail || "Terjadi kesalahan saat memproses pesanan.";
    alert(`Gagal Checkout: ${errorMsg}`);
  } finally {
    isCheckingOut.value = false;
  }
};

const formatRupiah = (angka: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  })
    .format(angka || 0)
    .replace("Rp", "Rp ");
};

// ✅ TAMBAHAN: Formatter Berat (Gram / Kg)
const formatWeight = (grams: number | undefined) => {
  if (!grams) return "0 gr";
  return grams >= 1000
    ? `${(grams / 1000).toFixed(2).replace(/\.00$/, "")} kg`
    : `${grams} gr`;
};

const shippingCost = computed(() => selectedShipping.value?.price || 0);
const finalGrandTotal = computed(() => checkoutStore.grandTotal + shippingCost.value);
</script>

<template>
  <main class="bg-[#F3F4F5] min-h-screen py-10 font-sans">
    <div class="max-w-[1100px] mx-auto px-4 md:px-6">
      <div class="mb-8 flex items-center gap-4">
        <button @click="$router.push('/cart')" class="text-gray-500 hover:text-black">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            ></path>
          </svg>
        </button>
        <h1 class="text-2xl font-black text-gray-900 tracking-tight">
          Pengiriman & Pembayaran
        </h1>
      </div>

      <div class="flex flex-col lg:flex-row gap-8 items-start">
        <div class="flex-1 min-w-0 space-y-6">
          <section
            class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <div
              class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50"
            >
              <h2 class="font-bold text-gray-900">Alamat Pengiriman</h2>
              <NuxtLink
                to="/dashboard/address"
                class="text-sm font-bold text-[#03AC0E] hover:text-[#028c0b] transition-colors"
              >
                Pilih Alamat Lain
              </NuxtLink>
            </div>

            <div class="p-6">
              <div
                v-if="isLoadingAddress"
                class="h-24 bg-gray-100 animate-pulse rounded-lg"
              ></div>

              <div v-else-if="!defaultAddress" class="text-center py-6">
                <p class="text-gray-500 mb-4">Anda belum memiliki alamat pengiriman.</p>
                <NuxtLink
                  to="/dashboard/address"
                  class="px-6 py-2 bg-[#03AC0E] text-white font-bold rounded-lg shadow-sm"
                >
                  Tambah Alamat
                </NuxtLink>
              </div>

              <div v-else class="flex gap-4">
                <UIcon
                  name="i-heroicons-map-pin"
                  class="w-6 h-6 text-[#03AC0E] mt-0.5 shrink-0"
                />
                <div>
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-bold text-gray-900">Rumah / Utama</span>
                    <span
                      class="px-2 py-0.5 bg-green-100 text-[#03AC0E] text-[10px] font-bold rounded-sm"
                      >Utama</span
                    >
                  </div>
                  <p class="text-gray-800 font-semibold text-sm mb-1">
                    {{ defaultAddress.label }}
                  </p>
                  <p class="text-gray-600 text-sm leading-relaxed">
                    {{ defaultAddress.full_address }}
                  </p>
                  <p class="text-gray-500 text-sm mt-1">
                    Kode Pos:
                    <span class="font-medium text-gray-800">{{
                      defaultAddress.zip_code
                    }}</span>
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section
            class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h2 class="font-bold text-gray-900">Pesanan Anda</h2>
            </div>
            <div class="p-6 space-y-5">
              <div
                v-for="item in checkoutStore.items"
                :key="item.stock_uuid"
                class="flex gap-4"
              >
                <div
                  class="w-20 h-20 shrink-0 bg-gray-50 rounded-lg border border-gray-100 overflow-hidden p-1"
                >
                  <NuxtImg
                    :src="item.image || 'https://via.placeholder.com/100'"
                    class="w-full h-full object-contain bg-white"
                  />
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-800 text-sm leading-snug">
                    {{ item.title }}
                  </h3>
                  <div class="flex items-center gap-2 mt-1">
                    <p class="text-xs text-gray-500 uppercase tracking-wider">
                      {{ item.brand || "NO BRAND" }}
                    </p>
                    <span
                      v-if="item.weight"
                      class="text-[10px] text-gray-400 bg-gray-100 border border-gray-200 px-1.5 py-0.5 rounded font-medium"
                      >{{ formatWeight(item.weight) }}</span
                    >
                  </div>
                    <p class="font-bold text-gray-900 mt-2">
                      {{ formatRupiah(item.price) }}
                      <span class="text-gray-500 font-normal text-xs ml-1"
                        >x {{ item.quantity }}</span
                      >
                    </p>

                    <!-- Addons Display -->
                    <div v-if="item.options?.addons?.length" class="mt-3 space-y-2 border-l-2 border-green-500 pl-3 py-0.5">
                      <div v-for="addon in item.options.addons" :key="addon.uuid" class="flex justify-between items-center text-[11px]">
                        <span class="text-gray-600 font-medium">↳ {{ addon.name }} (x{{ addon.quantity }})</span>
                        <span class="text-green-600 font-black">+ {{ formatRupiah(addon.price * addon.quantity) }}</span>
                      </div>
                    </div>
                  </div>
                <div class="text-right">
                  <p class="font-black text-gray-900">
                    {{ formatRupiah(item.price * item.quantity) }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section
            class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h2 class="font-bold text-gray-900">Pilih Pengiriman</h2>
            </div>

            <div class="p-6">
              <div
                v-if="!defaultAddress"
                class="text-sm text-red-500 font-semibold bg-red-50 p-4 rounded-lg"
              >
                Isi alamat terlebih dahulu untuk melihat opsi pengiriman.
              </div>

              <div v-else-if="isLoadingShipping" class="flex flex-col gap-3">
                <div
                  v-for="i in 3"
                  :key="i"
                  class="h-16 bg-gray-100 animate-pulse rounded-xl border border-gray-200"
                ></div>
              </div>

              <div
                v-else-if="shippingOptions.length === 0"
                class="text-sm text-orange-600 font-semibold bg-orange-50 p-4 rounded-lg border border-orange-100"
              >
                Tidak ada layanan pengiriman yang tersedia untuk alamat ini.
              </div>

              <div v-else class="grid grid-cols-1 gap-3">
                <label
                  v-for="(option, index) in shippingOptions"
                  :key="index"
                  class="flex items-start gap-4 p-4 border rounded-xl cursor-pointer transition-all"
                  :class="
                    selectedShipping?.service === option.service &&
                    selectedShipping?.courier === option.courier
                      ? 'border-[#03AC0E] bg-green-50/20 shadow-[0_0_0_1px_#03AC0E]'
                      : 'border-gray-200 hover:border-green-300'
                  "
                >
                  <div class="flex items-center h-5 mt-0.5">
                    <input
                      type="radio"
                      name="shipping"
                      :value="option"
                      v-model="selectedShipping"
                      class="w-4 h-4 text-[#03AC0E] border-gray-300 focus:ring-[#03AC0E]"
                    />
                  </div>
                  <div class="flex-1">
                    <div class="flex justify-between items-start">
                      <div>
                        <p class="font-bold text-gray-900">
                          {{ option.courier }} -
                          <span class="text-[#03AC0E]">{{ option.service }}</span>
                        </p>
                        <p class="text-xs text-gray-500 mt-1">
                          Estimasi tiba:
                          <span class="font-semibold text-gray-700">{{
                            option.etd || "Mengikuti jadwal kurir"
                          }}</span>
                        </p>
                      </div>
                      <span class="font-black text-gray-900">{{
                        formatRupiah(option.price)
                      }}</span>
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </section>

          <!-- 💳 Section Pembayaran -->
          <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h2 class="font-bold text-gray-900">Pilih Metode Pembayaran</h2>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <label class="flex items-center gap-4 p-4 border rounded-xl cursor-pointer transition-all hover:border-[#03AC0E]"
                  :class="selectedPaymentMethod === 'gopay' ? 'border-[#03AC0E] bg-green-50/20 shadow-[0_0_0_1px_#03AC0E]' : 'border-gray-200'">
                  <input type="radio" v-model="selectedPaymentMethod" value="gopay" class="w-4 h-4 text-[#03AC0E] border-gray-300 focus:ring-[#03AC0E]" />
                  <div class="flex-1 flex justify-between items-center">
                    <span class="font-bold text-gray-900 text-sm">GoPay</span>
                    <img src="https://upload.wikimedia.org/wikipedia/commons/8/86/Gopay_logo.svg" class="h-4" alt="GoPay" />
                  </div>
                </label>

                <label class="flex items-center gap-4 p-4 border rounded-xl cursor-pointer transition-all hover:border-[#03AC0E]"
                  :class="selectedPaymentMethod === 'qris' ? 'border-[#03AC0E] bg-green-50/20 shadow-[0_0_0_1px_#03AC0E]' : 'border-gray-200'">
                  <input type="radio" v-model="selectedPaymentMethod" value="qris" class="w-4 h-4 text-[#03AC0E] border-gray-300 focus:ring-[#03AC0E]" />
                  <div class="flex-1 flex justify-between items-center">
                    <span class="font-bold text-gray-900 text-sm">QRIS</span>
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a2/Logo_QRIS.svg" class="h-4" alt="QRIS" />
                  </div>
                </label>

                <label class="flex items-center gap-4 p-4 border rounded-xl cursor-pointer transition-all hover:border-[#03AC0E]"
                  :class="selectedPaymentMethod === 'bca_va' ? 'border-[#03AC0E] bg-green-50/20 shadow-[0_0_0_1px_#03AC0E]' : 'border-gray-200'">
                  <input type="radio" v-model="selectedPaymentMethod" value="bca_va" class="w-4 h-4 text-[#03AC0E] border-gray-300 focus:ring-[#03AC0E]" />
                  <div class="flex-1 flex justify-between items-center">
                    <span class="font-bold text-gray-900 text-sm">BCA Virtual Account</span>
                  </div>
                </label>

                <label class="flex items-center gap-4 p-4 border rounded-xl cursor-pointer transition-all hover:border-[#03AC0E]"
                  :class="selectedPaymentMethod === 'mandiri_va' ? 'border-[#03AC0E] bg-green-50/20 shadow-[0_0_0_1px_#03AC0E]' : 'border-gray-200'">
                  <input type="radio" v-model="selectedPaymentMethod" value="mandiri_va" class="w-4 h-4 text-[#03AC0E] border-gray-300 focus:ring-[#03AC0E]" />
                  <div class="flex-1 flex justify-between items-center">
                    <span class="font-bold text-gray-900 text-sm">Mandiri Virtual Account</span>
                  </div>
                </label>
              </div>
            </div>
          </section>

          <!-- 🎟️ Section Kupon -->
          <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden p-6 relative group">
            <div class="absolute top-0 right-0 w-24 h-24 bg-indigo-50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
            
            <div class="relative">
              <h2 class="font-bold text-gray-900 mb-5 flex items-center gap-2">
                <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-indigo-200">
                  <UIcon name="i-heroicons-ticket" class="w-5 h-5" />
                </div>
                Gunakan Kupon Promo
              </h2>
              
              <div v-if="!couponData" class="flex gap-2">
                <input 
                  v-model="couponInput" 
                  type="text" 
                  placeholder="MASUKKAN KODE KUPON" 
                  class="flex-1 px-4 py-3 bg-gray-50 border-2 border-gray-100 rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none uppercase font-mono text-sm font-bold transition-all placeholder:normal-case placeholder:font-normal"
                  @keyup.enter="handleApplyCoupon"
                />
                <button 
                  @click="handleApplyCoupon"
                  :disabled="isValidatingCoupon || !couponInput"
                  class="px-6 py-3 bg-black text-white font-black rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-all text-xs uppercase tracking-widest active:scale-95 shadow-md"
                >
                  {{ isValidatingCoupon ? 'Cek...' : 'Cek' }}
                </button>
              </div>

              <div v-else class="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-600 to-indigo-800 rounded-2xl shadow-lg shadow-indigo-200 border-2 border-indigo-400/20">
                <div class="flex items-center gap-4">
                  <div class="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center text-white border border-white/30">
                    <UIcon name="i-heroicons-sparkles" class="w-6 h-6 animate-pulse" />
                  </div>
                  <div>
                    <p class="text-[10px] font-black text-indigo-100 uppercase tracking-[0.2em] mb-0.5">KUPON TERPASANG</p>
                    <div class="flex items-baseline gap-2">
                      <span class="text-lg font-black text-white uppercase tracking-wider font-mono">{{ couponData.coupon_code }}</span>
                      <span class="text-xs font-bold text-indigo-200 bg-white/10 px-2 py-0.5 rounded">-{{ formatRupiah(couponData.discount_amount) }}</span>
                    </div>
                  </div>
                </div>
                <button @click="removeCoupon" class="bg-white/10 hover:bg-white/20 text-white p-2 rounded-xl border border-white/20 transition-all active:scale-90">
                  <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
                </button>
              </div>
              
              <div v-if="couponError" class="mt-3 flex items-center gap-2 text-[11px] text-red-500 font-bold bg-red-50 p-2.5 rounded-lg border border-red-100">
                <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4" />
                {{ couponError }}
              </div>
            </div>
          </section>
        </div>

        <div class="w-full lg:w-[380px] shrink-0">
          <div
            class="sticky top-24 bg-white rounded-2xl p-6 shadow-md border border-gray-200"
          >
            <h3 class="font-bold text-gray-900 mb-6 pb-4 border-b border-gray-100">
              Ringkasan Belanja
            </h3>

            <div class="space-y-3 text-sm mb-6">
              <div class="flex justify-between text-gray-600">
                <span>Total Harga ({{ checkoutStore.totalQuantity }} barang)</span>
                <span class="font-semibold text-gray-900">{{ formatRupiah(checkoutStore.subtotal) }}</span>
              </div>

              <div class="flex justify-between text-gray-600">
                <span>Total Ongkos Kirim</span>
                <span class="font-semibold text-gray-900">{{ formatRupiah(shippingCost) }}</span>
              </div>

              <div v-if="checkoutStore.discountPromo > 0" class="flex justify-between text-indigo-600 bg-indigo-50 p-2.5 rounded-xl border border-indigo-100">
                <div class="flex items-center gap-1.5">
                   <UIcon name="i-heroicons-ticket" class="w-4 h-4" />
                   <span class="font-bold uppercase text-[10px] tracking-wider">{{ checkoutStore.promoCode }}</span>
                </div>
                <span class="font-black">- {{ formatRupiah(checkoutStore.discountPromo) }}</span>
              </div>
            </div>

            <div class="pt-4 border-t border-gray-200 mb-6 flex justify-between items-end">
              <span class="font-bold text-gray-900 text-base">Total Tagihan</span>
              <span class="text-xl font-black text-indigo-600 leading-none">
                {{ formatRupiah(finalGrandTotal) }}
              </span>
            </div>

            <button
              @click="handleCheckout"
              :disabled="isCheckingOut || !selectedShipping || !defaultAddress"
              class="w-full bg-[#03AC0E] text-white font-bold py-3.5 rounded-xl text-sm transition-all hover:bg-[#028c0b] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <svg
                v-if="isCheckingOut"
                class="animate-spin h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span v-else>Lanjut ke Pembayaran</span>
            </button>

            <p class="text-[10px] text-gray-400 mt-4 text-center">
              Dengan membuat pesanan, Anda menyetujui Syarat & Ketentuan yang berlaku.
            </p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
