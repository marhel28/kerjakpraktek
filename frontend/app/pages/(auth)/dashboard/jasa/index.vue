<!-- pages/dashboard/jasa/index.vue -->
<template>
    <div class="min-h-screen bg-[#F4F5F7] font-sans selection:bg-green-600 selection:text-white pb-12">
        <!-- Header -->
<!-- Header -->
    <div class="bg-white border-b border-gray-100 sticky top-0 z-20 shadow-sm">
            <div class="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
                
                <!-- Bagian Kiri: Tombol Kembali + Judul -->
                <div class="flex items-center gap-3 sm:gap-4">
                    <button @click="navigateTo('/dashboard')"
                        class="p-2 -ml-2 rounded-full hover:bg-gray-50 text-gray-500 hover:text-gray-900 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500/20"
                        aria-label="Kembali ke Dashboard">
                        <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
                        </svg>
                    </button>
                    <div>
                        <h1 class="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">Jasa Saya</h1>
                        <p class="text-xs sm:text-sm font-medium text-gray-500 mt-0.5">Pantau semua booking kamera & servis</p>
                    </div>
                </div>

                <!-- Bagian Kanan: Tombol Booking -->
                <button
                    class="flex items-center gap-1.5 text-sm font-semibold bg-green-600 text-white px-4 sm:px-5 py-2 sm:py-2.5 rounded-full hover:bg-green-700 hover:shadow-md transition-all duration-200"
                    @click="navigateTo('/services/booking')">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    <span class="hidden sm:inline">Booking Baru</span>
                    <span class="sm:hidden">Baru</span>
                </button>
                
            </div>
        </div>

        <div class="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">

            <!-- Stats Cards -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <template v-if="pending">
                    <div v-for="i in 4" :key="i" class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm animate-pulse">
                        <div class="h-3 bg-gray-200 rounded-full w-1/2 mb-4"></div>
                        <div class="h-8 bg-gray-200 rounded-lg w-3/4"></div>
                    </div>
                </template>
                <template v-else-if="data">
                    <!-- Total -->
                    <div class="bg-white border border-gray-100 shadow-sm rounded-2xl p-5 hover:shadow-md transition-shadow">
                        <div class="flex items-center gap-3 mb-2">
                            <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-600">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
                            </div>
                            <p class="text-sm font-semibold text-gray-500">Total Booking</p>
                        </div>
                        <p class="text-2xl font-bold text-gray-900">{{ data.stats.total }}</p>
                    </div>
                    <!-- Aktif -->
                    <div class="bg-white border border-gray-100 shadow-sm rounded-2xl p-5 hover:shadow-md transition-shadow">
                        <div class="flex items-center gap-3 mb-2">
                            <div class="w-8 h-8 rounded-full bg-orange-50 flex items-center justify-center text-orange-500">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            </div>
                            <p class="text-sm font-semibold text-gray-500">Aktif</p>
                        </div>
                        <p class="text-2xl font-bold text-gray-900">{{ data.stats.active }}</p>
                    </div>
                    <!-- Selesai -->
                    <div class="bg-white border border-gray-100 shadow-sm rounded-2xl p-5 hover:shadow-md transition-shadow">
                        <div class="flex items-center gap-3 mb-2">
                            <div class="w-8 h-8 rounded-full bg-green-50 flex items-center justify-center text-green-600">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            </div>
                            <p class="text-sm font-semibold text-gray-500">Selesai</p>
                        </div>
                        <p class="text-2xl font-bold text-gray-900">{{ data.stats.done }}</p>
                    </div>
                    <!-- Tagihan -->
                    <div :class="data.stats.pending_payment > 0 ? 'bg-red-50 border-red-100' : 'bg-white border-gray-100'"
                        class="border shadow-sm rounded-2xl p-5 hover:shadow-md transition-shadow">
                        <div class="flex items-center gap-3 mb-2">
                            <div :class="data.stats.pending_payment > 0 ? 'bg-red-100 text-red-600' : 'bg-gray-50 text-gray-500'" class="w-8 h-8 rounded-full flex items-center justify-center">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            </div>
                            <p :class="data.stats.pending_payment > 0 ? 'text-red-600' : 'text-gray-500'" class="text-sm font-semibold">Tagihan</p>
                        </div>
                        <p :class="data.stats.pending_payment > 0 ? 'text-red-600' : 'text-gray-900'"
                            class="text-xl font-bold truncate">
                            {{ data.stats.pending_payment > 0 ? formatRupiah(data.stats.pending_payment) : 'Lunas Semua' }}
                        </p>
                    </div>
                </template>
            </div>

            <!-- Filter + Search -->
            <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                <!-- Status tabs -->
                <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                    <button v-for="tab in statusTabs" :key="tab.value" @click="setStatus(tab.value)" :class="[
                        'flex-shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition-colors duration-200',
                        currentStatus === tab.value
                            ? 'bg-green-600 text-white shadow-sm'
                            : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-green-50 hover:text-green-700 hover:border-green-200'
                    ]">
                        {{ tab.label }}
                    </button>
                </div>

                <!-- Search + sort -->
                <div class="flex flex-col sm:flex-row gap-3">
                    <div class="flex-1 relative">
                        <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none"
                            stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <input v-model="searchInput" type="text" placeholder="Cari nomor booking, kota, brand..."
                            class="w-full pl-11 pr-4 py-2.5 text-sm font-medium border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all bg-gray-50 hover:bg-white placeholder-gray-400" />
                    </div>
                    <select v-model="currentSort"
                        class="text-sm font-semibold border border-gray-200 rounded-xl px-4 py-2.5 bg-gray-50 hover:bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 cursor-pointer transition-all min-w-[160px]"
                        @change="currentPage = 1">
                        <option v-for="s in sortOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
                    </select>
                </div>
            </div>

            <!-- Booking List -->
            <div class="space-y-4">
                <!-- Loading skeleton -->
                <template v-if="pending">
                    <div v-for="i in 3" :key="i" class="border border-gray-100 rounded-2xl p-5 shadow-sm bg-white animate-pulse">
                        <div class="flex justify-between mb-4">
                            <div class="h-4 bg-gray-200 rounded-full w-32"></div>
                            <div class="h-6 bg-gray-200 rounded-full w-24"></div>
                        </div>
                        <div class="h-3 bg-gray-100 rounded-full w-48 mb-3"></div>
                        <div class="h-3 bg-gray-100 rounded-full w-36 mb-6"></div>
                        <div class="flex justify-between items-center border-t border-gray-50 pt-4">
                            <div class="h-6 bg-gray-200 rounded-lg w-28"></div>
                            <div class="h-10 bg-gray-200 rounded-xl w-32"></div>
                        </div>
                    </div>
                </template>

                <!-- Empty State -->
                <template v-else-if="!data || data.bookings.items.length === 0">
                    <div class="text-center py-20 bg-white border border-gray-100 rounded-2xl shadow-sm">
                        <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                        </div>
                        <p class="text-base font-bold text-gray-900">Tidak ada booking ditemukan</p>
                        <p class="text-sm text-gray-500 mt-1">
                            {{ currentStatus !== 'all' ? 'Coba ganti filter status di atas.' : 'Kamu belum membuat pesanan jasa apapun.' }}
                        </p>
                    </div>
                </template>

                <!-- Booking cards -->
                <template v-else>
                    <div v-for="booking in data.bookings.items" :key="String(booking.uuid)"
                        class="bg-white border border-gray-100 shadow-sm hover:shadow-md rounded-2xl p-5 transition-all duration-200">

                        <!-- Top row -->
                        <div class="flex items-start justify-between gap-3 mb-4">
                            <div>
                                <div class="flex items-center gap-2 mb-1">
                                    <span class="text-xs font-semibold text-gray-500">#{{ booking.booking_number }}</span>
                                    <span class="w-1 h-1 rounded-full bg-gray-300"></span>
                                    <span class="text-xs font-medium text-gray-500">{{ booking.camera_count }} Kamera</span>
                                </div>
                                <h3 class="text-base font-bold text-gray-900 leading-tight">
                                    {{ booking.category }}
                                </h3>
                            </div>
                            <span :class="statusBadgeClass(booking.status_color)"
                                class="flex-shrink-0 text-xs font-semibold px-3 py-1 rounded-full">
                                {{ booking.status_label }}
                            </span>
                        </div>

                        <!-- Location + schedule -->
                        <div class="flex flex-wrap items-center gap-x-4 gap-y-2 mb-4 bg-gray-50 p-3 rounded-xl border border-gray-100/50">
                            <div class="flex items-center gap-1.5 text-xs font-semibold text-gray-600">
                                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                {{ booking.city }}
                            </div>
                            <div class="w-1 h-1 rounded-full bg-gray-300 hidden sm:block"></div>
                            <div class="flex items-center gap-1.5 text-xs font-semibold text-gray-600">
                                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                {{ booking.scheduled_label }} <span class="text-gray-400 font-normal">|</span> {{ booking.time_slot }}
                            </div>
                            <template v-if="booking.brand">
                                <div class="w-1 h-1 rounded-full bg-gray-300 hidden sm:block"></div>
                                <div class="flex items-center gap-1.5 text-xs font-semibold text-gray-600">
                                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                                    </svg>
                                    {{ booking.brand }}
                                </div>
                            </template>
                        </div>

                        <!-- Addons -->
                        <div v-if="booking.addons && booking.addons.length > 0" class="flex flex-wrap gap-2 mb-4">
                            <span v-for="addon in booking.addons.slice(0, 3)" :key="addon"
                                class="text-[11px] font-semibold bg-white border border-gray-200 text-gray-600 px-2.5 py-1 rounded-lg">
                                {{ addon }}
                            </span>
                            <span v-if="booking.addons.length > 3"
                                class="text-[11px] font-semibold text-gray-500 px-1 py-1">
                                +{{ booking.addons.length - 3 }} lainnya
                            </span>
                        </div>

                        <!-- Bottom: price + action -->
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-gray-100 mt-2">
                            <div>
                                <p class="text-sm font-medium text-gray-500 mb-0.5">Total Harga</p>
                                <p class="text-lg font-bold text-gray-900">{{ formatRupiah(booking.total_price) }}</p>
                                <p v-if="booking.action.action === 'pay_dp'" class="text-xs font-semibold text-orange-500 mt-1">
                                    Bayar DP: {{ formatRupiah(booking.dp_amount) }}
                                </p>
                                <p v-else-if="booking.action.action === 'pay_lunas'" class="text-xs font-semibold text-red-500 mt-1">
                                    Sisa Tagihan: {{ formatRupiah(booking.remaining_amount) }}
                                </p>
                            </div>

                            <div class="flex items-center gap-2 w-full sm:w-auto">
                                <button
                                    class="flex-1 sm:flex-none text-sm font-semibold px-4 py-2.5 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
                                    @click="navigateTo(`/dashboard/jasa/${booking.uuid}`)">
                                    Detail
                                </button>

                                <button
                                    v-if="booking.action.action === 'pay_dp' || booking.action.action === 'pay_lunas'"
                                    class="flex-1 sm:flex-none text-sm font-semibold px-5 py-2.5 text-white rounded-xl transition-all disabled:opacity-70 disabled:cursor-not-allowed shadow-sm shadow-green-500/20"
                                    :class="payingUuid === String(booking.uuid) ? 'bg-green-500' : 'bg-green-600 hover:bg-green-700'"
                                    :disabled="payingUuid === String(booking.uuid)"
                                    @click="handlePay(booking)">
                                    <span v-if="payingUuid === String(booking.uuid)" class="flex items-center justify-center gap-2">
                                        <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                                        </svg>
                                        Proses...
                                    </span>
                                    <span v-else>{{ booking.action.label }}</span>
                                </button>

                                <button v-else-if="booking.action.action === 'view_receipt'"
                                    class="flex-1 sm:flex-none text-sm font-semibold px-5 py-2.5 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors shadow-sm"
                                    @click="navigateTo(`/dashboard/jasa/${booking.uuid}`)">
                                    {{ booking.action.label }}
                                </button>
                            </div>
                        </div>
                    </div>
                </template>
            </div>

            <!-- Pagination -->
            <div v-if="data && data.bookings.total_pages > 1" class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-gray-200/50">
                <p class="text-sm font-semibold text-gray-500">
                    Menampilkan Halaman <span class="text-gray-900">{{ data.bookings.page }}</span> dari {{ data.bookings.total_pages }}
                    <span class="font-normal mx-1">·</span> <span class="text-gray-900">{{ data.bookings.total }}</span> Pesanan
                </p>
                <div class="flex gap-2 w-full sm:w-auto">
                    <button :disabled="!data.bookings.has_prev" @click="currentPage--"
                        :class="data.bookings.has_prev ? 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50' : 'bg-gray-50 border-gray-200 text-gray-400 cursor-not-allowed'"
                        class="flex-1 sm:flex-none px-4 py-2 text-sm font-semibold border rounded-xl transition-colors">
                        Sebelumnya
                    </button>
                    <button :disabled="!data.bookings.has_next" @click="currentPage++"
                        :class="data.bookings.has_next ? 'bg-gray-900 border-gray-900 text-white hover:bg-gray-800' : 'bg-gray-50 border-gray-200 text-gray-400 cursor-not-allowed'"
                        class="flex-1 sm:flex-none px-4 py-2 text-sm font-semibold border rounded-xl transition-colors">
                        Selanjutnya
                    </button>
                </div>
            </div>
        </div>

        <!-- Toast error -->
        <Teleport to="body">
            <Transition
                enter-active-class="transition duration-300 ease-out"
                enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                enter-to-class="opacity-100 translate-y-0 sm:scale-100"
                leave-active-class="transition duration-200 ease-in"
                leave-from-class="opacity-100 sm:scale-100"
                leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                <div v-if="toastError"
                    class="fixed bottom-4 sm:bottom-auto sm:top-4 right-4 left-4 sm:left-auto z-50 bg-red-600 text-white text-sm font-medium px-5 py-3.5 rounded-xl shadow-lg flex items-center gap-3">
                    <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    {{ toastError }}
                </div>
            </Transition>
        </Teleport>

    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter, navigateTo, useFetch, useHead } from '#app'

useHead({ title: 'Jasa Saya — Dashboard' })

const route  = useRoute()
const router = useRouter()

// ── State ──────────────────────────────────────────────────────────
const currentStatus = ref<string>((route.query.status as string) || 'all')
const currentSort   = ref<string>((route.query.sort as string) || 'newest')
const currentPage   = ref<number>(Number(route.query.page) || 1)
const searchInput   = ref<string>((route.query.q as string) || '')
const debouncedQ    = ref<string>(searchInput.value)
const payingUuid    = ref<string | null>(null)
const toastError    = ref<string | null>(null)

// Debounce search 300ms
let searchTimer: ReturnType<typeof setTimeout>
watch(searchInput, (val) => {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
        debouncedQ.value = val
        currentPage.value = 1
    }, 300)
})

// ── Query params → fetch ───────────────────────────────────────────
const queryParams = computed(() => ({
    status: currentStatus.value,
    sort:   currentSort.value,
    page:   currentPage.value,
    size:   10,
    ...(debouncedQ.value ? { q: debouncedQ.value } : {}),
}))

// Sync URL
watch(queryParams, (params) => {
    router.replace({ query: { ...params, page: String(params.page) } })
}, { deep: true })

// ── Fetch ──────────────────────────────────────────────────────────
const { data, pending, refresh } = await useFetch('/api/jasa', {
    query: queryParams,
    watch: [queryParams],
})

// ── Helpers ────────────────────────────────────────────────────────
function setStatus(val: string) {
    currentStatus.value = val
    currentPage.value   = 1
}

function showToast(msg: string) {
    toastError.value = msg
    setTimeout(() => { toastError.value = null }, 4000)
}

function formatRupiah(amount: number): string {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency', currency: 'IDR', minimumFractionDigits: 0
    }).format(amount)
}

function statusBadgeClass(color: string): string {
    const map: Record<string, string> = {
        amber:  'bg-amber-100 text-amber-700',
        blue:   'bg-blue-100 text-blue-700',
        green:  'bg-green-100 text-green-700',
        purple: 'bg-purple-100 text-purple-700',
        red:    'bg-red-100 text-red-600',
        gray:   'bg-gray-100 text-gray-700',
    }
    return map[color] ?? 'bg-gray-100 text-gray-700'
}

// ── handlePay ──────────────────────────────────────────────────────
async function handlePay(booking: any) {
    const action = booking.action

    if (action.payment_url) {
        window.open(action.payment_url, '_blank', 'noopener')
        return
    }

    const uuid = String(booking.uuid)
    payingUuid.value = uuid

    try {
        const paymentType = action.action === 'pay_dp' ? 'dp' : 'lunas'

        const res = await $fetch<{
            status: string
            payment_url: string
            payment_token: string
            order_id: string
            gross_amount: number
            expired_at: string
        }>(`/api/jasa/${uuid}/pay`, {
            method: 'POST',
            query:  { payment_type: paymentType },
        })

        if (res.payment_url) {
            window.open(res.payment_url, '_blank', 'noopener')
            await refresh()
        } else {
            showToast('Gagal mendapatkan link pembayaran')
        }
    } catch (err: any) {
        const msg = err?.data?.detail
            || err?.data?.message
            || err?.statusMessage
            || 'Gagal membuat pembayaran, coba lagi'
        showToast(msg)
    } finally {
        payingUuid.value = null
    }
}

// ── Constants ──────────────────────────────────────────────────────
const statusTabs = [
    { value: 'all',       label: 'Semua'        },
    { value: 'pending',   label: 'Menunggu'     },
    { value: 'confirmed', label: 'Dikonfirmasi' },
    { value: 'dp_paid',   label: 'DP Diterima'  },
    { value: 'progress',  label: 'Proses'       },
    { value: 'done',      label: 'Selesai'      },
    { value: 'lunas',     label: 'Lunas'        },
    { value: 'cancel',    label: 'Dibatalkan'   },
]

const sortOptions = [
    { value: 'newest',     label: 'Terbaru'         },
    { value: 'oldest',     label: 'Terlama'         },
    { value: 'scheduled',  label: 'Jadwal Terdekat' },
    { value: 'total_high', label: 'Harga Tertinggi' },
    { value: 'total_low',  label: 'Harga Terendah'  },
]
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>