<template>
  <div
    class="min-h-screen bg-[#F3F4F5] font-[Plus_Jakarta_Sans,sans-serif] pb-24 md:pb-12 text-gray-800"
  >
    <Head>
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
        rel="stylesheet"
      />
      <title>{{ booking?.booking_number ?? "Detail Transaksi" }} — Padjajaran CCTV</title>
    </Head>

    <div class="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
      <div class="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink
            to="/dashboard/jasa"
            class="p-2 -ml-2 hover:bg-gray-100 rounded-full transition-colors text-gray-600"
          >
            <Icon name="lucide:arrow-left" class="text-xl" />
          </NuxtLink>
          <h1 class="font-bold text-lg text-gray-900 tracking-tight">Detail Transaksi</h1>
        </div>
        <NuxtLink
          to="/dashboard/jasa"
          class="text-sm font-semibold text-[#00AA5B] hover:text-[#008c4a]"
        >
          Daftar Booking
        </NuxtLink>
      </div>
    </div>

    <div v-if="pending" class="max-w-5xl mx-auto px-4 py-6 space-y-4">
      <div class="h-32 bg-white animate-pulse rounded-xl" />
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-4">
          <div class="h-64 bg-white animate-pulse rounded-xl" />
          <div class="h-48 bg-white animate-pulse rounded-xl" />
        </div>
        <div class="h-96 bg-white animate-pulse rounded-xl" />
      </div>
    </div>

    <div v-else-if="error" class="max-w-xl mx-auto px-4 py-24 text-center">
      <Icon name="lucide:search-x" class="text-6xl text-gray-300 mb-4 mx-auto" />
      <h2 class="text-xl font-bold text-gray-900 mb-2">Transaksi Tidak Ditemukan</h2>
      <p class="text-sm text-gray-500 mb-6">
        Pastikan link atau ID transaksi yang Anda masukkan benar.
      </p>
      <NuxtLink
        to="/dashboard/jasa"
        class="px-6 py-2.5 bg-[#00AA5B] text-white rounded-lg font-bold hover:bg-[#008c4a] transition-colors"
      >
        Kembali ke Daftar Transaksi
      </NuxtLink>
    </div>

    <div v-else-if="booking" class="max-w-5xl mx-auto px-4 sm:px-6 py-6">
      <div
        class="bg-white p-4 sm:p-6 rounded-xl shadow-[0_1px_6px_rgba(0,0,0,0.05)] border border-gray-100 mb-6"
      >
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <p class="text-xs font-semibold text-gray-500 mb-1">
              Nomor Invoice •
              <span class="font-mono text-[#00AA5B]">{{ booking.booking_number }}</span>
            </p>
            <div class="flex items-center gap-3">
              <h2 class="text-2xl font-extrabold text-gray-900">
                {{ statusStyle.label }}
              </h2>
              <span
                :class="[
                  'px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider',
                  statusStyle.badge,
                ]"
              >
                {{ booking.status }}
              </span>
            </div>
            <p class="text-xs text-gray-400 mt-2">
              Tanggal Pembelian: {{ formatDateTime(booking.created_at) }}
            </p>
          </div>

          <a
            :href="`https://wa.me/6282218828108?text=Halo Admin Padjajaran CCTV, saya butuh bantuan untuk transaksi ${booking.booking_number}`"
            target="_blank"
            class="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-white border border-gray-300 rounded-lg text-sm font-bold text-gray-700 hover:bg-gray-50 hover:border-[#00AA5B] hover:text-[#00AA5B] transition-all"
          >
            <Icon name="logos:whatsapp-icon" class="text-lg" />
            Tanya CS
          </a>
        </div>
      </div>

      <div
        class="bg-white p-6 rounded-xl shadow-[0_1px_6px_rgba(0,0,0,0.05)] border border-gray-100 mb-6 overflow-x-auto no-scrollbar"
      >
        <div class="min-w-[600px] py-4 relative">
          <div class="flex items-start justify-between w-full">
            <template v-for="(step, i) in statusSteps" :key="step.key">
              <div class="relative flex flex-col items-center flex-1">
                <div
                  v-if="i !== statusSteps.length - 1"
                  class="absolute top-5 left-[50%] w-full h-[3px] -z-10 transition-colors duration-500"
                  :class="step.done ? 'bg-[#00AA5B]' : 'bg-gray-200'"
                ></div>

                <div
                  :class="[
                    'w-10 h-10 rounded-full border-[3px] bg-white flex items-center justify-center transition-all duration-300 z-10',
                    step.done || step.active
                      ? 'border-[#00AA5B] text-[#00AA5B]'
                      : 'border-gray-200 text-gray-300',
                  ]"
                >
                  <Icon :name="step.icon" class="text-xl" />
                </div>

                <div class="text-center mt-3 absolute top-12 w-28 -ml-14 left-1/2">
                  <p
                    :class="[
                      'text-[11px] sm:text-xs font-bold leading-tight',
                      step.done || step.active ? 'text-gray-800' : 'text-gray-400',
                    ]"
                  >
                    {{ step.label }}
                  </p>
                  <p
                    v-if="step.date && (step.done || step.active)"
                    class="text-[10px] text-gray-400 mt-1"
                  >
                    {{ step.date }}
                  </p>
                </div>
              </div>
            </template>
          </div>
          <div class="h-10"></div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div
            class="bg-white rounded-xl shadow-[0_1px_6px_rgba(0,0,0,0.05)] border border-gray-100 overflow-hidden"
          >
            <div
              class="px-6 py-4 border-b border-gray-100 bg-white flex justify-between items-center"
            >
              <h3 class="font-bold text-gray-900">Detail Layanan Jasa</h3>
            </div>

            <div class="p-6">
              <div class="flex items-start gap-4">
                <div
                  class="w-16 h-16 rounded-lg bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 flex-shrink-0"
                >
                  <Icon name="lucide:cctv" class="text-3xl text-[#00AA5B]" />
                </div>

                <div class="flex-1">
                  <h4 class="font-bold text-base text-gray-900 mb-1">
                    {{ CATEGORY_LABELS[booking.category] || booking.category }} ({{
                      booking.camera_count
                    }}
                    Titik)
                  </h4>
                  <p class="text-sm text-gray-500 mb-2">Perangkat: {{ booking.brand }}</p>
                  <div class="flex justify-between items-end">
                    <p
                      class="text-xs font-semibold text-gray-500 bg-gray-100 px-2.5 py-1 rounded"
                    >
                      Jarak: {{ booking.distance_km }} km
                    </p>
                    <p class="font-bold text-lg text-gray-900">
                      {{ formatRp(booking.total_price) }}
                    </p>
                  </div>
                </div>
              </div>

              <div
                v-if="booking.addons?.length"
                class="mt-5 pt-5 border-t border-dashed border-gray-200"
              >
                <p class="text-xs font-bold text-gray-900 mb-2">
                  Layanan Tambahan (Add-on)
                </p>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="addon in booking.addons"
                    :key="addon"
                    class="px-3 py-1 bg-green-50 text-[#00AA5B] rounded-md text-xs font-semibold border border-green-100"
                  >
                    {{ addon }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div
            class="bg-white rounded-xl shadow-[0_1px_6px_rgba(0,0,0,0.05)] border border-gray-100"
          >
            <div class="px-6 py-4 border-b border-gray-100">
              <h3 class="font-bold text-gray-900">Info Pemasangan & Kontak</h3>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div class="flex gap-3">
                  <Icon
                    name="lucide:calendar-clock"
                    class="text-xl text-gray-400 flex-shrink-0"
                  />
                  <div>
                    <p class="text-xs text-gray-500 mb-0.5">Jadwal Kunjungan</p>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ formatDate(booking.scheduled_date) }}
                    </p>
                    <p class="text-xs text-gray-600">{{ slotLabel }}</p>
                  </div>
                </div>
                <div class="flex gap-3">
                  <Icon
                    name="lucide:map-pin"
                    class="text-xl text-gray-400 flex-shrink-0"
                  />
                  <div>
                    <p class="text-xs text-gray-500 mb-0.5">Alamat Lokasi</p>
                    <p class="text-sm font-semibold text-gray-900 leading-relaxed">
                      {{ booking.address }}
                    </p>
                    <p class="text-xs text-gray-600">{{ booking.city }}</p>
                  </div>
                </div>
              </div>

              <div class="bg-gray-50 rounded-lg p-4 border border-gray-100">
                <p class="text-xs text-gray-500 mb-2">Detail Kontak Pelanggan</p>
                <div class="flex items-center gap-3 mb-2">
                  <div
                    class="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center"
                  >
                    <Icon name="lucide:user" class="text-gray-500" />
                  </div>
                  <div>
                    <p class="text-sm font-bold text-gray-900">
                      {{ booking.contact_name }}
                    </p>
                    <p class="text-xs font-mono text-gray-600">
                      {{ booking.contact_phone }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="booking.payments?.length"
            class="bg-white rounded-xl shadow-[0_1px_6px_rgba(0,0,0,0.05)] border border-gray-100"
          >
            <div class="px-6 py-4 border-b border-gray-100">
              <h3 class="font-bold text-gray-900">Riwayat Transaksi</h3>
            </div>
            <div class="p-2">
              <div
                v-for="pay in booking.payments"
                :key="pay.uuid"
                class="flex flex-col sm:flex-row sm:items-center justify-between p-4 hover:bg-gray-50 rounded-lg transition-colors border-b border-gray-50 last:border-0"
              >
                <div class="flex items-center gap-4 mb-3 sm:mb-0">
                  <div
                    class="w-10 h-10 rounded-full bg-[#E5F9F1] flex items-center justify-center text-[#00AA5B]"
                  >
                    <Icon name="lucide:receipt" class="text-lg" />
                  </div>
                  <div>
                    <p class="text-sm font-bold text-gray-900">
                      {{
                        pay.payment_type === "dp"
                          ? `DP (${booking.dp_percentage}%)`
                          : "Pelunasan Akhir"
                      }}
                    </p>
                    <p class="text-[11px] text-gray-500 font-mono">{{ pay.order_id }}</p>
                  </div>
                </div>
                <div class="text-left sm:text-right flex items-center sm:block gap-4">
                  <p class="text-sm font-extrabold text-gray-900 mb-1">
                    {{ formatRp(pay.gross_amount) }}
                  </p>
                  <span
                    :class="[
                      'text-[10px] font-bold px-2 py-0.5 rounded uppercase',
                      payStatusStyle(pay.status).badge,
                    ]"
                  >
                    {{ payStatusStyle(pay.status).label }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="lg:col-span-1">
          <div
            class="sticky top-20 bg-white rounded-xl shadow-[0_1px_6px_rgba(0,0,0,0.05)] border border-gray-100 overflow-hidden"
          >
            <div class="px-6 py-4 border-b border-gray-100">
              <h3 class="font-bold text-gray-900">Ringkasan Pembayaran</h3>
            </div>

            <div class="p-6 space-y-3">
              <div v-if="booking.device_price > 0" class="flex justify-between text-sm">
                <span class="text-gray-600">Total Perangkat</span>
                <span class="font-semibold text-gray-900">{{
                  formatRp(booking.device_price)
                }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Biaya Jasa Pemasangan</span>
                <span class="font-semibold text-gray-900">{{
                  formatRp(booking.service_price)
                }}</span>
              </div>
              <div v-if="booking.addon_price > 0" class="flex justify-between text-sm">
                <span class="text-gray-600">Layanan Tambahan</span>
                <span class="font-semibold text-gray-900">{{
                  formatRp(booking.addon_price)
                }}</span>
              </div>
              <div v-if="booking.transport_fee > 0" class="flex justify-between text-sm">
                <span class="text-gray-600">Ongkos Transport</span>
                <span class="font-semibold text-gray-900">{{
                  formatRp(booking.transport_fee)
                }}</span>
              </div>

              <div class="border-t border-gray-200 pt-4 mt-4">
                <div class="flex justify-between items-end mb-2">
                  <span class="font-bold text-gray-900">Total Tagihan</span>
                  <span class="text-lg font-extrabold text-[#00AA5B]">{{
                    formatRp(booking.total_price)
                  }}</span>
                </div>
              </div>

              <div
                class="bg-gray-50 rounded-lg p-3 space-y-2 mt-4 border border-gray-100"
              >
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Uang Muka (DP)</span>
                  <span class="font-bold text-gray-900">
                    {{ formatRp(booking.dp_amount) }}
                    <Icon
                      v-if="isDpPaid"
                      name="lucide:check-circle-2"
                      class="text-[#00AA5B] inline-block ml-1"
                    />
                  </span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Sisa Pembayaran</span>
                  <span class="font-bold text-gray-900">
                    {{ formatRp(booking.remaining_amount) }}
                    <Icon
                      v-if="isFullyPaid"
                      name="lucide:check-circle-2"
                      class="text-[#00AA5B] inline-block ml-1"
                    />
                  </span>
                </div>
              </div>
            </div>

            <div class="p-6 bg-white border-t border-gray-100">
              <div v-if="canPayDp">
                <button
                  @click="payNow('dp')"
                  :disabled="payLoading"
                  class="w-full py-3 bg-[#00AA5B] hover:bg-[#008c4a] text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Icon
                    v-if="payLoading"
                    name="lucide:loader-2"
                    class="animate-spin text-xl"
                  />
                  <span>Bayar DP Sekarang</span>
                </button>
              </div>

              <div v-else-if="canPayLunas">
                <button
                  @click="payNow('lunas')"
                  :disabled="payLoading"
                  class="w-full py-3 bg-[#00AA5B] hover:bg-[#008c4a] text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Icon
                    v-if="payLoading"
                    name="lucide:loader-2"
                    class="animate-spin text-xl"
                  />
                  <span>Lunasi Sekarang</span>
                </button>
              </div>

              <div
                v-else-if="isFullyPaid"
                class="bg-[#E5F9F1] border border-[#00AA5B]/30 rounded-lg p-4 flex flex-col items-center text-center"
              >
                <div
                  class="w-10 h-10 bg-[#00AA5B] text-white rounded-full flex items-center justify-center mb-2"
                >
                  <Icon name="lucide:check" class="text-2xl font-bold" />
                </div>
                <p class="font-bold text-[#008c4a]">Transaksi Selesai & Lunas</p>
                <p class="text-xs text-green-700 mt-1">
                  Terima kasih telah berbelanja di Padjajaran CCTV.
                </p>
              </div>

              <div
                v-else-if="booking.status === 'cancel'"
                class="bg-red-50 border border-red-200 rounded-lg p-4 text-center"
              >
                <Icon name="lucide:x-circle" class="text-red-500 text-3xl mx-auto mb-1" />
                <p class="font-bold text-red-700">Transaksi Dibatalkan</p>
              </div>

              <div v-else class="text-center py-2">
                <p
                  class="text-sm font-semibold text-gray-500 flex items-center justify-center gap-2"
                >
                  <Icon name="lucide:clock" /> Menunggu Konfirmasi Admin
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Transition name="toast">
      <div
        v-if="toast.show"
        :class="[
          'fixed bottom-8 left-1/2 -translate-x-1/2 z-[100] px-5 py-3 rounded-lg text-sm font-semibold text-white shadow-lg flex items-center gap-3 min-w-[280px]',
          toast.type === 'success' ? 'bg-[#00AA5B]' : 'bg-red-500',
        ]"
      >
        <Icon
          :name="
            toast.type === 'success' ? 'lucide:check-circle-2' : 'lucide:alert-circle'
          "
          class="text-xl"
        />
        <span class="flex-1">{{ toast.message }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

definePageMeta({ layout: "public" });

interface PaymentInfo {
  uuid: string;
  order_id: string;
  payment_type: string;
  gross_amount: number;
  status: string;
}

interface Booking {
  uuid: string;
  booking_number: string;
  category: string;
  camera_count: number;
  brand: string;
  addons: string[];
  scheduled_date: string;
  time_slot: string;
  address: string;
  city: string;
  distance_km: number;
  contact_name: string;
  contact_phone: string;
  device_price: number;
  service_price: number;
  addon_price: number;
  transport_fee: number;
  total_price: number;
  dp_percentage: number;
  dp_amount: number;
  remaining_amount: number;
  status: string;
  payments: PaymentInfo[];
  created_at: string;
}

const route = useRoute();
const id = route.params.id as string;

const { data: booking, pending, error, refresh } = await useAsyncData<Booking>(
  `jasa-${id}`,
  () => $fetch(`/api/jasa/${id}`)
);

const payLoading = ref(false);
const toast = ref({ show: false, message: "", type: "success" as "success" | "error" });

const SLOT_LABELS: Record<string, string> = {
  "08:00-11:00": "08:00 - 11:00 WIB",
  "11:00-14:00": "11:00 - 14:00 WIB",
  "14:00-17:00": "14:00 - 17:00 WIB",
};

const CATEGORY_LABELS: Record<string, string> = {
  installation: "Pemasangan Baru",
  maintenance: "Maintenance",
  consultation: "Konsultasi Cek Lokasi",
  troubleshoot: "Perbaikan",
};

type StatusKey =
  | "pending"
  | "confirmed"
  | "dp_paid"
  | "progress"
  | "done"
  | "lunas"
  | "cancel";

// Styling untuk Banner Status di atas
const STATUS_CONFIG: Record<StatusKey, { label: string; badge: string }> = {
  pending: { label: "Menunggu Konfirmasi", badge: "bg-yellow-100 text-yellow-800" },
  confirmed: { label: "Menunggu Pembayaran DP", badge: "bg-orange-100 text-orange-800" },
  dp_paid: { label: "Pembayaran DP Berhasil", badge: "bg-blue-100 text-blue-800" },
  progress: { label: "Sedang Dalam Pengerjaan", badge: "bg-purple-100 text-purple-800" },
  done: { label: "Pekerjaan Selesai", badge: "bg-teal-100 text-teal-800" },
  lunas: { label: "Transaksi Selesai", badge: "bg-green-100 text-green-800" },
  cancel: { label: "Transaksi Dibatalkan", badge: "bg-red-100 text-red-800" },
};

const statusStyle = computed(
  () => STATUS_CONFIG[booking.value?.status as StatusKey] || STATUS_CONFIG.pending
);

// Konfigurasi Horizontal Stepper persis seperti Tokopedia
const TIMELINE = [
  { key: "pending", label: "Pesanan Dibuat", icon: "lucide:file-text" },
  { key: "confirmed", label: "Dikonfirmasi", icon: "lucide:package" },
  { key: "dp_paid", label: "DP Dibayar", icon: "lucide:wallet" },
  { key: "progress", label: "Pengerjaan", icon: "lucide:wrench" },
  { key: "done", label: "Selesai", icon: "lucide:check-circle" },
  { key: "lunas", label: "Lunas", icon: "lucide:receipt" },
];

const statusSteps = computed(() => {
  const current = booking.value?.status || "pending";
  const order = ["pending", "confirmed", "dp_paid", "progress", "done", "lunas"];
  const currentIdx = order.indexOf(current);

  return TIMELINE.map((step, i) => {
    // Menyematkan tanggal pada step yang sudah dilewati (mocking dengan created_at untuk contoh tampilan)
    let dateStr = "";
    if (i === 0 && booking.value?.created_at) {
      dateStr = formatSimpleDate(booking.value.created_at);
    }
    return {
      ...step,
      done: i < currentIdx,
      active: i === currentIdx,
      date: dateStr,
    };
  });
});

const isDpPaid = computed(() =>
  ["dp_paid", "progress", "done", "lunas"].includes(booking.value?.status || "")
);
const isFullyPaid = computed(() => booking.value?.status === "lunas");
const canPayDp = computed(() => booking.value?.status === "confirmed");
const canPayLunas = computed(() => booking.value?.status === "done");

const slotLabel = computed(
  () => SLOT_LABELS[booking.value?.time_slot || ""] || booking.value?.time_slot
);

function payStatusStyle(status: string) {
  const map: Record<string, any> = {
    success: { label: "Berhasil", badge: "bg-[#E5F9F1] text-[#00AA5B]" },
    pending: { label: "Menunggu", badge: "bg-yellow-50 text-yellow-700" },
    failed: { label: "Gagal", badge: "bg-red-50 text-red-700" },
  };
  return map[status] || map.pending;
}

async function payNow(type: "dp" | "lunas") {
  if (!booking.value) return;
  payLoading.value = true;
  try {
    const res = await $fetch<any>(
      `/api/jasa/${booking.value.uuid}/pay?payment_type=${type}`,
      { method: "POST" }
    );
    if (res.payment_token && (window as any).snap) {
      (window as any).snap.pay(res.payment_token, {
        onSuccess: async () => {
          showToast("Pembayaran berhasil!", "success");
          await refresh();
        },
        onPending: () => {
          showToast("Menunggu pembayaran...", "success");
          refresh();
        },
        onClose: () => showToast("Halaman pembayaran ditutup", "error"),
      });
    } else if (res.payment_url) {
      window.open(res.payment_url, "_blank");
    }
  } catch (e: any) {
    showToast(e?.data?.detail || "Gagal membuat pembayaran", "error");
  } finally {
    payLoading.value = false;
  }
}

// Helpers Formatter
function formatRp(n: number) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(n);
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("id-ID", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function formatSimpleDate(iso: string) {
  return new Date(iso)
    .toLocaleString("id-ID", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
    .replace(".", ":");
}

function formatDateTime(iso: string) {
  return (
    new Date(iso).toLocaleString("id-ID", {
      day: "numeric",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }) + " WIB"
  );
}

function showToast(message: string, type: "success" | "error") {
  toast.value = { show: true, message, type };
  setTimeout(() => {
    toast.value.show = false;
  }, 4000);
}
</script>

<style scoped>
/* Transisi Smooth Notification */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.toast-enter-from {
  opacity: 0;
  transform: translate(-50%, 20px);
}
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px) scale(0.95);
}

/* Hide Scrollbar for Horizontal Stepper */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
</style>
