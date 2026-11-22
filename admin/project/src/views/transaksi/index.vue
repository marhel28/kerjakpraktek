<template>
    <div class="min-h-screen bg-slate-50 font-sans">
        <div class="max-w-7xl mx-auto px-5 py-8">

            <!-- Header -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-7">
                <div>
                    <div class="flex items-center gap-2.5 mb-1">
                        <div class="w-8 h-8 bg-slate-900 rounded-xl flex items-center justify-center">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                        </div>
                        <h1 class="text-xl font-bold text-slate-900">Manajemen Transaksi</h1>
                    </div>
                    <p class="text-sm text-slate-500 ml-10.5">Semua transaksi pembelian barang</p>
                </div>

                <!-- Nav pills -->
                <div class="flex items-center gap-2">
                    <NuxtLink to="/transaksi" class="nav-pill active">Semua</NuxtLink>
                    <NuxtLink to="/transaksi/payment" class="nav-pill">Pembayaran</NuxtLink>
                    <NuxtLink to="/transaksi/shipping" class="nav-pill">Pengiriman</NuxtLink>
                </div>
            </div>

            <!-- Stats -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
                <div v-for="s in summaryStats" :key="s.label"
                    class="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-3">
                    <div :class="['w-9 h-9 rounded-xl flex items-center justify-center shrink-0', s.bg]">
                        <svg class="w-4 h-4" :class="s.color" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="s.icon" />
                        </svg>
                    </div>
                    <div>
                        <p class="text-lg font-bold text-slate-900 leading-none">{{ s.value }}</p>
                        <p class="text-xs text-slate-400 mt-0.5">{{ s.label }}</p>
                    </div>
                </div>
            </div>

            <!-- Filter Bar -->
            <div
                class="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 mb-4 flex flex-wrap items-center gap-3">
                <!-- Search -->
                <div class="relative flex-1 min-w-[200px]">
                    <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none"
                        stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0" />
                    </svg>
                    <input v-model="filters.search" @input="debounceSearch" type="text"
                        placeholder="Cari Order ID atau nama produk…"
                        class="w-full pl-9 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition" />
                </div>
                <!-- Status filter -->
                <select v-model="filters.status" @change="fetchTransactions(true)"
                    class="px-3 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900 transition text-slate-700">
                    <option value="">Semua Status</option>
                    <option value="pending_payment">Menunggu</option>
                    <option value="settlement">Lunas</option>
                    <option value="cancel">Dibatalkan</option>
                    <option value="expire">Kedaluwarsa</option>
                    <option value="failed">Gagal</option>
                    <option value="refund">Refund</option>
                </select>
                <!-- Amount range -->
                <div class="flex items-center gap-2">
                    <div class="relative">
                        <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-slate-400">Rp</span>
                        <input v-model.number="filters.min_amount" @change="fetchTransactions(true)" type="number"
                            placeholder="Min" min="0"
                            class="pl-8 pr-3 py-2.5 w-28 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900 transition font-mono" />
                    </div>
                    <span class="text-slate-300">-</span>
                    <div class="relative">
                        <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-slate-400">Rp</span>
                        <input v-model.number="filters.max_amount" @change="fetchTransactions(true)" type="number"
                            placeholder="Max" min="0"
                            class="pl-8 pr-3 py-2.5 w-28 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900 transition font-mono" />
                    </div>
                </div>
                <!-- Reset -->
                <button @click="resetFilters"
                    class="px-3 py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-700 hover:bg-slate-50 rounded-xl transition border border-slate-200">
                    Reset
                </button>
            </div>

            <!-- Table -->
            <TransactionTable :columns="columns" :rows="transactions" :loading="loading" :clickable="true"
                :page="pagination.page" :limit="pagination.limit" :total="pagination.total"
                :total-page="pagination.totalPage" empty-text="Belum ada transaksi ditemukan" @row-click="goDetail"
                @update:page="changePage">
                <template #row="{ row }">
                    <td class="px-4 py-3.5">
                        <span class="font-mono text-xs font-bold text-slate-700">{{ row.order_id }}</span>
                    </td>
                    <td class="px-4 py-3.5">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-white rounded-lg border border-slate-100 overflow-hidden shrink-0 flex items-center justify-center p-1">
                                <img v-if="row.items?.[0]?.thumbnail_url" :src="row.items[0].thumbnail_url" alt="Gambar produk" class="w-full h-full object-contain" />
                                <svg v-else class="w-5 h-5 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                            </div>
                            <div class="flex flex-col min-w-0">
                                <span class="text-sm font-bold text-slate-700 truncate max-w-[180px]" :title="row.items?.[0]?.stock_title">
                                    {{ row.items?.[0]?.stock_title || 'No Title' }}
                                </span>
                                <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                    {{ row.items?.length > 1 ? `+${row.items.length - 1} Produk Lain` : '1 Produk' }}
                                </span>
                            </div>
                        </div>
                    </td>
                    <td class="px-4 py-3.5">
                        <div class="flex flex-col gap-0.5">
                            <span class="text-sm font-semibold text-slate-900 font-mono">{{ formatRp(row.gross_amount)
                                }}</span>
                            <span class="text-xs text-slate-400">Ongkir {{ formatRp(row.shipping_cost) }}</span>
                        </div>
                    </td>
                    <td class="px-4 py-3.5">
                        <StatusBadge type="payment" :status="row.transaction_status" />
                    </td>
                    <td class="px-4 py-3.5">
                        <StatusBadge v-if="row.shipment" type="delivery" :status="row.shipment.delivery_status" />
                        <span v-else class="text-slate-300">-</span>
                    </td>
                    <td class="px-4 py-3.5 text-xs text-slate-500 whitespace-nowrap">
                        {{ formatDate(row.created_at) }}
                    </td>
                    <td class="px-4 py-3.5">
                        <button
                            class="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition"
                            @click.stop="goDetail(row)">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M9 5l7 7-7 7" />
                            </svg>
                        </button>
                    </td>
                </template>
            </TransactionTable>

        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/service/api'
import TransactionTable from '@/components/TransactionTable.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { formatDateTime } from '@/service/datetime'

const router = useRouter()
const route = useRoute()

// ── State ──────────────────────────────────────────────────────────
const loading = ref(true)
const transactions = ref([])
const pagination = reactive({ page: 1, limit: 10, total: 0, totalPage: 1 })
const filters = reactive({ search: '', status: route.query.status || '', min_amount: null, max_amount: null })
const summary = ref({ lunas: 0, pending: 0 })

let searchTimer = null

const columns = [
    { key: 'order_id', label: 'Order ID' },
    { key: 'produk', label: 'Produk' },
    { key: 'total', label: 'Total' },
    { key: 'payment', label: 'Pembayaran' },
    { key: 'delivery', label: 'Pengiriman' },
    { key: 'tanggal', label: 'Tanggal' },
    { key: 'aksi', label: '', thClass: 'w-10' },
]

// ── Computed Stats ─────────────────────────────────────────────────
const summaryStats = computed(() => [
    {
        label: 'Total Transaksi',
        value: pagination.total,
        bg: 'bg-slate-100', color: 'text-slate-600',
        icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
    },
    {
        label: 'Lunas',
        value: summary.value.lunas,
        bg: 'bg-emerald-50', color: 'text-emerald-600',
        icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    },
    {
        label: 'Menunggu',
        value: summary.value.pending,
        bg: 'bg-amber-50', color: 'text-amber-600',
        icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    },
    {
        label: 'Dibatalkan',
        value: transactions.value.filter(t => ['cancel', 'expire', 'failed'].includes(t.transaction_status)).length,
        bg: 'bg-red-50', color: 'text-red-500',
        icon: 'M6 18L18 6M6 6l12 12',
    },
])

// ── API ────────────────────────────────────────────────────────────
async function fetchTransactions(resetPage = false) {
    if (resetPage) pagination.page = 1
    loading.value = true
    try {
        const params = {
            page: pagination.page,
            limit: pagination.limit,
            sort_by: 'created_at',
            sort_order: 'desc',
        }
        if (filters.status) params.transaction_status = filters.status
        if (filters.min_amount) params.min_amount = filters.min_amount
        if (filters.max_amount) params.max_amount = filters.max_amount
        if (filters.search) params.stock_name = filters.search

        const { data } = await api.get('/recap/transaksi', { params })
        transactions.value = data.data || []
        pagination.total = data.total || 0
        pagination.totalPage = data.total_page || 1
        if (data.summary) summary.value = data.summary
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

function debounceSearch() {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => fetchTransactions(true), 400)
}

function changePage(p) {
    pagination.page = p
    fetchTransactions()
}

function resetFilters() {
    filters.search = ''
    filters.status = ''
    filters.min_amount = null
    filters.max_amount = null
    fetchTransactions(true)
}

function goDetail(row) {
    router.push(`/transaksi/${row.order_id}`)
}

// ── Helpers ────────────────────────────────────────────────────────
function formatRp(n) {
    return n != null ? 'Rp ' + Number(n).toLocaleString('id-ID') : 'Rp 0'
}

function formatDate(d) {
    return formatDateTime(d)
}

onMounted(() => fetchTransactions())
</script>

<style scoped>
@reference "tailwindcss"; 
.nav-pill {
    @apply px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-500 hover:bg-white hover:text-slate-800 hover:shadow-sm transition border border-transparent;
}

.nav-pill.active {
    @apply bg-white text-slate-900 shadow-sm border-slate-200;
}

.line-clamp-1 {
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>