<template>
  <div class="min-h-screen bg-[#F7F8FC] font-sans text-gray-800">

    <!-- ── Header ─────────────────────────────── -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
      <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Pengaturan Link Preview</h1>
            <p class="text-xs text-gray-400 mt-0.5">Atur target URL untuk tombol preview dan live preview banner</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <a
            :href="urlInput"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 active:scale-95 transition-all shadow-sm"
          >
            <svg class="w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Buka di Tab Baru
          </a>
          <button
            @click="save"
            class="flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-100 cursor-pointer border-none"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Simpan Perubahan
          </button>
        </div>
      </div>
    </div>

    <!-- ── Content ────────────────────────────── -->
    <div class="max-w-screen-2xl mx-auto px-6 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

        <!-- Left: Form Settings -->
        <div class="lg:col-span-1 space-y-6">
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h3 class="text-sm font-bold text-gray-900">Konfigurasi Target URL</h3>
            </div>

            <div class="p-6 space-y-5">
              <div class="space-y-2">
                <label class="text-xs font-bold text-gray-500 uppercase tracking-wider block">URL Preview Website</label>
                <input
                  v-model="urlInput"
                  type="url"
                  placeholder="https://..."
                  class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none"
                  @keydown.enter="save"
                />
                <p class="text-[11px] text-gray-400">
                  URL ini akan dipakai sebagai tujuan tombol preview di navbar dan dasar embed live preview komponen.
                </p>
              </div>

              <!-- Quick Presets -->
              <div class="space-y-2 pt-2 border-t border-gray-100">
                <span class="text-xs font-semibold text-gray-500 block">Pilihan Cepat (Preset):</span>
                <div class="flex flex-col gap-2">
                  <button
                    type="button"
                    @click="setPreset('https://marketplace-pi-sable.vercel.app/login')"
                    class="text-left px-3 py-2 rounded-xl text-xs border transition-all flex items-center justify-between"
                    :class="urlInput === 'https://marketplace-pi-sable.vercel.app/login' ? 'border-indigo-500 bg-indigo-50 text-indigo-700 font-semibold' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'"
                  >
                    <span class="truncate">Vercel Login (Default)</span>
                    <span class="text-[10px] text-gray-400 shrink-0 ml-2">marketplace-pi-sable</span>
                  </button>
                  <button
                    type="button"
                    @click="setPreset('https://marketplace-pi-sable.vercel.app')"
                    class="text-left px-3 py-2 rounded-xl text-xs border transition-all flex items-center justify-between"
                    :class="urlInput === 'https://marketplace-pi-sable.vercel.app' ? 'border-indigo-500 bg-indigo-50 text-indigo-700 font-semibold' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'"
                  >
                    <span class="truncate">Vercel Storefront</span>
                    <span class="text-[10px] text-gray-400 shrink-0 ml-2">Home</span>
                  </button>
                  <button
                    type="button"
                    @click="setPreset('http://localhost:3000')"
                    class="text-left px-3 py-2 rounded-xl text-xs border transition-all flex items-center justify-between"
                    :class="urlInput === 'http://localhost:3000' ? 'border-indigo-500 bg-indigo-50 text-indigo-700 font-semibold' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'"
                  >
                    <span class="truncate">Local Development</span>
                    <span class="text-[10px] text-gray-400 shrink-0 ml-2">localhost:3000</span>
                  </button>
                </div>
              </div>

              <!-- Reset to Default Button -->
              <div class="pt-2">
                <button
                  type="button"
                  @click="resetDefault"
                  class="w-full py-2 px-3 text-xs font-semibold text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all"
                >
                  Kembalikan ke Default
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Live Frame -->
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden flex flex-col h-[700px]">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="flex gap-1.5">
                  <span class="w-3 h-3 rounded-full bg-rose-400 inline-block"></span>
                  <span class="w-3 h-3 rounded-full bg-amber-400 inline-block"></span>
                  <span class="w-3 h-3 rounded-full bg-emerald-400 inline-block"></span>
                </div>
                <span class="text-xs font-mono text-gray-500 truncate max-w-md ml-2">{{ activePreviewUrl }}</span>
              </div>
              <button
                @click="reloadIframe"
                class="p-1.5 text-gray-400 hover:text-indigo-600 rounded-lg hover:bg-white transition-all"
                title="Reload Preview"
              >
                <svg class="w-4 h-4" :class="{ 'animate-spin': isReloading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
            <div class="flex-1 bg-gray-100 relative">
              <iframe
                :key="iframeKey"
                :src="activePreviewUrl"
                class="w-full h-full border-0"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
              ></iframe>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePreviewStore, DEFAULT_PREVIEW_URL } from '@/stores/previewStore'
import { useToastStore } from '@/stores/toast'

const previewStore = usePreviewStore()
const toast = useToastStore()

const urlInput = ref(previewStore.previewUrl)
const activePreviewUrl = computed(() => urlInput.value || DEFAULT_PREVIEW_URL)
const iframeKey = ref(0)
const isReloading = ref(false)

const setPreset = (url) => {
  urlInput.value = url
}

const resetDefault = () => {
  urlInput.value = DEFAULT_PREVIEW_URL
  previewStore.resetToDefault()
  iframeKey.value++
  toast.info('URL dikembalikan ke default')
}

const save = () => {
  if (!urlInput.value.trim()) {
    toast.error('URL preview tidak boleh kosong')
    return
  }
  previewStore.setPreviewUrl(urlInput.value)
  iframeKey.value++
  toast.success('Link preview berhasil disimpan!')
}

const reloadIframe = () => {
  isReloading.value = true
  iframeKey.value++
  setTimeout(() => {
    isReloading.value = false
  }, 600)
}
</script>
