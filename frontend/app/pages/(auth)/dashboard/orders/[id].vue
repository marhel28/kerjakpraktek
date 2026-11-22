<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

definePageMeta({ layout: "auth" });

// ─── Midtrans Snap ────────────────────────────────────────
const config = useRuntimeConfig();
useHead({
  script: [{ src: "https://app.sandbox.midtrans.com/snap/snap.js", "data-client-key": config.public.midtransClientKey, async: true }],
});

const route = useRoute();
const orderId = route.params.id as string;
const API_BASE = `${config.public.apiBase}/transaksi`;
const getToken = () => useCookie("token").value;

const CATEGORY_LABELS: Record<string, string> = { 
  installation: "Pemasangan Baru", 
  maintenance: "Maintenance", 
  consultation: "Cek Lokasi", 
  troubleshoot: "Perbaikan" 
};

// ─── State ────────────────────────────────────────────────
const order = ref<any>(null);
const isLoading = ref(true);
const isRepaying = ref(false);
const isDownloadingInvoice = ref(false);

const downloadInvoice = async () => {
  if (isDownloadingInvoice.value) return;
  isDownloadingInvoice.value = true;
  try {
    const zone = encodeURIComponent(Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Jakarta");
    const response = await fetch(`${config.public.apiBase}/transaksi/invoice/${orderId}?tz=${zone}`, {
      method: "GET",
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    
    if (!response.ok) throw new Error("Gagal mengunduh invoice");
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `Invoice-${orderId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    useToast().add({ title: "Gagal Mengunduh", description: "Gagal mengunduh invoice. Silakan coba lagi.", color: "error" });
  } finally {
    isDownloadingInvoice.value = false;
  }
};

const fetchOrderDetail = async () => {
  isLoading.value = true;
  try {
    const response: any = await $fetch(`${API_BASE}/detail/${orderId}`, {
      method: "GET",
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    order.value = response.data || response;
  } catch (err: any) {
    order.value = null;
  } finally {
    isLoading.value = false;
  }
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

const confirmDelivery = () => {
  confirmModal.value = {
    show: true,
    orderId: orderId,
    loading: false,
  };
};

const executeConfirmDelivery = async () => {
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
      useToast().add({ title: "Gagal Konfirmasi", description: response.message || "Gagal mengonfirmasi penerimaan barang.", color: "error" });
    }
  } catch (err: any) {
    useToast().add({ title: "Gagal Konfirmasi", description: err?.data?.detail || "Gagal mengonfirmasi penerimaan barang.", color: "error" });
  } finally {
    confirmModal.value.loading = false;
  }
};

const closeSuccessModal = () => {
  successModal.value.show = false;
  fetchOrderDetail();
};

onMounted(() => fetchOrderDetail());

// ─── Stepper Logic ────────────────────────────────────────
const steps = [
  { id: "created", label: "Dibuat", icon: "i-heroicons-shopping-cart" },
  { id: "processing", label: "Diproses", icon: "i-heroicons-cube" },
  { id: "shipped", label: "Dikirim", icon: "i-heroicons-truck" },
  { id: "completed", label: "Selesai", icon: "i-heroicons-check-badge" },
];

const JASA_STEPS = [
  { id: "pending", label: "Dibuat", icon: "i-heroicons-document-text" },
  { id: "confirmed", label: "Konfirmasi", icon: "i-heroicons-user-group" },
  { id: "dp_paid", label: "Bayar DP", icon: "i-heroicons-credit-card" },
  { id: "progress", label: "Pengerjaan", icon: "i-heroicons-wrench" },
  { id: "done", label: "Selesai", icon: "i-heroicons-check-badge" },
];

const stepIndex = computed<number>(() => {
  if (!order.value) return 0;
  
  if (order.value.trx_type === 'jasa' && order.value.booking) {
    const status = (order.value.booking.status || "").toLowerCase();
    const sequence = ["pending", "confirmed", "dp_paid", "progress", "done", "lunas"];
    if (status === 'cancel') return -1;
    const idx = sequence.indexOf(status);
    return idx > 4 ? 4 : idx;
  }

  const tStatus = (order.value.transaction_status || "").toLowerCase();
  const sStatus = (order.value.shipment?.delivery_status || "").toLowerCase();
  const hasWaybill = !!order.value.shipment?.waybill_number;

  if (["cancel", "expire", "deny"].includes(tStatus)) return -1;
  if (["pending", "pending_payment"].includes(tStatus)) return 0;
  
  if (["settlement", "success", "capture"].includes(tStatus)) {
    if (["delivered", "completed"].includes(sStatus)) return 3;
    if (sStatus === "shipped" || hasWaybill) return 2;
    return 1;
  }
  return 0;
});

const formatRupiah = (angka: number) =>
  new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(angka || 0);

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return "-";
  return new Intl.DateTimeFormat("id-ID", { day: "2-digit", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit", timeZoneName: "short" }).format(new Date(dateString));
};

const payOrder = async () => {
  const existingToken = order.value?.snap_token || order.value?.raw_response?.token;
  if (existingToken) { openSnap(existingToken); return; }
  isRepaying.value = true;
  try {
    const res: any = await $fetch(`${API_BASE}/repay/${orderId}`, { method: "POST", headers: { Authorization: `Bearer ${getToken()}` } });
    if (res?.success && res?.data?.snap_token) openSnap(res.data.snap_token);
    else if (res?.snap_token) openSnap(res.snap_token);
  } catch (err: any) {
    useToast().add({ title: "Gagal Pembayaran", description: err?.data?.detail || "Gagal memuat pembayaran.", color: "error" });
  } finally { isRepaying.value = false; }
};

const isPaymentEmbedded = ref(false);

const openSnap = (token: string) => {
  const snapObj = (window as any).snap;
  if (!snapObj) return;
  
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
        useToast().add({ title: "Pembayaran Gagal", description: "Pembayaran gagal atau dibatalkan.", color: "error" });
      },
      onClose: () => {
        isPaymentEmbedded.value = false;
      }
    });
  }, 100);
};

const { getOrderStatus } = useOrderStatus();

const getStatusBadge = () => {
  return getOrderStatus(order.value?.transaction_status, order.value?.shipment?.delivery_status, !!order.value?.shipment?.waybill_number).badge;
};
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- HEADER -->
    <div class="px-8 py-4 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white z-10">
      <div class="flex items-center gap-4">
        <button @click="$router.back()" class="p-2 -ml-2 text-gray-400 hover:text-gray-900 transition-colors">
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        </button>
        <h1 class="text-base font-bold text-gray-900">Detail Transaksi</h1>
      </div>
      <div class="flex items-center gap-4">
        <button 
          v-if="order && ['settlement', 'success', 'capture'].includes(order.transaction_status?.toLowerCase())"
          @click="downloadInvoice" 
          :disabled="isDownloadingInvoice"
          class="flex items-center gap-2 text-gray-600 font-bold text-sm hover:text-black transition-colors disabled:opacity-50"
        >
          <UIcon v-if="isDownloadingInvoice" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
          <UIcon v-else name="i-heroicons-document-arrow-down" class="w-4 h-4" />
          {{ isDownloadingInvoice ? 'Generating...' : 'Cetak Invoice' }}
        </button>
        <div class="w-px h-4 bg-gray-200" v-if="order && ['settlement', 'success', 'capture'].includes(order.transaction_status?.toLowerCase())"></div>
        <a v-if="order" :href="`https://wa.me/${config.public.waNumber}?text=Bantuan Pesanan ${order.order_id}`" target="_blank" class="flex items-center gap-2 text-[#03AC0E] font-bold text-sm hover:underline">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-4 h-4" />
          Tanya Kami
        </a>
      </div>
    </div>

    <div v-if="isLoading" class="p-8 max-w-5xl mx-auto space-y-6">
      <div class="h-24 bg-gray-50 rounded-xl animate-pulse"></div>
      <div class="h-64 bg-gray-50 rounded-xl animate-pulse"></div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="h-40 bg-gray-50 rounded-xl animate-pulse"></div>
      </div>
    </div>

    <div v-else-if="!order" class="py-24 text-center max-w-md mx-auto px-8">
      <div class="w-20 h-20 bg-gray-50 rounded-xl flex items-center justify-center text-gray-200 mx-auto mb-6">
        <UIcon name="i-heroicons-shopping-cart" class="w-10 h-10" />
      </div>
      <h3 class="text-xl font-bold text-gray-900 mb-2">Pesanan Tidak Ada</h3>
      <p class="text-sm text-gray-500 font-medium leading-relaxed mb-8">
        Kami tidak menemukan data pesanan dengan ID ini. Pastikan Anda masuk dengan akun yang benar.
      </p>
      <NuxtLink to="/dashboard/orders" class="inline-flex items-center gap-2 px-8 py-3 bg-gray-900 text-white text-xs font-black rounded-xl hover:bg-black transition-all">
        Kembali ke Daftar
      </NuxtLink>
    </div>

    <div v-else class="p-4 sm:p-8 space-y-6 max-w-5xl mx-auto">
      
      <!-- 1. HEADER SUMMARY -->
      <div class="bg-white border border-gray-100 rounded-xl p-6 sm:p-8 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div class="space-y-2">
          <div class="flex items-center gap-3 flex-wrap">
            <h2 class="text-xl font-bold text-gray-900 font-mono tracking-tight">{{ order.order_id }}</h2>
            <div :class="getStatusBadge()" class="px-3 py-1 rounded-xl text-[10px] font-bold uppercase tracking-wider border">
              {{ getOrderStatus(order.transaction_status, order.shipment?.delivery_status, !!order.shipment?.waybill_number).label }}
            </div>
          </div>
          <p class="text-xs text-gray-500 font-medium flex items-center gap-2">
            <UIcon name="i-heroicons-calendar" class="w-4 h-4" />
            Dipesan pada {{ formatDate(order.created_at) }}
          </p>
        </div>
        
        <div class="flex items-center gap-3">
          <button v-if="['pending', 'pending_payment'].includes(order.transaction_status?.toLowerCase())" 
            @click="payOrder" :disabled="isRepaying"
            class="px-8 py-3 bg-[#03AC0E] text-white text-xs font-black rounded-xl hover:bg-[#028a0b] transition-all shadow-lg shadow-[#03AC0E]/20 flex items-center gap-2"
          >
            <UIcon v-if="isRepaying" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            Lanjutkan Pembayaran
          </button>
          
          <button v-if="stepIndex === 2 && order.trx_type !== 'jasa'"
            @click="confirmDelivery" :disabled="confirmModal.loading"
            class="px-8 py-3 bg-[#03AC0E] text-white text-xs font-black rounded-xl hover:bg-[#028a0b] transition-all shadow-lg shadow-[#03AC0E]/20 flex items-center gap-2"
          >
            <UIcon v-if="confirmModal.loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            <UIcon v-else name="i-heroicons-check-circle" class="w-4 h-4" />
            Barang Sudah Sampai
          </button>
          
          <a :href="`https://wa.me/${config.public.waNumber}?text=Halo Admin, saya ingin bertanya tentang pesanan ${order.order_id}`" 
             target="_blank"
             class="p-3 bg-white border border-gray-200 text-gray-400 hover:text-[#03AC0E] hover:border-[#03AC0E] rounded-xl transition-all shadow-sm"
          >
            <UIcon name="i-heroicons-chat-bubble-left-right" class="w-5 h-5" />
          </a>
        </div>
      </div>

      <!-- 2. STEPPER -->
      <section v-if="stepIndex >= 0" class="bg-white border border-gray-100 rounded-xl p-6 sm:p-8 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <template v-if="order.trx_type === 'jasa'">
          <div v-for="(step, i) in JASA_STEPS" :key="step.id" class="flex flex-col items-center gap-3 w-1/5 sm:w-auto flex-shrink-0">
            <div :class="i <= stepIndex ? 'bg-[#03AC0E] text-white ring-4 ring-[#03AC0E]/10' : 'bg-white text-gray-200 border-gray-100 border'" class="w-12 h-12 rounded-full flex items-center justify-center transition-all shadow-sm">
              <UIcon :name="step.icon" class="w-6 h-6" />
            </div>
            <span :class="i <= stepIndex ? 'text-gray-900 font-bold' : 'text-gray-500 font-medium'" class="text-[10px] uppercase tracking-wider text-center px-2 sm:whitespace-nowrap">{{ step.label }}</span>
          </div>
        </template>

        <template v-else>
          <div v-for="(step, i) in steps" :key="step.id" class="flex flex-col items-center gap-3 w-1/4 sm:w-auto flex-shrink-0">
            <div :class="i <= stepIndex ? 'bg-[#03AC0E] text-white ring-4 ring-[#03AC0E]/10' : 'bg-white text-gray-200 border-gray-100 border'" class="w-12 h-12 rounded-full flex items-center justify-center transition-all shadow-sm">
              <UIcon :name="step.icon" class="w-6 h-6" />
            </div>
            <span :class="i <= stepIndex ? 'text-gray-900 font-bold' : 'text-gray-500 font-medium'" class="text-[10px] uppercase tracking-wider text-center px-2 sm:whitespace-nowrap">{{ step.label }}</span>
          </div>
        </template>
      </section>

      <!-- EMBEDDED PAYMENT WIDGET -->
      <div v-show="isPaymentEmbedded" class="bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden max-w-xl mx-auto mb-8 animate-fade-in">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-credit-card" class="w-5 h-5 text-[#03AC0E]" />
            <h3 class="font-black text-gray-900 text-sm uppercase tracking-widest">Selesaikan Pembayaran</h3>
          </div>
          <button @click="isPaymentEmbedded = false" class="text-xs font-bold text-gray-400 hover:text-red-500 transition-colors uppercase tracking-widest">
            Tutup
          </button>
        </div>
        <div id="snap-container" class="w-full min-h-[500px]"></div>
      </div>

      <!-- 3. INFO GRID -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Payment Info -->
        <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center text-emerald-600">
              <UIcon name="i-heroicons-credit-card" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-gray-900 tracking-tight">Pembayaran</h3>
              <p class="text-[10px] text-gray-500 font-medium tracking-tight">{{ order.payment_type || 'Metode Otomatis' }}</p>
            </div>
          </div>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-[11px] text-gray-500 font-medium">Status</span>
              <span :class="getOrderStatus(order.transaction_status, order.shipment?.delivery_status, !!order.shipment?.waybill_number).badge" class="px-2 py-0.5 rounded-lg text-[9px] font-bold uppercase border">{{ getOrderStatus(order.transaction_status, order.shipment?.delivery_status, !!order.shipment?.waybill_number).label }}</span>
            </div>
            <div v-if="order.va_numbers?.[0]" class="flex justify-between items-center">
              <span class="text-[11px] text-gray-500 font-medium">VA {{ order.va_numbers[0].bank }}</span>
              <span class="text-xs font-bold text-gray-900">{{ order.va_numbers[0].va_number }}</span>
            </div>
            <div v-if="order.payment_code" class="flex justify-between items-center">
              <span class="text-[11px] text-gray-500 font-medium">Kode Bayar</span>
              <span class="text-xs font-bold text-gray-900">{{ order.payment_code }}</span>
            </div>
            <div class="flex justify-between items-center pt-3 border-t border-gray-50">
              <span class="text-[11px] text-gray-500 font-medium">Waktu Bayar</span>
              <span class="text-[11px] font-medium text-gray-700">{{ order.settlement_time ? formatDate(order.settlement_time) : '-' }}</span>
            </div>
          </div>
        </div>

        <!-- Shipping Info (Goods) -->
        <div v-if="order.trx_type !== 'jasa'" class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
              <UIcon name="i-heroicons-truck" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-gray-900 tracking-tight">Pengiriman</h3>
              <p class="text-[10px] text-gray-500 font-medium tracking-tight">{{ order.shipment?.courier_name || 'Reguler' }}</p>
            </div>
          </div>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-[11px] text-gray-500 font-medium">Layanan</span>
              <span class="text-[11px] font-medium text-gray-900">{{ order.shipment?.courier_service || '-' }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-[11px] text-gray-500 font-medium">No. Resi</span>
              <span class="text-[11px] font-bold text-[#03AC0E]">{{ order.shipment?.waybill_number || 'Proses' }}</span>
            </div>
            <div class="pt-3 border-t border-gray-50">
              <span class="text-[11px] text-gray-500 font-medium block mb-1">Alamat</span>
              <p class="text-[11px] font-medium text-gray-900 leading-tight mb-0.5">{{ order.shipment?.recipient_name }}</p>
              <p class="text-[10px] text-gray-500 leading-relaxed line-clamp-2">{{ order.shipment?.shipping_address }}</p>
            </div>
            <div v-if="stepIndex === 2" class="pt-3 border-t border-gray-50">
              <button 
                @click="confirmDelivery" :disabled="confirmModal.loading"
                class="w-full py-2 bg-[#03AC0E] text-white text-xs font-black rounded-lg hover:bg-[#028a0b] transition-all flex items-center justify-center gap-2"
              >
                <UIcon v-if="confirmModal.loading" name="i-heroicons-arrow-path" class="w-3.5 h-3.5 animate-spin" />
                <UIcon v-else name="i-heroicons-check-circle" class="w-3.5 h-3.5" />
                Konfirmasi Barang Sampai
              </button>
            </div>
          </div>
        </div>

        <!-- Booking Info (Service) -->
        <div v-if="order.trx_type === 'jasa' && order.booking" class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
              <UIcon name="i-heroicons-wrench-screwdriver" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-gray-900 tracking-tight">Informasi Kunjungan</h3>
              <p class="text-[10px] text-gray-500 font-medium tracking-tight">{{ CATEGORY_LABELS[order.booking.category] || order.booking.category }}</p>
            </div>
          </div>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-[11px] text-gray-500 font-medium">Jadwal</span>
              <span class="text-[11px] font-medium text-gray-900">{{ formatDate(order.booking.scheduled_date) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-[11px] text-gray-500 font-medium">Waktu</span>
              <span class="text-[11px] font-medium text-[#03AC0E]">{{ order.booking.time_slot }}</span>
            </div>
            <div class="pt-3 border-t border-gray-50">
              <span class="text-[11px] text-gray-500 font-medium block mb-1">PIC & Lokasi</span>
              <p class="text-[11px] font-medium text-gray-900 leading-tight mb-0.5">{{ order.booking.contact_name }} ({{ order.booking.contact_phone }})</p>
              <p class="text-[10px] text-gray-500 leading-relaxed line-clamp-2">{{ order.booking.address }}, {{ order.booking.city }}</p>
            </div>
          </div>
        </div>

        <!-- Technician & Verification -->
        <div v-if="order.trx_type === 'jasa' && order.booking?.technician" class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600">
              <UIcon name="i-heroicons-identification" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-gray-900 tracking-tight">Teknisi Bertugas</h3>
              <p class="text-[10px] text-gray-500 font-medium tracking-tight">Tim PasarCCTV</p>
            </div>
          </div>
          <div class="flex items-center gap-4 mb-6">
            <div class="w-16 h-16 rounded-xl bg-gray-50 border border-gray-100 overflow-hidden shrink-0">
              <img v-if="order.booking.technician.picture_url" :src="order.booking.technician.picture_url" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-200">
                <UIcon name="i-heroicons-user" class="w-8 h-8" />
              </div>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-bold text-gray-900 truncate">{{ order.booking.technician.name }}</p>
              <p class="text-[10px] font-bold text-gray-500">{{ order.booking.technician.id_employee }}</p>
              <a :href="`https://wa.me/${order.booking.technician.phone?.replace('+', '')}`" target="_blank" class="mt-1 flex items-center gap-1 text-[10px] font-bold text-[#03AC0E] hover:underline">
                <UIcon name="i-heroicons-phone" class="w-3 h-3" />
                Hubungi WA
              </a>
            </div>
          </div>
          <div class="pt-4 border-t border-gray-100 flex flex-col items-center">
            <div class="bg-gray-50 p-4 rounded-xl border border-gray-100 mb-2 text-center">
              <p class="text-sm text-gray-700 font-bold tracking-wider">{{ order.booking.technician.id_employee }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ order.order_id }}</p>
            </div>
            <p class="text-[9px] text-center text-gray-500 font-semibold uppercase tracking-wider leading-relaxed">
              ID Verifikasi Teknisi<br/>PasarCCTV Cimahi
            </p>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm lg:col-span-1 md:col-span-2">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-amber-50 rounded-xl flex items-center justify-center text-amber-600">
              <UIcon name="i-heroicons-receipt-percent" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-gray-900 tracking-tight">Ringkasan</h3>
              <p class="text-[10px] text-gray-500 font-medium tracking-tight">Final Kalkulasi</p>
            </div>
          </div>
          <div class="space-y-3">
            <div class="flex justify-between text-[11px] font-medium">
              <span class="text-gray-500">Subtotal</span>
              <span class="text-gray-900">{{ formatRupiah(order.items_subtotal) }}</span>
            </div>
            <div v-if="order.total_discount > 0" class="flex justify-between text-[11px] font-medium">
              <span class="text-emerald-600">Promo</span>
              <span class="text-emerald-600">- {{ formatRupiah(order.total_discount) }}</span>
            </div>
            <div class="flex justify-between text-[11px] font-medium">
              <span class="text-gray-500">Ongkir</span>
              <span class="text-gray-900">{{ formatRupiah(order.shipping_cost) }}</span>
            </div>
            <div v-if="order.service_cost > 0" class="flex justify-between text-[11px] font-medium">
              <span class="text-gray-500">Layanan</span>
              <span class="text-gray-900">{{ formatRupiah(order.service_cost) }}</span>
            </div>
            <div class="pt-4 mt-2 border-t border-gray-100 flex justify-between items-center">
              <span class="text-xs font-bold text-gray-900">Total</span>
              <span class="text-xl font-bold text-[#03AC0E] tracking-tight">{{ formatRupiah(order.gross_amount) }}</span>
            </div>
          </div>
        </div>

        <!-- Payment History (For Jasa) -->
        <div v-if="order.trx_type === 'jasa' && order.payments?.length" class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm md:col-span-2 lg:col-span-1">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center text-emerald-600">
              <UIcon name="i-heroicons-banknotes" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-xs font-bold text-gray-900 tracking-tight">Riwayat Bayar</h3>
              <p class="text-[10px] text-gray-500 font-medium tracking-tight">Status Pembayaran</p>
            </div>
          </div>
          <div class="space-y-4">
            <div v-for="pay in order.payments" :key="pay.type" class="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div class="flex justify-between items-start mb-1">
                <span class="text-[10px] font-bold text-gray-900">{{ pay.type === 'dp' ? 'DP 50%' : 'Pelunasan' }}</span>
                <span :class="pay.status === 'success' ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'" class="px-2 py-0.5 rounded text-[8px] font-bold uppercase">
                  {{ pay.status }}
                </span>
              </div>
              <p class="text-[11px] font-bold text-gray-900">{{ formatRupiah(pay.amount) }}</p>
              <p v-if="pay.paid_at" class="text-[9px] text-gray-500 font-medium mt-1">{{ formatDate(pay.paid_at) }} • {{ pay.method || 'Midtrans' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. TIMELINE -->
      <section v-if="order.timeline?.length" class="bg-white border border-gray-100 rounded-xl p-6 sm:p-8 shadow-sm">
        <h3 class="text-xs font-bold text-gray-900 tracking-tight mb-6 flex items-center gap-2">
          <UIcon name="i-heroicons-clock" class="w-5 h-5 text-[#03AC0E]" />
          Riwayat Aktivitas
        </h3>
        <div class="relative pl-8 space-y-6">
          <div class="absolute left-[11px] top-2 bottom-2 w-0.5 bg-gray-100"></div>
          <div v-for="(log, i) in order.timeline" :key="i" class="relative">
            <div :class="log.status === 'done' ? 'bg-[#03AC0E]' : 'bg-gray-200'" class="absolute -left-8 top-1 w-2.5 h-2.5 rounded-full border-4 border-white ring-2 ring-gray-50 z-10"></div>
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
              <p :class="log.status === 'done' ? 'text-gray-900 font-bold' : 'text-gray-500 font-medium'" class="text-sm tracking-tight">{{ log.event }}</p>
              <span v-if="log.timestamp" class="text-[10px] text-gray-500 font-medium">{{ formatDate(log.timestamp) }}</span>
              <span v-else class="text-[10px] text-gray-400 font-medium italic">Menunggu</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 4. ITEM LIST -->
      <section class="bg-white border border-gray-100 rounded-xl overflow-hidden shadow-sm">
        <div class="px-6 sm:px-8 py-5 border-b border-gray-50 bg-gray-50/30 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-black rounded-xl flex items-center justify-center text-white">
              <UIcon name="i-heroicons-shopping-bag" class="w-5 h-5" />
            </div>
            <h3 class="text-sm font-bold text-gray-900 tracking-tight">Produk yang Dibeli</h3>
          </div>
          <span class="text-[10px] font-medium text-gray-500">{{ order.items?.length || 0 }} Item</span>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="(item, idx) in order.items" :key="idx" class="p-6 sm:p-8 flex flex-col sm:flex-row items-start gap-6 hover:bg-gray-50/50 transition-all group">
            <div class="w-24 h-24 bg-white rounded-xl overflow-hidden border border-gray-100 shrink-0 shadow-sm p-2">
              <NuxtImg v-if="item.cover_image_url" :src="item.cover_image_url" class="w-full h-full object-contain group-hover:scale-110 transition-transform duration-500" />
              <div v-else class="w-full h-full flex items-center justify-center"><UIcon name="i-heroicons-photo" class="w-10 h-10 text-gray-200" /></div>
            </div>
            <div class="flex-1 min-w-0 space-y-3">
              <div>
                <h4 class="text-base font-bold text-gray-900 tracking-tight mb-1">{{ item.item_name || item.stock_title || '-' }}</h4>
                <div class="flex items-center gap-4 text-[11px] font-medium text-gray-500">
                  <span>{{ item.brand || 'No Brand' }}</span>
                  <span class="w-1 h-1 bg-gray-200 rounded-full"></span>
                  <span>{{ item.quantity }} Barang</span>
                  <span class="w-1 h-1 bg-gray-200 rounded-full"></span>
                  <span class="text-gray-900 font-bold">{{ formatRupiah(item.unit_price) }}</span>
                </div>
              </div>
              
              <!-- Specs Chips -->
              <div v-if="item.specs && Object.keys(item.specs).length > 0" class="flex flex-wrap gap-2">
                <span v-for="(val, key) in item.specs" :key="key" class="px-2 py-0.5 bg-gray-100 text-[9px] font-semibold text-gray-600 rounded">
                  {{ key.replace('_', ' ') }}: {{ val }}
                </span>
              </div>

              <!-- Addons List -->
              <div v-if="item.addons?.length" class="bg-emerald-50/50 rounded-xl border border-emerald-100/50 p-4 space-y-2">
                <p class="text-[9px] font-bold text-emerald-700 uppercase tracking-widest mb-2 flex items-center gap-2">
                  <UIcon name="i-heroicons-sparkles" class="w-3.5 h-3.5" />
                  Layanan Tambahan
                </p>
                <div v-for="addon in item.addons" :key="addon.uuid" class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="w-1 h-1 bg-emerald-400 rounded-full"></span>
                    <span class="text-[11px] text-emerald-800 font-bold">{{ addon.name }} (x{{ addon.quantity }})</span>
                  </div>
                  <span class="text-[11px] font-black text-emerald-600">{{ formatRupiah(addon.price * addon.quantity) }}</span>
                </div>
              </div>
            </div>
            <div class="w-full sm:w-auto sm:text-right pt-4 sm:pt-0 border-t sm:border-0 border-gray-50">
              <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Subtotal Item</p>
              <p class="text-lg font-black text-gray-900 tracking-tighter">{{ formatRupiah(item.subtotal) }}</p>
            </div>
          </div>
        </div>
      </section>

    </div>

    <!-- ── MODAL KONFIRMASI & SUKSES ── -->
    <DashboardConfirmDeliveryModal
      :show="confirmModal.show"
      :order-id="confirmModal.orderId"
      :loading="confirmModal.loading"
      @confirm="executeConfirmDelivery"
      @close="confirmModal.show = false"
    />
    <DashboardSuccessDeliveryModal :show="successModal.show" @close="closeSuccessModal" />

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
