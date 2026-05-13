<template>
  <div class="h-full max-w-7xl mx-auto flex flex-col font-sans text-gray-800">

    <!-- ══════════════════════════ HEADER ══════════════════════════ -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-gray-900">Manajemen Kupon</h1>
        <p class="mt-1 text-sm text-gray-500">Kelola kode promo dan diskon khusus untuk pelanggan.</p>
      </div>
      <button @click="openModal()"
        class="inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-sm hover:bg-indigo-700 active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 shrink-0">
        <svg class="w-5 h-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        Buat Kupon Baru
      </button>
    </div>

    <!-- ══════════════════════════ STATS ══════════════════════════ -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Total Kupon</p>
        <p class="text-2xl font-bold text-gray-900 mt-1">{{ coupons.length }}</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Aktif</p>
        <p class="text-2xl font-bold text-emerald-600 mt-1">{{ activeCount }}</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Terpakai</p>
        <p class="text-2xl font-bold text-indigo-600 mt-1">{{ totalUsed }}</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Expired</p>
        <p class="text-2xl font-bold text-rose-500 mt-1">{{ expiredCount }}</p>
      </div>
    </div>

    <!-- ══════════════════════════ TABLE ══════════════════════════ -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden flex-1 flex flex-col">
      <div v-if="isLoading" class="p-8 space-y-4">
        <div v-for="i in 5" :key="i" class="h-12 bg-gray-50 animate-pulse rounded-xl"></div>
      </div>

      <div v-else-if="coupons.length === 0" class="flex-1 flex flex-col items-center justify-center py-20">
        <div class="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mb-4 text-indigo-400">
            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/></svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900">Belum Ada Kupon</h3>
        <p class="text-gray-500 text-sm mt-1">Klik tombol di atas untuk membuat kupon pertama Anda.</p>
      </div>

      <div v-else class="overflow-x-auto flex-1">
        <table class="min-w-full divide-y divide-gray-100">
          <thead class="bg-gray-50/50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Kupon</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Tipe & Nilai</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Min. Belanja</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Kuota</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Masa Berlaku</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 bg-white">
            <tr v-for="coupon in coupons" :key="coupon.code" class="hover:bg-gray-50/80 transition-colors group">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/></svg>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-gray-900 uppercase tracking-wider font-mono">{{ coupon.code }}</p>
                    <p class="text-xs text-gray-400 mt-0.5">{{ coupon.description || 'Tanpa deskripsi' }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
                  :class="coupon.discount_type === 'percentage' ? 'bg-blue-50 text-blue-700' : 'bg-emerald-50 text-emerald-700'">
                  {{ coupon.discount_type === 'percentage' ? coupon.discount_value + '%' : formatRp(coupon.discount_value) }}
                </span>
                <p v-if="coupon.max_discount" class="text-[10px] text-gray-400 mt-1">Maks: {{ formatRp(coupon.max_discount) }}</p>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ formatRp(coupon.min_purchase) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                    <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden w-20">
                        <div class="h-full bg-indigo-500 rounded-full" :style="{ width: (coupon.used_count / coupon.quota * 100) + '%' }"></div>
                    </div>
                    <span class="text-xs text-gray-500 font-mono">{{ coupon.used_count }}/{{ coupon.quota }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                <p>{{ formatDate(coupon.valid_from) }}</p>
                <p class="text-gray-400 mt-0.5">s/d {{ formatDate(coupon.valid_until) }}</p>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(coupon)" class="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">
                  {{ getStatusLabel(coupon) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <div class="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="openModal(coupon)" class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                    </button>
                    <button @click="deleteCoupon(coupon.code)" class="p-2 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══════════════════════════ MODAL ══════════════════════════ -->
    <teleport to="body">
      <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0"
        enter-to-class="opacity-100" leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeModal"></div>
            <div class="relative bg-white w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
                    <h3 class="text-lg font-bold text-gray-900">{{ form.isEdit ? 'Edit Kupon' : 'Buat Kupon Baru' }}</h3>
                    <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
                        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>
                
                <div class="p-6 overflow-y-auto space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Kode Kupon</label>
                            <input v-model="form.code" :disabled="form.isEdit" type="text" placeholder="PROMO2024" 
                                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none uppercase font-mono transition-all disabled:opacity-60" />
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Status</label>
                            <div class="flex items-center h-10">
                                <label class="inline-flex items-center cursor-pointer">
                                    <input type="checkbox" v-model="form.is_active" class="sr-only peer">
                                    <div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                                    <span class="ms-3 text-sm font-medium text-gray-600">{{ form.is_active ? 'Aktif' : 'Non-Aktif' }}</span>
                                </label>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Deskripsi</label>
                        <textarea v-model="form.description" rows="2" placeholder="Promo spesial pembukaan toko..." 
                            class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"></textarea>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Tipe Diskon</label>
                            <select v-model="form.discount_type" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all">
                                <option value="percentage">Persentase (%)</option>
                                <option value="fixed_amount">Nominal Tetap (Rp)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Nilai Diskon</label>
                            <input v-model.number="form.discount_value" type="number" placeholder="10" 
                                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Min. Belanja (Rp)</label>
                            <input v-model.number="form.min_purchase" type="number" placeholder="50000" 
                                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Maks. Diskon (Rp)</label>
                            <input v-model.number="form.max_discount" type="number" placeholder="0 = Tanpa Batas" 
                                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Kuota Total</label>
                            <input v-model.number="form.quota" type="number" placeholder="100" 
                                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Mulai Berlaku</label>
                            <input v-model="form.valid_from" type="datetime-local" 
                                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Berakhir Pada</label>
                            <input v-model="form.valid_until" type="datetime-local" 
                                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                        </div>
                    </div>
                </div>

                <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-3">
                    <button @click="closeModal" class="px-5 py-2.5 text-sm font-semibold text-gray-600 hover:text-gray-800 transition-colors">Batal</button>
                    <button @click="saveCoupon" :disabled="isSubmitting" 
                        class="px-6 py-2.5 bg-indigo-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-indigo-200 hover:bg-indigo-700 active:scale-95 transition-all flex items-center gap-2">
                        <svg v-if="isSubmitting" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                        {{ isSubmitting ? 'Menyimpan...' : 'Simpan Kupon' }}
                    </button>
                </div>
            </div>
        </div>
      </transition>
    </teleport>

    <!-- ══════════════════════════ MODAL KONFIRMASI (CUSTOM) ══════════════════════════ -->
    <teleport to="body">
      <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
        <div v-if="isConfirmModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="isConfirmModalOpen = false"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm border border-gray-100 p-6 text-center">
            <div :class="confirmModalConfig.isDanger ? 'bg-rose-50 text-rose-600' : 'bg-indigo-50 text-indigo-600'" 
              class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg v-if="confirmModalConfig.isDanger" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <svg v-else class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">{{ confirmModalConfig.title }}</h3>
            <p class="text-sm text-gray-500 mb-8">{{ confirmModalConfig.message }}</p>
            <div class="flex flex-col gap-2">
              <button @click="handleConfirmAction" 
                :class="confirmModalConfig.isDanger ? 'bg-rose-600 hover:bg-rose-700' : 'bg-indigo-600 hover:bg-indigo-700'"
                class="w-full py-3 text-white font-bold rounded-xl transition-all active:scale-95">
                {{ confirmModalConfig.confirmText }}
              </button>
              <button @click="isConfirmModalOpen = false" 
                class="w-full py-3 text-gray-600 font-semibold hover:bg-gray-50 rounded-xl transition-all">
                Batal
              </button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/service/api'

// Custom Modal State for Confirmations
const isConfirmModalOpen = ref(false)
const confirmModalConfig = ref({
    title: '',
    message: '',
    action: null,
    confirmText: 'Ya, Hapus',
    isDanger: true
})

const showConfirm = (config) => {
    confirmModalConfig.value = {
        title: config.title || 'Konfirmasi',
        message: config.message || 'Apakah Anda yakin?',
        action: config.action,
        confirmText: config.confirmText || 'Ya',
        isDanger: config.isDanger !== false
    }
    isConfirmModalOpen.value = true
}

const handleConfirmAction = async () => {
    if (confirmModalConfig.value.action) {
        await confirmModalConfig.value.action()
    }
    isConfirmModalOpen.value = false
}

const coupons = ref([])
const isLoading = ref(false)
const isSubmitting = ref(false)
const isModalOpen = ref(false)

const form = ref({
    isEdit: false,
    code: '',
    description: '',
    discount_type: 'percentage',
    discount_value: 0,
    min_purchase: 0,
    max_discount: 0,
    quota: 100,
    valid_from: '',
    valid_until: '',
    is_active: true
})

// Stats
const activeCount = computed(() => coupons.value.filter(c => c.is_active && !isExpired(c)).length)
const totalUsed = computed(() => coupons.value.reduce((acc, c) => acc + (c.used_count || 0), 0))
const expiredCount = computed(() => coupons.value.filter(c => isExpired(c)).length)

const isExpired = (coupon) => {
    if (!coupon.valid_until) return false
    return new Date(coupon.valid_until) < new Date()
}

const fetchCoupons = async () => {
    isLoading.value = true
    try {
        const res = await api.get('/admin/coupon')
        if (res.data.success) {
            coupons.value = res.data.data.items
        }
    } catch (error) {
        console.error('Failed to fetch coupons:', error)
    } finally {
        isLoading.value = false
    }
}

const openModal = (coupon = null) => {
    if (coupon) {
        form.value = {
            isEdit: true,
            code: coupon.code,
            description: coupon.description || '',
            discount_type: coupon.discount_type,
            discount_value: coupon.discount_value,
            min_purchase: coupon.min_purchase,
            max_discount: coupon.max_discount || 0,
            quota: coupon.quota,
            valid_from: coupon.valid_from ? coupon.valid_from.slice(0, 16) : '',
            valid_until: coupon.valid_until ? coupon.valid_until.slice(0, 16) : '',
            is_active: coupon.is_active
        }
    } else {
        form.value = {
            isEdit: false,
            code: '',
            description: '',
            discount_type: 'percentage',
            discount_value: 0,
            min_purchase: 0,
            max_discount: 0,
            quota: 100,
            valid_from: '',
            valid_until: '',
            is_active: true
        }
    }
    isModalOpen.value = true
}

const closeModal = () => {
    isModalOpen.value = false
}

const saveCoupon = async () => {
    if (!form.value.code || form.value.discount_value <= 0) {
        alert('Harap isi kode dan nilai diskon')
        return
    }

    isSubmitting.value = true
    try {
        const payload = { ...form.value }
        delete payload.isEdit
        
        // Clean optional fields: change empty strings or 0 to null
        if (!payload.max_discount || payload.max_discount <= 0) payload.max_discount = null
        
        // Handle timezone for datetime-local (convert to ISO with local offset or Z)
        const toISO = (dateStr) => {
            if (!dateStr) return null
            // browser datetime-local format: YYYY-MM-DDTHH:mm
            const date = new Date(dateStr)
            return date.toISOString()
        }

        payload.valid_from = toISO(form.value.valid_from)
        payload.valid_until = toISO(form.value.valid_until)
        
        if (!payload.description) payload.description = null
        
        if (form.value.isEdit) {
            await api.patch(`/admin/coupon/${form.value.code}`, payload)
        } else {
            await api.post('/admin/coupon', payload)
        }
        
        closeModal()
        fetchCoupons()
    } catch (error) {
        alert(error.response?.data?.detail || 'Gagal menyimpan kupon')
    } finally {
        isSubmitting.value = false
    }
}

const deleteCoupon = async (code) => {
    showConfirm({
        title: 'Hapus Kupon?',
        message: `Kupon ${code} akan dinonaktifkan (soft delete) dan tidak dapat digunakan oleh pelanggan.`,
        confirmText: 'Ya, Hapus Kupon',
        action: async () => {
            try {
                await api.delete(`/admin/coupon/${code}`)
                fetchCoupons()
            } catch (error) {
                alert('Gagal menghapus kupon')
            }
        }
    })
}

const formatRp = (val) => {
    if (!val) return 'Rp 0'
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(val)
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const getStatusClass = (coupon) => {
    if (isExpired(coupon)) return 'bg-gray-100 text-gray-500'
    if (!coupon.is_active) return 'bg-rose-50 text-rose-600'
    if (coupon.used_count >= coupon.quota) return 'bg-amber-50 text-amber-600'
    return 'bg-emerald-50 text-emerald-600'
}

const getStatusLabel = (coupon) => {
    if (isExpired(coupon)) return 'Expired'
    if (!coupon.is_active) return 'Non-Aktif'
    if (coupon.used_count >= coupon.quota) return 'Limit Habis'
    return 'Aktif'
}

onMounted(fetchCoupons)
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
