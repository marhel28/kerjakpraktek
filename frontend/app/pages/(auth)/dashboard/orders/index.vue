<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

definePageMeta({ layout: 'public' })

const API_BASE = 'http://127.0.0.1:8000/transaksi'
const getToken = () => useCookie('token').value

// ─── State ───────────────────────────────────────────────
const transactions = ref<any[]>([])
const isLoading    = ref(true)
const activeTab    = ref('semua')
const searchQuery  = ref('')
const page         = ref(1)
const limit        = ref(10)
const totalPage    = ref(1)
const total        = ref(0)

// ─── Tabs ─────────────────────────────────────────────────
const tabs = [
  { id: 'semua',      label: 'Semua',           status: '' },
  { id: 'pending',    label: 'Belum Bayar',      status: 'pending' },
  { id: 'processing', label: 'Dikemas',          status: 'processing' },
  { id: 'shipped',    label: 'Dikirim',          status: 'shipped' },
  { id: 'settlement', label: 'Selesai',          status: 'settlement' },
  { id: 'cancel',     label: 'Dibatalkan',       status: 'cancel' },
]

// ─── Fetch ────────────────────────────────────────────────
const fetchTransactions = async () => {
  isLoading.value = true
  try {
    const queryParams: Record<string, any> = {
      page:  page.value,
      limit: limit.value,
      sort:  'desc',
    }

    // Status filter
    if (activeTab.value !== 'semua') {
      queryParams.status = activeTab.value
    }

    // Search hanya berlaku untuk transaksi reguler (stock_name)
    // di endpoint /my/all tidak ada stock_name, jadi kita kirim saja — backend ignore kalau tidak support
    if (searchQuery.value) queryParams.stock_name = searchQuery.value

    const response: any = await $fetch(`${API_BASE}/my/all`, {
      method: 'GET',
      query: queryParams,
      headers: { Authorization: `Bearer ${getToken()}` },
    })

    transactions.value = response.data      || []
    totalPage.value    = response.total_page || 1
    total.value        = response.total      || 0
  } catch (err: any) {
    console.error('Gagal mengambil data transaksi:', err)
    transactions.value = []
  } finally {
    isLoading.value = false
  }
}

watch([activeTab], () => {
  page.value = 1
  fetchTransactions()
})

watch(page, () => fetchTransactions())

let searchTimeout: ReturnType<typeof setTimeout> | null = null
const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    fetchTransactions()
  }, 500)
}

// ─── Utilities ────────────────────────────────────────────
const formatRupiah = (angka: number) =>
  new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(angka || 0)

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('id-ID', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  }).format(date)
}

/**
 * Hitung "order state" dari kombinasi payment status + shipment status.
 * Berlaku untuk transaksi reguler maupun promo.
 */
const getOrderState = (trx: any): string => {
  const tStatus = (trx.transaction_status || '').toLowerCase()
  const sStatus = (trx.shipment?.delivery_status || '').toLowerCase()

  if (['cancel', 'expire', 'deny'].includes(tStatus)) return 'cancel'
  if (['pending', 'pending_payment'].includes(tStatus))  return 'pending'

  if (['settlement', 'success', 'capture'].includes(tStatus)) {
    if (sStatus === 'shipped')                              return 'shipped'
    if (['delivered', 'completed'].includes(sStatus))      return 'settled'
    return 'processing'
  }
  return 'unknown'
}

const getStatusBadge = (trx: any) => {
  const state = getOrderState(trx)
  const map: Record<string, { text: string; cls: string }> = {
    pending:    { text: 'Menunggu Pembayaran', cls: 'bg-amber-50 text-amber-600 border-amber-200' },
    processing: { text: 'Sedang Dikemas',      cls: 'bg-blue-50 text-blue-600 border-blue-200' },
    shipped:    { text: 'Dikirim',             cls: 'bg-indigo-50 text-indigo-600 border-indigo-200' },
    settled:    { text: 'Selesai',             cls: 'bg-emerald-50 text-emerald-600 border-emerald-200' },
    cancel:     { text: 'Dibatalkan',          cls: 'bg-red-50 text-red-500 border-red-200' },
  }
  return map[state] || { text: trx.transaction_status || '-', cls: 'bg-gray-100 text-gray-500 border-gray-200' }
}

/** Badge kecil membedakan reguler vs promo */
const getTrxTypeBadge = (trx: any) => {
  if (trx.trx_type === 'promo') {
    return { text: trx.promo_name ? `Promo: ${trx.promo_name}` : 'Promo', cls: 'bg-purple-50 text-purple-600 border-purple-200' }
  }
  return { text: 'Reguler', cls: 'bg-gray-50 text-gray-500 border-gray-200' }
}

/** Ambil item pertama dari transaksi (reguler & promo punya field berbeda) */
const getFirstItem = (trx: any) => {
  if (!trx.items || trx.items.length === 0) return null
  const item = trx.items[0]
  return {
    name:      item.item_name  || item.stock_title || '-',
    qty:       item.quantity   || 1,
    unitPrice: item.unit_price || item.stock_online_price || 0,
    cover:     item.cover_image_url || null,
  }
}

// ─── Navigation ──────────────────────────────────────────
const payOrder    = (orderId: string) => navigateTo(`/payment/${orderId}`)
const viewDetail  = (orderId: string) => navigateTo(`/dashboard/orders/${orderId}`)

onMounted(() => fetchTransactions())
</script>

<template>
  <div class="min-h-screen bg-[#f3f4f5] py-8">
    <div class="container mx-auto px-4 max-w-[1200px] flex flex-col lg:flex-row gap-6">

      <AccountSidebar />

      <main class="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

        <!-- Header -->
        <header class="px-6 py-5 border-b border-gray-100">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 class="text-xl font-bold text-gray-900">Daftar Transaksi</h1>
              <p v-if="!isLoading" class="text-xs text-gray-400 mt-0.5">{{ total }} transaksi ditemukan</p>
            </div>
            <div class="relative w-full md:w-72">
              <input
                v-model="searchQuery"
                @input="handleSearch"
                type="text"
                placeholder="Cari nama produk..."
                class="w-full px-4 py-2 pl-10 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#03AC0E] outline-none transition"
              />
              <svg class="w-4 h-4 absolute left-3 top-2.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
          </div>
        </header>

        <!-- Tabs -->
        <div class="border-b border-gray-100 w-full overflow-x-auto no-scrollbar">
          <div class="flex px-2 min-w-max">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              class="px-5 py-3.5 text-sm font-semibold transition-colors border-b-[3px] whitespace-nowrap"
              :class="activeTab === tab.id
                ? 'border-[#03AC0E] text-[#03AC0E]'
                : 'border-transparent text-gray-500 hover:text-gray-700'"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="p-5 bg-gray-50/50 min-h-[500px]">

          <!-- Skeleton -->
          <div v-if="isLoading" class="space-y-4">
            <div v-for="i in 3" :key="i" class="w-full h-40 bg-white rounded-xl border border-gray-200 animate-pulse" />
          </div>

          <!-- Empty -->
          <div v-else-if="transactions.length === 0"
            class="flex flex-col items-center justify-center py-20 text-center"
          >
            <svg class="w-36 h-36 text-gray-300 mb-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <h3 class="text-lg font-bold text-gray-700">Belum ada transaksi</h3>
            <p class="text-gray-400 mt-1 text-sm max-w-xs">Anda belum memiliki pesanan di sini. Yuk mulai belanja!</p>
            <NuxtLink to="/" class="mt-5 px-8 py-2.5 bg-[#03AC0E] text-white font-bold rounded-lg hover:bg-[#028c0b] transition-colors shadow-sm text-sm">
              Mulai Belanja
            </NuxtLink>
          </div>

          <!-- List -->
          <div v-else class="space-y-3">
            <div
              v-for="trx in transactions"
              :key="trx.uuid"
              class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden"
            >
              <!-- Card Header -->
              <div class="flex flex-wrap items-center justify-between gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/60">
                <div class="flex flex-wrap items-center gap-2">
                  <!-- Tanggal -->
                  <span class="text-xs text-gray-500">{{ formatDate(trx.created_at) }}</span>
                  <span class="text-gray-300 hidden sm:block">|</span>
                  <!-- Order ID -->
                  <span class="text-xs font-mono font-semibold text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                    {{ trx.order_id }}
                  </span>
                  <!-- Promo / Reguler badge -->
                  <span
                    class="text-xs font-semibold px-2 py-0.5 rounded border"
                    :class="getTrxTypeBadge(trx).cls"
                  >
                    {{ getTrxTypeBadge(trx).text }}
                  </span>
                </div>
                <!-- Status Badge -->
                <span
                  class="text-xs font-bold px-3 py-1 rounded-md border"
                  :class="getStatusBadge(trx).cls"
                >
                  {{ getStatusBadge(trx).text }}
                </span>
              </div>

              <!-- Card Body -->
              <div class="px-5 py-4 flex flex-col md:flex-row gap-4 items-start">

                <!-- Gambar produk pertama -->
                <div class="w-16 h-16 flex-shrink-0 rounded-lg overflow-hidden border border-gray-100 bg-gray-50">
                  <template v-if="getFirstItem(trx)?.cover">
                    <NuxtImg
                      :src="getFirstItem(trx)!.cover"
                      class="w-full h-full object-cover"
                      alt="Produk"
                    />
                  </template>
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <svg class="w-7 h-7 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14M14 8h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                  </div>
                </div>

                <!-- Info produk -->
                <div class="flex-1 min-w-0">
                  <h3 class="font-bold text-gray-900 text-sm line-clamp-1">
                    {{ getFirstItem(trx)?.name || '-' }}
                  </h3>
                  <p class="text-xs text-gray-500 mt-0.5">
                    {{ getFirstItem(trx)?.qty }} barang
                    <span v-if="getFirstItem(trx)?.unitPrice"> × {{ formatRupiah(getFirstItem(trx)!.unitPrice) }}</span>
                  </p>

                  <!-- +N produk lainnya -->
                  <p v-if="trx.items && trx.items.length > 1" class="text-xs font-semibold text-gray-400 mt-1">
                    + {{ trx.items.length - 1 }} produk lainnya
                  </p>

                  <!-- Kurir -->
                  <div v-if="trx.shipment?.courier_name"
                    class="mt-2 inline-flex items-center gap-1.5 px-2 py-1 bg-gray-50 border border-gray-100 rounded text-xs text-gray-500"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l3 5v6H8m12-11V7m-5 5h5m-5 0v3m0-3l-3-5m-7 5v6H3V7h5m0 5h5m-5 0v3m0-3l-3-5"/>
                    </svg>
                    <span class="font-semibold uppercase">{{ trx.shipment.courier_name }} {{ trx.shipment.courier_service }}</span>
                  </div>

                  <!-- Jika promo: tampilkan diskon -->
                  <div v-if="trx.trx_type === 'promo' && trx.total_discount > 0"
                    class="mt-2 inline-flex items-center gap-1 px-2 py-1 bg-purple-50 border border-purple-100 rounded text-xs text-purple-600 font-semibold"
                  >
                    🏷 Hemat {{ formatRupiah(trx.total_discount) }}
                  </div>
                </div>

                <!-- Total & Actions -->
                <div class="flex flex-col items-end gap-3 w-full md:w-auto border-t md:border-t-0 pt-3 md:pt-0 border-gray-100">
                  <div class="text-right">
                    <p class="text-xs text-gray-400">Total Belanja</p>
                    <p class="text-lg font-bold text-gray-900">{{ formatRupiah(trx.gross_amount) }}</p>
                  </div>

                  <!-- CTA buttons -->
                  <div class="flex gap-2 w-full md:w-auto">
                    <button
                      @click="viewDetail(trx.order_id)"
                      class="flex-1 md:flex-none px-4 py-2 text-xs font-bold text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Detail
                    </button>

                    <!-- Bayar Sekarang (pending) -->
                    <button
                      v-if="getOrderState(trx) === 'pending'"
                      @click="payOrder(trx.order_id)"
                      class="flex-1 md:flex-none px-4 py-2 text-xs font-bold text-white bg-[#03AC0E] rounded-lg hover:bg-[#028c0b] transition-colors shadow-sm"
                    >
                      Bayar Sekarang
                    </button>

                    <!-- Lacak Resi (shipped) -->
                    <button
                      v-else-if="getOrderState(trx) === 'shipped'"
                      @click="viewDetail(trx.order_id)"
                      class="flex-1 md:flex-none px-4 py-2 text-xs font-bold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
                    >
                      Lacak Resi
                    </button>

                    <!-- Beli Lagi (settled) -->
                    <button
                      v-else-if="getOrderState(trx) === 'settled'"
                      class="flex-1 md:flex-none px-4 py-2 text-xs font-bold text-[#03AC0E] bg-green-50 border border-[#03AC0E] rounded-lg hover:bg-green-100 transition-colors"
                    >
                      Beli Lagi
                    </button>
                  </div>
                </div>

              </div>
            </div>

            <!-- Pagination -->
            <div v-if="totalPage > 1" class="flex items-center justify-center gap-2 pt-4">
              <button
                @click="page--"
                :disabled="page <= 1"
                class="px-4 py-2 text-sm font-semibold rounded-lg border border-gray-300 disabled:opacity-40 hover:bg-gray-50 transition"
              >
                ← Prev
              </button>
              <span class="text-sm text-gray-500 px-2">
                Hal {{ page }} / {{ totalPage }}
              </span>
              <button
                @click="page++"
                :disabled="page >= totalPage"
                class="px-4 py-2 text-sm font-semibold rounded-lg border border-gray-300 disabled:opacity-40 hover:bg-gray-50 transition"
              >
                Next →
              </button>
            </div>

          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>