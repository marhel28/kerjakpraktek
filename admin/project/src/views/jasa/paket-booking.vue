<template>
    <div class="min-h-screen bg-[#F7F8FC] font-sans text-gray-900">

        <!-- ── Toast ──────────────────────────────────────────────── -->
        <Transition name="toast">
            <div v-if="toast.show" :class="[
                'fixed top-5 right-5 z-[100] flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-xl text-sm font-semibold backdrop-blur-sm',
                toast.type === 'success' ? 'bg-emerald-600 text-white'
                    : toast.type === 'info' ? 'bg-indigo-900 text-white'
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

        <!-- ── Header ─────────────────────────────── -->
        <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
            <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
                        </svg>
                    </div>
                    <div>
                        <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Paket Jasa</h1>
                        <p class="text-xs text-gray-400 mt-0.5">Atur bundle hardware + instalasi siap jual</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button @click="openCreateModal"
                        class="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 active:scale-95 transition-all shadow-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                        Buat Paket
                    </button>
                </div>
            </div>
        </div>

        <!-- ── Delete Confirm Modal ───────────────────────────────── -->
        <Transition name="modal">
            <div v-if="deleteModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="deleteModal.show = false" />
                <div class="relative bg-white rounded-xl shadow-2xl p-6 w-full max-w-sm">
                    <div class="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </div>
                    <h3 class="text-center font-bold text-gray-800 mb-1">Hapus Paket?</h3>
                    <p class="text-center text-sm text-gray-500 mb-6">
                        <span class="font-medium text-gray-700">{{ deleteModal.name }}</span> akan dihapus permanen.
                    </p>
                    <div class="flex gap-3">
                        <button @click="deleteModal.show = false"
                            class="flex-1 py-2 rounded-lg border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50 transition">
                            Batal
                        </button>
                        <button @click="confirmDelete" :disabled="deleting"
                            class="flex-1 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-semibold transition disabled:opacity-50">
                            {{ deleting ? '...' : 'Hapus' }}
                        </button>
                    </div>
                </div>
            </div>
        </Transition>

        <!-- ── Package Form Modal ────────────────── -->
        <Transition name="modal">
            <div v-if="formModal.show" class="fixed inset-0 z-50 flex items-start justify-center p-4 overflow-y-auto">
                <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeFormModal" />
                <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-2xl my-6 overflow-hidden">
                    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                        <h2 class="font-bold text-gray-900 text-lg">
                            {{ formModal.mode === 'create' ? 'Buat Paket Baru' : 'Edit Paket' }}
                        </h2>
                        <button @click="closeFormModal" class="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                        </button>
                    </div>

                    <div class="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div class="sm:col-span-2">
                                <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Nama Paket *</label>
                                <input v-model="pkgForm.name" type="text" class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white outline-none" @input="autoSlug" />
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Slug *</label>
                                <input v-model="pkgForm.slug" type="text" class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg font-mono" />
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Kategori *</label>
                                <select v-model="pkgForm.category" class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg outline-none bg-gray-50">
                                    <option v-for="c in CATEGORIES" :key="c.id" :value="c.id">{{ c.label }}</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Brand Default *</label>
                                <select v-model="pkgForm.default_brand" class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg outline-none bg-gray-50">
                                    <option v-for="b in BRANDS" :key="b" :value="b">{{ capitalize(b) }}</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Jumlah Kamera *</label>
                                <input v-model.number="pkgForm.camera_count" type="number" class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg font-mono outline-none bg-gray-50" />
                            </div>
                            <div class="sm:col-span-2">
                                <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Deskripsi</label>
                                <textarea v-model="pkgForm.description" rows="2" class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg outline-none bg-gray-50 focus:bg-white" />
                            </div>
                        </div>

                        <!-- Media Area -->
                        <div class="pt-2 border-t border-gray-100">
                             <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Media Paket</label>
                             <div class="grid grid-cols-2 gap-4">
                                <div class="relative w-full h-32 border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:bg-gray-50 transition" @click="$refs.fileInput.click()">
                                    <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileChange" />
                                    <img v-if="previewUrl" :src="previewUrl" alt="Pratinjau paket booking" class="absolute inset-0 w-full h-full object-cover rounded-lg" />
                                    <svg v-else class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                                    <span class="text-[10px] font-bold text-gray-400 mt-2">Upload Gambar</span>
                                </div>
                                <div class="flex flex-col gap-2">
                                    <label class="text-[10px] font-bold text-gray-400 uppercase">Atau URL Gambar</label>
                                    <input v-model="pkgForm.thumbnail_url" type="url" placeholder="https://..." class="w-full px-4 py-2 text-xs border border-gray-200 rounded-lg outline-none" />
                                    <div v-if="pkgForm.thumbnail_url && !previewUrl" class="flex-1 rounded-xl bg-gray-50 border border-gray-100 overflow-hidden">
                                        <img :src="pkgForm.thumbnail_url" alt="Gambar paket booking" class="w-full h-full object-cover" />
                                    </div>
                                </div>
                             </div>
                        </div>

                        <!-- Highlights -->
                        <div class="pt-2 border-t border-gray-100">
                            <div class="flex items-center justify-between mb-3">
                                <label class="text-xs font-bold text-gray-400 uppercase tracking-widest">Highlights</label>
                                <button @click="addHighlight" class="text-[10px] font-bold text-indigo-600 hover:bg-indigo-50 px-2 py-1 rounded-lg transition border border-indigo-100">+ Tambah</button>
                            </div>
                            <div class="space-y-2">
                                <div v-for="(h, i) in pkgForm.highlights" :key="i" class="flex gap-2">
                                    <input v-model="pkgForm.highlights[i]" type="text" placeholder="Fitur unggulan..." class="flex-1 px-4 py-2 text-sm border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50" />
                                    <button @click="removeHighlight(i)" class="p-2 text-gray-300 hover:text-red-500 rounded-lg transition"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                                </div>
                            </div>
                        </div>

                        <!-- Items (Only Create) -->
                        <div v-if="formModal.mode === 'create'" class="pt-2 border-t border-gray-100">
                            <div class="flex items-center justify-between mb-3">
                                <label class="text-xs font-bold text-gray-400 uppercase tracking-widest">Item / Bundle Barang</label>
                                <button @click="addItem" class="text-[10px] font-bold text-indigo-600 hover:bg-indigo-50 px-2 py-1 rounded-lg transition border border-indigo-100">+ Item</button>
                            </div>
                            <div class="space-y-3">
                                <div v-for="(item, idx) in pkgForm.items" :key="idx" class="p-4 border border-gray-100 rounded-xl bg-gray-50/50">
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-[10px] font-bold text-gray-400">ITEM #{{ idx + 1 }}</span>
                                        <button @click="removeItem(idx)" class="text-gray-300 hover:text-red-500"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                                    </div>
                                    <div class="grid grid-cols-2 gap-3">
                                        <div class="col-span-2">
                                            <input v-model="item.stock_uuid" type="text" placeholder="Stock UUID" class="w-full px-3 py-1.5 text-xs font-mono border border-gray-200 rounded-lg outline-none" />
                                        </div>
                                        <input v-model="item.label" type="text" placeholder="Label Item" class="w-full px-3 py-1.5 text-xs border border-gray-200 rounded-lg outline-none" />
                                        <div class="flex gap-2">
                                            <input v-model.number="item.quantity" type="number" placeholder="Qty" class="w-16 px-3 py-1.5 text-xs border border-gray-200 rounded-lg outline-none" />
                                            <input v-model.number="item.override_price" type="number" placeholder="Price (Optional)" class="flex-1 px-3 py-1.5 text-xs border border-gray-200 rounded-lg outline-none" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-end gap-3">
                        <button @click="closeFormModal" class="px-5 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 transition">Batal</button>
                        <button @click="submitForm" :disabled="submitting" class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-lg transition disabled:opacity-50">
                            {{ submitting ? '...' : 'Simpan' }}
                        </button>
                    </div>
                </div>
            </div>
        </Transition>

        <!-- ── Main Content ───────────────────────────────────────── -->
        <div class="max-w-6xl mx-auto px-5 py-12">

            <!-- Header -->
            <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10">
                <div class="space-y-1.5">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-slate-900 rounded-2xl flex items-center justify-center shadow-xl shadow-slate-200 rotate-3 transition hover:rotate-0">
                            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                            </svg>
                        </div>
                        <div>
                            <h1 class="text-2xl font-black text-slate-900 tracking-tight">Manajemen Paket CCTV</h1>
                            <p class="text-sm font-medium text-slate-400">Atur bundle hardware + instalasi siap jual</p>
                        </div>
                    </div>
                </div>
                
                <div class="flex flex-wrap items-center gap-3">
                    <!-- Filter kategori -->
                    <div class="relative">
                        <select v-model="filterCategory"
                            class="appearance-none text-sm font-bold bg-white border border-slate-200 rounded-2xl pl-4 pr-10 py-3 text-slate-700 focus:outline-none focus:ring-4 focus:ring-slate-100 transition shadow-sm hover:border-slate-300">
                            <option value="">Semua Kategori</option>
                            <option v-for="c in CATEGORIES" :key="c.id" :value="c.id">{{ c.label }}</option>
                        </select>
                        <svg class="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>
                    
                    <!-- Toggle aktif -->
                    <button 
                        @click="showInactive = !showInactive"
                        :class="[
                            'flex items-center gap-2 text-sm font-bold border rounded-2xl px-5 py-3 transition-all active:scale-95 shadow-sm',
                            showInactive ? 'bg-slate-900 border-slate-900 text-white shadow-slate-200' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                        ]"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        {{ showInactive ? 'Sembunyikan Non-aktif' : 'Tampilkan Semua' }}
                    </button>

                    <!-- Tambah paket -->
                    <button @click="openCreateModal"
                        class="inline-flex items-center gap-2.5 px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white text-sm font-black rounded-2xl transition shadow-lg shadow-slate-200 hover:shadow-slate-300 active:scale-95">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3"
                                d="M12 4v16m8-8H4" />
                        </svg>
                        Buat Paket
                    </button>
                </div>
            </div>

            <!-- Stats Row -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
                <div v-for="stat in stats" :key="stat.label"
                    class="bg-white rounded-3xl shadow-sm border border-slate-100 p-5 flex items-center gap-4 transition-all hover:shadow-md hover:border-slate-200">
                    <div :class="['w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-sm', stat.bg]">
                        <svg class="w-6 h-6" :class="stat.color" fill="none" stroke="currentColor"
                            viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" :d="stat.icon" />
                        </svg>
                    </div>
                    <div class="overflow-hidden">
                        <p class="text-xl font-black text-slate-900 leading-none truncate">{{ stat.value }}</p>
                        <p class="text-[10px] font-bold text-slate-400 mt-1.5 uppercase tracking-wider">{{ stat.label }}</p>
                    </div>
                </div>
            </div>

            <!-- Loading Skeleton -->
            <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                <div v-for="n in 6" :key="n" class="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 animate-pulse space-y-4">
                    <div class="h-40 bg-slate-50 rounded-2xl" />
                    <div class="space-y-2">
                        <div class="h-5 bg-slate-50 rounded-lg w-3/4" />
                        <div class="h-3.5 bg-slate-50 rounded-lg w-1/2" />
                    </div>
                    <div class="flex gap-3 pt-2">
                        <div class="h-10 bg-slate-50 rounded-xl flex-1" />
                        <div class="h-10 bg-slate-50 rounded-xl w-10" />
                    </div>
                </div>
            </div>

            <!-- Empty state -->
            <div v-else-if="filteredPackages.length === 0" class="text-center py-20 bg-white rounded-xl border border-dashed border-gray-200">
                <svg class="w-16 h-16 text-gray-200 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/></svg>
                <h3 class="text-gray-400 font-bold">Belum ada paket ditemukan</h3>
            </div>

            <!-- Package Grid -->
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                <div v-for="pkg in filteredPackages" :key="pkg.uuid" :class="[
                    'group bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col transition-all duration-300 hover:shadow-md',
                    !pkg.is_active && 'opacity-60 grayscale-[0.5]'
                ]">
                    <!-- Thumbnail -->
                    <div class="relative h-40 bg-gray-50 overflow-hidden">
                        <img v-if="pkg.thumbnail_url" :src="pkg.thumbnail_url" alt="Gambar paket booking" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                        <div v-else class="w-full h-full flex items-center justify-center text-gray-200">
                            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/></svg>
                        </div>
                        <div class="absolute top-3 left-3 flex flex-col gap-1">
                            <span :class="[
                                'text-[10px] font-bold uppercase px-2 py-1 rounded-lg border border-white/20 backdrop-blur-md shadow-sm',
                                CATEGORY_COLOR[pkg.category] || 'bg-gray-100 text-gray-600'
                            ]">
                                {{CATEGORIES.find(c => c.id === pkg.category)?.label || pkg.category}}
                            </span>
                        </div>
                        <div v-if="!pkg.is_active" class="absolute inset-0 bg-gray-900/40 flex items-center justify-center">
                            <span class="text-white text-[10px] font-black uppercase tracking-widest border border-white/30 px-3 py-1 rounded-lg backdrop-blur-sm">Non-aktif</span>
                        </div>
                    </div>

                    <!-- Body -->
                    <div class="p-5 flex-1 flex flex-col">
                        <div class="mb-4 flex-1">
                            <h3 class="font-bold text-gray-900 text-sm mb-1 line-clamp-2">{{ pkg.name }}</h3>
                            <p class="text-[11px] text-gray-400 line-clamp-2 leading-relaxed">{{ pkg.description || '...' }}</p>
                        </div>

                        <!-- Pricing Card -->
                        <div class="bg-gray-50 rounded-xl p-3 mb-4 border border-gray-100">
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-[9px] font-bold text-gray-400 uppercase">Estimasi</span>
                                <span class="text-sm font-bold text-gray-900 font-mono">{{ formatRp(pkg.total_estimated) }}</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-[9px] font-bold text-emerald-500 uppercase">DP Booking</span>
                                <span class="text-xs font-bold text-emerald-600 font-mono">{{ formatRp(pkg.dp_amount) }}</span>
                            </div>
                        </div>

                        <div class="flex items-center gap-4 mb-4 text-[10px] font-bold text-gray-500">
                            <span class="flex items-center gap-1"><svg class="w-3 h-3 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 10l4.553-2.069A1 1 0 0121 8.82V15a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/></svg> {{ pkg.camera_count }} Cam</span>
                            <span class="w-px h-3 bg-gray-200"></span>
                            <span class="capitalize">{{ pkg.default_brand }}</span>
                        </div>

                        <!-- Actions -->
                        <div class="flex gap-2">
                            <button @click="openEditModal(pkg)"
                                class="flex-1 py-2 text-[11px] font-bold text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-100 transition active:scale-95">
                                Kelola
                            </button>
                            <button @click="recalculate(pkg)" :disabled="recalcLoading === pkg.uuid" class="w-9 h-9 flex items-center justify-center rounded-lg border border-gray-200 text-indigo-500 hover:bg-indigo-50 transition active:scale-95">
                                <svg :class="['w-4 h-4', recalcLoading === pkg.uuid && 'animate-spin']" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                            </button>
                            <button @click="promptDelete(pkg)" class="w-9 h-9 flex items-center justify-center rounded-lg border border-gray-200 text-red-400 hover:bg-red-50 transition active:scale-95">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pagination hint -->
            <div v-if="packages.length > 0" class="flex flex-col items-center gap-2 mt-12">
                <p class="text-xs font-bold text-slate-300 uppercase tracking-[0.2em]">
                    Menampilkan {{ filteredPackages.length }} dari {{ packages.length }} paket tersedia
                </p>
                <div class="flex gap-1">
                    <div v-for="i in 3" :key="i" class="w-1 h-1 bg-slate-200 rounded-full"></div>
                </div>
            </div>

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
    installation: 'bg-blue-600 text-white',
    maintenance: 'bg-amber-500 text-white',
    consultation: 'bg-teal-500 text-white',
    troubleshoot: 'bg-rose-500 text-white',
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

// File upload state
const fileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)

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
    }).sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
})

const stats = computed(() => [
    {
        label: 'Total Paket',
        value: packages.value.length,
        bg: 'bg-slate-900', color: 'text-white',
        icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
    },
    {
        label: 'Aktif',
        value: packages.value.filter(p => p.is_active).length,
        bg: 'bg-emerald-50', color: 'text-emerald-500',
        icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    },
    {
        label: 'Pemasangan',
        value: packages.value.filter(p => p.category === 'installation').length,
        bg: 'bg-blue-50', color: 'text-blue-500',
        icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    },
    {
        label: 'Draf/Lainnya',
        value: packages.value.filter(p => !p.is_active || p.category !== 'installation').length,
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
    
    // Reset file state
    selectedFile.value = null
    previewUrl.value = null
}

// ── Media Helpers ──────────────────────────────────────────────────

function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return
    
    if (file.size > 2 * 1024 * 1024) {
        showToast('error', 'Ukuran file maksimal 2MB')
        return
    }
    
    processFile(file)
}

function handleFileDrop(e) {
    const file = e.dataTransfer.files[0]
    if (!file || !file.type.startsWith('image/')) return
    processFile(file)
}

function processFile(file) {
    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
    // Clear URL field when file is picked to avoid confusion, though backend handles both
    pkgForm.thumbnail_url = ''
}

function handleUrlError(e) {
    e.target.style.display = 'none'
}

function handleCardUrlError(e) {
    e.target.style.opacity = '0'
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
        // silent — dp_percentage pakai default
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
        const formData = new FormData()
        
        if (selectedFile.value) {
            formData.append('thumbnail', selectedFile.value)
        }

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
            
            formData.append('data', JSON.stringify(payload))
            
            const { data } = await api.post('/admin/service/packages', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            packages.value.unshift(data)
            showToast('success', `Paket "${data.name}" berhasil dibuat!`)

        } else {
            // Edit — PATCH
            const updates = {
                name: pkgForm.name.trim(),
                description: pkgForm.description || null,
                thumbnail_url: pkgForm.thumbnail_url || null,
                highlights: pkgForm.highlights.filter(h => h.trim()),
                is_active: pkgForm.is_active,
                sort_order: pkgForm.sort_order,
                category: pkgForm.category,
                camera_count: pkgForm.camera_count,
                default_brand: pkgForm.default_brand
            }

            formData.append('updates', JSON.stringify(updates))

            const { data } = await api.patch(`/admin/service/packages/${pkgForm.uuid}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
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
        // We use FormData even for simple updates to stay consistent with the new endpoint signature
        const formData = new FormData()
        formData.append('updates', JSON.stringify({ is_active: !pkg.is_active }))
        
        const { data } = await api.patch(`/admin/service/packages/${pkg.uuid}`, formData)
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
        // Just deactivate
        const formData = new FormData()
        formData.append('updates', JSON.stringify({ is_active: false }))
        await api.patch(`/admin/service/packages/${deleteModal.uuid}`, formData)
        
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
    @apply block text-[10px] font-black text-slate-400 mb-2 uppercase tracking-[0.15em];
}

.field-input {
    @apply w-full px-4 py-3 text-sm bg-slate-50 border border-slate-100 rounded-2xl focus:outline-none focus:ring-4 focus:ring-slate-100 focus:bg-white focus:border-slate-300 transition-all duration-300 text-slate-800 placeholder:text-slate-300;
}

.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    @apply bg-transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    @apply bg-slate-100 rounded-full;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    @apply bg-slate-200;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-4px); }
    75% { transform: translateX(4px); }
}
.animate-shake {
    animation: shake 0.3s ease-in-out;
}

/* Toast */
.toast-enter-active,
.toast-leave-active {
    transition: all .4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-enter-from,
.toast-leave-to {
    opacity: 0;
    transform: translateY(-1rem) scale(.9);
}

/* Modal */
.modal-enter-active,
.modal-leave-active {
    transition: all .3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
    transform: scale(.9) translateY(20px);
}

/* Line clamp */
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>