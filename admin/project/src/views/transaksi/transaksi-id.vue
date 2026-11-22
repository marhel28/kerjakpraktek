<template>
    <div class="min-h-screen bg-slate-50 font-sans">
        <div class="max-w-5xl mx-auto px-5 py-8">

            <!-- Back -->
            <router-link to="/transaksi/list"
                class="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-6 transition group">
                <svg class="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Kembali ke Daftar
            </router-link>

            <!-- Loading -->
            <div v-if="loading" class="space-y-4">
                <div class="bg-white rounded-2xl p-6 h-24 animate-pulse border border-slate-100" />
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div v-for="n in 3" :key="n"
                        class="bg-white rounded-2xl p-6 h-40 animate-pulse border border-slate-100" />
                </div>
            </div>

            <!-- Not Found -->
            <div v-else-if="!trx" class="text-center py-24 bg-white rounded-2xl border border-slate-100 shadow-sm">
                <svg class="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p class="font-semibold text-slate-700">Transaksi tidak ditemukan</p>
                <p class="text-sm text-slate-400 mt-1">
                    ID: <span class="font-mono">{{ routeParamId || '-' }}</span>
                </p>
            </div>

            <template v-else>
                <!-- ── Page Header ─────────────────────────────────────── -->
                <div
                    class="bg-white rounded-2xl border border-slate-100 shadow-sm px-6 py-4 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div class="flex flex-col gap-1">
                        <div class="flex items-center gap-3 flex-wrap">
                            <span class="font-mono text-lg font-bold text-slate-900">{{ trx.order_id }}</span>
                            <StatusBadge type="payment" :status="trx.transaction_status" />
                            <StatusBadge v-if="trx.shipment" type="delivery" :status="trx.shipment.delivery_status" />
                        </div>
                        <div class="flex items-center gap-2 text-xs text-slate-400">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            Dibuat: {{ formatDate(trx.created_at) }}
                        </div>
                    </div>
                    
                    <div class="flex items-center gap-2">
                        <button @click="copyOrderId" class="p-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition" title="Salin Order ID">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m-3 8.5V11a.5.5 0 00-.5-.5H11m4 5.5a2 2 0 11-4 0 2 2 0 014 0z" />
                            </svg>
                        </button>
                        <a v-if="trx.snap_token" :href="`${trx.payment_url}`" target="_blank" class="px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-xl hover:bg-indigo-700 transition shadow-sm shadow-indigo-200 flex items-center gap-2">
                            Snap Payment Page
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                        </a>
                    </div>
                </div>

                <!-- ── Main Grid ──────────────────────────────────────── -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">

                    <!-- Payment Info -->
                    <InfoCard title="Info Pembayaran" subtitle="Midtrans Gateway"
                        icon="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
                        icon-bg="bg-emerald-50" icon-color="text-emerald-600">
                        <dl class="space-y-3">
                            <div class="flex justify-between items-center gap-2">
                                <dt class="text-xs text-slate-500 font-medium">Metode</dt>
                                <dd class="text-xs font-bold text-slate-900 capitalize">{{ trx.payment_type || '-' }}</dd>
                            </div>
                            <div class="flex justify-between items-center gap-2">
                                <dt class="text-xs text-slate-500 font-medium">Status</dt>
                                <dd><StatusBadge type="payment" :status="trx.transaction_status" /></dd>
                            </div>
                            <div class="flex justify-between items-center gap-2 pt-1 border-t border-slate-50">
                                <dt class="text-xs text-slate-500 font-medium">Waktu Transaksi</dt>
                                <dd class="text-xs text-slate-700 text-right">{{ trx.transaction_time ? formatDate(trx.transaction_time) : '-' }}</dd>
                            </div>
                            <div v-if="trx.settlement_time" class="flex justify-between items-center gap-2">
                                <dt class="text-xs text-slate-500 font-medium">Waktu Settlement</dt>
                                <dd class="text-xs text-slate-700 text-right">{{ formatDate(trx.settlement_time) }}</dd>
                            </div>
                        </dl>
                    </InfoCard>

                    <!-- Column 2 (Shipping / Booking + Action Card) -->
                    <div class="flex flex-col gap-4">
                        <!-- Shipment Info -->
                        <InfoCard v-if="trx.trx_type === 'regular' || trx.shipment" title="Info Pengiriman" subtitle="Kurir & Tujuan"
                            icon="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" icon-bg="bg-blue-50"
                            icon-color="text-blue-600">
                            <div v-if="trx.shipment">
                                <dl class="space-y-3">
                                    <div class="flex justify-between items-center gap-2">
                                        <dt class="text-xs text-slate-500 font-medium">Kurir</dt>
                                        <dd class="text-xs font-bold text-slate-900 uppercase">
                                            {{ trx.shipment.courier_name }} <span class="text-slate-300 mx-1">/</span> {{ trx.shipment.courier_service }}
                                        </dd>
                                    </div>
                                    <div class="flex justify-between items-center gap-2">
                                        <dt class="text-xs text-slate-500 font-medium">No. Resi</dt>
                                        <dd class="text-xs font-mono font-bold text-indigo-600">{{ trx.shipment.waybill_number || 'Belum diinput' }}</dd>
                                    </div>
                                    <div class="flex justify-between items-center gap-2 pt-1 border-t border-slate-50">
                                        <dt class="text-xs text-slate-500 font-medium">Penerima</dt>
                                        <dd class="text-xs text-slate-900 font-medium text-right">{{ trx.shipment.recipient_name }}</dd>
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <dt class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Alamat Tujuan</dt>
                                        <dd class="text-xs text-slate-600 leading-relaxed">{{ trx.shipment.shipping_address }}</dd>
                                    </div>
                                </dl>
                            </div>
                            <div v-else class="flex flex-col items-center justify-center py-6 text-center">
                                <svg class="w-8 h-8 text-slate-200 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0a2 2 0 01-2 2H6a2 2 0 01-2-2m16 0l-8 4-8-4" />
                                </svg>
                                <p class="text-xs text-slate-400 font-medium">Tidak ada data pengiriman</p>
                            </div>
                        </InfoCard>

                        <!-- Booking Card -->
                        <InfoCard v-else-if="trx.trx_type === 'booking' || trx.booking" title="Info Booking" subtitle="Layanan & Jadwal"
                            icon="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" icon-bg="bg-amber-50"
                            icon-color="text-amber-600">
                            <div v-if="trx.booking">
                                <dl class="space-y-3">
                                    <div class="flex justify-between items-center gap-2">
                                        <dt class="text-xs text-slate-500 font-medium">Layanan</dt>
                                        <dd class="text-xs font-bold text-slate-900 uppercase text-right">{{ trx.booking.service_name || 'Service' }}</dd>
                                    </div>
                                    <div class="flex justify-between items-center gap-2">
                                        <dt class="text-xs text-slate-500 font-medium">Status</dt>
                                        <dd><StatusBadge type="delivery" :status="trx.booking.booking_status || 'PENDING'" /></dd>
                                    </div>
                                    <div class="flex justify-between items-center gap-2 pt-1 border-t border-slate-50">
                                        <dt class="text-xs text-slate-500 font-medium">Jadwal</dt>
                                        <dd class="text-xs text-slate-900 font-bold text-right">{{ formatDate(trx.booking.booking_date) }}</dd>
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <dt class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Catatan User</dt>
                                        <dd class="text-xs text-slate-600 italic">"{{ trx.booking.notes || 'Tidak ada catatan' }}"</dd>
                                    </div>
                                </dl>
                            </div>
                        </InfoCard>

                        <!-- Aksi Pengiriman Card -->
                        <div v-if="(trx.trx_type === 'regular' || trx.shipment) && trx.shipment" class="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 flex flex-col justify-between gap-3">
                            <div class="flex items-center gap-2.5">
                                <div class="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
                                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="text-sm font-bold text-slate-800">Aksi Pengiriman</h3>
                                    <p class="text-[10px] text-slate-400 mt-0.5">Kelola Resi & Logistik</p>
                                </div>
                            </div>
                            <p class="text-xs text-slate-500 leading-relaxed mt-1">
                                Pesanan ini memerlukan pengiriman kurir. Silakan masukkan nomor resi pengiriman untuk melacak logistik dan memberikan notifikasi pengiriman kepada pelanggan.
                            </p>
                            <div class="pt-3 border-t border-slate-50 flex items-center justify-between gap-3">
                                <div class="flex flex-col">
                                    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Status Kirim</span>
                                    <span class="text-xs font-bold text-slate-700 mt-0.5">{{ trx.shipment.delivery_status }}</span>
                                </div>
                                <button 
                                  @click="goToFillWaybill"
                                  class="py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition shadow-sm shadow-indigo-100 flex items-center gap-1.5 active:scale-95"
                                >
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                    </svg>
                                    Lanjutkan Isi Resi
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Price Breakdown -->
                    <InfoCard title="Rincian Biaya" subtitle="Final Kalkulasi"
                        icon="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"
                        icon-bg="bg-violet-50" icon-color="text-violet-600">
                        <dl class="space-y-3">
                            <div class="flex justify-between">
                                <dt class="text-xs text-slate-500">Subtotal Produk</dt>
                                <dd class="text-xs font-bold text-slate-800 font-mono">{{ formatRp(trx.items_subtotal) }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-xs text-slate-500">Biaya Kirim</dt>
                                <dd class="text-xs font-bold text-slate-800 font-mono">{{ formatRp(trx.shipping_cost) }}</dd>
                            </div>
                            <div v-if="trx.service_cost" class="flex justify-between">
                                <dt class="text-xs text-slate-500">Biaya Layanan</dt>
                                <dd class="text-xs font-bold text-slate-800 font-mono">{{ formatRp(trx.service_cost) }}</dd>
                            </div>
                            <div v-if="trx.total_discount" class="flex justify-between">
                                <dt class="text-xs text-emerald-600">Promo / Diskon</dt>
                                <dd class="text-xs font-bold text-emerald-600 font-mono">- {{ formatRp(trx.total_discount) }}</dd>
                            </div>
                            <div class="border-t border-slate-100 pt-3 flex justify-between items-center">
                                <dt class="text-sm font-black text-slate-900">GRAND TOTAL</dt>
                                <dd class="text-lg font-black text-slate-900 font-mono">{{ formatRp(trx.gross_amount) }}</dd>
                            </div>
                        </dl>
                    </InfoCard>
                </div>

                <!-- ── Items List ─────────────────────────────────────── -->
                <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden mb-4">
                    <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                        <div class="flex items-center gap-2.5">
                            <div class="w-7 h-7 bg-amber-50 rounded-lg flex items-center justify-center shrink-0">
                                <svg class="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                </svg>
                            </div>
                            <div>
                                <h3 class="text-sm font-bold text-slate-800">Daftar Produk</h3>
                                <p class="text-xs text-slate-400 mt-0.5">{{ trx.items?.length || 0 }} Item dibeli</p>
                            </div>
                        </div>
                    </div>
                    <div class="p-5">
                        <div class="space-y-4">
                            <div v-for="item in trx.items" :key="item.stock_uuid"
                                class="flex items-start gap-4 p-4 bg-slate-50 rounded-2xl border border-slate-100/80 group hover:border-indigo-100 transition shadow-sm hover:shadow-md">
                                <!-- Thumbnail -->
                                <div class="w-16 h-16 rounded-xl overflow-hidden bg-white border border-slate-200 shrink-0 shadow-sm">
                                    <img v-if="item.cover_image_url" :src="item.cover_image_url" :alt="item.stock_title"
                                        class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" loading="lazy" />
                                    <div v-else class="w-full h-full flex items-center justify-center bg-slate-50">
                                        <svg class="w-6 h-6 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                    </div>
                                </div>
                                <!-- Info -->
                                <div class="flex-1 min-w-0 py-0.5">
                                    <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                                        <div>
                                            <p class="text-sm font-bold text-slate-900 line-clamp-1 group-hover:text-indigo-600 transition">{{ item.item_name }}</p>
                                            <p v-if="item.brand" class="text-[11px] font-bold text-indigo-500 uppercase tracking-widest mt-0.5">{{ item.brand }}</p>
                                        </div>
                                        <div class="text-right shrink-0">
                                            <p class="text-sm font-black text-slate-900 font-mono">{{ formatRp(item.subtotal) }}</p>
                                            <p class="text-[11px] text-slate-400 font-medium">{{ formatRp(item.unit_price) }} × {{ item.quantity }}</p>
                                        </div>
                                    </div>
                                    
                                    <!-- Specs -->
                                    <div v-if="item.specs && Object.keys(item.specs).length > 0" class="flex flex-wrap gap-1.5 mt-3">
                                        <span v-for="(value, key) in item.specs" :key="key" 
                                            class="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 bg-white border border-slate-200 text-slate-500 rounded-lg capitalize shadow-xs">
                                            <span class="font-bold text-slate-400">{{ key.replace('_', ' ') }}:</span>
                                            <span class="font-black text-slate-700">{{ value }}</span>
                                        </span>
                                    </div>

                                    <!-- Addons -->
                                    <div v-if="item.addons && item.addons.length > 0" class="mt-3 space-y-2 border-l-2 border-emerald-500 pl-3 py-0.5 bg-emerald-50/30 rounded-r-xl">
                                        <div v-for="(addon, idx) in item.addons" :key="idx" class="flex justify-between items-center text-[11px]">
                                            <span class="text-slate-600 font-medium">↳ {{ addon.name }} (x{{ addon.quantity }})</span>
                                            <span class="text-emerald-600 font-bold font-mono">+ {{ formatRp(addon.price * addon.quantity) }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ── Raw Data ─────────────────────────────────────── -->
                <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                    <button @click="rawExpanded = !rawExpanded"
                        class="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-slate-50/80 transition">
                        <div class="flex items-center gap-2.5">
                            <div class="w-7 h-7 bg-slate-100 rounded-lg flex items-center justify-center">
                                <svg class="w-3.5 h-3.5 text-slate-600" fill="none" stroke="currentColor"
                                    viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-sm font-bold text-slate-800">Raw Data</p>
                                <p class="text-xs text-slate-400">JSON response dari server</p>
                            </div>
                        </div>
                        <svg :class="['w-4 h-4 text-slate-400 transition-transform', rawExpanded && 'rotate-180']"
                            fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                        </svg>
                    </button>
                    <Transition name="slide">
                        <div v-if="rawExpanded" class="border-t border-slate-100">
                            <pre
                                class="p-5 text-xs text-slate-600 bg-slate-900 text-indigo-300 overflow-x-auto leading-relaxed font-mono rounded-b-2xl max-h-96 overflow-y-auto">{{ JSON.stringify(trx, null, 2) }}</pre>
                        </div>
                    </Transition>
                </div>
            </template>

        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/service/api'
import StatusBadge from '@/components/StatusBadge.vue'
import InfoCard from '@/components/InfoCard.vue'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()
const loading = ref(true)
const trx = ref(null)
const rawExpanded = ref(false)

// [PENTING] Menangkap ID dari berbagai kemungkinan param router
const routeParamId = computed(() => {
    return route.params.uuid || route.params.id || route.params.order_id || route.path.split('/').pop() || null;
})

async function fetchDetail() {
    const id = routeParamId.value;
    if (!id || id === 'transaksi') return;

    loading.value = true
    try {
        console.log(`📡 Fetching detail: /transaksi/detail/${id}`);
        const { data } = await api.get(`/transaksi/detail/${id}`)
        
        // Fix: API response is { success: true, data: { ... } }
        if (data && data.success) {
            trx.value = data.data
            console.log("✅ Data detail berhasil dimuat:", trx.value);
        } else {
            console.warn("⚠️ API sukses tapi data.success false atau data kosong", data);
            trx.value = null
        }
        
    } catch (e) {
        console.error("❌ Gagal memuat detail transaksi:", e)
        trx.value = null
        toastStore.error("Gagal memuat detail transaksi")
    } finally {
        loading.value = false
    }
}

// Format IDR helper
function formatRp(n) {
    if (n == null) return 'Rp 0'
    return 'Rp ' + Number(n).toLocaleString('id-ID')
}

function formatDate(d) {
    if (!d) return '-'
    try {
        return new Date(d).toLocaleDateString('id-ID', { 
            day: '2-digit', 
            month: 'short', 
            year: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        })
    } catch (e) {
        return d
    }
}

function copyOrderId() {
    if (!trx.value?.order_id) return
    navigator.clipboard.writeText(trx.value.order_id)
    toastStore.success("Order ID berhasil disalin!")
}

// Watcher untuk handle pergantian route ID di URL yang sama
watch(() => route.params.uuid, (newVal) => {
    if (newVal) fetchDetail()
})

function goToFillWaybill() {
    if (trx.value?.order_id) {
        router.push(`/transaksi/shipping?search=${trx.value.order_id}`)
    }
}

onMounted(fetchDetail)
</script>

<style scoped>
@reference "tailwindcss";

.slide-enter-active,
.slide-leave-active {
    transition: all .25s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-enter-from,
.slide-leave-to {
    opacity: 0;
    transform: translateY(-8px);
}

/* Custom shadow for cards */
.shadow-xs {
    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}
</style>