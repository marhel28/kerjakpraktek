<template>
  <div class="min-h-screen bg-[#F7F8FC] font-sans pb-20">
    <!-- ── Header ─────────────────────────────── -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
      <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Manajemen Addons</h1>
            <p class="text-xs text-gray-400 mt-0.5">Atur produk tambahan & bundle layanan</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button @click="openLivePreview()" class="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-all">
            <svg class="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Live Preview
          </button>
          <button @click="openGroupModal()" class="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 active:scale-95 transition-all shadow-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Tambah Group
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-screen-2xl mx-auto px-6 py-6 space-y-6">
      <!-- ── Addon Groups List ────────────────── -->
      <div v-if="loading" class="flex items-center justify-center py-24">
        <div class="flex flex-col items-center gap-3">
          <div class="w-10 h-10 border-[3px] border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
          <p class="text-sm text-gray-400 font-medium">Memuat data addons...</p>
        </div>
      </div>

      <div v-else-if="groups.length === 0" class="flex flex-col items-center justify-center py-24 gap-4 bg-white rounded-2xl border border-dashed border-gray-300">
        <div class="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center text-gray-300">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
          </svg>
        </div>
        <div class="text-center">
          <p class="text-sm font-bold text-gray-600">Belum ada Addon Group</p>
          <p class="text-xs text-gray-400 mt-1">Gunakan addon untuk menawarkan produk tambahan saat checkout</p>
        </div>
        <button @click="openGroupModal()" class="px-4 py-2 text-sm font-bold text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors">
          Buat Group Pertama
        </button>
      </div>

      <div v-else class="grid grid-cols-1 gap-6">
        <div v-for="group in groups" :key="group.uuid" class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden group/card hover:border-indigo-200 transition-all">
          <!-- Group Header -->
          <div class="px-6 py-4 bg-gray-50/50 border-b border-gray-100 flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-xl bg-white border border-gray-200 flex items-center justify-center shadow-sm">
                <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <div>
                <h3 class="text-sm font-bold text-gray-900 leading-none">{{ group.name }}</h3>
                <p class="text-xs text-gray-400 mt-1">
                  Order: {{ group.sort_order }} • {{ group.is_required ? 'Wajib Pilih' : 'Opsional' }}
                  <span v-if="group.is_global" class="ml-1 text-indigo-500 font-bold">• GLOBAL</span>
                </p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div v-if="group.group_type" :class="['px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border shadow-sm', 
                group.group_type === 'required' ? 'bg-rose-50 text-rose-600 border-rose-100' : 
                group.group_type === 'recommended' ? 'bg-amber-50 text-amber-600 border-amber-100' : 
                'bg-blue-50 text-blue-600 border-blue-100']">
                {{ group.group_type === 'required' ? 'Wajib' : group.group_type === 'recommended' ? 'Rekomendasi' : 'Tambahan' }}
              </div>
              <button @click="openItemModal(group)" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Tambah Item
              </button>
              <div class="w-px h-4 bg-gray-200 mx-1"></div>
              <button @click="openGroupModal(group)" class="p-1.5 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-all">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button @click="confirmDeleteGroup(group)" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Group Items Table -->
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-white border-b border-gray-50 text-[10px] font-black text-gray-400 uppercase tracking-[0.1em]">
                  <th class="px-6 py-3 text-left">Produk Addon</th>
                  <th class="px-6 py-3 text-right">Harga</th>
                  <th class="px-6 py-3 text-center">Stok</th>
                  <th class="px-6 py-3 text-center">Berat</th>
                  <th class="px-6 py-3 text-center">Qty</th>
                  <th class="px-6 py-3 text-center">Status</th>
                  <th class="px-6 py-3 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="item in groupItems[group.uuid]" :key="item.uuid" class="hover:bg-gray-50/50 transition-colors">
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-lg bg-gray-100 overflow-hidden border border-gray-100 flex-shrink-0 flex items-center justify-center cursor-pointer" @click="showImagePreview(item.image_url)">
                        <img v-if="item.image_url" :src="item.image_url" class="w-full h-full object-cover" />
                        <svg v-else class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div class="min-w-0">
                        <p class="font-bold text-gray-800 text-sm truncate max-w-[240px]">{{ item.name }}</p>
                        <p class="text-[10px] text-gray-400 mt-0.5 truncate max-w-[240px] italic">{{ item.description || 'Tanpa deskripsi' }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 text-right font-black text-gray-900">
                    {{ formatPrice(item.price) }}
                  </td>
                  <td class="px-6 py-4 text-center">
                    <span :class="['font-bold', item.stock > 10 ? 'text-gray-600' : 'text-rose-500']">{{ item.stock }}</span>
                  </td>
                  <td class="px-6 py-4 text-center text-xs text-gray-500">
                    {{ item.weight }}g
                  </td>
                  <td class="px-6 py-4 text-center">
                    <span v-if="item.allow_quantity" class="inline-flex items-center px-2 py-0.5 rounded bg-blue-50 text-blue-600 text-[10px] font-bold">
                      Max {{ item.max_quantity }}
                    </span>
                    <span v-else class="text-gray-300 text-[10px]">—</span>
                  </td>
                  <td class="px-6 py-4 text-center">
                    <div class="flex justify-center">
                      <div :class="['w-2 h-2 rounded-full', item.is_active ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-gray-300']"></div>
                    </div>
                  </td>
                  <td class="px-6 py-4 text-right">
                    <div class="flex items-center justify-end gap-1">
                      <button @click="openItemModal(group, item)" class="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button @click="confirmDeleteItem(item)" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!groupItems[group.uuid] || groupItems[group.uuid].length === 0">
                  <td colspan="7" class="px-6 py-8 text-center text-gray-400 text-xs">Belum ada item dalam group ini.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Group Modal ─────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="groupModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="groupModal.show = false">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 class="text-base font-bold text-gray-900">{{ groupModal.isEdit ? 'Edit Addon Group' : 'Tambah Addon Group' }}</h3>
              <button @click="groupModal.show = false" class="text-gray-400 hover:text-gray-600 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Nama Group</label>
                <input v-model="groupModal.form.name" type="text" placeholder="Contoh: Kebutuhan Kabel" class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all" />
              </div>
              
              <!-- Category & SubCategory Selection -->
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Kategori / SubKategori Terkait <span class="text-rose-500">*</span></label>
                <div class="bg-gray-50 rounded-xl border border-gray-200 p-3 max-h-48 overflow-y-auto custom-scrollbar space-y-1">
                  <div v-for="item in flattenedCategories" :key="item.id" class="flex items-center gap-2 px-2 py-1.5 hover:bg-white rounded-lg transition-colors cursor-pointer group" @click="toggleGroupCategory(item.id)">
                    <div :class="['w-4 h-4 rounded border flex items-center justify-center transition-all', groupModal.form.category_uuids.includes(item.id) ? 'bg-indigo-600 border-indigo-600' : 'bg-white border-gray-300']">
                      <svg v-if="groupModal.form.category_uuids.includes(item.id)" class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div :class="['flex items-center gap-2', item.isSub ? 'ml-4 opacity-70' : '']">
                      <span v-if="item.isSub" class="text-[10px] text-gray-400">└</span>
                      <span :class="['text-xs font-semibold', item.isSub ? 'text-gray-500' : 'text-gray-900']">{{ item.name }}</span>
                    </div>
                  </div>
                </div>
                <p v-if="groupModal.form.category_uuids.length === 0" class="text-[10px] text-rose-500 mt-1 font-medium italic">Wajib pilih minimal satu kategori/subkategori</p>
                <p v-else class="text-[10px] text-gray-400 mt-1 italic">{{ groupModal.form.category_uuids.length }} item dipilih</p>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Tipe Seleksi</label>
                  <select v-model="groupModal.form.selection_type" class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none bg-white transition-all">
                    <option value="single">Single (Radio)</option>
                    <option value="multi">Multi (Checkbox)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Urutan Tampil</label>
                  <input v-model.number="groupModal.form.sort_order" type="number" class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Kategori Group</label>
                  <select v-model="groupModal.form.group_type" class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none bg-white transition-all">
                    <option value="required">Wajib (Required)</option>
                    <option value="optional">Tambahan (Optional)</option>
                    <option value="recommended">Rekomendasi (Recommended)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Global Fallback</label>
                  <div class="flex items-center h-10 px-4 bg-gray-50 rounded-xl border border-gray-200">
                    <label class="flex items-center gap-2 cursor-pointer w-full">
                      <input v-model="groupModal.form.is_global" type="checkbox" class="w-4 h-4 rounded border-gray-300 text-indigo-600" />
                      <span class="text-xs font-bold text-gray-600">Jadikan Global</span>
                    </label>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-6 pt-2">
                <label class="flex items-center gap-2 cursor-pointer group">
                  <input v-model="groupModal.form.is_required" type="checkbox" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <span class="text-xs font-bold text-gray-600 group-hover:text-indigo-600 transition-colors">Wajib Pilih</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer group">
                  <input v-model="groupModal.form.is_active" type="checkbox" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <span class="text-xs font-bold text-gray-600 group-hover:text-indigo-600 transition-colors">Status Aktif</span>
                </label>
              </div>
            </div>
            <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex gap-3">
              <button @click="groupModal.show = false" class="flex-1 px-4 py-2.5 text-sm font-bold text-gray-500 hover:bg-gray-200 rounded-xl transition-all">Batal</button>
              <button @click="saveGroup" :disabled="groupModal.loading" class="flex-2 px-6 py-2.5 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all shadow-md active:scale-95 disabled:opacity-50">
                {{ groupModal.loading ? 'Menyimpan...' : 'Simpan Group' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Item Modal ──────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="itemModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="itemModal.show = false">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h3 class="text-base font-bold text-gray-900">{{ itemModal.isEdit ? 'Edit Addon Item' : 'Tambah Addon Item' }}</h3>
                <p class="text-[10px] text-gray-400 uppercase tracking-widest mt-0.5">Group: {{ itemModal.group?.name }}</p>
              </div>
              <button @click="itemModal.show = false" class="text-gray-400 hover:text-gray-600 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="p-6 grid grid-cols-2 gap-6 max-h-[70vh] overflow-y-auto custom-scrollbar">
              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Nama Item</label>
                  <input v-model="itemModal.form.name" type="text" placeholder="Contoh: Kabel Cat6 1M" class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all" />
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Deskripsi Singkat</label>
                  <textarea v-model="itemModal.form.description" rows="3" placeholder="Penjelasan singkat addon..." class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all resize-none"></textarea>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Harga</label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-bold text-gray-400">Rp</span>
                      <input v-model.number="itemModal.form.price" type="number" class="w-full pl-9 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all" />
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Stok</label>
                    <input v-model.number="itemModal.form.stock" type="number" class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all" />
                  </div>
                </div>
              </div>
              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Image URL</label>
                  <input v-model="itemModal.form.image_url" type="text" placeholder="https://..." class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all" />
                  <div class="mt-2 w-full aspect-video bg-gray-50 rounded-xl border border-dashed border-gray-200 flex items-center justify-center overflow-hidden">
                    <img v-if="itemModal.form.image_url" :src="itemModal.form.image_url" class="w-full h-full object-contain" />
                    <span v-else class="text-[10px] text-gray-300">Preview Image</span>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Berat (Gram)</label>
                    <input v-model.number="itemModal.form.weight" type="number" class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all" />
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5">Max Qty</label>
                    <input v-model.number="itemModal.form.max_quantity" type="number" class="w-full px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all" />
                  </div>
                </div>
                <div class="flex items-center gap-6 pt-2">
                  <label class="flex items-center gap-2 cursor-pointer group">
                    <input v-model="itemModal.form.allow_quantity" type="checkbox" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                    <span class="text-xs font-bold text-gray-600 group-hover:text-indigo-600 transition-colors">Bisa Multiple</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer group">
                    <input v-model="itemModal.form.is_active" type="checkbox" class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                    <span class="text-xs font-bold text-gray-600 group-hover:text-indigo-600 transition-colors">Aktif</span>
                  </label>
                </div>
              </div>
            </div>
            <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex gap-3">
              <button @click="itemModal.show = false" class="flex-1 px-4 py-2.5 text-sm font-bold text-gray-500 hover:bg-gray-200 rounded-xl transition-all">Batal</button>
              <button @click="saveItem" :disabled="itemModal.loading" class="flex-2 px-6 py-2.5 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all shadow-md active:scale-95 disabled:opacity-50">
                {{ itemModal.loading ? 'Menyimpan...' : 'Simpan Item' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Toast ──────────────────────────── -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show" :class="['fixed bottom-6 right-6 z-[100] flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl text-sm font-bold max-w-sm border', toast.type === 'success' ? 'bg-gray-900 text-white border-gray-800' : 'bg-rose-600 text-white border-rose-500']">
          <div :class="['w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-[10px] font-black', toast.type === 'success' ? 'bg-emerald-500' : 'bg-rose-400']">
            {{ toast.type === 'success' ? '✓' : '✕' }}
          </div>
          {{ toast.message }}
        </div>
      </Transition>
    </Teleport>

    <!-- ── Full Image Preview Modal ────────── -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="imagePreview" class="fixed inset-0 z-[100] bg-black/90 flex items-center justify-center p-10" @click="imagePreview = null">
          <img :src="imagePreview" class="max-w-full max-h-full object-contain shadow-2xl rounded-lg" />
          <button class="absolute top-6 right-6 text-white/50 hover:text-white transition-colors">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Live Preview Section ────────────── -->
    <ImageSectionPreview
      v-model="showLivePreview"
      :section="previewSection"
      :initial-url="previewStore.resolveUrl('/product/sample-cctv-kit')"
      hideModePicker
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { get, post, patch, del } from '@/service/api'
import ImageSectionPreview from '@/components/ImageSectionPreview.vue'
import { usePreviewStore } from '@/stores/previewStore'

const previewStore = usePreviewStore()

// ── State ────────────────────────────────────────────────
const groups = ref([])
const allCategories = ref([])
const groupItems = reactive({})
const loading = ref(false)
const imagePreview = ref(null)
const showLivePreview = ref(false)
const previewSection = ref(null)

const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

const showToast = (message, type = 'success') => {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

// ── Modals State ────────────────────────────────────────
const groupModal = reactive({
  show: false,
  isEdit: false,
  loading: false,
  uuid: null,
  form: {
    name: '',
    selection_type: 'multi',
    is_required: false,
    is_active: true,
    group_type: 'optional',
    is_global: false,
    sort_order: 1,
    category_uuids: []
  }
})

const itemModal = reactive({
  show: false,
  isEdit: false,
  loading: false,
  group: null,
  uuid: null,
  form: {
    name: '',
    description: '',
    price: 0,
    weight: 0,
    stock: 0,
    image_url: '',
    is_active: true,
    allow_quantity: true,
    max_quantity: 10
  }
})

// ── Fetching ─────────────────────────────────────────────
const fetchData = async () => {
  loading.value = true
  try {
    // Parallel fetch
    const [groupRes, catRes] = await Promise.all([
      get('/admin/addons/groups'),
      get('/category/')
    ])

    if (groupRes.data.success) {
      groups.value = groupRes.data.data
      for (const group of groups.value) {
        await fetchItems(group.uuid)
      }
    }

    if (catRes.data) {
      allCategories.value = catRes.data
    }
  } catch (e) {
    showToast('Gagal memuat data', 'error')
  } finally {
    loading.value = false
  }
}

const flattenedCategories = computed(() => {
  const list = []
  if (!allCategories.value || !Array.isArray(allCategories.value)) return list
  
  allCategories.value.forEach(cat => {
    const catId = cat.uuid || cat.id
    if (catId) {
      list.push({ id: catId, name: cat.name, isSub: false })
    }
    
    if (cat.subcategories && Array.isArray(cat.subcategories)) {
      cat.subcategories.forEach(sub => {
        const subId = sub.uuid || sub.id
        if (subId) {
          list.push({ id: subId, name: sub.name, isSub: true })
        }
      })
    }
  })
  return list
})

const fetchItems = async (groupUuid) => {
  try {
    const res = await get(`/admin/addons/groups/${groupUuid}/items`)
    if (res.data.success) {
      groupItems[groupUuid] = res.data.data
    }
  } catch (e) {
    console.error(`Gagal memuat item group ${groupUuid}`, e)
  }
}

// ── Group Actions ────────────────────────────────────────
const openGroupModal = async (group = null) => {
  if (group) {
    groupModal.isEdit = true
    groupModal.uuid = group.uuid
    
    // Fetch mapping
    try {
      const res = await get(`/admin/addons/groups/${group.uuid}/categories`)
      const category_uuids = res.data.success ? res.data.data : []
      groupModal.form = { ...group, category_uuids }
    } catch (e) {
      groupModal.form = { ...group, category_uuids: [] }
    }
  } else {
    groupModal.isEdit = false
    groupModal.uuid = null
    groupModal.form = {
      name: '',
      selection_type: 'multi',
      is_required: false,
      is_active: true,
      group_type: 'optional',
      is_global: false,
      sort_order: groups.value.length + 1,
      category_uuids: []
    }
  }
  groupModal.show = true
}

const toggleGroupCategory = (id) => {
  if (!id) return
  const index = groupModal.form.category_uuids.indexOf(id)
  if (index > -1) {
    groupModal.form.category_uuids.splice(index, 1)
  } else {
    groupModal.form.category_uuids.push(id)
  }
}

const saveGroup = async () => {
  if (!groupModal.form.name) return showToast('Nama group wajib diisi', 'error')
  if (groupModal.form.category_uuids.length === 0) return showToast('Wajib pilih minimal satu kategori', 'error')
  
  groupModal.loading = true
  try {
    let res
    if (groupModal.isEdit) {
      res = await patch(`/admin/addons/groups/${groupModal.uuid}`, groupModal.form)
    } else {
      res = await post('/admin/addons/groups', groupModal.form)
    }
    
    if (res.data.success) {
      showToast(groupModal.isEdit ? 'Group diperbarui' : 'Group berhasil dibuat')
      groupModal.show = false
      await fetchData()
    }
  } catch (e) {
    showToast('Gagal menyimpan group', 'error')
  } finally {
    groupModal.loading = false
  }
}

const confirmDeleteGroup = async (group) => {
  if (confirm(`Hapus group "${group.name}"? Semua item didalamnya akan terhapus.`)) {
    try {
      const res = await del(`/admin/addons/groups/${group.uuid}`)
      if (res.data.success) {
        showToast('Group dihapus')
        await fetchData()
      }
    } catch (e) {
      showToast('Gagal menghapus group', 'error')
    }
  }
}

// ── Item Actions ─────────────────────────────────────────
const openItemModal = (group, item = null) => {
  itemModal.group = group
  if (item) {
    itemModal.isEdit = true
    itemModal.uuid = item.uuid
    itemModal.form = { ...item }
  } else {
    itemModal.isEdit = false
    itemModal.uuid = null
    itemModal.form = {
      group_uuid: group.uuid,
      name: '',
      description: '',
      price: 0,
      weight: 0,
      stock: 100,
      image_url: '',
      is_active: true,
      allow_quantity: true,
      max_quantity: 10
    }
  }
  itemModal.show = true
}

const saveItem = async () => {
  if (!itemModal.form.name) return showToast('Nama item wajib diisi', 'error')
  
  itemModal.loading = true
  try {
    let res
    if (itemModal.isEdit) {
      res = await patch(`/admin/addons/items/${itemModal.uuid}`, itemModal.form)
    } else {
      res = await post('/admin/addons/items', itemModal.form)
    }
    
    if (res.data.success) {
      showToast(itemModal.isEdit ? 'Item diperbarui' : 'Item berhasil ditambahkan')
      itemModal.show = false
      await fetchItems(itemModal.group.uuid)
    }
  } catch (e) {
    showToast('Gagal menyimpan item', 'error')
  } finally {
    itemModal.loading = false
  }
}

const confirmDeleteItem = async (item) => {
  if (confirm(`Hapus item "${item.name}"?`)) {
    try {
      const res = await del(`/admin/addons/items/${item.uuid}`)
      if (res.data.success) {
        showToast('Item dihapus')
        await fetchItems(item.group_uuid)
      }
    } catch (e) {
      showToast('Gagal menghapus item', 'error')
    }
  }
}

const showImagePreview = (url) => {
  if (url) imagePreview.value = url
}

const openLivePreview = () => {
  previewSection.value = {
    identifier: 'Addon Preview',
    items: groups.value.map(g => ({ ...g, type: 'addon_group' }))
  }
  showLivePreview.value = true
}

// ── Helpers ──────────────────────────────────────────────
const formatPrice = (v) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(v).replace('Rp', 'Rp ')
}

onMounted(fetchData)
</script>

<style scoped>
.flex-2 { flex: 2; }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }

/* Transitions */
.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active > div, .modal-leave-active > div { transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-enter-from > div, .modal-leave-to > div { transform: scale(0.9) translateY(20px); }

.toast-enter-active, .toast-leave-active { transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.toast-enter-from, .toast-leave-to { transform: translateX(100%) scale(0.7); opacity: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
