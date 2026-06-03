<template>
  <div class="h-full max-w-7xl mx-auto flex flex-col font-sans text-gray-800">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-gray-900">FAQ Database</h1>
        <p class="mt-1 text-sm text-gray-500">Kelola daftar Tanya-Jawab (Q&A) yang digunakan PasarBot untuk merespons pertanyaan pelanggan secara lokal.</p>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="reloadIndex"
          :disabled="isReloading"
          class="inline-flex items-center justify-center px-4 py-2.5 bg-white border border-gray-300 text-gray-700 text-sm font-semibold rounded-xl shadow-sm hover:bg-gray-50 active:scale-95 transition-all duration-200 focus:outline-none disabled:opacity-50"
        >
          <svg v-if="isReloading" class="animate-spin -ml-1 mr-1.5 h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-4 h-4 mr-1.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 7.89l-2.094 2.094" />
          </svg>
          {{ isReloading ? 'Menyinkronkan...' : 'Sinkronkan Index' }}
        </button>
        <button 
          @click="openModal()"
          class="inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-sm hover:bg-indigo-700 active:scale-95 transition-all duration-200 focus:outline-none shrink-0"
        >
          <svg class="w-5 h-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Tambah Q&A
        </button>
      </div>
    </div>

    <!-- Search & Filter Card -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 mb-6 flex flex-col md:flex-row items-center gap-4 justify-between">
      <div class="relative w-full md:w-96">
        <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Cari pertanyaan atau jawaban..." 
          class="block w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
        />
      </div>

      <!-- Category Filter Pills -->
      <div class="flex flex-wrap gap-2 w-full md:w-auto">
        <button 
          v-for="cat in categories" 
          :key="cat.value"
          @click="selectedCategory = cat.value"
          :class="[
            'px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150',
            selectedCategory === cat.value 
              ? 'bg-indigo-600 text-white shadow-sm' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ cat.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 flex flex-col items-center justify-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-4 border-indigo-600/30 border-t-indigo-600 mb-4"></div>
      <p class="text-sm font-medium text-gray-500">Memuat basis pengetahuan...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredEntries.length === 0" class="flex-1 flex flex-col items-center justify-center py-20 px-4 bg-white border border-gray-200 border-dashed rounded-2xl">
      <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-base font-semibold text-gray-900">Q&A tidak ditemukan</h3>
      <p class="mt-1 text-sm text-gray-500 max-w-sm text-center">Coba ubah kata kunci pencarian Anda atau tambahkan data Tanya-Jawab baru.</p>
    </div>

    <!-- Table List -->
    <div v-else class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-12">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/70 border-b border-gray-100 text-xs font-semibold uppercase tracking-wider text-gray-500">
              <th class="px-6 py-4">Tanya / Jawab</th>
              <th class="px-6 py-4 w-32">Kategori</th>
              <th class="px-6 py-4 w-28 text-center">Hit Count</th>
              <th class="px-6 py-4 w-28 text-center">Status</th>
              <th class="px-6 py-4 w-28 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 text-sm">
            <tr v-for="entry in filteredEntries" :key="entry.uuid" class="hover:bg-gray-50/50 transition-colors group">
              <td class="px-6 py-4.5 max-w-xl">
                <div class="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors line-clamp-1" :title="entry.question">
                  {{ entry.question }}
                </div>
                <div class="text-xs text-gray-500 mt-1 line-clamp-2" :title="entry.answer">
                  {{ entry.answer }}
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                  {{ entry.category }}
                </span>
              </td>
              <td class="px-6 py-4 text-center font-medium text-gray-900">
                {{ entry.hit_count }}
              </td>
              <td class="px-6 py-4 text-center">
                <button 
                  @click="toggleStatus(entry)"
                  :class="[
                    'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold shadow-sm transition-all focus:outline-none',
                    entry.is_active 
                      ? 'bg-green-50 text-green-700 border border-green-200 hover:bg-green-100' 
                      : 'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100'
                  ]"
                >
                  <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="entry.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
                  {{ entry.is_active ? 'Aktif' : 'Non-Aktif' }}
                </button>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end space-x-1">
                  <button 
                    @click="openModal(entry)"
                    class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors focus:outline-none"
                    title="Edit Q&A"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button 
                    @click="confirmDelete(entry.uuid)"
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors focus:outline-none"
                    title="Hapus Q&A"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit/Create Modal -->
    <Transition name="modal-fade">
      <div v-if="isModalOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeModal"></div>

        <!-- Modal Card -->
        <div class="modal-card relative bg-white rounded-2xl shadow-xl w-full max-w-2xl border border-gray-100 flex flex-col overflow-hidden max-h-[90vh] z-10">
          
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
            <h3 class="text-lg font-semibold text-gray-900">{{ editingUuid ? 'Edit Q&A Pair' : 'Tambah Q&A Baru' }}</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600 focus:outline-none">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-6 overflow-y-auto">
            <form @submit.prevent="saveEntry" class="space-y-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Kategori</label>
                <select 
                  v-model="form.category" 
                  required
                  class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all font-sans"
                >
                  <option value="general">Umum (General)</option>
                  <option value="harga">Harga & Promo</option>
                  <option value="garansi">Garansi & Retur</option>
                  <option value="layanan">Layanan Jasa</option>
                  <option value="pengiriman">Pengiriman & COD</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Pertanyaan (User Query)</label>
                <input 
                  v-model="form.question" 
                  type="text" 
                  required 
                  placeholder="Contoh: Bagaimana cara klaim garansi PasarCCTV?" 
                  class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all font-sans"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Jawaban (Bot Response)</label>
                <textarea 
                  v-model="form.answer" 
                  required 
                  rows="6"
                  placeholder="Tuliskan jawaban yang lengkap, jelas, dan ramah..." 
                  class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all resize-none font-sans"
                ></textarea>
              </div>
            </form>
          </div>

          <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-end space-x-3 rounded-b-2xl">
            <button 
              type="button" 
              @click="closeModal" 
              class="px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 active:scale-95 transition-all font-sans"
            >
              Batal
            </button>
            <button 
              @click="saveEntry" 
              :disabled="isSubmitting"
              class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500/50 active:scale-95 disabled:opacity-70 transition-all flex items-center justify-center min-w-[100px] font-sans font-semibold"
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
    </Transition>

    <!-- Delete Confirmation Modal -->
    <Transition name="modal-fade">
      <div v-if="isDeleteModalOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="isDeleteModalOpen = false"></div>

        <!-- Modal Card -->
        <div class="modal-card relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center border border-gray-100 z-10">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
            <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-1">Hapus Q&A?</h3>
          <p class="text-sm text-gray-500 mb-6 font-sans">Aksi ini akan menghapus pasangan Tanya-Jawab ini secara permanen dari basis pengetahuan chatbot.</p>
          <div class="flex space-x-3">
            <button @click="isDeleteModalOpen = false" class="flex-1 py-2.5 bg-white border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 active:scale-95 transition-all font-sans">Batal</button>
            <button @click="deleteEntry" :disabled="isSubmitting" class="flex-1 py-2.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 active:scale-95 disabled:opacity-70 transition-all flex justify-center items-center font-sans">
              <span>Hapus</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/service/api'
import { useToastStore } from '@/stores/toast'

// Route parameters (for checking prefill from chatbot logs page)
const route = useRoute()
const toastStore = useToastStore()

// State
const entries = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)
const isReloading = ref(false)
const isModalOpen = ref(false)
const isDeleteModalOpen = ref(false)

const editingUuid = ref(null)
const uuidToDelete = ref(null)
const searchQuery = ref('')
const selectedCategory = ref('all')

const form = reactive({
  question: '',
  answer: '',
  category: 'general'
})

const categories = [
  { label: 'Semua Kategori', value: 'all' },
  { label: 'Umum', value: 'general' },
  { label: 'Harga & Promo', value: 'harga' },
  { label: 'Garansi', value: 'garansi' },
  { label: 'Jasa Pasang', value: 'layanan' },
  { label: 'Pengiriman', value: 'pengiriman' }
]

// Computed filtering
const filteredEntries = computed(() => {
  return entries.value.filter(e => {
    const matchesSearch = e.question.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          e.answer.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value === 'all' || e.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

// Fetch Data
const fetchEntries = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/chatbot/knowledge')
    entries.value = res.data || []
  } catch (err) {
    console.error('Failed to load FAQ database:', err)
    toastStore.error(err.response?.data?.detail || 'Terjadi kesalahan saat memuat data FAQ.')
  } finally {
    isLoading.value = false
  }
}

// Reload TurboQuant index
const reloadIndex = async () => {
  isReloading.value = true
  try {
    await api.post('/chatbot/knowledge/init')
    toastStore.success('Index FAQ berhasil diperbarui!')
  } catch (err) {
    console.error('Failed to reload index:', err)
    toastStore.error('Gagal menyinkronkan index chatbot.')
  } finally {
    isReloading.value = false
  }
}

// Open modal for Create / Edit
const openModal = (entry = null) => {
  if (entry) {
    editingUuid.value = entry.uuid
    form.question = entry.question
    form.answer = entry.answer
    form.category = entry.category
  } else {
    editingUuid.value = null
    form.question = ''
    form.answer = ''
    form.category = 'general'
  }
  isModalOpen.value = true
}

const closeModal = () => {
  if (isSubmitting.value) return
  isModalOpen.value = false
}

// Save (Create/Update)
const saveEntry = async () => {
  if (!form.question.trim() || !form.answer.trim()) {
    toastStore.error('Kolom pertanyaan dan jawaban tidak boleh kosong.')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      question: form.question.trim(),
      answer: form.answer.trim(),
      category: form.category
    }

    if (editingUuid.value) {
      await api.patch(`/chatbot/knowledge/${editingUuid.value}`, payload)
      toastStore.success('Tanya-Jawab berhasil diperbarui!')
    } else {
      await api.post('/chatbot/knowledge', payload)
      toastStore.success('Tanya-Jawab baru berhasil ditambahkan!')
    }

    await fetchEntries()
    closeModal()
  } catch (err) {
    console.error('Failed to save Q&A:', err)
    toastStore.error(err.response?.data?.detail || 'Gagal menyimpan Tanya-Jawab.')
  } finally {
    isSubmitting.value = false
  }
}

// Toggle active status
const toggleStatus = async (entry) => {
  try {
    const updatedStatus = !entry.is_active
    await api.patch(`/chatbot/knowledge/${entry.uuid}`, {
      is_active: updatedStatus
    })
    entry.is_active = updatedStatus
    toastStore.success(`Tanya-Jawab berhasil ${updatedStatus ? 'diaktifkan' : 'dinonaktifkan'}!`)
  } catch (err) {
    console.error('Failed to toggle status:', err)
    toastStore.error('Gagal memperbarui status keaktifan.')
  }
}

// Delete
const confirmDelete = (uuid) => {
  uuidToDelete.value = uuid
  isDeleteModalOpen.value = true
}

const deleteEntry = async () => {
  if (!uuidToDelete.value) return
  isSubmitting.value = true
  try {
    await api.delete(`/chatbot/knowledge/${uuidToDelete.value}`)
    toastStore.success('Tanya-Jawab berhasil dihapus!')
    await fetchEntries()
    isDeleteModalOpen.value = false
  } catch (err) {
    console.error('Failed to delete Q&A:', err)
    toastStore.error(err.response?.data?.detail || 'Gagal menghapus Tanya-Jawab.')
  } finally {
    isSubmitting.value = false
    uuidToDelete.value = null
  }
}

// Initialize and handle pre-fills from routing (e.g. from chatbot logs page)
onMounted(() => {
  fetchEntries()
  
  if (route.query.question) {
    form.question = route.query.question
    form.answer = ''
    form.category = 'general'
    editingUuid.value = null
    isModalOpen.value = true
  }
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
