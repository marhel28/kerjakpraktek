<script setup lang="ts">
import { ref, computed, watch } from "vue";

definePageMeta({ layout: "auth" });
useHead({ title: "Booking Jasa Saya — PasarCctv" });

const route = useRoute();
const router = useRouter();

// ── State ──────────────────────────────────────────────────────────
const currentStatus = ref<string>((route.query.status as string) || "all");
const currentSort = ref<string>((route.query.sort as string) || "newest");
const currentPage = ref<number>(Number(route.query.page) || 1);
const searchInput = ref<string>((route.query.q as string) || "");
const debouncedQ = ref<string>(searchInput.value);
const payingUuid = ref<string | null>(null);
const toastError = ref<string | null>(null);

let searchTimer: ReturnType<typeof setTimeout>;
watch(searchInput, (val) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { debouncedQ.value = val; currentPage.value = 1; }, 300);
});

const queryParams = computed(() => ({
  status: currentStatus.value,
  sort: currentSort.value,
  page: currentPage.value,
  size: 10,
  ...(debouncedQ.value ? { q: debouncedQ.value } : {}),
}));

watch(queryParams, (params) => { router.replace({ query: { ...params, page: String(params.page) } }); }, { deep: true });

const { data, pending, refresh } = await useFetch("/api/jasa", {
  query: queryParams,
  watch: [queryParams],
});

function setStatus(val: string) { currentStatus.value = val; currentPage.value = 1; }
function formatRupiah(amount: number): string {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(amount);
}

function statusBadgeClass(color: string): string {
  const map: Record<string, string> = {
    amber: "bg-amber-50 text-amber-600 border-amber-100",
    blue: "bg-blue-50 text-blue-600 border-blue-100",
    green: "bg-emerald-50 text-emerald-600 border-emerald-100",
    purple: "bg-purple-50 text-purple-600 border-purple-100",
    red: "bg-red-50 text-red-500 border-red-100",
    gray: "bg-gray-50 text-gray-500 border-gray-100",
  };
  return map[color] ?? map.gray;
}


const statusTabs = [
  { value: "all", label: "Semua" },
  { value: "pending", label: "Menunggu" },
  { value: "confirmed", label: "Dikonfirmasi" },
  { value: "dp_paid", label: "DP Diterima" },
  { value: "progress", label: "Proses" },
  { value: "done", label: "Selesai" },
  { value: "lunas", label: "Lunas" },
  { value: "cancel", label: "Dibatalkan" },
];

async function handlePay(booking: any) {
  if (booking.action.payment_url) { window.open(booking.action.payment_url, "_blank"); return; }
  payingUuid.value = String(booking.uuid);
  try {
    const paymentType = booking.action.action === "pay_dp" ? "dp" : "lunas";
    const res = await $fetch<any>(`/api/jasa/${booking.uuid}/pay`, { method: "POST", query: { payment_type: paymentType } });
    if (res.payment_url) { window.open(res.payment_url, "_blank"); await refresh(); }
  } catch (err: any) {
    toastError.value = "Gagal memproses pembayaran.";
    setTimeout(() => toastError.value = null, 3000);
  } finally { payingUuid.value = null; }
}
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- MOBILE HEADER -->
    <div class="lg:hidden flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-white sticky top-0 z-10">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/dashboard')" class="p-1 -ml-1 text-gray-400 hover:text-gray-900 transition-colors">
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        </button>
        <h1 class="text-base font-black text-gray-900 uppercase tracking-wider">Jasa Saya</h1>
      </div>
      <NuxtLink to="/services/booking" class="p-2 bg-[#03AC0E]/10 text-[#03AC0E] active:bg-[#03AC0E]/20 rounded-lg transition-all flex items-center justify-center">
        <UIcon name="i-heroicons-plus" class="w-5 h-5" />
      </NuxtLink>
    </div>

    <!-- DESKTOP HEADER (Tokopedia Style) -->
    <div class="hidden lg:block px-8 py-5 border-b border-gray-200/80 bg-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-lg font-bold text-gray-900">Layanan Jasa Teknisi</h1>
          <p class="text-xs text-gray-500 mt-0.5">Kelola jadwal pemasangan baru, survei lokasi, dan servis perbaikan CCTV</p>
        </div>
        <NuxtLink to="/services/booking" class="px-5 py-2 bg-[#03AC0E] text-white text-xs font-bold rounded-lg hover:bg-[#028a0b] transition-all flex items-center gap-1.5 shadow-sm">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Booking Teknisi Baru
        </NuxtLink>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="p-4 sm:p-8">

      <!-- STATS -->
      <section v-if="data" class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Total</p>
          <p class="text-xl font-black text-gray-900">{{ data.stats.total }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Aktif</p>
          <p class="text-xl font-black text-[#03AC0E]">{{ data.stats.active }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Selesai</p>
          <p class="text-xl font-black text-gray-900">{{ data.stats.done }}</p>
        </div>
        <div class="bg-red-50 p-4 rounded-xl border border-red-100">
          <p class="text-[10px] font-bold text-red-400 uppercase tracking-widest mb-1">Tagihan</p>
          <p class="text-lg font-black text-red-600 truncate">{{ data.stats.pending_payment > 0 ? formatRupiah(data.stats.pending_payment) : 'Lunas' }}</p>
        </div>
      </section>

      <!-- STATUS TABS (Sub-tabs) -->
      <div class="flex items-center gap-6 border-b border-gray-100 mb-6 overflow-x-auto no-scrollbar pb-1 px-1 sm:px-0">
        <button 
          v-for="tab in statusTabs" 
          :key="tab.value" 
          @click="setStatus(tab.value)" 
          class="flex-shrink-0 pb-3 text-sm font-bold transition-all relative whitespace-nowrap"
          :class="currentStatus === tab.value ? 'text-[#03AC0E]' : 'text-gray-400 hover:text-gray-600'"
        >
          {{ tab.label }}
          <div v-if="currentStatus === tab.value" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#03AC0E]"></div>
        </button>
      </div>

      <!-- SEARCH -->
      <div class="relative mb-8 group">
        <input v-model="searchInput" type="text" placeholder="Cari nomor booking, kota, atau jenis layanan..." 
          class="w-full pl-12 pr-6 py-3 rounded-xl bg-gray-50 border-2 border-transparent focus:bg-white focus:border-[#03AC0E] transition-all text-sm font-bold outline-none" 
        />
        <UIcon name="i-heroicons-magnifying-glass" class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-300 group-focus-within:text-[#03AC0E]" />
      </div>

      <!-- LIST -->
      <main class="space-y-4">
        <div v-if="pending" class="space-y-4">
          <div v-for="i in 3" :key="i" class="h-40 bg-gray-50 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="!data || data.bookings.items.length === 0" class="py-24 text-center border-2 border-dashed border-gray-100 rounded-xl">
          <UIcon name="i-heroicons-calendar-days" class="w-12 h-12 text-gray-200 mx-auto mb-4" />
          <p class="text-sm font-bold text-gray-400">Belum ada data booking.</p>
        </div>

        <div v-else class="space-y-4">
          <div v-for="booking in data.bookings.items" :key="String(booking.uuid)" 
            class="bg-white border border-gray-200 rounded-xl p-6 transition-all hover:border-[#03AC0E] shadow-sm"
          >
            <div class="flex flex-col sm:flex-row items-center justify-between gap-4 mb-4 pb-4 border-b border-gray-50">
              <div class="flex items-center gap-3">
                <UIcon name="i-heroicons-wrench-screwdriver" class="w-5 h-5 text-gray-400" />
                <span class="text-xs font-bold text-gray-900 uppercase tracking-tight">Layanan Jasa</span>
                <span :class="statusBadgeClass(booking.status_color)" class="px-2 py-0.5 rounded text-[10px] font-bold border">
                  {{ booking.status_label }}
                </span>
                <span class="text-xs font-bold text-gray-300">#{{ booking.booking_number }}</span>
              </div>
            </div>

            <div class="flex flex-col md:flex-row gap-6">
              <div class="flex-1 min-w-0">
                <h4 class="text-base font-bold text-gray-900 mb-2">{{ booking.category }}</h4>
                <div class="flex flex-wrap items-center gap-x-6 gap-y-2 text-[11px] font-bold text-gray-500">
                  <div class="flex items-center gap-1.5"><UIcon name="i-heroicons-map-pin" class="w-4 h-4 text-gray-300" /> {{ booking.city }}</div>
                  <div class="flex items-center gap-1.5"><UIcon name="i-heroicons-calendar" class="w-4 h-4 text-gray-300" /> {{ booking.scheduled_label }}</div>
                  <div class="flex items-center gap-1.5"><UIcon name="i-heroicons-clock" class="w-4 h-4 text-gray-300" /> {{ booking.time_slot }}</div>
                </div>
                <div v-if="booking.addons?.length" class="mt-3 flex flex-wrap gap-2">
                  <span v-for="addon in booking.addons" :key="addon" class="px-2 py-0.5 bg-gray-50 border border-gray-100 rounded text-[9px] font-bold text-gray-400 uppercase tracking-widest">{{ addon }}</span>
                </div>
              </div>
              
              <div class="md:text-right md:border-l md:border-gray-50 md:pl-8 flex md:flex-col items-center md:items-end justify-between gap-4">
                <div>
                  <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Estimasi Biaya</p>
                  <p class="text-lg font-black text-gray-900">{{ formatRupiah(booking.total_price) }}</p>
                  <p v-if="booking.action.action === 'pay_dp'" class="text-[10px] font-bold text-amber-500 uppercase tracking-widest mt-1">DP: {{ formatRupiah(booking.dp_amount) }}</p>
                </div>
                <div class="flex items-center gap-3">
                  <NuxtLink :to="`/dashboard/orders/${booking.booking_number}`" class="text-sm font-bold text-[#03AC0E] hover:underline">Detail</NuxtLink>
                  <button v-if="booking.action.action.startsWith('pay')" @click="handlePay(booking)" :disabled="payingUuid === String(booking.uuid)"
                    class="px-6 py-2 bg-[#03AC0E] text-white text-xs font-bold rounded-lg hover:bg-[#028a0b] transition-all shadow-sm flex items-center gap-2"
                  >
                    <UIcon v-if="payingUuid === String(booking.uuid)" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                    {{ booking.action.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="data && data.bookings.total_pages > 1" class="flex items-center justify-center gap-3 pt-10">
          <button @click="currentPage--" :disabled="!data.bookings.has_prev" class="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-200 text-gray-400 hover:text-gray-900 disabled:opacity-30">
            <UIcon name="i-heroicons-chevron-left" class="w-5 h-5" />
          </button>
          <span class="text-xs font-bold text-gray-900 px-4 py-2 bg-gray-50 rounded-lg border border-gray-100">{{ currentPage }} / {{ data.bookings.total_pages }}</span>
          <button @click="currentPage++" :disabled="!data.bookings.has_next" class="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-200 text-gray-400 hover:text-gray-900 disabled:opacity-30">
            <UIcon name="i-heroicons-chevron-right" class="w-5 h-5" />
          </button>
        </div>
      </main>
    </div>

    <!-- Error Toast -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="translate-y-10 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-10 opacity-0"
    >
      <div v-if="toastError" class="fixed bottom-10 left-1/2 -translate-x-1/2 z-[100] px-6 py-3 bg-red-600 text-white text-xs font-bold rounded-xl shadow-xl uppercase tracking-widest">
        {{ toastError }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
