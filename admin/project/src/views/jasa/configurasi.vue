<!-- pages/admin/pricing.vue -->
<template>
    <div class="min-h-screen bg-[#F4F3EF] font-['Geist',sans-serif]">

        <!-- ── Google Fonts ────────────────────────────────────── -->
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
            href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800;900&family=Geist+Mono:wght@400;500;600;700&display=swap"
            rel="stylesheet" />

        <!-- ══════════════════════════════════════════════════════ -->
        <!-- TOAST                                                 -->
        <!-- ══════════════════════════════════════════════════════ -->
        <Teleport to="body">
            <Transition name="toast">
                <div v-if="toast.show" :class="[
                    'fixed top-5 right-5 z-[9999] flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl text-sm font-semibold',
                    toast.type === 'success' ? 'bg-emerald-600 text-white'
                        : toast.type === 'info' ? 'bg-stone-800 text-white'
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
                    <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="confirmModal.show = false" />
                    <div class="relative bg-white rounded-2xl shadow-2xl p-7 w-full max-w-sm">
                        <div class="w-12 h-12 bg-amber-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <svg class="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                        </div>
                        <h3 class="text-center font-bold text-stone-900 mb-2">Simpan Konfigurasi Baru?</h3>
                        <p class="text-center text-sm text-stone-500 mb-6 leading-relaxed">
                            Konfigurasi lama akan <span class="font-semibold text-stone-700">dinonaktifkan</span> dan
                            diganti yang baru. Versi lama tetap tersimpan sebagai audit trail.
                        </p>
                        <div class="flex gap-3">
                            <button @click="confirmModal.show = false"
                                class="flex-1 py-2.5 rounded-xl border border-stone-200 text-sm font-semibold text-stone-600 hover:bg-stone-50 transition active:scale-95">
                                Batal
                            </button>
                            <button @click="doSave" :disabled="saving"
                                class="flex-1 py-2.5 rounded-xl bg-stone-900 hover:bg-stone-700 text-white text-sm font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2 active:scale-95">
                                <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                        stroke-width="4" />
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                                </svg>
                                {{ saving ? 'Menyimpan…' : 'Ya, Simpan' }}
                            </button>
                        </div>
                    </div>
                </div>
            </Transition>
        </Teleport>

        <!-- ══════════════════════════════════════════════════════ -->
        <!-- HEADER BAND                                           -->
        <!-- ══════════════════════════════════════════════════════ -->
        <div class="bg-stone-900 text-white px-6 py-6">
            <div class="max-w-5xl mx-auto flex items-center justify-between gap-4">
                <div>
                    <p class="text-[10px] tracking-[0.3em] uppercase text-stone-400 font-medium mb-1">Admin · Padjajaran
                        CCTV</p>
                    <h1 class="text-2xl font-black tracking-tight leading-none">Pricing Configuration</h1>
                </div>
                <div class="flex items-center gap-3">
                    <!-- Active config badge -->
                    <div v-if="current && !loading"
                        class="hidden sm:flex items-center gap-2 bg-stone-800 border border-stone-700 rounded-xl px-3 py-2">
                        <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span class="text-xs text-stone-300 font-medium">Config Aktif</span>
                        <span class="font-mono text-xs text-stone-400">v{{ currentVersion }}</span>
                    </div>
                    <button @click="fetchCurrent" :disabled="loading"
                        class="w-9 h-9 flex items-center justify-center rounded-xl bg-stone-800 hover:bg-stone-700 border border-stone-700 text-stone-400 hover:text-white transition disabled:opacity-50 active:scale-95">
                        <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor"
                            viewBox="0 0 24 24" stroke-width="2.5">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <!-- ══════════════════════════════════════════════════════ -->
        <!-- LOADING                                               -->
        <!-- ══════════════════════════════════════════════════════ -->
        <div v-if="loading" class="max-w-5xl mx-auto px-6 py-12 flex flex-col items-center gap-4">
            <div class="w-8 h-8 rounded-full border-2 border-stone-300 border-t-stone-700 animate-spin" />
            <p class="text-xs tracking-widest text-stone-400 uppercase">Memuat konfigurasi aktif...</p>
        </div>

        <!-- ══════════════════════════════════════════════════════ -->
        <!-- MAIN FORM                                             -->
        <!-- ══════════════════════════════════════════════════════ -->
        <div v-else class="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">

            <!-- Info banner jika belum ada config -->
            <div v-if="!current" class="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex gap-3">
                <svg class="w-5 h-5 text-amber-500 shrink-0 mt-0.5" fill="none" stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                    <p class="text-sm font-bold text-amber-800">Belum ada konfigurasi aktif</p>
                    <p class="text-xs text-amber-700 mt-0.5">Isi form di bawah dan simpan untuk membuat konfigurasi
                        pertama.</p>
                </div>
            </div>

            <!-- ══ SECTION 1: Harga Dasar per Kamera ══════════════ -->
            <section class="bg-white rounded-2xl border border-stone-200 overflow-hidden shadow-sm">
                <div class="px-5 py-4 border-b border-stone-100 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div>
                            <p class="font-bold text-stone-900 text-sm">Harga Dasar per Kamera</p>
                            <p class="text-xs text-stone-400">Biaya jasa per titik kamera (Rp)</p>
                        </div>
                    </div>
                </div>
                <div class="p-5 grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div v-for="cat in CATEGORIES" :key="cat.id">
                        <label class="block text-[10px] font-black tracking-[0.15em] uppercase text-stone-400 mb-1.5">{{
                            cat.label }}</label>
                        <div class="relative">
                            <span
                                class="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-stone-400 font-mono select-none">Rp</span>
                            <input v-model.number="form.base_price_per_camera[cat.id]" type="number" min="0" step="1000"
                                class="w-full pl-8 pr-3 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-sm font-mono text-stone-800 focus:outline-none focus:bg-white focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition" />
                        </div>
                    </div>
                </div>
            </section>

            <!-- ══ SECTION 2: Brand & Multiplier ══════════════════ -->
            <section class="bg-white rounded-2xl border border-stone-200 overflow-hidden shadow-sm">
                <div class="px-5 py-4 border-b border-stone-100 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-xl bg-violet-600 flex items-center justify-center">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                            </svg>
                        </div>
                        <div>
                            <p class="font-bold text-stone-900 text-sm">Brand & Multiplier</p>
                            <p class="text-xs text-stone-400">Faktor pengali harga berdasarkan merek kamera</p>
                        </div>
                    </div>
                    <button @click="addBrand"
                        class="flex items-center gap-1.5 text-xs font-semibold text-violet-600 bg-violet-50 hover:bg-violet-100 px-3 py-1.5 rounded-lg transition active:scale-95">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                            stroke-width="2.5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
                        </svg>
                        Tambah Brand
                    </button>
                </div>
                <div class="p-5 space-y-2">
                    <div v-for="(brand, idx) in brandList" :key="idx"
                        class="flex items-center gap-3 p-3 bg-stone-50 rounded-xl border border-stone-100">
                        <div class="flex-1 grid grid-cols-2 gap-3">
                            <div>
                                <label
                                    class="block text-[10px] font-bold tracking-widest uppercase text-stone-400 mb-1">Brand
                                    Key</label>
                                <input v-model="brand.key" type="text" placeholder="hikvision"
                                    class="w-full px-3 py-2 bg-white border border-stone-200 rounded-lg text-sm font-mono text-stone-700 focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition lowercase"
                                    @input="brand.key = brand.key.toLowerCase().replace(/\s+/g, '')" />
                            </div>
                            <div>
                                <label
                                    class="block text-[10px] font-bold tracking-widest uppercase text-stone-400 mb-1">Multiplier</label>
                                <input v-model.number="brand.multiplier" type="number" min="0.1" max="10" step="0.1"
                                    class="w-full px-3 py-2 bg-white border border-stone-200 rounded-lg text-sm font-mono text-stone-700 focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition" />
                            </div>
                        </div>
                        <div class="flex flex-col items-center gap-1">
                            <!-- Multiplier visual badge -->
                            <span :class="[
                                'text-[10px] font-black px-2 py-0.5 rounded-md',
                                brand.multiplier === 1.0 ? 'bg-stone-100 text-stone-500'
                                    : brand.multiplier > 1.0 ? 'bg-amber-100 text-amber-700'
                                        : 'bg-emerald-100 text-emerald-700'
                            ]">×{{ brand.multiplier?.toFixed(1) }}</span>
                            <button @click="removeBrand(idx)"
                                class="p-1.5 text-stone-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                                    stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    <p v-if="brandList.length === 0" class="text-center text-xs text-stone-400 py-4 italic">Belum ada
                        brand. Klik "Tambah Brand".</p>
                </div>
            </section>

            <!-- ══ SECTION 3: Transport & Jarak ══════════════════ -->
            <section class="bg-white rounded-2xl border border-stone-200 overflow-hidden shadow-sm">
                <div class="px-5 py-4 border-b border-stone-100 flex items-center gap-3">
                    <div class="w-8 h-8 rounded-xl bg-emerald-600 flex items-center justify-center">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0zM15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    </div>
                    <div>
                        <p class="font-bold text-stone-900 text-sm">Biaya Transport & Jarak</p>
                        <p class="text-xs text-stone-400">Aturan perhitungan ongkos kirim teknisi</p>
                    </div>
                </div>
                <div class="p-5 grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div>
                        <label class="field-label">Per KM (Rp)</label>
                        <div class="relative">
                            <span class="abs-prefix">Rp</span>
                            <input v-model.number="form.transport_per_km" type="number" min="0" step="500"
                                class="field-input pl-8" />
                        </div>
                    </div>
                    <div>
                        <label class="field-label">Min. Fee (Rp)</label>
                        <div class="relative">
                            <span class="abs-prefix">Rp</span>
                            <input v-model.number="form.transport_min_fee" type="number" min="0" step="1000"
                                class="field-input pl-8" />
                        </div>
                    </div>
                    <div>
                        <label class="field-label">Max. Fee (Rp)</label>
                        <div class="relative">
                            <span class="abs-prefix">Rp</span>
                            <input v-model.number="form.transport_max_fee" type="number" min="0" step="5000"
                                class="field-input pl-8" />
                        </div>
                    </div>
                    <div>
                        <label class="field-label">Max Jarak (KM)</label>
                        <div class="relative">
                            <input v-model.number="form.max_distance_km" type="number" min="1" max="100" step="1"
                                class="field-input pr-10" />
                            <span
                                class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-stone-400 font-mono select-none">km</span>
                        </div>
                    </div>
                </div>
                <!-- Transport preview -->
                <div class="mx-5 mb-5 p-3 bg-stone-50 rounded-xl border border-stone-100">
                    <p class="text-[10px] font-black uppercase tracking-widest text-stone-400 mb-2">Preview Kalkulasi
                    </p>
                    <div class="flex flex-wrap gap-x-6 gap-y-1 text-xs text-stone-600">
                        <span>5 km → <span class="font-mono font-bold text-stone-800">{{ previewTransport(5)
                                }}</span></span>
                        <span>10 km → <span class="font-mono font-bold text-stone-800">{{ previewTransport(10)
                                }}</span></span>
                        <span>20 km → <span class="font-mono font-bold text-stone-800">{{ previewTransport(20)
                                }}</span></span>
                        <span>30 km → <span class="font-mono font-bold text-stone-800">{{ previewTransport(30)
                                }}</span></span>
                    </div>
                </div>
            </section>

            <!-- ══ SECTION 4: Konsultasi & DP ════════════════════ -->
            <section class="bg-white rounded-2xl border border-stone-200 overflow-hidden shadow-sm">
                <div class="px-5 py-4 border-b border-stone-100 flex items-center gap-3">
                    <div class="w-8 h-8 rounded-xl bg-amber-500 flex items-center justify-center">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z" />
                        </svg>
                    </div>
                    <div>
                        <p class="font-bold text-stone-900 text-sm">Konsultasi & Down Payment</p>
                        <p class="text-xs text-stone-400">Biaya konsultasi flat + persentase DP</p>
                    </div>
                </div>
                <div class="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label class="field-label">Biaya Konsultasi (Rp)</label>
                        <div class="relative">
                            <span class="abs-prefix">Rp</span>
                            <input v-model.number="form.consultation_fee" type="number" min="0" step="10000"
                                class="field-input pl-8" />
                        </div>
                        <p class="text-xs text-stone-400 mt-1.5">Flat fee untuk kategori "Konsultasi & Survey"</p>
                    </div>
                    <div>
                        <label class="field-label">Persentase DP (%)</label>
                        <div class="relative">
                            <input v-model.number="form.dp_percentage" type="number" min="10" max="100" step="5"
                                class="field-input pr-8" />
                            <span
                                class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-stone-400 font-mono select-none">%</span>
                        </div>
                        <!-- DP slider visual -->
                        <div class="mt-2.5">
                            <div class="flex justify-between text-[10px] text-stone-400 mb-1">
                                <span>10%</span><span>50%</span><span>100%</span>
                            </div>
                            <div class="relative h-1.5 bg-stone-100 rounded-full overflow-hidden">
                                <div class="absolute inset-y-0 left-0 bg-amber-500 rounded-full transition-all"
                                    :style="`width: ${((form.dp_percentage - 10) / 90) * 100}%`" />
                            </div>
                            <p class="text-xs text-stone-500 mt-1.5">
                                Untuk total <span class="font-mono font-bold">Rp 2.000.000</span> →
                                DP = <span class="font-mono font-bold text-amber-700">{{ fmt(2000000 *
                                    form.dp_percentage / 100) }}</span>,
                                sisa = <span class="font-mono font-bold text-stone-700">{{ fmt(2000000 - 2000000 *
                                    form.dp_percentage / 100) }}</span>
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- ══ SECTION 5: Addons ══════════════════════════════ -->
            <section class="bg-white rounded-2xl border border-stone-200 overflow-hidden shadow-sm">
                <div class="px-5 py-4 border-b border-stone-100 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-xl bg-rose-500 flex items-center justify-center">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                            </svg>
                        </div>
                        <div>
                            <p class="font-bold text-stone-900 text-sm">Addons / Layanan Tambahan</p>
                            <p class="text-xs text-stone-400">Opsi tambahan yang bisa dipilih pelanggan saat booking</p>
                        </div>
                    </div>
                    <button @click="addAddon"
                        class="flex items-center gap-1.5 text-xs font-semibold text-rose-600 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-lg transition active:scale-95">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                            stroke-width="2.5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
                        </svg>
                        Tambah Addon
                    </button>
                </div>
                <div class="p-5 space-y-3">
                    <div v-if="form.addons_config.length === 0"
                        class="text-center py-8 border-2 border-dashed border-stone-100 rounded-xl">
                        <p class="text-sm text-stone-400">Belum ada addon. Klik "Tambah Addon".</p>
                    </div>

                    <div v-for="(addon, idx) in form.addons_config" :key="idx"
                        class="border border-stone-100 rounded-xl overflow-hidden">
                        <!-- Addon header bar -->
                        <div
                            class="bg-stone-50 px-4 py-2.5 flex items-center justify-between border-b border-stone-100">
                            <div class="flex items-center gap-2.5">
                                <span
                                    class="w-5 h-5 bg-white border border-stone-200 rounded-md flex items-center justify-center text-[10px] font-black text-stone-500">{{
                                    idx + 1 }}</span>
                                <span class="text-xs font-bold text-stone-600 font-mono">{{ addon.key || 'addon-key'
                                    }}</span>
                                <span :class="[
                                    'text-[10px] font-bold px-2 py-0.5 rounded',
                                    addon.type === 'per_cam' ? 'bg-blue-100 text-blue-700' : 'bg-teal-100 text-teal-700'
                                ]">{{ addon.type === 'per_cam' ? 'per kamera' : 'flat' }}</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="text-xs font-mono font-bold text-stone-700">{{ fmt(addon.price || 0)
                                    }}</span>
                                <button @click="removeAddon(idx)"
                                    class="p-1 text-stone-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                                        stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round"
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                        <!-- Addon fields -->
                        <div class="p-4 grid grid-cols-2 sm:grid-cols-3 gap-3">
                            <div>
                                <label class="field-label">Key *</label>
                                <input v-model="addon.key" type="text" placeholder="conduit_kabel"
                                    class="field-input font-mono text-xs"
                                    @input="addon.key = addon.key.toLowerCase().replace(/\s+/g, '_')" />
                            </div>
                            <div>
                                <label class="field-label">Label (tampilan)</label>
                                <input v-model="addon.label" type="text" placeholder="Conduit Kabel"
                                    class="field-input" />
                            </div>
                            <div>
                                <label class="field-label">Tipe</label>
                                <select v-model="addon.type" class="field-input cursor-pointer">
                                    <option value="per_cam">per_cam (×jumlah kamera)</option>
                                    <option value="flat">flat (biaya tetap)</option>
                                </select>
                            </div>
                            <div>
                                <label class="field-label">Harga (Rp)</label>
                                <div class="relative">
                                    <span class="abs-prefix">Rp</span>
                                    <input v-model.number="addon.price" type="number" min="0" step="5000"
                                        class="field-input pl-8 font-mono" />
                                </div>
                            </div>
                            <div>
                                <label class="field-label">Icon (nama heroicon)</label>
                                <input v-model="addon.icon" type="text" placeholder="wrench-screwdriver"
                                    class="field-input text-xs" />
                            </div>
                            <div>
                                <label class="field-label">Deskripsi</label>
                                <input v-model="addon.description" type="text" placeholder="Pemasangan conduit…"
                                    class="field-input text-xs" />
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- ══ PREVIEW RINGKASAN ══════════════════════════════ -->
            <section class="bg-stone-900 rounded-2xl overflow-hidden shadow-sm text-white">
                <div class="px-5 py-4 border-b border-stone-800 flex items-center gap-3">
                    <div class="w-8 h-8 rounded-xl bg-stone-700 flex items-center justify-center">
                        <svg class="w-4 h-4 text-stone-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                    </div>
                    <div>
                        <p class="font-bold text-sm">Ringkasan Config</p>
                        <p class="text-xs text-stone-400">Pratinjau sebelum disimpan</p>
                    </div>
                </div>
                <div class="p-5 grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div v-for="cat in CATEGORIES" :key="cat.id">
                        <p class="text-[10px] uppercase tracking-widest text-stone-500 mb-1">{{ cat.label }}</p>
                        <p class="font-mono font-bold text-sm">{{ fmt(form.base_price_per_camera[cat.id] || 0) }}</p>
                        <p class="text-[10px] text-stone-500 mt-0.5">per titik</p>
                    </div>
                </div>
                <div class="px-5 pb-5 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-stone-800 pt-4">
                    <div>
                        <p class="text-[10px] uppercase tracking-widest text-stone-500 mb-1">Transport/km</p>
                        <p class="font-mono font-bold text-sm">{{ fmt(form.transport_per_km) }}</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase tracking-widest text-stone-500 mb-1">Max Jarak</p>
                        <p class="font-mono font-bold text-sm">{{ form.max_distance_km }} km</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase tracking-widest text-stone-500 mb-1">DP</p>
                        <p class="font-mono font-bold text-sm text-amber-400">{{ form.dp_percentage }}%</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase tracking-widest text-stone-500 mb-1">Addons</p>
                        <p class="font-mono font-bold text-sm">{{ form.addons_config.length }} item</p>
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
                    <button @click="confirmModal.show = true" :disabled="saving || !isValid"
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
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/service/api'

// ── Constants ──────────────────────────────────────────────
const CATEGORIES = [
    { id: 'installation', label: 'Pemasangan' },
    { id: 'maintenance', label: 'Servis' },
    { id: 'troubleshoot', label: 'Troubleshoot' },
    { id: 'consultation', label: 'Konsultasi' },
]

// ── State ──────────────────────────────────────────────────
const loading = ref(true)
const saving = ref(false)
const current = ref(null)       // config aktif dari backend
const currentVersion = ref('1') // versi display

const toast = reactive({ show: false, type: 'success', message: '' })
let toastTimer = null

const confirmModal = reactive({ show: false })

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
    dp_percentage: 50,
})

// Brand list sebagai array untuk UI (di-convert ke object saat save)
const brandList = ref([])

// ── Computed ───────────────────────────────────────────────
const formErrors = computed(() => {
    const errs = []
    CATEGORIES.forEach(c => {
        if (!form.base_price_per_camera[c.id] || form.base_price_per_camera[c.id] < 0)
            errs.push(`Harga "${c.label}" harus diisi dan >= 0`)
    })
    if (form.dp_percentage < 10 || form.dp_percentage > 100)
        errs.push('DP harus antara 10% – 100%')
    if (form.max_distance_km < 1 || form.max_distance_km > 400)
        errs.push('Max jarak harus antara 1 – 400 km')
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
        price: a.price || 0,
        icon: a.icon || '',
        description: a.description || '',
    }))
}

// ── API Calls ──────────────────────────────────────────────

async function fetchCurrent() {
    loading.value = true
    try {
        const { data } = await api.get('/admin/service/pricing/active')
        current.value = data
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
            showToast('error', 'Gagal memuat config: ' + (e?.response?.data?.detail || e.message))
        }
    } finally {
        loading.value = false
    }
}

function loadFromCurrent() {
    if (!current.value) return
    applyConfig(current.value)
    showToast('info', 'Form direset ke konfigurasi aktif.')
}

async function doSave() {
    if (!isValid.value) {
        confirmModal.show = false
        return
    }
    saving.value = true
    try {
        // Build brand_multiplier object dari brandList array
        const brand_multiplier = {}
        brandList.value.forEach(b => {
            if (b.key.trim()) {
                brand_multiplier[b.key.trim()] = Number(b.multiplier) || 1.0
            }
        })

        // Build addons_config — strip empty fields
        const addons_config = form.addons_config
            .filter(a => a.key.trim())
            .map(a => ({
                key: a.key.trim(),
                label: a.label || a.key,
                type: a.type || 'flat',
                price: Number(a.price) || 0,
                ...(a.icon && { icon: a.icon }),
                ...(a.description && { description: a.description }),
            }))

        // base_price_per_camera: konsultasi pakai consultation_fee
        const base_price_per_camera = {}
        CATEGORIES.forEach(c => {
            base_price_per_camera[c.id] =
                c.id === 'consultation'
                    ? Number(form.consultation_fee) || 200_000
                    : Number(form.base_price_per_camera[c.id]) || 0
        })

        const payload = {
            base_price_per_camera,
            brand_multiplier,
            consultation_fee: Number(form.consultation_fee) || 200_000,
            transport_per_km: Number(form.transport_per_km) || 5_000,
            transport_min_fee: Number(form.transport_min_fee) || 25_000,
            transport_max_fee: Number(form.transport_max_fee) || 300_000,
            max_distance_km: Number(form.max_distance_km) || 30.0,
            addons_config,
            dp_percentage: Number(form.dp_percentage) || 50,
        }

        const { data } = await api.post('/admin/service/pricing', payload)
        current.value = data
        if (data.updated_at) {
            currentVersion.value = new Date(data.updated_at).toLocaleDateString('id-ID', {
                day: '2-digit', month: '2-digit', year: '2-digit'
            })
        }
        confirmModal.show = false
        showToast('success', 'Konfigurasi pricing berhasil disimpan dan diaktifkan!')
    } catch (e) {
        confirmModal.show = false
        const detail = e?.response?.data?.detail
        const msg = typeof detail === 'string'
            ? detail
            : Array.isArray(detail)
                ? detail.map(d => `${d.loc?.join('.')} — ${d.msg}`).join('; ')
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

// ── Init ───────────────────────────────────────────────────
onMounted(fetchCurrent)
</script>