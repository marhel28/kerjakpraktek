<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, watch } from "vue";

definePageMeta({ layout: "public" });

const route = useRoute();
const orderId = route.params.id as string;
const config = useRuntimeConfig();
const API_BASE = `${config.public.apiBase}/transaksi`;
const getToken = () => useCookie("token").value;

const order = ref<any>(null);
const isLoading = ref(true);
let pollingInterval: any = null;

const toast = useToast();

const fetchOrderDetail = async () => {
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

// Countdown Timer
const countdownText = ref("00:00:00");
let countdownTimer: any = null;

const startCountdown = () => {
  if (countdownTimer) clearInterval(countdownTimer);
  if (!order.value?.created_at) return;
  
  const createdAt = new Date(order.value.created_at).getTime();
  const expiryTime = createdAt + 24 * 60 * 60 * 1000; // 24 hours expiry
  
  const updateTimer = () => {
    const now = new Date().getTime();
    const diff = expiryTime - now;
    
    if (diff <= 0) {
      countdownText.value = "EXPIRED";
      clearInterval(countdownTimer);
      fetchOrderDetail();
      return;
    }
    
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    countdownText.value = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };
  
  updateTimer();
  countdownTimer = setInterval(updateTimer, 1000);
};

onMounted(() => {
  fetchOrderDetail();
  pollingInterval = setInterval(() => {
    if (isPending.value) {
      fetchOrderDetail();
    }
  }, 5000);
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
  if (countdownTimer) clearInterval(countdownTimer);
});

const formatRupiah = (angka: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  }).format(angka || 0).replace("Rp", "Rp ");
};

const isPending = computed(() => {
  return order.value?.transaction_status?.toLowerCase() === "pending";
});

const isPaid = computed(() => {
  const status = order.value?.transaction_status?.toLowerCase();
  return ["settlement", "success", "capture"].includes(status || "");
});

const isCancelled = computed(() => {
  const status = order.value?.transaction_status?.toLowerCase();
  return ["cancel", "expire", "deny", "failure"].includes(status || "");
});

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text);
  toast.add({
    title: 'Disalin ke Clipboard',
    description: 'Teks berhasil disalin.',
    icon: 'i-heroicons-check-circle',
    color: 'green'
  });
};

const isPaymentEmbedded = ref(false);
const snapToken = computed(() => order.value?.snap_token || order.value?.raw_response?.token);

const openSnapEmbed = () => {
  const token = snapToken.value;
  if (!token) return;

  const snapObj = (window as any).snap;
  if (!snapObj) {
    console.error("Midtrans snap script not loaded");
    return;
  }

  isPaymentEmbedded.value = true;

  setTimeout(() => {
    snapObj.embed(token, {
      embedId: 'snap-container',
      onSuccess: () => {
        isPaymentEmbedded.value = false;
        fetchOrderDetail();
      },
      onPending: () => {
        isPaymentEmbedded.value = false;
        fetchOrderDetail();
      },
      onError: () => {
        toast.add({
          title: 'Pembayaran Gagal',
          description: 'Ada kendala saat memproses transaksi.',
          icon: 'i-heroicons-x-circle',
          color: 'red'
        });
      },
      onClose: () => {
        isPaymentEmbedded.value = false;
      }
    });
  }, 100);
};

// Auto-open embed if pending
watch(() => isPending.value, (newVal) => {
  if (newVal && snapToken.value && !isPaymentEmbedded.value) {
    openSnapEmbed();
  }
}, { immediate: true });

watch(() => snapToken.value, (newVal) => {
  if (newVal && isPending.value && !isPaymentEmbedded.value) {
    openSnapEmbed();
  }
}, { immediate: true });

watch(() => order.value, (newVal) => {
  if (newVal && isPending.value) {
    startCountdown();
  } else {
    if (countdownTimer) {
      clearInterval(countdownTimer);
      countdownTimer = null;
    }
  }
}, { immediate: true });
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8 font-sans">
    <div class="max-w-[1100px] mx-auto">
      
      <!-- Top Title Area -->
      <div class="flex items-center gap-3 mb-8">
        <NuxtLink to="/" class="hover:opacity-85 transition-opacity">
          <img src="/pasarcctv.png" alt="PasarCctv" class="h-10 w-auto object-contain" />
        </NuxtLink>
        <span class="w-1.5 h-1.5 rounded-full bg-gray-300"></span>
        <span class="text-sm font-bold text-gray-500 uppercase tracking-widest">Pembayaran</span>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="bg-white rounded-2xl shadow-sm border border-gray-150 p-16 flex flex-col items-center justify-center min-h-[400px]">
        <Icon name="lucide:loader-2" class="w-12 h-12 text-[#03AC0E] animate-spin mb-4" />
        <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Memuat Rincian Transaksi...</p>
      </div>

      <!-- Main Layout -->
      <div v-else-if="order" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Left: Payment Frame & Instructions (2 columns on lg) -->
        <div class="lg:col-span-2 space-y-6">
          
          <!-- Status Banner -->
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8 flex flex-col sm:flex-row items-center gap-6">
            <div
              class="w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0"
              :class="[
                isPaid ? 'bg-green-50 text-green-600 border border-green-200' :
                isPending ? 'bg-amber-50 text-amber-600 border border-amber-200 animate-pulse' :
                'bg-red-50 text-red-500 border border-red-200'
              ]"
            >
              <Icon :name="isPaid ? 'lucide:check-circle-2' : isPending ? 'lucide:clock' : 'lucide:alert-circle'" class="w-8 h-8" />
            </div>

            <div class="flex-1 text-center sm:text-left min-w-0">
              <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2.5 mb-1.5">
                <h2 class="text-xl font-black text-gray-900 tracking-tight">
                  {{ isPaid ? "Pembayaran Sukses!" : isPending ? "Menunggu Pembayaran" : "Transaksi Dibatalkan" }}
                </h2>
                <span
                  class="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded border"
                  :class="[
                    isPaid ? 'bg-green-50 border-green-200 text-green-700' :
                    isPending ? 'bg-amber-50 border-amber-200 text-amber-700' :
                    'bg-red-50 border-red-200 text-red-700'
                  ]"
                >
                  {{ order.transaction_status }}
                </span>
              </div>
              <p class="text-xs text-gray-400">Order ID: <span class="font-mono font-bold text-gray-800">{{ order.order_id }}</span></p>
            </div>

            <!-- Expiry countdown for pending transactions -->
            <div v-if="isPending" class="text-center bg-amber-50/70 border border-amber-100 rounded-xl px-5 py-3 shrink-0">
              <p class="text-[9px] font-black text-amber-600 uppercase tracking-widest leading-none mb-1">Sisa Batas Waktu</p>
              <p class="text-lg font-mono font-black text-amber-700 leading-none">{{ countdownText }}</p>
            </div>
          </div>

          <!-- Midtrans Embed Container -->
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div class="px-6 py-4.5 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
              <div class="flex items-center gap-2">
                <Icon name="lucide:credit-card" class="w-5 h-5 text-[#03AC0E]" />
                <span class="text-xs font-black text-gray-900 uppercase tracking-widest">Pintu Gerbang Pembayaran</span>
              </div>
              <div class="flex items-center gap-1.5 opacity-60">
                <Icon name="lucide:shield-check" class="w-4 h-4 text-green-600" />
                <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Enkripsi 3D-Secure</span>
              </div>
            </div>

            <div class="p-6">
              <div v-if="isPending" class="space-y-6">
                <!-- Snap frame element -->
                <div v-show="isPaymentEmbedded" class="w-full bg-white rounded-xl overflow-hidden border border-gray-150">
                  <div id="snap-container" class="w-full min-h-[600px]"></div>
                </div>

                <!-- Fallback Button if embed closed or failed -->
                <div v-if="!isPaymentEmbedded && snapToken" class="text-center py-10">
                  <button
                    @click="openSnapEmbed"
                    class="px-8 py-3.5 bg-[#03AC0E] hover:bg-[#028c0b] text-white text-xs font-black uppercase tracking-widest rounded-xl transition-all shadow-md active:scale-95 flex items-center gap-2 mx-auto"
                  >
                    <Icon name="lucide:wallet" class="w-4 h-4" />
                    Tampilkan Pilihan Pembayaran
                  </button>
                </div>

                <div v-if="!isPaymentEmbedded && !snapToken" class="text-center py-12 text-gray-400 text-xs font-bold uppercase tracking-widest flex flex-col items-center gap-3">
                  <Icon name="lucide:loader-2" class="w-6 h-6 animate-spin text-gray-300" />
                  Menginisialisasi Pembayaran...
                </div>
              </div>

              <!-- Post-payment screens -->
              <div v-else class="text-center py-12 max-w-sm mx-auto space-y-6">
                <p class="text-xs text-gray-500 font-medium leading-relaxed">
                  {{ isPaid ? "Terima kasih telah berbelanja di PasarCctv! Pembayaran Anda telah kami verifikasi secara otomatis. Kami akan segera memproses pengiriman pesanan Anda." : "Transaksi ini telah dibatalkan atau kedaluwarsa. Silakan lakukan checkout ulang jika Anda masih ingin membeli produk ini." }}
                </p>
                <div class="flex flex-col sm:flex-row gap-3">
                  <NuxtLink
                    :to="`/dashboard/orders/${order.order_id}`"
                    class="flex-1 text-center py-3 bg-gray-900 text-white text-xs font-black uppercase tracking-widest rounded-xl transition hover:bg-gray-800"
                  >
                    Detail Transaksi
                  </NuxtLink>
                  <NuxtLink
                    to="/"
                    class="flex-1 text-center py-3 border border-gray-200 text-gray-700 text-xs font-black uppercase tracking-widest rounded-xl transition hover:bg-gray-50"
                  >
                    Ke Beranda
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>

          <!-- Partners Section -->
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-2">
              <Icon name="lucide:help-circle" class="w-4 h-4 text-gray-400" />
              <span class="text-xs text-gray-500 font-medium">Butuh bantuan pembayaran?</span>
              <NuxtLink to="/help" class="text-xs font-bold text-[#03AC0E] hover:underline">Hubungi CS</NuxtLink>
            </div>
            <div class="flex items-center gap-4 opacity-50 grayscale shrink-0">
              <img src="https://upload.wikimedia.org/wikipedia/commons/e/e1/Midtrans_Logo.png" alt="Midtrans" class="h-5 object-contain" />
              <img src="https://upload.wikimedia.org/wikipedia/commons/5/5e/Visa_Inc._logo.svg" alt="Visa" class="h-3 object-contain" />
              <img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg" alt="Mastercard" class="h-5 object-contain" />
            </div>
          </div>
        </div>

        <!-- Right: Invoice Details & Items Summary -->
        <div class="space-y-6">
          
          <!-- Summary Card -->
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm sticky top-8 overflow-hidden divide-y divide-gray-100">
            
            <!-- Section 1: Billing Total -->
            <div class="p-6">
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1">Total Tagihan</span>
              <div class="flex items-baseline justify-between gap-4">
                <span class="text-2xl font-black text-[#03AC0E] tracking-tight">
                  {{ formatRupiah(order.gross_amount || 0) }}
                </span>
                <button
                  @click="copyToClipboard(String(order.gross_amount))"
                  class="text-[10px] font-bold text-[#03AC0E] bg-[#D6FFDE]/40 border border-[#03AC0E]/20 px-2.5 py-1 rounded-lg hover:bg-[#D6FFDE]/70 transition active:scale-95"
                >
                  Salin Jumlah
                </button>
              </div>
            </div>

            <!-- Section 2: Items List -->
            <div class="p-6">
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-3">Item Pesanan</span>
              <div class="space-y-4 max-h-[220px] overflow-y-auto custom-scrollbar pr-1">
                <div v-for="item in order.items" :key="item.item_uuid" class="flex gap-3">
                  <!-- Image -->
                  <div class="w-12 h-12 rounded-lg bg-gray-50 border border-gray-150 overflow-hidden flex-shrink-0 flex items-center justify-center p-1">
                    <img
                      v-if="item.cover_image_url"
                      :src="item.cover_image_url"
                      :alt="item.item_name"
                      class="w-full h-full object-contain mix-blend-multiply"
                    />
                    <Icon v-else name="lucide:camera" class="w-5 h-5 text-gray-300" />
                  </div>

                  <!-- Details -->
                  <div class="flex-1 min-w-0">
                    <span class="text-[9px] font-black text-[#03AC0E] uppercase tracking-wider block mb-0.5" v-if="item.brand">
                      {{ item.brand }}
                    </span>
                    <p class="text-xs font-bold text-gray-900 leading-tight truncate">
                      {{ item.item_name }}
                    </p>
                    <p class="text-[11px] font-bold text-gray-500 mt-1">
                      {{ item.quantity }}x <span class="font-normal text-gray-400">@</span> {{ formatRupiah(item.unit_price) }}
                    </p>

                    <!-- Addons snapshot list -->
                    <div v-if="item.addons && item.addons.length" class="mt-1.5 space-y-0.5 border-l border-gray-200 pl-2">
                      <p v-for="ad in item.addons" :key="ad.uuid" class="text-[10px] font-medium text-gray-400 flex items-center gap-1.5">
                        <span class="w-1 h-1 rounded-full bg-[#03AC0E]/60"></span>
                        <span>{{ ad.name }} ({{ ad.quantity }}x)</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 3: Billing Breakdown -->
            <div class="p-6 space-y-3">
              <div class="flex justify-between items-center text-xs">
                <span class="text-gray-500 font-medium">Subtotal Barang</span>
                <span class="font-bold text-gray-900">{{ formatRupiah(order.items_subtotal || 0) }}</span>
              </div>
              <div class="flex justify-between items-center text-xs" v-if="order.shipping_cost > 0">
                <span class="text-gray-500 font-medium">Ongkos Kirim</span>
                <span class="font-bold text-gray-900">{{ formatRupiah(order.shipping_cost || 0) }}</span>
              </div>
              <div class="flex justify-between items-center text-xs" v-if="order.service_cost > 0">
                <span class="text-gray-500 font-medium">Biaya Jasa / Transport</span>
                <span class="font-bold text-gray-900">{{ formatRupiah(order.service_cost || 0) }}</span>
              </div>
              <div class="flex justify-between items-center text-xs text-green-600 bg-green-50/50 p-2 rounded-lg border border-green-100" v-if="order.total_discount > 0">
                <span class="font-medium">Diskon Promo</span>
                <span class="font-black">-{{ formatRupiah(order.total_discount) }}</span>
              </div>
            </div>

            <!-- Section 4: Shipping Info -->
            <div class="p-6 bg-gray-50/50" v-if="order.shipment">
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-2">Tujuan Pengiriman</span>
              <p class="text-xs font-bold text-gray-900">{{ order.shipment.recipient_name }}</p>
              <p class="text-[11px] font-semibold text-gray-500 mt-0.5">{{ order.shipment.recipient_phone }}</p>
              <p class="text-[11px] text-gray-400 mt-1 leading-relaxed line-clamp-3">
                {{ order.shipment.shipping_address }}
              </p>
              <div class="mt-3 flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-150 rounded-xl w-fit">
                <Icon name="lucide:truck" class="w-4 h-4 text-gray-400" />
                <span class="text-[10px] font-black text-gray-600 uppercase tracking-wider">
                  {{ order.shipment.courier_name }} ({{ order.shipment.courier_service }})
                </span>
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- Not Found Screen -->
      <div v-else class="bg-white rounded-2xl border border-gray-200 p-16 text-center max-w-md mx-auto space-y-6">
        <div class="w-16 h-16 bg-red-50 text-red-500 border border-red-100 rounded-full flex items-center justify-center mx-auto">
          <Icon name="lucide:search-code" class="w-8 h-8" />
        </div>
        <div class="space-y-2">
          <h3 class="text-lg font-black text-gray-900">Tagihan Tidak Ditemukan</h3>
          <p class="text-xs text-gray-500 leading-relaxed">
            Maaf, kami tidak dapat menemukan invoice dengan ID tersebut. Hubungi tim support jika Anda merasa ini adalah kesalahan.
          </p>
        </div>
        <NuxtLink
          to="/dashboard/orders"
          class="block w-full text-center py-3 bg-[#03AC0E] hover:bg-[#028c0b] text-white text-xs font-black uppercase tracking-widest rounded-xl transition shadow-md"
        >
          Lihat Daftar Transaksi
        </NuxtLink>
      </div>

    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: #94a3b8;
}
</style>