<!-- pages/check-booking.vue -->
<template>
    <div class="min-h-screen bg-gray-50/50 py-12 px-4 sm:px-6 lg:px-8 font-sans text-gray-800">
        <div class="max-w-3xl mx-auto space-y-8">

            <!-- 1. HEADER & SEARCH INPUT -->
            <div class="text-center space-y-2 mb-8">
                <h1 class="text-3xl font-bold tracking-tight text-gray-900">Cek Status Booking</h1>
                <p class="text-gray-500 text-sm">Pantau status pemasangan, detail layanan, dan tagihan Anda.</p>
            </div>

            <div
                class="bg-white p-2 rounded-2xl shadow-sm border border-gray-200 flex flex-col sm:flex-row gap-2 max-w-xl mx-auto focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all">
                <div class="relative flex-1 flex items-center">
                    <svg class="w-5 h-5 text-gray-400 absolute left-4" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <input v-model="searchQuery" @keyup.enter="fetchBooking" type="text"
                        placeholder="Masukkan Nomor Booking (BK-xxxx) atau UUID"
                        class="w-full pl-12 pr-4 py-3 bg-transparent text-sm focus:outline-none placeholder-gray-400"
                        :disabled="isLoading" />
                </div>
                <button @click="fetchBooking" :disabled="!searchQuery.trim() || isLoading"
                    class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-xl shadow-sm transition-all focus:outline-none active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center whitespace-nowrap">
                    <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none"
                        viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                    </svg>
                    Cek Booking
                </button>
            </div>

            <!-- 2. ERROR STATE -->
            <transition enter-active-class="transition ease-out duration-200" enter-from-class="opacity-0 translate-y-1"
                enter-to-class="opacity-100 translate-y-0">
                <div v-if="errorMsg"
                    class="bg-red-50 border border-red-200 p-4 rounded-xl flex items-start gap-3 max-w-xl mx-auto">
                    <svg class="w-5 h-5 text-red-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                        <h3 class="text-sm font-bold text-red-800">Booking tidak ditemukan</h3>
                        <p class="text-xs text-red-600 mt-1">{{ errorMsg }}</p>
                    </div>
                </div>
            </transition>

            <!-- 3. LOADING SKELETON -->
            <div v-if="isLoading && !booking"
                class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8 animate-pulse space-y-8">
                <div class="flex justify-between items-center border-b pb-6">
                    <div class="h-8 bg-gray-200 rounded w-40"></div>
                    <div class="h-6 bg-gray-200 rounded-full w-24"></div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-3">
                        <div class="h-4 bg-gray-200 rounded w-24"></div>
                        <div class="h-16 bg-gray-100 rounded w-full"></div>
                    </div>
                    <div class="space-y-3">
                        <div class="h-4 bg-gray-200 rounded w-24"></div>
                        <div class="h-16 bg-gray-100 rounded w-full"></div>
                    </div>
                </div>
            </div>

            <!-- 4. DISPLAY DATA -->
            <transition enter-active-class="transition ease-out duration-300" enter-from-class="opacity-0 translate-y-4"
                enter-to-class="opacity-100 translate-y-0">
                <div v-if="booking && !isLoading"
                    class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden relative">

                    <!-- A. HEADER -->
                    <div
                        class="px-6 sm:px-8 py-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gray-50/50">
                        <div>
                            <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Nomor Booking</p>
                            <h2 class="text-2xl font-black text-indigo-900 font-mono tracking-tight">{{
                                booking.booking_number }}</h2>
                        </div>
                        <div class="shrink-0">
                            <span :class="getStatusClass(booking.status)"
                                class="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border">
                                {{ booking.status ? booking.status.replace('_', ' ') : 'UNKNOWN' }}
                            </span>
                        </div>
                    </div>

                    <div class="p-6 sm:p-8 space-y-8">
                        <!-- Grid Atas -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

                            <!-- B. INFORMASI PELANGGAN -->
                            <div>
                                <h3
                                    class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                    Pelanggan
                                </h3>
                                <div class="bg-gray-50 p-4 rounded-xl text-sm space-y-2.5">
                                    <p class="font-bold text-gray-900">{{ booking.contact_name }}</p>
                                    <p v-if="booking.contact_phone">
                                        <a :href="`https://wa.me/${formatWaNumber(booking.contact_phone)}`"
                                            target="_blank"
                                            class="text-green-600 font-medium hover:underline flex items-center gap-1">
                                            {{ booking.contact_phone }}
                                            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                            </svg>
                                        </a>
                                    </p>
                                    <div class="pt-2 border-t border-gray-200/60 text-gray-600">
                                        <p>{{ booking.address || '-' }}</p>
                                        <p class="text-xs mt-1 text-gray-500 font-medium">{{ booking.city || '-' }} •
                                            Jarak: {{ booking.distance_km || 0 }} KM</p>
                                    </div>
                                </div>
                            </div>

                            <!-- C & D. DETAIL LAYANAN & JADWAL -->
                            <div class="space-y-6">
                                <div>
                                    <h3
                                        class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                        </svg>
                                        Detail Layanan
                                    </h3>
                                    <div class="bg-gray-50 p-4 rounded-xl text-sm space-y-2">
                                        <div class="flex justify-between"><span
                                                class="text-gray-500">Kategori</span><span
                                                class="font-bold text-gray-900 capitalize">{{ booking.category }}</span>
                                        </div>
                                        <div class="flex justify-between"><span class="text-gray-500">Jumlah</span><span
                                                class="font-bold text-gray-900">{{ booking.camera_count }} Titik</span>
                                        </div>
                                        <div class="flex justify-between"><span class="text-gray-500">Brand</span><span
                                                class="font-bold text-gray-900 uppercase">{{ booking.brand }}</span>
                                        </div>
                                        <div v-if="booking.addons && booking.addons.length"
                                            class="pt-2 flex flex-wrap gap-1.5">
                                            <span v-for="(addon, idx) in booking.addons" :key="idx"
                                                class="px-2 py-0.5 bg-white border border-gray-200 text-gray-600 rounded text-[10px] font-bold uppercase">
                                                {{ addon }}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3
                                        class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        Jadwal Pelaksanaan
                                    </h3>
                                    <div
                                        class="flex items-center gap-3 bg-indigo-50 border border-indigo-100 p-3 rounded-xl">
                                        <div class="text-sm font-bold text-indigo-900">{{
                                            formatDateLong(booking.scheduled_date) }}</div>
                                        <div class="w-px h-4 bg-indigo-200"></div>
                                        <div
                                            class="text-xs font-semibold text-indigo-700 bg-white px-2 py-1 rounded border border-indigo-100">
                                            {{ booking.time_slot || '-' }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <hr class="border-gray-100">

                        <!-- Grid Bawah (Keuangan) -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

                            <!-- E. RINCIAN HARGA -->
                            <div>
                                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Rincian Biaya
                                </h3>
                                <div class="bg-white border border-gray-200 p-4 rounded-xl text-sm space-y-3">
                                    <div class="flex justify-between text-gray-600"><span>Perangkat CCTV</span><span
                                            class="font-medium text-gray-900">{{ formatRupiah(booking.device_price)
                                            }}</span></div>
                                    <div class="flex justify-between text-gray-600"><span>Biaya Jasa</span><span
                                            class="font-medium text-gray-900">{{ formatRupiah(booking.service_price)
                                            }}</span></div>
                                    <div v-if="booking.addon_price > 0" class="flex justify-between text-gray-600">
                                        <span>Biaya Add-ons</span><span class="font-medium text-gray-900">{{
                                            formatRupiah(booking.addon_price) }}</span></div>
                                    <div class="flex justify-between text-gray-600 border-b border-gray-100 pb-3">
                                        <span>Transport ({{ booking.distance_km }} KM)</span><span
                                            class="font-medium text-gray-900">{{ formatRupiah(booking.transport_fee)
                                            }}</span></div>
                                    <div class="flex justify-between items-center pt-1">
                                        <span class="font-bold text-gray-900">Total Keseluruhan</span>
                                        <span class="text-xl font-black text-indigo-600">{{
                                            formatRupiah(booking.total_price) }}</span>
                                    </div>
                                </div>
                            </div>

                            <!-- F. PEMBAYARAN -->
                            <div>
                                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Status
                                    Pembayaran</h3>
                                <div class="space-y-4">

                                    <!-- Tagihan Summary -->
                                    <div class="grid grid-cols-2 gap-3">
                                        <div class="bg-gray-50 border border-gray-100 p-3 rounded-xl text-center">
                                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-0.5">Wajib DP</p>
                                            <p class="text-sm font-bold text-gray-900">{{
                                                formatRupiah(booking.dp_amount) }}</p>
                                        </div>
                                        <div :class="booking.remaining_amount === 0 ? 'bg-emerald-50 border-emerald-100' : 'bg-orange-50 border-orange-100'"
                                            class="border p-3 rounded-xl text-center">
                                            <p :class="booking.remaining_amount === 0 ? 'text-emerald-600' : 'text-orange-600'"
                                                class="text-[10px] uppercase font-bold mb-0.5">Sisa Tagihan</p>
                                            <p :class="booking.remaining_amount === 0 ? 'text-emerald-900' : 'text-orange-900'"
                                                class="text-sm font-bold">{{ formatRupiah(booking.remaining_amount) }}
                                            </p>
                                        </div>
                                    </div>

                                    <!-- Riwayat List -->
                                    <div v-if="booking.payments && booking.payments.length > 0" class="space-y-2">
                                        <div v-for="payment in booking.payments" :key="payment.order_id"
                                            class="flex justify-between items-center bg-white border border-gray-200 p-3 rounded-xl">
                                            <div>
                                                <p class="text-xs font-bold text-gray-900 uppercase">{{
                                                    payment.payment_type }}</p>
                                                <p class="text-[10px] text-gray-400 font-mono mt-0.5">{{
                                                    payment.order_id }}</p>
                                            </div>
                                            <div class="text-right">
                                                <p class="text-sm font-bold text-gray-900 mb-0.5">{{
                                                    formatRupiah(payment.gross_amount) }}</p>
                                                <span
                                                    :class="payment.status === 'success' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                                                    class="px-2 py-0.5 rounded text-[10px] font-bold uppercase">
                                                    {{ payment.status }}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else
                                        class="text-center p-4 border border-dashed border-gray-200 rounded-xl bg-gray-50/50">
                                        <p class="text-xs font-medium text-gray-500">Belum ada riwayat pembayaran.</p>
                                    </div>

                                </div>
                            </div>

                        </div>
                    </div>

                    <!-- 6. ACTION CTA -->
                    <div v-if="ctaAction" class="p-6 bg-gray-50 border-t border-gray-100">
                        <button @click="processPayment" :disabled="isPaymentLoading"
                            :class="ctaAction.type === 'dp' ? 'bg-orange-500 hover:bg-orange-600' : 'bg-emerald-500 hover:bg-emerald-600'"
                            class="w-full sm:w-auto sm:min-w-[240px] float-right inline-flex items-center justify-center px-6 py-3.5 text-white text-sm font-bold rounded-xl shadow-sm transition-all focus:outline-none active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
                            <svg v-if="isPaymentLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none"
                                viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                </path>
                            </svg>
                            {{ ctaAction.label }}
                        </button>
                        <div class="clear-both"></div>
                    </div>

                </div>
            </transition>

        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/service/api' // Sesuaikan path ini dengan lokasi file api.js Anda

const searchQuery = ref('')
const booking = ref(null)
const isLoading = ref(false)
const isPaymentLoading = ref(false)
const errorMsg = ref('')

// --- FETCH LOGIC ---
const fetchBooking = async () => {
  const query = searchQuery.value.trim()
  if (!query) return

  isLoading.value = true
  errorMsg.value = ''
  booking.value = null

  // Auto-detect endpoint berdasarkan prefix input
  const isNumber = query.toUpperCase().startsWith('BK-')
  const endpoint = isNumber 
    ? `/services/booking/number/${query.toUpperCase()}`
    : `/services/booking/${query}`

  try {
    // Menggunakan api.get dari service Anda
    const res = await api.get(endpoint)
    
    // Menyesuaikan dengan standar response Axios (biasanya data ada di res.data)
    booking.value = res.data?.data || res.data

  } catch (error) {
    console.error('Fetch error:', error)
    errorMsg.value = 'Pastikan nomor booking atau UUID yang Anda masukkan benar.'
  } finally {
    isLoading.value = false
  }
}

// --- PAYMENT LOGIC ---
const ctaAction = computed(() => {
  if (!booking.value) return null
  
  if (booking.value.status === 'confirmed') {
    return { type: 'dp', label: 'Bayar DP Sekarang' }
  }
  if (booking.value.status === 'done' && booking.value.remaining_amount > 0) {
    return { type: 'lunas', label: 'Bayar Pelunasan' }
  }
  
  return null
})

const processPayment = async () => {
  if (!booking.value || !ctaAction.value) return

  isPaymentLoading.value = true
  try {
    const payload = {
      booking_uuid: booking.value.uuid,
      payment_type: ctaAction.value.type // 'dp' atau 'lunas'
    }

    // Menggunakan api.post dari service Anda
    const res = await api.post('/services/payment/create', payload)
    
    // Asumsi response axios menyimpan URL di res.data.payment_url
    const paymentUrl = res.data?.payment_url || res.payment_url

    // Redirect ke payment gateway (Midtrans/Xendit URL) jika ada
    if (paymentUrl) {
      window.location.href = paymentUrl
    } else {
      alert('Link pembayaran berhasil dibuat, silakan cek email / WhatsApp Anda.')
      await fetchBooking() // Refresh data
    }
    
  } catch (error) {
    console.error('Payment create error:', error)
    alert('Gagal membuat link pembayaran. Silakan coba lagi.')
  } finally {
    isPaymentLoading.value = false
  }
}

// --- FORMATTERS ---
const formatRupiah = (number) => {
  return new Intl.NumberFormat('id-ID', { 
    style: 'currency', 
    currency: 'IDR', 
    minimumFractionDigits: 0 
  }).format(number || 0)
}

const formatDateLong = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID', { 
    weekday: 'long', 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
}

const formatWaNumber = (phone) => {
  if (!phone) return ''
  // Mengubah 0812... menjadi 62812... untuk standard link wa.me
  if (phone.startsWith('0')) return '62' + phone.substring(1)
  return phone
}

const getStatusClass = (status) => {
  const map = {
    'pending': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'confirmed': 'bg-blue-100 text-blue-800 border-blue-200',
    'dp_paid': 'bg-purple-100 text-purple-800 border-purple-200',
    'progress': 'bg-indigo-100 text-indigo-800 border-indigo-200',
    'done': 'bg-green-100 text-green-800 border-green-200',
    'lunas': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    'cancel': 'bg-red-100 text-red-800 border-red-200'
  }
  return map[status?.toLowerCase()] || 'bg-gray-100 text-gray-800 border-gray-200'
}
</script>