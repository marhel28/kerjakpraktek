<template>
    <div class="min-h-screen bg-[#F7F8FC] font-sans">

        <!-- ── Header ──────────────────────────────────────────────────────── -->
        <div class="bg-white border-b border-gray-200 sticky top-0 z-20 shadow-sm">
            <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">

                <div class="flex items-center gap-3">
                    <router-link to="/stock"
                        class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors border border-transparent hover:border-gray-200">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                        </svg>
                    </router-link>

                    <div>
                        <h1 class="text-lg font-bold text-gray-900 leading-none">Tambah Produk Baru</h1>
                        <p class="text-xs text-gray-500 mt-1">Isi data di bawah dengan lengkap</p>
                    </div>
                </div>

                <div class="flex items-center gap-3">
                    <router-link to="/stock"
                        class="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
                        Batal
                    </router-link>

                    <button @click="submitForm" :disabled="submitting"
                        class="flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 disabled:opacity-60 active:scale-95 transition-all shadow-sm">
                        <div v-if="submitting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        {{ submitting ? 'Menyimpan...' : 'Simpan Produk' }}
                    </button>
                </div>

            </div>
        </div>

        <!-- ── Body / Form Area ────────────────────────────────────────────── -->
        <div class="max-w-4xl mx-auto px-6 py-8 space-y-6">

            <!-- 1. Informasi Dasar -->
            <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                    <h2 class="text-sm font-bold text-gray-800">Informasi Dasar</h2>
                </div>
                <div class="p-6 space-y-5">
                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">Nama Produk <span class="text-red-500">*</span></label>
                        <input v-model="form.title" type="text" placeholder="Contoh: Kamera CCTV Ezviz C6N 2MP"
                            :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all', errors.title ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']" />
                        <p v-if="errors.title" class="text-xs text-red-500 mt-1.5">{{ errors.title }}</p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1.5">Kategori <span class="text-red-500">*</span></label>
                            <select v-model="form.category_slug" @change="onCategoryChange"
                                :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all', errors.category_slug ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']">
                                <option value="" disabled>Pilih Kategori</option>
                                <option v-for="c in categories" :key="c.slug" :value="c.slug">{{ c.name || c.slug }}</option>
                            </select>
                            <p v-if="errors.category_slug" class="text-xs text-red-500 mt-1.5">{{ errors.category_slug }}</p>
                        </div>

                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1.5">Subkategori</label>
                            <select v-model="form.subcategory_slug" :disabled="!form.category_slug"
                                class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                                <option value="">Tidak ada subkategori</option>
                                <option v-for="s in subcategories" :key="s.slug" :value="s.slug">{{ s.name || s.slug }}</option>
                            </select>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1.5">Brand</label>
                            <select v-model="form.brand"
                                class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all">
                                <option value="">Pilih Brand (Opsional)</option>
                                <option v-for="b in brands" :key="b.key || b.s" :value="b.key || b.s">{{ b.n || b.key }}</option>
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
                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">Harga Asli (Rp) <span class="text-red-500">*</span></label>
                        <input v-model.number="form.original_price" type="number" min="0" placeholder="0"
                            :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all font-mono', errors.original_price ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']" />
                        <p v-if="errors.original_price" class="text-xs text-red-500 mt-1.5">{{ errors.original_price }}</p>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">Diskon (%)</label>
                        <input v-model.number="form.discount_percentage" type="number" min="0" max="100" placeholder="0"
                            class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all font-mono" />
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">Jumlah Stok <span class="text-red-500">*</span></label>
                        <input v-model.number="form.stok" type="number" min="0" placeholder="1"
                            :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all font-mono', errors.stok ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']" />
                        <p v-if="errors.stok" class="text-xs text-red-500 mt-1.5">{{ errors.stok }}</p>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">Berat (Gram) <span class="text-red-500">*</span></label>
                        <input v-model.number="form.weight" type="number" min="1" placeholder="700"
                            :class="['w-full px-4 py-2.5 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all font-mono', errors.weight ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']" />
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
                    <textarea v-model="form.specs" rows="5" placeholder='{"resolusi": "2MP", "fitur": "Night Vision"}'
                        :class="['w-full px-4 py-3 text-sm border rounded-xl focus:outline-none focus:ring-2 transition-all font-mono', errors.specs ? 'border-red-300 focus:ring-red-500 bg-red-50/30' : 'border-gray-200 focus:ring-indigo-500 bg-gray-50 focus:bg-white']"></textarea>
                    <p v-if="errors.specs" class="text-xs text-red-500 mt-1.5">{{ errors.specs }}</p>
                    <p v-else class="text-[11px] text-gray-400 mt-1.5 font-medium">Gunakan tanda kutip ganda (") untuk key dan string value.</p>
                </div>
            </div>

            <!-- 4. Upload Gambar -->
            <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
                    <h2 class="text-sm font-bold text-gray-800">Upload Gambar</h2>
                    <span class="text-xs text-gray-500">Maks. 4 gambar</span>
                </div>
                <div class="p-6">
                    <label class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all hover:bg-indigo-50"
                        :class="[errors.images ? 'border-red-300 bg-red-50/30' : 'border-gray-300 bg-gray-50']">
                        <div class="flex flex-col items-center justify-center text-gray-500">
                            <svg class="w-8 h-8 mb-2 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                            </svg>
                            <p class="mb-1 text-sm font-semibold"><span class="text-indigo-600">Klik untuk upload</span> gambar produk</p>
                            <p class="text-xs">PNG, JPG, WEBP</p>
                        </div>
                        <input type="file" multiple accept="image/*" class="hidden" @change="handleFileUpload" />
                    </label>
                    <p v-if="errors.images" class="text-xs text-red-500 mt-1.5">{{ errors.images }}</p>

                    <!-- Preview Gambar -->
                    <div v-if="imageFiles.length > 0" class="mt-4 flex flex-wrap gap-3">
                        <div v-for="(file, idx) in imageFiles" :key="idx" class="relative w-24 h-24 rounded-xl border-2 border-indigo-200 overflow-hidden group shadow-sm">
                            <img :src="getPreviewUrl(file)" alt="Pratinjau gambar produk" class="w-full h-full object-cover" />
                            <button type="button" @click="removeImage(idx)"
                                class="absolute inset-0 bg-black/60 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-[2px]">
                                <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 5. Addon Resolution -->
            <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                    <h2 class="text-sm font-bold text-gray-800">Sistem Layanan Tambahan (Addons)</h2>
                </div>
                <div class="p-6">
                    <div class="flex items-center justify-between gap-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
                        <div class="flex-1">
                            <p class="text-sm font-bold text-gray-800 mb-1">Metode Resolusi Addon</p>
                            <p class="text-xs text-gray-400">Pilih bagaimana sistem menentukan addon untuk produk ini.</p>
                        </div>
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
                    <div class="mt-4 px-1">
                        <p v-if="form.addon_scope === 'inherit'" class="text-[11px] text-indigo-500 font-medium italic">
                            ✨ Mode Inherit: Produk akan menggunakan addon dari SubKategori atau Kategori (Default).
                        </p>
                        <p v-else class="text-[11px] text-amber-600 font-medium italic">
                            ⚠️ Mode Custom: Produk akan menggunakan addon yang secara spesifik dipetakan ke produk ini. (Atur detail setelah simpan)
                        </p>
                    </div>
                </div>
            </div>

        </div>



    </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { brandApi, categoryApi, stockApi } from '@/service/stock'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const toastStore = useToastStore()

// ── States ──
const brands = ref([])
const categories = ref([])
const subcategories = ref([])
const submitting = ref(false)
const imageFiles = ref([])

const errors = ref({})

const form = reactive({
    title: '',
    brand: '',
    category_slug: '',
    subcategory_slug: '',
    type: 'camera cctv',
    original_price: 0,
    discount_percentage: 0,
    online_price: 0,
    stok: 1,
    weight: 700,
    specs: JSON.stringify({ garansi: '1 Tahun' }, null, 2),
    addon_scope: 'inherit'
})

// ── Computed & Watcher untuk Kalkulasi Harga Online ──
const calculatedPrice = computed(() => {
    const original = form.original_price || 0;
    const discount = form.discount_percentage || 0;
    if (original > 0 && discount > 0) {
        return Math.floor(original - (original * discount / 100));
    }
    return original;
})

watch(calculatedPrice, (newPrice) => {
    form.online_price = newPrice;
})

// ── Image Handling ──
function handleFileUpload(event) {
    const files = Array.from(event.target.files);
    if (imageFiles.value.length + files.length > 4) {
        toastStore.warning("Maksimal hanya boleh 4 gambar!");
        return;
    }
    imageFiles.value = [...imageFiles.value, ...files];
}

function removeImage(index) {
    imageFiles.value.splice(index, 1);
}

function getPreviewUrl(file) {
    return URL.createObjectURL(file);
}

// ── Fetch Meta Data (Kategori & Brand) ──
async function fetchMeta() {
    try {
        const [b, c] = await Promise.allSettled([
            brandApi.list(),
            categoryApi.list()
        ])

        if (b.status === 'fulfilled') {
            const payload = b.value?.data || b.value
            brands.value = Array.isArray(payload) ? payload : []
        }

        if (c.status === 'fulfilled') {
            const payload = c.value?.data || c.value
            categories.value = Array.isArray(payload) ? payload : []
        }
    } catch (e) {
        console.error(e)
    }
}

// ── Subkategori Mapping Lokal (Lebih cepat, tidak nembak API) ──
function onCategoryChange() {
    form.subcategory_slug = ''
    subcategories.value = []
    
    if (!form.category_slug) return
    
    const cat = categories.value.find(c => c.slug === form.category_slug)
    if (cat && cat.subcategories) {
        subcategories.value = cat.subcategories
    }
}

// ── Validation ──
function validateForm() {
    const e = {}

    if (!form.title.trim()) e.title = 'Judul wajib diisi'
    if (!form.category_slug) e.category_slug = 'Kategori wajib dipilih'
    if (form.original_price <= 0) e.original_price = 'Harga harus lebih dari 0'
    if (form.stok < 0) e.stok = 'Stok tidak valid'
    if (form.weight <= 0) e.weight = 'Berat harus lebih dari 0 gram'

    if (imageFiles.value.length > 4) e.images = 'Maksimal 4 gambar'

    try {
        JSON.parse(form.specs)
    } catch {
        e.specs = 'Specs harus berformat JSON yang valid'
    }

    errors.value = e
    return Object.keys(e).length === 0
}

// ── Submit ──
async function submitForm() {
    if (!validateForm()) {
        toastStore.error('Form belum lengkap atau terdapat error')
        return
    }

    submitting.value = true

    try {
        const fd = new FormData()

        // Append text fields
        Object.entries(form).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                fd.append(key, value)
            }
        })

        // Append images
        imageFiles.value.forEach(file => {
            fd.append('images', file)
        })

        await stockApi.create(fd)

        toastStore.success('Produk berhasil ditambahkan')
        setTimeout(() => router.push('/stock'), 1500)

    } catch (e) {
        console.error(e)
        toastStore.error('Gagal menyimpan produk')
    } finally {
        submitting.value = false
    }
}



onMounted(fetchMeta)
</script>

<style scoped>
@reference "tailwindcss";
</style>