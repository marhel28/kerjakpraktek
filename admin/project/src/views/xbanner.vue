<template>
    <div class="h-full max-w-7xl mx-auto flex flex-col font-sans text-gray-800">
      
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-gray-900">X Banner Management</h1>
          <p class="mt-1 text-sm text-gray-500">Kelola banner utama (Hero) yang tampil di halaman depan marketplace.</p>
        </div>
        <button 
          @click="openModal()"
          class="inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-sm hover:bg-indigo-700 hover:shadow active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 shrink-0"
        >
          <svg class="w-5 h-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Tambah Banner
        </button>
      </div>
  
      <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div v-for="i in 4" :key="i" class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm animate-pulse">
          <div class="w-full aspect-video bg-gray-200 rounded-xl mb-4"></div>
          <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
  
      <div v-else-if="banners.length === 0" class="flex-1 flex flex-col items-center justify-center py-16 px-4 bg-white border border-gray-200 border-dashed rounded-2xl">
        <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 class="text-base font-semibold text-gray-900">Belum ada banner</h3>
        <p class="mt-1 text-sm text-gray-500 max-w-sm text-center">Mulai tambahkan banner promo atau informasi untuk ditampilkan di beranda marketplace.</p>
        <button @click="openModal()" class="mt-6 text-sm font-medium text-indigo-600 hover:text-indigo-500">
          + Tambah Banner Pertama
        </button>
      </div>
  
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-12">
        <div 
          v-for="banner in banners" 
          :key="banner.id"
          class="group relative bg-white rounded-2xl p-3 border border-gray-200 shadow-sm hover:shadow-md hover:border-indigo-100 hover:scale-[1.02] transition-all duration-300 flex flex-col"
        >
          <div class="relative w-full aspect-video rounded-xl overflow-hidden bg-gray-100 mb-4 shrink-0">
            <img :src="banner.image" :alt="banner.title" class="w-full h-full object-cover" loading="lazy" />
            <div class="absolute top-2 right-2 bg-gray-900/70 backdrop-blur-md text-white text-xs font-semibold px-2 py-1 rounded-lg shadow-sm">
              Pos #{{ banner.position }}
            </div>
          </div>
  
          <div class="flex-1 px-1">
            <h3 class="font-semibold text-gray-900 text-sm truncate" :title="banner.title">{{ banner.title }}</h3>
            <a :href="banner.link" target="_blank" class="text-xs text-indigo-500 hover:text-indigo-600 truncate block mt-0.5" :title="banner.link">
              {{ banner.link || 'Tidak ada link' }}
            </a>
          </div>
  
          <div class="mt-4 flex items-center justify-end space-x-2 pt-3 border-t border-gray-100">
            <button 
              @click="openModal(banner)"
              class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors focus:outline-none"
              title="Edit Banner"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button 
              @click="confirmDelete(banner.id)"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors focus:outline-none"
              title="Hapus Banner"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
  
      <Transition name="modal-fade">
        <div v-if="isModalOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeModal"></div>
  
          <div class="modal-card relative bg-white rounded-2xl shadow-xl w-full max-w-lg border border-gray-100 flex flex-col overflow-hidden max-h-[90vh]">
            
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h3 class="text-lg font-semibold text-gray-900">{{ editingId ? 'Edit Banner' : 'Tambah Banner' }}</h3>
              <button @click="closeModal" class="text-gray-400 hover:text-gray-600 focus:outline-none">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
  
            <div class="p-6 overflow-y-auto">
              <form @submit.prevent="saveBanner" class="space-y-5">
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Gambar Banner</label>
                  <div 
                    class="relative flex flex-col items-center justify-center w-full aspect-video border-2 border-dashed rounded-xl transition-all duration-200 overflow-hidden cursor-pointer bg-gray-50 hover:bg-gray-100 group"
                    :class="imagePreview ? 'border-transparent' : 'border-gray-300 hover:border-indigo-400'"
                    @click="triggerFileInput"
                  >
                    <template v-if="imagePreview">
                      <img :src="imagePreview" class="w-full h-full object-cover" />
                      <div class="absolute inset-0 bg-gray-900/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <span class="text-white text-sm font-medium drop-shadow-md">Ganti Gambar</span>
                      </div>
                    </template>
                    <template v-else>
                      <svg class="w-8 h-8 text-gray-400 mb-2 group-hover:text-indigo-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p class="text-sm text-gray-500 font-medium">Klik untuk upload gambar</p>
                      <p class="text-xs text-gray-400 mt-1">PNG, JPG, WEBP (Max 2MB)</p>
                    </template>
                    <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileChange" />
                  </div>
                </div>
  
                <div class="grid grid-cols-3 gap-4">
                  <div class="col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Judul</label>
                    <input 
                      v-model="form.title" 
                      type="text" 
                      required 
                      placeholder="Promo Kemerdekaan" 
                      class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Posisi</label>
                    <input 
                      v-model.number="form.position" 
                      type="number" 
                      min="1"
                      required 
                      class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                    />
                  </div>
                </div>
  
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Tautan (URL)</label>
                  <input 
                    v-model="form.link" 
                    type="url" 
                    placeholder="https://pasarcctv.com/promo..." 
                    class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                  />
                </div>
  
              </form>
            </div>
  
            <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-end space-x-3 rounded-b-2xl">
              <button 
                type="button" 
                @click="closeModal" 
                class="px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 active:scale-95 transition-all"
              >
                Batal
              </button>
              <button 
                @click="saveBanner" 
                :disabled="isSubmitting"
                class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500/50 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed transition-all flex items-center justify-center min-w-[100px]"
              >
                <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ isSubmitting ? 'Menyimpan...' : 'Simpan' }}
              </button>
            </div>
  
          </div>
        </div>
      </transition>
  
      <Transition name="modal-fade">
        <div v-if="isDeleteModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="isDeleteModalOpen = false"></div>
          <div class="modal-card relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center border border-gray-100">
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-1">Hapus Banner?</h3>
            <p class="text-sm text-gray-500 mb-6">Aksi ini tidak dapat dibatalkan. Banner akan dihapus secara permanen dari sistem.</p>
            <div class="flex space-x-3">
              <button @click="isDeleteModalOpen = false" class="flex-1 py-2.5 bg-white border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 active:scale-95 transition-all">Batal</button>
              <button @click="deleteBanner" :disabled="isSubmitting" class="flex-1 py-2.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 active:scale-95 disabled:opacity-70 transition-all flex justify-center items-center">
                <span v-if="!isSubmitting">Hapus</span>
                <svg v-else class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </transition>
  
    </div>
  </template>
  
  <script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/service/api' // <-- Mengambil instance API dari service kamu
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

// Base path untuk endpoint xbanner
const API_BASE = '/banner'

// --- STATE MANAGEMENT ---
const banners = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)

const isModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const editingId = ref(null)
const bannerToDelete = ref(null)

const fileInput = ref(null)
const selectedFile = ref(null)
const imagePreview = ref(null)

const form = reactive({
  title: '',
  link: '',
  position: 1
})

// --- FETCH DATA ---
const fetchBanners = async () => {
  isLoading.value = true
  try {
    // Menggunakan api.get()
    const response = await api.get(`${API_BASE}/`)
    
    // Axios otomatis mengubah response ke JSON yang bisa diakses via response.data
    const rawData = response.data
    
    // Mapping dari format RAW FastAPI ke standar frontend kita
    banners.value = rawData.map(b => ({
      id: b.id,
      title: b.t,
      link: b.l,
      image: b.img,
      position: b.p
    })).sort((a, b) => a.position - b.position)
    
  } catch (error) {
    console.error('Error fetching banners:', error)
    const errorMsg = error.response?.data?.detail || 'Terjadi kesalahan saat memuat data.'
    toastStore.error(errorMsg)
  } finally {
    isLoading.value = false
  }
}

// --- MODAL & FORM LOGIC ---
const openModal = (banner = null) => {
  if (banner) {
    editingId.value = banner.id
    form.title = banner.title
    form.link = banner.link
    form.position = banner.position
    imagePreview.value = banner.image
    selectedFile.value = null
  } else {
    editingId.value = null
    form.title = ''
    form.link = ''
    form.position = banners.value.length > 0 ? Math.max(...banners.value.map(b => b.position)) + 1 : 1
    imagePreview.value = null
    selectedFile.value = null
  }
  isModalOpen.value = true
}

const closeModal = () => {
  if (isSubmitting.value) return
  isModalOpen.value = false
}

// --- IMAGE UPLOAD LOGIC ---
const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Validasi ukuran (Max 2MB)
  if (file.size > 2 * 1024 * 1024) {
    toastStore.error('Ukuran gambar maksimal 2MB')
    return
  }

  selectedFile.value = file
  
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// --- SUBMIT CREATE / EDIT ---
const saveBanner = async () => {
  // Validasi: Wajib ada gambar untuk banner baru
  if (!editingId.value && !selectedFile.value) {
    toastStore.error('Silakan pilih gambar banner terlebih dahulu.')
    return
  }

  isSubmitting.value = true
  const formData = new FormData()
  
  if (selectedFile.value) formData.append('file', selectedFile.value)
  formData.append('title', form.title)
  formData.append('link', form.link || '')
  formData.append('position', form.position)

  try {
    if (editingId.value) {
      await api.put(`${API_BASE}/admin/${editingId.value}`, formData)
      toastStore.success('Banner berhasil diperbarui!')
    } else {
      await api.post(`${API_BASE}/admin/create`, formData)
      toastStore.success('Banner baru berhasil ditambahkan!')
    }

    await fetchBanners()
    closeModal()
  } catch (error) {
    console.error('Error saving banner:', error)
    const errorMsg = error.response?.data?.detail || 'Terjadi kesalahan saat menyimpan banner.'
    toastStore.error(errorMsg)
  } finally {
    isSubmitting.value = false
  }
}

// --- DELETE LOGIC ---
const confirmDelete = (id) => {
  bannerToDelete.value = id
  isDeleteModalOpen.value = true
}

const deleteBanner = async () => {
  if (!bannerToDelete.value) return
  isSubmitting.value = true

  try {
    await api.delete(`${API_BASE}/admin/${bannerToDelete.value}`)
    toastStore.success('Banner berhasil dihapus!')
    await fetchBanners()
    isDeleteModalOpen.value = false
  } catch (error) {
    console.error('Error deleting banner:', error)
    const errorMsg = error.response?.data?.detail || 'Terjadi kesalahan saat menghapus data.'
    toastStore.error(errorMsg)
  } finally {
    isSubmitting.value = false
    bannerToDelete.value = null
  }
}

// --- INITIALIZE ---
onMounted(() => {
  fetchBanners()
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