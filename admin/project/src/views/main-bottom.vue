<template>
    <div class="h-full max-w-7xl mx-auto flex flex-col font-sans text-gray-800">
  
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-gray-900">Banner Bawah Halaman</h1>
          <p class="mt-1 text-sm text-gray-500">Kelola banner yang muncul di bagian bawah homepage (maks. 4 aktif).</p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button
            @click="openPreview"
            class="inline-flex items-center justify-center px-4 py-2.5 bg-white text-gray-700 text-sm font-semibold rounded-xl shadow-sm border border-gray-200 hover:bg-gray-50 hover:shadow active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
          >
            <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            Preview
          </button>
          <button
            @click="openModal()"
            class="inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-sm hover:bg-indigo-700 hover:shadow active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <svg class="w-5 h-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Tambah Banner
          </button>
        </div>
      </div>
  
      <!-- Loading Skeleton -->
      <div v-if="isLoading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
        <div v-for="i in 8" :key="i"
          class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm animate-pulse flex flex-col">
          <div class="w-full h-24 bg-gray-100 rounded-xl mb-4"></div>
          <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
  
      <!-- Empty State -->
      <div v-else-if="banners.length === 0"
        class="flex-1 flex flex-col items-center justify-center py-16 px-4 bg-white border border-gray-200 border-dashed rounded-2xl">
        <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 class="text-base font-semibold text-gray-900">Belum ada banner</h3>
        <p class="mt-1 text-sm text-gray-500 max-w-sm text-center">Tambahkan banner promosi atau informasi untuk
          ditampilkan di bagian bawah homepage.</p>
        <button @click="openModal()" class="mt-6 text-sm font-medium text-indigo-600 hover:text-indigo-500">
          + Tambah Banner Pertama
        </button>
      </div>
  
      <!-- Banner Grid -->
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5 pb-12">
        <div v-for="banner in banners" :key="banner.uuid"
          class="group relative bg-white rounded-2xl p-4 border border-gray-200 shadow-sm hover:shadow-md hover:border-indigo-100 hover:scale-[1.02] transition-all duration-300 flex flex-col">
  
          <!-- Active Badge -->
          <div class="absolute top-3 right-3 z-10">
            <span v-if="banner.is_active"
              class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-green-100 text-green-700">
              Aktif
            </span>
            <span v-else
              class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-gray-100 text-gray-500">
              Nonaktif
            </span>
          </div>
  
          <!-- Image -->
          <div
            class="relative w-full h-28 bg-gray-50 rounded-xl overflow-hidden mb-4 shrink-0 flex items-center justify-center p-3 border border-gray-100 group-hover:bg-white transition-colors">
            <img :src="banner.image_url" :alt="banner.title"
              class="w-full h-full object-contain filter group-hover:brightness-110 transition-all duration-300"
              loading="lazy" />
          </div>
  
          <!-- Info -->
          <div class="flex-1 flex flex-col justify-end">
            <h3 class="font-bold text-gray-900 text-sm line-clamp-2" :title="banner.title">{{ banner.title }}</h3>
            <p class="text-xs text-gray-500 truncate mt-0.5">Urutan: {{ banner.sort_order }}</p>
            <p class="text-[10px] text-indigo-500 font-medium truncate mt-1">{{ banner.route_link }}</p>
          </div>
  
          <!-- Hover Actions -->
          <div
            class="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-white via-white to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex justify-end space-x-1.5 rounded-b-2xl">
            <button @click="openModal(banner)"
              class="p-2 bg-white border border-gray-200 text-gray-600 hover:text-indigo-600 hover:border-indigo-200 hover:bg-indigo-50 rounded-lg shadow-sm transition-all focus:outline-none active:scale-95"
              title="Edit Banner">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button @click="confirmDelete(banner.uuid)"
              class="p-2 bg-white border border-gray-200 text-gray-600 hover:text-red-600 hover:border-red-200 hover:bg-red-50 rounded-lg shadow-sm transition-all focus:outline-none active:scale-95"
              title="Hapus Banner">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
  
      <!-- ════════════ MODAL: CREATE / EDIT ════════════ -->
      <teleport to="body">
        <Transition name="modal-fade">
          <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm" @click="closeModal"></div>
            <div
              class="modal-card relative bg-white rounded-2xl shadow-xl w-full max-w-md border border-gray-100 flex flex-col overflow-hidden max-h-[90vh]">
  
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                <h3 class="text-lg font-semibold text-gray-900">{{ editingId ? 'Edit Banner' : 'Tambah Banner' }}</h3>
                <button @click="closeModal" class="text-gray-400 hover:text-gray-600 focus:outline-none active:scale-95">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
  
              <!-- Form -->
              <div class="p-6 overflow-y-auto custom-scrollbar">
                <form @submit.prevent="saveBanner" class="space-y-5">
  
                  <!-- Image Upload -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Gambar Banner</label>
                    <div class="relative flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl transition-all duration-200 overflow-hidden cursor-pointer group"
                      :class="imagePreview ? 'border-indigo-200 bg-white' : 'border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-indigo-400'"
                      @click="triggerFileInput">
                      <template v-if="imagePreview">
                        <div class="p-4 w-full h-full flex items-center justify-center">
                          <img :src="imagePreview" alt="Pratinjau banner bawah" class="max-w-full max-h-full object-contain drop-shadow-sm" />
                        </div>
                        <div
                          class="absolute inset-0 bg-gray-900/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[2px]">
                          <span class="text-white text-sm font-medium">Ganti Gambar</span>
                        </div>
                      </template>
                      <template v-else>
                        <div
                          class="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                          <svg class="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <p class="text-sm text-gray-600 font-medium">Upload gambar (WebP/PNG/JPG)</p>
                        <p class="text-xs text-gray-400 mt-0.5">Maks. 2MB, disarankan 720x360px</p>
                      </template>
                      <input type="file" ref="fileInput" class="hidden" accept="image/png, image/jpeg, image/webp"
                        @change="handleFileChange" />
                    </div>
                  </div>
  
                  <!-- Title -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Judul</label>
                    <input v-model="form.title" type="text" required placeholder="Contoh: Ambil Promonya Sekarang!"
                      class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                  </div>
  
                  <!-- Route Link -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Route Tujuan</label>
                    <input v-model="form.route_link" type="text" required placeholder="/promo atau /category/cctv"
                      class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                    <p class="text-xs text-gray-400 mt-1">Halaman yang dibuka saat banner diklik.</p>
                  </div>
  
                  <!-- Sort Order & Active Switch -->
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">Urutan</label>
                      <input v-model.number="form.sort_order" type="number" min="0" required
                        class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                    </div>
                    <div class="flex items-end pb-1">
                      <div class="flex items-center justify-between w-full p-3 bg-gray-50 rounded-xl border border-gray-100">
                        <div>
                          <p class="text-sm font-medium text-gray-900">Aktif</p>
                          <p class="text-xs text-gray-500">Tampilkan di homepage</p>
                        </div>
                        <button type="button" @click="form.is_active = !form.is_active"
                          :class="form.is_active ? 'bg-green-500' : 'bg-gray-200'"
                          class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500/50">
                          <span :class="form.is_active ? 'translate-x-5' : 'translate-x-0'"
                            class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out"></span>
                        </button>
                      </div>
                    </div>
                  </div>
  
                </form>
              </div>
  
              <!-- Modal Footer -->
              <div
                class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-end space-x-3 rounded-b-2xl shrink-0">
                <button type="button" @click="closeModal"
                  class="px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 active:scale-95 transition-all">
                  Batal
                </button>
                <button @click="saveBanner" :disabled="isSubmitting"
                  class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500/50 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed transition-all flex items-center justify-center min-w-[100px]">
                  <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
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
      </teleport>
  
      <!-- ════════════ MODAL: DELETE CONFIRM ════════════ -->
      <teleport to="body">
        <Transition name="modal-fade">
          <div v-if="isDeleteModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm" @click="isDeleteModalOpen = false"></div>
            <div class="modal-card relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center border border-gray-100">
              <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900 mb-1">Hapus Banner?</h3>
              <p class="text-sm text-gray-500 mb-6">Gambar dan data banner ini akan dihapus permanen. Tindakan ini tidak
                dapat dibatalkan.</p>
              <div class="flex space-x-3">
                <button @click="isDeleteModalOpen = false"
                  class="flex-1 py-2.5 bg-white border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 active:scale-95 transition-all">
                  Batal
                </button>
                <button @click="deleteBanner" :disabled="isSubmitting"
                  class="flex-1 py-2.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 active:scale-95 disabled:opacity-70 transition-all flex justify-center items-center">
                  <span v-if="!isSubmitting">Hapus</span>
                  <svg v-else class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </teleport>
  
      <!-- ════════════ PREVIEW PANEL ════════════ -->
      <!--
        Komponen preview reusable. Untuk halaman ini:
        - hanya ada 1 preset URL (Home), karena banner ini khusus homepage
        - section prop dibuat sintetis dari data banners yang ada
        - tidak ada apply-mode (banner ini tidak pakai mode layout)
      -->
      <ImageSectionPreview
        v-model="showPreview"
        :section="previewSectionSynthetic"
        :extra-presets="[]"
        :initial-url="HOME_URL"
        :hide-mode-picker="true"
      />
  
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed, onMounted } from 'vue'
  import { useToastStore } from '@/stores/toast'
  import api from '@/service/api'
  import ImageSectionPreview from '@/components/ImageSectionPreview.vue'
  import { usePreviewStore } from '@/stores/previewStore'

  const toastStore = useToastStore()
  const previewStore = usePreviewStore()

  const ADMIN_BASE = '/main-bottom/admin'
  const HOME_URL   = previewStore.resolveUrl('/')
  
  // ── State ─────────────────────────────────────────────
  const banners          = ref([])
  const isLoading        = ref(true)
  const isSubmitting     = ref(false)
  const isModalOpen      = ref(false)
  const isDeleteModalOpen = ref(false)
  const editingId        = ref(null)
  const bannerToDelete   = ref(null)
  const showPreview      = ref(false)
  
  const fileInput    = ref(null)
  const selectedFile = ref(null)
  const imagePreview = ref(null)
  
  const form = reactive({
    title:      '',
    route_link: '',
    is_active:  true,
    sort_order: 0,
  })
  
  /**
   * Synthetic "section" object passed to ImageSectionPreview.
   * The preview component needs a section shape to show info like item count.
   * We build it from the banners list so the panel shows meaningful data.
   */
  const previewSectionSynthetic = computed(() => ({
    uuid:       null,
    identifier: 'main-bottom',
    title:      'Banner Bawah Halaman',
    mode:       null,
    is_active:  true,
    items:      banners.value.filter(b => b.is_active),
  }))
  
  // ── Fetch ─────────────────────────────────────────────
  const fetchBanners = async () => {
    isLoading.value = true
    try {
      const response = await api.get(ADMIN_BASE)
      banners.value = response.data.data || []
    } catch (error) {
      console.error('Error fetching banners:', error)
      toastStore.error(error.response?.data?.detail || 'Gagal memuat data banner.')
    } finally {
      isLoading.value = false
    }
  }
  
  // ── Preview ───────────────────────────────────────────
  const openPreview = () => {
    showPreview.value = true
  }
  
  // ── Modal controllers ─────────────────────────────────
  const openModal = (banner = null) => {
    if (banner) {
      editingId.value     = banner.uuid
      form.title          = banner.title
      form.route_link     = banner.route_link
      form.is_active      = banner.is_active
      form.sort_order     = banner.sort_order
      imagePreview.value  = banner.image_url
      selectedFile.value  = null
    } else {
      editingId.value     = null
      form.title          = ''
      form.route_link     = ''
      form.is_active      = true
      form.sort_order     = banners.value.length + 1
      imagePreview.value  = null
      selectedFile.value  = null
    }
    isModalOpen.value = true
  }
  
  const closeModal = () => {
    if (isSubmitting.value) return
    isModalOpen.value = false
  }
  
  // ── File handling ─────────────────────────────────────
  const triggerFileInput = () => fileInput.value?.click()
  
  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (!file) return
    if (file.size > 2 * 1024 * 1024) { toastStore.warning('Ukuran gambar maksimal 2MB'); return }
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => { imagePreview.value = e.target.result }
    reader.readAsDataURL(file)
  }
  
  // ── Save ──────────────────────────────────────────────
  const saveBanner = async () => {
    if (!editingId.value && !selectedFile.value) {
      toastStore.warning('Silakan upload gambar banner terlebih dahulu.')
      return
    }
    isSubmitting.value = true
    const formData = new FormData()
    formData.append('title',      form.title)
    formData.append('route_link', form.route_link)
    formData.append('is_active',  form.is_active ? 'true' : 'false')
    formData.append('sort_order', form.sort_order)
    if (selectedFile.value) formData.append('file', selectedFile.value)
  
    try {
      if (editingId.value) {
        await api.put(`${ADMIN_BASE}/${editingId.value}`, formData)
      } else {
        await api.post(ADMIN_BASE, formData)
      }
      await fetchBanners()
      closeModal()
      toastStore.success('Banner berhasil disimpan.')
    } catch (error) {
      console.error('Error saving banner:', error)
      toastStore.error(error.response?.data?.detail || 'Terjadi kesalahan saat menyimpan banner.')
    } finally {
      isSubmitting.value = false
    }
  }
  
  // ── Delete ────────────────────────────────────────────
  const confirmDelete = (uuid) => {
    bannerToDelete.value   = uuid
    isDeleteModalOpen.value = true
  }
  
  const deleteBanner = async () => {
    if (!bannerToDelete.value) return
    isSubmitting.value = true
    try {
      await api.delete(`${ADMIN_BASE}/${bannerToDelete.value}`)
      await fetchBanners()
      isDeleteModalOpen.value = false
      toastStore.success('Banner berhasil dihapus.')
    } catch (error) {
      console.error('Error deleting banner:', error)
      toastStore.error(error.response?.data?.detail || 'Gagal menghapus banner.')
    } finally {
      isSubmitting.value = false
      bannerToDelete.value = null
    }
  }
  
  // ── Init ──────────────────────────────────────────────
  onMounted(() => fetchBanners())
  </script>
  
  <style scoped>
  .custom-scrollbar::-webkit-scrollbar { width: 6px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 10px; }
  .custom-scrollbar:hover::-webkit-scrollbar-thumb { background-color: #d1d5db; }
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

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