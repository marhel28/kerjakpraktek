<template>
    <div class="h-full max-w-7xl mx-auto flex flex-col font-sans text-gray-800">

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
            <div>
                <h1 class="text-2xl font-bold tracking-tight text-gray-900">Brand Logo Management</h1>
                <p class="mt-1 text-sm text-gray-500">Kelola daftar logo brand yang bermitra atau tersedia di
                    marketplace.</p>
            </div>
            <button @click="openModal()"
                class="inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-sm hover:bg-indigo-700 hover:shadow active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 shrink-0">
                <svg class="w-5 h-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                Tambah Brand
            </button>
        </div>

        <div v-if="isLoading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
            <div v-for="i in 10" :key="i"
                class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm animate-pulse flex flex-col">
                <div class="w-full h-24 bg-gray-100 rounded-xl mb-4"></div>
                <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
        </div>

        <div v-else-if="brands.length === 0"
            class="flex-1 flex flex-col items-center justify-center py-16 px-4 bg-white border border-gray-200 border-dashed rounded-2xl">
            <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round"
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
            </div>
            <h3 class="text-base font-semibold text-gray-900">Belum ada brand</h3>
            <p class="mt-1 text-sm text-gray-500 max-w-sm text-center">Tambahkan logo brand pertama Anda untuk
                ditampilkan di halaman depan marketplace.</p>
            <button @click="openModal()" class="mt-6 text-sm font-medium text-indigo-600 hover:text-indigo-500">
                + Tambah Brand Pertama
            </button>
        </div>

        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5 pb-12">
            <div v-for="brand in brands" :key="brand.id"
                class="group relative bg-white rounded-2xl p-4 border border-gray-200 shadow-sm hover:shadow-md hover:border-indigo-100 hover:scale-[1.02] transition-all duration-300 flex flex-col">
                <div v-if="brand.isFeatured" class="absolute top-3 right-3 z-10">
                    <span
                        class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-green-100 text-green-700">
                        Featured
                    </span>
                </div>

                <div
                    class="relative w-full h-28 bg-gray-50 rounded-xl overflow-hidden mb-4 shrink-0 flex items-center justify-center p-3 border border-gray-100 group-hover:bg-white transition-colors">
                    <img :src="brand.logo" :alt="brand.name"
                        class="w-full h-full object-contain filter group-hover:brightness-110 transition-all duration-300"
                        loading="lazy" />
                </div>

                <div class="flex-1 flex flex-col justify-end">
                    <h3 class="font-bold text-gray-900 text-sm truncate" :title="brand.name">{{ brand.name }}</h3>
                    <p class="text-xs text-gray-500 truncate mt-0.5" :title="brand.slug">/{{ brand.slug }}</p>
                    <p v-if="brand.route" class="text-[10px] text-indigo-500 font-medium truncate mt-1">Route: {{
                        brand.route }}</p>
                </div>

                <div
                    class="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-white via-white to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex justify-end space-x-1.5 rounded-b-2xl">
                    <button @click="openModal(brand)"
                        class="p-2 bg-white border border-gray-200 text-gray-600 hover:text-indigo-600 hover:border-indigo-200 hover:bg-indigo-50 rounded-lg shadow-sm transition-all focus:outline-none active:scale-95"
                        title="Edit Brand">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                    </button>
                    <button @click="confirmDelete(brand.id)"
                        class="p-2 bg-white border border-gray-200 text-gray-600 hover:text-red-600 hover:border-red-200 hover:bg-red-50 rounded-lg shadow-sm transition-all focus:outline-none active:scale-95"
                        title="Hapus Brand">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
            <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm transition-opacity" @click="closeModal">
                </div>

                <div
                    class="relative bg-white rounded-2xl shadow-xl w-full max-w-md border border-gray-100 flex flex-col overflow-hidden max-h-[90vh]">

                    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                        <h3 class="text-lg font-semibold text-gray-900">{{ editingId ? 'Edit Brand' : 'Tambah Brand' }}
                        </h3>
                        <button @click="closeModal"
                            class="text-gray-400 hover:text-gray-600 focus:outline-none active:scale-95">
                            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <div class="p-6 overflow-y-auto custom-scrollbar">
                        <form @submit.prevent="saveBrand" class="space-y-5">

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1.5">Logo Brand</label>
                                <div class="relative flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl transition-all duration-200 overflow-hidden cursor-pointer group"
                                    :class="imagePreview ? 'border-indigo-200 bg-white' : 'border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-indigo-400'"
                                    @click="triggerFileInput">
                                    <template v-if="imagePreview">
                                        <div class="p-4 w-full h-full flex items-center justify-center">
                                            <img :src="imagePreview"
                                                class="max-w-full max-h-full object-contain drop-shadow-sm" />
                                        </div>
                                        <div
                                            class="absolute inset-0 bg-gray-900/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[2px]">
                                            <span class="text-white text-sm font-medium">Ganti Logo</span>
                                        </div>
                                    </template>
                                    <template v-else>
                                        <div
                                            class="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                                            <svg class="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24"
                                                stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                        </div>
                                        <p class="text-sm text-gray-600 font-medium">Upload logo PNG/JPG</p>
                                        <p class="text-xs text-gray-400 mt-0.5">Maks. 2MB, transparan disarankan</p>
                                    </template>
                                    <input type="file" ref="fileInput" class="hidden"
                                        accept="image/png, image/jpeg, image/webp" @change="handleFileChange" />
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1.5">Nama Brand</label>
                                <input v-model="form.name" type="text" required placeholder="Contoh: Hikvision"
                                    class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                            </div>

                            <div class="grid grid-cols-3 gap-4">
                                <div class="col-span-2">
                                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Slug (URL)</label>
                                    <input v-model="form.slug" type="text" required placeholder="hikvision"
                                        class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Posisi</label>
                                    <input v-model.number="form.position" type="number" min="1" required
                                        class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1.5">Route Navigasi <span
                                        class="text-gray-400 font-normal">(Opsional)</span></label>
                                <input v-model="form.route" type="text" placeholder="/category/hikvision"
                                    class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                            </div>

                            <div
                                class="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
                                <div>
                                    <p class="text-sm font-medium text-gray-900">Jadikan Featured</p>
                                    <p class="text-xs text-gray-500">Tampilkan brand ini di posisi utama.</p>
                                </div>
                                <button type="button" @click="form.isFeatured = !form.isFeatured"
                                    :class="form.isFeatured ? 'bg-green-500' : 'bg-gray-200'"
                                    class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500/50">
                                    <span :class="form.isFeatured ? 'translate-x-5' : 'translate-x-0'"
                                        class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out"></span>
                                </button>
                            </div>

                        </form>
                    </div>

                    <div
                        class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-end space-x-3 rounded-b-2xl shrink-0">
                        <button type="button" @click="closeModal"
                            class="px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 active:scale-95 transition-all">
                            Batal
                        </button>
                        <button @click="saveBrand" :disabled="isSubmitting"
                            class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500/50 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed transition-all flex items-center justify-center min-w-[100px]">
                            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none"
                                viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                </path>
                            </svg>
                            {{ isSubmitting ? 'Menyimpan...' : 'Simpan' }}
                        </button>
                    </div>

                </div>
            </div>
        </transition>

        <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
            <div v-if="isDeleteModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
                <div class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm" @click="isDeleteModalOpen = false"></div>
                <div
                    class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center border border-gray-100">
                    <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                        <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                            stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </div>
                    <h3 class="text-lg font-bold text-gray-900 mb-1">Hapus Brand?</h3>
                    <p class="text-sm text-gray-500 mb-6">Logo dan data brand ini akan dihapus permanen. Tindakan ini
                        tidak
                        dapat dibatalkan.</p>
                    <div class="flex space-x-3">
                        <button @click="isDeleteModalOpen = false"
                            class="flex-1 py-2.5 bg-white border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 active:scale-95 transition-all">Batal</button>
                        <button @click="deleteBrand" :disabled="isSubmitting"
                            class="flex-1 py-2.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 active:scale-95 disabled:opacity-70 transition-all flex justify-center items-center">
                            <span v-if="!isSubmitting">Hapus</span>
                            <svg v-else class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4">
                                </circle>
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                </path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </transition>

    </div>
</template>

<style scoped>
/* Thin scrollbar for modal */
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: #e5e7eb;
    border-radius: 10px;
}

.custom-scrollbar:hover::-webkit-scrollbar-thumb {
    background-color: #d1d5db;
}
</style>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import api from '@/service/api'

// --- API SETUP ---
const API_BASE = '/brands'

// --- STATE MANAGEMENT ---
const brands = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)

const isModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const editingId = ref(null)
const brandToDelete = ref(null)

const fileInput = ref(null)
const selectedFile = ref(null)
const imagePreview = ref(null)

const form = reactive({
    name: '',
    slug: '',
    route: '',
    position: 1,
    isFeatured: false
})

// --- AUTO SLUG GENERATOR ---
// Otomatis membuat slug dari nama saat membuat brand baru
watch(() => form.name, (newVal) => {
    if (!editingId.value) {
        form.slug = newVal
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)+/g, '');
    }
})

// --- FETCH DATA ---
const fetchBrands = async () => {
    isLoading.value = true
    try {
        const response = await api.get(`${API_BASE}/`)
        const rawData = response.data

        // Mapping dari JSON Redis backend ke struktur frontend
        brands.value = rawData.map(b => ({
            id: b.id,
            name: b.n,
            slug: b.s,
            route: b.r,
            isFeatured: b.f,
            logo: b.img,
            // Karena position mungkin tidak dikembalikan di list Redis, 
            // berikan default fallback (jika backend tidak mengirim).
            position: b.position || 1
        }))
    } catch (error) {
        console.error('Error fetching brands:', error)
        const errorMsg = error.response?.data?.detail || 'Gagal memuat data brand.'
        alert(errorMsg)
    } finally {
        isLoading.value = false
    }
}

// --- MODAL & FORM LOGIC ---
const openModal = (brand = null) => {
    if (brand) {
        editingId.value = brand.id
        form.name = brand.name
        form.slug = brand.slug
        form.route = brand.route || ''
        form.position = brand.position || 1
        form.isFeatured = brand.isFeatured
        imagePreview.value = brand.logo
        selectedFile.value = null
    } else {
        editingId.value = null
        form.name = ''
        form.slug = ''
        form.route = ''
        form.position = brands.value.length > 0 ? brands.value.length + 1 : 1
        form.isFeatured = false
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

    if (file.size > 2 * 1024 * 1024) {
        alert('Ukuran gambar maksimal 2MB')
        return
    }

    selectedFile.value = file

    const reader = new FileReader()
    reader.onload = (e) => {
        imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
}

// --- SUBMIT (CREATE / EDIT) ---
const saveBrand = async () => {
    // Validasi: Wajib ada logo untuk brand baru
    if (!editingId.value && !selectedFile.value) {
        alert('Silakan upload logo brand terlebih dahulu.')
        return
    }

    isSubmitting.value = true
    const formData = new FormData()

    if (selectedFile.value) formData.append('file', selectedFile.value)
    formData.append('name', form.name)
    formData.append('slug', form.slug)
    if (form.route) formData.append('route', form.route)
    formData.append('position', form.position)
    // Backend FastAPI biasanya menerima string "true"/"false" untuk field boolean di FormData
    formData.append('is_featured', form.isFeatured ? 'true' : 'false')

    try {
        if (editingId.value) {
            // Edit
            await api.put(`${API_BASE}/admin/${editingId.value}`, formData)
        } else {
            // Create
            await api.post(`${API_BASE}/admin/create`, formData)
        }

        await fetchBrands()
        closeModal()
    } catch (error) {
        console.error('Error saving brand:', error)
        const errorMsg = error.response?.data?.detail || 'Terjadi kesalahan saat menyimpan brand.'
        alert(errorMsg)
    } finally {
        isSubmitting.value = false
    }
}

// --- DELETE LOGIC ---
const confirmDelete = (id) => {
    brandToDelete.value = id
    isDeleteModalOpen.value = true
}

const deleteBrand = async () => {
    if (!brandToDelete.value) return
    isSubmitting.value = true

    try {
        await api.delete(`${API_BASE}/admin/${brandToDelete.value}`)
        await fetchBrands()
        isDeleteModalOpen.value = false
    } catch (error) {
        console.error('Error deleting brand:', error)
        const errorMsg = error.response?.data?.detail || 'Terjadi kesalahan saat menghapus data.'
        alert(errorMsg)
    } finally {
        isSubmitting.value = false
        brandToDelete.value = null
    }
}

// --- INIT ---
onMounted(() => {
    fetchBrands()
})
</script>