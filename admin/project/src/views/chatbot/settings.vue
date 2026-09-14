<template>
  <div class="h-full max-w-4xl mx-auto flex flex-col font-sans text-gray-800">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold tracking-tight text-gray-900">AI & Chatbot Settings</h1>
      <p class="mt-1 text-sm text-gray-500">Konfigurasikan sistem hybrid AI PasarBot. Hubungkan API provider LLM luar atau gunakan pencarian lokal (Internal RAG) gratis.</p>
    </div>



    <!-- Main Config Card -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 md:p-8 mb-12">
      <form @submit.prevent="saveSettings" class="space-y-6">
        
        <!-- Hybrid Switcher (Provider) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start pb-6 border-b border-gray-100">
          <div>
            <h3 class="font-semibold text-gray-900 text-sm">AI Engine Provider</h3>
            <p class="text-xs text-gray-500 mt-1">Pilih motor kecerdasan buatan utama yang menggerakkan PasarBot.</p>
          </div>
          <div class="md:col-span-2">
            <select 
              v-model="form.provider" 
              class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all font-medium"
              @change="onProviderChange"
            >
              <option value="internal">Sistem Internal (Lokal & Gratis • Tanpa LLM)</option>
              <option value="groq">Groq AI (Qwen/Llama - Cepat & Ekonomis)</option>
              <option value="openai">OpenAI (GPT-4o / GPT-4o-mini)</option>
              <option value="gemini">Google Gemini (Gemini-1.5 / Gemini-2.0)</option>
              <option value="deepseek">DeepSeek AI (Fuzzy & Reasoning Cerdas)</option>
            </select>

            <div class="mt-3 p-3 bg-gray-50 border border-gray-100 rounded-xl text-xs text-gray-600 flex items-start gap-2">
              <svg class="w-4 h-4 shrink-0 text-indigo-500 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span v-if="form.provider === 'internal'">
                <strong>Sistem Internal RAG:</strong> PasarBot akan menjawab murni berdasarkan FAQ lokal yang ditambahkan admin dan relasi produk terdekat di database (Manticore Search). Tanpa biaya API eksternal dan response time instan.
              </span>
              <span v-else>
                <strong>Hybrid LLM Agent:</strong> PasarBot akan mengombinasikan pencarian database produk kita lalu mengirimkannya sebagai konteks ke model LLM pilihan Anda ({{ form.provider.toUpperCase() }}) untuk menyusun jawaban rekomendasi yang luwes dan cerdas.
              </span>
            </div>
          </div>
        </div>

        <template v-if="form.provider !== 'internal'">
          <!-- API Key -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start pb-6 border-b border-gray-100">
            <div>
              <h3 class="font-semibold text-gray-900 text-sm">API Key Credentials</h3>
              <p class="text-xs text-gray-500 mt-1">Kunci autentikasi untuk memanggil API endpoint {{ form.provider.toUpperCase() }}.</p>
            </div>
            <div class="md:col-span-2">
              <div class="relative">
                <input 
                  v-model="form.api_key" 
                  :type="showApiKey ? 'text' : 'password'" 
                  required
                  placeholder="Masukkan Kunci API Anda..." 
                  class="block w-full pl-4 pr-12 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 font-mono focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                />
                <button 
                  type="button"
                  @click="showApiKey = !showApiKey"
                  class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
                >
                  <svg v-if="showApiKey" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Model Name Selector -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start pb-6 border-b border-gray-100">
            <div>
              <h3 class="font-semibold text-gray-900 text-sm">Model Name</h3>
              <p class="text-xs text-gray-500 mt-1">Pilih spesifik model AI yang digunakan untuk generating teks.</p>
            </div>
            <div class="md:col-span-2 space-y-3">
              <select 
                v-model="selectedModelPreset" 
                class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                @change="onModelPresetChange"
              >
                <option v-for="m in modelOptions" :key="m.value" :value="m.value">
                  {{ m.label }}
                </option>
                <option value="custom">Model Kustom (Tulis Nama Model Sendiri)</option>
              </select>

              <input 
                v-if="selectedModelPreset === 'custom'"
                v-model="form.model" 
                type="text" 
                required
                placeholder="Tuliskan nama model lengkap (misal: gpt-4-turbo)..." 
                class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all font-mono"
              />
            </div>
          </div>

          <!-- Temperature & Max Tokens -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start pb-6 border-b border-gray-100">
            <div>
              <h3 class="font-semibold text-gray-900 text-sm">Parameters</h3>
              <p class="text-xs text-gray-500 mt-1">Mengontrol tingkat kreativitas dan panjang respons AI.</p>
            </div>
            <div class="md:col-span-2 space-y-5">
              <div>
                <div class="flex items-center justify-between text-xs text-gray-600 font-semibold mb-1.5">
                  <span>Temperature (Kreativitas): {{ form.temperature }}</span>
                  <span class="text-gray-400">0.0 (Kaku/Faktual) — 1.0 (Kreatif)</span>
                </div>
                <input 
                  v-model.number="form.temperature" 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="0.1"
                  class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Max Completion Tokens (Panjang maksimum jawaban)</label>
                <input 
                  v-model.number="form.max_tokens" 
                  type="number" 
                  min="128" 
                  max="8192"
                  required
                  class="block w-40 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all font-mono"
                />
              </div>
            </div>
          </div>

          <!-- Custom System Prompt -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start pb-6">
            <div>
              <h3 class="font-semibold text-gray-900 text-sm">Custom System Prompt</h3>
              <p class="text-xs text-gray-500 mt-1">Aturan dasar dan karakter kepribadian yang memandu bot saat merespons percakapan.</p>
            </div>
            <div class="md:col-span-2">
              <textarea 
                v-model="form.custom_system_prompt" 
                rows="10"
                placeholder="Tuliskan instruksi sistem lengkap..." 
                class="block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all resize-none font-mono"
              ></textarea>
              <div class="mt-2 text-[10px] text-gray-400 leading-normal">
                Gunakan variabel placeholder <code class="bg-gray-100 px-1 rounded text-gray-600">{products_context}</code> untuk menyisipkan data produk catalog terdekat, dan <code class="bg-gray-100 px-1 rounded text-gray-600">{graph_context}</code> untuk data relasi spesifikasi.
              </div>
            </div>
          </div>
        </template>

        <!-- Save Button Section -->
        <div class="pt-6 border-t border-gray-100 flex items-center justify-end">
          <button 
            type="submit" 
            :disabled="isSubmitting"
            class="px-6 py-3 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500/50 active:scale-95 disabled:opacity-75 disabled:cursor-not-allowed transition-all flex items-center justify-center min-w-[140px] shadow-md shadow-indigo-600/10"
          >
            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isSubmitting ? 'Menyimpan...' : 'Simpan Pengaturan' }}
          </button>
        </div>

      </form>
    </div>

    <!-- Toast Notification -->
    <Transition name="toast">
      <div v-if="toast.show" :class="[
        'fixed bottom-6 right-6 z-[10000] flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-xl text-sm font-semibold transition-all border font-sans',
        toast.type === 'success' ? 'bg-gray-900 border-gray-800 text-white' : 'bg-red-50 border-red-200 text-red-700'
      ]">
        <div :class="['w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold', toast.type === 'success' ? 'bg-indigo-500 text-white' : 'bg-red-200 text-red-700']">
          {{ toast.type === 'success' ? '✓' : '✕' }}
        </div>
        <span>{{ toast.message }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/service/api'

// Form State
const form = reactive({
  provider: 'groq',
  api_key: '',
  model: '',
  temperature: 0.6,
  max_tokens: 4096,
  custom_system_prompt: ''
})

const isLoading = ref(true)
const isSubmitting = ref(false)
const showApiKey = ref(false)
const selectedModelPreset = ref('')

// Toast State
const toast = reactive({ show: false, message: '', type: 'success' })
let toastTimer = null
const showToast = (message, type = 'success') => {
  clearTimeout(toastTimer)
  toast.message = message
  toast.type = type
  toast.show = true
  toastTimer = setTimeout(() => {
    toast.show = false
  }, 4000)
}

// Model choices maps based on provider
const providerModels = {
  groq: [
    { label: 'Qwen 2.5 32B (Direkomendasikan)', value: 'qwen-2.5-32b' },
    { label: 'Llama 3.3 70B (Sangat Akurat)', value: 'llama-3.3-70b-versatile' },
    { label: 'Mixtral 8x7B (Luwes & Cepat)', value: 'mixtral-8x7b-32768' }
  ],
  openai: [
    { label: 'GPT-4o Mini (Cepat & Ekonomis)', value: 'gpt-4o-mini' },
    { label: 'GPT-4o (Kemampuan Penalaran Tinggi)', value: 'gpt-4o' }
  ],
  gemini: [
    { label: 'Gemini 1.5 Flash (Cepat & Akurat)', value: 'gemini-1.5-flash' },
    { label: 'Gemini 1.5 Pro (Penalaran Kompleks)', value: 'gemini-1.5-pro' },
    { label: 'Gemini 2.0 Flash (Model Terbaru)', value: 'gemini-2.0-flash' }
  ],
  deepseek: [
    { label: 'DeepSeek Chat (Faktual & Hemat)', value: 'deepseek-chat' }
  ]
}

const modelOptions = computed(() => {
  return providerModels[form.provider] || []
})

// Triggered when provider changes
const onProviderChange = () => {
  if (form.provider === 'internal') {
    form.api_key = ''
    form.model = ''
    selectedModelPreset.value = ''
  } else {
    const opts = providerModels[form.provider]
    if (opts && opts.length > 0) {
      selectedModelPreset.value = opts[0].value
      form.model = opts[0].value
    } else {
      selectedModelPreset.value = 'custom'
      form.model = ''
    }
  }
}

// Preset model selection change handler
const onModelPresetChange = () => {
  if (selectedModelPreset.value !== 'custom') {
    form.model = selectedModelPreset.value
  }
}

// Load current settings from backend
const loadSettings = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/chatbot/settings')
    const data = res.data
    form.provider = data.provider
    form.api_key = data.api_key || ''
    form.model = data.model || ''
    form.temperature = data.temperature
    form.max_tokens = data.max_tokens
    form.custom_system_prompt = data.custom_system_prompt || ''

    // Determine model preset
    const options = providerModels[form.provider] || []
    const match = options.find(o => o.value === form.model)
    if (match) {
      selectedModelPreset.value = form.model
    } else if (form.provider !== 'internal') {
      selectedModelPreset.value = 'custom'
    } else {
      selectedModelPreset.value = ''
    }
  } catch (err) {
    console.error('Failed to load AI settings:', err)
  } finally {
    isLoading.value = false
  }
}

// Save Settings
const saveSettings = async () => {
  isSubmitting.value = true
  try {
    const payload = {
      provider: form.provider,
      api_key: form.provider === 'internal' ? null : form.api_key.trim(),
      model: form.provider === 'internal' ? null : form.model.trim(),
      temperature: form.temperature,
      max_tokens: form.max_tokens,
      custom_system_prompt: form.provider === 'internal' ? null : form.custom_system_prompt.trim()
    }

    await api.put('/chatbot/settings', payload)
    showToast('Pengaturan hybrid AI berhasil diperbarui!')
  } catch (err) {
    console.error('Failed to update AI settings:', err)
    showToast(err.response?.data?.detail || 'Gagal menyimpan pengaturan AI.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
/* Toast Animation */
.toast-enter-active, .toast-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}
</style>
