<script setup lang="ts">
import { ref, watch, onMounted } from "vue";

definePageMeta({ layout: "auth" });
const config = useRuntimeConfig();
const toast = useToast();
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
  return new Intl.DateTimeFormat("id-ID", { day: "2-digit", month: "short", year: "numeric", timeZoneName: "short" }).format(new Date(dateString));
};

import { useOrderStatus } from "~/composables/useOrderStatus";
const { getOrderStatus } = useOrderStatus();

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
      toast.add({ title: "Gagal Konfirmasi", description: response.message || "Gagal mengonfirmasi penerimaan barang.", color: "error" });
    }
  } catch (err: any) {
    toast.add({ title: "Gagal Konfirmasi", description: err?.data?.detail || "Gagal mengonfirmasi penerimaan barang.", color: "error" });
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
      <h1 class="text-base font-bold text-gray-900">Pesanan Saya</h1>
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

        <DashboardEmptyState
          v-else-if="!transactions.length"
          icon="i-heroicons-shopping-bag"
          title="Belum Ada Transaksi"
          description="Riwayat belanja perangkat keamanan Anda akan tampil di sini."
          cta-label="Mulai Belanja"
          cta-to="/search"
        />

        <div v-else class="space-y-4">
          <div v-for="trx in transactions" :key="trx.uuid" 
            class="bg-white border border-gray-100 rounded-xl p-5 sm:p-6 transition-all hover:border-[#03AC0E]/30 shadow-sm hover:shadow-md group"
          >
            <!-- Card Header -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 pb-4 border-b border-gray-50">
              <div class="flex flex-wrap items-center gap-2 sm:gap-4">
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-shopping-bag" class="w-4 h-4 text-[#03AC0E]" />
                  <span class="text-[11px] font-bold text-gray-900">Belanja</span>
                </div>
                <span class="text-[11px] text-gray-500 font-medium">{{ formatDate(trx.created_at) }}</span>
                <div :class="getOrderStatus(trx.transaction_status, trx.shipment?.delivery_status, !!trx.shipment?.waybill_number).badge" class="px-2 py-0.5 rounded-lg text-[10px] font-bold border uppercase tracking-wider">
                  {{ getOrderStatus(trx.transaction_status, trx.shipment?.delivery_status, !!trx.shipment?.waybill_number).label }}
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
                  <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-0.5">Total Belanja</p>
                  <p class="text-base font-bold text-gray-900 tracking-tight">{{ formatRupiah(trx.gross_amount) }}</p>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="mt-6 flex flex-wrap items-center justify-end gap-3 pt-4 border-t border-gray-50">
              <NuxtLink :to="`/dashboard/orders/${trx.order_id}`" class="text-xs font-black text-gray-500 hover:text-[#03AC0E] px-4 py-2 transition-colors">
                Lihat Detail
              </NuxtLink>
              
              <button v-if="getOrderStatus(trx.transaction_status, trx.shipment?.delivery_status, !!trx.shipment?.waybill_number).label === 'Dikirim' && trx.trx_type !== 'jasa'"
                @click="confirmDelivery(trx.order_id)" :disabled="confirmModal.loading"
                class="px-6 py-2 bg-[#03AC0E] text-white text-xs font-black rounded-xl hover:bg-[#028a0b] transition-all active:scale-95 disabled:opacity-50 shadow-sm flex items-center gap-1.5"
              >
                <UIcon v-if="confirmModal.loading && confirmModal.orderId === trx.order_id" name="i-heroicons-arrow-path" class="w-3.5 h-3.5 animate-spin" />
                <UIcon v-else name="i-heroicons-check-circle" class="w-3.5 h-3.5" />
                Barang Sudah Sampai
              </button>
              
              <button v-if="(trx.transaction_status === 'settlement' || trx.transaction_status === 'success') && getOrderStatus(trx.transaction_status, trx.shipment?.delivery_status, !!trx.shipment?.waybill_number).label !== 'Dikirim'" 
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

    <!-- ── MODAL KONFIRMASI & SUKSES ── -->
    <DashboardConfirmDeliveryModal
      :show="confirmModal.show"
      :order-id="confirmModal.orderId"
      :loading="confirmModal.loading"
      @confirm="executeConfirmDelivery"
      @close="confirmModal.show = false"
    />
    <DashboardSuccessDeliveryModal
      :show="successModal.show"
      @close="closeSuccessModal"
    />
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
