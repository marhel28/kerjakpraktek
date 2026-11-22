<template>
    <div class="min-h-screen bg-[#F7F8FC] font-sans text-gray-900">

        <!-- ══════════════════════════════════════════════════════ -->
        <!-- TOAST                                                 -->
        <!-- ══════════════════════════════════════════════════════ -->
        <Teleport to="body">
            <Transition name="toast">
                <div v-if="toast.show" :class="[
                    'fixed top-5 right-5 z-[9999] flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-2xl text-sm font-semibold backdrop-blur-sm',
                    toast.type === 'success' ? 'bg-emerald-600 text-white'
                        : toast.type === 'info' ? 'bg-indigo-900 text-white'
                            : 'bg-red-600 text-white'
                ]">
                    <svg v-if="toast.type === 'success'" class="w-4 h-4 shrink-0" fill="none" stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                    </svg>
                    <svg v-else-if="toast.type === 'info'" class="w-4 h-4 shrink-0" fill="none" stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <svg v-else class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
                            d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    {{ toast.message }}
                </div>
            </Transition>
        </Teleport>

        <!-- ══════════════════════════════════════════════════════ -->
        <!-- CONFIRM MODAL                                         -->
        <!-- ══════════════════════════════════════════════════════ -->
        <Teleport to="body">
            <Transition name="modal">
                <div v-if="confirmModal.show" class="fixed inset-0 z-[9998] flex items-center justify-center p-4">
                    <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="confirmModal.show = false" />
                    <div class="relative bg-white rounded-xl shadow-2xl p-7 w-full max-w-sm border border-gray-100">
                        <div class="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mx-auto mb-4">
                            <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                        </div>
                        <h3 class="text-center font-bold text-gray-900 mb-2">
                            {{ isEditMode ? 'Simpan Perubahan?' : 'Simpan Konfigurasi Baru?' }}
                        </h3>
                        <p class="text-center text-sm text-gray-500 mb-6 leading-relaxed">
                            <template v-if="isEditMode">
                                Perubahan akan <span class="font-bold text-gray-700">memperbarui</span> record yang ada.
                            </template>
                            <template v-else>
                                Konfigurasi lama akan <span class="font-bold text-gray-700">dinonaktifkan</span> dan
                                diganti yang baru.
                            </template>
                        </p>
                        <div v-if="loadError"
                            class="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-left text-xs leading-relaxed text-red-700">
                            Data konfigurasi belum berhasil dimuat ({{ loadError }}). Simpan dinonaktifkan agar record
                            lama tidak tertimpa. Tutup dialog ini lalu gunakan tombol muat ulang di header.
                        </div>
                        <div class="flex gap-3">
                            <button @click="confirmModal.show = false"
                                class="flex-1 py-2.5 rounded-lg border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50 transition active:scale-95">
                                Batal
                            </button>
                            <button @click="doSave" :disabled="saving || !canSave"
                                class="flex-1 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2 active:scale-95">
                                <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                        stroke-width="4" />
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                                </svg>
                                {{ saving ? '...' : 'Simpan' }}
                            </button>
                        </div>
                    </div>
                </div>
            </Transition>
        </Teleport>

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
                        <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Konfigurasi Harga</h1>
                        <p class="text-xs text-gray-400 mt-0.5">Atur biaya jasa, multiplier brand, dan operasional</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <div v-if="current && !loading"
                        class="hidden sm:flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 mr-2">
                        <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Active v{{ currentVersion }}</span>
                    </div>
                    <button @click="reload" :disabled="loading"
                        class="w-9 h-9 flex items-center justify-center rounded-lg bg-white hover:bg-gray-50 border border-gray-200 text-gray-400 transition disabled:opacity-50 active:scale-95">
                        <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </button>
                    <button @click="goBack" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded-lg transition active:scale-95 shadow-sm">
                        Keluar
                    </button>
                </div>
            </div>
        </div>

        <div v-if="loading" class="max-w-5xl mx-auto px-6 py-12 flex flex-col items-center gap-4">
            <div class="w-8 h-8 rounded-full border-2 border-gray-200 border-t-indigo-600 animate-spin" />
            <p class="text-[10px] font-bold tracking-widest text-gray-400 uppercase">Sinkronisasi Data...</p>
        </div>

        <!-- ── Main Content ───────────────────────────────────────── -->
        <div v-else class="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6 pb-24">

            <!-- Active Config Info -->
            <div v-if="!current" class="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3 shadow-sm">
                <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                </svg>
                <div>
                    <p class="text-sm font-bold text-amber-800">Belum ada konfigurasi aktif</p>
                    <p class="text-xs text-amber-700">Sistem booking memerlukan konfigurasi harga dasar untuk berfungsi.</p>
                </div>
            </div>

            <!-- Base Price Section -->
            <section class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                        </div>
                        <div>
                            <p class="font-bold text-gray-900 text-sm">Biaya Dasar Jasa</p>
                            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Base price per camera point</p>
                        </div>
                    </div>
                </div>
                <div class="p-5 grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div v-for="cat in CATEGORIES" :key="cat.id">
                        <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">{{ cat.label }}</label>
                        <div class="relative">
                            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-400">Rp</span>
                            <input v-model.number="form.base_price_per_camera[cat.id]" type="number" class="w-full pl-8 pr-3 py-2 text-sm font-mono bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition" />
                        </div>
                    </div>
                </div>
            </section>

            <!-- Brand Multipliers -->
            <section class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                        </div>
                        <div>
                            <p class="font-bold text-gray-900 text-sm">Brand Multipliers</p>
                            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Pricing adjustments by brand</p>
                        </div>
                    </div>
                    <button @click="addBrand" class="px-3 py-1 text-[10px] font-bold text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition border border-indigo-100">+ Brand</button>
                </div>
                <div class="p-5">
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div v-for="(mul, brand) in form.brand_multipliers" :key="brand" class="p-4 bg-gray-50 rounded-xl border border-gray-100 flex items-center gap-3 hover:bg-white hover:shadow-md transition-all group">
                            <div class="flex-1">
                                <p class="text-[10px] font-bold text-gray-400 uppercase mb-1">{{ brand }}</p>
                                <input v-model.number="form.brand_multipliers[brand]" type="number" step="0.1" class="w-full px-3 py-1.5 text-sm font-mono border border-gray-200 rounded-lg outline-none group-hover:border-indigo-200" />
                            </div>
                            <button @click="removeBrand(brand)" class="p-2 text-gray-300 hover:text-red-500 transition"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Transport & Operational -->
            <section class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0zM15 11a3 3 0 11-6 0 3 3 0 016 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                        </div>
                        <div>
                            <p class="font-bold text-gray-900 text-sm">Transport & Distance</p>
                            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Shipping and operational rules</p>
                        </div>
                    </div>
                </div>
                <div class="p-5 grid grid-cols-1 sm:grid-cols-4 gap-5">
                    <div>
                        <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Per KM (Rp)</label>
                        <div class="relative">
                            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-400">Rp</span>
                            <input v-model.number="form.transport_per_km" type="number" class="w-full pl-8 pr-3 py-2 text-sm font-mono bg-gray-50 border border-gray-200 rounded-lg outline-none" />
                        </div>
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Min Fee (Rp)</label>
                        <div class="relative">
                            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-400">Rp</span>
                            <input v-model.number="form.transport_min_fee" type="number" class="w-full pl-8 pr-3 py-2 text-sm font-mono bg-gray-50 border border-gray-200 rounded-lg outline-none" />
                        </div>
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Max Fee (Rp)</label>
                        <div class="relative">
                            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-400">Rp</span>
                            <input v-model.number="form.transport_max_fee" type="number" class="w-full pl-8 pr-3 py-2 text-sm font-mono bg-gray-50 border border-gray-200 rounded-lg outline-none" />
                        </div>
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Max Distance (KM)</label>
                        <div class="relative">
                            <input v-model.number="form.max_distance_km" type="number" min="1" max="1000" step="1" class="w-full px-3 py-2 text-sm font-mono bg-gray-50 border border-gray-200 rounded-lg outline-none" />
                            <span class="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-400">KM</span>
                        </div>
                    </div>
                </div>
                <!-- Preview area -->
                <div class="mx-5 mb-5 p-4 bg-indigo-50/50 rounded-xl border border-indigo-100/50 flex flex-wrap gap-x-8 gap-y-2">
                    <div v-for="km in [5, 10, 20, 30]" :key="km" class="text-[11px]">
                        <span class="text-gray-400 font-bold uppercase tracking-tighter">{{ km }} KM:</span>
                        <span class="ml-2 font-mono font-bold text-indigo-600">{{ previewTransport(km) }}</span>
                    </div>
                </div>
            </section>

            <!-- Operation & DP -->
            <section class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                        </div>
                        <div>
                            <p class="font-bold text-gray-900 text-sm">System & DP Settings</p>
                            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Core system operational rules</p>
                        </div>
                    </div>
                </div>
                <div class="p-5 grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Booking DP (%)</label>
                        <div class="flex items-center gap-4">
                            <div class="relative w-24">
                                <input v-model.number="form.dp_percentage" type="number" class="w-full pr-8 pl-3 py-2 text-sm font-mono bg-gray-50 border border-gray-200 rounded-lg outline-none" />
                                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-400">%</span>
                            </div>
                            <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                                <div class="h-full bg-indigo-500 transition-all" :style="{ width: form.dp_percentage + '%' }"></div>
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
                        <div>
                            <p class="text-[10px] font-bold text-gray-400 uppercase mb-1">System Status</p>
                            <p class="text-xs font-bold" :class="form.is_active ? 'text-emerald-600' : 'text-gray-400'">{{ form.is_active ? 'SISTEM AKTIF' : 'SISTEM MAINTENANCE' }}</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" v-model="form.is_active" class="sr-only peer">
                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                        </label>
                    </div>
                </div>
            </section>

            <!-- ══ AKSI SIMPAN ════════════════════════════════════ -->
            <div class="flex items-center justify-between gap-4 pb-4">
                <div class="flex items-center gap-2 text-xs text-stone-400">
                    <svg class="w-4 h-4 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Menyimpan akan <span class="font-semibold text-stone-600">menonaktifkan config lama</span> dan
                    membuat versi baru.
                </div>
                <div class="flex items-center gap-3 shrink-0">
                    <button @click="loadFromCurrent" :disabled="!current"
                        class="px-4 py-2.5 text-sm font-semibold text-stone-600 bg-white border border-stone-200 rounded-xl hover:border-stone-400 disabled:opacity-40 disabled:cursor-not-allowed transition active:scale-95">
                        Reset ke Aktif
                    </button>
                    <button @click="confirmModal.show = true" :disabled="saving || !canSave"
                        class="px-6 py-2.5 bg-stone-900 hover:bg-stone-700 text-white text-sm font-black rounded-xl transition disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 active:scale-95 shadow-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
                                d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                        </svg>
                        Simpan Konfigurasi
                    </button>
                </div>
            </div>

            <!-- Validation errors -->
            <div v-if="formErrors.length" class="bg-red-50 border border-red-200 rounded-2xl p-4 space-y-1">
                <p class="text-xs font-bold text-red-700 mb-2">Perbaiki sebelum menyimpan:</p>
                <p v-for="err in formErrors" :key="err" class="text-xs text-red-600 flex items-center gap-2">
                    <span class="w-1 h-1 rounded-full bg-red-400 shrink-0" />
                    {{ err }}
                </p>
            </div>

        </div><!-- end main form -->
    </div>
</template>

<!-- ══════════════════════════════════════════════════════════ -->
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800;900&family=Geist+Mono:wght@400;500;600;700&display=swap');

.field-label {
    display: block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #78716c;
    margin-bottom: 6px;
}

.field-input {
    width: 100%;
    padding: 10px 12px;
    background: #fafaf9;
    border: 1px solid #e7e5e4;
    border-radius: 12px;
    font-size: 13px;
    color: #1c1917;
    transition: all 0.15s ease;
}

.field-input:focus {
    outline: none;
    background: white;
    border-color: #a8a29e;
    box-shadow: 0 0 0 3px rgba(168, 162, 158, 0.15);
}

.abs-prefix {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 11px;
    color: #a8a29e;
    font-family: 'Geist Mono', monospace;
    pointer-events: none;
    user-select: none;
}

/* Toast */
.toast-enter-active,
.toast-leave-active {
    transition: all .25s ease;
}

.toast-enter-from,
.toast-leave-to {
    opacity: 0;
    transform: translateX(1rem) scale(.95);
}

/* Modal */
.modal-enter-active,
.modal-leave-active {
    transition: all .2s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}
</style>

<!-- ══════════════════════════════════════════════════════════ -->
<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/service/api'

// ── Constants ──────────────────────────────────────────────
const CATEGORIES = [
    { id: 'installation', label: 'Pemasangan' },
    { id: 'maintenance', label: 'Servis' },
    { id: 'troubleshoot', label: 'Troubleshoot' },
    { id: 'consultation', label: 'Konsultasi' },
]

// ── Props & Emits ──────────────────────────────────────────
const props = defineProps({
    initialData: { type: Object, default: null }
})
const emit = defineEmits(['close', 'saved'])

const route = useRoute()
const router = useRouter()

// ── State ──────────────────────────────────────────────────
const loading = ref(true)
const saving = ref(false)
const current = ref(null)       // config aktif dari backend
const currentVersion = ref('1') // versi display
const loadError = ref('')       // gagal memuat config saat mode edit

const toast = reactive({ show: false, type: 'success', message: '' })
let toastTimer = null

const confirmModal = reactive({ show: false })

// ── Init ───────────────────────────────────────────────────
onMounted(async () => {
    const uuid = route.query.uuid
    
    if (props.initialData) {
        current.value = props.initialData
        applyConfig(props.initialData)
        loading.value = false
    } else if (uuid) {
        await fetchByUuid(uuid)
    } else {
        await fetchCurrent()
    }
})

// Form utama — field sesuai PricingConfigCreate schema
const form = reactive({
    base_price_per_camera: {
        installation: 150_000,
        maintenance: 75_000,
        troubleshoot: 75_000,
        consultation: 200_000,
    },
    brand_multiplier: {},     // dikelola lewat brandList
    consultation_fee: 200_000,
    transport_per_km: 5_000,
    transport_min_fee: 25_000,
    transport_max_fee: 300_000,
    max_distance_km: 30.0,
    addons_config: [],
    routes_config: [],
    dp_percentage: 50,
})

// Brand list sebagai array untuk UI
const brandList = ref([])
// Route list sebagai array untuk UI
const routeList = ref([])

// ── Sync Konsultasi ────────────────────────────────────────
// Sinkronkan form.consultation_fee dengan base_price_per_camera.consultation
watch(() => form.consultation_fee, (val) => {
    form.base_price_per_camera.consultation = val
})
watch(() => form.base_price_per_camera.consultation, (val) => {
    form.consultation_fee = val
})

// ── Computed ───────────────────────────────────────────────
const isEditMode = computed(() => !!(route.query.uuid || props.initialData?.uuid))

const formErrors = computed(() => {
    const errs = []
    CATEGORIES.forEach(c => {
        const val = form.base_price_per_camera[c.id];
        if (val === undefined || val === null || val === '' || Number(val) < 0)
            errs.push(`Harga "${c.label}" harus diisi dan >= 0`)
    })
    if (form.dp_percentage < 10 || form.dp_percentage > 100)
        errs.push('DP harus antara 10% – 100%')
    if (form.max_distance_km < 1 || form.max_distance_km > 1000)
        errs.push('Max jarak harus antara 1 – 1000 km')
    if (form.transport_min_fee > form.transport_max_fee)
        errs.push('Transport min fee tidak boleh lebih besar dari max fee')
    brandList.value.forEach((b, i) => {
        if (!b.key.trim()) errs.push(`Brand #${i + 1}: key wajib diisi`)
        if (!b.multiplier || b.multiplier <= 0) errs.push(`Brand #${i + 1}: multiplier harus > 0`)
    })
    form.addons_config.forEach((a, i) => {
        if (!a.key.trim()) errs.push(`Addon #${i + 1}: key wajib diisi`)
        if (!a.price || a.price < 0) errs.push(`Addon #${i + 1}: harga harus >= 0`)
    })
    return errs
})

const isValid = computed(() => formErrors.value.length === 0)
// Di mode edit, jangan simpan jika data aslinya gagal dimuat —
// form masih berisi default dan PATCH akan menimpa record.
const canSave = computed(() => isValid.value && (!isEditMode.value || !!current.value))

// ── Helpers ────────────────────────────────────────────────
function fmt(n) {
    if (!n && n !== 0) return 'Rp 0'
    return 'Rp ' + Number(n).toLocaleString('id-ID')
}

function showToast(type, message) {
    clearTimeout(toastTimer)
    Object.assign(toast, { show: true, type, message })
    toastTimer = setTimeout(() => { toast.show = false }, 3500)
}

function previewTransport(km) {
    if (km === 0) return fmt(0)
    const raw = Math.round(km * (form.transport_per_km || 0))
    const fee = Math.max(
        form.transport_min_fee || 0,
        Math.min(raw, form.transport_max_fee || 999_999_999)
    )
    return fmt(fee)
}

// ── Load from API response → form ─────────────────────────
function applyConfig(cfg) {
    if (!cfg) return
    // base prices
    CATEGORIES.forEach(c => {
        form.base_price_per_camera[c.id] =
            cfg.categories?.find(x => x.id === c.id)?.base_price
            ?? cfg.base_price_per_camera?.[c.id]
            ?? 0
    })
    // consultation_fee
    form.consultation_fee = cfg.consultation_fee ?? 200_000
    // transport
    form.transport_per_km = cfg.transport_per_km ?? 5_000
    form.transport_min_fee = cfg.transport_min_fee ?? 25_000
    form.transport_max_fee = cfg.transport_max_fee ?? 300_000
    form.max_distance_km = cfg.max_distance_km ?? 30.0
    // dp
    form.dp_percentage = cfg.dp_percentage ?? 50
    // brands — from either brands[] or brand_multiplier{}
    if (cfg.brands) {
        brandList.value = cfg.brands.map(b => ({
            key: b.key,
            multiplier: b.multiplier,
        }))
    } else if (cfg.brand_multiplier) {
        brandList.value = Object.entries(cfg.brand_multiplier).map(([key, multiplier]) => ({
            key, multiplier
        }))
    }
    // addons
    form.addons_config = (cfg.addons || cfg.addons_config || []).map(a => ({
        key: a.key || '',
        label: a.label || '',
        type: a.type || 'per_cam',
        price: a.price ?? 0,
        icon: a.icon || '',
        description: a.description || '',
    }))
    // routes
    routeList.value = (cfg.routes || cfg.routes_config || []).map(r => ({
        key: r.key || '',
        label: r.label || '',
        price: r.price ?? 0,
    }))
}

// ── API Calls ──────────────────────────────────────────────

async function fetchCurrent() {
    loading.value = true
    try {
        const { data } = await api.get('/admin/service/pricing/active')
        current.value = data
        loadError.value = ''
        // Generate version display dari updated_at atau uuid suffix
        if (data.updated_at) {
            currentVersion.value = new Date(data.updated_at).toLocaleDateString('id-ID', {
                day: '2-digit', month: '2-digit', year: '2-digit'
            })
        }
        applyConfig(data)
    } catch (e) {
        const status = e?.response?.status
        if (status === 503 || status === 404) {
            // Belum ada config — form kosong dengan default
            current.value = null
            showToast('info', 'Belum ada konfigurasi aktif. Isi form untuk membuat yang pertama.')
        } else {
            loadError.value = e?.response?.data?.detail || e.message
            showToast('error', 'Gagal memuat config: ' + loadError.value)
        }
    } finally {
        loading.value = false
    }
}

async function fetchByUuid(uuid) {
    loading.value = true
    try {
        const { data } = await api.get(`/admin/pricing/${uuid}`)
        current.value = data
        loadError.value = ''
        if (data.updated_at) {
            currentVersion.value = new Date(data.updated_at).toLocaleDateString('id-ID', {
                day: '2-digit', month: '2-digit', year: '2-digit'
            })
        }
        applyConfig(data)
    } catch (e) {
        current.value = null
        loadError.value = e?.response?.data?.detail || e.message
        showToast('error', 'Gagal memuat config: ' + loadError.value)
    } finally {
        loading.value = false
    }
}

function reload() {
    const uuid = route.query.uuid
    return uuid ? fetchByUuid(uuid) : fetchCurrent()
}

function goBack() {
    if (props.initialData) {
        emit('close')
    } else {
        router.push({ name: 'jasa-config-list' })
    }
}

function loadFromCurrent() {
    if (!current.value) return
    applyConfig(current.value)
    showToast('info', 'Form direset ke konfigurasi aktif.')
}

async function doSave() {
    if (!canSave.value) {
        confirmModal.show = false
        return
    }
    saving.value = true
    try {
        // Build brand_multiplier object dari brandList array
        const brand_multiplier = {}
        brandList.value.forEach(b => {
            if (b.key.trim()) {
                // Gunakan ?? 1.0 agar multiplier 0 tidak di-override
                brand_multiplier[b.key.trim()] = (b.multiplier !== undefined && b.multiplier !== null && b.multiplier !== '') 
                    ? Number(b.multiplier) 
                    : 1.0
            }
        })

        // Build addons_config — strip empty fields
        const addons_config = form.addons_config
            .filter(a => a.key.trim())
            .map(a => ({
                key: a.key.trim(),
                label: a.label || a.key,
                type: a.type || 'flat',
                price: Number(a.price ?? 0),
                ...(a.icon && { icon: a.icon }),
                ...(a.description && { description: a.description }),
            }))

        // Build routes_config
        const routes_config = routeList.value
            .filter(r => r.key.trim())
            .map(r => ({
                key: r.key.trim(),
                label: r.label || r.key,
                price: Number(r.price ?? 0),
            }))

        // base_price_per_camera: konsultasi pakai consultation_fee
        const base_price_per_camera = {}
        const getNum = (val, def) => (val === '' || val === null || val === undefined) ? def : Number(val);

        CATEGORIES.forEach(c => {
            base_price_per_camera[c.id] = getNum(form.base_price_per_camera[c.id], 0)
        })

        const payload = {
            base_price_per_camera,
            brand_multiplier,
            consultation_fee: getNum(form.consultation_fee, 200_000),
            transport_per_km: getNum(form.transport_per_km, 5_000),
            transport_min_fee: getNum(form.transport_min_fee, 25_000),
            transport_max_fee: getNum(form.transport_max_fee, 300_000),
            max_distance_km: getNum(form.max_distance_km, 30.0),
            addons_config,
            routes_config,
            dp_percentage: getNum(form.dp_percentage, 50),
        }

        const endpoint = isEditMode.value
            ? `/admin/service/pricing/${route.query.uuid || props.initialData?.uuid}`
            : '/admin/service/pricing'
        
        const response = isEditMode.value 
            ? await api.patch(endpoint, payload)
            : await api.post(endpoint, payload)
            
        const data = response.data
        current.value = data
        applyConfig(data)

        if (data.updated_at) {
            currentVersion.value = new Date(data.updated_at).toLocaleDateString('id-ID', {
                day: '2-digit', month: '2-digit', year: '2-digit'
            })
        }

        confirmModal.show = false
        showToast('success', isEditMode.value ? 'Konfigurasi diperbarui!' : 'Konfigurasi baru disimpan!')
        
        if (!isEditMode.value && data.uuid) {
            router.replace({ name: 'jasa-configurasi', query: { uuid: data.uuid } })
        }

        emit('saved')
    } catch (e) {
        confirmModal.show = false
        const detail = e?.response?.data?.detail
        const msg = typeof detail === 'string'
            ? detail
            : Array.isArray(detail)
                ? detail.map(d => `${d.loc?.join('.')} - ${d.msg}`).join('; ')
                : (e.message || 'Terjadi kesalahan')
        showToast('error', 'Gagal menyimpan: ' + msg)
    } finally {
        saving.value = false
    }
}

// ── Brand helpers ──────────────────────────────────────────
function addBrand() {
    brandList.value.push({ key: '', multiplier: 1.0 })
}
function removeBrand(idx) {
    brandList.value.splice(idx, 1)
}

// ── Addon helpers ──────────────────────────────────────────
function addAddon() {
    form.addons_config.push({
        key: '', label: '', type: 'per_cam', price: 0, icon: '', description: ''
    })
}
function removeAddon(idx) {
    form.addons_config.splice(idx, 1)
}

function addRoute() {
    routeList.value.push({ key: '', label: '', price: 0 })
}

function removeRoute(idx) {
    routeList.value.splice(idx, 1)
}


</script>