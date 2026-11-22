<template>
  <div class="min-h-screen bg-[#F7F8FC] font-sans">
    <!-- ── Header ─────────────────────────────── -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
      <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Konfigurasi Pricing Jasa</h1>
            <p class="text-xs text-gray-400 mt-0.5">PasarCCTV, Admin Panel</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button @click="showPreview = true"
            class="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 active:scale-95 transition-all shadow-sm">
            <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Live Preview
          </button>
          <button @click="openCreate"
            class="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 active:scale-95 transition-all shadow-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Buat Versi Baru
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-screen-2xl mx-auto px-6 py-6 space-y-6">
      <!-- ── Stats Cards ─────────────────────── -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-400 uppercase tracking-wide">Total Versi</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">{{ configs.length }}</p>
            </div>
            <div class="w-9 h-9 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-400 uppercase tracking-wide">Versi Aktif</p>
              <p class="text-2xl font-bold text-emerald-600 mt-1" v-if="activeConfig">
                {{ activeConfig.uuid.substring(0, 8) }}...
              </p>
              <p class="text-2xl font-bold text-red-500 mt-1" v-else>Tidak Ada</p>
            </div>
            <div class="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-400 uppercase tracking-wide">Terakhir Diperbarui</p>
              <p class="text-2xl font-bold text-gray-900 mt-1" v-if="configs.length">
                {{ formatDate(configs[0].created_at) }}
              </p>
              <p class="text-2xl font-bold text-gray-300 mt-1" v-else>-</p>
            </div>
            <div class="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Table ──────────────────────────── -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-24">
          <div class="flex flex-col items-center gap-3">
            <div class="w-10 h-10 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
            <p class="text-sm text-gray-400 font-medium">Memuat data...</p>
          </div>
        </div>

        <div v-else-if="!configs.length" class="flex flex-col items-center justify-center py-24 gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center text-gray-300">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-sm font-semibold text-gray-600">Belum ada konfigurasi pricing</p>
          <button @click="openCreate" class="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
            + Buat Konfigurasi Pertama
          </button>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50/80">
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Info Versi</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Dasar Jasa</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Transport</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">DP %</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                <th class="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="cfg in configs" :key="cfg.uuid"
                class="group hover:bg-indigo-50/20 transition-colors">
                
                <!-- Info Versi -->
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                      </svg>
                    </div>
                    <div>
                      <p class="font-bold text-gray-900 leading-none mb-1">{{ cfg.uuid.substring(0, 8).toUpperCase() }}</p>
                      <p class="text-xs text-gray-400">{{ formatDate(cfg.created_at) }}</p>
                    </div>
                  </div>
                </td>

                <!-- Dasar Jasa -->
                <td class="px-6 py-4">
                  <div class="space-y-1">
                    <div class="flex items-center gap-2">
                      <span class="text-[10px] font-bold text-gray-400 uppercase w-16">Instalasi:</span>
                      <span class="font-semibold text-gray-700">{{ formatPrice(getCategoryPrice(cfg, 'installation')) }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-[10px] font-bold text-gray-400 uppercase w-16">Survey:</span>
                      <span class="font-semibold text-gray-700">{{ formatPrice(cfg.consultation_fee) }}</span>
                    </div>
                  </div>
                </td>

                <!-- Transport -->
                <td class="px-6 py-4 text-center">
                  <p class="font-bold text-gray-800">{{ formatPrice(cfg.transport_per_km) }}<span class="text-gray-400 font-normal">/km</span></p>
                  <p class="text-[10px] text-gray-400 mt-0.5">Min: {{ formatPrice(cfg.transport_min_fee) }}</p>
                </td>

                <!-- DP % -->
                <td class="px-6 py-4 text-center">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700 border border-amber-100 font-bold">
                    {{ cfg.dp_percentage }}%
                  </span>
                </td>

                <!-- Status -->
                <td class="px-6 py-4 text-center">
                  <div class="flex flex-col items-center gap-1.5">
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" :checked="cfg.is_active" class="sr-only peer" @change="activateConfig(cfg)">
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                    </label>
                    <span :class="['text-[10px] font-bold uppercase tracking-wider', cfg.is_active ? 'text-indigo-600' : 'text-gray-400']">
                      {{ cfg.is_active ? 'Aktif' : 'Nonaktif' }}
                    </span>
                  </div>
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 text-center">
                  <div class="flex items-center justify-center gap-2">
                    <button @click="openEdit(cfg)"
                      class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                      title="Edit / Lihat Detail">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Live Preview Modal -->
    <ImageSectionPreview
      v-model="showPreview"
      :initial-url="previewStore.resolveUrl('/services/booking')"
      hide-mode-picker
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/service/api'
import ImageSectionPreview from '@/components/ImageSectionPreview.vue'
import { usePreviewStore } from '@/stores/previewStore'

const previewStore = usePreviewStore()

interface CategoryConfig {
  id: string
  base_price: number
  label: string
}

interface PricingConfig {
  uuid: string
  is_active: boolean
  created_at: string
  consultation_fee: number
  transport_per_km: number
  transport_min_fee: number
  transport_max_fee: number
  dp_percentage: number
  categories: CategoryConfig[]
}

const router = useRouter()
const configs = ref<PricingConfig[]>([])
const loading = ref(true)
const showPreview = ref(false)

const activeConfig = computed(() => configs.value.find(c => c.is_active))

const formatDate = (iso: string) => {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(price)
}

const getCategoryPrice = (cfg: PricingConfig, categoryId: string) => {
  const cat = cfg.categories?.find(c => c.id === categoryId)
  return cat ? cat.base_price : 0
}

const fetchConfigs = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/admin/service/pricing/all')
    configs.value = data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  } catch (error) {
    console.error('Gagal mengambil data:', error)
  } finally {
    loading.value = false
  }
}

const activateConfig = async (cfg: PricingConfig) => {
  const prevConfigs = [...configs.value]
  configs.value = configs.value.map(c => ({
    ...c,
    is_active: c.uuid === cfg.uuid
  }))

  try {
    await api.post('/admin/service/pricing/activate', { uuid: cfg.uuid })
    await fetchConfigs()
  } catch (error) {
    console.error('Gagal mengaktifkan konfigurasi:', error)
    configs.value = prevConfigs
  }
}

const openEdit = (cfg: PricingConfig) => {
  router.push({ 
    name: 'jasa-configurasi', 
    query: { uuid: cfg.uuid } 
  })
}

const openCreate = () => {
  router.push({ name: 'jasa-configurasi' })
}

onMounted(fetchConfigs)
</script>

<style scoped>
/* Transisi sudah dihandle di komponen Imagesectionpreview */
</style>
