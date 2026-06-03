<template>
  <div class="h-full max-w-7xl mx-auto flex flex-col font-sans text-gray-800">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-gray-900">Chatbot Logs & Ratings</h1>
        <p class="mt-1 text-sm text-gray-500">Tinjau respons dan penilaian kepuasan dari pelanggan untuk mengevaluasi akurasi PasarBot.</p>
      </div>
    </div>

    <!-- Filters Card -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 mb-6 flex flex-col sm:flex-row items-center gap-4 justify-between">
      <div class="flex items-center gap-2.5 w-full sm:w-auto">
        <button 
          @click="satisfactionFilter = 'all'"
          :class="[
            'px-4 py-2 text-xs font-semibold rounded-xl border transition-all duration-150',
            satisfactionFilter === 'all'
              ? 'bg-indigo-50 border-indigo-200 text-indigo-700 shadow-sm'
              : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
          ]"
        >
          Semua Evaluasi
        </button>
        <button 
          @click="satisfactionFilter = 'satisfied'"
          :class="[
            'px-4 py-2 text-xs font-semibold rounded-xl border transition-all duration-150 flex items-center gap-1.5',
            satisfactionFilter === 'satisfied'
              ? 'bg-green-50 border-green-200 text-green-700 shadow-sm'
              : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
          ]"
        >
          <span>👍</span> Puas
        </button>
        <button 
          @click="satisfactionFilter = 'unsatisfied'"
          :class="[
            'px-4 py-2 text-xs font-semibold rounded-xl border transition-all duration-150 flex items-center gap-1.5',
            satisfactionFilter === 'unsatisfied'
              ? 'bg-red-50 border-red-200 text-red-700 shadow-sm'
              : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
          ]"
        >
          <span>👎</span> Kurang Puas
        </button>
      </div>

      <div class="relative w-full sm:w-80">
        <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Cari kata kunci query..." 
          class="block w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 flex flex-col items-center justify-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-4 border-indigo-600/30 border-t-indigo-600 mb-4"></div>
      <p class="text-sm font-medium text-gray-500">Memuat log chatbot...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredLogs.length === 0" class="flex-1 flex flex-col items-center justify-center py-20 px-4 bg-white border border-gray-200 border-dashed rounded-2xl">
      <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-base font-semibold text-gray-900">Belum ada evaluasi</h3>
      <p class="mt-1 text-sm text-gray-500 max-w-sm text-center">Evaluasi kepuasan pelanggan terhadap PasarBot akan tampil di halaman ini.</p>
    </div>

    <!-- Table List -->
    <div v-else class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-12">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/70 border-b border-gray-100 text-xs font-semibold uppercase tracking-wider text-gray-500">
              <th class="px-6 py-4 w-44">Tanggal & Waktu</th>
              <th class="px-6 py-4">Pertanyaan User</th>
              <th class="px-6 py-4">Jawaban PasarBot</th>
              <th class="px-6 py-4 w-28 text-center">Rating</th>
              <th class="px-6 py-4 w-40 text-right">Tindakan</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 text-sm">
            <tr v-for="log in filteredLogs" :key="log.id" class="hover:bg-gray-50/50 transition-colors">
              <td class="px-6 py-4.5 text-gray-500 whitespace-nowrap">
                {{ formatDateTime(log.created_at) }}
              </td>
              <td class="px-6 py-4 font-medium text-gray-900 max-w-xs break-words">
                {{ log.query || '-' }}
              </td>
              <td class="px-6 py-4 text-gray-600 max-w-md break-words">
                <div class="line-clamp-3" :title="log.bot_reply">
                  {{ log.bot_reply || 'Tidak tercatat' }}
                </div>
              </td>
              <td class="px-6 py-4 text-center">
                <span 
                  :class="[
                    'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold shadow-sm border',
                    log.satisfied 
                      ? 'bg-green-50 text-green-700 border-green-200' 
                      : 'bg-red-50 text-red-700 border-red-200'
                  ]"
                >
                  <span class="mr-1">{{ log.satisfied ? '👍' : '👎' }}</span>
                  {{ log.satisfied ? 'Puas' : 'Kecewa' }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end space-x-2">
                  <!-- Quick FAQ creation for unsatisfied query -->
                  <button 
                    v-if="!log.satisfied && log.query"
                    @click="convertToFAQ(log.query)"
                    class="inline-flex items-center px-2.5 py-1.5 text-xs font-semibold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-lg shadow-sm border border-indigo-200 transition-all focus:outline-none"
                    title="Jadikan Jawaban Baru di FAQ"
                  >
                    + Buat FAQ
                  </button>
                  <button 
                    @click="confirmDelete(log.id)"
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors focus:outline-none"
                    title="Hapus Log"
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
          <h3 class="text-lg font-bold text-gray-900 mb-1">Hapus Log Evaluasi?</h3>
          <p class="text-sm text-gray-500 mb-6 font-sans">Aksi ini akan menghapus log rating terpilih dari database admin secara permanen.</p>
          <div class="flex space-x-3">
            <button @click="isDeleteModalOpen = false" class="flex-1 py-2.5 bg-white border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 active:scale-95 transition-all font-sans">Batal</button>
            <button @click="deleteLog" :disabled="isSubmitting" class="flex-1 py-2.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 active:scale-95 disabled:opacity-70 transition-all flex justify-center items-center font-sans">
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
import { useRouter } from 'vue-router'
import api from '@/service/api'
import { useToastStore } from '@/stores/toast'

// Router
const router = useRouter()
const toastStore = useToastStore()

// State
const logs = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)
const isDeleteModalOpen = ref(false)
const logToDelete = ref(null)

const searchQuery = ref('')
const satisfactionFilter = ref('all') // all, satisfied, unsatisfied

// Computed filter
const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    const matchesSearch = !searchQuery.value.trim() || 
                          (log.query && log.query.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
                          (log.bot_reply && log.bot_reply.toLowerCase().includes(searchQuery.value.toLowerCase()))
    
    let matchesSat = true
    if (satisfactionFilter.value === 'satisfied') {
      matchesSat = log.satisfied === true
    } else if (satisfactionFilter.value === 'unsatisfied') {
      matchesSat = log.satisfied === false
    }

    return matchesSearch && matchesSat
  })
})

// Fetch Data
const fetchLogs = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/chatbot/feedback')
    logs.value = res.data || []
  } catch (err) {
    console.error('Failed to fetch evaluation logs:', err)
    toastStore.error(err.response?.data?.detail || 'Gagal memuat log evaluasi.')
  } finally {
    isLoading.value = false
  }
}

// Convert unsatisfied query to FAQ
const convertToFAQ = (query) => {
  router.push({
    path: '/chatbot/faq',
    query: { question: query }
  })
}

// Delete Log
const confirmDelete = (id) => {
  logToDelete.value = id
  isDeleteModalOpen.value = true
}

const deleteLog = async () => {
  if (!logToDelete.value) return
  isSubmitting.value = true
  try {
    await api.delete(`/chatbot/feedback/${logToDelete.value}`)
    toastStore.success('Log evaluasi berhasil dihapus!')
    await fetchLogs()
    isDeleteModalOpen.value = false
  } catch (err) {
    console.error('Failed to delete log:', err)
    toastStore.error('Gagal menghapus log evaluasi.')
  } finally {
    isSubmitting.value = false
    logToDelete.value = null
  }
}

// Date formatter helper
const formatDateTime = (isoString) => {
  if (!isoString) return '-'
  const d = new Date(isoString)
  return d.toLocaleString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchLogs()
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
