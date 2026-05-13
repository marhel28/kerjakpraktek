<template>
    <div class="min-h-screen bg-[#F7F8FC] font-sans">

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
                        <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Manajemen Stok</h1>
                        <p class="text-xs text-gray-400 mt-0.5">Padjajaran CCTV — Admin Panel</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <router-link to="/stock/coupon"
                        class="flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all">
                        <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
                        </svg>
                        Kupon
                    </router-link>
                    <router-link
                        to="/stock/createsData"
                        class="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 active:scale-95 transition-all shadow-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                        Tambah Stok
                    </router-link>
                </div>
            </div>
        </div>

        <div class="max-w-screen-2xl mx-auto px-6 py-6 space-y-5">

            <!-- ── Stats Cards ─────────────────────── -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div v-for="stat in stats" :key="stat.label"
                    class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
                    <div class="flex items-start justify-between">
                        <div>
                            <p class="text-xs font-medium text-gray-400 uppercase tracking-wide">{{ stat.label }}</p>
                            <p class="text-2xl font-bold text-gray-900 mt-1">{{ stat.value }}</p>
                        </div>
                        <div :class="['w-9 h-9 rounded-lg flex items-center justify-center', stat.iconBg]">
                            <svg class="w-4 h-4" :class="stat.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.icon" />
                            </svg>
                        </div>
                    </div>
                    <p :class="['text-xs mt-2 font-medium', stat.change > 0 ? 'text-emerald-600' : stat.change < 0 ? 'text-red-500' : 'text-gray-400']">
                        {{ stat.sub }}
                    </p>
                </div>
            </div>

            <!-- ── Filter Bar ──────────────────────── -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                <div class="flex flex-wrap gap-3 items-end">
                    <!-- Search -->
                    <div class="flex-1 min-w-56">
                        <label class="block text-xs font-semibold text-gray-500 mb-1.5">Cari Produk</label>
                        <div class="relative">
                            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            <input v-model="filters.q" type="text" placeholder="Cari nama produk, brand..."
                                class="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-gray-50 focus:bg-white transition-all"
                                @input="debouncedFetch" />
                        </div>
                    </div>

                    <!-- Ketersediaan -->
                    <div class="min-w-36">
                        <label class="block text-xs font-semibold text-gray-500 mb-1.5">Ketersediaan</label>
                        <select v-model="filters.stock_status" @change="resetPageAndFetch"
                            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all">
                            <option value="">Semua Stok</option>
                            <option value="tersedia">Tersedia</option>
                            <option value="kosong">Kosong / Habis</option>
                        </select>
                    </div>

                    <!-- Status Tayang -->
                    <div class="min-w-36">
                        <label class="block text-xs font-semibold text-gray-500 mb-1.5">Status Tayang</label>
                        <select v-model="filters.is_active" @change="resetPageAndFetch"
                            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all">
                            <option value="">Semua Status</option>
                            <option value="true">Aktif (Live)</option>
                            <option value="false">Nonaktif</option>
                        </select>
                    </div>

                    <!-- Brand -->
                    <div class="min-w-36">
                        <label class="block text-xs font-semibold text-gray-500 mb-1.5">Brand</label>
                        <select v-model="filters.brand" @change="resetPageAndFetch"
                            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all">
                            <option value="">Semua Brand</option>
                            <option v-for="b in brands" :key="b.key || b.s" :value="b.key || b.s">{{ b.key || b.n }}</option>
                        </select>
                    </div>

                    <!-- Kategori — searchable -->
                    <div class="min-w-44 relative" ref="categoryDropdownRef">
                        <label class="block text-xs font-semibold text-gray-500 mb-1.5">Kategori</label>
                        <div class="relative">
                            <input
                                v-model="categorySearch"
                                type="text"
                                placeholder="Cari kategori..."
                                class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all pr-8"
                                @focus="categoryDropdownOpen = true"
                                @input="categoryDropdownOpen = true"
                                readonly-placeholder="Semua Kategori"
                            />
                            <!-- Clear button -->
                            <button v-if="filters.cat" @click.stop="clearCategory"
                                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                                </svg>
                            </button>
                            <svg v-else class="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                            </svg>
                        </div>

                        <!-- Dropdown list -->
                        <Transition name="dropdown">
                            <div v-if="categoryDropdownOpen"
                                class="absolute z-20 mt-1 w-full min-w-[200px] bg-white border border-gray-200 rounded-xl shadow-xl overflow-hidden">
                                <div class="max-h-56 overflow-y-auto">
                                    <button
                                        class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                                        :class="filters.cat === '' ? 'bg-indigo-50 text-indigo-700 font-semibold' : 'text-gray-600'"
                                        @click="selectCategory('')">
                                        Semua Kategori
                                    </button>
                                    <template v-for="c in filteredCategories" :key="c.slug">
                                        <button
                                            class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                                            :class="filters.cat === c.slug ? 'bg-indigo-50 text-indigo-700 font-semibold' : 'text-gray-600'"
                                            @click="selectCategory(c.slug)">
                                            {{ c.name || c.slug }}
                                        </button>
                                    </template>
                                    <div v-if="filteredCategories.length === 0" class="px-3 py-3 text-xs text-gray-400 text-center">
                                        Tidak ada kategori ditemukan
                                    </div>
                                </div>
                            </div>
                        </Transition>
                    </div>

                    <!-- Urutkan -->
                    <div class="min-w-36">
                        <label class="block text-xs font-semibold text-gray-500 mb-1.5">Urutkan</label>
                        <select v-model="filters.sort" @change="resetPageAndFetch"
                            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50 focus:bg-white transition-all">
                            <option value="newest">Terbaru</option>
                            <option value="price_asc">Harga ↑</option>
                            <option value="price_desc">Harga ↓</option>
                            <option value="stock_high">Stok Terbanyak</option>
                            <option value="sold_high">Terlaris</option>
                        </select>
                    </div>

                    <!-- Reset -->
                    <button @click="resetFilters"
                        class="px-4 py-2 text-sm font-medium text-gray-500 border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-gray-700 transition-all flex items-center gap-1.5">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Reset
                    </button>
                </div>

                <!-- Active filters pills -->
                <div v-if="activeFilterCount > 0" class="mt-3 flex flex-wrap gap-2">
                    <span v-if="filters.q" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">
                        Cari: "{{ filters.q }}"
                        <button @click="filters.q = ''; resetPageAndFetch()" class="ml-1 hover:text-indigo-900">×</button>
                    </span>
                    <span v-if="filters.cat" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-violet-50 text-violet-700 border border-violet-100">
                        Kategori: {{ filters.cat }}
                        <button @click="clearCategory()" class="ml-1 hover:text-violet-900">×</button>
                    </span>
                    <span v-if="filters.brand" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
                        Brand: {{ filters.brand }}
                        <button @click="filters.brand = ''; resetPageAndFetch()" class="ml-1 hover:text-blue-900">×</button>
                    </span>
                    <span v-if="filters.stock_status" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-100">
                        Stok: {{ filters.stock_status === 'tersedia' ? 'Tersedia' : 'Kosong' }}
                        <button @click="filters.stock_status = ''; resetPageAndFetch()" class="ml-1 hover:text-amber-900">×</button>
                    </span>
                    <span v-if="filters.is_active !== ''" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-100">
                        Status: {{ filters.is_active === 'true' ? 'Aktif' : 'Nonaktif' }}
                        <button @click="filters.is_active = ''; resetPageAndFetch()" class="ml-1 hover:text-emerald-900">×</button>
                    </span>
                </div>

                <!-- Bulk Actions -->
                <div v-if="selectedIds.length > 0" class="mt-3 pt-3 border-t border-gray-100 flex items-center gap-3">
                    <span class="text-xs font-medium text-indigo-700 bg-indigo-50 px-3 py-1.5 rounded-lg border border-indigo-100">
                        {{ selectedIds.length }} item dipilih
                    </span>
                    <button @click="confirmBulkDelete"
                        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-red-600 bg-red-50 border border-red-100 rounded-lg hover:bg-red-100 transition-colors">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Hapus Terpilih
                    </button>
                    <button @click="selectedIds = []; selectAll = false" class="text-xs text-gray-400 hover:text-gray-600 transition-colors">
                        Batal pilih
                    </button>
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

                <div v-else-if="!stocks.length" class="flex flex-col items-center justify-center py-24 gap-4">
                    <div class="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center">
                        <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
                        </svg>
                    </div>
                    <div class="text-center">
                        <p class="text-sm font-semibold text-gray-600">Tidak ada produk ditemukan</p>
                        <p class="text-xs text-gray-400 mt-1">Coba ubah filter atau tambah produk baru</p>
                    </div>
                    <router-link to="/stock/create"
                        class="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
                        + Tambah Produk
                    </router-link>
                </div>

                <div v-else class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b border-gray-100 bg-gray-50/80">
                                <th class="px-4 py-3 w-10">
                                    <input type="checkbox" v-model="selectAll" @change="toggleSelectAll"
                                        class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                                </th>
                                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Produk</th>
                                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Brand</th>
                                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Kategori</th>
                                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Harga</th>
                                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Stok</th>
                                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Terjual</th>
                                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Aksi</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-50">
                            <tr v-for="item in stocks" :key="item.uuid"
                                :class="['group hover:bg-indigo-50/20 transition-colors cursor-pointer', selectedIds.includes(item.uuid) ? 'bg-indigo-50/30' : '']"
                                @click.stop="openDetailDrawer(item)">

                                <td class="px-4 py-3.5" @click.stop>
                                    <input type="checkbox" :value="item.uuid" v-model="selectedIds"
                                        class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                                </td>

                                <!-- Product -->
                                <td class="px-4 py-3.5">
                                    <div class="flex items-center gap-3">
                                        <div class="w-12 h-12 rounded-xl overflow-hidden bg-gray-100 flex-shrink-0 border border-gray-100 shadow-sm flex items-center justify-center">
                                            <img v-if="item.image || item.cover_image_url"
                                                :src="item.image || item.cover_image_url" :alt="item.title"
                                                class="w-full h-full object-cover" loading="lazy" />
                                            <svg v-else class="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                        </div>
                                        <div class="min-w-0">
                                            <p class="font-semibold text-gray-800 truncate max-w-[200px] text-sm">{{ item.title }}</p>
                                            <p class="text-xs text-gray-400 truncate mt-0.5">{{ item.slug }}</p>
                                        </div>
                                    </div>
                                </td>

                                <!-- Brand -->
                                <td class="px-4 py-3.5">
                                    <span v-if="item.brand"
                                        class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                                        {{ item.brand }}
                                    </span>
                                    <span v-else class="text-gray-300 text-xs">—</span>
                                </td>

                                <!-- Kategori -->
                                <td class="px-4 py-3.5">
                                    <div class="space-y-1">
                                        <button
                                            class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-600 hover:bg-indigo-100 hover:text-indigo-700 transition-colors"
                                            @click.stop="quickFilterCategory(item.category || item.category_slug)"
                                            :title="'Filter kategori: ' + (item.category || item.category_slug)">
                                            {{ item.category || item.category_slug }}
                                        </button>
                                        <span v-if="item.subcategory || item.subcategory_slug" class="block text-xs text-gray-400">
                                            {{ item.subcategory || item.subcategory_slug }}
                                        </span>
                                    </div>
                                </td>

                                <!-- Harga -->
                                <td class="px-4 py-3.5 text-right">
                                    <p class="font-bold text-gray-800 text-sm">{{ formatPrice(item.price || item.online_price) }}</p>
                                    <div v-if="item.discount_percentage > 0" class="flex items-center justify-end gap-1.5 mt-0.5">
                                        <span class="text-xs text-gray-400 line-through">{{ formatPrice(item.original_price) }}</span>
                                        <span class="text-xs font-bold text-rose-500 bg-rose-50 px-1.5 py-0.5 rounded-md border border-rose-100">-{{ item.discount_percentage }}%</span>
                                    </div>
                                </td>

                                <!-- Stok -->
                                <td class="px-4 py-3.5 text-center">
                                    <div class="flex flex-col items-center gap-1">
                                        <!-- Badge stok tersedia / kosong -->
                                        <span :class="[
                                            'inline-flex items-center justify-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold',
                                            stockBadgeClass(item)
                                        ]">
                                            <span :class="['w-1.5 h-1.5 rounded-full', stockDotClass(item)]"></span>
                                            {{ stockLabel(item) }}
                                        </span>
                                        <span class="text-[11px] text-gray-400 font-medium">
                                            Sisa {{ item.sisa ?? item.stok ?? 0 }} / {{ item.stok ?? 0 }} total
                                        </span>
                                    </div>
                                </td>

                                <!-- Terjual — dedicated column -->
                                <td class="px-4 py-3.5 text-center">
                                    <div class="flex flex-col items-center gap-1">
                                        <span class="text-base font-black text-indigo-600">
                                            {{ (item.terjual ?? 0).toLocaleString('id-ID') }}
                                        </span>
                                        <!-- mini progress bar -->
                                        <div class="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                            <div class="h-full bg-indigo-400 rounded-full transition-all"
                                                :style="{ width: soldPercent(item) + '%' }">
                                            </div>
                                        </div>
                                        <span class="text-[10px] text-gray-400">{{ soldPercent(item) }}% terjual</span>
                                    </div>
                                </td>

                                <!-- Status Tayang -->
                                <td class="px-4 py-3.5 text-center">
                                    <span :class="[
                                        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border',
                                        item.is_active ? 'bg-blue-50 text-blue-700 border-blue-100' : 'bg-gray-100 text-gray-500 border-gray-200'
                                    ]">
                                        <span :class="['w-1.5 h-1.5 rounded-full', item.is_active ? 'bg-blue-500' : 'bg-gray-400']"></span>
                                        {{ item.is_active ? 'Aktif' : 'Nonaktif' }}
                                    </span>
                                </td>

                                <!-- Actions -->
                                <td class="px-4 py-3.5" @click.stop>
                                    <div class="flex items-center justify-center gap-1">
                                        <button @click.stop="openDetailDrawer(item)"
                                            class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                                            title="Lihat Detail">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                            </svg>
                                        </button>
                                        <button @click.stop="openQuickEdit(item)"
                                            class="p-2 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all"
                                            title="Edit Cepat Stok">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                                            </svg>
                                        </button>
                                        <router-link :to="`/stock/${item.uuid}/edit`"
                                            class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                                            title="Edit Produk">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                        </router-link>
                                        <button @click.stop="confirmDelete(item)"
                                            class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                                            title="Hapus Produk">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div v-if="!loading && stocks.length"
                    class="px-5 py-3.5 border-t border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <p class="text-xs text-gray-400">
                        Menampilkan
                        <span class="font-semibold text-gray-700">{{ (pagination.page - 1) * pagination.size + 1 }}–{{ Math.min(pagination.page * pagination.size, pagination.total) }}</span>
                        dari <span class="font-semibold text-gray-700">{{ pagination.total.toLocaleString('id') }}</span> produk
                    </p>
                    <div class="flex items-center gap-1">
                        <button @click="changePage(pagination.page - 1)" :disabled="pagination.page <= 1"
                            class="w-8 h-8 flex items-center justify-center text-xs font-medium text-gray-500 border border-gray-200 rounded-lg disabled:opacity-30 hover:bg-gray-100 transition-colors disabled:cursor-not-allowed">
                            ←
                        </button>
                        <template v-for="p in visiblePages" :key="p">
                            <button v-if="p !== '...'" @click="changePage(p)" :class="[
                                'w-8 h-8 flex items-center justify-center text-xs font-semibold rounded-lg transition-colors',
                                p === pagination.page
                                    ? 'bg-indigo-600 text-white shadow-sm'
                                    : 'text-gray-500 border border-gray-200 hover:bg-gray-100'
                            ]">{{ p }}</button>
                            <span v-else class="w-6 flex items-center justify-center text-gray-300 text-xs">…</span>
                        </template>
                        <button @click="changePage(pagination.page + 1)" :disabled="pagination.page >= pagination.totalPages"
                            class="w-8 h-8 flex items-center justify-center text-xs font-medium text-gray-500 border border-gray-200 rounded-lg disabled:opacity-30 hover:bg-gray-100 transition-colors disabled:cursor-not-allowed">
                            →
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- ══════════════════════════════════════════════════════ -->
        <!-- ── DETAIL DRAWER ──────────────────────────────────── -->
        <!-- ══════════════════════════════════════════════════════ -->
        <Teleport to="body">
            <Transition name="drawer-overlay">
                <div v-if="detailDrawer.show"
                    class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
                    @click="detailDrawer.show = false">
                </div>
            </Transition>
            <Transition name="drawer-panel">
                <div v-if="detailDrawer.show"
                    class="fixed top-0 right-0 bottom-0 z-50 w-full max-w-xl bg-white shadow-2xl flex flex-col"
                    @click.stop>

                    <!-- Drawer Header -->
                    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                        <div class="flex items-center gap-3">
                            <button @click="detailDrawer.show = false"
                                class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                            <h3 class="text-sm font-bold text-gray-900">Detail Produk</h3>
                        </div>
                        <div class="flex items-center gap-2">
                            <button @click="openQuickEdit(detailDrawer.item); detailDrawer.show = false"
                                class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-lg hover:bg-emerald-100 transition-colors">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                                </svg>
                                Edit Cepat
                            </button>
                            <router-link v-if="editUrl" :to="editUrl"
                                class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                                Edit Lengkap
                            </router-link>
                        </div>
                    </div>

                    <!-- Drawer Body -->
                    <div v-if="detailDrawer.loading" class="flex-1 flex items-center justify-center">
                        <div class="flex flex-col items-center gap-3">
                            <div class="w-10 h-10 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                            <p class="text-sm text-gray-400">Memuat detail...</p>
                        </div>
                    </div>

                    <div v-else-if="detailDrawer.data" class="flex-1 overflow-y-auto">

                        <!-- Image Gallery -->
                        <div class="relative bg-gray-50 border-b border-gray-100">
                            <div v-if="detailDrawer.data.images && detailDrawer.data.images.length" class="flex gap-2 p-4 overflow-x-auto">
                                <div v-for="(img, idx) in detailDrawer.data.images" :key="idx"
                                    class="w-32 h-32 flex-shrink-0 rounded-xl overflow-hidden border border-gray-200 bg-white cursor-pointer"
                                    :class="detailDrawer.activeImg === idx ? 'ring-2 ring-indigo-500' : ''"
                                    @click="detailDrawer.activeImg = idx">
                                    <img :src="img" class="w-full h-full object-cover" />
                                </div>
                            </div>
                            <div v-if="detailDrawer.data.images && detailDrawer.data.images.length" class="px-4 pb-4">
                                <div class="w-full aspect-video rounded-xl overflow-hidden bg-white border border-gray-200 flex items-center justify-center">
                                    <img :src="detailDrawer.data.images[detailDrawer.activeImg]" class="max-h-full max-w-full object-contain" />
                                </div>
                            </div>
                            <div v-else class="h-40 flex items-center justify-center">
                                <div class="text-center">
                                    <svg class="w-12 h-12 text-gray-200 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <p class="text-xs text-gray-400 mt-2">Tidak ada gambar</p>
                                </div>
                            </div>
                        </div>

                        <!-- Product Info -->
                        <div class="p-6 space-y-5">

                            <!-- Title & Status -->
                            <div>
                                <div class="flex items-start justify-between gap-3 mb-1">
                                    <h2 class="text-base font-bold text-gray-900 leading-snug">{{ detailDrawer.data.title }}</h2>
                                    <span :class="[
                                        'flex-shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border',
                                        detailDrawer.data.is_active
                                            ? 'bg-blue-50 text-blue-700 border-blue-100'
                                            : 'bg-gray-100 text-gray-500 border-gray-200'
                                    ]">
                                        <span :class="['w-1.5 h-1.5 rounded-full', detailDrawer.data.is_active ? 'bg-blue-500' : 'bg-gray-400']"></span>
                                        {{ detailDrawer.data.is_active ? 'Aktif' : 'Nonaktif' }}
                                    </span>
                                </div>
                                <p class="text-xs text-gray-400">{{ detailDrawer.data.slug }}</p>
                            </div>

                            <!-- Badges -->
                            <div class="flex flex-wrap gap-2">
                                <span v-if="detailDrawer.data.brand"
                                    class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                                    {{ detailDrawer.data.brand }}
                                </span>
                                <span v-if="detailDrawer.data.category || detailDrawer.data.category_slug"
                                    class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-600">
                                    {{ detailDrawer.data.category || detailDrawer.data.category_slug }}
                                </span>
                                <span v-if="detailDrawer.data.subcategory || detailDrawer.data.subcategory_slug"
                                    class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-500">
                                    {{ detailDrawer.data.subcategory || detailDrawer.data.subcategory_slug }}
                                </span>
                                <span v-if="detailDrawer.data.type"
                                    class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-violet-50 text-violet-600 border border-violet-100">
                                    {{ detailDrawer.data.type }}
                                </span>
                                <span v-if="detailDrawer.data.weight"
                                    class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-orange-50 text-orange-600 border border-orange-100">
                                    {{ detailDrawer.data.weight }}g
                                </span>
                            </div>

                            <!-- Price Card -->
                            <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
                                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Harga</p>
                                <div class="flex items-end gap-3">
                                    <p class="text-2xl font-bold text-gray-900">{{ formatPrice(detailDrawer.data.price || detailDrawer.data.online_price) }}</p>
                                    <div v-if="detailDrawer.data.discount_percentage > 0" class="flex items-center gap-2 mb-0.5">
                                        <span class="text-sm text-gray-400 line-through">{{ formatPrice(detailDrawer.data.original_price) }}</span>
                                        <span class="text-xs font-bold text-rose-500 bg-rose-50 px-2 py-0.5 rounded-md border border-rose-100">-{{ detailDrawer.data.discount_percentage }}%</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Stock Info Grid (4 columns now including terjual prominently) -->
                            <div class="grid grid-cols-4 gap-3">
                                <div class="bg-white border border-gray-100 rounded-xl p-3 text-center shadow-sm">
                                    <p class="text-xs text-gray-400 font-medium">Total Stok</p>
                                    <p :class="[
                                        'text-xl font-bold mt-1',
                                        (detailDrawer.data.stok ?? 0) === 0 ? 'text-red-500' :
                                        (detailDrawer.data.stok ?? 0) <= 5 ? 'text-amber-600' : 'text-gray-900'
                                    ]">{{ detailDrawer.data.stok ?? 0 }}</p>
                                </div>
                                <div class="bg-white border border-gray-100 rounded-xl p-3 text-center shadow-sm">
                                    <p class="text-xs text-gray-400 font-medium">Sisa</p>
                                    <p class="text-xl font-bold text-emerald-600 mt-1">{{ detailDrawer.data.sisa ?? detailDrawer.data.stok ?? 0 }}</p>
                                </div>
                                <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-3 text-center shadow-sm col-span-2">
                                    <p class="text-xs text-indigo-400 font-medium">Terjual</p>
                                    <p class="text-2xl font-black text-indigo-600 mt-1">{{ (detailDrawer.data.terjual ?? 0).toLocaleString('id-ID') }}</p>
                                    <p class="text-[10px] text-indigo-400 mt-0.5">unit terjual</p>
                                </div>
                            </div>

                            <!-- Stock Status Bar -->
                            <div v-if="(detailDrawer.data.stok ?? 0) > 0">
                                <div class="flex items-center justify-between mb-1.5">
                                    <span class="text-xs text-gray-400">Progres Penjualan</span>
                                    <span class="text-xs font-medium text-gray-600">
                                        {{ Math.round(((detailDrawer.data.terjual ?? 0) / (detailDrawer.data.stok ?? 1)) * 100) }}%
                                    </span>
                                </div>
                                <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                                    <div class="h-full bg-indigo-500 rounded-full transition-all duration-500"
                                        :style="{ width: Math.min(((detailDrawer.data.terjual ?? 0) / (detailDrawer.data.stok ?? 1)) * 100, 100) + '%' }">
                                    </div>
                                </div>
                            </div>

                            <!-- Specs -->
                            <div v-if="detailDrawer.data.specs && Object.keys(detailDrawer.data.specs).length">
                                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Spesifikasi</p>
                                <div class="bg-gray-50 rounded-xl border border-gray-100 overflow-hidden">
                                    <div v-for="(value, key, idx) in detailDrawer.data.specs" :key="key"
                                        :class="['flex items-start px-4 py-2.5', idx % 2 === 0 ? 'bg-transparent' : 'bg-white/60']">
                                        <span class="text-xs text-gray-500 font-medium min-w-[120px] capitalize">{{ key }}</span>
                                        <span class="text-xs text-gray-800 font-semibold">{{ value }}</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Description -->
                            <div v-if="detailDrawer.data.description">
                                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Deskripsi</p>
                                <p class="text-sm text-gray-600 leading-relaxed">{{ detailDrawer.data.description }}</p>
                            </div>

                            <!-- Timestamps -->
                            <div class="grid grid-cols-2 gap-3 pt-2 border-t border-gray-100">
                                <div>
                                    <p class="text-xs text-gray-400">Dibuat</p>
                                    <p class="text-xs font-medium text-gray-600 mt-0.5">{{ formatDate(detailDrawer.data.created_at) }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-400">Diperbarui</p>
                                    <p class="text-xs font-medium text-gray-600 mt-0.5">{{ formatDate(detailDrawer.data.updated_at) }}</p>
                                </div>
                            </div>

                            <!-- Danger Zone -->
                            <div class="pt-2 border-t border-gray-100">
                                <button @click="confirmDelete(detailDrawer.item); detailDrawer.show = false"
                                    class="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-semibold text-red-600 border border-red-100 rounded-xl hover:bg-red-50 transition-colors">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                    Hapus Produk Ini
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </Transition>
        </Teleport>

        <!-- ── Quick Edit Modal ────────────────────── -->
        <Teleport to="body">
            <Transition name="modal">
                <div v-if="quickEdit.show"
                    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
                    @click.self="quickEdit.show = false">
                    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 space-y-5">
                        <div class="flex items-center justify-between">
                            <h3 class="text-base font-bold text-gray-900">Edit Cepat</h3>
                            <button @click="quickEdit.show = false" class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                            <div class="w-12 h-12 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0 border border-gray-100">
                                <img v-if="quickEdit.item?.image || quickEdit.item?.cover_image_url"
                                    :src="quickEdit.item.image || quickEdit.item.cover_image_url"
                                    class="w-full h-full object-cover" />
                                <div v-else class="w-full h-full flex items-center justify-center">
                                    <svg class="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16" />
                                    </svg>
                                </div>
                            </div>
                            <div class="min-w-0">
                                <p class="font-semibold text-gray-800 text-sm truncate">{{ quickEdit.item?.title }}</p>
                                <p class="text-xs text-gray-400 mt-0.5">{{ quickEdit.item?.brand || 'No Brand' }}</p>
                            </div>
                        </div>
                        <div class="space-y-4">
                            <div>
                                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Jumlah Stok</label>
                                <input v-model.number="quickEdit.stok" type="number" min="0"
                                    class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent" />
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Harga Online</label>
                                <div class="relative">
                                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-semibold text-gray-400">Rp</span>
                                    <input v-model.number="quickEdit.price" type="number" min="0"
                                        class="w-full pl-10 pr-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent" />
                                </div>
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-600 mb-1.5">Diskon (%)</label>
                                <input v-model.number="quickEdit.discount" type="number" min="0" max="100"
                                    class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent" />
                            </div>
                        </div>
                        <div class="flex gap-3">
                            <button @click="quickEdit.show = false"
                                class="flex-1 px-4 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
                                Batal
                            </button>
                            <button @click="doQuickEdit" :disabled="quickEdit.loading"
                                class="flex-1 px-4 py-2.5 text-sm font-bold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 disabled:opacity-60 active:scale-95 transition-all">
                                <span v-if="quickEdit.loading" class="flex items-center justify-center gap-2">
                                    <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                    Menyimpan...
                                </span>
                                <span v-else>Simpan</span>
                            </button>
                        </div>
                    </div>
                </div>
            </Transition>
        </Teleport>

        <!-- ── Delete Modal ────────────────────── -->
        <Teleport to="body">
            <Transition name="modal">
                <div v-if="deleteModal.show"
                    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
                    @click.self="deleteModal.show = false">
                    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-5">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                                <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <div>
                                <h3 class="text-base font-bold text-gray-900">
                                    {{ deleteModal.isBulk ? `Hapus ${selectedIds.length} Produk` : 'Hapus Produk' }}
                                </h3>
                                <p class="text-sm text-gray-400 mt-0.5">Tindakan ini tidak bisa dibatalkan</p>
                            </div>
                        </div>
                        <p class="text-sm text-gray-600 bg-gray-50 px-4 py-3 rounded-xl border border-gray-100">
                            <span v-if="deleteModal.isBulk">
                                Apakah kamu yakin ingin menghapus <span class="font-bold text-gray-800">{{ selectedIds.length }} produk</span> yang dipilih?
                            </span>
                            <span v-else>
                                Apakah kamu yakin ingin menghapus <span class="font-bold text-gray-800">{{ deleteModal.item?.title }}</span>?
                            </span>
                        </p>
                        <div class="flex gap-3 pt-1">
                            <button @click="deleteModal.show = false"
                                class="flex-1 px-4 py-2.5 text-sm font-medium text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
                                Batal
                            </button>
                            <button @click="doDelete" :disabled="deleteModal.loading"
                                class="flex-1 px-4 py-2.5 text-sm font-bold text-white bg-red-500 rounded-xl hover:bg-red-600 disabled:opacity-60 active:scale-95 transition-all">
                                <span v-if="deleteModal.loading" class="flex items-center justify-center gap-2">
                                    <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                    Menghapus...
                                </span>
                                <span v-else>Ya, Hapus</span>
                            </button>
                        </div>
                    </div>
                </div>
            </Transition>
        </Teleport>

        <!-- ── Toast ──────────────────────────── -->
        <Teleport to="body">
            <Transition name="toast">
                <div v-if="toast.show" :class="[
                    'fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-2xl text-sm font-semibold max-w-sm',
                    toast.type === 'success' ? 'bg-gray-900 text-white' : 'bg-red-600 text-white'
                ]">
                    <div :class="['w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-black', toast.type === 'success' ? 'bg-emerald-500' : 'bg-red-400']">
                        {{ toast.type === 'success' ? '✓' : '✕' }}
                    </div>
                    {{ toast.message }}
                </div>
            </Transition>
        </Teleport>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { brandApi, categoryApi, stockApi } from '@/service/stock'
import api from '@/service/api'

// ── State ──────────────────────────────────────────────────────────
const stocks = ref([])
const brands = ref([])
const categories = ref([])
const loading = ref(true)
const selectedIds = ref([])
const selectAll = ref(false)

// Kategori dropdown
const categorySearch = ref('')
const categoryDropdownOpen = ref(false)
const categoryDropdownRef = ref(null)

const filters = reactive({
    q: '', brand: '', cat: '', min_price: null, max_price: null,
    sort: 'newest', is_active: '', stock_status: ''
})
const pagination = reactive({ page: 1, size: 20, total: 0, totalPages: 1 })

const deleteModal = reactive({ show: false, item: null, loading: false, isBulk: false })
const quickEdit = reactive({ show: false, item: null, stok: 0, price: 0, discount: 0, loading: false })
const toast = reactive({ show: false, type: 'success', message: '' })

const detailDrawer = reactive({
    show: false, item: null, data: null, loading: false, activeImg: 0,
})

// ── Computed ───────────────────────────────────────────────────────
const filteredCategories = computed(() => {
    if (!categorySearch.value) return categories.value
    const q = categorySearch.value.toLowerCase()
    return categories.value.filter(c =>
        (c.name || c.slug || '').toLowerCase().includes(q)
    )
})

const activeFilterCount = computed(() => {
    let count = 0
    if (filters.q) count++
    if (filters.cat) count++
    if (filters.brand) count++
    if (filters.stock_status) count++
    if (filters.is_active !== '') count++
    return count
})

const stats = computed(() => [
    {
        label: 'Total Produk', value: pagination.total.toLocaleString('id'),
        sub: 'di database', change: 1,
        icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10',
        iconBg: 'bg-indigo-50', iconColor: 'text-indigo-500'
    },
    {
        label: 'Tayang (Aktif)', value: stocks.value.filter(s => s.is_active).length,
        sub: `dari ${stocks.value.length} di halaman ini`, change: 1,
        icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
        iconBg: 'bg-blue-50', iconColor: 'text-blue-500'
    },
    {
        label: 'Stok Kosong', value: stocks.value.filter(s => s.status_stok === 'habis' || (s.sisa ?? s.stok ?? 0) === 0).length,
        sub: 'perlu diisi ulang', change: -1,
        icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
        iconBg: 'bg-red-50', iconColor: 'text-red-400'
    },
    {
        label: 'Total Terjual', value: stocks.value.reduce((acc, s) => acc + (s.terjual ?? 0), 0).toLocaleString('id'),
        sub: 'dari semua produk di halaman', change: 1,
        icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
        iconBg: 'bg-emerald-50', iconColor: 'text-emerald-500'
    },
])

const visiblePages = computed(() => {
    const { page, totalPages } = pagination
    if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
    const pages = []
    if (page <= 4) {
        for (let i = 1; i <= Math.min(5, totalPages); i++) pages.push(i)
        pages.push('...')
        pages.push(totalPages)
    } else if (page >= totalPages - 3) {
        pages.push(1); pages.push('...')
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i)
    } else {
        pages.push(1); pages.push('...')
        for (let i = page - 1; i <= page + 1; i++) pages.push(i)
        pages.push('...'); pages.push(totalPages)
    }
    return pages
})

// ── Helpers ────────────────────────────────────────────────────────
function soldPercent(item) {
    const total = item.stok ?? 0
    const sold = item.terjual ?? 0
    if (!total) return 0
    return Math.min(Math.round((sold / total) * 100), 100)
}

function stockBadgeClass(item) {
    const sisa = item.sisa ?? item.stok ?? 0
    if (sisa === 0) return 'bg-red-100 text-red-600'
    if (sisa <= 5) return 'bg-amber-100 text-amber-700'
    return 'bg-emerald-100 text-emerald-700'
}

function stockDotClass(item) {
    const sisa = item.sisa ?? item.stok ?? 0
    if (sisa === 0) return 'bg-red-500'
    if (sisa <= 5) return 'bg-amber-500'
    return 'bg-emerald-500'
}

function stockLabel(item) {
    const sisa = item.sisa ?? item.stok ?? 0
    if (sisa === 0) return 'Kosong'
    if (sisa <= 5) return `Sisa ${sisa}`
    return 'Tersedia'
}

// ── Category Dropdown ──────────────────────────────────────────────
function selectCategory(slug) {
    filters.cat = slug
    categorySearch.value = slug
        ? (categories.value.find(c => c.slug === slug)?.name || slug)
        : ''
    categoryDropdownOpen.value = false
    resetPageAndFetch()
}

function clearCategory() {
    filters.cat = ''
    categorySearch.value = ''
    categoryDropdownOpen.value = false
    resetPageAndFetch()
}

// Click outside to close dropdown
function handleClickOutside(e) {
    if (categoryDropdownRef.value && !categoryDropdownRef.value.contains(e.target)) {
        categoryDropdownOpen.value = false
    }
}

// Quick filter by clicking category badge in table
function quickFilterCategory(slug) {
    if (!slug) return
    filters.cat = slug
    categorySearch.value = categories.value.find(c => c.slug === slug)?.name || slug
    resetPageAndFetch()
    showToast(`Filter kategori: ${slug}`)
}

// ── Methods ────────────────────────────────────────────────────────
async function fetchStocks() {
    loading.value = true
    try {
        const params = { page: pagination.page, size: pagination.size, sort: filters.sort }
        if (filters.q) params.q = filters.q
        if (filters.brand) params.brand = filters.brand
        if (filters.cat) params.cat = filters.cat
        if (filters.min_price) params.min_price = filters.min_price
        if (filters.max_price) params.max_price = filters.max_price
        if (filters.is_active !== '') params.is_active = filters.is_active === 'true'
        // ★ Ketersediaan dikirim ke backend agar di-filter via Elasticsearch
        if (filters.stock_status) params.stock_status = filters.stock_status

        const res = await api.get('stok/admin/stocks', { params })
        const payload = res.data || res
        stocks.value = payload.items || payload.data || []
        pagination.total = payload.total || 0
        pagination.totalPages = Math.max(1, Math.ceil(pagination.total / pagination.size))
    } catch (e) {
        console.error(e)
        showToast('Gagal memuat data stok', 'error')
    } finally {
        loading.value = false
    }
}

async function fetchBrands() {
    try {
        const res = await brandApi.list()
        const payload = res.data || res
        brands.value = Array.isArray(payload) ? payload : (payload.data || payload.items || [])
    } catch { }
}

async function fetchCategories() {
    try {
        const res = await categoryApi.list()
        const payload = res.data || res
        categories.value = Array.isArray(payload) ? payload : (payload.data || payload.items || [])
    } catch { }
}

let debounceTimer = null
function debouncedFetch() {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => { pagination.page = 1; fetchStocks() }, 400)
}

function resetPageAndFetch() {
    pagination.page = 1
    fetchStocks()
}

function resetFilters() {
    Object.assign(filters, {
        q: '', brand: '', cat: '', min_price: null, max_price: null,
        sort: 'newest', is_active: '', stock_status: ''
    })
    categorySearch.value = ''
    pagination.page = 1
    fetchStocks()
}

function changePage(p) {
    if (p < 1 || p > pagination.totalPages) return
    pagination.page = p
    fetchStocks()
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

function toggleSelectAll() {
    selectedIds.value = selectAll.value ? stocks.value.map(s => s.uuid) : []
}

// ── Detail Drawer ──────────────────────────────────────────────────
async function openDetailDrawer(item) {
    detailDrawer.item = item
    detailDrawer.show = true
    detailDrawer.activeImg = 0
    if (detailDrawer.data?.uuid === item.uuid) return

    detailDrawer.data = null
    detailDrawer.loading = true
    try {
        const res = await api.get(`stok/public/detail/${item.uuid}`)
        const payload = res.data || res
        detailDrawer.data = payload.data || payload
    } catch (e) {
        console.error(e)
        detailDrawer.data = {
            ...item,
            images: item.image ? [item.image] : [],
            online_price: item.price || item.online_price,
        }
    } finally {
        detailDrawer.loading = false
    }
}

const editUrl = computed(() =>
    detailDrawer.item?.uuid ? `/stock/${detailDrawer.item.uuid}/edit` : null
)

// ── Quick Edit ─────────────────────────────────────────────────────
function openQuickEdit(item) {
    quickEdit.item = item
    quickEdit.stok = item.stok ?? 0
    quickEdit.price = item.price || item.online_price || 0
    quickEdit.discount = item.discount_percentage || 0
    quickEdit.show = true
}

async function doQuickEdit() {
    if (!quickEdit.item) return
    quickEdit.loading = true
    try {
        const formData = new FormData()
        formData.append('stok', quickEdit.stok)
        formData.append('online_price', quickEdit.price)
        formData.append('discount_percentage', quickEdit.discount)
        await stockApi.update(quickEdit.item.uuid, formData)
        showToast('Stok berhasil diperbarui')
        quickEdit.show = false
        if (detailDrawer.data?.uuid === quickEdit.item.uuid) {
            detailDrawer.data = null
        }
        fetchStocks()
    } catch (e) {
        console.error(e)
        showToast('Gagal memperbarui stok', 'error')
    } finally {
        quickEdit.loading = false
    }
}

// ── Delete ────────────────────────────────────────────────────────
function confirmDelete(item) {
    deleteModal.item = item
    deleteModal.isBulk = false
    deleteModal.show = true
}

function confirmBulkDelete() {
    deleteModal.isBulk = true
    deleteModal.show = true
}

async function doDelete() {
    deleteModal.loading = true
    try {
        if (deleteModal.isBulk) {
            await Promise.all(selectedIds.value.map(id => api.delete(`/stok/admin/delete/${id}`)))
            showToast(`${selectedIds.value.length} produk berhasil dihapus`)
            selectedIds.value = []
            selectAll.value = false
        } else {
            await api.delete(`/stok/admin/delete/${deleteModal.item.uuid}`)
            showToast('Produk berhasil dihapus')
        }
        deleteModal.show = false
        fetchStocks()
    } catch (e) {
        console.error(e)
        showToast('Gagal menghapus produk', 'error')
    } finally {
        deleteModal.loading = false
    }
}

// ── Formatters ────────────────────────────────────────────────────
function formatPrice(val) {
    if (!val && val !== 0) return 'Rp 0'
    return 'Rp ' + Number(val).toLocaleString('id-ID')
}

function formatDate(val) {
    if (!val) return '—'
    return new Date(val).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

function showToast(message, type = 'success') {
    toast.show = true; toast.type = type; toast.message = message
    setTimeout(() => toast.show = false, 3500)
}

// ── Lifecycle ──────────────────────────────────────────────────────
onMounted(() => {
    fetchStocks()
    fetchBrands()
    fetchCategories()
    document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
@reference "tailwindcss";

/* Modal */
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

/* Drawer Overlay */
.drawer-overlay-enter-active, .drawer-overlay-leave-active { transition: opacity 0.25s ease; }
.drawer-overlay-enter-from, .drawer-overlay-leave-to { opacity: 0; }

/* Drawer Panel */
.drawer-panel-enter-active, .drawer-panel-leave-active { transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.drawer-panel-enter-from, .drawer-panel-leave-to { transform: translateX(100%); }

/* Toast */
.toast-enter-active, .toast-leave-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(100%) scale(0.9); }

/* Category dropdown */
.dropdown-enter-active, .dropdown-leave-active { transition: all 0.15s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-4px); }
</style>