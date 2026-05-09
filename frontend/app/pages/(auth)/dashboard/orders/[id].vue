<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

definePageMeta({ layout: 'public' })

// ─── Midtrans Snap ────────────────────────────────────────
useHead({
  script: [
    {
      src: 'https://app.sandbox.midtrans.com/snap/snap.js',
      'data-client-key': 'SB-Mid-client-pn3mYe4w4xeY6F0w',
      async: true,
    },
  ],
})

const route    = useRoute()
const orderId  = route.params.id as string

const API_BASE = 'http://127.0.0.1:8000/transaksi'
const getToken = () => useCookie('token').value

// ─── State ────────────────────────────────────────────────
const order     = ref<any>(null)
const isLoading = ref(true)
const isRepaying = ref(false)

// ─── Fetch Detail ─────────────────────────────────────────
const fetchOrderDetail = async () => {
  isLoading.value = true
  try {
    const response: any = await $fetch(`${API_BASE}/detail/${orderId}`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    order.value = response
  } catch (err: any) {
    console.error('Gagal mengambil detail transaksi:', err)
    order.value = null
  } finally {
    isLoading.value = false
  }
}

onMounted(() => fetchOrderDetail())

// ─── Stepper Logic ────────────────────────────────────────
/**
 * stepIndex:
 *  -1 = dibatalkan
 *   0 = pending (belum bayar)
 *   1 = processing (sudah bayar, dikemas)
 *   2 = shipped (dikirim)
 *   3 = completed / selesai
 */
const stepIndex = computed<number>(() => {
  if (!order.value) return 0
  const tStatus = (order.value.transaction_status || '').toLowerCase()
  const sStatus = (order.value.shipment?.delivery_status || '').toLowerCase()

  if (['cancel', 'expire', 'deny'].includes(tStatus)) return -1
  if (['pending', 'pending_payment'].includes(tStatus)) return 0

  if (['settlement', 'success', 'capture'].includes(tStatus)) {
    if (['delivered', 'completed'].includes(sStatus)) return 3
    if (sStatus === 'shipped') return 2
    return 1 // processing / PROCESSING / null
  }
  return 0
})

const steps = [
  { id: 'created',    label: 'Pesanan Dibuat',  icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { id: 'processing', label: 'Sedang Dikemas',  icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' },
  { id: 'shipped',    label: 'Dikirim',          icon: 'M8 7h12m0 0l3 5v6H8m12-11V7m-5 5h5m-5 0v3m0-3l-3-5m-7 5v6H3V7h5m0 5h5m-5 0v3m0-3l-3-5' },
  { id: 'completed',  label: 'Selesai',          icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
]

// ─── Utilities ────────────────────────────────────────────
const formatRupiah = (angka: number) =>
  new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(angka || 0)

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('id-ID', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  }).format(date)
}

const isPromo    = computed(() => order.value?.trx_type === 'promo')
const isPending  = computed(() => stepIndex.value === 0)
const isCanceled = computed(() => stepIndex.value === -1)

/** Label item name — handle reguler (item_name) & promo (item_name) */
const getItemName = (item: any) => item.item_name || item.stock_title || '-'

/** Cover image — field sama antara reguler & promo */
const getItemCover = (item: any) => item.cover_image_url || null

/** Progress bar width untuk stepper */
const progressWidth = computed(() => {
  if (stepIndex.value <= 0) return '0%'
  return `${(stepIndex.value / (steps.length - 1)) * 80}%`
})

// ─── Repay via endpoint /repay/:orderId ───────────────────
/**
 * Coba pakai snap_token yang sudah ada di order.
 * Jika tidak ada / sudah expire, call /repay dulu untuk dapat token baru.
 */
const payOrder = async () => {
  const existingToken = order.value?.snap_token || order.value?.raw_response?.token

  if (existingToken) {
    openSnap(existingToken)
    return
  }

  // Tidak ada token → minta token baru via /repay
  isRepaying.value = true
  try {
    const res: any = await $fetch(`${API_BASE}/repay/${orderId}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (res?.snap_token) {
      openSnap(res.snap_token)
    } else {
      alert('Gagal mendapatkan token pembayaran. Silakan coba lagi.')
    }
  } catch (err: any) {
    const msg = err?.data?.detail || 'Gagal memuat pembayaran. Silakan coba lagi.'
    alert(msg)
  } finally {
    isRepaying.value = false
  }
}

const openSnap = (token: string) => {
  const snapObj = (window as any).snap
  if (!snapObj) {
    alert('Modul pembayaran belum siap. Muat ulang halaman dan coba lagi.')
    return
  }
  snapObj.pay(token, {
    onSuccess: () => { fetchOrderDetail() },
    onPending: () => { fetchOrderDetail() },
    onError:   () => { alert('Pembayaran gagal, silakan coba lagi.') },
    onClose:   () => { /* user tutup popup */ },
  })
}

// ─── Booking Info (khusus promo dengan service) ───────────
const hasBooking = computed(() => !!order.value?.booking)
</script>

<template>
  <div class="min-h-screen bg-[#f3f4f5] py-8">
    <div class="container mx-auto px-4 max-w-[1200px] flex flex-col lg:flex-row gap-6">

      <AccountSidebar />

      <main class="flex-1 w-full max-w-full overflow-hidden">

        <!-- Back -->
        <button
          @click="$router.push('/dashboard/orders')"
          class="flex items-center gap-2 text-gray-500 hover:text-[#03AC0E] font-semibold text-sm mb-6 transition-colors w-fit"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          KEMBALI KE DAFTAR TRANSAKSI
        </button>

        <!-- Skeleton -->
        <div v-if="isLoading" class="space-y-6">
          <div class="h-44 bg-white rounded-xl border border-gray-200 animate-pulse shadow-sm" />
          <div class="h-64 bg-white rounded-xl border border-gray-200 animate-pulse shadow-sm" />
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="h-48 bg-white rounded-xl border border-gray-200 animate-pulse shadow-sm" />
            <div class="h-48 bg-white rounded-xl border border-gray-200 animate-pulse shadow-sm" />
          </div>
        </div>

        <!-- Not Found -->
        <div v-else-if="!order" class="text-center py-20 bg-white rounded-xl border border-gray-200 shadow-sm">
          <h3 class="text-xl font-bold text-gray-800">Transaksi tidak ditemukan</h3>
          <p class="text-gray-500 text-sm mt-2 mb-6">Mungkin URL salah atau transaksi ini milik akun lain.</p>
          <button
            @click="$router.push('/dashboard/orders')"
            class="px-6 py-2.5 bg-[#03AC0E] text-white font-bold rounded-lg hover:bg-[#028c0b] transition-colors"
          >
            Kembali ke Daftar Transaksi
          </button>
        </div>

        <!-- Detail -->
        <div v-else class="space-y-5">

          <!-- ① Stepper Card -->
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sm:p-8">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <h1 class="text-xl font-bold text-gray-900">Detail Transaksi</h1>
                  <!-- Promo badge -->
                  <span
                    v-if="isPromo"
                    class="text-xs font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-600 border border-purple-200"
                  >
                    🏷 {{ order.promo_name || 'Transaksi Promo' }}
                  </span>
                </div>
                <p class="text-sm text-gray-500 mt-1">
                  No. Invoice:
                  <span class="font-bold text-[#03AC0E]">{{ order.order_id }}</span>
                </p>
                <p class="text-xs text-gray-400 mt-0.5">Dibuat: {{ formatDate(order.created_at) }}</p>
              </div>

              <!-- Canceled badge -->
              <div v-if="isCanceled" class="px-4 py-2 bg-red-50 border border-red-200 text-red-600 font-bold rounded-lg text-sm">
                Pesanan Dibatalkan
              </div>
            </div>

            <!-- Progress Stepper -->
            <div v-if="!isCanceled" class="relative">
              <!-- Track BG -->
              <div class="absolute top-[28px] left-[10%] right-[10%] h-[3px] bg-gray-200 z-0" />
              <!-- Track Active -->
              <div
                class="absolute top-[28px] left-[10%] h-[3px] bg-[#03AC0E] z-0 transition-all duration-700 ease-in-out"
                :style="{ width: progressWidth }"
              />

              <div class="relative z-10 flex justify-between">
                <div
                  v-for="(step, index) in steps"
                  :key="step.id"
                  class="flex flex-col items-center w-1/4"
                >
                  <div
                    class="w-14 h-14 rounded-full border-4 flex items-center justify-center transition-colors duration-300"
                    :class="[
                      index <= stepIndex ? 'border-[#03AC0E] text-[#03AC0E] bg-green-50 shadow-sm' : 'border-gray-200 text-gray-300 bg-white',
                      index === stepIndex ? 'shadow-md' : '',
                    ]"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="step.icon" />
                    </svg>
                  </div>
                  <div class="mt-3 text-center">
                    <p class="text-xs font-bold" :class="index <= stepIndex ? 'text-gray-900' : 'text-gray-400'">
                      {{ step.label }}
                    </p>
                    <p v-if="index === 0" class="text-[10px] text-gray-400 mt-0.5">{{ formatDate(order.created_at) }}</p>
                    <p v-if="index === 1 && stepIndex >= 1" class="text-[10px] text-gray-400 mt-0.5">{{ formatDate(order.transaction_time || order.settlement_time) }}</p>
                    <p v-if="index === 2 && stepIndex >= 2" class="text-[10px] text-gray-400 mt-0.5">Dalam pengiriman</p>
                    <p v-if="index === 3 && stepIndex >= 3" class="text-[10px] text-gray-400 mt-0.5">{{ formatDate(order.settlement_time) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Canceled Detail -->
            <div v-else class="mt-2 text-sm text-gray-500">
              Status: <span class="font-semibold text-red-500 uppercase">{{ order.transaction_status }}</span>
              <span v-if="order.payment_type"> · Metode: <span class="font-semibold">{{ order.payment_type }}</span></span>
            </div>
          </div>

          <!-- ② Produk -->
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sm:p-8">
            <h2 class="text-base font-bold text-gray-900 mb-4">
              {{ isPromo ? 'Item yang Dibeli' : 'Detail Produk' }}
            </h2>

            <div class="space-y-3">
              <div
                v-for="(item, idx) in order.items"
                :key="idx"
                class="flex items-start gap-4 p-4 border border-gray-100 rounded-xl bg-gray-50/50"
              >
                <!-- Cover -->
                <div class="w-16 h-16 flex-shrink-0 rounded-lg overflow-hidden border border-gray-100 bg-white">
                  <NuxtImg
                    v-if="getItemCover(item)"
                    :src="getItemCover(item)!"
                    class="w-full h-full object-cover"
                    alt="Item"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <svg class="w-7 h-7 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14M14 8h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                  </div>
                </div>

                <!-- Info -->
                <div class="flex-1 min-w-0">
                  <h3 class="font-bold text-gray-900 text-sm line-clamp-2">{{ getItemName(item) }}</h3>
                  <p class="text-xs text-gray-500 mt-0.5">{{ item.quantity }} × {{ formatRupiah(item.unit_price) }}</p>

                  <!-- Promo: tampilkan harga asli + diskon -->
                  <template v-if="isPromo && item.discount_value > 0">
                    <p class="text-xs text-gray-400 line-through mt-0.5">{{ formatRupiah(item.original_price) }}</p>
                    <span class="inline-block mt-1 text-[10px] font-bold px-1.5 py-0.5 bg-purple-50 text-purple-600 rounded border border-purple-100">
                      Hemat {{ formatRupiah(item.discount_value * item.quantity) }}
                    </span>
                  </template>

                  <!-- Tipe item (produk / paket) -->
                  <span
                    v-if="item.item_type && item.item_type !== 'stock'"
                    class="inline-block mt-1 text-[10px] font-semibold px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded border border-indigo-100 ml-1"
                  >
                    {{ item.item_type }}
                  </span>
                </div>

                <!-- Subtotal -->
                <div class="text-right flex-shrink-0">
                  <p class="text-xs text-gray-400 mb-0.5">Subtotal</p>
                  <p class="font-bold text-gray-900 text-sm">{{ formatRupiah(item.subtotal) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- ③ Pengiriman + Pembayaran -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">

            <!-- Pengiriman -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sm:p-7">
              <h2 class="text-base font-bold text-gray-900 mb-4 border-b border-gray-100 pb-3">Info Pengiriman</h2>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between gap-2">
                  <span class="text-gray-500 flex-shrink-0">Kurir</span>
                  <span class="font-bold text-gray-900 uppercase text-right">
                    {{ order.shipment?.courier_name || '-' }} {{ order.shipment?.courier_service || '' }}
                  </span>
                </div>
                <div class="flex justify-between gap-2">
                  <span class="text-gray-500 flex-shrink-0">ETD</span>
                  <span class="font-semibold text-gray-900 text-right">{{ order.shipment?.etd || '-' }}</span>
                </div>
                <div class="flex justify-between gap-2">
                  <span class="text-gray-500 flex-shrink-0">No. Resi</span>
                  <span class="font-bold text-right" :class="order.shipment?.waybill_number ? 'text-[#03AC0E]' : 'text-gray-400'">
                    {{ order.shipment?.waybill_number || 'Menunggu Resi' }}
                  </span>
                </div>
                <div class="pt-2 border-t border-gray-100">
                  <p class="text-gray-500 mb-1">Alamat Pengiriman</p>
                  <p class="font-bold text-gray-900">
                    {{ order.shipment?.recipient_name }}
                    <span class="font-normal text-gray-500 ml-1 text-xs">{{ order.shipment?.recipient_phone }}</span>
                  </p>
                  <p class="text-gray-600 mt-1 text-xs leading-relaxed">{{ order.shipment?.shipping_address || '-' }}</p>
                </div>
              </div>
            </div>

            <!-- Pembayaran -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sm:p-7 flex flex-col">
              <h2 class="text-base font-bold text-gray-900 mb-4 border-b border-gray-100 pb-3">Rincian Pembayaran</h2>

              <div class="space-y-2.5 text-sm flex-1">
                <div class="flex justify-between">
                  <span class="text-gray-500">Status</span>
                  <span class="font-bold uppercase text-right"
                    :class="isPending ? 'text-amber-500' : isCanceled ? 'text-red-500' : 'text-[#03AC0E]'"
                  >
                    {{ order.transaction_status }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">Metode</span>
                  <span class="font-bold text-gray-900 uppercase text-right">{{ order.payment_type || 'Belum Dipilih' }}</span>
                </div>

                <!-- Harga item -->
                <div class="flex justify-between">
                  <span class="text-gray-500">Subtotal Barang</span>
                  <span class="font-medium text-gray-900">
                    {{ formatRupiah(order.items_subtotal || order.items_subtotal_original || 0) }}
                  </span>
                </div>

                <!-- Diskon promo -->
                <div v-if="(order.total_discount || 0) > 0" class="flex justify-between text-purple-600">
                  <span>Diskon{{ isPromo ? ' Promo' : '' }}</span>
                  <span class="font-medium">- {{ formatRupiah(order.total_discount) }}</span>
                </div>

                <!-- Diskon kupon (reguler) -->
                <div v-if="!isPromo && (order.discount_amount || 0) > 0" class="flex justify-between text-[#03AC0E]">
                  <span>Diskon Kupon</span>
                  <span class="font-medium">- {{ formatRupiah(order.discount_amount) }}</span>
                </div>

                <!-- Ongkir -->
                <div class="flex justify-between">
                  <span class="text-gray-500">Ongkos Kirim</span>
                  <span class="font-medium text-gray-900">{{ formatRupiah(order.shipping_cost || 0) }}</span>
                </div>

                <!-- Biaya transport teknisi (promo service) -->
                <div v-if="(order.service_cost || 0) > 0" class="flex justify-between">
                  <span class="text-gray-500">Biaya Transport Teknisi</span>
                  <span class="font-medium text-gray-900">{{ formatRupiah(order.service_cost) }}</span>
                </div>

                <!-- Total -->
                <div class="flex justify-between items-center pt-3 border-t border-gray-100 mt-2">
                  <span class="font-bold text-gray-900">Total Belanja</span>
                  <span class="font-bold text-[#03AC0E] text-lg">{{ formatRupiah(order.gross_amount) }}</span>
                </div>
              </div>

              <!-- CTA Bayar -->
              <div v-if="isPending" class="mt-5 pt-4 border-t border-gray-100">
                <button
                  @click="payOrder"
                  :disabled="isRepaying"
                  class="w-full bg-[#03AC0E] hover:bg-[#028c0b] disabled:bg-gray-400 text-white font-bold py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 text-sm"
                >
                  <svg v-if="!isRepaying" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/>
                  </svg>
                  <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                  {{ isRepaying ? 'Memuat Pembayaran...' : 'Lanjutkan Pembayaran' }}
                </button>
              </div>
            </div>
          </div>

          <!-- ④ Booking Info (Promo Service) -->
          <div v-if="hasBooking" class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sm:p-8">
            <h2 class="text-base font-bold text-gray-900 mb-4 border-b border-gray-100 pb-3">
              🔧 Info Jadwal Teknisi
            </h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div class="flex justify-between gap-2">
                <span class="text-gray-500">No. Booking</span>
                <span class="font-bold text-gray-900 font-mono">{{ order.booking.booking_number }}</span>
              </div>
              <div class="flex justify-between gap-2">
                <span class="text-gray-500">Status Booking</span>
                <span class="font-bold capitalize" :class="order.booking.status === 'confirmed' ? 'text-[#03AC0E]' : 'text-amber-500'">
                  {{ order.booking.status }}
                </span>
              </div>
              <div class="flex justify-between gap-2">
                <span class="text-gray-500">Tanggal</span>
                <span class="font-semibold text-gray-900">{{ order.booking.scheduled_date || '-' }}</span>
              </div>
              <div class="flex justify-between gap-2">
                <span class="text-gray-500">Waktu</span>
                <span class="font-semibold text-gray-900">{{ order.booking.time_slot || '-' }}</span>
              </div>
              <div class="sm:col-span-2 flex justify-between gap-2">
                <span class="text-gray-500">Nama / HP</span>
                <span class="font-semibold text-gray-900 text-right">
                  {{ order.booking.contact_name }} · {{ order.booking.contact_phone }}
                </span>
              </div>
              <div class="sm:col-span-2 flex justify-between gap-2">
                <span class="text-gray-500 flex-shrink-0">Alamat</span>
                <span class="font-semibold text-gray-900 text-right text-xs leading-relaxed">
                  {{ [order.booking.address, order.booking.district, order.booking.city].filter(Boolean).join(', ') }}
                </span>
              </div>
            </div>
          </div>

        </div>
        <!-- /detail -->

      </main>
    </div>
  </div>
</template>