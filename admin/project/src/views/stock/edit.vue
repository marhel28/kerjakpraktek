<template>
    <div class="min-h-screen bg-[#F7F8FC] font-sans">

        <!-- ── Header ──────────────────────────────────────────────────────── -->
        <div class="bg-white border-b border-gray-200 sticky top-0 z-20 shadow-sm">
            <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">

                <div class="flex items-center gap-3">
                    <router-link to="/stock"
                        class="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors border border-transparent hover:border-gray-200">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                        </svg>
                    </router-link>
                    <div>
                        <h1 class="text-lg font-bold text-gray-900 leading-none">Edit Produk</h1>
                        <p class="text-xs text-gray-500 mt-1">Perbarui informasi produk</p>
                    </div>
                </div>

                <div class="flex items-center gap-3">
                    <router-link to="/stock"
                        class="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
                        Batal
                    </router-link>
                    <button @click="submitForm" :disabled="submitting || fetchingData"
                        class="flex items-center gap-2 px-5 py-2 text-sm font-bold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 disabled:opacity-60 active:scale-95 transition-all shadow-sm">
                        <div v-if="submitting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        {{ submitting ? 'Menyimpan...' : 'Perbarui Produk' }}
                    </button>
                </div>

            </div>
        </div>

        <!-- ── Body / Form Area ────────────────────────────────────────────── -->
        <div class="max-w-4xl mx-auto px-6 py-8">

            <!-- Loading State -->
            <div v-if="fetchingData" class="flex flex-col items-center justify-center py-32 gap-3">
                <div class="w-10 h-10 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                <p class="text-sm text-gray-500">Mengambil data produk...</p>
            </div>

            <div v-else class="space-y-6">

                <!-- 1. Informasi Dasar -->
                <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                        <h2 class="text-sm font-bold text-gray-800">Informasi Dasar</h2>
                    </div>
                    <div class="p-6 space-y-5">
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1.5">
                                Nama Produk <span class="text-red-500">*</span>
                            </label>
                            <input v-model="form.title" type="text"
                                placeholder="Contoh: Kamera CCTV Ezviz C6N 2MP"
                                :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all',
                                    errors.title ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']" />
                            <p v-if="errors.title" class="text-xs text-red-500 mt-1.5">{{ errors.title }}</p>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                            <div>
                                <label class="block text-xs font-semibold text-gray-600 mb-1.5">
                                    Kategori <span class="text-red-500">*</span>
                                </label>
                                <select v-model="form.category_slug" @change="onCategoryChange"
                                    :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all',
                                        errors.category_slug ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']">
                                    <option value="" disabled>Pilih Kategori</option>
                                    <option v-for="c in categories" :key="c.slug" :value="c.slug">{{ c.name }}</option>
                                </select>
                                <p v-if="errors.category_slug" class="text-xs text-red-500 mt-1.5">{{ errors.category_slug }}</p>
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Subkategori</label>
                                <select v-model="form.subcategory_slug"
                                    :disabled="!form.category_slug || loadingSubcategories"
                                    class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                                    <option value="">Tidak ada subkategori</option>
                                    <option v-for="s in subcategories" :key="s.slug" :value="s.slug">{{ s.name }}</option>
                                </select>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                            <div>
                                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Brand</label>
                                <!--
                                    value = b.n (nama asli brand, misal "Hikvision")
                                    karena backend menerima brand sebagai nama, bukan slug.
                                    Field form.brand menyimpan nama brand.
                                -->
                                <select v-model="form.brand"
                                    class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all">
                                    <option value="">Pilih Brand (Opsional)</option>
                                    <option v-for="b in brands" :key="b.id || b.s" :value="b.n">{{ b.n }}</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Tipe Item</label>
                                <input v-model="form.type" type="text" placeholder="Contoh: camera cctv"
                                    class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all" />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 2. Harga & Stok -->
                <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
                        <h2 class="text-sm font-bold text-gray-800">Harga & Stok</h2>
                        <span class="text-xs font-bold text-indigo-700 bg-indigo-50 px-3 py-1 rounded-lg border border-indigo-100">
                            Harga Final: Rp {{ calculatedPrice.toLocaleString('id-ID') }}
                        </span>
                    </div>
                    <div class="p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1.5">
                                Harga Asli (Rp) <span class="text-red-500">*</span>
                            </label>
                            <input v-model.number="form.original_price" type="number" min="0" placeholder="0"
                                :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all font-mono',
                                    errors.original_price ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']" />
                            <p v-if="errors.original_price" class="text-xs text-red-500 mt-1.5">{{ errors.original_price }}</p>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1.5">Diskon (%)</label>
                            <input v-model.number="form.discount_percentage" type="number" min="0" max="100" placeholder="0"
                                class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all font-mono" />
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1.5">
                                Jumlah Stok <span class="text-red-500">*</span>
                            </label>
                            <input v-model.number="form.stok" type="number" min="0" placeholder="0"
                                :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all font-mono',
                                    errors.stok ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']" />
                            <p v-if="errors.stok" class="text-xs text-red-500 mt-1.5">{{ errors.stok }}</p>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1.5">
                                Berat (Gram) <span class="text-red-500">*</span>
                            </label>
                            <input v-model.number="form.weight" type="number" min="1" placeholder="700"
                                :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all font-mono',
                                    errors.weight ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']" />
                            <p v-if="errors.weight" class="text-xs text-red-500 mt-1.5">{{ errors.weight }}</p>
                        </div>
                    </div>
                </div>

                <!-- 3. Spesifikasi JSON -->
                <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                        <h2 class="text-sm font-bold text-gray-800">Spesifikasi Detail (Format JSON)</h2>
                    </div>
                    <div class="p-6">
                        <textarea v-model="form.specs" rows="6"
                            placeholder='{"resolusi": "2MP", "fitur": "Night Vision"}'
                            :class="['w-full px-4 py-3 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all font-mono resize-none',
                                errors.specs ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']">
                        </textarea>
                        <p v-if="errors.specs" class="text-xs text-red-500 mt-1.5">{{ errors.specs }}</p>
                        <p v-else class="text-[11px] text-gray-400 mt-1.5 font-medium">
                            Contoh: <code>{"include_dvr": "yes", "camera_count": 4}</code>. Gunakan kutip ganda (").
                        </p>
                    </div>
                </div>

                <!-- 4. Upload Gambar -->
                <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
                        <h2 class="text-sm font-bold text-gray-800">Upload Gambar</h2>
                        <span class="text-xs text-gray-500">Gambar yang diupload akan menimpa gambar lama</span>
                    </div>
                    <div class="p-6">

                        <!-- Preview Gambar Lama -->
                        <div v-if="existingImages && existingImages.length" class="mb-6">
                            <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Gambar Saat Ini:</p>
                            <div class="flex flex-wrap gap-4">
                                <div v-for="(img, idx) in existingImages" :key="idx"
                                    class="w-24 h-24 rounded-2xl border-2 border-gray-100 overflow-hidden shadow-sm bg-gray-50">
                                    <img :src="img" alt="Gambar produk tersimpan" class="w-full h-full object-cover" loading="lazy"
                                        @error="e => e.target.style.opacity = '0.3'" />
                                </div>
                            </div>
                            <p class="text-xs text-gray-400 mt-2">
                                {{ existingImages.length }} gambar tersimpan.
                                {{ imageFiles.length > 0 ? 'Akan ditimpa dengan gambar baru.' : 'Biarkan kosong jika tidak ingin mengubah gambar.' }}
                            </p>
                        </div>

                        <!-- Area Upload Baru -->
                        <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Upload Gambar Baru (Opsional):</p>
                        <label
                            class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-2xl cursor-pointer transition-all hover:bg-indigo-50"
                            :class="[errors.images ? 'border-red-300 bg-red-50/30' : 'border-gray-300 bg-gray-50']">
                            <div class="flex flex-col items-center justify-center text-gray-500">
                                <svg class="w-8 h-8 mb-2 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                                </svg>
                                <p class="mb-1 text-sm font-semibold">
                                    <span class="text-indigo-600">Klik untuk upload</span> gambar baru
                                </p>
                                <p class="text-xs text-gray-400">PNG, JPG, WEBP (Maks. 4 gambar)</p>
                            </div>
                            <input type="file" multiple accept="image/*" class="hidden" @change="handleFileUpload"
                                :disabled="imageFiles.length >= 4" />
                        </label>
                        <p v-if="errors.images" class="text-xs text-red-500 mt-1.5">{{ errors.images }}</p>

                        <!-- Preview File Upload Baru -->
                        <div v-if="imageFiles.length > 0" class="mt-4 flex flex-wrap gap-4">
                            <div v-for="(file, idx) in imageFiles" :key="idx"
                                class="relative w-24 h-24 rounded-2xl border-2 border-indigo-200 overflow-hidden group shadow-sm">
                                <img :src="previewUrls[idx]" alt="Pratinjau gambar produk" class="w-full h-full object-cover" />
                                <button type="button" @click="removeImage(idx)"
                                    class="absolute inset-0 bg-black/50 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-[2px]">
                                    <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                    </div>
                </div>

                <!-- 5. Addon Resolution -->
                <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
                        <h2 class="text-sm font-bold text-gray-800">Sistem Layanan Tambahan (Addons)</h2>
                        <div class="flex bg-white p-1 rounded-lg border border-gray-200">
                            <button @click="form.addon_scope = 'inherit'" 
                                :class="['px-4 py-1.5 text-xs font-bold rounded-md transition-all', form.addon_scope === 'inherit' ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-400 hover:text-gray-600']">
                                Inherit
                            </button>
                            <button @click="form.addon_scope = 'custom'" 
                                :class="['px-4 py-1.5 text-xs font-bold rounded-md transition-all', form.addon_scope === 'custom' ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-400 hover:text-gray-600']">
                                Custom
                            </button>
                        </div>
                    </div>
                    <div class="p-6">
                        <div v-if="form.addon_scope === 'inherit'" class="flex items-center gap-3 p-4 bg-indigo-50/50 border border-indigo-100 rounded-xl">
                            <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 shrink-0">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-sm font-bold text-indigo-900">Mode Inherit Aktif</p>
                                <p class="text-[11px] text-indigo-600 leading-relaxed">Sistem akan otomatis mengambil layanan (addons) dari SubKategori atau Kategori induk produk ini. Tidak perlu konfigurasi manual.</p>
                            </div>
                        </div>

                        <div v-else class="space-y-4">
                            <div class="flex items-center gap-3 p-4 bg-amber-50/50 border border-amber-100 rounded-xl">
                                <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-600 shrink-0">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                                    </svg>
                                </div>
                                <div>
                                    <p class="text-sm font-bold text-amber-900">Mode Custom Aktif</p>
                                    <p class="text-[11px] text-amber-600 leading-relaxed">Silakan pilih layanan tambahan yang secara spesifik berlaku hanya untuk produk ini saja.</p>
                                </div>
                            </div>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div v-for="group in allGroups" :key="group.uuid" 
                                    @click="toggleGroupSelection(group.uuid)"
                                    :class="['p-3 rounded-xl border transition-all cursor-pointer flex items-center gap-3', 
                                        selectedGroupUuids.includes(group.uuid) 
                                        ? 'border-indigo-600 bg-indigo-50/50 ring-1 ring-indigo-600' 
                                        : 'border-gray-200 hover:border-gray-300 bg-white']">
                                    <div :class="['w-5 h-5 rounded border flex items-center justify-center transition-colors', 
                                        selectedGroupUuids.includes(group.uuid) ? 'bg-indigo-600 border-indigo-600' : 'bg-white border-gray-300']">
                                        <svg v-if="selectedGroupUuids.includes(group.uuid)" class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                    <div class="min-w-0 flex-1">
                                        <p class="text-xs font-bold text-gray-800 truncate">{{ group.name }}</p>
                                        <p class="text-[10px] text-gray-400 mt-0.5 truncate">
                                            {{ group.group_type === 'required' ? 'Wajib' : group.group_type === 'recommended' ? 'Rekomendasi' : 'Opsional' }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div v-if="!allGroups.length" class="text-center py-6 border border-dashed border-gray-200 rounded-xl">
                                <p class="text-xs text-gray-400">Belum ada grup layanan yang tersedia.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 6. Status Aktif -->
                <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                        <h2 class="text-sm font-bold text-gray-800">Status Produk</h2>
                    </div>
                    <div class="p-6">
                        <label class="flex items-center gap-3 cursor-pointer select-none group">
                            <div class="relative" @click="form.is_active = !form.is_active">
                                <div :class="['w-11 h-6 rounded-full transition-colors duration-200',
                                    form.is_active ? 'bg-indigo-600' : 'bg-gray-300']" />
                                <div :class="['absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200',
                                    form.is_active ? 'translate-x-5' : 'translate-x-0']" />
                            </div>
                            <div>
                                <p class="text-sm font-semibold text-gray-800">
                                    {{ form.is_active ? 'Produk Aktif' : 'Produk Non-aktif' }}
                                </p>
                                <p class="text-xs text-gray-400 mt-0.5">
                                    {{ form.is_active
                                        ? 'Produk tampil di halaman publik dan bisa dibeli.'
                                        : 'Produk disembunyikan dari halaman publik.' }}
                                </p>
                            </div>
                        </label>
                    </div>
                </div>

            </div>
        </div>

        <!-- ── Toast ───────────────────────────────────────────────────────── -->
        <Teleport to="body">
            <Transition name="toast">
                <div v-if="toast.show"
                    :class="['fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-2xl text-sm font-semibold',
                        toast.type === 'success' ? 'bg-gray-900 text-white' : 'bg-red-600 text-white']">
                    <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-black"
                        :class="toast.type === 'success' ? 'bg-emerald-500' : 'bg-red-400'">
                        {{ toast.type === 'success' ? '✓' : '✕' }}
                    </div>
                    {{ toast.message }}
                </div>
            </Transition>
        </Teleport>

    </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { brandApi, categoryApi, stockApi, addonApi } from '@/service/stock'

// ── Addon State ───────────────────────────────────────────────────
const allGroups = ref([])
const selectedGroupUuids = ref([])

function toggleGroupSelection(uuid) {
    const idx = selectedGroupUuids.value.indexOf(uuid)
    if (idx > -1) {
        selectedGroupUuids.value.splice(idx, 1)
    } else {
        selectedGroupUuids.value.push(uuid)
    }
}

const router   = useRouter()
const route    = useRoute()
const stockUuid = route.params.uuid

// ── State ──────────────────────────────────────────────────────────
const brands              = ref([])
const categories          = ref([])
const subcategories       = ref([])
const loadingSubcategories = ref(false)
const fetchingData        = ref(true)
const submitting          = ref(false)

// Gambar
const imageFiles   = ref([])   // File[] baru dari user
const previewUrls  = ref([])   // ObjectURL untuk preview lokal
const existingImages = ref([]) // URL gambar lama dari server

const errors = ref({})

const toast = reactive({ show: false, type: 'success', message: '' })
let toastTimer = null

const form = reactive({
    title:               '',
    brand:               '',   // simpan nama brand asli, bukan slug
    category_slug:       '',
    subcategory_slug:    '',
    type:                'camera cctv',
    original_price:      0,
    discount_percentage: 0,
    online_price:        0,
    weight:              700,
    specs:               '{}',
    is_active:           true,
    addon_scope:         'inherit',
})

// ── Computed ───────────────────────────────────────────────────────
const calculatedPrice = computed(() => {
    const orig = Number(form.original_price) || 0
    const disc = Number(form.discount_percentage) || 0
    if (orig > 0 && disc > 0) {
        return Math.floor(orig - (orig * disc / 100))
    }
    return orig
})

// Sync online_price setiap kali calculatedPrice berubah
watch(calculatedPrice, (val) => { form.online_price = val })

// ── Helpers ────────────────────────────────────────────────────────
function showToast(message, type = 'success') {
    clearTimeout(toastTimer)
    toast.message = message
    toast.type    = type
    toast.show    = true
    toastTimer    = setTimeout(() => toast.show = false, 3500)
}

// ── Image Handling ─────────────────────────────────────────────────
function handleFileUpload(event) {
    const files   = Array.from(event.target.files)
    const remaining = 4 - imageFiles.value.length

    if (files.length > remaining) {
        showToast(`Maksimal 4 gambar. Hanya ${remaining} slot tersisa.`, 'error')
    }

    const toAdd = files.slice(0, remaining)
    toAdd.forEach(f => {
        imageFiles.value.push(f)
        previewUrls.value.push(URL.createObjectURL(f))
    })

    // Reset input agar bisa upload file yang sama lagi jika perlu
    event.target.value = ''
}

function removeImage(idx) {
    URL.revokeObjectURL(previewUrls.value[idx])
    imageFiles.value.splice(idx, 1)
    previewUrls.value.splice(idx, 1)
}

// Bersihkan ObjectURL saat komponen di-unmount agar tidak memory leak
onBeforeUnmount(() => {
    previewUrls.value.forEach(url => URL.revokeObjectURL(url))
})

// ── Category & Subcategory ─────────────────────────────────────────
function extractSubcategoriesLocal(categorySlug) {
    if (!categorySlug) { subcategories.value = []; return }
    const cat = categories.value.find(c => c.slug === categorySlug)
    subcategories.value = cat?.subcategories || []
}

function onCategoryChange() {
    form.subcategory_slug = ''
    extractSubcategoriesLocal(form.category_slug)
}

// ── Fetch data produk + meta ───────────────────────────────────────
async function fetchMetaAndData() {
    fetchingData.value = true
    try {
        const [b, c, s, g, m] = await Promise.allSettled([
            brandApi.list(),
            categoryApi.list(),
            stockApi.detail(stockUuid),
            addonApi.listGroups(),
            addonApi.listStockMappings(stockUuid)
        ])

        // Brands: API /brands/ return array [{id,n,s,r,f,img}]
        if (b.status === 'fulfilled') {
            const raw = b.value?.data ?? b.value
            brands.value = Array.isArray(raw) ? raw : []
        }

        // Categories: API /category/ return array [{id,name,slug,subcategories}]
        if (c.status === 'fulfilled') {
            const raw = c.value?.data ?? c.value
            categories.value = Array.isArray(raw) ? raw : []
        }

        // Addon Groups
        if (g.status === 'fulfilled') {
            const raw = g.value?.data?.data ?? g.value?.data ?? g.value
            allGroups.value = Array.isArray(raw) ? raw : []
        }

        // Stock Addon Mappings
        if (m.status === 'fulfilled') {
            const raw = m.value?.data?.data ?? m.value?.data ?? m.value
            selectedGroupUuids.value = Array.isArray(raw) ? raw : []
        }

        // Stock detail: /public/detail/:uuid → { status, data: {...} }
        if (s.status === 'fulfilled') {
            const axiosData = s.value?.data ?? s.value
            const product   = axiosData?.data ?? axiosData

            // Petakan brand_slug → nama brand asli untuk select
            // product.brand = nama brand (dari DB), bukan slug
            const matchedBrand = brands.value.find(b =>
                b.n?.toLowerCase() === product?.brand?.toLowerCase() ||
                b.s?.toLowerCase() === product?.brand?.toLowerCase()
            )

            Object.assign(form, {
                title:               product?.title              || '',
                brand:               matchedBrand?.n            || product?.brand || '',
                category_slug:       product?.category          || product?.category_slug || '',
                subcategory_slug:    product?.subcategory        || product?.subcategory_slug || '',
                type:                product?.type               || 'camera cctv',
                original_price:      Number(product?.original_price  || 0),
                discount_percentage: Number(product?.discount_percentage || 0),
                online_price:        Number(product?.price || product?.online_price || 0),
                stok:                Number(product?.stok       || 0),
                weight:              Number(product?.weight      || 700),
                specs:               product?.specs
                                         ? JSON.stringify(product.specs, null, 2)
                                         : '{}',
                is_active:           product?.is_active ?? true,
                addon_scope:         product?.addon_scope || 'inherit',
            })

            existingImages.value = product?.images || []

            if (form.category_slug) {
                extractSubcategoriesLocal(form.category_slug)
            }
        } else {
            showToast('Data produk tidak ditemukan atau gagal dimuat', 'error')
            setTimeout(() => router.push('/stock'), 1500)
        }

    } catch (err) {
        console.error('Fetch Data Error:', err)
        showToast('Terjadi kesalahan sistem saat memuat data', 'error')
    } finally {
        fetchingData.value = false
    }
}

// ── Validation ─────────────────────────────────────────────────────
function validateForm() {
    const e = {}

    if (!form.title.trim())          e.title          = 'Judul wajib diisi'
    if (!form.category_slug)         e.category_slug  = 'Kategori wajib dipilih'
    if (Number(form.original_price) <= 0) e.original_price = 'Harga asli harus lebih dari 0'
    if (Number(form.stok) < 0)       e.stok           = 'Stok tidak boleh negatif'
    if (Number(form.weight) <= 0)    e.weight         = 'Berat harus lebih dari 0 gram'
    if (imageFiles.value.length > 4) e.images         = 'Maksimal 4 gambar baru'

    try {
        JSON.parse(form.specs)
    } catch {
        e.specs = 'Spesifikasi harus berformat JSON yang valid. Contoh: {"resolusi": "4MP"}'
    }

    errors.value = e
    return Object.keys(e).length === 0
}

// ── Submit ─────────────────────────────────────────────────────────
async function submitForm() {
    if (!validateForm()) {
        showToast('Periksa kembali form Anda', 'error')
        return
    }

    submitting.value = true

    try {
        const fd = new FormData()

        // ── Field teks — sesuai PATCH /admin/update/{uuid} ──────────────
        fd.append('title',               form.title.trim())
        fd.append('category_slug',       form.category_slug)
        fd.append('type',                form.type || 'camera cctv')
        fd.append('original_price',      String(form.original_price))
        fd.append('discount_percentage', String(form.discount_percentage ?? 0))
        fd.append('stok',                String(form.stok))
        fd.append('weight',              String(form.weight || 700))

        // is_active — multipart hanya bisa string
        fd.append('is_active', form.is_active ? 'true' : 'false')
        fd.append('addon_scope', form.addon_scope || 'inherit')

        // brand — nama asli brand (bukan slug)
        // Backend Stock model menyimpan brand sebagai varchar nama, bukan slug
        if (form.brand) {
            fd.append('brand', form.brand)
        }

        // subcategory (opsional)
        if (form.subcategory_slug) {
            fd.append('subcategory_slug', form.subcategory_slug)
        }

        // online_price:
        // Jika ada diskon → backend PATCH route hitung sendiri dari orig+disc
        // Kirim juga sebagai fallback jika user set manual (tanpa diskon)
        if (form.discount_percentage > 0) {
            // Biarkan backend kalkulasi, tapi tetap kirim computed value
            fd.append('online_price', String(calculatedPrice.value))
        } else {
            // Harga manual — tidak ada diskon
            fd.append('online_price', String(form.original_price))
        }

        // specs — JSON compact string, field name "specs" sesuai Form(...) backend
        try {
            fd.append('specs', JSON.stringify(JSON.parse(form.specs)))
        } catch {
            fd.append('specs', '{}')
        }

        // ── Gambar baru — kosong = gambar lama tidak disentuh ────────────
        if (imageFiles.value.length > 0) {
            imageFiles.value.forEach(img => fd.append('images', img))
        }

        // ── Kirim ke backend ─────────────────────────────────────────────
        await stockApi.update(stockUuid, fd)

        // ── Sync Addon Mappings jika custom ──────────────────────────────
        if (form.addon_scope === 'custom') {
            await addonApi.syncStockMappings(stockUuid, selectedGroupUuids.value)
        }

        showToast('Produk berhasil diperbarui!')
        setTimeout(() => router.push('/stock'), 1500)

    } catch (err) {
        console.error('Update Error:', err)

        // Parsing error detail dari FastAPI
        const detail = err?.response?.data?.detail
        const msg = typeof detail === 'string'
            ? detail
            : Array.isArray(detail)
                ? detail.map(d => d.msg || d.message).join(', ')
                : 'Gagal mengupdate produk. Coba lagi.'

        showToast(msg, 'error')
    } finally {
        submitting.value = false
    }
}

// ── Init ───────────────────────────────────────────────────────────
onMounted(fetchMetaAndData)
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
    transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
    opacity: 0;
    transform: translateX(20px);
}
</style>