<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from "vue";

const route = useRoute();
const bookingNumber = route.params.number as string;

useSeoMeta({
  title: `Booking ${bookingNumber} | Padjajaran CCTV`,
  robots: "noindex",
});

const { data: booking, pending, error, refresh } = await useFetch<any>(
  `/api/proxy/services/booking/number/${bookingNumber}`,
  { key: `booking-${bookingNumber}` }
);

// ── Payment ───────────────────────────────────────────────────────
const paymentLoading = ref(false);
const paymentError = ref("");

const createAndOpenPayment = async (paymentType: "dp" | "lunas") => {
  if (!booking.value) return;
  paymentLoading.value = true;
  paymentError.value = "";

  try {
    const resp = await $fetch<any>("/api/proxy/services/payment/create", {
      method: "POST",
      body: {
        booking_uuid: booking.value.uuid,
        payment_type: paymentType,
      },
    });

    if (resp.payment_url) {
      // Buka Midtrans Snap di tab baru
      window.open(resp.payment_url, "_blank", "noopener");
      // Poll status setelah 3 detik (user sudah ke Midtrans)
      setTimeout(() => refresh(), 3000);
    } else {
      paymentError.value = "Gagal mendapatkan link pembayaran";
    }
  } catch (e: any) {
    paymentError.value =
      e?.data?.detail || e?.statusMessage || "Gagal membuat pembayaran";
  } finally {
    paymentLoading.value = false;
  }
};

// Helper untuk membuka URL eksternal dari template
const openUrl = (url: string) => {
  if (url) window.open(url, "_blank", "noopener");
};

// ── Status config ──────────────────────────────────────────────────
const STATUS_CONFIG: Record<
  string,
  {
    label: string;
    color: string;
    icon: string;
    desc: string;
    bgClass: string;
    iconClass: string;
  }
> = {
  pending: {
    label: "Menunggu Konfirmasi",
    color: "amber",
    icon: "i-heroicons-clock",
    desc: "Admin sedang memverifikasi booking Anda. Mohon tunggu konfirmasi.",
    bgClass: "bg-amber-50 border-amber-100",
    iconClass: "text-amber-500 bg-amber-100",
  },
  confirmed: {
    label: "Dikonfirmasi — Lakukan Pembayaran DP",
    color: "blue",
    icon: "i-heroicons-check-circle",
    desc:
      "Booking Anda telah dikonfirmasi. Silakan lakukan pembayaran DP untuk menjadwalkan teknisi.",
    bgClass: "bg-blue-50 border-blue-100",
    iconClass: "text-blue-500 bg-blue-100",
  },
  dp_paid: {
    label: "DP Diterima",
    color: "green",
    icon: "i-heroicons-banknotes",
    desc: "Pembayaran DP telah diterima. Teknisi akan segera dijadwalkan ke lokasi Anda.",
    bgClass: "bg-green-50 border-green-100",
    iconClass: "text-green-600 bg-green-100",
  },
  progress: {
    label: "Sedang Dikerjakan",
    color: "purple",
    icon: "i-heroicons-wrench-screwdriver",
    desc: "Teknisi kami sedang bekerja di lokasi Anda.",
    bgClass: "bg-purple-50 border-purple-100",
    iconClass: "text-purple-600 bg-purple-100",
  },
  done: {
    label: "Pekerjaan Selesai",
    color: "green",
    icon: "i-heroicons-check-badge",
    desc: "Pekerjaan selesai! Lakukan pelunasan untuk menyelesaikan transaksi.",
    bgClass: "bg-green-50 border-green-100",
    iconClass: "text-green-600 bg-green-100",
  },
  lunas: {
    label: "Lunas — Terima Kasih!",
    color: "green",
    icon: "i-heroicons-star",
    desc: "Transaksi selesai. Terima kasih telah menggunakan layanan Padjajaran CCTV.",
    bgClass: "bg-green-50 border-green-100",
    iconClass: "text-green-600 bg-green-100",
  },
  cancel: {
    label: "Dibatalkan",
    color: "red",
    icon: "i-heroicons-x-circle",
    desc: "Booking ini telah dibatalkan.",
    bgClass: "bg-red-50 border-red-100",
    iconClass: "text-red-500 bg-red-100",
  },
};

const statusInfo = computed(
  () => STATUS_CONFIG[booking.value?.status] || STATUS_CONFIG.pending
);

// Cek apakah ada payment pending yang sudah punya token
const pendingDpPayment = computed(() =>
  booking.value?.payments?.find(
    (p: any) => p.payment_type === "dp" && p.status === "pending" && p.payment_url
  )
);
const pendingLunasPayment = computed(() =>
  booking.value?.payments?.find(
    (p: any) => p.payment_type === "lunas" && p.status === "pending" && p.payment_url
  )
);

const fmt = (n: number) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  })
    .format(n)
    .replace("Rp", "Rp ");

// Auto-refresh setiap 30 detik jika status masih aktif
const shouldPoll = computed(() =>
  ["pending", "confirmed", "dp_paid", "progress"].includes(booking.value?.status)
);

let pollTimer: ReturnType<typeof setInterval>;
onMounted(() => {
  if (shouldPoll.value) {
    pollTimer = setInterval(() => refresh(), 30_000);
  }
});
onBeforeUnmount(() => clearInterval(pollTimer));
</script>

<template>
  <div class="min-h-screen bg-[#F8F9FA] font-sans py-8 px-4">
    <div class="max-w-lg mx-auto space-y-5">
      <div v-if="pending" class="flex flex-col items-center gap-4 py-24">
        <div
          class="w-8 h-8 rounded-full border-2 border-black border-t-transparent animate-spin"
        />
        <p class="text-sm font-bold text-gray-500 uppercase tracking-widest">
          Memuat status...
        </p>
      </div>

      <div v-else-if="error" class="text-center py-24">
        <UIcon
          name="i-heroicons-exclamation-triangle"
          class="w-12 h-12 text-red-500 mx-auto mb-4"
          aria-hidden="true"
        />
        <h2 class="text-lg font-black text-gray-900 mb-2">Booking Tidak Ditemukan</h2>
        <p class="text-sm text-gray-500 mb-6">
          Nomor booking tidak valid atau sudah kadaluarsa.
        </p>
        <NuxtLink to="/" class="text-sm font-bold text-black underline"
          >Kembali ke Beranda</NuxtLink
        >
      </div>

      <template v-else-if="booking">
        <div
          class="bg-white rounded-3xl border border-gray-100 shadow-xl overflow-hidden"
        >
          <div
            class="p-8 text-center border-b-2 border-dashed border-gray-200"
            :class="statusInfo.bgClass"
          >
            <div
              class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
              :class="statusInfo.iconClass"
            >
              <UIcon :name="statusInfo.icon" class="w-8 h-8" aria-hidden="true" />
            </div>
            <h1 class="text-xl font-black text-gray-900 uppercase tracking-tight mb-2">
              {{ statusInfo.label }}
            </h1>
            <p class="text-sm text-gray-600 font-medium leading-relaxed">
              {{ statusInfo.desc }}
            </p>
            <div
              class="mt-4 inline-block bg-white/70 backdrop-blur px-4 py-2 rounded-xl border border-gray-200"
            >
              <p class="text-xs font-black uppercase tracking-widest text-gray-700">
                {{ booking.booking_number }}
              </p>
            </div>
          </div>

          <div class="p-6 space-y-3">
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div class="bg-gray-50 rounded-xl p-3">
                <p
                  class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1"
                >
                  Layanan
                </p>
                <p class="font-black text-black capitalize">{{ booking.category }}</p>
              </div>
              <div class="bg-gray-50 rounded-xl p-3">
                <p
                  class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1"
                >
                  Kamera
                </p>
                <p class="font-black text-black">{{ booking.camera_count }} titik</p>
              </div>
              <div class="bg-gray-50 rounded-xl p-3">
                <p
                  class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1"
                >
                  Brand
                </p>
                <p class="font-black text-black capitalize">{{ booking.brand }}</p>
              </div>
              <div class="bg-gray-50 rounded-xl p-3">
                <p
                  class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1"
                >
                  Lokasi
                </p>
                <p class="font-black text-black">{{ booking.city }}</p>
              </div>
            </div>

            <div class="bg-gray-50 rounded-xl p-3 text-sm">
              <p
                class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1"
              >
                Jadwal
              </p>
              <p class="font-black text-black">
                {{ booking.scheduled_date }} · {{ booking.time_slot }}
              </p>
            </div>
          </div>

          <div class="mx-6 mb-6 bg-black text-white rounded-2xl p-5">
            <div class="space-y-2 text-sm mb-4">
              <div class="flex justify-between text-gray-300">
                <span>Biaya Jasa</span>
                <span class="text-white font-bold">{{ fmt(booking.service_price) }}</span>
              </div>
              <div v-if="booking.addon_price" class="flex justify-between text-gray-300">
                <span>Addon</span>
                <span class="text-white font-bold">{{ fmt(booking.addon_price) }}</span>
              </div>
              <div
                v-if="booking.transport_fee"
                class="flex justify-between text-gray-300"
              >
                <span>Transport</span>
                <span class="text-white font-bold">{{ fmt(booking.transport_fee) }}</span>
              </div>
            </div>
            <div class="border-t border-gray-700 pt-3 space-y-2">
              <div class="flex justify-between items-center">
                <span
                  class="text-[10px] font-bold uppercase tracking-widest text-gray-400"
                  >Total</span
                >
                <span class="text-2xl font-black">{{ fmt(booking.total_price) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-400">DP {{ booking.dp_percentage }}%</span>
                <span class="text-green-400 font-black">{{
                  fmt(booking.dp_amount)
                }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-400">Sisa {{ 100 - booking.dp_percentage }}%</span>
                <span class="text-yellow-400 font-black">{{
                  fmt(booking.remaining_amount)
                }}</span>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="paymentError"
          role="alert"
          class="p-4 bg-red-50 border border-red-100 rounded-xl flex items-start gap-3"
        >
          <UIcon
            name="i-heroicons-exclamation-circle"
            class="w-5 h-5 text-red-500 flex-shrink-0"
            aria-hidden="true"
          />
          <p class="text-sm font-semibold text-red-700">{{ paymentError }}</p>
        </div>

        <div
          v-if="booking.status === 'confirmed'"
          class="bg-white rounded-2xl border border-blue-200 p-5 shadow-sm"
        >
          <div class="flex items-center gap-3 mb-4">
            <div
              class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center"
            >
              <UIcon
                name="i-heroicons-banknotes"
                class="w-5 h-5 text-blue-600"
                aria-hidden="true"
              />
            </div>
            <div>
              <h3 class="text-sm font-black uppercase tracking-widest text-black">
                Bayar DP
              </h3>
              <p class="text-[10px] font-semibold text-gray-500">
                {{ booking.dp_percentage }}% dari total
              </p>
            </div>
          </div>

          <div v-if="pendingDpPayment" class="space-y-3">
            <div
              class="flex items-center gap-2 p-3 bg-amber-50 border border-amber-100 rounded-xl"
            >
              <UIcon
                name="i-heroicons-clock"
                class="w-4 h-4 text-amber-500"
                aria-hidden="true"
              />
              <p class="text-xs font-semibold text-amber-700">
                Transaksi DP sudah dibuat. Selesaikan pembayaran.
              </p>
            </div>
            <button
              class="w-full bg-blue-600 text-white py-4 rounded-xl text-sm font-black uppercase tracking-widest hover:bg-blue-700 transition-colors"
              @click="openUrl(pendingDpPayment.payment_url)"
            >
              Lanjutkan Bayar DP {{ fmt(booking.dp_amount) }}
            </button>
          </div>

          <div v-else class="space-y-3">
            <div class="flex justify-between text-sm p-3 bg-gray-50 rounded-xl">
              <span class="text-gray-500 font-medium">Jumlah DP</span>
              <span class="font-black text-black text-lg">{{
                fmt(booking.dp_amount)
              }}</span>
            </div>
            <button
              :disabled="paymentLoading"
              class="w-full bg-black text-white py-4 rounded-xl text-sm font-black uppercase tracking-widest hover:bg-gray-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              @click="createAndOpenPayment('dp')"
            >
              <UIcon
                v-if="paymentLoading"
                name="i-heroicons-arrow-path"
                class="w-4 h-4 animate-spin"
                aria-hidden="true"
              />
              <span>{{
                paymentLoading ? "Menyiapkan..." : `Bayar DP ${fmt(booking.dp_amount)}`
              }}</span>
            </button>
            <p class="text-[10px] text-center text-gray-400 font-semibold">
              Pembayaran via Midtrans · Transfer Bank, QRIS, GoPay, dll
            </p>
          </div>
        </div>

        <div
          v-if="booking.status === 'done'"
          class="bg-white rounded-2xl border border-green-200 p-5 shadow-sm"
        >
          <div class="flex items-center gap-3 mb-4">
            <div
              class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center"
            >
              <UIcon
                name="i-heroicons-check-badge"
                class="w-5 h-5 text-green-600"
                aria-hidden="true"
              />
            </div>
            <div>
              <h3 class="text-sm font-black uppercase tracking-widest text-black">
                Pelunasan
              </h3>
              <p class="text-[10px] font-semibold text-gray-500">
                Pekerjaan selesai · sisa {{ 100 - booking.dp_percentage }}%
              </p>
            </div>
          </div>

          <div v-if="pendingLunasPayment" class="space-y-3">
            <div
              class="flex items-center gap-2 p-3 bg-amber-50 border border-amber-100 rounded-xl"
            >
              <UIcon
                name="i-heroicons-clock"
                class="w-4 h-4 text-amber-500"
                aria-hidden="true"
              />
              <p class="text-xs font-semibold text-amber-700">
                Transaksi pelunasan sudah dibuat.
              </p>
            </div>
            <button
              class="w-full bg-green-600 text-white py-4 rounded-xl text-sm font-black uppercase tracking-widest hover:bg-green-700 transition-colors"
              @click="openUrl(pendingLunasPayment.payment_url)"
            >
              Lanjutkan Bayar Pelunasan {{ fmt(booking.remaining_amount) }}
            </button>
          </div>

          <div v-else class="space-y-3">
            <div class="flex justify-between text-sm p-3 bg-gray-50 rounded-xl">
              <span class="text-gray-500 font-medium">Sisa Pembayaran</span>
              <span class="font-black text-black text-lg">{{
                fmt(booking.remaining_amount)
              }}</span>
            </div>
            <button
              :disabled="paymentLoading"
              class="w-full bg-green-600 text-white py-4 rounded-xl text-sm font-black uppercase tracking-widest hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              @click="createAndOpenPayment('lunas')"
            >
              <UIcon
                v-if="paymentLoading"
                name="i-heroicons-arrow-path"
                class="w-4 h-4 animate-spin"
                aria-hidden="true"
              />
              <span>{{
                paymentLoading
                  ? "Menyiapkan..."
                  : `Bayar Pelunasan ${fmt(booking.remaining_amount)}`
              }}</span>
            </button>
          </div>
        </div>

        <div
          v-if="booking.payments?.length"
          class="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm"
        >
          <h3 class="text-xs font-black uppercase tracking-widest text-gray-500 mb-4">
            Riwayat Pembayaran
          </h3>
          <div class="space-y-3">
            <div
              v-for="pay in booking.payments"
              :key="pay.uuid"
              class="flex items-center justify-between p-3 rounded-xl"
              :class="{
                'bg-green-50': pay.status === 'success',
                'bg-amber-50': pay.status === 'pending',
                'bg-red-50': ['failed', 'cancel', 'expire'].includes(pay.status),
              }"
            >
              <div class="flex items-center gap-3">
                <UIcon
                  :name="
                    pay.status === 'success'
                      ? 'i-heroicons-check-circle'
                      : pay.status === 'pending'
                      ? 'i-heroicons-clock'
                      : 'i-heroicons-x-circle'
                  "
                  class="w-5 h-5 flex-shrink-0"
                  :class="{
                    'text-green-600': pay.status === 'success',
                    'text-amber-500': pay.status === 'pending',
                    'text-red-500': ['failed', 'cancel', 'expire'].includes(pay.status),
                  }"
                  aria-hidden="true"
                />
                <div>
                  <p class="text-xs font-black uppercase tracking-widest text-gray-800">
                    {{ pay.payment_type === "dp" ? "DP" : "Pelunasan" }}
                  </p>
                  <p class="text-[10px] text-gray-500 font-semibold">
                    {{ pay.order_id }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-black text-black">{{ fmt(pay.gross_amount) }}</p>
                <p
                  class="text-[10px] font-bold uppercase"
                  :class="{
                    'text-green-600': pay.status === 'success',
                    'text-amber-500': pay.status === 'pending',
                    'text-red-500': ['failed', 'cancel', 'expire'].includes(pay.status),
                  }"
                >
                  {{ pay.status }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <button
            class="w-full bg-white border border-gray-200 text-gray-700 py-3.5 rounded-xl text-sm font-bold uppercase tracking-widest hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            @click="refresh()"
          >
            <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" aria-hidden="true" />
            Refresh Status
          </button>
          <NuxtLink
            to="/"
            class="w-full text-center text-sm font-bold text-gray-500 py-3 hover:text-black transition-colors"
          >
            Kembali ke Beranda
          </NuxtLink>
        </div>
      </template>
    </div>
  </div>
</template>
