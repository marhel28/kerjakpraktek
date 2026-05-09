<script setup lang="ts">
import { useUserStore } from '~/stores/user'
import { ref, onMounted, reactive, watch } from 'vue'

definePageMeta({ layout: 'public' })

const userStore = useUserStore()
const API_BASE = 'http://127.0.0.1:8000/cek'
const getToken = () => useCookie('token').value

// ----------------------------------------------------------------------
// STATE ALAMAT PENGIRIMAN (SHIPPING ADDRESS)
// ----------------------------------------------------------------------
const shippingAddresses = ref<any[]>([])
const isLoadingAddresses = ref(false)

const fetchShippingAddresses = async () => {
  isLoadingAddresses.value = true
  try {
    const response: any = await $fetch(`${API_BASE}/shipping/address`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    shippingAddresses.value = response.data || []
  } catch (err) {
    console.error('Gagal memuat alamat pengiriman:', err)
  } finally {
    isLoadingAddresses.value = false
  }
}

// ----------------------------------------------------------------------
// STATE FORM LOKAL (BIODATA)
// ----------------------------------------------------------------------
const form = reactive({
  username: '',
  email: '',
  nomertlp: '',
  alamat: '',
  provinsi: '',
  kabupaten: '',
  kecamatan: ''
})

// --- REGIONAL API LOGIC (EMSIFA) ---
const API_WILAYAH = 'https://www.emsifa.com/api-wilayah-indonesia/api'

const regions = reactive({
  provinces: [] as any[],
  regencies: [] as any[],
  districts: [] as any[]
})

const selectedIds = reactive({
  prov: '',
  reg: '',
  dist: ''
})

const isRegionLoading = reactive({
  prov: false,
  reg: false,
  dist: false
})

// ======================================================================
// 1. LOGIKA AUTO-RESTORE DARI DATABASE KE DROPDOWN
// ======================================================================
const restoreDropdownsFromDB = async () => {
  isRegionLoading.prov = true
  try {
    regions.provinces = await $fetch<any[]>(`${API_WILAYAH}/provinces.json`)
  } catch (err) { console.error(err) }
  isRegionLoading.prov = false

  if (!form.provinsi) return 

  const provMatch = regions.provinces.find(p => p.name.trim().toUpperCase() === form.provinsi.trim().toUpperCase())
  
  if (provMatch) {
    selectedIds.prov = provMatch.id 

    isRegionLoading.reg = true
    try {
      regions.regencies = await $fetch<any[]>(`${API_WILAYAH}/regencies/${provMatch.id}.json`)
    } catch (err) { console.error(err) }
    isRegionLoading.reg = false

    if (!form.kabupaten) return

    const regMatch = regions.regencies.find(r => r.name.trim().toUpperCase() === form.kabupaten.trim().toUpperCase())
    
    if (regMatch) {
      selectedIds.reg = regMatch.id 

      isRegionLoading.dist = true
      try {
        regions.districts = await $fetch<any[]>(`${API_WILAYAH}/districts/${regMatch.id}.json`)
      } catch (err) { console.error(err) }
      isRegionLoading.dist = false

      if (!form.kecamatan) return

      const distMatch = regions.districts.find(d => d.name.trim().toUpperCase() === form.kecamatan.trim().toUpperCase())
      if (distMatch) {
        selectedIds.dist = distMatch.id 
      }
    }
  }
}

// ======================================================================
// 2. LOGIKA MANUAL SAAT USER GANTI DROPDOWN
// ======================================================================
const onProvinsiChange = async () => {
  const p = regions.provinces.find(x => x.id === selectedIds.prov)
  if (p) form.provinsi = p.name
  
  form.kabupaten = ''
  form.kecamatan = ''
  selectedIds.reg = ''
  selectedIds.dist = ''
  regions.regencies = []
  regions.districts = []

  if (selectedIds.prov) {
    isRegionLoading.reg = true
    try {
      regions.regencies = await $fetch<any[]>(`${API_WILAYAH}/regencies/${selectedIds.prov}.json`)
    } catch (e) { console.error(e) } 
    finally { isRegionLoading.reg = false }
  }
}

const onKabupatenChange = async () => {
  const r = regions.regencies.find(x => x.id === selectedIds.reg)
  if (r) form.kabupaten = r.name
  
  form.kecamatan = ''
  selectedIds.dist = ''
  regions.districts = []

  if (selectedIds.reg) {
    isRegionLoading.dist = true
    try {
      regions.districts = await $fetch<any[]>(`${API_WILAYAH}/districts/${selectedIds.reg}.json`)
    } catch (e) { console.error(e) }
    finally { isRegionLoading.dist = false }
  }
}

const onKecamatanChange = () => {
  const d = regions.districts.find(x => x.id === selectedIds.dist)
  if (d) form.kecamatan = d.name
}

// ======================================================================
// 3. INIT & SYNC APP
// ======================================================================
const syncForm = () => {
  if (userStore.profile) {
    Object.assign(form, {
      username: userStore.profile.username || '',
      email: userStore.profile.email || '',
      nomertlp: userStore.profile.nomertlp || '',
      alamat: userStore.profile.alamat || '',
      provinsi: userStore.profile.provinsi || '',
      kabupaten: userStore.profile.kabupaten || '',
      kecamatan: userStore.profile.kecamatan || ''
    })
  }
}

const initializeData = async () => {
  if (!userStore.profile) {
    await userStore.fetchProfile()
  }
  syncForm()
  await Promise.all([
    restoreDropdownsFromDB(),
    fetchShippingAddresses() // Fetch Daftar Alamat
  ])
}

onMounted(() => {
  initializeData()
})

// ======================================================================
// 4. ACTIONS
// ======================================================================
const handleSave = async () => {
  const success = await userStore.updateProfile({
    username: form.username,
    nomertlp: form.nomertlp,
    alamat: form.alamat,
    provinsi: form.provinsi,
    kabupaten: form.kabupaten,
    kecamatan: form.kecamatan
  })

  if (success) {
    alert('Profil berhasil diperbarui!') 
  }
}

const handleDelete = async () => {
  if (confirm('Apakah Anda yakin ingin menghapus akun? Semua data akan hilang permanen.')) {
    await userStore.deleteUserData()
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#f3f4f5] py-8 font-sans">
    <div class="container mx-auto px-4 max-w-[1200px] flex flex-col lg:flex-row gap-6">
      
      <AccountSidebar />

      <main class="flex-1 space-y-6">
        
        <div class="bg-white rounded-xl shadow-[0_2px_10px_-4px_rgba(0,0,0,0.1)] border border-gray-100 overflow-hidden">
          <header class="px-8 py-5 border-b border-gray-100 flex justify-between items-center">
            <div>
              <h2 class="text-lg font-extrabold text-gray-900 tracking-tight">Alamat Pengiriman Utama</h2>
              <p class="text-xs font-medium text-gray-500 mt-1">Digunakan sebagai alamat default saat checkout.</p>
            </div>
            <NuxtLink to="/dashboard/address" class="text-sm font-bold text-[#00AA5B] hover:text-[#008f4c] transition-colors">
              Atur Alamat
            </NuxtLink>
          </header>

          <div class="p-8 bg-gray-50/30">
            <div v-if="isLoadingAddresses" class="h-32 bg-gray-100 animate-pulse rounded-xl border border-gray-200"></div>
            
            <div v-else-if="shippingAddresses.length === 0" class="text-center py-6 border-2 border-dashed border-gray-200 rounded-xl bg-white">
              <Icon name="lucide:map-pin" class="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p class="text-sm font-bold text-gray-700">Belum ada alamat pengiriman.</p>
              <NuxtLink to="/dashboard/address" class="text-[#00AA5B] text-xs font-bold hover:underline mt-1 block">Tambah Sekarang</NuxtLink>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div 
                v-for="addr in shippingAddresses.slice(0, 2)" 
                :key="addr.uuid"
                class="p-5 rounded-xl border transition-all"
                :class="addr.is_default ? 'border-[#00AA5B] bg-[#e5f7ed]/50 shadow-sm' : 'border-gray-200 bg-white'"
              >
                <div class="flex items-center gap-2 mb-2">
                  <Icon name="lucide:home" class="w-4 h-4 text-gray-500" />
                  <span class="font-bold text-gray-800 text-sm">Rumah / Kantor</span>
                  <span v-if="addr.is_default" class="px-2 py-0.5 text-[9px] font-black uppercase tracking-widest text-[#00AA5B] bg-green-100 rounded">Utama</span>
                </div>
                <p class="text-sm font-bold text-gray-900 truncate">{{ addr.label || addr.city }}</p>
                <p class="text-xs text-gray-500 mt-1 line-clamp-2 leading-relaxed">{{ addr.full_address }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-[0_2px_10px_-4px_rgba(0,0,0,0.1)] border border-gray-100 overflow-hidden">
          <header class="px-8 py-6 border-b border-gray-100 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <div>
              <h1 class="text-xl font-extrabold text-gray-900 tracking-tight">Biodata Diri</h1>
              <p class="text-sm font-medium text-gray-500 mt-1">Kelola informasi profil Anda untuk mengontrol dan mengamankan akun.</p>
            </div>
            <button 
              @click="handleDelete" 
              :disabled="userStore.isSaving"
              class="px-5 py-2.5 text-sm font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors active:scale-95 disabled:opacity-50"
            >
              Hapus Akun
            </button>
          </header>

          <div v-if="userStore.isLoading && !userStore.profile" class="p-8 space-y-8" aria-busy="true">
             <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div class="h-12 bg-gray-100 rounded-xl animate-pulse"></div>
               <div class="h-12 bg-gray-100 rounded-xl animate-pulse"></div>
             </div>
             <div class="h-12 bg-gray-100 rounded-xl animate-pulse w-1/2"></div>
          </div>

          <div v-else class="p-8">
            <form @submit.prevent="handleSave" class="space-y-8 max-w-3xl">
              
              <section>
                <h2 class="text-base font-extrabold text-gray-900 mb-4 tracking-tight">Informasi Pribadi</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-bold text-gray-700">Nama Lengkap</label>
                    <input v-model="form.username" type="text" class="w-full px-4 py-3 text-sm border border-gray-300 rounded-xl focus:ring-4 focus:ring-[#00AA5B]/20 focus:border-[#00AA5B] outline-none transition-all font-medium text-gray-800" placeholder="Masukkan nama lengkap" required />
                  </div>
                  
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-bold text-gray-700 flex items-center justify-between">
                      Email 
                      <span v-if="userStore.profile?.is_verified" class="text-[10px] text-[#00AA5B] bg-[#e5f7ed] px-2 py-0.5 rounded font-black tracking-widest uppercase">Terverifikasi</span>
                    </label>
                    <input v-model="form.email" type="email" disabled class="w-full px-4 py-3 text-sm bg-gray-50 border border-gray-200 text-gray-500 rounded-xl cursor-not-allowed outline-none font-medium shadow-sm" />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-bold text-gray-700">Nomor Telepon</label>
                    <input v-model="form.nomertlp" type="tel" class="w-full px-4 py-3 text-sm border border-gray-300 rounded-xl focus:ring-4 focus:ring-[#00AA5B]/20 focus:border-[#00AA5B] outline-none transition-all font-medium text-gray-800" placeholder="Contoh: 081234567890" />
                  </div>
                </div>
              </section>

              <hr class="border-gray-100" />

              <section>
                <h2 class="text-base font-extrabold text-gray-900 mb-4 tracking-tight">Alamat Invoice (Billing)</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-5">
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-bold text-gray-700">Provinsi</label>
                    <div class="relative">
                      <select 
                        v-model="selectedIds.prov" 
                        @change="onProvinsiChange"
                        :disabled="isRegionLoading.prov"
                        class="w-full px-4 py-3 text-sm border border-gray-300 rounded-xl focus:ring-4 focus:ring-[#00AA5B]/20 focus:border-[#00AA5B] outline-none transition-all appearance-none bg-white disabled:bg-gray-50 disabled:text-gray-400 capitalize font-medium text-gray-800 cursor-pointer"
                      >
                        <option value="" disabled>Pilih Provinsi</option>
                        <option v-for="prov in regions.provinces" :key="prov.id" :value="prov.id" class="capitalize">
                          {{ prov.name.toLowerCase() }}
                        </option>
                      </select>
                      <div class="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-gray-400">
                        <Icon v-if="isRegionLoading.prov" name="lucide:loader-2" class="animate-spin w-4 h-4 text-[#00AA5B]" />
                        <Icon v-else name="lucide:chevron-down" class="w-4 h-4" />
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-bold text-gray-700">Kota / Kabupaten</label>
                    <div class="relative">
                      <select 
                        v-model="selectedIds.reg" 
                        @change="onKabupatenChange"
                        :disabled="!selectedIds.prov || isRegionLoading.reg"
                        class="w-full px-4 py-3 text-sm border border-gray-300 rounded-xl focus:ring-4 focus:ring-[#00AA5B]/20 focus:border-[#00AA5B] outline-none transition-all appearance-none bg-white disabled:bg-gray-50 disabled:text-gray-400 capitalize font-medium text-gray-800 cursor-pointer"
                      >
                        <option value="" disabled>Pilih Kota/Kab.</option>
                        <option v-for="reg in regions.regencies" :key="reg.id" :value="reg.id" class="capitalize">
                          {{ reg.name.toLowerCase() }}
                        </option>
                      </select>
                      <div class="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-gray-400">
                        <Icon v-if="isRegionLoading.reg" name="lucide:loader-2" class="animate-spin w-4 h-4 text-[#00AA5B]" />
                        <Icon v-else name="lucide:chevron-down" class="w-4 h-4" />
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-bold text-gray-700">Kecamatan</label>
                    <div class="relative">
                      <select 
                        v-model="selectedIds.dist" 
                        @change="onKecamatanChange"
                        :disabled="!selectedIds.reg || isRegionLoading.dist"
                        class="w-full px-4 py-3 text-sm border border-gray-300 rounded-xl focus:ring-4 focus:ring-[#00AA5B]/20 focus:border-[#00AA5B] outline-none transition-all appearance-none bg-white disabled:bg-gray-50 disabled:text-gray-400 capitalize font-medium text-gray-800 cursor-pointer"
                      >
                        <option value="" disabled>Pilih Kecamatan</option>
                        <option v-for="dist in regions.districts" :key="dist.id" :value="dist.id" class="capitalize">
                          {{ dist.name.toLowerCase() }}
                        </option>
                      </select>
                      <div class="absolute inset-y-0 right-0 flex items-center px-4 pointer-events-none text-gray-400">
                        <Icon v-if="isRegionLoading.dist" name="lucide:loader-2" class="animate-spin w-4 h-4 text-[#00AA5B]" />
                        <Icon v-else name="lucide:chevron-down" class="w-4 h-4" />
                      </div>
                    </div>
                  </div>
                </div>

                <div class="flex flex-col gap-2">
                  <label class="text-sm font-bold text-gray-700">Detail Alamat</label>
                  <textarea v-model="form.alamat" rows="3" class="w-full px-4 py-3 text-sm border border-gray-300 rounded-xl focus:ring-4 focus:ring-[#00AA5B]/20 focus:border-[#00AA5B] outline-none transition-all resize-none font-medium text-gray-800" placeholder="Nama Jalan, Gedung, No. Rumah, RT/RW, Patokan"></textarea>
                </div>
              </section>

              <div v-if="userStore.error" class="p-4 bg-red-50 border border-red-100 text-red-600 rounded-xl text-sm font-bold flex items-center gap-2">
                <Icon name="lucide:alert-circle" class="w-5 h-5" />
                {{ userStore.error }}
              </div>

              <div class="flex justify-end pt-2">
                <button 
                  type="submit" 
                  :disabled="userStore.isSaving" 
                  class="px-8 py-3.5 bg-[#00AA5B] text-white font-black rounded-xl hover:bg-[#008f4c] hover:shadow-lg hover:shadow-green-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] w-full sm:w-auto"
                >
                  <Icon v-if="userStore.isSaving" name="lucide:loader-2" class="animate-spin w-5 h-5" />
                  <span v-else>Simpan Perubahan</span>
                </button>
              </div>

            </form>
          </div>
        </div>
      </main>

    </div>
  </div>
</template>