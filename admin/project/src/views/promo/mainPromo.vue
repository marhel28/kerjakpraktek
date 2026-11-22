<template>
    <div class="h-full max-w-7xl mx-auto flex flex-col font-sans text-gray-800">
  
      <!-- ══════════════════════════ HEADER ══════════════════════════ -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-gray-900">Manajemen Promo</h1>
          <p class="mt-1 text-sm text-gray-500">Kelola promo, diskon, dan flash sale untuk toko Anda.</p>
        </div>
        <button @click="openPromoModal()"
          class="inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow-sm hover:bg-indigo-700 active:scale-95 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 shrink-0">
          <svg class="w-5 h-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Buat Promo
        </button>
      </div>
  
      <!-- ══════════════════════════ STATS CARDS ══════════════════════════ -->
      <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
          <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Promo Aktif</p>
          <p class="text-2xl font-bold text-gray-900 mt-1">{{ stats.active_promos }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
          <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Total Order</p>
          <p class="text-2xl font-bold text-gray-900 mt-1">{{ stats.total_promo_orders }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
          <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Revenue Promo</p>
          <p class="text-2xl font-bold text-emerald-600 mt-1">{{ formatRp(stats.total_revenue_from_promo) }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
          <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Total Hemat</p>
          <p class="text-2xl font-bold text-rose-500 mt-1">{{ formatRp(stats.total_customer_savings) }}</p>
        </div>
      </div>
      <!-- Stats skeleton -->
      <div v-else class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div v-for="i in 4" :key="i" class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 animate-pulse">
          <div class="h-3 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div class="h-7 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
  
      <!-- ══════════════════════════ TOP PROMOS ══════════════════════════ -->
      <div v-if="stats && stats.top_promos_by_usage && stats.top_promos_by_usage.length > 0"
        class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 mb-6">
        <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Top Promo by Usage</p>
        <div class="flex flex-wrap gap-2">
          <div v-for="tp in stats.top_promos_by_usage" :key="tp.uuid"
            class="flex items-center gap-2 px-3 py-1.5 bg-indigo-50 border border-indigo-100 rounded-xl">
            <span class="text-xs font-semibold text-indigo-700 truncate max-w-[120px]">{{ tp.name }}</span>
            <span class="text-xs text-indigo-400 font-mono">{{ tp.used_count }}x</span>
          </div>
        </div>
      </div>
  
      <!-- ══════════════════════════ FILTER & SEARCH ══════════════════════════ -->
      <div class="flex flex-col sm:flex-row gap-3 mb-5">
        <div class="relative flex-1">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none"
            viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input v-model="searchQuery" type="text" placeholder="Cari nama promo..."
            class="block w-full pl-9 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all" />
        </div>
        <select v-model="filterStatus"
          class="px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-700 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all">
          <option value="">Semua Status</option>
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="archived">Archived</option>
        </select>
        <select v-model="filterType"
          class="px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-700 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all">
          <option value="">Semua Tipe</option>
          <option value="percentage">Percentage</option>
          <option value="fixed">Fixed</option>
          <option value="bogo">BOGO</option>
          <option value="bundle_disc">Bundle Disc</option>
          <option value="flash_sale">Flash Sale</option>
        </select>
      </div>
  
      <!-- ══════════════════════════ TABLE SKELETON ══════════════════════════ -->
      <div v-if="isLoading" class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div class="p-4 border-b border-gray-100 animate-pulse flex gap-4">
          <div class="h-4 bg-gray-200 rounded w-1/4"></div>
          <div class="h-4 bg-gray-200 rounded w-1/6"></div>
          <div class="h-4 bg-gray-200 rounded w-1/6"></div>
        </div>
        <div v-for="i in 5" :key="i" class="p-4 border-b border-gray-50 animate-pulse flex gap-4 items-center">
          <div class="h-8 w-8 bg-gray-100 rounded-xl shrink-0"></div>
          <div class="flex-1 space-y-2">
            <div class="h-4 bg-gray-200 rounded w-2/5"></div>
            <div class="h-3 bg-gray-100 rounded w-1/4"></div>
          </div>
          <div class="h-6 bg-gray-100 rounded-full w-20"></div>
          <div class="h-6 bg-gray-100 rounded w-16"></div>
        </div>
      </div>
  
      <!-- ══════════════════════════ EMPTY STATE ══════════════════════════ -->
      <div v-else-if="filteredPromos.length === 0"
        class="flex-1 flex flex-col items-center justify-center py-20 bg-white border border-gray-200 border-dashed rounded-2xl">
        <div class="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        </div>
        <h3 class="text-base font-semibold text-gray-900">Belum ada promo</h3>
        <p class="mt-1 text-sm text-gray-500">Buat promo pertama untuk menarik lebih banyak pelanggan.</p>
        <button @click="openPromoModal()" class="mt-5 text-sm font-semibold text-indigo-600 hover:text-indigo-500">
          + Buat Promo Sekarang
        </button>
      </div>
  
      <!-- ══════════════════════════ PROMO TABLE ══════════════════════════ -->
      <div v-else class="bg-white rounded-2xl border border-gray-200 shadow-sm ">
        <div class="overflow-x-auto">
          <table class="min-w-full">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50/60">
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Promo</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Tipe</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Diskon</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Periode</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Kuota</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="promo in paginatedPromos" :key="promo.uuid"
                class="hover:bg-gray-50/80 transition-colors duration-100 group">
                <!-- Name & Slug -->
                <td class="px-4 py-3.5">
                  <div class="flex items-center gap-3">
                    <div :class="promoTypeIcon(promo.promo_type).bg"
                      class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0">
                      <span :class="promoTypeIcon(promo.promo_type).text" class="text-sm font-bold">
                        {{ promoTypeIcon(promo.promo_type).label }}
                      </span>
                    </div>
                    <div>
                      <p class="font-semibold text-gray-900 text-sm">{{ promo.name }}</p>
                      <p class="text-xs text-gray-400 mt-0.5">{{ promo.slug }}</p>
                    </div>
                    <span v-if="promo.is_flash_sale"
                      class="ml-1 inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700">
                      ⚡ Flash
                    </span>
                  </div>
                </td>
                <!-- Tipe -->
                <td class="px-4 py-3.5">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
                    :class="promoTypeColor(promo.promo_type)">
                    {{ promoTypeLabel(promo.promo_type) }}
                  </span>
                </td>
                <!-- Diskon -->
                <td class="px-4 py-3.5">
                  <p class="text-sm font-bold text-gray-900">
                    <template v-if="promo.promo_type === 'bogo'">Beli {{ promo.buy_quantity }} Gratis {{ promo.get_quantity }}</template>
                    <template v-else-if="promo.promo_type === 'fixed'">{{ formatRp(promo.discount_value) }}</template>
                    <template v-else>{{ promo.discount_value }}%</template>
                  </p>
                  <p v-if="promo.max_discount" class="text-[11px] text-gray-400">maks. {{ formatRp(promo.max_discount) }}</p>
                </td>
                <!-- Periode -->
                <td class="px-4 py-3.5">
                  <p class="text-xs text-gray-700">{{ formatDate(promo.valid_from) }}</p>
                  <p class="text-xs text-gray-400">s/d {{ formatDate(promo.valid_until) }}</p>
                </td>
                <!-- Kuota -->
                <td class="px-4 py-3.5">
                  <div v-if="promo.quota">
                    <div class="flex items-center gap-2">
                      <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden" style="min-width:60px">
                        <div class="h-full rounded-full transition-all duration-500"
                          :class="quotaPercent(promo) > 80 ? 'bg-rose-400' : 'bg-indigo-400'"
                          :style="`width:${quotaPercent(promo)}%`"></div>
                      </div>
                      <span class="text-xs text-gray-500 tabular-nums">{{ promo.used_count }}/{{ promo.quota }}</span>
                    </div>
                  </div>
                  <span v-else class="text-xs text-gray-400">Tak terbatas</span>
                </td>
                <!-- Status -->
                <td class="px-4 py-3.5">
                  <span :class="statusBadge(promo.status)"
                    class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold">
                    {{ statusLabel(promo.status) }}
                  </span>
                </td>
                <!-- Actions -->
                <td class="px-4 py-3.5 text-right">
                  <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <!-- Detail -->
                    <button @click="openDetailDrawer(promo)" title="Lihat Detail"
                      class="p-1.5 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <!-- Items -->
                    <button @click="openItemsDrawer(promo)" title="Kelola Item"
                      class="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                      </svg>
                    </button>
                    <!-- Notify -->
                    <button @click="sendNotif(promo)" title="Kirim Notifikasi ke User"
                      class="p-1.5 text-gray-400 hover:text-sky-600 hover:bg-sky-50 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round"
                          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                    </button>
                    <!-- Edit -->
                    <button @click="openPromoModal(promo)" title="Edit Promo"
                      class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round"
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <!-- Publish -->
                    <button v-if="promo.status === 'draft' || promo.status === 'paused'"
                      @click="publishPromo(promo)" title="Publish"
                      class="p-1.5 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </button>
                    <!-- Pause -->
                    <button v-if="promo.status === 'active'" @click="pausePromo(promo)" title="Pause"
                      class="p-1.5 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M10 9v6m4-6v6" />
                      </svg>
                    </button>
                    <!-- Delete -->
                    <button @click="confirmDelete(promo)" title="Hapus"
                      class="p-1.5 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round"
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
  
        <!-- Pagination -->
        <div class="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50/40">
          <p class="text-sm text-gray-500">
            Menampilkan <span class="font-semibold text-gray-700">{{ paginationFrom }}–{{ paginationTo }}</span>
            dari <span class="font-semibold text-gray-700">{{ filteredPromos.length }}</span> promo
          </p>
          <div class="flex gap-1">
            <button @click="currentPage--" :disabled="currentPage === 1"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg bg-white disabled:opacity-40 hover:bg-gray-50 transition-colors">←</button>
            <button v-for="p in totalPages" :key="p" @click="currentPage = p"
              :class="p === currentPage ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'"
              class="px-3 py-1.5 text-sm border rounded-lg transition-colors">{{ p }}</button>
            <button @click="currentPage++" :disabled="currentPage === totalPages"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg bg-white disabled:opacity-40 hover:bg-gray-50 transition-colors">→</button>
          </div>
        </div>
      </div>
  
  
      <!-- ══════════════════════════════════════════════════════════
           MODAL: BUAT / EDIT PROMO
      ═══════════════════════════════════════════════════════════ -->
      <teleport to="body">
        <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0"
          enter-to-class="opacity-100" leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100" leave-to-class="opacity-0">
          <div v-if="isPromoModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm" @click="closePromoModal"></div>
            <div
              class="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl border border-gray-100 flex flex-col max-h-[92vh]">
  
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50 rounded-t-2xl">
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ editingPromoId ? 'Edit Promo' : 'Buat Promo Baru' }}
                </h3>
                <button @click="closePromoModal" class="text-gray-400 hover:text-gray-600 focus:outline-none">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
  
              <!-- Form Body -->
              <div class="p-6 overflow-y-auto custom-scrollbar space-y-5">
  
                <!-- Nama & Slug -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Nama Promo <span class="text-rose-500">*</span></label>
                    <input v-model="promoForm.name" @input="autoSlug" type="text"
                      placeholder="Flash Sale Kamera 25% OFF" class="input-field" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Slug</label>
                    <input v-model="promoForm.slug" type="text" placeholder="flash-sale-kamera-25-off"
                      class="input-field font-mono text-xs" />
                  </div>
                </div>
  
                <!-- Deskripsi -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Deskripsi</label>
                  <textarea v-model="promoForm.description" rows="2" placeholder="Deskripsi singkat promo..."
                    class="input-field resize-none"></textarea>
                </div>
  
                <!-- Banner Upload -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Banner Promo</label>
                  
                  <!-- Jika sudah ada URL Banner -->
                  <div v-if="promoForm.banner_url" class="relative w-full max-w-xs rounded-xl overflow-hidden border border-gray-200">
                    <img :src="promoForm.banner_url" alt="Banner Preview" class="w-full h-auto object-cover" />
                    <button @click="removeBanner" type="button" 
                      class="absolute top-2 right-2 p-1.5 bg-gray-900/60 hover:bg-rose-500 text-white rounded-lg backdrop-blur-sm transition-colors duration-200">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
  
                  <!-- Input Upload -->
                  <div v-else class="flex flex-col gap-2">
                    <input type="file" ref="bannerInput" @change="handleBannerUpload" accept="image/*" class="hidden" />
                    <button type="button" @click="$refs.bannerInput.click()" :disabled="isUploadingBanner" 
                      class="w-full max-w-xs py-3 px-4 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 hover:bg-indigo-50 hover:border-indigo-300 hover:text-indigo-600 disabled:opacity-50 transition-all flex flex-col items-center justify-center gap-1">
                      <svg v-if="isUploadingBanner" class="animate-spin h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                      </svg>
                      <svg v-else class="h-6 w-6 text-gray-400 group-hover:text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                      </svg>
                      <span class="text-sm font-medium text-gray-600">{{ isUploadingBanner ? 'Mengunggah...' : 'Klik untuk Upload Gambar' }}</span>
                    </button>
                    <span class="text-[11px] text-gray-400">Format: JPG, PNG, WEBP (Maksimal 2MB)</span>
                  </div>
                </div>
  
                <!-- Tipe, Target -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Tipe Promo <span class="text-rose-500">*</span></label>
                    <select v-model="promoForm.promo_type" class="input-field">
                      <option value="percentage">Percentage (%)</option>
                      <option value="fixed">Fixed (Rp)</option>
                      <option value="bogo">BOGO (Beli X Gratis Y)</option>
                      <option value="bundle_disc">Bundle Disc</option>
                      <option value="flash_sale">Flash Sale</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Target</label>
                    <select v-model="promoForm.target" class="input-field">
                      <option value="all">Semua (Produk + Jasa)</option>
                      <option value="stock">Produk Fisik</option>
                      <option value="service_package">Paket Jasa</option>
                    </select>
                  </div>
                </div>
  
                <!-- Nilai Diskon Section -->
                <div class="p-4 bg-indigo-50/60 border border-indigo-100 rounded-xl space-y-3">
                  <p class="text-sm font-semibold text-indigo-800">Konfigurasi Diskon</p>
                  <div v-if="promoForm.promo_type !== 'bogo'" class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">
                        {{ promoForm.promo_type === 'fixed' ? 'Potongan (Rp)' : 'Diskon (%)' }}
                        <span class="text-rose-500">*</span>
                      </label>
                      <input v-model.number="promoForm.discount_value" type="number" min="0"
                        :placeholder="promoForm.promo_type === 'fixed' ? '200000' : '25'" class="input-field" />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Maks. Diskon (Rp)</label>
                      <input v-model.number="promoForm.max_discount" type="number" min="0" placeholder="Opsional"
                        class="input-field" />
                    </div>
                  </div>
                  <div v-if="promoForm.promo_type === 'bogo'" class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Beli (qty) <span class="text-rose-500">*</span></label>
                      <input v-model.number="promoForm.buy_quantity" type="number" min="1" placeholder="2" class="input-field" />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Gratis (qty) <span class="text-rose-500">*</span></label>
                      <input v-model.number="promoForm.get_quantity" type="number" min="1" placeholder="1" class="input-field" />
                    </div>
                  </div>
                </div>
  
                <!-- Min Purchase & Min Qty -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Min. Pembelian (Rp)</label>
                    <input v-model.number="promoForm.min_purchase" type="number" min="0" placeholder="0" class="input-field" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Min. Qty Item</label>
                    <input v-model.number="promoForm.min_qty" type="number" min="1" placeholder="1" class="input-field" />
                  </div>
                </div>
  
                <!-- Kuota & Max Use Per User -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Kuota Total</label>
                    <input v-model.number="promoForm.quota" type="number" min="1" placeholder="Tak terbatas" class="input-field" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Maks. / User</label>
                    <input v-model.number="promoForm.max_use_per_user" type="number" min="1" placeholder="Tak terbatas" class="input-field" />
                  </div>
                </div>
  
                <!-- Periode -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Mulai <span class="text-rose-500">*</span></label>
                    <input v-model="promoForm.valid_from" type="datetime-local" class="input-field" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Berakhir <span class="text-rose-500">*</span></label>
                    <input v-model="promoForm.valid_until" type="datetime-local" class="input-field" />
                  </div>
                </div>
  
                <!-- Flash Sale -->
                <div class="flex items-center gap-4 p-3 bg-amber-50 border border-amber-100 rounded-xl">
                  <div class="flex-1">
                    <p class="text-sm font-medium text-amber-900">Flash Sale</p>
                    <p class="text-xs text-amber-600">Tampilkan kuota dan urgency di halaman publik</p>
                  </div>
                  <button type="button" @click="promoForm.is_flash_sale = !promoForm.is_flash_sale"
                    :class="promoForm.is_flash_sale ? 'bg-amber-500' : 'bg-gray-200'"
                    class="relative inline-flex h-6 w-11 shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none">
                    <span :class="promoForm.is_flash_sale ? 'translate-x-5' : 'translate-x-0'"
                      class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200"></span>
                  </button>
                </div>
                <div v-if="promoForm.is_flash_sale">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">Kuota Flash Sale</label>
                  <input v-model.number="promoForm.flash_sale_quota" type="number" min="1" placeholder="Contoh: 50"
                    class="input-field" />
                </div>
  
                <!-- Prioritas -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">Prioritas</label>
                    <input v-model.number="promoForm.priority" type="number" min="0" placeholder="0" class="input-field" />
                    <p class="text-xs text-gray-400 mt-1">Angka lebih tinggi = tampil lebih dulu</p>
                  </div>
                </div>
  
              </div>
  
              <!-- Modal Footer -->
              <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3 rounded-b-2xl shrink-0">
                <button @click="closePromoModal"
                  class="px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 active:scale-95 transition-all">
                  Batal
                </button>
                <button @click="savePromo" :disabled="isSubmitting || isUploadingBanner"
                  class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed transition-all flex items-center min-w-[120px] justify-center">
                  <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                  </svg>
                  {{ isSubmitting ? 'Menyimpan...' : (editingPromoId ? 'Simpan Perubahan' : 'Buat Promo') }}
                </button>
              </div>
            </div>
          </div>
        </transition>
      </teleport>
  
  
      <!-- ══════════════════════════════════════════════════════════
           DRAWER: DETAIL PROMO
      ═══════════════════════════════════════════════════════════ -->
      <teleport to="body">
        <transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 translate-x-8"
          enter-to-class="opacity-100 translate-x-0" leave-active-class="transition duration-200 ease-in"
          leave-from-class="opacity-100 translate-x-0" leave-to-class="opacity-0 translate-x-8">
          <div v-if="isDetailDrawerOpen" class="fixed inset-0 z-50 flex justify-end">
            <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeDetailDrawer"></div>
            <div class="relative bg-white w-full max-w-md h-full shadow-2xl flex flex-col">
  
              <!-- Drawer Header -->
              <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 bg-gray-50/50 shrink-0">
                <div>
                  <h3 class="text-base font-semibold text-gray-900">Detail Promo</h3>
                  <p class="text-xs text-gray-500 mt-0.5 truncate max-w-[260px]">{{ activeDetailPromo?.name }}</p>
                </div>
                <button @click="closeDetailDrawer" class="text-gray-400 hover:text-gray-600">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
  
              <!-- Drawer Body -->
              <div v-if="isDetailLoading" class="flex-1 flex items-center justify-center">
                <div class="text-center">
                  <svg class="animate-spin h-8 w-8 text-indigo-500 mx-auto mb-3" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                  <p class="text-sm text-gray-400">Memuat detail...</p>
                </div>
              </div>
  
              <div v-else-if="activeDetailPromo" class="flex-1 overflow-y-auto custom-scrollbar p-5 space-y-5">
  
                <!-- Banner -->
                <div v-if="activeDetailPromo.banner_url" class="rounded-xl overflow-hidden border border-gray-100">
                  <img :src="activeDetailPromo.banner_url" alt="Banner Promo" class="w-full h-36 object-cover" />
                </div>
  
                <!-- Badge + Status -->
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
                    :class="promoTypeColor(activeDetailPromo.promo_type)">
                    {{ promoTypeLabel(activeDetailPromo.promo_type) }}
                  </span>
                  <span :class="statusBadge(activeDetailPromo.status)"
                    class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold">
                    {{ statusLabel(activeDetailPromo.status) }}
                  </span>
                  <span v-if="activeDetailPromo.is_flash_sale"
                    class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700">
                    ⚡ Flash Sale
                  </span>
                  <span v-if="!activeDetailPromo.is_valid"
                    class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-600">
                    ✗ Tidak Valid
                  </span>
                </div>
  
                <!-- Info Grid -->
                <div class="bg-gray-50 rounded-xl p-4 space-y-3">
                  <div class="flex justify-between items-start">
                    <span class="text-xs text-gray-500">Slug</span>
                    <span class="text-xs font-mono text-gray-700 text-right max-w-[200px] break-all">{{ activeDetailPromo.slug }}</span>
                  </div>
                  <div class="flex justify-between items-start">
                    <span class="text-xs text-gray-500">Deskripsi</span>
                    <span class="text-xs text-gray-700 text-right max-w-[200px]">{{ activeDetailPromo.description || '-' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-xs text-gray-500">Target</span>
                    <span class="text-xs font-semibold text-gray-700 capitalize">{{ activeDetailPromo.target }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-xs text-gray-500">Nilai Diskon</span>
                    <span class="text-xs font-bold text-gray-900">
                      <template v-if="activeDetailPromo.promo_type === 'bogo'">
                        Beli {{ activeDetailPromo.buy_quantity }} Gratis {{ activeDetailPromo.get_quantity }}
                      </template>
                      <template v-else-if="activeDetailPromo.promo_type === 'fixed'">
                        {{ formatRp(activeDetailPromo.discount_value) }}
                      </template>
                      <template v-else>{{ activeDetailPromo.discount_value }}%</template>
                    </span>
                  </div>
                  <div v-if="activeDetailPromo.max_discount" class="flex justify-between">
                    <span class="text-xs text-gray-500">Maks. Diskon</span>
                    <span class="text-xs text-gray-700">{{ formatRp(activeDetailPromo.max_discount) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-xs text-gray-500">Min. Pembelian</span>
                    <span class="text-xs text-gray-700">{{ formatRp(activeDetailPromo.min_purchase) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-xs text-gray-500">Min. Qty</span>
                    <span class="text-xs text-gray-700">{{ activeDetailPromo.min_qty }} item</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-xs text-gray-500">Maks. / User</span>
                    <span class="text-xs text-gray-700">{{ activeDetailPromo.max_use_per_user || 'Tak terbatas' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-xs text-gray-500">Periode</span>
                    <span class="text-xs text-gray-700 text-right">
                      {{ formatDate(activeDetailPromo.valid_from) }}<br/>
                      <span class="text-gray-400">s/d {{ formatDate(activeDetailPromo.valid_until) }}</span>
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-xs text-gray-500">Prioritas</span>
                    <span class="text-xs text-gray-700">{{ activeDetailPromo.priority }}</span>
                  </div>
                </div>
  
                <!-- Kuota Progress -->
                <div class="bg-indigo-50/60 border border-indigo-100 rounded-xl p-4">
                  <div class="flex justify-between mb-2">
                    <span class="text-xs font-semibold text-indigo-800">Penggunaan Kuota</span>
                    <span class="text-xs text-indigo-600 font-mono">
                      {{ activeDetailPromo.used_count }} / {{ activeDetailPromo.quota || '∞' }}
                    </span>
                  </div>
                  <div v-if="activeDetailPromo.quota" class="h-2 bg-indigo-100 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all"
                      :class="quotaPercent(activeDetailPromo) > 80 ? 'bg-rose-400' : 'bg-indigo-400'"
                      :style="`width:${quotaPercent(activeDetailPromo)}%`"></div>
                  </div>
                  <p v-if="activeDetailPromo.remaining_quota !== null" class="text-xs text-indigo-500 mt-1.5">
                    Sisa: {{ activeDetailPromo.remaining_quota }} slot
                  </p>
                  <div v-if="activeDetailPromo.is_flash_sale && activeDetailPromo.flash_sale_quota" class="mt-2 pt-2 border-t border-indigo-200">
                    <p class="text-xs text-amber-700 font-medium">⚡ Flash Sale Quota: {{ activeDetailPromo.flash_sale_quota }}</p>
                  </div>
                </div>
  
                <!-- Items List -->
                <div>
                  <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    Item Terikat ({{ activeDetailPromo.items?.length || 0 }})
                  </p>
                  <div v-if="!activeDetailPromo.items || activeDetailPromo.items.length === 0"
                    class="text-center py-6 text-sm text-gray-400 border border-dashed border-gray-200 rounded-xl">
                    Tidak ada item spesifik, promo berlaku untuk semua
                  </div>
                  <div v-else class="space-y-2">
                    <div v-for="item in activeDetailPromo.items" :key="item.uuid"
                      class="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-xl">
                      <img v-if="item.thumbnail_url" :src="item.thumbnail_url" alt="Thumbnail promo" class="w-10 h-10 rounded-lg object-cover shrink-0" />
                      <div v-else
                        :class="item.item_type === 'stock' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'"
                        class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 text-xs font-bold">
                        {{ item.item_type === 'stock' ? 'PRD' : 'PKG' }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">{{ item.item_name }}</p>
                        <p class="text-xs text-gray-400">{{ formatRp(item.item_price) }}</p>
                      </div>
                      <div v-if="item.override_discount_value" class="text-right">
                        <span class="text-xs font-semibold text-indigo-600">override</span>
                        <p class="text-xs text-gray-500">{{ item.override_discount_value }}</p>
                      </div>
                    </div>
                  </div>
                </div>
  
                <!-- Quick Actions -->
                <div class="grid grid-cols-2 gap-2 pt-2">
                  <button @click="closeDetailDrawer(); openPromoModal(activeDetailPromo)"
                    class="flex items-center justify-center gap-2 py-2.5 text-sm font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl transition-colors">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Edit Promo
                  </button>
                  <button @click="closeDetailDrawer(); openItemsDrawer(activeDetailPromo)"
                    class="flex items-center justify-center gap-2 py-2.5 text-sm font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-xl transition-colors">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                    </svg>
                    Kelola Item
                  </button>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </teleport>
  
  
      <!-- ══════════════════════════════════════════════════════════
           DRAWER: KELOLA ITEMS PROMO
      ═══════════════════════════════════════════════════════════ -->
      <teleport to="body">
        <transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 translate-x-8"
          enter-to-class="opacity-100 translate-x-0" leave-active-class="transition duration-200 ease-in"
          leave-from-class="opacity-100 translate-x-0" leave-to-class="opacity-0 translate-x-8">
          <div v-if="isItemsDrawerOpen" class="fixed inset-0 z-50 flex justify-end">
            <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeItemsDrawer"></div>
            <div class="relative bg-white w-full max-w-md h-full shadow-2xl flex flex-col">
  
              <!-- Drawer Header -->
              <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 bg-gray-50/50 shrink-0">
                <div>
                  <h3 class="text-base font-semibold text-gray-900">Item Promo</h3>
                  <p class="text-xs text-gray-500 mt-0.5 truncate max-w-[260px]">{{ activePromo?.name }}</p>
                </div>
                <button @click="closeItemsDrawer" class="text-gray-400 hover:text-gray-600">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
  
              <!-- Drawer Body -->
              <div class="flex-1 overflow-y-auto custom-scrollbar p-5 space-y-5">
  
                <!-- Tambah Item Form -->
                <div class="bg-indigo-50/60 border border-indigo-100 rounded-xl p-4 space-y-3">
                  <p class="text-sm font-semibold text-indigo-800">Tambah Item</p>
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Tipe Item</label>
                    <select v-model="itemForm.type" class="input-field text-sm">
                      <option value="stock">Produk (Stock UUID)</option>
                      <option value="package">Paket Jasa (Package UUID)</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">
                      {{ itemForm.type === 'stock' ? 'Stock UUID' : 'Package UUID' }}
                      <span class="text-rose-500">*</span>
                    </label>
                    <input v-model="itemForm.uuid" type="text" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                      class="input-field font-mono text-xs" />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Override Diskon (opsional)</label>
                    <input v-model.number="itemForm.override_discount_value" type="number" min="0"
                      placeholder="Biarkan kosong untuk pakai diskon promo" class="input-field text-sm" />
                    <p class="text-[11px] text-gray-400 mt-1">Isi ini jika item ini punya nilai diskon berbeda dari promo.</p>
                  </div>
                  <button @click="addItem" :disabled="isAddingItem"
                    class="w-full py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 rounded-xl active:scale-95 transition-all flex items-center justify-center gap-2">
                    <svg v-if="isAddingItem" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    {{ isAddingItem ? 'Menambahkan...' : '+ Tambah Item' }}
                  </button>
                </div>
  
                <!-- List Item -->
                <div>
                  <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    Item Terdaftar ({{ activePromoItems.length }})
                  </p>
                  <div v-if="activePromoItems.length === 0"
                    class="text-center py-8 text-sm text-gray-400 border border-dashed border-gray-200 rounded-xl">
                    Belum ada item di promo ini
                  </div>
                  <div v-else class="space-y-2">
                    <div v-for="item in activePromoItems" :key="item.uuid"
                      class="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-xl hover:border-gray-300 transition-colors group">
                      <div :class="item.item_type === 'stock' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'"
                        class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-xs font-bold">
                        {{ item.item_type === 'stock' ? 'PRD' : 'PKG' }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">{{ item.item_name }}</p>
                        <p class="text-xs text-gray-400">{{ formatRp(item.item_price) }}
                          <span v-if="item.override_discount_value" class="ml-1 text-indigo-500">
                            · override: {{ item.override_discount_value }}
                          </span>
                        </p>
                      </div>
                      <button @click="removeItem(item.uuid)"
                        class="p-1.5 text-gray-300 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </teleport>
  
  
      <!-- ══════════════════════════════════════════════════════════
           MODAL: NOTIFY CONFIRM
      ═══════════════════════════════════════════════════════════ -->
      <teleport to="body">
        <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
          <div v-if="isNotifModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm" @click="isNotifModalOpen = false"></div>
            <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center border border-gray-100">
              <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-sky-100 mb-4">
                <svg class="h-6 w-6 text-sky-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900 mb-1">Kirim Notifikasi?</h3>
              <p class="text-sm text-gray-500 mb-2">
                Notifikasi promo <span class="font-semibold text-gray-800">{{ promoToNotif?.name }}</span> akan
                dikirim ke semua user yang berlangganan.
              </p>
              <p class="text-xs text-gray-400 mb-6">Proses dikirim via queue (Celery). Tidak bisa dibatalkan.</p>
              <div class="flex gap-3">
                <button @click="isNotifModalOpen = false"
                  class="flex-1 py-2.5 bg-white border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 active:scale-95 transition-all">
                  Batal
                </button>
                <button @click="confirmSendNotif" :disabled="isSubmitting"
                  class="flex-1 py-2.5 bg-sky-600 text-white rounded-xl text-sm font-medium hover:bg-sky-700 active:scale-95 disabled:opacity-70 transition-all flex justify-center items-center gap-2">
                  <svg v-if="isSubmitting" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                  <span>{{ isSubmitting ? 'Mengirim...' : 'Kirim Notif' }}</span>
                </button>
              </div>
            </div>
          </div>
        </transition>
      </teleport>
  
  
      <!-- ══════════════════════════════════════════════════════════
           MODAL: DELETE CONFIRM
      ═══════════════════════════════════════════════════════════ -->
      <teleport to="body">
        <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
          <div v-if="isDeleteModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm" @click="isDeleteModalOpen = false"></div>
            <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center border border-gray-100">
              <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-rose-100 mb-4">
                <svg class="h-6 w-6 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900 mb-1">Arsipkan Promo?</h3>
              <p class="text-sm text-gray-500 mb-2">
                Promo <span class="font-semibold text-gray-800">{{ promoToDelete?.name }}</span> akan diarsipkan dan
                tidak lagi tampil.
              </p>
              <p class="text-xs text-gray-400 mb-6">Data transaksi terkait tetap tersimpan.</p>
              <div class="flex gap-3">
                <button @click="isDeleteModalOpen = false"
                  class="flex-1 py-2.5 bg-white border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 active:scale-95 transition-all">
                  Batal
                </button>
                <button @click="deletePromo" :disabled="isSubmitting"
                  class="flex-1 py-2.5 bg-rose-600 text-white rounded-xl text-sm font-medium hover:bg-rose-700 active:scale-95 disabled:opacity-70 transition-all flex justify-center items-center">
                  <span v-if="!isSubmitting">Arsipkan</span>
                  <svg v-else class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </transition>
      </teleport>
  
  
      <!-- ══════════════════════════════════════════════════════════
           TOAST
      ═══════════════════════════════════════════════════════════ -->
      <teleport to="body">
        <transition enter-active-class="transition duration-300 ease-out"
          enter-from-class="opacity-0 translate-y-2 scale-95"
          enter-to-class="opacity-100 translate-y-0 scale-100"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="opacity-100 translate-y-0 scale-100"
          leave-to-class="opacity-0 translate-y-2 scale-95">
          <div v-if="toast" class="fixed bottom-6 right-6 z-[100] flex items-center gap-3 px-4 py-3 rounded-2xl shadow-lg border max-w-sm"
            :class="toast.type === 'error'
              ? 'bg-rose-600 border-rose-500 text-white'
              : 'bg-gray-900 border-gray-700 text-white'">
            <svg v-if="toast.type === 'error'" class="w-5 h-5 shrink-0 text-rose-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else class="w-5 h-5 shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            <p class="text-sm font-medium">{{ toast.message }}</p>
          </div>
        </transition>
      </teleport>
  
    </div>
  </template>
  
  
  <style scoped>
  @reference "tailwindcss";
  
  .input-field {
    @apply block w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all;
  }
  
  .custom-scrollbar::-webkit-scrollbar { width: 5px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 10px; }
  .custom-scrollbar:hover::-webkit-scrollbar-thumb { background-color: #d1d5db; }
  </style>
  
  
  <script setup>
  import { ref, reactive, computed, onMounted } from 'vue'
  import api from '@/service/api'
  
  const ADMIN_BASE = '/admin/promos'
  
  // ══════════════════════════════════
  // STATE
  // ══════════════════════════════════
  
  const promos       = ref([])
  const stats        = ref(null)
  const isLoading    = ref(true)
  const isSubmitting = ref(false)
  const isAddingItem = ref(false)
  
  const searchQuery  = ref('')
  const filterStatus = ref('')
  const filterType   = ref('')
  const currentPage  = ref(1)
  const pageSize     = 10
  
  // Banner Upload State
  const bannerInput       = ref(null)
  const isUploadingBanner = ref(false)
  
  // Modal / Drawer states
  const isPromoModalOpen   = ref(false)
  const isItemsDrawerOpen  = ref(false)
  const isDetailDrawerOpen = ref(false)
  const isDetailLoading    = ref(false)
  const isDeleteModalOpen  = ref(false)
  const isNotifModalOpen   = ref(false)
  
  const editingPromoId    = ref(null)
  const activePromo       = ref(null)
  const activePromoItems  = ref([])
  const activeDetailPromo = ref(null)
  const promoToDelete     = ref(null)
  const promoToNotif      = ref(null)
  
  // ══════════════════════════════════
  // FORMS
  // ══════════════════════════════════
  
  const defaultPromoForm = () => ({
    name: '', slug: '', description: '', banner_url: '',
    promo_type: 'percentage', target: 'all',
    discount_value: 0, max_discount: null,
    buy_quantity: null, get_quantity: null,
    min_purchase: 0, min_qty: 1,
    quota: null, max_use_per_user: null,
    valid_from: '', valid_until: '',
    is_flash_sale: false, flash_sale_quota: null,
    priority: 0,
  })
  
  const promoForm = reactive(defaultPromoForm())
  
  const itemForm = reactive({
    type: 'stock',
    uuid: '',
    override_discount_value: null,
  })
  
  // ══════════════════════════════════
  // COMPUTED
  // ══════════════════════════════════
  
  const filteredPromos = computed(() => {
  let list = promos.value
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(q) || p.slug.toLowerCase().includes(q))
  }
  
  if (filterStatus.value) {
    list = list.filter(p => p.status === filterStatus.value)
  }
  
  if (filterType.value) {
    if (filterType.value === 'flash_sale') {
      // ✅ FIX: Tampilkan promo yang tipe aslinya 'flash_sale' ATAU toggle is_flash_sale nya menyala
      list = list.filter(p => p.promo_type === 'flash_sale' || p.is_flash_sale)
    } else {
      list = list.filter(p => p.promo_type === filterType.value)
    }
  }
  
  return list
})
  const totalPages = computed(() => Math.max(1, Math.ceil(filteredPromos.value.length / pageSize)))
  
  const paginatedPromos = computed(() => {
    const start = (currentPage.value - 1) * pageSize
    return filteredPromos.value.slice(start, start + pageSize)
  })
  
  const paginationFrom = computed(() =>
    Math.min((currentPage.value - 1) * pageSize + 1, filteredPromos.value.length)
  )
  const paginationTo = computed(() =>
    Math.min(currentPage.value * pageSize, filteredPromos.value.length)
  )
  
  // ══════════════════════════════════
  // FETCH
  // ══════════════════════════════════
  
  const fetchPromos = async () => {
    isLoading.value = true
    try {
      const res = await api.get(ADMIN_BASE, { params: { page: 1, size: 200 } })
      promos.value = res.data.items || []
    } catch (e) {
      console.error('fetchPromos error:', e)
      showToast('Gagal memuat data promo.', 'error')
    } finally {
      isLoading.value = false
    }
  }
  
  const fetchStats = async () => {
    try {
      const res = await api.get(`${ADMIN_BASE}/status`)
      stats.value = res.data
    } catch (e) {
      console.error('fetchStats error:', e)
    }
  }
  
  // ══════════════════════════════════
  // DETAIL DRAWER
  // ══════════════════════════════════
  
  const openDetailDrawer = async (promo) => {
    activeDetailPromo.value = promo   // tampil segera dari list data
    isDetailDrawerOpen.value = true
    isDetailLoading.value = true
    try {
      const res = await api.get(`${ADMIN_BASE}/${promo.uuid}`)
      activeDetailPromo.value = res.data
    } catch (e) {
      // Tetap pakai data dari list jika gagal
      console.error('fetchDetail error:', e)
    } finally {
      isDetailLoading.value = false
    }
  }
  
  const closeDetailDrawer = () => {
    isDetailDrawerOpen.value = false
    activeDetailPromo.value = null
  }
  
  // ══════════════════════════════════
  // PROMO CRUD & BANNER
  // ══════════════════════════════════
  
  const openPromoModal = (promo = null) => {
    if (promo) {
      editingPromoId.value = promo.uuid
      Object.assign(promoForm, {
        name: promo.name,
        slug: promo.slug,
        description: promo.description || '',
        banner_url: promo.banner_url || '',
        promo_type: promo.promo_type,
        target: promo.target,
        discount_value: promo.discount_value,
        max_discount: promo.max_discount,
        buy_quantity: promo.buy_quantity,
        get_quantity: promo.get_quantity,
        min_purchase: promo.min_purchase,
        min_qty: promo.min_qty,
        quota: promo.quota,
        max_use_per_user: promo.max_use_per_user,
        valid_from: toInputDatetime(promo.valid_from),
        valid_until: toInputDatetime(promo.valid_until),
        is_flash_sale: promo.is_flash_sale,
        flash_sale_quota: promo.flash_sale_quota,
        priority: promo.priority,
      })
    } else {
      editingPromoId.value = null
      Object.assign(promoForm, defaultPromoForm())
    }
    isPromoModalOpen.value = true
  }
  
  const closePromoModal = () => {
    if (isSubmitting.value || isUploadingBanner.value) return
    isPromoModalOpen.value = false
  }
  
  const autoSlug = () => {
    if (!editingPromoId.value) {
      promoForm.slug = promoForm.name
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-')
    }
  }
  
  // Handler Upload Banner
  const handleBannerUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
  
    // Validasi ukuran maks 2MB
    if (file.size > 2 * 1024 * 1024) {
      showToast('Ukuran gambar maksimal 2MB', 'error')
      if (bannerInput.value) bannerInput.value.value = ''
      return
    }
  
    const formData = new FormData()
    formData.append('file', file)
  
    isUploadingBanner.value = true
    try {
      const res = await api.post('/admin/promos/upload-banner', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      promoForm.banner_url = res.data.banner_url
      showToast('Banner berhasil diunggah.')
    } catch (e) {
      showToast(e.response?.data?.detail || 'Gagal mengunggah banner.', 'error')
    } finally {
      isUploadingBanner.value = false
      if (bannerInput.value) bannerInput.value.value = ''
    }
  }
  
  // Remove Banner (Local Only, opsional jika ingin hit api delete bisa tambahkan logic di sini)
  const removeBanner = () => {
    promoForm.banner_url = ''
  }
  
  const savePromo = async () => {
    if (!promoForm.name || !promoForm.valid_from || !promoForm.valid_until) {
      showToast('Nama, mulai, dan berakhir wajib diisi.', 'error')
      return
    }
    isSubmitting.value = true
    try {
      const payload = {
        ...promoForm,
        valid_from: new Date(promoForm.valid_from).toISOString(),
        valid_until: new Date(promoForm.valid_until).toISOString(),
        items: [],
      }
      Object.keys(payload).forEach(k => payload[k] === null && delete payload[k])
  
      if (editingPromoId.value) {
        await api.patch(`${ADMIN_BASE}/${editingPromoId.value}`, payload)
        showToast('Promo berhasil diperbarui.')
      } else {
        await api.post(ADMIN_BASE, payload)
        showToast('Promo berhasil dibuat.')
      }
      await fetchPromos()
      await fetchStats()
      closePromoModal()
    } catch (e) {
      const msg = e.response?.data?.detail || 'Gagal menyimpan promo.'
      showToast(Array.isArray(msg) ? msg.map(m => m.msg).join(', ') : msg, 'error')
    } finally {
      isSubmitting.value = false
    }
  }
  
  const publishPromo = async (promo) => {
    try {
      await api.post(`${ADMIN_BASE}/${promo.uuid}/publish`)
      showToast(`Promo "${promo.name}" dipublish.`)
      await fetchPromos()
      await fetchStats()
    } catch (e) {
      showToast(e.response?.data?.detail || 'Gagal publish promo.', 'error')
    }
  }
  
  const pausePromo = async (promo) => {
    try {
      await api.post(`${ADMIN_BASE}/${promo.uuid}/pause`)
      showToast(`Promo "${promo.name}" di-pause.`)
      await fetchPromos()
      await fetchStats()
    } catch (e) {
      showToast(e.response?.data?.detail || 'Gagal pause promo.', 'error')
    }
  }
  
  const confirmDelete = (promo) => {
    promoToDelete.value = promo
    isDeleteModalOpen.value = true
  }
  
  const deletePromo = async () => {
    if (!promoToDelete.value) return
    isSubmitting.value = true
    try {
      await api.delete(`${ADMIN_BASE}/${promoToDelete.value.uuid}`)
      showToast(`Promo "${promoToDelete.value.name}" diarsipkan.`)
      promos.value = promos.value.filter(p => p.uuid !== promoToDelete.value.uuid)
      await fetchStats()
      isDeleteModalOpen.value = false
    } catch (e) {
      showToast(e.response?.data?.detail || 'Gagal menghapus promo.', 'error')
    } finally {
      isSubmitting.value = false
      promoToDelete.value = null
    }
  }
  
  // ══════════════════════════════════
  // NOTIFY
  // ══════════════════════════════════
  
  const sendNotif = (promo) => {
    promoToNotif.value = promo
    isNotifModalOpen.value = true
  }
  
  const confirmSendNotif = async () => {
    if (!promoToNotif.value) return
    isSubmitting.value = true
    try {
      await api.post(`/admin/promos/${promoToNotif.value.uuid}/notify`)
      showToast(`Notifikasi untuk "${promoToNotif.value.name}" sedang dikirim via queue.`)
      isNotifModalOpen.value = false
    } catch (e) {
      showToast(e.response?.data?.detail || 'Gagal mengirim notifikasi.', 'error')
    } finally {
      isSubmitting.value = false
      promoToNotif.value = null
    }
  }
  
  // ══════════════════════════════════
  // ITEMS DRAWER
  // ══════════════════════════════════
  
  const openItemsDrawer = async (promo) => {
    activePromo.value = promo
    isItemsDrawerOpen.value = true
    try {
      const res = await api.get(`${ADMIN_BASE}/${promo.uuid}`)
      activePromoItems.value = res.data.items || []
    } catch (e) {
      activePromoItems.value = promo.items || []
    }
    Object.assign(itemForm, { type: 'stock', uuid: '', override_discount_value: null })
  }
  
  const closeItemsDrawer = () => {
    isItemsDrawerOpen.value = false
    activePromo.value = null
    activePromoItems.value = []
  }
  
  const addItem = async () => {
    if (!itemForm.uuid.trim()) {
      showToast('UUID item wajib diisi.', 'error')
      return
    }
    isAddingItem.value = true
    try {
      const payload = {
        override_discount_value: itemForm.override_discount_value || undefined,
      }
      if (itemForm.type === 'stock')   payload.stock_uuid   = itemForm.uuid.trim()
      if (itemForm.type === 'package') payload.package_uuid = itemForm.uuid.trim()
  
      await api.post(`${ADMIN_BASE}/${activePromo.value.uuid}/items`, payload)
      showToast('Item berhasil ditambahkan.')
  
      const res = await api.get(`${ADMIN_BASE}/${activePromo.value.uuid}`)
      activePromoItems.value = res.data.items || []
      await fetchPromos()
  
      itemForm.uuid = ''
      itemForm.override_discount_value = null
    } catch (e) {
      showToast(e.response?.data?.detail || 'Gagal menambahkan item.', 'error')
    } finally {
      isAddingItem.value = false
    }
  }
  
  const removeItem = async (itemUuid) => {
    try {
      await api.delete(`${ADMIN_BASE}/${activePromo.value.uuid}/items/${itemUuid}`)
      activePromoItems.value = activePromoItems.value.filter(i => i.uuid !== itemUuid)
      await fetchPromos()
      showToast('Item dihapus dari promo.')
    } catch (e) {
      showToast(e.response?.data?.detail || 'Gagal menghapus item.', 'error')
    }
  }
  
  // ══════════════════════════════════
  // HELPERS
  // ══════════════════════════════════
  
  const formatRp = (val) => {
    if (!val && val !== 0) return '-'
    return new Intl.NumberFormat('id-ID', {
      style: 'currency', currency: 'IDR', maximumFractionDigits: 0,
    }).format(val)
  }
  
  const formatDate = (dt) => {
    if (!dt) return '-'
    return new Date(dt).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
  }
  
  const toInputDatetime = (dt) => {
    if (!dt) return ''
    const d = new Date(dt)
    const pad = n => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
  }
  
  const quotaPercent = (promo) => {
    if (!promo.quota) return 0
    return Math.min(100, Math.round((promo.used_count / promo.quota) * 100))
  }
  
  const promoTypeLabel = (type) => {
    const map = {
      percentage: 'Persentase', fixed: 'Fixed', bogo: 'BOGO',
      bundle_disc: 'Bundle', flash_sale: 'Flash Sale',
    }
    return map[type] || type
  }
  
  const promoTypeColor = (type) => {
    const map = {
      percentage: 'bg-blue-100 text-blue-700',
      fixed: 'bg-emerald-100 text-emerald-700',
      bogo: 'bg-purple-100 text-purple-700',
      bundle_disc: 'bg-teal-100 text-teal-700',
      flash_sale: 'bg-amber-100 text-amber-700',
    }
    return map[type] || 'bg-gray-100 text-gray-600'
  }
  
  const promoTypeIcon = (type) => {
    const map = {
      percentage:  { label: '%',   bg: 'bg-blue-100',   text: 'text-blue-700'   },
      fixed:       { label: 'Rp',  bg: 'bg-emerald-100', text: 'text-emerald-700' },
      bogo:        { label: '2+1', bg: 'bg-purple-100',  text: 'text-purple-700'  },
      bundle_disc: { label: 'BDL', bg: 'bg-teal-100',    text: 'text-teal-700'    },
      flash_sale:  { label: '⚡',  bg: 'bg-amber-100',   text: 'text-amber-700'   },
    }
    return map[type] || { label: '?', bg: 'bg-gray-100', text: 'text-gray-500' }
  }
  
  const statusBadge = (status) => {
    const map = {
      draft:    'bg-gray-100 text-gray-600',
      active:   'bg-emerald-100 text-emerald-700',
      paused:   'bg-amber-100 text-amber-700',
      archived: 'bg-rose-100 text-rose-600',
    }
    return map[status] || 'bg-gray-100 text-gray-500'
  }
  
  const statusLabel = (status) => {
    const map = { draft: 'Draft', active: 'Aktif', paused: 'Dijeda', archived: 'Diarsipkan' }
    return map[status] || status
  }
  
  // ══════════════════════════════════
  // TOAST
  // ══════════════════════════════════
  
  const toast = ref(null)
  const showToast = (message, type = 'success') => {
    toast.value = { message, type }
    setTimeout(() => { toast.value = null }, 3500)
  }
  
  // ══════════════════════════════════
  // INIT
  // ══════════════════════════════════
  
  onMounted(async () => {
    await Promise.all([fetchPromos(), fetchStats()])
  })
  </script>