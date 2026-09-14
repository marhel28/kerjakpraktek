<!-- pages/admin/booking.vue -->
<template>
  <div class="min-h-screen bg-gray-50 font-sans pb-16">

    <!-- ── Header ─────────────────────────────── -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
      <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Manajemen Booking</h1>
            <p class="text-xs text-gray-400 mt-0.5">Kelola jadwal layanan dan pembayaran jasa</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div class="hidden sm:flex flex-col items-end border-r border-gray-200 pr-4 mr-1">
            <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest leading-none mb-1">Total Booking</p>
            <p class="text-lg font-black text-indigo-600 leading-none">{{ pagination.total }}</p>
          </div>
          <button
            @click="fetchBookings"
            :disabled="isLoading"
            class="w-9 h-9 flex items-center justify-center rounded-lg bg-white border border-gray-200 text-gray-400 hover:text-indigo-600 transition disabled:opacity-50 active:scale-95 shadow-sm"
          >
            <svg class="w-4 h-4" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- ── Filters ──────────────────────────── -->
    <div class="max-w-screen-2xl mx-auto px-6 py-6">
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col lg:flex-row gap-4 items-end">
        
        <div class="flex-1 w-full">
          <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Pencarian</label>
          <div class="relative">
            <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="filters.search"
              @input="debounceSearch"
              type="text"
              placeholder="No. Booking, Nama, atau No. HP..."
              class="w-full pl-10 pr-4 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition"
            />
          </div>
        </div>

        <div class="w-full lg:w-44">
          <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Status</label>
          <select
            v-model="filters.status"
            class="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition cursor-pointer"
          >
            <option value="">Semua Status</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="dp_paid">DP Paid</option>
            <option value="progress">In Progress</option>
            <option value="done">Done</option>
            <option value="lunas">Lunas</option>
            <option value="cancel">Canceled</option>
          </select>
        </div>

        <div class="flex gap-2 w-full lg:w-auto">
          <div class="flex-1 lg:w-40">
            <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Dari</label>
            <input v-model="filters.date_from" type="date" class="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition cursor-pointer"/>
          </div>
          <div class="flex-1 lg:w-40">
            <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Sampai</label>
            <input v-model="filters.date_to" type="date" class="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none transition cursor-pointer"/>
          </div>
        </div>

        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="px-4 py-2 text-sm font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition active:scale-95"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- ── Table ──────────────────────────── -->
    <div class="max-w-screen-2xl mx-auto px-6 pb-8">
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50/50">
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Booking</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Pelanggan</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Layanan</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Jadwal</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Status</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-right">Total</th>
              </tr>
            </thead>

            <!-- Skeleton -->
            <tbody v-if="isLoading && bookings.length === 0" class="divide-y divide-gray-50">
              <tr v-for="i in 6" :key="i" class="animate-pulse">
                <td class="px-6 py-4"><div class="h-3 bg-gray-100 rounded-full w-24 mb-2"/><div class="h-2 bg-gray-50 rounded-full w-16"/></td>
                <td class="px-6 py-4"><div class="h-3 bg-gray-100 rounded-full w-32 mb-2"/><div class="h-2 bg-gray-50 rounded-full w-24"/></td>
                <td class="px-6 py-4"><div class="h-3 bg-gray-100 rounded-full w-28 mb-2"/><div class="h-2 bg-gray-50 rounded-full w-20"/></td>
                <td class="px-6 py-4"><div class="h-3 bg-gray-100 rounded-full w-24 mb-2"/><div class="h-2 bg-gray-50 rounded-full w-16"/></td>
                <td class="px-6 py-4"><div class="h-6 bg-gray-100 rounded-full w-20"/></td>
                <td class="px-6 py-4 flex justify-end"><div class="h-3 bg-gray-100 rounded-full w-24"/></td>
              </tr>
            </tbody>

            <!-- Empty -->
            <tbody v-else-if="bookings.length === 0">
              <tr>
                <td colspan="6" class="px-6 py-24 text-center">
                  <div class="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center mx-auto mb-4 border border-gray-100 text-gray-300">
                    <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                    </svg>
                  </div>
                  <p class="font-bold text-gray-900 mb-1">Tidak ada booking</p>
                  <p class="text-xs text-gray-400">Tidak ada data yang sesuai dengan kriteria filter.</p>
                </td>
              </tr>
            </tbody>

            <!-- Rows -->
            <tbody v-else class="divide-y divide-gray-50">
              <tr
                v-for="booking in bookings"
                :key="booking.uuid"
                @click="openDrawer(booking)"
                class="hover:bg-indigo-50/30 cursor-pointer transition-colors group"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="font-mono text-xs font-bold text-gray-900 tracking-wider group-hover:text-indigo-600 transition">{{ booking.booking_number }}</div>
                  <div class="text-[11px] text-gray-400 mt-0.5">{{ formatDateShort(booking.created_at) }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-bold text-gray-900">{{ booking.contact_name || '-' }}</div>
                  <div class="text-[11px] text-gray-400 mt-0.5">{{ booking.contact_phone || '-' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-700 capitalize">{{ booking.category }} <span class="text-gray-400">({{ booking.camera_count }}×)</span></div>
                  <div class="text-[11px] text-gray-400 mt-0.5">{{ booking.city }} · {{ booking.distance_km }} km</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ formatDateShort(booking.scheduled_date) }}</div>
                  <div class="text-[11px] text-gray-400 mt-0.5">{{ booking.time_slot }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="statusBadge(booking.status).cls" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider border">
                    <span class="w-1.5 h-1.5 rounded-full" :class="statusBadge(booking.status).dot"/>
                    {{ booking.status?.replace('_', ' ') || 'pending' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="text-sm font-black text-gray-900">{{ fmt(booking.total_price) }}</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="bg-gray-50/50 px-6 py-4 border-t border-gray-100 flex items-center justify-between">
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest hidden sm:block">
            Showing <span class="text-gray-900">{{ pagination.total === 0 ? 0 : (pagination.page - 1) * pagination.size + 1 }}–{{ Math.min(pagination.page * pagination.size, pagination.total) }}</span>
            of {{ pagination.total }} entries
          </p>
          <div class="flex items-center gap-2 ml-auto">
            <button @click="changePage(pagination.page - 1)" :disabled="pagination.page === 1"
              class="w-10 h-10 flex items-center justify-center rounded-lg bg-white border border-gray-200 text-gray-400 hover:text-indigo-600 disabled:opacity-40 transition shadow-sm active:scale-95">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/></svg>
            </button>
            <div class="px-4 py-2 bg-white border border-gray-200 rounded-lg text-[10px] font-black text-gray-400 shadow-sm">
              <span class="text-indigo-600">{{ pagination.page }}</span> / {{ Math.ceil(pagination.total / pagination.size) || 1 }}
            </div>
            <button @click="changePage(pagination.page + 1)" :disabled="pagination.page * pagination.size >= pagination.total"
              class="w-10 h-10 flex items-center justify-center rounded-lg bg-white border border-gray-200 text-gray-400 hover:text-indigo-600 disabled:opacity-40 transition shadow-sm active:scale-95">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>


    <!-- ── Drawer ────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="drawer.isOpen"
          class="fixed inset-0 bg-gray-950/40 backdrop-blur-sm"
          style="z-index:9998"
          @click="closeDrawer"
        />
      </Transition>

      <Transition
        enter-active-class="transition-transform duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition-transform duration-250 ease-[cubic-bezier(0.32,0.72,0,1)]"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <div
          v-if="drawer.isOpen && drawer.data"
          class="fixed inset-y-0 right-0 w-full max-w-[500px] flex flex-col bg-white shadow-2xl border-l border-gray-200"
          style="z-index:9999"
        >

          <!-- Drawer Header -->
          <div class="px-6 py-5 border-b border-gray-100 flex items-start justify-between bg-white shrink-0">
            <div>
              <p class="text-[10px] font-bold tracking-[0.2em] uppercase text-gray-400 mb-1">Detail Booking</p>
              <p class="font-mono text-base font-bold text-gray-900 tracking-wider">{{ drawer.data.booking_number }}</p>
            </div>
            <button @click="closeDrawer" class="w-9 h-9 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-400 transition">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Drawer Body -->
          <div class="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">

            <!-- Status -->
            <div class="flex items-center justify-between pb-6 border-b border-gray-50">
              <span :class="statusBadge(drawer.data.status).cls" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider border">
                <span class="w-1.5 h-1.5 rounded-full" :class="statusBadge(drawer.data.status).dot"/>
                {{ drawer.data.status?.replace('_', ' ') || 'pending' }}
              </span>
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{{ formatDateShort(drawer.data.created_at) }}</span>
            </div>

            <!-- Pelanggan -->
            <section>
              <p class="text-[10px] font-bold tracking-widest uppercase text-gray-400 mb-4 ml-1">Informasi Pelanggan</p>
              <div class="bg-gray-50 rounded-2xl p-5 border border-gray-100 space-y-4">
                <div class="flex justify-between">
                  <span class="text-xs text-gray-400">Nama Pelanggan</span>
                  <span class="text-sm font-bold text-gray-900">{{ drawer.data.contact_name || '-' }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-xs text-gray-400">WhatsApp</span>
                  <a v-if="drawer.data.contact_phone" :href="`https://wa.me/${drawer.data.contact_phone.replace(/^0/, '62')}`" target="_blank" class="px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-bold rounded-lg border border-emerald-100 hover:bg-emerald-100 transition">
                    {{ drawer.data.contact_phone }}
                  </a>
                </div>
                <div class="pt-2 border-t border-gray-200/50">
                  <span class="text-xs text-gray-400 block mb-1.5">Alamat Pemasangan</span>
                  <p class="text-sm font-medium text-gray-700 leading-relaxed">{{ drawer.data.address || '-' }}</p>
                  <p class="text-[11px] text-gray-400 mt-1 font-bold">{{ drawer.data.city }} · {{ drawer.data.distance_km }} km dari workshop</p>
                </div>
              </div>
            </section>

            <!-- Layanan -->
            <section>
              <p class="text-[10px] font-bold tracking-widest uppercase text-gray-400 mb-4 ml-1">Detail Layanan</p>
              <div class="grid grid-cols-2 gap-3">
                <div class="p-4 bg-white border border-gray-200 rounded-xl">
                  <p class="text-[10px] text-gray-400 uppercase font-bold mb-1">Kategori</p>
                  <p class="text-sm font-black text-gray-900 capitalize">{{ drawer.data.category }}</p>
                </div>
                <div class="p-4 bg-white border border-gray-200 rounded-xl">
                  <p class="text-[10px] text-gray-400 uppercase font-bold mb-1">Brand</p>
                  <p class="text-sm font-black text-gray-900 uppercase">{{ drawer.data.brand }}</p>
                </div>
                <div class="p-4 bg-white border border-gray-200 rounded-xl">
                  <p class="text-[10px] text-gray-400 uppercase font-bold mb-1">Jumlah</p>
                  <p class="text-sm font-black text-gray-900">{{ drawer.data.camera_count }} Titik</p>
                </div>
                <div class="p-4 bg-white border border-gray-200 rounded-xl">
                  <p class="text-[10px] text-gray-400 uppercase font-bold mb-1">Jadwal</p>
                  <p class="text-sm font-black text-gray-900">{{ formatDateShort(drawer.data.scheduled_date) }}</p>
                </div>
              </div>
            </section>

            <!-- Teknisi -->
            <section v-if="['dp_paid', 'progress', 'done', 'lunas'].includes(drawer.data.status)">
              <p class="text-[10px] font-bold tracking-widest uppercase text-gray-400 mb-4 ml-1">Penugasan Teknisi</p>
              <div v-if="drawer.data.technician && !showAssign" class="flex items-center gap-4 p-4 bg-indigo-600 rounded-2xl text-white shadow-lg shadow-indigo-200">
                <div class="w-12 h-12 rounded-xl bg-white/20 border border-white/30 overflow-hidden shrink-0">
                  <img v-if="drawer.data.technician.picture_url" :src="drawer.data.technician.picture_url" class="w-full h-full object-cover" />
                  <div v-else class="w-full h-full flex items-center justify-center"><svg class="w-6 h-6 opacity-40" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-black tracking-tight">{{ drawer.data.technician.name }}</p>
                  <p class="text-[10px] font-mono opacity-60">{{ drawer.data.technician.id_employee }}</p>
                </div>
                <button @click="showAssign = true" class="w-8 h-8 flex items-center justify-center rounded-lg bg-white/10 hover:bg-white/20 transition">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/></svg>
                </button>
              </div>

              <div v-if="!drawer.data.technician || showAssign" class="space-y-3">
                <div class="relative">
                  <select 
                    v-model="actionState.selectedTech" 
                    @change="validateTechAssignment"
                    class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm font-bold text-gray-700 outline-none focus:ring-2 focus:ring-indigo-500 transition"
                  >
                    <option value="">-- Pilih Teknisi --</option>
                    <option v-for="t in technicians" :key="t.uuid" :value="t.uuid">{{ t.name }} ({{ t.id_employee }})</option>
                  </select>
                  <div v-if="actionState.isValidatingTech" class="absolute right-10 top-1/2 -translate-y-1/2">
                    <svg class="animate-spin h-4 w-4 text-indigo-600" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                  </div>
                </div>

                <!-- Warnings -->
                <div v-if="actionState.techWarning" :class="actionState.techWarning.type === 'err' ? 'bg-red-50 border-red-100 text-red-600' : 'bg-amber-50 border-amber-100 text-amber-600'" class="p-3 rounded-xl border text-[11px] font-bold flex items-start gap-2 animate-in fade-in slide-in-from-top-2">
                  <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>{{ actionState.techWarning.msg }}</span>
                </div>

                <div class="flex gap-2">
                  <button v-if="showAssign" @click="showAssign = false" class="flex-1 py-2.5 text-xs font-bold text-gray-400 uppercase">Batal</button>
                  <button 
                    @click="assignTechnician" 
                    :disabled="!actionState.selectedTech || actionState.isAssigning || (actionState.techWarning && actionState.techWarning.type === 'err')" 
                    class="flex-[2] py-2.5 bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-indigo-700 transition disabled:opacity-50"
                  >
                    {{ actionState.isAssigning ? 'Memproses...' : 'Tugaskan Sekarang' }}
                  </button>
                </div>
              </div>
            </section>

            <!-- Ringkasan Biaya -->
            <section>
              <p class="text-[10px] font-bold tracking-widest uppercase text-gray-400 mb-4 ml-1">Ringkasan Biaya</p>
              <div class="space-y-2.5">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Service Jasa</span>
                  <span class="font-bold text-gray-700">{{ fmt(drawer.data.service_price) }}</span>
                </div>
                <div v-if="drawer.data.addon_price" class="flex justify-between text-sm">
                  <span class="text-gray-500">Layanan Tambahan</span>
                  <span class="font-bold text-gray-700">{{ fmt(drawer.data.addon_price) }}</span>
                </div>
                <div v-if="drawer.data.transport_fee" class="flex justify-between text-sm">
                  <span class="text-gray-500">Biaya Transport</span>
                  <span class="font-bold text-gray-700">{{ fmt(drawer.data.transport_fee) }}</span>
                </div>
                <div class="pt-3 border-t border-gray-100 flex justify-between items-baseline">
                  <span class="text-sm font-bold text-gray-900">Total Tagihan</span>
                  <span class="text-xl font-black text-indigo-600">{{ fmt(drawer.data.total_price) }}</span>
                </div>
              </div>
            </section>

          </div>

          <!-- Drawer Footer -->
          <div class="p-6 bg-gray-50 border-t border-gray-100 shrink-0 space-y-4">
            
            <div class="flex gap-2">
              <select v-model="actionState.selectedStatus" class="flex-1 px-3 py-2.5 bg-white border border-gray-200 rounded-xl text-sm font-bold text-gray-700 outline-none focus:ring-2 focus:ring-indigo-500 transition">
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="dp_paid">DP Paid</option>
                <option value="progress">In Progress</option>
                <option value="done">Done</option>
                <option value="lunas">Lunas</option>
                <option value="cancel">Canceled</option>
              </select>
              <button @click="updateStatus" :disabled="actionState.isUpdatingStatus || actionState.selectedStatus === drawer.data.status" class="px-6 py-2.5 bg-gray-900 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-gray-800 transition disabled:opacity-40">
                Update
              </button>
            </div>

            <div v-if="drawer.data.status !== 'lunas' && drawer.data.status !== 'cancel'" class="pt-2">
              <button v-if="drawer.data.status === 'confirmed'" @click="processPayment('dp')" :disabled="actionState.isProcessingPayment" class="w-full py-3.5 bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-indigo-700 transition shadow-lg shadow-indigo-200 active:scale-95 flex items-center justify-center gap-2">
                <svg v-if="actionState.isProcessingPayment" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Bayar DP — {{ fmt(drawer.data.dp_amount) }}
              </button>
              <button v-if="drawer.data.status === 'done' && drawer.data.remaining_amount > 0" @click="processPayment('lunas')" :disabled="actionState.isProcessingPayment" class="w-full py-3.5 bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-indigo-700 transition shadow-lg shadow-indigo-200 active:scale-95 flex items-center justify-center gap-2">
                <svg v-if="actionState.isProcessingPayment" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Bayar Lunas — {{ fmt(drawer.data.remaining_amount) }}
              </button>
            </div>

          </div><!-- end footer -->
        </div><!-- end drawer panel -->
      </Transition>
    </Teleport>

  </div>
</template>

<!-- ══════════════════════════════════════════════════════════ -->
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800;900&display=swap');

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e7e5e4; border-radius: 99px; }
.custom-scrollbar:hover::-webkit-scrollbar-thumb { background: #d6d3d1; }
</style>

<!-- ══════════════════════════════════════════════════════════ -->
<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/service/api'

const route = useRoute()

// ── State ──────────────────────────────────────────────────
const bookings  = ref([])
const technicians = ref([])
const isLoading = ref(true)
const showAssign = ref(false)

const filters = reactive({
  search: '',
  status: route.query.status || '',
  date_from: '',
  date_to: '',
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

const drawer = reactive({
  isOpen: false,
  data: null,
})

const actionState = reactive({
  isUpdatingStatus: false,
  isProcessingPayment: false,
  isAssigning: false,
  selectedTech: '',
  notes: '',
  feedback: null,   // { type: 'ok'|'err', msg: string }
  isValidatingTech: false,
  techWarning: null, // { type: 'warn'|'err', msg: string }
})

let searchTimeout = null
let feedbackTimer = null

// ── Computed ───────────────────────────────────────────────
const hasActiveFilters = computed(() =>
  filters.search || filters.status || filters.date_from || filters.date_to
)

// ── Fetch ──────────────────────────────────────────────────
const fetchBookings = async () => {
  isLoading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...(filters.status    && { status: filters.status }),
      ...(filters.date_from && { date_from: filters.date_from }),
      ...(filters.date_to   && { date_to: filters.date_to }),
      ...(filters.search    && { search: filters.search }),
    }
    const res = await api.get('/admin/service/bookings', { params })
    bookings.value   = res.data.items  || []
    pagination.total = res.data.total  || 0
  } catch (e) {
    console.error('fetchBookings:', e)
  } finally {
    isLoading.value = false
  }
}

const fetchTechnicians = async () => {
  try {
    const res = await api.get('/admin/service/technicians?active_only=true')
    technicians.value = res.data || []
  } catch (e) { console.error('fetchTechnicians:', e) }
}

// ── Filters ────────────────────────────────────────────────
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.page = 1
    fetchBookings()
  }, 500)
}

watch(() => [filters.status, filters.date_from, filters.date_to], () => {
  pagination.page = 1
  fetchBookings()
})

const clearFilters = () => {
  filters.search = filters.status = filters.date_from = filters.date_to = ''
  pagination.page = 1
  fetchBookings()
}

const changePage = (p) => {
  const max = Math.ceil(pagination.total / pagination.size)
  if (p < 1 || p > max) return
  pagination.page = p
  fetchBookings()
}

// ── Drawer ─────────────────────────────────────────────────
const openDrawer = (booking) => {
  drawer.data             = { ...booking }
  actionState.selectedStatus = booking.status
  actionState.selectedTech   = booking.technician_uuid || ''
  actionState.notes       = ''
  actionState.feedback    = null
  showAssign.value        = false
  drawer.isOpen           = true
  document.body.style.overflow = 'hidden'
}

const closeDrawer = () => {
  drawer.isOpen = false
  document.body.style.overflow = ''
  setTimeout(() => { drawer.data = null }, 300)
}

// ── Feedback helper ────────────────────────────────────────
const showFeedback = (type, msg) => {
  clearTimeout(feedbackTimer)
  actionState.feedback = { type, msg }
  feedbackTimer = setTimeout(() => { actionState.feedback = null }, 3500)
}

// ── Update Status ──────────────────────────────────────────
// PATCH /admin/service/bookings/{uuid}/status
// Body: { "status": "...", "notes": "..." }
const updateStatus = async () => {
  if (!drawer.data?.uuid || !actionState.selectedStatus) return
  actionState.isUpdatingStatus = true
  try {
    await api.patch(
      `/admin/service/bookings/${drawer.data.uuid}/status`,
      {
        status: actionState.selectedStatus,
        notes:  actionState.notes || undefined,
        technician_uuid: actionState.selectedTech || undefined,
      }
    )
    // Update local state
    drawer.data.status = actionState.selectedStatus
    actionState.notes  = ''
    showFeedback('ok', `✓ Status diperbarui ke "${actionState.selectedStatus.replace('_', ' ')}"`)
    fetchBookings()
    
    // Refresh detail to get technician info if assigned
    const refreshed = await api.get(`/services/booking/${drawer.data.uuid}`)
    if (refreshed.data) drawer.data = { ...refreshed.data }
  } catch (e) {
    const msg = e?.response?.data?.detail || 'Gagal memperbarui status.'
    showFeedback('err', `✗ ${msg}`)
    console.error('updateStatus:', e)
  } finally {
    actionState.isUpdatingStatus = false
  }
}

const assignTechnician = async () => {
  if (!drawer.data?.uuid || !actionState.selectedTech) return
  actionState.isAssigning = true
  try {
    await api.patch(
      `/admin/service/bookings/${drawer.data.uuid}/status`,
      {
        status: drawer.data.status, // Tetap gunakan status saat ini
        technician_uuid: actionState.selectedTech,
      }
    )
    showFeedback('ok', `✓ Teknisi berhasil ditugaskan`)
    showAssign.value = false
    
    // Refresh detail
    const refreshed = await api.get(`/services/booking/${drawer.data.uuid}`)
    if (refreshed.data) drawer.data = { ...refreshed.data }
    fetchBookings()
  } catch (e) {
    const msg = e?.response?.data?.detail || 'Gagal menugaskan teknisi.'
    showFeedback('err', `✗ ${msg}`)
  } finally {
    actionState.isAssigning = false
  }
}

const validateTechAssignment = async () => {
  if (!actionState.selectedTech || !drawer.data) {
    actionState.techWarning = null
    return
  }
  
  actionState.isValidatingTech = true
  actionState.techWarning = null
  
  try {
    const res = await api.get(`/admin/service/technicians/${actionState.selectedTech}/validate-assignment`, {
      params: {
        target_date: drawer.data.scheduled_date,
        target_slot: drawer.data.time_slot,
        exclude_booking: drawer.data.uuid
      }
    })
    
    if (res.data.conflict) {
      actionState.techWarning = { type: 'err', msg: res.data.message }
    } else if (res.data.tight) {
      actionState.techWarning = { type: 'warn', msg: res.data.message }
    }
  } catch (e) {
    console.error('validateTechAssignment:', e)
  } finally {
    actionState.isValidatingTech = false
  }
}

// ── Process Payment ────────────────────────────────────────
// POST /services/payment/create
// Body: { booking_uuid, payment_type }
const processPayment = async (type) => {
  if (!drawer.data?.uuid) return
  actionState.isProcessingPayment = true
  try {
    const res = await api.post('/services/payment/create', {
      booking_uuid: drawer.data.uuid,
      payment_type: type,
    })
    const data = res.data
    // Jika ada snap token / redirect_url, buka di tab baru untuk admin
    const url = data.payment_url || data.redirect_url
    if (url) window.open(url, '_blank', 'noopener')
    // Refresh booking detail
    const refreshed = await api.get(`/services/booking/${drawer.data.uuid}`)
    if (refreshed.data) {
      drawer.data = { ...refreshed.data }
      actionState.selectedStatus = drawer.data.status
    }
    showFeedback('ok', `✓ Tautan pembayaran ${type.toUpperCase()} dibuka di tab baru`)
    fetchBookings()
  } catch (e) {
    const msg = e?.response?.data?.detail || `Gagal memproses pembayaran ${type}.`
    showFeedback('err', `✗ ${msg}`)
    console.error('processPayment:', e)
  } finally {
    actionState.isProcessingPayment = false
  }
}

// ── Helpers ────────────────────────────────────────────────
const fmt = (n) =>
  new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 })
    .format(n || 0).replace('Rp', 'Rp\u00A0')

const formatDateShort = (d) =>
  d ? new Date(d).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' }) : '-'

const statusBadge = (s) => {
  const map = {
    pending:   { cls: 'bg-amber-50   text-amber-700   border-amber-200',   dot: 'bg-amber-400' },
    confirmed: { cls: 'bg-blue-50    text-blue-700    border-blue-200',    dot: 'bg-blue-400' },
    dp_paid:   { cls: 'bg-violet-50  text-violet-700  border-violet-200',  dot: 'bg-violet-400' },
    progress:  { cls: 'bg-indigo-50  text-indigo-700  border-indigo-200',  dot: 'bg-indigo-400' },
    done:      { cls: 'bg-emerald-50 text-emerald-700 border-emerald-200', dot: 'bg-emerald-400' },
    lunas:     { cls: 'bg-green-50   text-green-700   border-green-200',   dot: 'bg-green-500' },
    cancel:    { cls: 'bg-red-50     text-red-700     border-red-200',     dot: 'bg-red-400' },
  }
  return map[s?.toLowerCase()] ?? { cls: 'bg-stone-100 text-stone-600 border-stone-200', dot: 'bg-stone-400' }
}

// ── Init ───────────────────────────────────────────────────
onMounted(() => {
  if (route.query.status) {
    filters.status = route.query.status
  }
  fetchBookings()
  fetchTechnicians()
})
</script>