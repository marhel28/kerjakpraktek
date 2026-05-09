<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

// Layout public agar Sidebar AccountSidebar bisa ditampilkan
definePageMeta({ layout: 'public' })
const config = useRuntimeConfig()
const API_BASE = `${config.public.apiBase}/cek/shipping` // Base URL disesuaikan dengan prefix router_ship

// State Management
const addresses = ref<any[]>([])
const isLoading = ref(true)
const isModalOpen = ref(false)
const isSaving = ref(false)
const isSearching = ref(false)
const isDeleting = ref<string | null>(null)

// Pencarian Lokasi
const searchQuery = ref('')
const searchResults = ref<any[]>([])
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// Form State (Diperbarui menyesuaikan UserAddressCreate & SaveUserAddressRequest)
const form = reactive({
  id: '', // UUID
  location_id: '',
  zip_code: '',
  full_address: '',
  province: '',
  city: '',
  district: '',
  subdistrict: '',
  label: '', // Nama lokasi lengkap dari API
  is_default: false
})

// Mengambil Token Auth
const getToken = () => useCookie('token').value

// ----------------------------------------------------
// 1. FETCH DAFTAR ALAMAT USER
// ----------------------------------------------------
const fetchAddresses = async () => {
  isLoading.value = true
  try {
    const response: any = await $fetch(`${API_BASE}/address`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    addresses.value = response.data || []
  } catch (err) {
    console.error('Gagal mengambil daftar alamat:', err)
  } finally {
    isLoading.value = false
  }
}

// ----------------------------------------------------
// 2. HANDLER PENCARIAN LOKASI (AUTOCOMPLETE)
// ----------------------------------------------------
const handleSearchLocation = (e: Event) => {
  const query = (e.target as HTMLInputElement).value
  searchQuery.value = query

  // Reset data jika kurang dari 3 huruf
  if (query.length < 3) {
    searchResults.value = []
    form.location_id = ''
    form.zip_code = ''
    form.province = ''
    form.city = ''
    form.district = ''
    form.subdistrict = ''
    form.label = ''
    return
  }

  if (searchTimeout) clearTimeout(searchTimeout)
  
  searchTimeout = setTimeout(async () => {
    isSearching.value = true
    try {
      const response: any = await $fetch(`${API_BASE}/lokasi`, {
        method: 'GET',
        query: { q: query, limit: 10, offset: 0 },
        headers: { Authorization: `Bearer ${getToken()}` }
      })
      searchResults.value = response.data || []
    } catch (err) {
      console.error('Pencarian lokasi gagal:', err)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }, 500)
}

// Menangkap seluruh data lokasi saat user klik hasil pencarian
const selectLocation = (loc: any) => {
  form.location_id = loc.id.toString() 
  form.zip_code = loc.zip 
  form.label = loc.label 
  form.province = loc.province
  form.city = loc.city
  form.district = loc.district
  form.subdistrict = loc.subdistrict
  
  // Tampilkan label komplit di input search
  searchQuery.value = form.label
  searchResults.value = []
}

// ----------------------------------------------------
// 3. CREATE & UPDATE ADDRESS
// ----------------------------------------------------
const saveAddress = async () => {
  if (!form.location_id || !form.zip_code) {
    alert('Silakan cari dan pilih kecamatan/kota dari daftar dropdown terlebih dahulu.')
    return
  }
  if (!form.full_address || form.full_address.length < 10) {
    alert('Detail alamat lengkap wajib diisi (Minimal 10 karakter).')
    return
  }

  isSaving.value = true
  
  // Payload sesuai schema pydantic backend
  const payload = {
    location_id: form.location_id,
    zip_code: form.zip_code,
    full_address: form.full_address,
    province: form.province,
    city: form.city,
    district: form.district,
    subdistrict: form.subdistrict,
    label: form.label,
    is_default: form.is_default
  }

  try {
    if (form.id) {
      // UPDATE (PUT)
      await $fetch(`${API_BASE}/address/${form.id}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: payload
      })
    } else {
      // CREATE (POST)
      await $fetch(`${API_BASE}/address`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: payload
      })
    }
    
    closeModal()
    await fetchAddresses() 
  } catch (err: any) {
    const errorMsg = err.data?.detail?.[0]?.msg || err.data?.detail || 'Terjadi kesalahan pada server.'
    alert(`Gagal menyimpan: ${errorMsg}`)
  } finally {
    isSaving.value = false
  }
}

// ----------------------------------------------------
// 4. DELETE ADDRESS
// ----------------------------------------------------
const deleteAddress = async (id: string) => {
  if (!confirm('Apakah Anda yakin ingin menghapus alamat ini?')) return

  isDeleting.value = id
  try {
    await $fetch(`${API_BASE}/address/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    await fetchAddresses()
  } catch (err: any) {
    console.error('Gagal menghapus alamat:', err)
    alert('Gagal menghapus alamat. Silakan coba lagi.')
  } finally {
    isDeleting.value = null
  }
}

// ----------------------------------------------------
// 5. UTILITIES
// ----------------------------------------------------
const setAsDefault = async (address: any) => {
  if (address.is_default) return
  
  const targetId = address.uuid || address.id;

  try {
    await $fetch(`${API_BASE}/address/${targetId}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${getToken()}` },
      // Mengirimkan data utuh dengan is_default true
      body: { 
        location_id: address.location_id,
        zip_code: address.zip_code,
        full_address: address.full_address,
        province: address.province,
        city: address.city,
        district: address.district,
        subdistrict: address.subdistrict,
        label: address.label,
        is_default: true 
      }
    })
    await fetchAddresses()
  } catch (err) {
    console.error('Gagal mengubah alamat utama', err)
  }
}

const openAddModal = () => {
  form.id = ''
  form.location_id = ''
  form.zip_code = ''
  form.full_address = ''
  form.province = ''
  form.city = ''
  form.district = ''
  form.subdistrict = ''
  form.label = ''
  form.is_default = addresses.value.length === 0
  
  searchQuery.value = ''
  searchResults.value = []
  isModalOpen.value = true
}

const openEditModal = (address: any) => {
  form.id = address.uuid || address.id
  form.location_id = address.location_id
  form.zip_code = address.zip_code
  form.full_address = address.full_address
  form.province = address.province || ''
  form.city = address.city || ''
  form.district = address.district || ''
  form.subdistrict = address.subdistrict || ''
  form.label = address.label || `Lokasi ID: ${address.location_id}` 
  form.is_default = address.is_default
  
  // Set tampilan input pencarian ke label yang sudah tersimpan
  searchQuery.value = form.label
  searchResults.value = []
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

onMounted(() => {
  fetchAddresses()
})
</script>

<template>
  <div class="min-h-screen bg-[#f3f4f5] py-8">
    <div class="container mx-auto px-4 max-w-[1200px] flex flex-col lg:flex-row gap-6">
      
      <AccountSidebar />

      <main class="flex-1 bg-white rounded-xl shadow-sm border border-gray-200">
        
        <header class="px-8 py-6 border-b border-gray-100 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
          <div>
            <h1 class="text-xl font-bold text-gray-900">Daftar Alamat</h1>
            <p class="text-sm text-gray-500 mt-1">Kelola alamat pengiriman untuk pesanan Anda</p>
          </div>
          <button 
            @click="openAddModal" 
            class="px-5 py-2.5 text-sm font-bold text-white bg-[#03AC0E] hover:bg-[#028c0b] rounded-lg transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            Tambah Alamat Baru
          </button>
        </header>

        <div class="p-8">
          
          <div v-if="isLoading" class="space-y-4">
            <div v-for="i in 2" :key="i" class="w-full h-32 bg-gray-100 animate-pulse rounded-xl border border-gray-200"></div>
          </div>

          <div v-else-if="addresses.length === 0" class="text-center py-12 px-4 border-2 border-dashed border-gray-200 rounded-xl">
            <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            <h3 class="text-lg font-bold text-gray-900">Belum Ada Alamat</h3>
            <p class="text-gray-500 mt-1 mb-4 text-sm">Tambahkan alamat pengiriman agar Anda dapat mulai berbelanja.</p>
            <button @click="openAddModal" class="text-[#03AC0E] font-bold text-sm hover:underline">Tambah Alamat Sekarang</button>
          </div>

          <div v-else class="space-y-4">
            <div 
              v-for="address in addresses" 
              :key="address.uuid || address.id"
              class="p-5 rounded-xl border transition-all"
              :class="address.is_default ? 'border-[#03AC0E] bg-green-50/30' : 'border-gray-200 hover:border-green-300'"
            >
              <div class="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <span class="font-bold text-gray-800">Rumah / Kantor</span>
                    <span v-if="address.is_default" class="px-2 py-0.5 text-[10px] font-bold text-[#03AC0E] bg-green-100 rounded-full">
                      Alamat Utama
                    </span>
                  </div>
                  <p class="text-gray-800 font-semibold text-sm">{{ address.label || address.city }}</p>
                  <p class="text-gray-500 text-sm mt-1 leading-relaxed">{{ address.full_address }}</p>
                  <div class="mt-2 flex gap-4 text-sm text-gray-500">
                     <span class="bg-gray-100 px-2 py-1 rounded">Kode Pos: <span class="font-bold text-gray-700">{{ address.zip_code }}</span></span>
                     <span class="bg-gray-100 px-2 py-1 rounded font-mono text-xs mt-0.5">Loc ID: {{ address.location_id }}</span>
                  </div>
                </div>

                <div class="flex flex-row md:flex-col gap-3 md:items-end w-full md:w-auto mt-2 md:mt-0">
                  <div class="flex gap-4 items-center">
                    <button @click="openEditModal(address)" class="text-sm font-semibold text-gray-600 hover:text-[#03AC0E] transition-colors">Ubah</button>
                    <button 
                      @click="deleteAddress(address.uuid || address.id)" 
                      :disabled="isDeleting === (address.uuid || address.id)"
                      class="text-sm font-semibold text-red-500 hover:text-red-700 transition-colors disabled:opacity-50 flex items-center gap-1"
                    >
                      <svg v-if="isDeleting === (address.uuid || address.id)" class="animate-spin h-3 w-3 text-red-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                      Hapus
                    </button>
                  </div>

                  <button 
                    v-if="!address.is_default" 
                    @click="setAsDefault(address)" 
                    class="text-sm font-semibold text-gray-700 border border-gray-300 hover:border-[#03AC0E] hover:text-[#03AC0E] bg-white px-4 py-2 rounded-lg transition-colors w-full md:w-auto mt-2"
                  >
                    Jadikan Utama
                  </button>
                </div>

              </div>
            </div>
          </div>
        </div>
      </main>

      <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="closeModal"></div>
        
        <div class="relative w-full max-w-lg bg-white rounded-xl shadow-xl flex flex-col max-h-[90vh]">
          
          <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white rounded-t-xl sticky top-0 z-10">
            <h2 class="text-lg font-bold text-gray-900">{{ form.id ? 'Ubah Alamat' : 'Tambah Alamat Baru' }}</h2>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600 p-1">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>

          <div class="p-6 overflow-y-auto space-y-6">
            
            <div class="flex flex-col gap-2 relative z-20">
              <label class="text-sm font-semibold text-gray-700">Kecamatan / Kota / Kabupaten <span class="text-red-500">*</span></label>
              <div class="relative">
                <input 
                  v-model="searchQuery" 
                  @input="handleSearchLocation"
                  type="text" 
                  placeholder="Ketik minimal 3 huruf (Cth: Wonosobo)" 
                  class="w-full px-4 py-3 pl-10 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all"
                />
                <svg class="w-5 h-5 absolute left-3 top-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                <svg v-if="isSearching" class="w-4 h-4 absolute right-4 top-3.5 animate-spin text-gray-400" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              </div>

              <ul v-if="searchResults.length > 0" class="absolute top-[70px] left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-xl max-h-56 overflow-y-auto divide-y divide-gray-100">
                <li 
                  v-for="res in searchResults" 
                  :key="res.id"
                  @click="selectLocation(res)"
                  class="px-4 py-3 hover:bg-green-50 cursor-pointer transition-colors"
                >
                  <p class="text-sm font-semibold text-gray-800 leading-snug">{{ res.label }}</p>
                </li>
              </ul>
            </div>

            <div v-if="form.location_id" class="flex gap-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-sm text-blue-800">
               <div class="flex-1"><strong>Kode Pos:</strong> {{ form.zip_code }}</div>
               <div class="flex-1 text-right"><strong>ID Lokasi:</strong> <span class="font-mono">{{ form.location_id }}</span></div>
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-sm font-semibold text-gray-700">Detail Alamat Lengkap <span class="text-red-500">*</span></label>
              <textarea 
                v-model="form.full_address" 
                rows="4" 
                class="w-full px-4 py-3 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all resize-none" 
                placeholder="Contoh: Jl. Diponegoro No.1, RT 01/RW 02, Patokan samping minimarket"
              ></textarea>
            </div>

            <div class="flex items-center gap-3">
              <input 
                type="checkbox" 
                id="is_default" 
                v-model="form.is_default" 
                class="w-5 h-5 text-[#03AC0E] bg-gray-100 border-gray-300 rounded focus:ring-[#03AC0E] focus:ring-2 cursor-pointer"
              >
              <label for="is_default" class="text-sm font-medium text-gray-700 cursor-pointer">
                Jadikan sebagai alamat utama
              </label>
            </div>

          </div>

          <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-xl flex justify-end gap-3">
            <button 
              @click="closeModal" 
              type="button" 
              class="px-6 py-2.5 text-sm font-bold text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Batal
            </button>
            <button 
              @click="saveAddress" 
              :disabled="isSaving || !form.location_id || !form.full_address || form.full_address.length < 10"
              class="px-8 py-2.5 text-sm font-bold text-white bg-[#03AC0E] hover:bg-[#028c0b] rounded-lg transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="isSaving" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span v-else>Simpan Alamat</span>
            </button>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>