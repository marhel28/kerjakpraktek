<template>
    <div class="min-h-screen bg-[#F0F0EB] font-sans">

        <!-- ── Toast ──────────────────────────────────────────────── -->
        <Transition name="toast">
            <div v-if="toast.show" :class="[
                'fixed top-5 right-5 z-[100] flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-xl text-sm font-semibold backdrop-blur-sm',
                toast.type === 'success' ? 'bg-emerald-600 text-white'
                    : toast.type === 'info' ? 'bg-slate-800 text-white'
                        : 'bg-red-600 text-white',
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
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
                </svg>
                {{ toast.message }}
            </div>
        </Transition>

        <!-- ── Delete Confirm Modal ───────────────────────────────── -->
        <Transition name="modal">
            <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="deleteModal.show = false" />
                <div class="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm">
                    <div class="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </div>
                    <h3 class="text-center font-bold text-slate-800 mb-1">Hapus Paket?</h3>
                    <p class="text-center text-sm text-slate-500 mb-6">
                        <span class="font-medium text-slate-700">{{ deleteModal.name }}</span> akan dihapus permanen dan
                        tidak bisa dikembalikan.
                    </p>
                    <div class="flex gap-3">
                        <button @click="deleteModal.show = false"
                            class="flex-1 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition">
                            Batal
                        </button>
                        <button @click="confirmDelete" :disabled="deleting"
                            class="flex-1 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-sm font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2">
                            <svg v-if="deleting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4" />
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                            </svg>
                            {{ deleting ? 'Menghapus…' : 'Hapus' }}
                        </button>
                    </div>
                </div>
            </div>
        </Transition>

        <!-- ── Package Form Modal (Create / Edit) ────────────────── -->
        <Transition name="modal">
            <div v-if="formModal.show" class="fixed inset-0 z-50 flex items-start justify-center p-4 overflow-y-auto">
                <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeFormModal" />
                <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl my-6">

                    <!-- Modal Header -->
                    <div class="flex items-center justify-between px-6 pt-5 pb-4 border-b border-slate-100">
                        <div>
                            <h2 class="font-bold text-slate-900 text-base">
                                {{ formModal.mode === 'create' ? 'Buat Paket Baru' : 'Edit Paket' }}
                            </h2>
                            <p class="text-xs text-slate-400 mt-0.5">
                                {{ formModal.mode === 'create' ? 'Tambah paket CCTV + bundle barang' : 'Update metadatapaket' }}
                            </p>
                        </div>
                        <button @click="closeFormModal"
                            class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <!-- Modal Body -->
                    <div class="p-6 space-y-5">

                        <!-- ─ Info Dasar ─────────────────────────────────── -->
                        <div class="space-y-3">
                            <p class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Informasi Dasar
                            </p>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div class="sm:col-span-2">
                                    <label class="field-label">Nama Paket *</label>
                                    <input v-model="pkgForm.name" type="text"
                                        placeholder="Paket Premium Bisnis 8 Titik (Hikvision)" class="field-input"
                                        @input="autoSlug" />
                                </div>
                                <div>
                                    <label class="field-label">Slug *</label>
                                    <input v-model="pkgForm.slug" type="text" placeholder="paket-premium-bisnis-8-titik"
                                        class="field-input font-mono text-xs" />
                                    <p v-if="slugError" class="text-xs text-red-500 mt-1">{{ slugError }}</p>
                                </div>
                                <div>
                                    <label class="field-label">Kategori *</label>
                                    <select v-model="pkgForm.category" class="field-input">
                                        <option v-for="c in CATEGORIES" :key="c.id" :value="c.id">{{ c.label }}</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="field-label">Brand Default *</label>
                                    <select v-model="pkgForm.default_brand" class="field-input">
                                        <option v-for="b in BRANDS" :key="b" :value="b">{{ capitalize(b) }}</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="field-label">Jumlah Kamera *</label>
                                    <input v-model.number="pkgForm.camera_count" type="number" min="1" max="200"
                                        class="field-input font-mono" />
                                </div>
                                <div class="sm:col-span-2">
                                    <label class="field-label">Deskripsi</label>
                                    <textarea v-model="pkgForm.description" rows="2"
                                        placeholder="Solusi keamanan untuk…" class="field-input resize-none" />
                                </div>
                                <div class="sm:col-span-2">
                                    <label class="field-label">Thumbnail URL</label>
                                    <input v-model="pkgForm.thumbnail_url" type="url" placeholder="https://…"
                                        class="field-input" />
                                </div>
                            </div>
                        </div>

                        <!-- ─ Highlights ─────────────────────────────────── -->
                        <div class="space-y-2">
                            <div class="flex items-center justify-between">
                                <p class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Highlights</p>
                                <button @click="addHighlight"
                                    class="text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 px-2.5 py-1 rounded-lg transition">
                                    + Tambah
                                </button>
                            </div>
                            <div v-for="(h, i) in pkgForm.highlights" :key="i" class="flex items-center gap-2">
                                <input v-model="pkgForm.highlights[i]" type="text" placeholder="Fitur unggulan…"
                                    class="flex-1 px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition" />
                                <button @click="removeHighlight(i)"
                                    class="p-1.5 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                            <p v-if="pkgForm.highlights.length === 0" class="text-xs text-slate-400 italic">Belum ada
                                highlight.</p>
                        </div>

                        <!-- ─ Items (Stock Bundle) ────────────────────────── -->
                        <div v-if="formModal.mode === 'create'" class="space-y-2">
                            <div class="flex items-center justify-between">
                                <div>
                                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Item /
                                        Bundle Barang</p>
                                    <p class="text-xs text-slate-400 mt-0.5">Gunakan UUID dari data Stock</p>
                                </div>
                                <button @click="addItem"
                                    class="text-xs font-medium text-violet-600 hover:text-violet-700 bg-violet-50 hover:bg-violet-100 px-2.5 py-1 rounded-lg transition">
                                    + Tambah Item
                                </button>
                            </div>
                            <div v-if="pkgForm.items.length === 0"
                                class="text-center py-6 border-2 border-dashed border-slate-200 rounded-xl text-sm text-slate-400">
                                Belum ada item. Klik "+ Tambah Item".
                            </div>
                            <div v-for="(item, idx) in pkgForm.items" :key="idx"
                                class="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-2">
                                <div class="flex items-center justify-between mb-1">
                                    <span class="text-xs font-semibold text-slate-500">Item #{{ idx + 1 }}</span>
                                    <button @click="removeItem(idx)"
                                        class="p-1 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                                <div class="grid grid-cols-2 gap-2">
                                    <div class="col-span-2">
                                        <label class="text-xs text-slate-400 mb-0.5 block">Stock UUID *</label>
                                        <input v-model="item.stock_uuid" type="text"
                                            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                                            class="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition font-mono" />
                                    </div>
                                    <div>
                                        <label class="text-xs text-slate-400 mb-0.5 block">Label</label>
                                        <input v-model="item.label" type="text" placeholder="Kamera Utama"
                                            class="w-full px-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition" />
                                    </div>
                                    <div>
                                        <label class="text-xs text-slate-400 mb-0.5 block">Qty</label>
                                        <input v-model.number="item.quantity" type="number" min="1"
                                            class="w-full px-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition font-mono" />
                                    </div>
                                    <div>
                                        <label class="text-xs text-slate-400 mb-0.5 block">Override Price <span
                                                class="text-slate-300">(opsional)</span></label>
                                        <div class="relative">
                                            <span
                                                class="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-slate-400">Rp</span>
                                            <input v-model.number="item.override_price" type="number" min="0"
                                                placeholder="0"
                                                class="w-full pl-8 pr-2 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition font-mono" />
                                        </div>
                                    </div>
                                    <div>
                                        <label class="text-xs text-slate-400 mb-0.5 block">Sort Order</label>
                                        <input v-model.number="item.sort_order" type="number" min="0"
                                            class="w-full px-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition font-mono" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- ─ Opsi Tambahan ──────────────────────────────── -->
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="field-label">Sort Order</label>
                                <input v-model.number="pkgForm.sort_order" type="number" min="0"
                                    class="field-input font-mono" />
                            </div>
                            <div class="flex items-end pb-1">
                                <label class="flex items-center gap-2.5 cursor-pointer select-none">
                                    <div class="relative">
                                        <input type="checkbox" v-model="pkgForm.is_active" class="sr-only" />
                                        <div :class="[
                                            'w-10 h-6 rounded-full transition-colors',
                                            pkgForm.is_active ? 'bg-emerald-500' : 'bg-slate-300'
                                        ]" />
                                        <div :class="[
                                            'absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform',
                                            pkgForm.is_active ? 'translate-x-4' : 'translate-x-0'
                                        ]" />
                                    </div>
                                    <span class="text-sm font-medium text-slate-700">Aktif</span>
                                </label>
                            </div>
                        </div>

                    </div>

                    <!-- Modal Footer -->
                    <div class="px-6 pb-5 flex items-center justify-between gap-3 border-t border-slate-100 pt-4">
                        <p v-if="formError" class="text-xs text-red-500 flex-1">{{ formError }}</p>
                        <div class="flex gap-3 ml-auto">
                            <button @click="closeFormModal"
                                class="px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition">
                                Batal
                            </button>
                            <button @click="submitForm" :disabled="submitting"
                                class="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-700 text-white text-sm font-semibold transition disabled:opacity-50 flex items-center gap-2">
                                <svg v-if="submitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                        stroke-width="4" />
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                                </svg>
                                {{ submitting ? 'Menyimpan…' : formModal.mode === 'create' ? 'Buat Paket' : 'Simpan Perubahan' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>

        <!-- ── Main Content ───────────────────────────────────────── -->
        <div class="max-w-6xl mx-auto px-5 py-10">

            <!-- Header -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
                <div>
                    <div class="flex items-center gap-2.5 mb-1">
                        <div class="w-8 h-8 bg-slate-900 rounded-xl flex items-center justify-center">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                            </svg>
                        </div>
                        <h1 class="text-xl font-bold text-slate-900 tracking-tight">Manajemen Paket CCTV</h1>
                    </div>
                    <p class="text-sm text-slate-500 ml-10.5">Bundle kamera + jasa pemasangan siap pesan</p>
                </div>
                <div class="flex items-center gap-3">
                    <!-- Filter kategori -->
                    <select v-model="filterCategory"
                        class="text-sm bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900 transition shadow-sm">
                        <option value="">Semua Kategori</option>
                        <option v-for="c in CATEGORIES" :key="c.id" :value="c.id">{{ c.label }}</option>
                    </select>
                    <!-- Toggle aktif -->
                    <label
                        class="flex items-center gap-2 text-sm text-slate-600 bg-white border border-slate-200 rounded-xl px-3 py-2 cursor-pointer shadow-sm">
                        <input type="checkbox" v-model="showInactive" class="rounded" />
                        Non-aktif
                    </label>
                    <!-- Tambah paket -->
                    <button @click="openCreateModal"
                        class="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-700 text-white text-sm font-semibold rounded-xl transition shadow-sm hover:shadow active:scale-95">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
                                d="M12 4v16m8-8H4" />
                        </svg>
                        Buat Paket
                    </button>
                </div>
            </div>

            <!-- Stats Row -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
                <div v-for="stat in stats" :key="stat.label"
                    class="bg-white rounded-2xl shadow-sm p-4 flex items-center gap-3">
                    <div :class="['w-9 h-9 rounded-xl flex items-center justify-center shrink-0', stat.bg]">
                        <svg class="w-4.5 h-4.5" :class="stat.color" fill="none" stroke="currentColor"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.icon" />
                        </svg>
                    </div>
                    <div>
                        <p class="text-lg font-bold text-slate-900 leading-none">{{ stat.value }}</p>
                        <p class="text-xs text-slate-400 mt-0.5">{{ stat.label }}</p>
                    </div>
                </div>
            </div>

            <!-- Loading Skeleton -->
            <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="n in 6" :key="n" class="bg-white rounded-2xl p-5 shadow-sm animate-pulse space-y-3">
                    <div class="h-36 bg-slate-100 rounded-xl" />
                    <div class="h-4 bg-slate-100 rounded w-3/4" />
                    <div class="h-3 bg-slate-100 rounded w-1/2" />
                    <div class="flex gap-2 pt-2">
                        <div class="h-8 bg-slate-100 rounded-lg flex-1" />
                        <div class="h-8 bg-slate-100 rounded-lg w-8" />
                    </div>
                </div>
            </div>

            <!-- Empty state -->
            <div v-else-if="filteredPackages.length === 0 && !loading"
                class="text-center py-20 bg-white rounded-2xl shadow-sm">
                <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                </div>
                <p class="font-semibold text-slate-700 mb-1">Belum ada paket</p>
                <p class="text-sm text-slate-400 mb-5">Buat paket CCTV pertama untuk ditampilkan ke pelanggan</p>
                <button @click="openCreateModal"
                    class="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-900 text-white text-sm font-semibold rounded-xl transition hover:bg-slate-700">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
                    </svg>
                    Buat Paket Pertama
                </button>
            </div>

            <!-- Package Grid -->
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="pkg in filteredPackages" :key="pkg.uuid" :class="[
                    'bg-white rounded-2xl shadow-sm overflow-hidden flex flex-col transition-all hover:shadow-md hover:-translate-y-0.5',
                    !pkg.is_active && 'opacity-60'
                ]">
                    <!-- Thumbnail -->
                    <div class="relative h-36 bg-slate-100 overflow-hidden">
                        <img v-if="pkg.thumbnail_url" :src="pkg.thumbnail_url" :alt="pkg.name"
                            class="w-full h-full object-cover" loading="lazy"
                            @error="e => e.target.style.display = 'none'" />
                        <div v-else class="w-full h-full flex items-center justify-center">
                            <svg class="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                    d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                        </div>
                        <!-- Badges -->
                        <div class="absolute top-2.5 left-2.5 flex gap-1.5">
                            <span :class="[
                                'text-xs font-semibold px-2 py-0.5 rounded-md',
                                CATEGORY_COLOR[pkg.category] || 'bg-slate-100 text-slate-600'
                            ]">
                                {{CATEGORIES.find(c => c.id === pkg.category)?.label || pkg.category}}
                            </span>
                        </div>
                        <div class="absolute top-2.5 right-2.5">
                            <span :class="[
                                'text-xs font-bold px-2 py-0.5 rounded-md',
                                pkg.is_active ? 'bg-emerald-500 text-white' : 'bg-slate-400 text-white'
                            ]">
                                {{ pkg.is_active ? 'Aktif' : 'Nonaktif' }}
                            </span>
                        </div>
                    </div>

                    <!-- Body -->
                    <div class="p-4 flex-1 flex flex-col">
                        <h3 class="font-bold text-slate-800 text-sm leading-tight mb-1 line-clamp-2">{{ pkg.name }}</h3>
                        <p class="text-xs text-slate-400 mb-3 line-clamp-2">{{ pkg.description || '—' }}</p>

                        <!-- Camera & Brand badges -->
                        <div class="flex items-center gap-1.5 flex-wrap mb-3">
                            <span
                                class="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-lg font-medium">
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M15 10l4.553-2.069A1 1 0 0121 8.82V15a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
                                </svg>
                                {{ pkg.camera_count }} Kamera
                            </span>
                            <span
                                class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-lg font-medium capitalize">
                                {{ pkg.default_brand }}
                            </span>
                        </div>

                        <!-- Pricing -->
                        <div class="bg-slate-50 rounded-xl p-3 mb-3 space-y-1">
                            <div class="flex justify-between items-center">
                                <span class="text-xs text-slate-500">Perangkat</span>
                                <span class="text-xs font-semibold text-slate-700 font-mono">{{
                                    formatRp(pkg.device_price) }}</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-xs text-slate-500">Est. Jasa</span>
                                <span class="text-xs font-semibold text-slate-700 font-mono">{{
                                    formatRp(pkg.estimated_service_price) }}</span>
                            </div>
                            <div class="border-t border-slate-200 pt-1 flex justify-between items-center">
                                <span class="text-xs font-bold text-slate-700">Total Estimasi</span>
                                <span class="text-sm font-bold text-slate-900 font-mono">{{
                                    formatRp(pkg.total_estimated) }}</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-xs text-emerald-600 font-semibold">DP ({{ dpPercentage }}%)</span>
                                <span class="text-xs font-bold text-emerald-700 font-mono">{{ formatRp(pkg.dp_amount)
                                }}</span>
                            </div>
                        </div>

                        <!-- Items summary -->
                        <div v-if="pkg.items && pkg.items.length" class="mb-3">
                            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Bundle Item
                            </p>
                            <div class="space-y-1">
                                <div v-for="item in pkg.items.slice(0, 3)" :key="item.uuid"
                                    class="flex items-center justify-between text-xs">
                                    <span class="text-slate-600 truncate max-w-[160px]">
                                        {{ item.label || item.stock_title }}
                                    </span>
                                    <span class="text-slate-400 font-mono shrink-0 ml-2">×{{ item.quantity }}</span>
                                </div>
                                <p v-if="pkg.items.length > 3" class="text-xs text-slate-400 italic">
                                    +{{ pkg.items.length - 3 }} item lainnya
                                </p>
                            </div>
                        </div>

                        <!-- Highlights -->
                        <div v-if="pkg.highlights && pkg.highlights.length" class="mb-4">
                            <div class="flex flex-wrap gap-1">
                                <span v-for="h in pkg.highlights.slice(0, 3)" :key="h"
                                    class="text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded-md">
                                    ✦ {{ h }}
                                </span>
                                <span v-if="pkg.highlights.length > 3" class="text-xs text-slate-400">+{{
                                    pkg.highlights.length - 3 }}</span>
                            </div>
                        </div>

                        <!-- Actions -->
                        <div class="flex gap-2 mt-auto">
                            <button @click="openEditModal(pkg)" :title="'Edit ' + pkg.name"
                                class="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                                Edit
                            </button>
                            <button @click="recalculate(pkg)" :disabled="recalcLoading === pkg.uuid"
                                :title="'Recalculate harga ' + pkg.name"
                                class="flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-blue-600 hover:bg-blue-50 transition disabled:opacity-50">
                                <svg :class="['w-3.5 h-3.5', recalcLoading === pkg.uuid && 'animate-spin']" fill="none"
                                    stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                            </button>
                            <button @click="toggleActive(pkg)" :title="pkg.is_active ? 'Nonaktifkan' : 'Aktifkan'"
                                :class="[
                                    'flex items-center justify-center px-3 py-2 rounded-xl border text-xs font-semibold transition',
                                    pkg.is_active
                                        ? 'border-slate-200 text-slate-400 hover:bg-slate-50'
                                        : 'border-emerald-200 text-emerald-600 hover:bg-emerald-50'
                                ]">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="pkg.is_active
                                        ? 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636'
                                        : 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'" />
                                </svg>
                            </button>
                            <button @click="promptDelete(pkg)"
                                class="flex items-center justify-center px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-red-400 hover:bg-red-50 hover:border-red-200 transition">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pagination hint -->
            <p v-if="packages.length > 0" class="text-center text-xs text-slate-400 mt-6">
                Menampilkan {{ filteredPackages.length }} dari {{ packages.length }} paket
            </p>

        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/service/api'

// ── Constants ──────────────────────────────────────────────────────

const CATEGORIES = [
    { id: 'installation', label: 'Pemasangan Baru' },
    { id: 'maintenance', label: 'Perbaikan & Service' },
    { id: 'consultation', label: 'Konsultasi' },
    { id: 'troubleshoot', label: 'Troubleshoot' },
]

const BRANDS = ['glenz', 'ezviz', 'dahua', 'tiandy', 'hikvision']

const CATEGORY_COLOR = {
    installation: 'bg-blue-100 text-blue-700',
    maintenance: 'bg-amber-100 text-amber-700',
    consultation: 'bg-teal-100 text-teal-700',
    troubleshoot: 'bg-rose-100 text-rose-700',
}

// Seeder default items (untuk quick-fill referensi UUID dari seeder)
const SEEDER_STOCK = {
    kamera_hkv: 'fe39bc24-edd2-4490-826b-fd2648376a0b',
    kamera_imou: '086f26c7-4c41-4acc-ba05-928f4b984e33',
    dvr_dahua: '713f829c-7be6-4ae1-a542-21f4368642ef',
    hdd_seagate: '81becc1d-782a-4c4e-91bd-3d2cd18ab234',
    kabel_belden: '39e8a45c-c158-4e6f-bc0b-6ccbd432e49a',
}

// ── State ──────────────────────────────────────────────────────────

const packages = ref([])
const loading = ref(true)
const filterCategory = ref('')
const showInactive = ref(false)
const dpPercentage = ref(30)   // dari pricing config aktif
const recalcLoading = ref(null)
const deleting = ref(false)
const submitting = ref(false)

const toast = reactive({ show: false, type: 'success', message: '' })
let toastTimer = null

const deleteModal = reactive({ show: false, uuid: null, name: '' })

const formModal = reactive({ show: false, mode: 'create' })  // mode: 'create' | 'edit'

const pkgForm = reactive({
    uuid: null,
    name: '',
    slug: '',
    description: '',
    category: 'installation',
    camera_count: 4,
    default_brand: 'hikvision',
    thumbnail_url: '',
    highlights: [],
    is_active: true,
    sort_order: 0,
    items: [],   // hanya untuk mode create
})

const formError = ref('')

// ── Computed ───────────────────────────────────────────────────────

const filteredPackages = computed(() => {
    return packages.value.filter(p => {
        if (!showInactive.value && !p.is_active) return false
        if (filterCategory.value && p.category !== filterCategory.value) return false
        return true
    })
})

const stats = computed(() => [
    {
        label: 'Total Paket',
        value: packages.value.length,
        bg: 'bg-slate-100', color: 'text-slate-600',
        icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
    },
    {
        label: 'Aktif',
        value: packages.value.filter(p => p.is_active).length,
        bg: 'bg-emerald-50', color: 'text-emerald-600',
        icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    },
    {
        label: 'Pemasangan',
        value: packages.value.filter(p => p.category === 'installation').length,
        bg: 'bg-blue-50', color: 'text-blue-600',
        icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    },
    {
        label: 'Non-aktif',
        value: packages.value.filter(p => !p.is_active).length,
        bg: 'bg-slate-100', color: 'text-slate-400',
        icon: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636',
    },
])

const slugError = computed(() => {
    if (!pkgForm.slug) return ''
    if (!/^[a-z0-9-]+$/.test(pkgForm.slug)) return 'Slug hanya boleh huruf kecil, angka, dan tanda hubung (-)'
    return ''
})

// ── Helpers ────────────────────────────────────────────────────────

function formatRp(n) {
    if (!n && n !== 0) return 'Rp 0'
    return 'Rp ' + Number(n).toLocaleString('id-ID')
}

function capitalize(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : s
}

function showToast(type, message) {
    clearTimeout(toastTimer)
    toast.type = type
    toast.message = message
    toast.show = true
    toastTimer = setTimeout(() => (toast.show = false), 3500)
}

function autoSlug() {
    if (formModal.mode === 'edit') return  // jangan overwrite slug saat edit
    pkgForm.slug = pkgForm.name
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-')
}

function resetPkgForm() {
    pkgForm.uuid = null
    pkgForm.name = ''
    pkgForm.slug = ''
    pkgForm.description = ''
    pkgForm.category = 'installation'
    pkgForm.camera_count = 4
    pkgForm.default_brand = 'hikvision'
    pkgForm.thumbnail_url = ''
    pkgForm.highlights = []
    pkgForm.is_active = true
    pkgForm.sort_order = 0
    pkgForm.items = []
    formError.value = ''
}

// ── Modal controls ─────────────────────────────────────────────────

function openCreateModal() {
    resetPkgForm()
    formModal.mode = 'create'
    formModal.show = true
}

function openEditModal(pkg) {
    resetPkgForm()
    formModal.mode = 'edit'
    pkgForm.uuid = pkg.uuid
    pkgForm.name = pkg.name
    pkgForm.slug = pkg.slug
    pkgForm.description = pkg.description || ''
    pkgForm.category = pkg.category
    pkgForm.camera_count = pkg.camera_count
    pkgForm.default_brand = pkg.default_brand
    pkgForm.thumbnail_url = pkg.thumbnail_url || ''
    pkgForm.highlights = [...(pkg.highlights || [])]
    pkgForm.is_active = pkg.is_active
    pkgForm.sort_order = pkg.sort_order ?? 0
    formModal.show = true
}

function closeFormModal() {
    formModal.show = false
    resetPkgForm()
}

function promptDelete(pkg) {
    deleteModal.uuid = pkg.uuid
    deleteModal.name = pkg.name
    deleteModal.show = true
}

// ── Highlights ─────────────────────────────────────────────────────

function addHighlight() {
    pkgForm.highlights.push('')
}
function removeHighlight(i) {
    pkgForm.highlights.splice(i, 1)
}

// ── Items ──────────────────────────────────────────────────────────

function addItem() {
    pkgForm.items.push({
        stock_uuid: '',
        quantity: 1,
        override_price: null,
        label: '',
        sort_order: pkgForm.items.length,
    })
}
function removeItem(i) {
    pkgForm.items.splice(i, 1)
}

// ── API Calls ──────────────────────────────────────────────────────

async function fetchPackages() {
    loading.value = true
    try {
        const { data } = await api.get('/admin/service/packages')
        packages.value = Array.isArray(data) ? data : (data.items || [])
    } catch (e) {
        showToast('error', 'Gagal memuat paket: ' + (e?.response?.data?.detail || e.message))
    } finally {
        loading.value = false
    }
}

async function fetchPricingConfig() {
    try {
        const { data } = await api.get('/admin/service/pricing/active')
        dpPercentage.value = data.dp_percentage ?? 30
    } catch {
        // silent — dp_percentage pakai default seeder
    }
}

async function submitForm() {
    if (!pkgForm.name.trim()) { formError.value = 'Nama paket wajib diisi.'; return }
    if (!pkgForm.slug.trim()) { formError.value = 'Slug wajib diisi.'; return }
    if (slugError.value) { formError.value = slugError.value; return }
    if (pkgForm.camera_count < 1) { formError.value = 'Jumlah kamera minimal 1.'; return }

    formError.value = ''
    submitting.value = true

    try {
        if (formModal.mode === 'create') {
            // Validasi items
            for (const [i, item] of pkgForm.items.entries()) {
                if (!item.stock_uuid.trim()) {
                    formError.value = `Item #${i + 1}: Stock UUID wajib diisi.`
                    submitting.value = false
                    return
                }
            }

            const payload = {
                name: pkgForm.name.trim(),
                slug: pkgForm.slug.trim().toLowerCase(),
                description: pkgForm.description || null,
                category: pkgForm.category,
                camera_count: pkgForm.camera_count,
                default_brand: pkgForm.default_brand,
                thumbnail_url: pkgForm.thumbnail_url || null,
                highlights: pkgForm.highlights.filter(h => h.trim()),
                is_active: pkgForm.is_active,
                sort_order: pkgForm.sort_order,
                items: pkgForm.items.map((item, idx) => ({
                    stock_uuid: item.stock_uuid.trim(),
                    quantity: item.quantity,
                    override_price: item.override_price || null,
                    label: item.label || null,
                    sort_order: item.sort_order ?? idx,
                })),
            }
            const { data } = await api.post('/admin/service/packages', payload)
            packages.value.unshift(data)
            showToast('success', `Paket "${data.name}" berhasil dibuat!`)

        } else {
            // Edit — PATCH metadata only (route: /admin/service/packages/:uuid)
            const payload = {}
            const allowed = ['name', 'description', 'thumbnail_url', 'highlights', 'is_active', 'sort_order', 'estimated_service_price']
            if (pkgForm.name.trim()) payload.name = pkgForm.name.trim()
            if (pkgForm.description) payload.description = pkgForm.description
            if (pkgForm.thumbnail_url) payload.thumbnail_url = pkgForm.thumbnail_url
            payload.highlights = pkgForm.highlights.filter(h => h.trim())
            payload.is_active = pkgForm.is_active
            payload.sort_order = pkgForm.sort_order

            const { data } = await api.patch(`/admin/service/packages/${pkgForm.uuid}`, payload)
            const idx = packages.value.findIndex(p => p.uuid === pkgForm.uuid)
            if (idx !== -1) packages.value[idx] = { ...packages.value[idx], ...data }
            showToast('success', `Paket "${data.name}" berhasil diupdate!`)
        }

        closeFormModal()
    } catch (e) {
        const detail = e?.response?.data?.detail
        formError.value = typeof detail === 'string'
            ? detail
            : Array.isArray(detail)
                ? detail.map(d => d.msg).join(', ')
                : (e.message || 'Terjadi kesalahan')
    } finally {
        submitting.value = false
    }
}

async function recalculate(pkg) {
    recalcLoading.value = pkg.uuid
    try {
        const { data } = await api.post(`/admin/service/packages/${pkg.uuid}/recalculate`)
        const idx = packages.value.findIndex(p => p.uuid === pkg.uuid)
        if (idx !== -1) packages.value[idx] = data
        showToast('success', `Harga "${pkg.name}" berhasil direcalculate.`)
    } catch (e) {
        showToast('error', 'Recalculate gagal: ' + (e?.response?.data?.detail || e.message))
    } finally {
        recalcLoading.value = null
    }
}

async function toggleActive(pkg) {
    try {
        const { data } = await api.patch(`/admin/service/packages/${pkg.uuid}`, {
            is_active: !pkg.is_active,
        })
        const idx = packages.value.findIndex(p => p.uuid === pkg.uuid)
        if (idx !== -1) packages.value[idx] = { ...packages.value[idx], ...data }
        showToast('success', `Paket ${!pkg.is_active ? 'diaktifkan' : 'dinonaktifkan'}.`)
    } catch (e) {
        showToast('error', 'Gagal mengubah status: ' + (e?.response?.data?.detail || e.message))
    }
}

async function confirmDelete() {
    if (!deleteModal.uuid) return
    deleting.value = true
    try {
        // Backend tidak punya DELETE endpoint di schema yang dikirim,
        // jadi kita nonaktifkan saja sebagai soft-delete
        await api.patch(`/admin/service/packages/${deleteModal.uuid}`, { is_active: false })
        packages.value = packages.value.filter(p => p.uuid !== deleteModal.uuid)
        showToast('success', `Paket "${deleteModal.name}" berhasil dihapus.`)
        deleteModal.show = false
    } catch (e) {
        showToast('error', 'Gagal menghapus: ' + (e?.response?.data?.detail || e.message))
    } finally {
        deleting.value = false
    }
}

// ── Lifecycle ──────────────────────────────────────────────────────

onMounted(async () => {
    await Promise.all([fetchPackages(), fetchPricingConfig()])
})
</script>

<style scoped>
@reference "tailwindcss"; 


.field-label {
    @apply block text-xs font-medium text-slate-500 mb-1.5 uppercase tracking-wide;
}

.field-input {
    @apply w-full px-3 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition text-slate-800;
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

.modal-enter-from .relative,
.modal-leave-to .relative {
    transform: scale(.96) translateY(-8px);
}

/* Line clamp */
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>