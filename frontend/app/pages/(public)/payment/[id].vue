<script setup lang="ts">
import { ref, onMounted, computed } from "vue";

// Kita gunakan layout blank/public agar fokus ke pembayaran (tanpa sidebar)
definePageMeta({ layout: "public" });

// ----------------------------------------------------
// 💉 INJECT MIDTRANS SNAP SCRIPT
// ----------------------------------------------------
useHead({
  script: [
    {
      // Gunakan URL Sandbox untuk testing (Ganti 'app.midtrans.com' untuk Production)
      src: "https://app.sandbox.midtrans.com/snap/snap.js",
      // WAJIB GANTI dengan Client Key Midtrans Anda
      "data-client-key": "SB-Mid-client-pn3mYe4w4xeY6F0w",
      async: true,
    },
  ],
});

const route = useRoute();
const orderId = route.params.id as string;
const config = useRuntimeConfig();
const API_BASE = `${config.public.apiBase}/transaksi`;
const getToken = () => useCookie("token").value;

const order = ref<any>(null);
const isLoading = ref(true);
const isPaymentLoading = ref(false);

// ----------------------------------------------------
// 1. FETCH DETAIL ORDER
// ----------------------------------------------------
const fetchOrderDetail = async () => {
  isLoading.value = true;
  try {
    const response: any = await $fetch(`${API_BASE}/detail/${orderId}`, {
      method: "GET",
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    order.value = response.data || response;
  } catch (err) {
    console.error("Gagal mengambil detail transaksi:", err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchOrderDetail();
});

// ----------------------------------------------------
// 2. FORMATTER & UTILITIES
// ----------------------------------------------------
const formatRupiah = (angka: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  }).format(angka || 0);
};

const isPending = computed(() => {
  return order.value?.transaction_status?.toLowerCase() === "pending";
});

const isPaid = computed(() => {
  const status = order.value?.transaction_status?.toLowerCase();
  return ["settlement", "success", "capture"].includes(status || "");
});

// ----------------------------------------------------
// 3. HANDLER PEMBAYARAN MIDTRANS (POPUP SNAP)
// ----------------------------------------------------
const payOrder = () => {
  isPaymentLoading.value = true;
  const snapToken = order.value?.raw_response?.token;

  if (snapToken && (window as any).snap) {
    (window as any).snap.pay(snapToken, {
      onSuccess: function (result: any) {
        // Jika sukses, fetch ulang untuk update UI, atau redirect ke halaman detail
        fetchOrderDetail();
      },
      onPending: function (result: any) {
        alert("Pembayaran Anda sedang diproses.");
        fetchOrderDetail();
      },
      onError: function (result: any) {
        alert("Pembayaran gagal. Silakan coba lagi.");
        isPaymentLoading.value = false;
      },
      onClose: function () {
        console.log("Popup ditutup oleh user");
        isPaymentLoading.value = false;
      },
    });
  } else {
    alert("Sistem pembayaran sedang dimuat. Mohon tunggu beberapa saat.");
    isPaymentLoading.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-[#f3f4f5] flex items-center justify-center py-10 px-4">
    <div
      class="w-full max-w-lg bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden"
    >
      <div v-if="isLoading" class="p-8 space-y-6">
        <div class="h-8 bg-gray-200 rounded w-1/2 mx-auto animate-pulse"></div>
        <div class="h-32 bg-gray-100 rounded animate-pulse"></div>
        <div class="h-12 bg-gray-200 rounded animate-pulse"></div>
      </div>

      <div v-else-if="order" class="p-8">
        <div class="text-center mb-8">
          <div
            v-if="isPaid"
            class="w-20 h-20 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4"
          >
            <svg
              class="w-10 h-10 text-[#03AC0E]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="3"
                d="M5 13l4 4L19 7"
              ></path>
            </svg>
          </div>
          <div
            v-else-if="isPending"
            class="w-20 h-20 mx-auto bg-orange-100 rounded-full flex items-center justify-center mb-4"
          >
            <svg
              class="w-10 h-10 text-orange-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
          </div>
          <div
            v-else
            class="w-20 h-20 mx-auto bg-red-100 rounded-full flex items-center justify-center mb-4"
          >
            <svg
              class="w-10 h-10 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </div>

          <h1 class="text-2xl font-black text-gray-900">
            {{
              isPaid
                ? "Pembayaran Berhasil!"
                : isPending
                ? "Menunggu Pembayaran"
                : "Pesanan Dibatalkan"
            }}
          </h1>
          <p class="text-gray-500 mt-2 text-sm">
            No. Tagihan: <span class="font-bold text-gray-800">{{ order.order_id }}</span>
          </p>
        </div>

        <div class="bg-gray-50 rounded-xl p-5 border border-gray-100 mb-8 space-y-3">
          <div class="flex justify-between items-center text-sm">
            <span class="text-gray-500">Total Harga Barang</span>
            <span class="font-semibold text-gray-900">{{
              formatRupiah(order.items_subtotal)
            }}</span>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="text-gray-500">Ongkos Kirim</span>
            <span class="font-semibold text-gray-900">{{
              formatRupiah(order.shipping_cost)
            }}</span>
          </div>
          <div
            v-if="order.discount_amount > 0"
            class="flex justify-between items-center text-sm text-[#03AC0E]"
          >
            <span>Total Diskon</span>
            <span class="font-bold">- {{ formatRupiah(order.discount_amount) }}</span>
          </div>

          <hr class="border-gray-200 my-2" />

          <div class="flex justify-between items-center">
            <span class="text-gray-900 font-bold">Total Pembayaran</span>
            <span class="text-xl font-black text-red-600">{{
              formatRupiah(order.gross_amount)
            }}</span>
          </div>
        </div>

        <div class="space-y-3">
          <button
            v-if="isPending"
            @click="payOrder"
            :disabled="isPaymentLoading"
            class="w-full bg-[#03AC0E] text-white font-bold py-3.5 rounded-xl transition-colors hover:bg-[#028c0b] shadow-md flex justify-center items-center gap-2"
          >
            <svg
              v-if="isPaymentLoading"
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
            <span v-else>Bayar Sekarang</span>
          </button>

          <NuxtLink
            :to="`/dashboard/orders/${order.order_id}`"
            class="block w-full text-center py-3.5 bg-white border border-gray-300 text-gray-700 font-bold rounded-xl hover:bg-gray-50 transition-colors"
          >
            Lihat Detail Pesanan
          </NuxtLink>
        </div>
      </div>

      <div v-else class="p-8 text-center">
        <h3 class="text-xl font-bold text-gray-900 mb-2">Tagihan tidak ditemukan</h3>
        <p class="text-gray-500 mb-6 text-sm">
          Pastikan link URL benar atau transaksi ini milik akun Anda.
        </p>
        <NuxtLink
          to="/dashboard/orders"
          class="px-6 py-3 bg-[#03AC0E] text-white font-bold rounded-xl inline-block"
        >
          Ke Daftar Transaksi
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
