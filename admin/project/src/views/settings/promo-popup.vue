<template>
  <div class="min-h-screen bg-[#F7F8FC] font-sans text-gray-800">
    
    <!-- ── Header ─────────────────────────────── -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
      <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5a2 2 0 10-2 2h2zm0 0h4m-4 0h-4m0 0v13m0 0h12" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Popup Promo Utama</h1>
            <p class="text-xs text-gray-400 mt-0.5">Atur popup promo besar yang muncul saat user masuk website</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button @click="saveSettings" :disabled="saving" class="flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-100 disabled:opacity-50 cursor-pointer border-none">
            <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            {{ saving ? 'Menyimpan...' : 'Simpan Perubahan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Content ────────────────────────────── -->
    <div class="max-w-screen-2xl mx-auto px-6 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Form Settings -->
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h3 class="text-sm font-bold text-gray-900">Konfigurasi Popup</h3>
            </div>
            
            <div class="p-6 space-y-6">
              <div v-if="loading" class="flex flex-col items-center justify-center py-12 gap-3">
                <div class="w-10 h-10 border-[3px] border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
                <p class="text-xs text-gray-400 font-medium">Memuat pengaturan...</p>
              </div>

              <div v-else class="space-y-6">
                <!-- Status Toggle -->
                <div class="flex items-center justify-between p-4 rounded-xl bg-gray-50 border border-gray-100">
                  <div>
                    <h4 class="text-sm font-bold text-gray-800">Status Popup Promo</h4>
                    <p class="text-xs text-gray-400 mt-0.5">Aktifkan untuk langsung menampilkan popup ke user baru</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="form.is_active" class="sr-only peer">
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>

                <!-- Image URL & Upload -->
                <div class="space-y-2">
                  <label class="text-xs font-bold text-gray-400 uppercase tracking-wider block">Gambar Banner</label>
                  
                  <div class="flex flex-col sm:flex-row gap-3">
                    <input 
                      type="text" 
                      v-model="form.image_url" 
                      placeholder="https://example.com/banner-promo.jpg"
                      class="flex-1 bg-gray-50 border border-gray-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl px-4 py-3 text-sm outline-none transition-all font-semibold"
                    />
                    
                    <input 
                      type="file" 
                      ref="fileInput" 
                      @change="handleFileUpload" 
                      accept="image/*" 
                      class="hidden" 
                    />
                    
                    <button 
                      type="button"
                      @click="$refs.fileInput.click()" 
                      :disabled="uploading"
                      class="px-5 py-3 text-sm font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 rounded-xl transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 border-none"
                    >
                      <svg v-if="uploading" class="animate-spin w-4 h-4 text-emerald-700" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
                      <svg v-else class="w-4 h-4 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                      {{ uploading ? 'Mengunggah...' : 'Unggah File' }}
                    </button>
                  </div>
                  
                  <p class="text-[11px] text-gray-400">Pilih gambar dari komputer Anda untuk dikonversi otomatis ke WebP dan disimpan di Cloudflare CDN, atau tempel URL langsung.</p>
                </div>

                <!-- Redirect Route -->
                <div class="space-y-2">
                  <label class="text-xs font-bold text-gray-400 uppercase tracking-wider block">Rute Redirect (Opsional)</label>
                  <input 
                    type="text" 
                    v-model="form.route" 
                    placeholder="/promo atau /search?q=CCTV"
                    class="w-full bg-gray-50 border border-gray-200 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl px-4 py-3 text-sm outline-none transition-all font-semibold"
                  />
                  <p class="text-[11px] text-gray-400">Rute lokal website tujuan ketika banner promo diklik oleh user.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Real-time Preview -->
        <div class="space-y-6">
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden sticky top-24">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
              <h3 class="text-sm font-bold text-gray-900">Live Preview Toko</h3>
              <span class="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest" :class="form.is_active ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-gray-100 text-gray-400'">
                {{ form.is_active ? 'Aktif' : 'Non-aktif' }}
              </span>
            </div>

            <!-- Preview Area -->
            <div class="p-6 bg-slate-900/5 flex flex-col items-center justify-center min-h-[350px]">
              <div v-if="form.image_url" class="relative w-full max-w-[240px] bg-white rounded-2xl overflow-hidden shadow-xl border border-gray-100 flex flex-col items-center">
                <!-- Mock Close button -->
                <div class="absolute top-2 right-2 w-6 h-6 rounded-full bg-black/40 text-white flex items-center justify-center text-[10px] pointer-events-none">✕</div>
                <!-- Image -->
                <img :src="form.image_url" alt="Banner Preview" class="w-full h-auto object-cover select-none" />
                <div v-if="form.route" class="w-full py-2 bg-indigo-50 text-indigo-700 text-[10px] font-bold text-center border-t border-indigo-100">
                  Target: {{ form.route }}
                </div>
              </div>

              <!-- Empty State Preview -->
              <div v-else class="text-center py-12 px-4 flex flex-col items-center">
                <svg class="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                <p class="text-xs text-gray-400 font-bold uppercase tracking-wider">Belum Ada Gambar</p>
                <p class="text-[10px] text-gray-400 mt-1 max-w-[180px]">Masukkan URL gambar di kiri untuk melihat preview langsung.</p>
              </div>
            </div>

            <div class="p-4 bg-indigo-50 border-t border-indigo-100/50 flex gap-2">
              <svg class="w-4 h-4 text-indigo-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <p class="text-[10px] text-indigo-700 leading-normal font-medium">Popup hanya muncul sekali per session agar tidak mengganggu navigasi pembeli.</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/service/api'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const fileInput = ref(null)

const form = ref({
  image_url: '',
  route: '',
  is_active: false
})

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    toastStore.error('File harus berupa gambar!')
    return
  }
  
  uploading.value = true
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const res = await api.post('/settings/promo-popup/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (res.data && res.data.image_url) {
      form.value.image_url = res.data.image_url
      toastStore.success('Gambar berhasil diunggah dan dikonversi ke WebP!')
    } else {
      throw new Error('No URL returned')
    }
  } catch (e) {
    console.error(e)
    toastStore.error('Gagal mengunggah gambar ke CDN Cloudflare')
  } finally {
    uploading.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

async function fetchSettings() {
  loading.value = true
  try {
    const res = await api.get('/settings/promo-popup')
    if (res.data && res.data.data) {
      form.value = res.data.data
    }
  } catch (e) {
    console.error(e)
    toastStore.error('Gagal mengambil pengaturan popup promo')
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  try {
    await api.put('/settings/promo-popup', form.value)
    toastStore.success('Pengaturan popup promo berhasil disimpan!')
  } catch (e) {
    console.error(e)
    toastStore.error('Gagal menyimpan pengaturan')
  } finally {
    saving.value = false
  }
}

onMounted(() => fetchSettings())
</script>

<style scoped></style>
