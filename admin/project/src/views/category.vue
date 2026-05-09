<template>
    <div class="h-full max-w-5xl mx-auto flex flex-col font-sans text-gray-800 pb-12">
  
      <!-- ── Header ── -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-gray-900">Category Management</h1>
          <p class="mt-1 text-sm text-gray-500">Kelola hierarki kategori utama dan subkategori untuk navigasi marketplace.</p>
        </div>
        <div class="flex items-center gap-3 shrink-0">
          <button
            @click="openPreview"
            class="inline-flex items-center justify-center px-4 py-2.5 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-xl shadow-sm hover:bg-gray-50 active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
          >
            <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            Preview
          </button>
          <button @click="openSubModal()"
            class="inline-flex items-center justify-center px-4 py-2.5 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-xl shadow-sm hover:bg-gray-50 active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
            + Subkategori
          </button>
          <button @click="openCatModal()"
            class="inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-sm hover:bg-indigo-700 hover:shadow active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
            <svg class="w-5 h-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Kategori Utama
          </button>
        </div>
      </div>
  
      <!-- ── Loading ── -->
      <div v-if="isLoading" class="space-y-4">
        <div v-for="i in 3" :key="i" class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm animate-pulse">
          <div class="flex items-center space-x-4">
            <div class="w-8 h-8 bg-gray-200 rounded-lg"></div>
            <div class="flex-1">
              <div class="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
              <div class="h-3 bg-gray-200 rounded w-1/6"></div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- ── Empty ── -->
      <div v-else-if="categories.length === 0"
        class="flex-1 flex flex-col items-center justify-center py-16 px-4 bg-white border border-gray-200 border-dashed rounded-2xl">
        <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
        </div>
        <h3 class="text-base font-semibold text-gray-900">Belum ada kategori</h3>
        <p class="mt-1 text-sm text-gray-500 max-w-sm text-center">Buat kategori utama terlebih dahulu untuk mulai menyusun navigasi produk.</p>
        <button @click="openCatModal()" class="mt-6 text-sm font-medium text-indigo-600 hover:text-indigo-500">+ Buat Kategori</button>
      </div>
  
      <!-- ── Category Tree ── -->
      <div v-else class="space-y-5">
        <div v-for="category in categories" :key="category.id"
          class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md">
          <div class="flex items-center justify-between p-5 bg-white relative z-10">
            <div class="flex items-center space-x-4">
              <button @click="toggleExpand(category.id)"
                class="p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700 rounded-lg transition-colors focus:outline-none">
                <svg class="w-5 h-5 transform transition-transform duration-200"
                  :class="isExpanded(category.id) ? 'rotate-90' : 'rotate-0'"
                  fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <div>
                <div class="flex items-center space-x-2">
                  <h3 class="font-bold text-gray-900 text-base">{{ category.name }}</h3>
                  <span v-if="category.icon" class="flex items-center gap-1 px-2 py-0.5 bg-indigo-50 text-indigo-600 text-[10px] rounded-md font-medium border border-indigo-100">
                    <svg v-if="getIconPath(category.icon)" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getIconPath(category.icon)" />
                    </svg>
                    {{ category.icon }}
                  </span>
                </div>
                <p class="text-xs text-gray-500 mt-0.5">/{{ category.slug }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button @click="openSubModal(category.id)"
                class="hidden sm:flex items-center px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors active:scale-95">
                + Subkategori
              </button>
              <button @click="confirmDelete(category.id)"
                class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors focus:outline-none active:scale-95"
                title="Hapus Kategori">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
  
          <div v-show="isExpanded(category.id)" class="border-t border-gray-100 bg-gray-50/50 p-4 pl-[4.5rem]">
            <div v-if="!category.subcategories || category.subcategories.length === 0" class="text-sm text-gray-400 italic py-2">Belum ada subkategori.</div>
            <div v-else class="space-y-2 border-l-2 border-indigo-100 pl-4 py-1 relative">
              <div v-for="sub in category.subcategories" :key="sub.slug"
                class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-xl hover:border-indigo-200 transition-colors shadow-sm group">
                <div class="absolute -left-[17px] w-4 h-[2px] bg-indigo-100"></div>
                <div>
                  <h4 class="text-sm font-semibold text-gray-800">{{ sub.name }}</h4>
                  <p class="text-[11px] text-gray-500 mt-0.5">/{{ sub.slug }}</p>
                </div>
                <div class="px-2.5 py-1 bg-gray-50 text-gray-400 text-xs rounded-lg border border-gray-100 font-medium group-hover:text-indigo-500 transition-colors">Subkategori</div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- ══════════════════════════════
           MODAL: TAMBAH KATEGORI
      ══════════════════════════════ -->
      <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
        <div v-if="showCatModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeModals"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md border border-gray-100 flex flex-col overflow-hidden max-h-[90vh]">
  
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50 shrink-0">
              <h3 class="text-lg font-semibold text-gray-900">Tambah Kategori Utama</h3>
              <button @click="closeModals" class="text-gray-400 hover:text-gray-600 focus:outline-none">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
  
            <div class="p-6 overflow-y-auto custom-scrollbar flex-1">
              <form @submit.prevent="saveCategory" class="space-y-5">
  
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Nama Kategori</label>
                  <input v-model="catForm.name" type="text" required placeholder="Contoh: Kamera CCTV"
                    class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                </div>
  
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Slug (URL)</label>
                  <input v-model="catForm.slug" type="text" required placeholder="kamera-cctv"
                    class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                  <div class="mt-2 flex flex-wrap gap-1.5">
                    <span class="text-[11px] text-gray-500 mr-1 mt-1">Saran:</span>
                    <button v-for="s in slugSuggestions" :key="s" type="button" @click="catForm.slug = s"
                      class="px-2.5 py-1 text-[11px] font-medium bg-gray-100 hover:bg-indigo-50 hover:text-indigo-600 text-gray-600 rounded-md transition-colors">{{ s }}</button>
                  </div>
                </div>
  
                <!-- ── Icon Picker ── -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Pilih Ikon</label>
  
                  <!-- Selected preview -->
                  <div v-if="catForm.icon_name" class="flex items-center gap-3 mb-3 p-3 bg-indigo-50 rounded-xl border border-indigo-100">
                    <div class="w-9 h-9 bg-white rounded-lg flex items-center justify-center shadow-sm border border-indigo-100">
                      <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="getIconPath(catForm.icon_name)" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-xs font-semibold text-indigo-700">{{ getIconName(catForm.icon_name) }}</p>
                      <p class="text-[10px] text-indigo-400 font-mono">{{ catForm.icon_name }}</p>
                    </div>
                    <button type="button" @click="catForm.icon_name = ''" class="ml-auto text-indigo-300 hover:text-indigo-500">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path d="M6 18L18 6M6 6l12 12"/>
                      </svg>
                    </button>
                  </div>
  
                  <!-- Search -->
                  <div class="relative mb-2">
                    <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 105 11a6 6 0 0012 0z"/>
                    </svg>
                    <input
                      v-model="iconSearch"
                      type="text"
                      placeholder="Cari ikon... (mis: camera, shield, home)"
                      class="block w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:border-indigo-500 transition-all"
                    />
                  </div>
  
                  <!-- Icon Grid -->
                  <div class="grid grid-cols-7 gap-1.5 max-h-52 overflow-y-auto custom-scrollbar pr-1">
                    <button
                      v-for="icon in filteredIcons"
                      :key="icon.class"
                      type="button"
                      @click="catForm.icon_name = icon.class"
                      :class="[
                        'aspect-square rounded-xl border flex flex-col items-center justify-center gap-1 transition-all hover:bg-indigo-50 hover:border-indigo-300 group relative',
                        catForm.icon_name === icon.class
                          ? 'bg-indigo-50 border-indigo-500 text-indigo-600 shadow-sm ring-2 ring-indigo-500/30'
                          : 'bg-white border-gray-200 text-gray-500'
                      ]"
                      :title="icon.name"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="icon.path" />
                      </svg>
                      <!-- Tooltip on hover -->
                      <div class="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-gray-800 text-white text-[10px] px-2 py-1 rounded-md opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-10">
                        {{ icon.name }}
                      </div>
                    </button>
                    <div v-if="filteredIcons.length === 0" class="col-span-7 text-center py-6 text-sm text-gray-400">
                      Tidak ada ikon yang cocok untuk "{{ iconSearch }}"
                    </div>
                  </div>
  
                  <p class="text-[11px] text-gray-400 mt-2">{{ filteredIcons.length }} ikon tersedia · klik untuk pilih</p>
  
                  <!-- Manual input -->
                  <div class="flex items-center gap-2 mt-2">
                    <span class="text-[11px] text-gray-400 whitespace-nowrap">Input Manual:</span>
                    <input v-model="catForm.icon_name" type="text" placeholder="i-heroicons-..."
                      class="flex-1 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-xs focus:bg-white focus:outline-none focus:border-indigo-500 transition-all font-mono" />
                  </div>
                </div>
  
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Posisi Urutan</label>
                  <input v-model.number="catForm.position" type="number" min="1" required
                    class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                </div>
  
              </form>
            </div>
  
            <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end space-x-3 shrink-0">
              <button type="button" @click="closeModals"
                class="px-4 py-2.5 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 active:scale-95 transition-all">Batal</button>
              <button @click="saveCategory" :disabled="isSubmitting"
                class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500/50 active:scale-95 disabled:opacity-70 transition-all">
                {{ isSubmitting ? 'Menyimpan...' : 'Simpan Kategori' }}
              </button>
            </div>
          </div>
        </div>
      </transition>
  
      <!-- ══════════════════════════════
           MODAL: TAMBAH SUBKATEGORI
      ══════════════════════════════ -->
      <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
        <div v-if="showSubModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeModals"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md border border-gray-100 flex flex-col overflow-hidden">
  
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h3 class="text-lg font-semibold text-gray-900">Tambah Subkategori</h3>
              <button @click="closeModals" class="text-gray-400 hover:text-gray-600 focus:outline-none">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
  
            <div class="p-6">
              <form @submit.prevent="saveSubcategory" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Pilih Kategori Utama</label>
                  <select v-model="subForm.category_uuid" required
                    class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all cursor-pointer">
                    <option value="" disabled>-- Pilih Kategori --</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Nama Subkategori</label>
                  <input v-model="subForm.name" type="text" required placeholder="Contoh: IP Camera"
                    class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                </div>
                <div class="grid grid-cols-3 gap-4">
                  <div class="col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Slug (URL)</label>
                    <input v-model="subForm.slug" type="text" required placeholder="ip-camera"
                      class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Posisi</label>
                    <input v-model.number="subForm.position" type="number" min="1" required
                      class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
                  </div>
                </div>
              </form>
            </div>
  
            <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end space-x-3">
              <button type="button" @click="closeModals"
                class="px-4 py-2.5 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 active:scale-95 transition-all">Batal</button>
              <button @click="saveSubcategory" :disabled="isSubmitting"
                class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500/50 active:scale-95 disabled:opacity-70 transition-all">
                {{ isSubmitting ? 'Menyimpan...' : 'Simpan Subkategori' }}
              </button>
            </div>
          </div>
        </div>
      </transition>
  
      <!-- ── MODAL: HAPUS ── -->
      <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
        <div v-if="showDeleteModal" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="showDeleteModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center border border-gray-100">
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-1">Hapus Kategori?</h3>
            <p class="text-sm text-gray-500 mb-6">Kategori ini dan semua subkategorinya akan dihapus. Aksi ini tidak dapat dibatalkan.</p>
            <div class="flex space-x-3">
              <button @click="showDeleteModal = false"
                class="flex-1 py-2.5 bg-white border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 active:scale-95 transition-all">Batal</button>
              <button @click="deleteCategory" :disabled="isSubmitting"
                class="flex-1 py-2.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 active:scale-95 disabled:opacity-70 transition-all flex justify-center items-center">
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
  
      <!-- ══════════════════════════════
           PREVIEW PANEL
      ══════════════════════════════ -->
      <ImageSectionPreview
        v-model="showPreview"
        :section="previewSectionSynthetic"
        :extra-presets="categoryPresets"
        :initial-url="'http://localhost:3000/category/security-alarm'"
        :hide-mode-picker="true"
      />
  
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed, watch, onMounted } from 'vue'
  import api from '@/service/api'
  import ImageSectionPreview from '@/components/ImageSectionPreview.vue'
  
  const API_BASE = '/category'
  
  // ── Slug suggestions ─────────────────────────────────
  const slugSuggestions = ['kamera-cctv', 'dvr-nvr', 'paket-cctv', 'aksesoris', 'security-alarm', 'access-control', 'networking', 'smart-home']
  
  // ── Icon Search ───────────────────────────────────────
  const iconSearch = ref('')
  
  // ── 60+ Icons ─────────────────────────────────────────
  const availableIcons = [
    // ── Surveillance & Camera
    { name: 'Video Camera',       class: 'i-heroicons-video-camera',       tags: 'camera video cctv record',      path: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' },
    { name: 'Camera',             class: 'i-heroicons-camera',             tags: 'camera photo capture photo',    path: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z M15 13a3 3 0 11-6 0 3 3 0 016 0z' },
    { name: 'Eye / Monitor',      class: 'i-heroicons-eye',                tags: 'eye view monitor watch see',    path: 'M2.458 12C3.732 7.943 7.523 5 12 5s8.268 2.943 9.542 7c-1.274 4.057-5.065 7-9.542 7S3.732 16.057 2.458 12zM12 15a3 3 0 100-6 3 3 0 000 6z' },
    { name: 'Film Strip',         class: 'i-heroicons-film',               tags: 'film video movie recording',    path: 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z' },
    { name: 'Photo Gallery',      class: 'i-heroicons-photo',              tags: 'photo image gallery media',     path: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z' },
  
    // ── Security & Protection
    { name: 'Shield Check',       class: 'i-heroicons-shield-check',       tags: 'shield security protect safe',  path: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
    { name: 'Shield Exclamation', class: 'i-heroicons-shield-exclamation', tags: 'shield warning alert security', path: 'M20.618 5.984A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016zM12 9v2m0 4h.01' },
    { name: 'Lock Closed',        class: 'i-heroicons-lock-closed',        tags: 'lock security locked password',  path: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
    { name: 'Lock Open',          class: 'i-heroicons-lock-open',          tags: 'lock unlock open access',       path: 'M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z' },
    { name: 'Finger Print',       class: 'i-heroicons-finger-print',       tags: 'fingerprint biometric access',  path: 'M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4' },
    { name: 'Key',                class: 'i-heroicons-key',                tags: 'key access lock password',      path: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z' },
    { name: 'Identification',     class: 'i-heroicons-identification',     tags: 'id card identity badge access', path: 'M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2' },
  
    // ── Networking & Connectivity
    { name: 'WiFi',               class: 'i-heroicons-wifi',               tags: 'wifi wireless network internet', path: 'M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.906 14.142 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0' },
    { name: 'Globe (Network)',    class: 'i-heroicons-globe-alt',          tags: 'globe internet network world',   path: 'M12 2a10 10 0 100 20 10 10 0 000-20zm0 0c2.21 0 4 4.477 4 10s-1.79 10-4 10-4-4.477-4-10 1.79-10 4-10zM2 12h20' },
    { name: 'Globe Americas',     class: 'i-heroicons-globe-americas',     tags: 'globe world internet map',      path: 'M12 21a9 9 0 110-18 9 9 0 010 18zm0-18c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9-4.03-9-9-9zM9 10c.55 0 1 .45 1 1v.5a.5.5 0 00.5.5h3a.5.5 0 00.5-.5v-2c0-.55-.45-1-1-1H9z' },
    { name: 'Link / Cable',       class: 'i-heroicons-link',               tags: 'link cable connect url',        path: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1' },
    { name: 'Signal',             class: 'i-heroicons-signal',             tags: 'signal network bars cellular',  path: 'M5 18h2v-6H5v6zm4 0h2V9H9v9zm4 0h2v-3h-2v3zm4 0h2V6h-2v12z' },
    { name: 'Signal Slash',       class: 'i-heroicons-signal-slash',       tags: 'no signal offline disconnect',  path: 'M3 3l18 18M8.59 8.59A3 3 0 005 11v.5M12 3c4.97 0 9 4.03 9 9 0 1.33-.29 2.6-.81 3.74M12 3C9.24 3 6.8 4.3 5.22 6.34' },
    { name: 'Rss Feed',           class: 'i-heroicons-rss',                tags: 'rss feed broadcast network',    path: 'M6 5c7.18 0 13 5.82 13 13M6 11a7 7 0 017 7m-6 0a1 1 0 11-2 0 1 1 0 012 0z' },
  
    // ── Hardware & Devices
    { name: 'Server / NVR',       class: 'i-heroicons-server',             tags: 'server nvr hardware rack',      path: 'M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01' },
    { name: 'Hard Drive',         class: 'i-heroicons-circle-stack',       tags: 'storage hard drive disk hdd',   path: 'M4 6a8 3 0 1116 0 8 3 0 01-16 0zm0 6a8 3 0 1116 0 8 3 0 01-16 0zm0 6a8 3 0 1116 0 8 3 0 01-16 0z' },
    { name: 'Computer Desktop',   class: 'i-heroicons-computer-desktop',   tags: 'desktop computer monitor pc',   path: 'M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25A2.25 2.25 0 015.25 3h13.5A2.25 2.25 0 0121 5.25z' },
    { name: 'Device Phone',       class: 'i-heroicons-device-phone-mobile', tags: 'phone mobile smartphone device', path: 'M10.5 1.5H8.25A2.25 2.25 0 006 3.75v16.5a2.25 2.25 0 002.25 2.25h7.5A2.25 2.25 0 0018 20.25V3.75a2.25 2.25 0 00-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18h3' },
    { name: 'Device Tablet',      class: 'i-heroicons-device-tablet',      tags: 'tablet ipad device screen',     path: 'M10.5 19.5h3m-6.75 2.25h10.5a2.25 2.25 0 002.25-2.25v-15a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 4.5v15a2.25 2.25 0 002.25 2.25z' },
    { name: 'Cpu Chip',           class: 'i-heroicons-cpu-chip',           tags: 'cpu chip processor hardware',   path: 'M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z' },
    { name: 'Power',              class: 'i-heroicons-power',              tags: 'power on off energy switch',    path: 'M5.636 5.636a9 9 0 1012.728 0M12 3v9' },
    { name: 'Bolt / Lightning',   class: 'i-heroicons-bolt',               tags: 'bolt lightning power flash',    path: 'M11.983 1.945a.75.75 0 011.384.602l-1.316 4.612h3.449a.75.75 0 01.564 1.255l-7.5 8.5a.75.75 0 01-1.285-.707l1.5-5.5H6.75a.75.75 0 01-.57-1.24l5.803-7.522z' },
    { name: 'Battery 100',        class: 'i-heroicons-battery-100',        tags: 'battery power energy full',     path: 'M4.5 6.375a4.125 4.125 0 118.25 0 4.125 4.125 0 01-8.25 0zM14.25 8.625a3.375 3.375 0 116.75 0 3.375 3.375 0 01-6.75 0zM1.5 19.125a7.125 7.125 0 0114.25 0v.003l-.001.119a.75.75 0 01-.363.63 13.067 13.067 0 01-6.761 1.873c-2.472 0-4.786-.684-6.76-1.873a.75.75 0 01-.364-.63l-.001-.122zM17.25 19.128l-.001.144a2.25 2.25 0 01-.233.96 10.088 10.088 0 005.06-1.01.75.75 0 00.42-.643 4.875 4.875 0 00-6.957-4.611 8.586 8.586 0 011.71 5.157v.003z' },
  
    // ── Smart Home & Automation
    { name: 'Home',               class: 'i-heroicons-home',               tags: 'home house building smart',     path: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { name: 'Home Modern',        class: 'i-heroicons-home-modern',        tags: 'home building modern residence', path: 'M8.25 21v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21m0 0h4.5V3.545M12.75 21h7.5V10.75M2.25 21h1.5m18 0h-18M2.25 9l4.5-1.636M18.75 3l-1.5.545m0 6.205l3 1m1.5.5l-1.5-.5M6.75 7.364V3h-3v18m3-13.636l10.5-3.819' },
    { name: 'Light Bulb',         class: 'i-heroicons-light-bulb',         tags: 'light bulb lamp smart home',    path: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
    { name: 'Speaker Wave',       class: 'i-heroicons-speaker-wave',       tags: 'speaker audio alarm siren',     path: 'M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z' },
    { name: 'Bell Alert',         class: 'i-heroicons-bell-alert',         tags: 'bell alarm alert notification', path: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
    { name: 'Bell',               class: 'i-heroicons-bell',               tags: 'bell notification alert ring',  path: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
    { name: 'Fire',               class: 'i-heroicons-fire',               tags: 'fire heat alarm sensor smoke',  path: 'M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z' },
    { name: 'Sun',                class: 'i-heroicons-sun',                tags: 'sun light outdoor weather',     path: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z' },
    { name: 'Moon',               class: 'i-heroicons-moon',               tags: 'moon night dark mode time',     path: 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z' },
  
    // ── Tools & Configuration
    { name: 'Wrench / Screwdriver', class: 'i-heroicons-wrench-screwdriver', tags: 'wrench tool repair maintenance', path: 'M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z' },
    { name: 'Cog / Settings',    class: 'i-heroicons-cog-6-tooth',        tags: 'settings config gear cog setup', path: 'M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
    { name: 'Adjustments',       class: 'i-heroicons-adjustments-horizontal', tags: 'adjust settings filter config', path: 'M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75' },
  
    // ── Data & Monitoring
    { name: 'Chart Bar',          class: 'i-heroicons-chart-bar',          tags: 'chart graph analytics data stats', path: 'M3 3v18h18M9 17V9m4 8V5m4 12v-3' },
    { name: 'Chart Line',         class: 'i-heroicons-chart-bar-square',   tags: 'chart line monitor analytics',  path: 'M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z' },
    { name: 'Presentation',       class: 'i-heroicons-presentation-chart-bar', tags: 'chart presentation monitor report', path: 'M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6' },
    { name: 'Clipboard List',     class: 'i-heroicons-clipboard-document-list', tags: 'clipboard list report document', path: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
    { name: 'Inbox Stack',        class: 'i-heroicons-inbox-stack',         tags: 'inbox archive storage list',    path: 'M7.875 14.25l1.214 1.942a2.25 2.25 0 001.908 1.058h2.006c.776 0 1.497-.4 1.908-1.058l1.214-1.942M2.41 9h4.636a2.25 2.25 0 011.872 1.002l.164.246a2.25 2.25 0 001.872 1.002h2.092a2.25 2.25 0 001.872-1.002l.164-.246A2.25 2.25 0 0116.954 9h4.636M2.41 9a2.25 2.25 0 00-.16.832V12a2.25 2.25 0 002.25 2.25h15a2.25 2.25 0 002.25-2.25V9.832c0-.287-.055-.57-.16-.832M2.41 9a2.25 2.25 0 01.382-.632l3.285-3.832a2.25 2.25 0 011.708-.786h8.43c.657 0 1.281.287 1.709.786l3.284 3.832c.163.19.291.404.382.632M4.5 20.25h15A2.25 2.25 0 0021.75 18v-2.625c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125V18a2.25 2.25 0 002.25 2.25z' },
  
    // ── People & Access
    { name: 'User Circle',        class: 'i-heroicons-user-circle',        tags: 'user person profile account',   path: 'M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z' },
    { name: 'Users',              class: 'i-heroicons-users',              tags: 'users team group people access', path: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z' },
    { name: 'User Group',         class: 'i-heroicons-user-group',         tags: 'group team access management',  path: 'M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z' },
  
    // ── Location & Area
    { name: 'Map Pin',            class: 'i-heroicons-map-pin',            tags: 'location map pin place area',   path: 'M15 10.5a3 3 0 11-6 0 3 3 0 016 0zM19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z' },
    { name: 'Map',                class: 'i-heroicons-map',                tags: 'map area location zone outdoor', path: 'M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z' },
    { name: 'Building',           class: 'i-heroicons-building-office',    tags: 'building office commercial area', path: 'M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3.75h.008v.008h-.008v-.008zm0 3h.008v.008h-.008v-.008zm0 3h.008v.008h-.008v-.008z' },
    { name: 'Building 2',         class: 'i-heroicons-building-storefront', tags: 'store shop building retail',    path: 'M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z' },
  
    // ── Vehicles & Outdoor
    { name: 'Truck',              class: 'i-heroicons-truck',              tags: 'truck vehicle transport outdoor', path: 'M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12' },
    { name: 'Car',                class: 'i-heroicons-car',               tags: 'car vehicle parking outdoor',    path: 'M 3 10 L 5.5 4 L 18.5 4 L 21 10 M 3 10 L 3 18 L 5 18 L 5 20 L 7 20 L 7 18 L 17 18 L 17 20 L 19 20 L 19 18 L 21 18 L 21 10 Z M 6.5 10 L 17.5 10 M 6 14 A 1 1 0 1 0 8 14 A 1 1 0 1 0 6 14 M 16 14 A 1 1 0 1 0 18 14 A 1 1 0 1 0 16 14' },
  
    // ── Misc Useful
    { name: 'Tag',                class: 'i-heroicons-tag',                tags: 'tag label category product',    path: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a4 4 0 014-4z' },
    { name: 'Archive',            class: 'i-heroicons-archive-box',        tags: 'archive storage box package',   path: 'M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z' },
    { name: 'Cube',               class: 'i-heroicons-cube',               tags: 'cube box 3d product hardware',  path: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' },
    { name: 'Cube Transparent',   class: 'i-heroicons-cube-transparent',   tags: 'cube transparent open package',  path: 'M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9' },
    { name: 'Shopping Cart',      class: 'i-heroicons-shopping-cart',      tags: 'cart shop buy product retail',  path: 'M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z' },
    { name: 'Gift',               class: 'i-heroicons-gift',               tags: 'gift promo discount package',   path: 'M12 8.25v-1.5m0 1.5c-1.355 0-2.697.056-4.024.166C6.845 8.51 6 9.473 6 10.608v2.513m6-4.87c1.355 0 2.697.055 4.024.165C17.155 8.51 18 9.473 18 10.608v2.513m-3-4.87v-1.5m-6 1.5v-1.5m12 9.75l-1.5.75a3.354 3.354 0 01-3 0 3.354 3.354 0 00-3 0 3.354 3.354 0 01-3 0 3.354 3.354 0 00-3 0 3.354 3.354 0 01-3 0L3 16.5m15-3.38a48.474 48.474 0 00-6-.37c-2.032 0-4.034.125-6 .37m12 0c.39.049.777.102 1.163.16 1.07.16 1.837 1.094 1.837 2.175v5.17c0 .62-.504 1.124-1.125 1.124H4.125A1.125 1.125 0 013 20.625v-5.17c0-1.08.768-2.014 1.837-2.174A47.78 47.78 0 016 13.12M12.265 3.11a.375.375 0 11-.53 0L12 2.845l.265.265zm-3 0a.375.375 0 11-.53 0L9 2.845l.265.265zm6 0a.375.375 0 11-.53 0L15 2.845l.265.265z' },
    { name: 'QR Code',            class: 'i-heroicons-qr-code',            tags: 'qr code scan barcode product',  path: 'M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 013.75 9.375v-4.5zM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5a1.125 1.125 0 01-1.125-1.125v-4.5zM13.5 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0113.5 9.375v-4.5z M6.75 6.75h.75v.75h-.75v-.75zM6.75 16.5h.75v.75h-.75v-.75zM16.5 6.75h.75v.75h-.75v-.75zM13.5 13.5h.75v.75h-.75v-.75zM13.5 19.5h.75v.75h-.75v-.75zM19.5 13.5h.75v.75h-.75v-.75zM19.5 19.5h.75v.75h-.75v-.75zM16.5 16.5h.75v.75h-.75v-.75z' },
    { name: 'Megaphone',          class: 'i-heroicons-megaphone',          tags: 'megaphone promo broadcast public', path: 'M10.34 15.84c-.196-.msg.3-.412.3-.67V11m0 4.84l-3.346 3.634a1 1 0 01-1.53-.094A1 1 0 015.5 19V4a1 1 0 01.5-.866l12 7A1 1 0 0118 11m0 0l-7.66 4.84M18 11l-7.66-4.84' },
    { name: 'Cursor Arrow',       class: 'i-heroicons-cursor-arrow-rays',  tags: 'cursor click interact ui',      path: 'M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zM12 2.25V4.5m5.834.166l-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243l-1.59-1.59' },
    { name: 'Squares Plus',       class: 'i-heroicons-squares-plus',       tags: 'add new category section grid', path: 'M13.5 16.875h3.375m0 0h3.375m-3.375 0V13.5m0 3.375v3.375M6 10.5h2.25a2.25 2.25 0 002.25-2.25V6a2.25 2.25 0 00-2.25-2.25H6A2.25 2.25 0 003.75 6v2.25A2.25 2.25 0 006 10.5zm0 9.75h2.25A2.25 2.25 0 0010.5 18v-2.25a2.25 2.25 0 00-2.25-2.25H6a2.25 2.25 0 00-2.25 2.25V18A2.25 2.25 0 006 20.25zm9.75-9.75H18a2.25 2.25 0 002.25-2.25V6A2.25 2.25 0 0018 3.75h-2.25A2.25 2.25 0 0013.5 6v2.25a2.25 2.25 0 002.25 2.25z' },
    { name: 'Rectangle Stack',    class: 'i-heroicons-rectangle-stack',    tags: 'stack layers category list',    path: 'M6 6.878V6a2.25 2.25 0 012.25-2.25h7.5A2.25 2.25 0 0118 6v.878m-12 0c.235-.083.487-.128.75-.128h10.5c.263 0 .515.045.75.128m-12 0A2.25 2.25 0 004.5 9v.878m13.5-3A2.25 2.25 0 0119.5 9v.878m0 0a2.246 2.246 0 00-.75-.128H5.25c-.263 0-.515.045-.75.128m15 0A2.25 2.25 0 0121 12v6a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18v-6c0-.98.626-1.813 1.5-2.122' },
    { name: 'Bookmark',           class: 'i-heroicons-bookmark',           tags: 'bookmark save favorite label',  path: 'M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z' },
    { name: 'Hashtag',            class: 'i-heroicons-hashtag',            tags: 'hashtag tag label category',    path: 'M5.25 8.25h15m-16.5 7.5h15m-1.8-13.5l-3.9 19.5m-2.1-19.5l-3.9 19.5' },
    { name: 'Funnel / Filter',    class: 'i-heroicons-funnel',             tags: 'filter funnel sort category',   path: 'M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z' },
    { name: 'Swatch',             class: 'i-heroicons-swatch',             tags: 'swatch color design palette',   path: 'M4.098 19.902a3.75 3.75 0 005.304 0l6.401-6.402M6.75 21A3.75 3.75 0 013 17.25V4.125C3 3.504 3.504 3 4.125 3h5.25c.621 0 1.125.504 1.125 1.125v4.072M6.75 21a3.75 3.75 0 003.75-3.75V8.197M6.75 21h13.125c.621 0 1.125-.504 1.125-1.125v-5.25c0-.621-.504-1.125-1.125-1.125h-4.072M10.5 8.197l2.88-2.88c.438-.439 1.15-.439 1.59 0l3.712 3.713c.44.44.44 1.152 0 1.59l-2.879 2.88M6.75 17.25h.008v.008H6.75v-.008z' },
  ]
  
  const filteredIcons = computed(() => {
    if (!iconSearch.value.trim()) return availableIcons
    const q = iconSearch.value.toLowerCase()
    return availableIcons.filter(i =>
      i.name.toLowerCase().includes(q) ||
      i.class.toLowerCase().includes(q) ||
      (i.tags && i.tags.toLowerCase().includes(q))
    )
  })
  
  const getIconPath = (iconClass) => {
    const icon = availableIcons.find(i => i.class === iconClass)
    return icon ? icon.path : null
  }
  const getIconName = (iconClass) => {
    const icon = availableIcons.find(i => i.class === iconClass)
    return icon ? icon.name : iconClass
  }
  
  // ── State ─────────────────────────────────────────────
  const categories   = ref([])
  const isLoading    = ref(true)
  const isSubmitting = ref(false)
  const showPreview  = ref(false)
  
  const showCatModal    = ref(false)
  const showSubModal    = ref(false)
  const showDeleteModal = ref(false)
  const itemToDelete    = ref(null)
  
  const expandedCategories = ref([])
  
  const catForm = reactive({ name: '', slug: '', icon_name: '', position: 1 })
  const subForm = reactive({ category_uuid: '', name: '', slug: '', position: 1 })
  
  // ── Computed: synthetic section for preview ───────────
  const previewSectionSynthetic = computed(() => ({
    uuid:       null,
    identifier: 'category-nav',
    title:      'Category Navigation',
    mode:       null,
    is_active:  true,
    items:      categories.value,
  }))
  
  // Category-specific URL presets for preview
  const categoryPresets = computed(() => {
    const presets = []
    categories.value.slice(0, 4).forEach(cat => {
      presets.push({
        label: cat.name,
        icon:  '📁',
        url:   `http://localhost:3000/category/${cat.slug}`,
      })
      if (cat.subcategories?.length) {
        presets.push({
          label: `↳ ${cat.subcategories[0].name}`,
          icon:  '📂',
          url:   `http://localhost:3000/category/${cat.slug}/${cat.subcategories[0].slug}`,
        })
      }
    })
    return presets
  })
  
  // ── Auto Slug ─────────────────────────────────────────
  const generateSlug = (text) => text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '')
  watch(() => catForm.name, (v) => { catForm.slug = generateSlug(v) })
  watch(() => subForm.name, (v) => { subForm.slug = generateSlug(v) })
  
  // ── Tree ──────────────────────────────────────────────
  const toggleExpand = (id) => {
    const i = expandedCategories.value.indexOf(id)
    i === -1 ? expandedCategories.value.push(id) : expandedCategories.value.splice(i, 1)
  }
  const isExpanded = (id) => expandedCategories.value.includes(id)
  
  // ── Fetch ─────────────────────────────────────────────
  const fetchCategories = async () => {
    isLoading.value = true
    try {
      const res = await api.get(`${API_BASE}/`)
      categories.value = res.data?.data || res.data || []
      if (categories.value.length > 0) {
        expandedCategories.value = categories.value.map(c => c.id)
      }
    } catch (e) {
      console.error(e)
      alert(e.response?.data?.detail || 'Gagal memuat data kategori.')
    } finally {
      isLoading.value = false
    }
  }
  
  // ── Modals ────────────────────────────────────────────
  const openCatModal = () => {
    catForm.name      = ''
    catForm.slug      = ''
    catForm.icon_name = 'i-heroicons-video-camera'
    catForm.position  = categories.value.length + 1
    iconSearch.value  = ''
    showCatModal.value = true
  }
  
  const openSubModal = (categoryId = null) => {
    subForm.category_uuid = categoryId || (categories.value.length > 0 ? categories.value[0].id : '')
    subForm.name          = ''
    subForm.slug          = ''
    const targetCat       = categories.value.find(c => c.id === categoryId)
    subForm.position      = targetCat?.subcategories?.length ? targetCat.subcategories.length + 1 : 1
    showSubModal.value    = true
  }
  
  const openPreview = () => { showPreview.value = true }
  
  const closeModals = () => {
    if (isSubmitting.value) return
    showCatModal.value = false
    showSubModal.value = false
  }
  
  // ── CRUD ──────────────────────────────────────────────
  const saveCategory = async () => {
    isSubmitting.value = true
    const fd = new FormData()
    fd.append('name', catForm.name)
    fd.append('slug', catForm.slug)
    if (catForm.icon_name) fd.append('icon_name', catForm.icon_name)
    fd.append('position', catForm.position)
    try {
      await api.post(`${API_BASE}/admin/category`, fd)
      await fetchCategories()
      closeModals()
    } catch (e) {
      alert(e.response?.data?.detail || 'Gagal menyimpan kategori.')
    } finally { isSubmitting.value = false }
  }
  
  const saveSubcategory = async () => {
    if (!subForm.category_uuid) { alert('Harap pilih kategori utama.'); return }
    isSubmitting.value = true
    const fd = new FormData()
    fd.append('category_uuid', subForm.category_uuid)
    fd.append('name', subForm.name)
    fd.append('slug', subForm.slug)
    fd.append('position', subForm.position)
    try {
      await api.post(`${API_BASE}/admin/subcategory`, fd)
      await fetchCategories()
      closeModals()
      if (!isExpanded(subForm.category_uuid)) toggleExpand(subForm.category_uuid)
    } catch (e) {
      alert(e.response?.data?.detail || 'Gagal menyimpan subkategori.')
    } finally { isSubmitting.value = false }
  }
  
  const confirmDelete = (id) => { itemToDelete.value = id; showDeleteModal.value = true }
  
  const deleteCategory = async () => {
    if (!itemToDelete.value) return
    isSubmitting.value = true
    try {
      await api.delete(`${API_BASE}/admin/category/${itemToDelete.value}`)
      await fetchCategories()
      showDeleteModal.value = false
    } catch (e) {
      alert(e.response?.data?.detail || 'Gagal menghapus kategori.')
    } finally { isSubmitting.value = false; itemToDelete.value = null }
  }
  
  onMounted(() => fetchCategories())
  </script>
  
  <style scoped>
  .custom-scrollbar::-webkit-scrollbar { width: 5px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 10px; }
  .custom-scrollbar:hover::-webkit-scrollbar-thumb { background-color: #d1d5db; }
  </style>