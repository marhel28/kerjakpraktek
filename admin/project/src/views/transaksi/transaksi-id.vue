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
                <div class="grid grid-cols-3 gap-4">
                    <div v-for="n in 3" :key="n"
                        class="bg-white rounded-2xl p-6 h-40 animate-pulse border border-slate-100" />
                </div>
            </div>

            <!-- Not Found / Missing Param -->
            <div v-else-if="!trx" class="text-center py-24 bg-white rounded-2xl border border-slate-100 shadow-sm">
                <svg class="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p class="font-semibold text-slate-700">Transaksi tidak ditemukan</p>
                <p class="text-sm text-slate-400 mt-1">
                    Order ID: <span class="font-mono">{{ routeParamId || 'Parameter Tidak Terbaca' }}</span>
                </p>
            </div>

            <template v-else>
                <!-- ── Page Header ─────────────────────────────────────── -->
                <div
                    class="bg-white rounded-2xl border border-slate-100 shadow-sm px-6 py-4 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div class="flex items-center gap-3 flex-wrap">
                        <span class="font-mono text-lg font-bold text-slate-900">{{ trx.order_id }}</span>
                        <StatusBadge type="payment" :status="trx.transaction_status" />
                        <StatusBadge v-if="trx.shipment" type="delivery" :status="trx.shipment.delivery_status" />
                    </div>
                    <div class="flex items-center gap-2 text-xs text-slate-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        {{ formatDate(trx.created_at) }}
                    </div>
                </div>

                <!-- ── Main Grid ──────────────────────────────────────── -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">

                    <!-- Payment Info -->
                    <InfoCard title="Info Pembayaran" subtitle="Detail transaksi Midtrans"
                        icon="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
                        icon-bg="bg-emerald-50" icon-color="text-emerald-600">
                        <dl class="space-y-2.5">
                            <div class="flex justify-between items-start gap-2">
                                <dt class="text-xs text-slate-500">Metode</dt>
                                <dd class="text-xs font-semibold text-slate-800 capitalize text-right">{{
                                    trx.payment_type || '—' }}</dd>
                            </div>
                            <div class="flex justify-between items-start gap-2">
                                <dt class="text-xs text-slate-500">Status</dt>
                                <dd>
                                    <StatusBadge type="payment" :status="trx.transaction_status" />
                                </dd>
                            </div>
                            <div class="flex justify-between items-start gap-2">
                                <dt class="text-xs text-slate-500">Waktu Bayar</dt>
                                <dd class="text-xs text-slate-700 text-right">{{ trx.transaction_time ?
                                    formatDate(trx.transaction_time) : '—' }}</dd>
                            </div>
                            <div class="flex justify-between items-start gap-2">
                                <dt class="text-xs text-slate-500">Settlement</dt>
                                <dd class="text-xs text-slate-700 text-right">{{ trx.settlement_time ?
                                    formatDate(trx.settlement_time) : '—' }}</dd>
                            </div>
                        </dl>
                    </InfoCard>

                    <!-- Shipment Info -->
                    <InfoCard title="Info Pengiriman" subtitle="Detail kurir & resi"
                        icon="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" icon-bg="bg-blue-50"
                        icon-color="text-blue-600">
                        <div v-if="trx.shipment">
                            <dl class="space-y-2.5">
                                <div class="flex justify-between items-start gap-2">
                                    <dt class="text-xs text-slate-500">Kurir</dt>
                                    <dd class="text-xs font-semibold text-slate-800 uppercase">
                                        {{ trx.shipment.courier_name }} · {{ trx.shipment.courier_service }}
                                    </dd>
                                </div>
                                <div class="flex justify-between items-start gap-2">
                                    <dt class="text-xs text-slate-500">No. Resi</dt>
                                    <dd class="text-xs font-mono font-bold text-slate-700">{{
                                        trx.shipment.waybill_number || '—' }}</dd>
                                </div>
                                <div class="flex justify-between items-start gap-2">
                                    <dt class="text-xs text-slate-500">Status</dt>
                                    <dd>
                                        <StatusBadge type="delivery" :status="trx.shipment.delivery_status" />
                                    </dd>
                                </div>
                                <div class="flex justify-between items-start gap-2">
                                    <dt class="text-xs text-slate-500">Penerima</dt>
                                    <dd class="text-xs text-slate-700 text-right">{{ trx.shipment.recipient_name }}</dd>
                                </div>
                                <div class="col-span-2 pt-1 border-t border-slate-100">
                                    <p class="text-xs text-slate-500 mb-1">Alamat</p>
                                    <p class="text-xs text-slate-700 leading-relaxed">{{ trx.shipment.shipping_address
                                        }}</p>
                                </div>
                            </dl>
                        </div>
                        <div v-else class="text-center py-6 text-slate-400 text-sm">Belum ada data pengiriman</div>
                    </InfoCard>

                    <!-- Price Breakdown -->
                    <InfoCard title="Rincian Harga" subtitle="Kalkulasi total pembayaran"
                        icon="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"
                        icon-bg="bg-violet-50" icon-color="text-violet-600">
                        <dl class="space-y-2.5">
                            <div class="flex justify-between">
                                <dt class="text-xs text-slate-500">Subtotal Produk</dt>
                                <dd class="text-xs font-semibold text-slate-800 font-mono">{{
                                    formatRp(trx.items_subtotal) }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-xs text-slate-500">Ongkos Kirim</dt>
                                <dd class="text-xs font-semibold text-slate-800 font-mono">{{
                                    formatRp(trx.shipping_cost) }}</dd>
                            </div>
                            <div v-if="trx.discount_amount" class="flex justify-between">
                                <dt class="text-xs text-emerald-600">Diskon</dt>
                                <dd class="text-xs font-semibold text-emerald-600 font-mono">- {{
                                    formatRp(trx.discount_amount) }}</dd>
                            </div>
                            <div class="border-t border-slate-100 pt-2.5 flex justify-between items-center">
                                <dt class="text-sm font-bold text-slate-900">Total</dt>
                                <dd class="text-base font-bold text-slate-900 font-mono">{{ formatRp(trx.gross_amount)
                                    }}</dd>
                            </div>
                        </dl>
                    </InfoCard>
                </div>

                <!-- ── Items List ─────────────────────────────────────── -->
                <InfoCard title="Produk Dipesan" :subtitle="`${trx.items?.length || 0} produk`"
                    icon="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" icon-bg="bg-amber-50" icon-color="text-amber-600"
                    class="mb-4">
                    <div class="space-y-3">
                        <div v-for="item in trx.items" :key="item.stock_uuid"
                            class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100">
                            <!-- Thumbnail -->
                            <div class="w-14 h-14 rounded-lg overflow-hidden bg-slate-100 shrink-0">
                                <img v-if="item.cover_image_url" :src="item.cover_image_url" :alt="item.stock_title"
                                    class="w-full h-full object-cover" loading="lazy" />
                                <div v-else class="w-full h-full flex items-center justify-center">
                                    <svg class="w-6 h-6 text-slate-300" fill="none" stroke="currentColor"
                                        viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                            d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                                    </svg>
                                </div>
                            </div>
                            <!-- Info -->
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-semibold text-slate-800 truncate">{{ item.stock_title }}</p>
                                <p v-if="item.stock_brand" class="text-xs text-slate-400 capitalize mt-0.5">{{
                                    item.stock_brand }}</p>
                                
                                <!-- 🔥 Specs Renderer -->
                                <div v-if="item.specs && Object.keys(item.specs).length > 0" class="flex flex-wrap gap-1.5 mt-1.5">
                                    <span v-for="(value, key) in item.specs" :key="key" 
                                        class="text-[10px] px-1.5 py-0.5 bg-slate-200 text-slate-600 rounded capitalize">
                                        {{ key.replace('_', ' ') }}: <span class="font-medium text-slate-800">{{ value }}</span>
                                    </span>
                                </div>

                                <div class="flex items-center justify-between mt-2">
                                    <span class="text-xs text-slate-500">{{ formatRp(item.unit_price) }} × {{
                                        item.quantity }}</span>
                                    <span class="text-sm font-bold text-slate-900 font-mono">{{ formatRp(item.subtotal)
                                        }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </InfoCard>

                <!-- ── Raw Response Viewer ────────────────────────────── -->
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
                                <p class="text-sm font-bold text-slate-800">Raw Midtrans Response</p>
                                <p class="text-xs text-slate-400">Data mentah dari payment gateway</p>
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
                                class="p-5 text-xs text-slate-600 bg-slate-950 text-green-400 overflow-x-auto leading-relaxed font-mono rounded-b-2xl max-h-80 overflow-y-auto">{{ JSON.stringify(trx.raw_response, null, 2) }}</pre>
                        </div>
                    </Transition>
                </div>
            </template>

        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/service/api'
import StatusBadge from '@/components/StatusBadge.vue'
import InfoCard from '@/components/InfoCard.vue'

const route = useRoute()
const loading = ref(true)
const trx = ref(null)
const rawExpanded = ref(false)

// [PENTING] Fallback Super Aman:
// Ambil ID dari param, jika gagal ambil string terakhir di URL (pasti ORD-xxxx)
const routeParamId = computed(() => {
    return route.params.id || route.params.order_id || route.path.split('/').pop() || null;
})

async function fetchDetail() {
    loading.value = true
    try {
        const id = routeParamId.value;
        
        // Mencegah hit backend jika URL nggak jelas atau kosong
        if (!id || id === 'transaksi' || id === 'detail') {
            console.error("Order ID tidak valid / tidak terbaca dari URL.")
            trx.value = null
            return
        }

        console.log(`📡 Menembak API: /transaksi/detail/${id}`);
        const { data } = await api.get(`/transaksi/detail/${id}`)
        
        trx.value = data
        console.log("✅ Data sukses didapat:", data);
        
    } catch (e) {
        console.error("❌ Gagal memuat detail transaksi", e)
        trx.value = null
    } finally {
        loading.value = false
    }
}

function formatRp(n) {
    return n != null ? 'Rp ' + Number(n).toLocaleString('id-ID') : 'Rp 0'
}

function formatDate(d) {
    if (!d) return '—'
    return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

watch(routeParamId, (newId) => {
    if (newId) fetchDetail();
})

onMounted(fetchDetail)
</script>

<style scoped>
@reference "tailwindcss";

.slide-enter-active,
.slide-leave-active {
    transition: all .2s ease;
}

.slide-enter-from,
.slide-leave-to {
    opacity: 0;
    transform: translateY(-6px);
}
</style>