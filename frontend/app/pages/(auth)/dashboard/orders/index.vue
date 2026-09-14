<script setup lang="ts">
import { ref, watch, onMounted } from "vue";

definePageMeta({ layout: "auth" });
const config = useRuntimeConfig();
const API_BASE = `${config.public.apiBase}/transaksi`;
const getToken = () => useCookie("token").value;

// ─── State ───────────────────────────────────────────────
const transactions = ref<any[]>([]);
const isLoading = ref(true);
const activeTab = ref("semua");
const page = ref(1);
const limit = ref(10);
const totalPage = ref(1);
const total = ref(0);


const statusTabs = [
  { id: "semua", label: "Semua" },
  { id: "pending_payment", label: "Belum Bayar" },
  { id: "settlement", label: "Berhasil" },
  { id: "expire", label: "Dibatalkan" },
];

const fetchTransactions = async () => {
  isLoading.value = true;
  try {
    const queryParams: Record<string, any> = { 
      page: page.value, 
      limit: limit.value, 
      sort: "desc" 
    };
    
    if (activeTab.value !== "semua") {
      queryParams.status = activeTab.value;
    }

    const response: any = await $fetch(`${API_BASE}/my/all`, {
      method: "GET",
      query: queryParams,
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    if (response.success) {
      transactions.value = response.data || [];
      totalPage.value = response.meta?.total_page || 1;
      total.value = response.meta?.total || 0;
    }
  } catch (err: any) {
    console.error("Gagal memuat pesanan:", err);
    transactions.value = [];
  } finally {
    isLoading.value = false;
  }
};

watch([activeTab], () => { 
  page.value = 1; 
  fetchTransactions(); 
});

const formatRupiah = (angka: number) =>
  new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(angka || 0);

const formatDate = (dateString: string) => {
  if (!dateString) return "-";
  return new Intl.DateTimeFormat("id-ID", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(dateString));
};

const getStatusConfig = (trx: any) => {
  const tStatus = (trx.transaction_status || "").toLowerCase();
  const sStatus = (trx.shipment?.delivery_status || "").toLowerCase();
  const hasWaybill = !!trx.shipment?.waybill_number;

  if (["expire", "cancel", "deny"].includes(tStatus)) return { text: "Dibatalkan", color: "bg-red-50 text-red-600 border-red-100" };
  if (["pending", "pending_payment"].includes(tStatus)) return { text: "Menunggu Pembayaran", color: "bg-amber-50 text-amber-600 border-amber-100" };
  
  if (["settlement", "success", "capture"].includes(tStatus)) {
    if (["delivered", "completed"].includes(sStatus)) return { text: "Selesai", color: "bg-emerald-50 text-emerald-600 border-emerald-100" };
    if (sStatus === "shipped" || hasWaybill) return { text: "Dikirim", color: "bg-blue-50 text-blue-600 border-blue-100" };
    return { text: "Diproses", color: "bg-green-50 text-green-600 border-green-100" };
  }
  return { text: trx.transaction_status || "Proses", color: "bg-gray-50 text-gray-500 border-gray-100" };
};

const confirmModal = ref({
  show: false,
  orderId: "",
  loading: false,
});

const successModal = ref({
  show: false,
  orderId: "",
});

const confirmDelivery = (orderId: string) => {
  confirmModal.value = {
    show: true,
    orderId: orderId,
    loading: false,
  };
};

const executeConfirmDelivery = async () => {
  const orderId = confirmModal.value.orderId;
  confirmModal.value.loading = true;
  try {
    const response: any = await $fetch(`${config.public.apiBase}/transaksi/confirm-delivery/${orderId}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (response.success) {
      confirmModal.value.show = false;
      successModal.value = {
        show: true,
        orderId: orderId,
      };
    } else {
      alert(response.message || "Gagal mengonfirmasi penerimaan barang.");
    }
  } catch (err: any) {
    alert(err?.data?.detail || "Gagal mengonfirmasi penerimaan barang.");
  } finally {
    confirmModal.value.loading = false;
  }
};

const closeSuccessModal = () => {
  successModal.value.show = false;
  fetchTransactions();
};

onMounted(() => {
  fetchTransactions();
});
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- MOBILE HEADER -->
    <div class="lg:hidden flex items-center gap-4 px-6 py-4 border-b border-gray-100 bg-white sticky top-0 z-10">
      <button @click="$router.push('/dashboard')" class="p-1 -ml-1 text-gray-400 hover:text-gray-900 transition-colors">
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </button>
      <h1 class="text-base font-black text-gray-900 uppercase tracking-wider">Pesanan Saya</h1>
    </div>

    <!-- DESKTOP HEADER (Tokopedia Style) -->
    <div class="hidden lg:block px-8 py-5 border-b border-gray-200/80 bg-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-lg font-bold text-gray-900">Daftar Transaksi</h1>
          <p class="text-xs text-gray-500 mt-0.5">Pantau status pesanan dan riwayat belanja perangkat keamanan Anda</p>
        </div>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="p-4 sm:p-8">

      <!-- STATUS TABS (Sub-tabs) -->
      <div class="flex items-center gap-6 border-b border-gray-100 mb-6 overflow-x-auto no-scrollbar pb-1 px-1 sm:px-0">
        <button 
          v-for="tab in statusTabs" 
          :key="tab.id" 
          @click="activeTab = tab.id" 
          class="flex-shrink-0 pb-3 text-sm font-bold transition-all relative"
          :class="activeTab === tab.id ? 'text-[#03AC0E]' : 'text-gray-400 hover:text-gray-600'"
        >
          {{ tab.label }}
          <div v-if="activeTab === tab.id" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#03AC0E]"></div>
        </button>
      </div>

      <!-- TRANSACTION LIST -->
      <main class="space-y-6">
        <div v-if="isLoading" class="space-y-4">
          <div v-for="i in 3" :key="i" class="h-40 bg-gray-50 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="!transactions.length" class="py-24 text-center border-2 border-dashed border-gray-100 rounded-xl">
          <UIcon name="i-heroicons-shopping-cart" class="w-12 h-12 text-gray-200 mx-auto mb-4" />
          <p class="text-sm font-bold text-gray-400">Belum ada transaksi.</p>
        </div>

        <div v-else class="space-y-4">
          <div v-for="trx in transactions" :key="trx.uuid" 
            class="bg-white border border-gray-100 rounded-xl p-5 sm:p-6 transition-all hover:border-[#03AC0E]/30 shadow-sm hover:shadow-md group"
          >
            <!-- Card Header -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 pb-4 border-b border-gray-50">
              <div class="flex flex-wrap items-center gap-2 sm:gap-4">
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-shopping-bag" class="w-4 h-4 text-[#03AC0E]" />
                  <span class="text-[11px] font-black text-gray-900 uppercase tracking-tight">Belanja</span>
                </div>
                <span class="text-[11px] text-gray-400 font-bold uppercase">{{ formatDate(trx.created_at) }}</span>
                <div :class="getStatusConfig(trx).color" class="px-2 py-0.5 rounded-lg text-[10px] font-black border uppercase tracking-wider">
                  {{ getStatusConfig(trx).text }}
                </div>
                <span class="text-[11px] font-mono font-bold text-gray-300">#{{ trx.order_id }}</span>
              </div>
            </div>

            <!-- Card Body -->
            <div class="flex flex-col sm:flex-row gap-5">
              <div class="flex flex-1 gap-4">
                <div class="w-20 h-20 bg-gray-50 rounded-xl overflow-hidden border border-gray-100 shrink-0 shadow-inner">
                  <NuxtImg v-if="trx.items?.[0]?.cover_image_url" :src="trx.items[0].cover_image_url" class="w-full h-full object-contain p-2 group-hover:scale-110 transition-transform duration-500" />
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-200">
                    <UIcon name="i-heroicons-photo" class="w-8 h-8" />
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="text-sm font-black text-gray-900 truncate tracking-tight">{{ trx.items?.[0]?.item_name || 'Produk' }}</h4>
                  <p class="text-[11px] text-gray-500 font-bold mt-1">
                    {{ trx.items?.[0]?.quantity }} Barang <span class="text-gray-300 mx-1">×</span> {{ formatRupiah(trx.items?.[0]?.unit_price || 0) }}
                  </p>
                  <p v-if="trx.items?.length > 1" class="text-[10px] text-[#03AC0E] font-black mt-2 bg-[#03AC0E]/5 inline-block px-2 py-0.5 rounded-md">
                    +{{ trx.items.length - 1 }} produk lainnya
                  </p>
                </div>
              </div>

              <!-- Price Info -->
              <div class="sm:text-right sm:border-l sm:border-gray-50 sm:pl-8 flex flex-row sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-2">
                <div>
                  <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Total Belanja</p>
                  <p class="text-base font-black text-gray-900 tracking-tight">{{ formatRupiah(trx.gross_amount) }}</p>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="mt-6 flex flex-wrap items-center justify-end gap-3 pt-4 border-t border-gray-50">
              <NuxtLink :to="`/dashboard/orders/${trx.order_id}`" class="text-xs font-black text-gray-500 hover:text-[#03AC0E] px-4 py-2 transition-colors">
                Lihat Detail
              </NuxtLink>
              
              <button v-if="getStatusConfig(trx).text === 'Dikirim' && trx.trx_type !== 'jasa'"
                @click="confirmDelivery(trx.order_id)" :disabled="confirmModal.loading"
                class="px-6 py-2 bg-[#03AC0E] text-white text-xs font-black rounded-xl hover:bg-[#028a0b] transition-all active:scale-95 disabled:opacity-50 shadow-sm flex items-center gap-1.5"
              >
                <UIcon v-if="confirmModal.loading && confirmModal.orderId === trx.order_id" name="i-heroicons-arrow-path" class="w-3.5 h-3.5 animate-spin" />
                <UIcon v-else name="i-heroicons-check-circle" class="w-3.5 h-3.5" />
                Barang Sudah Sampai
              </button>
              
              <button v-if="(trx.transaction_status === 'settlement' || trx.transaction_status === 'success') && getStatusConfig(trx).text !== 'Dikirim'" 
                @click="navigateTo(`/product/${trx.items?.[0]?.stock_uuid}`)"
                class="px-6 py-2 border-2 border-[#03AC0E] text-[#03AC0E] text-xs font-black rounded-xl hover:bg-[#03AC0E] hover:text-white transition-all active:scale-95 shadow-sm"
              >
                Beli Lagi
              </button>

              <button v-if="['pending', 'pending_payment'].includes(trx.transaction_status)" 
                @click="navigateTo(`/payment/${trx.order_id}`)" 
                class="px-8 py-2.5 bg-[#03AC0E] text-white text-xs font-black rounded-xl hover:bg-[#028a0b] transition-all active:scale-95 shadow-md shadow-[#03AC0E]/20"
              >
                Bayar Sekarang
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- ── MODAL KONFIRMASI (CONFIRM DELIVERY) ── -->
    <Teleport to="body">
      <Transition name="modal-scale">
        <div v-if="confirmModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="confirmModal.show = false"></div>
          
          <!-- Card -->
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden p-6 flex flex-col items-center text-center z-10 border border-gray-100">
            <!-- Icon -->
            <div class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center text-[#03AC0E] mb-4 ring-8 ring-emerald-50/50">
              <UIcon name="i-heroicons-question-mark-circle" class="w-10 h-10" />
            </div>
            
            <h3 class="text-base font-black text-gray-900 mb-2">Konfirmasi Barang Sampai</h3>
            <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-6 leading-relaxed">
              Apakah Anda yakin barang pesanan dengan ID<br/>
              <span class="font-mono text-gray-900 font-black tracking-tight text-xs bg-gray-100 px-2 py-1 rounded">{{ confirmModal.orderId }}</span><br/>
              sudah sampai dan diterima dengan baik?
            </p>
            
            <div class="flex gap-3 w-full">
              <button 
                @click="confirmModal.show = false" 
                class="flex-1 py-3 text-xs font-bold text-gray-500 bg-gray-50 border border-gray-200 rounded-xl hover:bg-gray-100 hover:text-gray-700 transition-all uppercase tracking-widest"
              >
                Batal
              </button>
              <button 
                @click="executeConfirmDelivery" 
                :disabled="confirmModal.loading"
                class="flex-1 py-3 text-xs font-black text-white bg-[#03AC0E] rounded-xl hover:bg-[#028a0b] transition-all flex items-center justify-center gap-2 shadow-lg shadow-[#03AC0E]/20 disabled:opacity-50 uppercase tracking-widest"
              >
                <UIcon v-if="confirmModal.loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <span v-else>Ya, Sampai</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── MODAL SUKSES (ORDER COMPLETED) ── -->
    <Teleport to="body">
      <Transition name="modal-scale">
        <div v-if="successModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="closeSuccessModal"></div>
          
          <!-- Card -->
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden p-6 flex flex-col items-center text-center z-10 border border-gray-100 animate-bounce-short">
            <!-- Animated Success Checkmark -->
            <div class="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center text-[#03AC0E] mb-6 ring-8 ring-emerald-50">
              <UIcon name="i-heroicons-check-circle" class="w-12 h-12 animate-pulse" />
            </div>
            
            <h3 class="text-lg font-black text-gray-900 mb-2">Pesanan Selesai! 🎉</h3>
            <p class="text-xs text-gray-500 font-semibold mb-6 leading-relaxed">
              Terima kasih telah berbelanja di PasarCctv. Semoga produk kami dapat memenuhi kebutuhan keamanan Anda.
            </p>
            
            <button 
              @click="closeSuccessModal" 
              class="w-full py-3 text-xs font-black text-white bg-gray-900 rounded-xl hover:bg-black transition-all uppercase tracking-widest shadow-lg shadow-gray-900/20"
            >
              Selesai
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

/* Modal Scale Transition */
.modal-scale-enter-active, .modal-scale-leave-active {
  transition: opacity 0.25s ease;
}
.modal-scale-enter-active .relative, .modal-scale-leave-active .relative {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.modal-scale-enter-from, .modal-scale-leave-to {
  opacity: 0;
}
.modal-scale-enter-from .relative {
  transform: scale(0.9) translateY(12px);
  opacity: 0;
}
.modal-scale-leave-to .relative {
  transform: scale(0.95);
  opacity: 0;
}
</style>
