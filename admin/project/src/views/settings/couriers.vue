<template>
  <div class="min-h-screen bg-[#F7F8FC] font-sans">
    
    <!-- ── Header ─────────────────────────────── -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
      <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Pengaturan Kurir</h1>
            <p class="text-xs text-gray-400 mt-0.5">Atur preferensi kurir yang aktif di marketplace</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button @click="saveSettings" :disabled="saving" class="flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-100 disabled:opacity-50">
            <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            {{ saving ? 'Menyimpan...' : 'Simpan Perubahan' }}
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-screen-xl mx-auto px-6 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Sidebar Info -->
        <div class="space-y-6">
          <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
            <h3 class="text-sm font-bold text-gray-900 mb-2">Pusat Bantuan</h3>
            <p class="text-xs text-gray-500 leading-relaxed">
              Kurir yang Anda aktifkan di sini akan muncul sebagai pilihan bagi pembeli saat melakukan checkout. Pastikan Anda sudah memiliki akun atau kerjasama dengan ekspedisi yang dipilih.
            </p>
            <div class="mt-4 p-3 bg-amber-50 rounded-xl border border-amber-100 flex gap-3">
              <svg class="w-5 h-5 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <p class="text-[11px] text-amber-700 leading-tight">Sistem menggunakan integrasi RajaOngkir untuk menghitung biaya secara otomatis.</p>
            </div>
          </div>
        </div>

        <!-- Main Settings Form -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h3 class="text-sm font-bold text-gray-900">Pilih Ekspeditur Aktif</h3>
            </div>
            
            <div class="p-6">
              <div v-if="loading" class="flex flex-col items-center justify-center py-12 gap-3">
                <div class="w-10 h-10 border-[3px] border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
                <p class="text-xs text-gray-400 font-medium">Memuat pengaturan...</p>
              </div>

              <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div v-for="(active, key) in couriers" :key="key" 
                  class="group relative flex items-center p-4 rounded-2xl border transition-all cursor-pointer"
                  :class="active ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-100' : 'bg-white border-gray-100 hover:border-gray-300'"
                  @click="couriers[key] = !active"
                >
                  <div class="w-12 h-12 rounded-xl flex items-center justify-center mr-4" :class="active ? 'bg-white shadow-sm text-indigo-600' : 'bg-gray-50 text-gray-400'">
                    <svg v-if="key === 'jne'" class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 011 1v2.5a1.5 1.5 0 01-3 0V16m-1 0h1m3 0h5l3 3v2a1 1 0 01-1 1h-1m-4-7V4a1 1 0 011-1h5a1 1 0 011 1v12a1 1 0 01-1 1h-1m-4 0h1" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/></svg>
                    <svg v-else class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/></svg>
                  </div>
                  <div class="flex-1">
                    <h4 class="text-sm font-bold uppercase tracking-wider" :class="active ? 'text-indigo-900' : 'text-gray-700'">{{ key }}</h4>
                    <p class="text-[10px] text-gray-400 font-medium">Layanan Regular & Ekspres</p>
                  </div>
                  <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all" :class="active ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-gray-200'">
                    <svg v-if="active" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                  </div>
                </div>
              </div>
            </div>

            <div class="px-6 py-4 bg-indigo-900 text-white flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
                <p class="text-[10px] font-bold uppercase tracking-widest opacity-80">Sinkronisasi Real-time</p>
              </div>
              <p class="text-[10px] opacity-60 italic">Perubahan akan langsung berdampak pada halaman checkout user.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Toast ──────────────────────────── -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show" class="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3 rounded-xl shadow-2xl text-sm font-semibold bg-gray-900 text-white">
          <div class="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center text-[10px] font-black text-white">✓</div>
          {{ toast.message }}
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/service/api'

const loading = ref(true)
const saving = ref(false)
const couriers = ref({})
const toast = ref({ show: false, message: '' })

async function fetchSettings() {
  loading.value = true
  try {
    const res = await api.get('/settings/couriers')
    couriers.value = res.data.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  try {
    await api.put('/settings/couriers', couriers.value)
    showToast('Preferensi kurir berhasil disimpan!')
  } catch (e) {
    alert('Gagal menyimpan pengaturan')
  } finally {
    saving.value = false
  }
}

function showToast(msg) {
  toast.value.message = msg
  toast.value.show = true
  setTimeout(() => toast.value.show = false, 3000)
}

onMounted(() => fetchSettings())
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(20px); }
</style>
