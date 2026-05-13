<script setup lang="ts">
import { ref, computed } from "vue";

definePageMeta({ layout: "auth" });

interface PaymentInfo { uuid: string; order_id: string; payment_type: string; gross_amount: number; status: string; }
interface Booking {
  uuid: string; booking_number: string; category: string; camera_count: number; brand: string; addons: string[];
  scheduled_date: string; time_slot: string; address: string; city: string; distance_km: number; contact_name: string; contact_phone: string;
  device_price: number; service_price: number; addon_price: number; transport_fee: number; total_price: number;
  dp_percentage: number; dp_amount: number; remaining_amount: number; status: string; payments: PaymentInfo[]; created_at: string;
}

const route = useRoute();
const id = route.params.id as string;
const { data: booking, pending, error, refresh } = await useAsyncData<Booking>(`jasa-${id}`, () => $fetch(`/api/jasa/${id}`));

const payLoading = ref(false);
const toast = ref({ show: false, message: "", type: "success" as "success" | "error" });

const SLOT_LABELS: Record<string, string> = { "08:00-11:00": "Pagi (08:00 - 11:00)", "11:00-14:00": "Siang (11:00 - 14:00)", "14:00-17:00": "Sore (14:00 - 17:00)" };
const CATEGORY_LABELS: Record<string, string> = { installation: "Pemasangan Baru", maintenance: "Maintenance", consultation: "Cek Lokasi", troubleshoot: "Perbaikan" };

type StatusKey = "pending" | "confirmed" | "dp_paid" | "progress" | "done" | "lunas" | "cancel";
const STATUS_CONFIG: Record<StatusKey, { label: string; color: string; icon: string }> = {
  pending: { label: "Menunggu Konfirmasi", color: "text-amber-600 bg-amber-50 border-amber-100", icon: "i-heroicons-clock" },
  confirmed: { label: "Menunggu Pembayaran DP", color: "text-orange-600 bg-orange-50 border-orange-100", icon: "i-heroicons-wallet" },
  dp_paid: { label: "DP Diterima", color: "text-blue-600 bg-blue-50 border-blue-100", icon: "i-heroicons-shield-check" },
  progress: { label: "Sedang Dikerjakan", color: "text-purple-600 bg-purple-50 border-purple-100", icon: "i-heroicons-wrench" },
  done: { label: "Selesai", color: "text-teal-600 bg-teal-50 border-teal-100", icon: "i-heroicons-check-badge" },
  lunas: { label: "Lunas", color: "text-[#03AC0E] bg-emerald-50 border-emerald-100", icon: "i-heroicons-check-circle" },
  cancel: { label: "Dibatalkan", color: "text-red-600 bg-red-50 border-red-100", icon: "i-heroicons-x-circle" },
};

const statusStyle = computed(() => STATUS_CONFIG[booking.value?.status as StatusKey] || STATUS_CONFIG.pending);

const TIMELINE = [
  { key: "pending", label: "Dibuat", icon: "i-heroicons-document-plus" },
  { key: "confirmed", label: "Konfirmasi", icon: "i-heroicons-user-group" },
  { key: "dp_paid", label: "Bayar DP", icon: "i-heroicons-credit-card" },
  { key: "progress", label: "Pengerjaan", icon: "i-heroicons-cog" },
  { key: "done", label: "Selesai", icon: "i-heroicons-check-badge" },
];

const statusSteps = computed(() => {
  const current = booking.value?.status || "pending";
  const order = ["pending", "confirmed", "dp_paid", "progress", "done", "lunas"];
  const currentIdx = order.indexOf(current);
  return TIMELINE.map((step, i) => ({ ...step, done: i < currentIdx, active: i === currentIdx }));
});

const isFullyPaid = computed(() => booking.value?.status === "lunas");
const canPayDp = computed(() => booking.value?.status === "confirmed");
const canPayLunas = computed(() => booking.value?.status === "done");

async function payNow(type: "dp" | "lunas") {
  if (!booking.value) return; payLoading.value = true;
  try {
    const res = await $fetch<any>(`/api/jasa/${booking.value.uuid}/pay?payment_type=${type}`, { method: "POST" });
    if (res.payment_token && (window as any).snap) {
      (window as any).snap.pay(res.payment_token, { onSuccess: async () => { showToast("Berhasil!", "success"); await refresh(); } });
    } else if (res.payment_url) { window.open(res.payment_url, "_blank"); }
  } catch (e: any) { showToast("Gagal!", "error"); } finally { payLoading.value = false; }
}

function formatRp(n: number) { return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(n); }
function formatDate(iso: string) { return new Date(iso).toLocaleDateString("id-ID", { weekday: "long", day: "numeric", month: "long", year: "numeric" }); }
function showToast(message: string, type: "success" | "error") { toast.value = { show: true, message, type }; setTimeout(() => toast.value.show = false, 3000); }
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- HEADER -->
    <div class="px-8 py-4 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white z-10">
      <div class="flex items-center gap-4">
        <button @click="$router.back()" class="p-2 -ml-2 text-gray-400 hover:text-gray-900 transition-colors">
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        </button>
        <h1 class="text-base font-bold text-gray-900">Detail Booking Jasa</h1>
      </div>
      <a v-if="booking" :href="`https://wa.me/6282218828108?text=Halo Admin, bantu cek booking ${booking.booking_number}`" target="_blank" class="flex items-center gap-2 text-[#03AC0E] font-bold text-sm hover:underline">
        <UIcon name="i-heroicons-chat-bubble-left-right" class="w-4 h-4" />
        Tanya Admin
      </a>
    </div>

    <div v-if="pending" class="p-8 space-y-6">
      <div class="h-24 bg-gray-50 rounded-xl animate-pulse"></div>
      <div class="h-48 bg-gray-50 rounded-xl animate-pulse"></div>
    </div>

    <div v-else-if="!booking" class="py-20 text-center border-2 border-dashed border-gray-100 rounded-xl m-8">
      <p class="text-gray-400 font-bold">Booking tidak ditemukan.</p>
    </div>

    <div v-else class="p-8 space-y-8">
      
      <!-- 1. STATUS & NUMBER -->
      <section :class="statusStyle.color" class="p-6 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div>
          <p class="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-70">Status Booking</p>
          <p class="text-lg font-black uppercase tracking-tight">{{ statusStyle.label }}</p>
        </div>
        <div class="sm:text-right">
          <p class="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-70">No. Booking</p>
          <p class="text-sm font-mono font-bold tracking-widest text-[#03AC0E]">#{{ booking.booking_number }}</p>
          <p class="text-[10px] text-gray-400 font-medium mt-1">Dibuat: {{ new Date(booking.created_at).toLocaleDateString() }}</p>
        </div>
      </section>

      <!-- 2. STEPPER -->
      <section v-if="booking.status !== 'cancel'" class="bg-white border border-gray-200 rounded-xl p-8 overflow-x-auto no-scrollbar shadow-sm">
        <div class="min-w-[600px] flex justify-between relative py-4">
          <div class="absolute top-1/2 -translate-y-1/2 left-[5%] right-[5%] h-0.5 bg-gray-100"></div>
          <div v-for="(step, i) in statusSteps" :key="step.key" class="relative z-10 flex flex-col items-center gap-3 w-1/5">
            <div :class="step.done || step.active ? 'bg-[#03AC0E] text-white' : 'bg-white text-gray-200 border-gray-100 border'" class="w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-sm">
              <UIcon :name="step.icon" class="w-5 h-5" />
            </div>
            <span :class="step.done || step.active ? 'text-gray-900 font-bold' : 'text-gray-400 font-medium'" class="text-[11px] uppercase tracking-wider text-center px-2">{{ step.label }}</span>
          </div>
        </div>
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- LEFT: SERVICE DETAILS -->
        <div class="lg:col-span-2 space-y-8">
          <section class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h3 class="text-xs font-bold text-gray-900 uppercase tracking-widest">Informasi Layanan</h3>
            </div>
            <div class="p-6">
              <div class="flex items-start gap-6 p-4 bg-gray-50 rounded-xl border border-gray-100 mb-6">
                <div class="w-16 h-16 bg-white rounded-lg flex items-center justify-center border border-gray-100 shrink-0 shadow-sm">
                  <UIcon name="i-heroicons-wrench-screwdriver" class="w-8 h-8 text-[#03AC0E]" />
                </div>
                <div>
                  <h4 class="text-base font-bold text-gray-900">{{ CATEGORY_LABELS[booking.category] || booking.category }}</h4>
                  <p class="text-xs text-gray-500 mt-1">{{ booking.camera_count }} Titik Pemasangan • {{ booking.brand }}</p>
                  <p class="text-[10px] font-bold text-[#03AC0E] uppercase mt-2 tracking-widest">Jarak Lokasi: {{ booking.distance_km }} KM</p>
                </div>
              </div>

              <div v-if="booking.addons?.length" class="space-y-3">
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Tambahan Layanan:</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="addon in booking.addons" :key="addon" class="px-3 py-1 bg-[#03AC0E]/5 text-[#03AC0E] border border-[#03AC0E]/10 rounded-lg text-[10px] font-bold uppercase tracking-wider">{{ addon }}</span>
                </div>
              </div>
            </div>
          </section>

          <section class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-6">Lokasi & Jadwal</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="space-y-4">
                <div>
                  <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Jadwal Kunjungan</p>
                  <p class="text-sm font-bold text-gray-900 mt-1">{{ formatDate(booking.scheduled_date) }}</p>
                  <p class="text-xs text-gray-500 font-medium">{{ SLOT_LABELS[booking.time_slot] || booking.time_slot }}</p>
                </div>
                <div>
                  <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">PIC Kunjungan</p>
                  <p class="text-sm font-bold text-gray-900 mt-1">{{ booking.contact_name }}</p>
                  <p class="text-xs text-gray-500 font-mono">{{ booking.contact_phone }}</p>
                </div>
              </div>
              <div>
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Alamat Lengkap</p>
                <p class="text-sm font-medium text-gray-700 mt-2 leading-relaxed">{{ booking.address }}</p>
                <p class="text-xs font-bold text-gray-900 mt-2 uppercase tracking-widest">{{ booking.city }}</p>
              </div>
            </div>
          </section>
        </div>

        <!-- RIGHT: PRICING SUMMARY -->
        <div class="space-y-8">
          <section class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm sticky top-24">
            <h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-6">Rincian Biaya</h3>
            <div class="space-y-4">
              <div v-if="booking.device_price > 0" class="flex justify-between text-xs font-medium">
                <span class="text-gray-500">Estimasi Perangkat</span>
                <span class="text-gray-900">{{ formatRp(booking.device_price) }}</span>
              </div>
              <div class="flex justify-between text-xs font-medium">
                <span class="text-gray-500">Jasa Pemasangan</span>
                <span class="text-gray-900">{{ formatRp(booking.service_price) }}</span>
              </div>
              <div v-if="booking.addon_price > 0" class="flex justify-between text-xs font-medium">
                <span class="text-gray-500">Biaya Tambahan</span>
                <span class="text-gray-900">{{ formatRp(booking.addon_price) }}</span>
              </div>
              <div v-if="booking.transport_fee > 0" class="flex justify-between text-xs font-medium">
                <span class="text-gray-500">Biaya Transport</span>
                <span class="text-gray-900">{{ formatRp(booking.transport_fee) }}</span>
              </div>
              <div class="pt-4 border-t border-gray-100 flex justify-between items-center">
                <span class="text-sm font-bold text-gray-900">Total Estimasi</span>
                <span class="text-xl font-black text-[#03AC0E] tracking-tight">{{ formatRp(booking.total_price) }}</span>
              </div>
            </div>

            <div class="mt-6 p-4 bg-gray-50 rounded-xl border border-gray-100 space-y-3">
              <div class="flex justify-between text-[11px] font-bold">
                <span class="text-gray-400 uppercase tracking-wider">DP Dibayar</span>
                <span class="text-gray-900">{{ formatRp(booking.dp_amount) }}</span>
              </div>
              <div class="flex justify-between text-[11px] font-bold">
                <span class="text-gray-400 uppercase tracking-wider">Sisa Pelunasan</span>
                <span :class="isFullyPaid ? 'text-[#03AC0E]' : 'text-red-500'">{{ formatRp(booking.remaining_amount) }}</span>
              </div>
            </div>

            <div v-if="canPayDp || canPayLunas" class="mt-8">
              <button @click="payNow(canPayDp ? 'dp' : 'lunas')" :disabled="payLoading" class="w-full py-4 bg-[#03AC0E] text-white text-xs font-black rounded-lg hover:bg-[#028a0b] transition-all flex items-center justify-center gap-2 shadow-sm">
                <UIcon v-if="payLoading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-credit-card" class="w-5 h-5" />
                {{ canPayDp ? 'Bayar DP Sekarang' : 'Bayar Pelunasan' }}
              </button>
            </div>
            <div v-else-if="isFullyPaid" class="mt-8 p-4 bg-emerald-50 rounded-lg border border-emerald-100 text-center">
              <UIcon name="i-heroicons-check-circle" class="w-8 h-8 text-[#03AC0E] mx-auto mb-2" />
              <p class="text-[10px] font-bold text-[#03AC0E] uppercase tracking-widest">Pembayaran Lunas</p>
            </div>
          </section>
        </div>

      </div>
    </div>

    <!-- Toast -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="translate-y-10 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-10 opacity-0"
    >
      <div v-if="toast.show" class="fixed bottom-10 left-1/2 -translate-x-1/2 z-[100] px-6 py-3 bg-gray-900 text-white text-xs font-bold rounded-xl shadow-xl uppercase tracking-widest">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
