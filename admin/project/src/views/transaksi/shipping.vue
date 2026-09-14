<template>
  <div class="min-h-screen bg-[#F7F8FC] font-sans">
    
    <!-- ── Header ─────────────────────────────── -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
      <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-200">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 011 1v2.5a1.5 1.5 0 01-3 0V16m-1 0h1m3 0h5l3 3v2a1 1 0 01-1 1h-1m-4-7V4a1 1 0 011-1h5a1 1 0 011 1v12a1 1 0 01-1 1h-1m-4 0h1" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Manajemen Pengiriman</h1>
            <p class="text-xs text-gray-400 mt-0.5">Padjajaran CCTV — Admin Panel</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <router-link to="/transaksi/list" class="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 active:scale-95 transition-all shadow-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M10 19l-7-7m0 0l7-7m-7 7h18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
            Daftar Transaksi
          </router-link>
        </div>
      </div>
    </div>

    <div class="max-w-screen-2xl mx-auto px-6 py-6 space-y-5">
      
      <!-- ── Stats Cards ─────────────────────── -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-400 uppercase tracking-wide">Perlu Dikirim</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">{{ totalPending }}</p>
            </div>
            <div class="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center">
              <svg class="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
          </div>
          <p class="text-xs mt-2 text-amber-600 font-medium">Menunggu input resi</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-400 uppercase tracking-wide">Sedang Dikirim</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">{{ totalShipped }}</p>
            </div>
            <div class="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            </div>
          </div>
          <p class="text-xs mt-2 text-blue-600 font-medium">Dalam perjalanan kurir</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-400 uppercase tracking-wide">Selesai</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">{{ totalDelivered }}</p>
            </div>
            <div class="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center">
              <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
          </div>
          <p class="text-xs mt-2 text-emerald-600 font-medium">Barang sudah diterima</p>
        </div>
      </div>

      <!-- ── Filter Bar ──────────────────────── -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
        <div class="flex flex-wrap gap-3 items-end">
          <div class="flex-1 min-w-56">
            <label class="block text-xs font-semibold text-gray-500 mb-1.5">Cari Pesanan</label>
            <div class="relative">
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              <input v-model="filters.search" @input="debounceSearch" type="text" placeholder="Cari Order ID atau nama pelanggan..." class="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all" />
            </div>
          </div>
          <div class="min-w-44">
            <label class="block text-xs font-semibold text-gray-500 mb-1.5">Status Filter</label>
            <select v-model="filters.status" @change="fetchData(true)" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all">
              <option value="settlement">Menunggu Pengiriman (Lunas)</option>
              <option value="SHIPPED">Sedang Dikirim</option>
              <option value="DELIVERED">Sudah Diterima</option>
            </select>
          </div>
          <button @click="fetchData(true)" class="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-100 transition-all flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
            Refresh
          </button>
        </div>
      </div>

      <!-- ── Table ──────────────────────────── -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-24">
          <div class="flex flex-col items-center gap-3">
            <div class="w-10 h-10 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
            <p class="text-sm text-gray-400 font-medium">Memuat data pengiriman...</p>
          </div>
        </div>

        <div v-else-if="!transactions.length" class="flex flex-col items-center justify-center py-24 gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center">
            <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 011 1v2.5a1.5 1.5 0 01-3 0V16m-1 0h1m3 0h5l3 3v2a1 1 0 01-1 1h-1m-4-7V4a1 1 0 011-1h5a1 1 0 011 1v12a1 1 0 01-1 1h-1m-4 0h1" /></svg>
          </div>
          <div class="text-center">
            <p class="text-sm font-semibold text-gray-600">Tidak ada transaksi ditemukan</p>
            <p class="text-xs text-gray-400 mt-1">Pastikan status pembayaran sudah lunas (Settlement)</p>
          </div>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50/80">
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Order ID</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Pelanggan</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Kurir & Resi</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="item in transactions" :key="item.uuid" class="group hover:bg-indigo-50/20 transition-colors">
                <td class="px-6 py-4 font-mono text-xs font-bold text-gray-900">{{ item.order_id }}</td>
                <td class="px-6 py-4">
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-gray-800">
                      {{ item.user?.email || item.raw_response?.customer_details?.email || 'Guest' }}
                    </span>
                    <span class="text-[10px] text-gray-400 uppercase tracking-wider">
                      {{ item.user?.username || item.raw_response?.customer_details?.full_name || 'No Name' }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex flex-col gap-1">
                    <div class="flex items-center gap-2">
                      <span class="px-2 py-0.5 bg-indigo-50 text-[10px] font-bold text-indigo-600 rounded uppercase border border-indigo-100">
                        {{ item.shipment?.courier_name || 'N/A' }}
                      </span>
                      <span v-if="item.shipment?.waybill_number" class="font-mono text-xs font-bold text-gray-900">
                        {{ item.shipment.waybill_number }}
                      </span>
                    </div>
                    <span class="text-[10px] text-gray-400 truncate max-w-[200px]" :title="item.shipment?.shipping_address">
                      {{ item.shipment?.shipping_address || 'No Address' }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 text-center">
                  <span :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border',
                    statusStyles(item.shipment?.delivery_status)
                  ]">
                    <span :class="['w-1.5 h-1.5 rounded-full', dotStyles(item.shipment?.delivery_status)]"></span>
                    {{ item.shipment?.delivery_status || 'PENDING' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button @click="openResiModal(item)" class="inline-flex items-center gap-1.5 px-4 py-2 bg-gray-900 text-white text-xs font-bold rounded-lg hover:bg-gray-800 active:scale-95 transition-all shadow-sm">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-5M16.243 3.243a3 3 0 114.243 4.243L9 18.172l-4 1L6 14l11.243-11.243z" /></svg>
                    Input Resi
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── Modal Update Resi ──────────────────── -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="resiModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="resiModal.show = false"></div>

          <!-- Modal Card -->
          <div class="modal-card relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col z-10">
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 class="text-sm font-bold text-gray-900">Input Nomor Resi</h3>
              <button @click="resiModal.show = false" class="p-1.5 text-gray-400 hover:text-gray-600 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
              </button>
            </div>

            <div class="p-6 space-y-4">
              <div class="grid grid-cols-2 gap-3">
                <div class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <p class="text-[10px] font-bold text-gray-400 uppercase mb-1">Order ID</p>
                  <p class="text-[11px] font-mono font-bold text-gray-700 truncate">{{ resiModal.order_id }}</p>
                </div>
                <div class="p-3 bg-indigo-50 rounded-xl border border-indigo-100">
                  <p class="text-[10px] font-bold text-indigo-400 uppercase mb-1">Kurir Pilihan User</p>
                  <p class="text-sm font-bold text-indigo-700">{{ resiModal.courier }}</p>
                </div>
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Nomor Resi (Waybill)</label>
                <input v-model="resiModal.waybill" type="text" placeholder="Masukkan nomor resi pengiriman..." class="w-full px-4 py-3 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 font-mono font-bold text-gray-900" />
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Status Pengiriman</label>
                <select v-model="resiModal.status" class="w-full px-4 py-3 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 transition-all font-bold text-gray-700">
                  <option value="SHIPPED">📦 Sedang Dikirim</option>
                  <option value="DELIVERED">✅ Pesanan Diterima</option>
                </select>
              </div>
            </div>

            <div class="p-6 bg-gray-50/50 border-t border-gray-100 flex gap-3">
              <button @click="resiModal.show = false" class="flex-1 px-4 py-2.5 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-100 transition-all">Batal</button>
              <button @click="submitResi" :disabled="resiModal.loading || !resiModal.waybill" class="flex-1 px-4 py-2.5 text-sm font-bold text-white bg-gray-900 rounded-xl hover:bg-gray-800 disabled:opacity-50 flex items-center justify-center gap-2 transition-all">
                <svg v-if="resiModal.loading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
                {{ resiModal.loading ? 'Menyimpan...' : 'Simpan Perubahan' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/service/api'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const route = useRoute()

const loading = ref(true)
const transactions = ref([])
const totalPending = ref(0)
const totalShipped = ref(0)
const totalDelivered = ref(0)
const filters = reactive({ 
  search: route.query.search || '', 
  status: route.query.status || 'settlement' 
})
const resiModal = reactive({
  show: false, loading: false,
  order_id: '', waybill: '', courier: 'JNE', status: 'SHIPPED'
})

let timer = null

async function fetchData(reset = false) {
  loading.value = true
  try {
    const params = {
      limit: 100, // Ambil lebih banyak untuk difilter
      transaction_status: 'settlement', // Hanya yang sudah lunas
    }
    
    const res = await api.get('/recap/transaksi', { params })
    const allData = res.data?.data || []
    
    // Hitung Stats dari data asli (hanya settlement)
    totalPending.value = allData.filter(t => !t.shipment?.waybill_number || t.shipment?.delivery_status === 'PENDING').length
    totalShipped.value = allData.filter(t => t.shipment?.waybill_number && t.shipment?.delivery_status !== 'DELIVERED').length
    totalDelivered.value = allData.filter(t => t.shipment?.delivery_status === 'DELIVERED').length

    // Filter untuk Tampilan
    let data = [...allData]
    if (filters.status === 'settlement') {
      // Perlu Dikirim: Lunas tapi belum ada resi atau status masih PENDING
      data = data.filter(t => !t.shipment?.waybill_number || t.shipment?.delivery_status === 'PENDING')
    } else if (filters.status === 'SHIPPED') {
      // Sedang Dikirim: Ada resi tapi belum DELIVERED
      data = data.filter(t => t.shipment?.waybill_number && t.shipment?.delivery_status !== 'DELIVERED')
    } else if (filters.status === 'DELIVERED') {
      data = data.filter(t => t.shipment?.delivery_status === 'DELIVERED')
    }

    if (filters.search) {
      const q = filters.search.toLowerCase()
      data = data.filter(t => 
        t.order_id.toLowerCase().includes(q) || 
        t.user?.username?.toLowerCase().includes(q) ||
        t.user?.email?.toLowerCase().includes(q)
      )
    }

    transactions.value = data
  } catch (e) {
    console.error(e)
    toastStore.error('Gagal mengambil data pengiriman')
  } finally {
    loading.value = false
  }
}

function debounceSearch() {
  clearTimeout(timer)
  timer = setTimeout(() => fetchData(), 400)
}

// Map order data to match inputs properly
function openResiModal(item) {
  resiModal.order_id = item.order_id
  resiModal.waybill = item.shipment?.waybill_number || ''
  resiModal.courier = item.shipment?.courier_name || 'JNE'
  resiModal.status = item.shipment?.delivery_status === 'PENDING' ? 'SHIPPED' : (item.shipment?.delivery_status || 'SHIPPED')
  resiModal.show = true
}

async function submitResi() {
  resiModal.loading = true
  try {
    await api.put(`/recap/transaksi/${resiModal.order_id}/waybill`, null, {
      params: {
        waybill_number: resiModal.waybill,
        courier_name: resiModal.courier,
        status: resiModal.status
      }
    })
    
    toastStore.success('Nomor resi berhasil diperbarui!')
    resiModal.show = false
    fetchData()
  } catch (e) {
    toastStore.error('Gagal mengupdate resi')
  } finally {
    resiModal.loading = false
  }
}

function statusStyles(s) {
  if (s === 'DELIVERED') return 'bg-emerald-50 text-emerald-700 border-emerald-100'
  if (s === 'SHIPPED') return 'bg-blue-50 text-blue-700 border-blue-100'
  return 'bg-amber-50 text-amber-700 border-amber-100'
}

// Dot styles helper
function dotStyles(s) {
  if (s === 'DELIVERED') return 'bg-emerald-500'
  if (s === 'SHIPPED') return 'bg-blue-500'
  return 'bg-amber-500'
}

onMounted(() => {
  if (route.query.search) {
    filters.search = route.query.search
  }
  if (route.query.status) {
    filters.status = route.query.status
  }
  fetchData()
})
</script>

<style scoped>
/* Modal Animation */
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.25s ease;
}
.modal-fade-enter-active .modal-card, .modal-fade-leave-active .modal-card {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .modal-card {
  transform: scale(0.95) translateY(12px);
  opacity: 0;
}
.modal-fade-leave-to .modal-card {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}
</style>
