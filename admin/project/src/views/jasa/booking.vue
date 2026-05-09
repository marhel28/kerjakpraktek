<!-- pages/admin/booking.vue -->
<template>
  <div class="min-h-screen bg-[#F5F4F0] font-['Geist',sans-serif] pb-16">

    <!-- ══════════════════════════════════════════ -->
    <!-- PAGE HEADER                               -->
    <!-- ══════════════════════════════════════════ -->
    <div class="px-6 pt-8 pb-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
      <div>
        <p class="text-[11px] tracking-[0.25em] uppercase text-stone-400 font-medium mb-1.5">Admin Panel</p>
        <h1 class="text-3xl font-black text-stone-900 tracking-tight leading-none">Booking</h1>
      </div>
      <div class="flex items-center gap-2">
        <div class="text-right hidden sm:block">
          <p class="text-xs text-stone-400">Total Booking</p>
          <p class="text-xl font-black text-stone-800">{{ pagination.total }}</p>
        </div>
        <button
          @click="fetchBookings"
          :disabled="isLoading"
          class="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-stone-200 hover:border-stone-400 text-stone-500 hover:text-stone-800 shadow-sm transition-all active:scale-95 disabled:opacity-50"
          title="Refresh"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': isLoading }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════ -->
    <!-- FILTERS                                   -->
    <!-- ══════════════════════════════════════════ -->
    <div class="px-6 mb-5">
      <div class="bg-white rounded-2xl border border-stone-200 shadow-sm p-4 flex flex-col lg:flex-row gap-3 lg:items-end">

        <!-- Search -->
        <div class="flex-1">
          <label class="block text-[10px] font-bold text-stone-400 uppercase tracking-widest mb-1.5">Cari Booking</label>
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              v-model="filters.search"
              @input="debounceSearch"
              type="text"
              placeholder="No. Booking, Nama, atau No. HP..."
              class="w-full pl-9 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-sm text-stone-800 placeholder-stone-400 focus:outline-none focus:bg-white focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition-all"
            />
          </div>
        </div>

        <!-- Status -->
        <div class="w-full lg:w-44">
          <label class="block text-[10px] font-bold text-stone-400 uppercase tracking-widest mb-1.5">Status</label>
          <select
            v-model="filters.status"
            class="w-full px-3 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-sm text-stone-700 focus:outline-none focus:bg-white focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition-all cursor-pointer"
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

        <!-- Date Range -->
        <div class="flex gap-2">
          <div>
            <label class="block text-[10px] font-bold text-stone-400 uppercase tracking-widest mb-1.5">Dari</label>
            <input v-model="filters.date_from" type="date" class="px-3 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-sm text-stone-700 focus:outline-none focus:bg-white focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition-all cursor-pointer"/>
          </div>
          <div>
            <label class="block text-[10px] font-bold text-stone-400 uppercase tracking-widest mb-1.5">Sampai</label>
            <input v-model="filters.date_to" type="date" class="px-3 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-sm text-stone-700 focus:outline-none focus:bg-white focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition-all cursor-pointer"/>
          </div>
        </div>

        <!-- Reset -->
        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="px-4 py-2.5 text-sm font-semibold text-stone-600 bg-stone-100 hover:bg-stone-200 rounded-xl transition-colors active:scale-95"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════ -->
    <!-- TABLE                                     -->
    <!-- ══════════════════════════════════════════ -->
    <div class="px-6">
      <div class="bg-white rounded-2xl border border-stone-200 shadow-sm overflow-hidden">

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-stone-100">
                <th class="px-5 py-3.5 text-[10px] font-black text-stone-400 uppercase tracking-widest whitespace-nowrap">Booking</th>
                <th class="px-5 py-3.5 text-[10px] font-black text-stone-400 uppercase tracking-widest whitespace-nowrap">Pelanggan</th>
                <th class="px-5 py-3.5 text-[10px] font-black text-stone-400 uppercase tracking-widest whitespace-nowrap">Layanan</th>
                <th class="px-5 py-3.5 text-[10px] font-black text-stone-400 uppercase tracking-widest whitespace-nowrap">Jadwal</th>
                <th class="px-5 py-3.5 text-[10px] font-black text-stone-400 uppercase tracking-widest whitespace-nowrap">Status</th>
                <th class="px-5 py-3.5 text-[10px] font-black text-stone-400 uppercase tracking-widest text-right whitespace-nowrap">Total</th>
              </tr>
            </thead>

            <!-- Skeleton -->
            <tbody v-if="isLoading && bookings.length === 0" class="divide-y divide-stone-50">
              <tr v-for="i in 6" :key="i" class="animate-pulse">
                <td class="px-5 py-4"><div class="h-3.5 bg-stone-100 rounded-full w-28 mb-2"/><div class="h-2.5 bg-stone-50 rounded-full w-20"/></td>
                <td class="px-5 py-4"><div class="h-3.5 bg-stone-100 rounded-full w-32 mb-2"/><div class="h-2.5 bg-stone-50 rounded-full w-24"/></td>
                <td class="px-5 py-4"><div class="h-3.5 bg-stone-100 rounded-full w-28 mb-2"/><div class="h-2.5 bg-stone-50 rounded-full w-20"/></td>
                <td class="px-5 py-4"><div class="h-3.5 bg-stone-100 rounded-full w-24 mb-2"/><div class="h-2.5 bg-stone-50 rounded-full w-16"/></td>
                <td class="px-5 py-4"><div class="h-6 bg-stone-100 rounded-full w-20"/></td>
                <td class="px-5 py-4 flex justify-end"><div class="h-3.5 bg-stone-100 rounded-full w-24"/></td>
              </tr>
            </tbody>

            <!-- Empty -->
            <tbody v-else-if="bookings.length === 0">
              <tr>
                <td colspan="6" class="px-5 py-16 text-center">
                  <div class="w-12 h-12 rounded-2xl bg-stone-100 flex items-center justify-center mx-auto mb-3">
                    <svg class="w-6 h-6 text-stone-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                    </svg>
                  </div>
                  <p class="font-bold text-stone-700 mb-1">Tidak ada data</p>
                  <p class="text-sm text-stone-400">Tidak ada booking yang sesuai filter.</p>
                </td>
              </tr>
            </tbody>

            <!-- Rows -->
            <tbody v-else class="divide-y divide-stone-50">
              <tr
                v-for="booking in bookings"
                :key="booking.uuid"
                @click="openDrawer(booking)"
                class="hover:bg-stone-50/80 cursor-pointer transition-colors group"
              >
                <td class="px-5 py-4 whitespace-nowrap">
                  <div class="font-mono text-xs font-bold text-stone-700 group-hover:text-stone-900 tracking-wider">{{ booking.booking_number }}</div>
                  <div class="text-[11px] text-stone-400 mt-1">{{ formatDateShort(booking.created_at) }}</div>
                </td>
                <td class="px-5 py-4 whitespace-nowrap">
                  <div class="text-sm font-semibold text-stone-800">{{ booking.contact_name || '-' }}</div>
                  <div class="text-[11px] text-stone-400 mt-1">{{ booking.contact_phone || '-' }}</div>
                </td>
                <td class="px-5 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-stone-800 capitalize">{{ booking.category }} <span class="text-stone-400">({{ booking.camera_count }}×)</span></div>
                  <div class="text-[11px] text-stone-400 mt-1">{{ booking.city }} · {{ booking.distance_km }} km</div>
                </td>
                <td class="px-5 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-stone-800">{{ formatDateShort(booking.scheduled_date) }}</div>
                  <div class="text-[11px] text-stone-400 mt-1">{{ booking.time_slot }}</div>
                </td>
                <td class="px-5 py-4 whitespace-nowrap">
                  <span :class="statusBadge(booking.status).cls" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border">
                    <span class="w-1.5 h-1.5 rounded-full" :class="statusBadge(booking.status).dot"/>
                    {{ booking.status?.replace('_', ' ') || 'pending' }}
                  </span>
                </td>
                <td class="px-5 py-4 whitespace-nowrap text-right">
                  <div class="text-sm font-bold text-stone-900">{{ fmt(booking.total_price) }}</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="bg-stone-50/50 px-5 py-3.5 border-t border-stone-100 flex items-center justify-between">
          <p class="text-xs text-stone-500 hidden sm:block">
            <span class="font-semibold text-stone-700">{{ pagination.total === 0 ? 0 : (pagination.page - 1) * pagination.size + 1 }}–{{ Math.min(pagination.page * pagination.size, pagination.total) }}</span>
            dari {{ pagination.total }} data
          </p>
          <div class="flex items-center gap-2 ml-auto">
            <button @click="changePage(pagination.page - 1)" :disabled="pagination.page === 1"
              class="px-3.5 py-1.5 text-xs font-semibold text-stone-600 bg-white border border-stone-200 rounded-lg hover:border-stone-400 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95">
              ← Prev
            </button>
            <span class="text-xs font-mono text-stone-500 px-1">{{ pagination.page }} / {{ Math.ceil(pagination.total / pagination.size) || 1 }}</span>
            <button @click="changePage(pagination.page + 1)" :disabled="pagination.page * pagination.size >= pagination.total"
              class="px-3.5 py-1.5 text-xs font-semibold text-stone-600 bg-white border border-stone-200 rounded-lg hover:border-stone-400 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95">
              Next →
            </button>
          </div>
        </div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════════════════ -->
    <!-- DRAWER BACKDROP — z-[9998]                               -->
    <!-- ══════════════════════════════════════════════════════════ -->
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
          class="fixed inset-0 bg-stone-950/50 backdrop-blur-sm"
          style="z-index:9998"
          @click="closeDrawer"
        />
      </Transition>

      <!-- ══════════════════════════════════════════════════════ -->
      <!-- DRAWER PANEL — z-[9999]                              -->
      <!-- ══════════════════════════════════════════════════════ -->
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
          class="fixed inset-y-0 right-0 w-full max-w-[500px] flex flex-col bg-white shadow-2xl border-l border-stone-200"
          style="z-index:9999"
        >

          <!-- Drawer Header -->
          <div class="px-6 py-5 border-b border-stone-100 flex items-start justify-between shrink-0 bg-white">
            <div>
              <p class="text-[10px] font-black tracking-[0.2em] uppercase text-stone-400 mb-1">Detail Booking</p>
              <p class="font-mono text-base font-bold text-stone-900 tracking-wider">{{ drawer.data.booking_number }}</p>
            </div>
            <button @click="closeDrawer" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-stone-100 text-stone-400 hover:text-stone-700 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Drawer Scroll Body -->
          <div class="flex-1 overflow-y-auto custom-scrollbar">

            <!-- Status Banner -->
            <div class="px-6 pt-5 pb-4 border-b border-stone-50">
              <div class="flex items-center justify-between">
                <span :class="statusBadge(drawer.data.status).cls" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-bold uppercase tracking-wider border">
                  <span class="w-1.5 h-1.5 rounded-full" :class="statusBadge(drawer.data.status).dot"/>
                  {{ drawer.data.status?.replace('_', ' ') || 'pending' }}
                </span>
                <span class="text-xs text-stone-400">Dibuat {{ formatDateShort(drawer.data.created_at) }}</span>
              </div>
            </div>

            <div class="px-6 py-5 space-y-7">

              <!-- Pelanggan -->
              <section>
                <p class="text-[10px] font-black tracking-[0.2em] uppercase text-stone-400 mb-3">Pelanggan</p>
                <div class="space-y-2.5">
                  <div class="flex justify-between items-baseline py-2 border-b border-stone-50">
                    <span class="text-xs text-stone-400">Nama</span>
                    <span class="text-sm font-semibold text-stone-800">{{ drawer.data.contact_name || '-' }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-stone-50">
                    <span class="text-xs text-stone-400">WhatsApp</span>
                    <a
                      v-if="drawer.data.contact_phone"
                      :href="`https://wa.me/${drawer.data.contact_phone.replace(/^0/, '62')}`"
                      target="_blank"
                      class="text-sm font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1 transition-colors"
                    >
                      {{ drawer.data.contact_phone }}
                      <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                    </a>
                    <span v-else class="text-sm text-stone-500">-</span>
                  </div>
                  <div class="py-2">
                    <span class="text-xs text-stone-400 block mb-1.5">Alamat</span>
                    <span class="text-sm font-medium text-stone-800 leading-relaxed">{{ drawer.data.address || '-' }}</span>
                    <span class="text-xs text-stone-400 block mt-1">{{ drawer.data.city }} · {{ drawer.data.distance_km }} km</span>
                  </div>
                </div>
              </section>

              <!-- Layanan -->
              <section>
                <p class="text-[10px] font-black tracking-[0.2em] uppercase text-stone-400 mb-3">Detail Layanan</p>
                <div class="bg-stone-50 rounded-xl overflow-hidden">
                  <div class="grid grid-cols-2 divide-x divide-stone-100">
                    <div class="p-3">
                      <p class="text-[10px] text-stone-400 uppercase tracking-wider mb-1">Kategori</p>
                      <p class="text-sm font-bold text-stone-800 capitalize">{{ drawer.data.category }}</p>
                    </div>
                    <div class="p-3">
                      <p class="text-[10px] text-stone-400 uppercase tracking-wider mb-1">Brand</p>
                      <p class="text-sm font-bold text-stone-800 uppercase">{{ drawer.data.brand }}</p>
                    </div>
                  </div>
                  <div class="border-t border-stone-100 grid grid-cols-2 divide-x divide-stone-100">
                    <div class="p-3">
                      <p class="text-[10px] text-stone-400 uppercase tracking-wider mb-1">Jumlah Titik</p>
                      <p class="text-sm font-bold text-stone-800">{{ drawer.data.camera_count }} titik</p>
                    </div>
                    <div class="p-3">
                      <p class="text-[10px] text-stone-400 uppercase tracking-wider mb-1">Jadwal</p>
                      <p class="text-sm font-bold text-stone-800">{{ formatDateShort(drawer.data.scheduled_date) }}</p>
                      <p class="text-xs text-stone-400">{{ drawer.data.time_slot }}</p>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Rincian Harga -->
              <section>
                <p class="text-[10px] font-black tracking-[0.2em] uppercase text-stone-400 mb-3">Rincian Harga</p>
                <div class="space-y-2">
                  <div v-if="drawer.data.device_price > 0" class="flex justify-between text-sm">
                    <span class="text-stone-500">Perangkat</span>
                    <span class="font-medium text-stone-700">{{ fmt(drawer.data.device_price) }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-stone-500">Jasa ({{ drawer.data.camera_count }} titik)</span>
                    <span class="font-medium text-stone-700">{{ fmt(drawer.data.service_price) }}</span>
                  </div>
                  <div v-if="drawer.data.addon_price > 0" class="flex justify-between text-sm">
                    <span class="text-stone-500">Add-ons</span>
                    <span class="font-medium text-stone-700">{{ fmt(drawer.data.addon_price) }}</span>
                  </div>
                  <div v-if="drawer.data.transport_fee > 0" class="flex justify-between text-sm">
                    <span class="text-stone-500">Transport</span>
                    <span class="font-medium text-stone-700">{{ fmt(drawer.data.transport_fee) }}</span>
                  </div>
                  <div class="pt-2.5 border-t border-stone-100 flex justify-between items-baseline">
                    <span class="font-bold text-stone-800">Total</span>
                    <span class="text-lg font-black text-stone-900">{{ fmt(drawer.data.total_price) }}</span>
                  </div>
                </div>
              </section>

              <!-- Pembayaran -->
              <section>
                <p class="text-[10px] font-black tracking-[0.2em] uppercase text-stone-400 mb-3">Pembayaran</p>
                <div class="grid grid-cols-2 gap-2 mb-3">
                  <div class="bg-blue-50 border border-blue-100 rounded-xl p-3">
                    <p class="text-[10px] text-blue-500 uppercase tracking-wider font-bold mb-1">DP {{ drawer.data.dp_percentage }}%</p>
                    <p class="text-sm font-black text-blue-900">{{ fmt(drawer.data.dp_amount) }}</p>
                  </div>
                  <div class="bg-amber-50 border border-amber-100 rounded-xl p-3">
                    <p class="text-[10px] text-amber-500 uppercase tracking-wider font-bold mb-1">Sisa</p>
                    <p class="text-sm font-black text-amber-900">{{ fmt(drawer.data.remaining_amount) }}</p>
                  </div>
                </div>

                <!-- Payment list -->
                <div v-if="drawer.data.payments?.length" class="space-y-2">
                  <div
                    v-for="pay in drawer.data.payments"
                    :key="pay.uuid"
                    class="flex items-center justify-between p-3 bg-white border border-stone-100 rounded-xl"
                  >
                    <div>
                      <p class="text-xs font-bold text-stone-800 uppercase tracking-wider">{{ pay.payment_type }}</p>
                      <p class="text-[10px] font-mono text-stone-400 mt-0.5">{{ pay.order_id }}</p>
                    </div>
                    <div class="text-right">
                      <p class="text-sm font-bold text-stone-900 mb-1">{{ fmt(pay.gross_amount) }}</p>
                      <span
                        class="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                        :class="pay.status === 'success'
                          ? 'bg-emerald-100 text-emerald-700'
                          : pay.status === 'pending'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-red-100 text-red-600'"
                      >{{ pay.status }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-5 rounded-xl border border-dashed border-stone-200">
                  <p class="text-xs text-stone-400">Belum ada riwayat pembayaran</p>
                </div>
              </section>

            </div><!-- end scroll body inner -->
          </div><!-- end scroll body -->

          <!-- ════════════════════════════════════ -->
          <!-- DRAWER FOOTER                       -->
          <!-- ════════════════════════════════════ -->
          <div class="shrink-0 border-t border-stone-100 bg-stone-50/80 p-5 space-y-4">

            <!-- Update Status -->
            <div>
              <p class="text-[10px] font-black tracking-[0.2em] uppercase text-stone-400 mb-2.5">Update Status</p>
              <div class="flex gap-2">
                <select
                  v-model="actionState.selectedStatus"
                  :disabled="actionState.isUpdatingStatus"
                  class="flex-1 px-3 py-2.5 bg-white border border-stone-200 rounded-xl text-sm text-stone-700 focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition-all cursor-pointer disabled:opacity-50"
                >
                  <option value="pending">Pending</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="dp_paid">DP Paid</option>
                  <option value="progress">In Progress</option>
                  <option value="done">Done</option>
                  <option value="lunas">Lunas</option>
                  <option value="cancel">Canceled</option>
                </select>
                <button
                  @click="updateStatus"
                  :disabled="actionState.isUpdatingStatus || actionState.selectedStatus === drawer.data.status"
                  class="px-4 py-2.5 bg-stone-900 hover:bg-stone-700 text-white text-sm font-bold rounded-xl transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 whitespace-nowrap"
                >
                  <svg v-if="actionState.isUpdatingStatus" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Update
                </button>
              </div>

              <!-- Notes field — muncul kalau status berubah -->
              <div v-if="actionState.selectedStatus !== drawer.data.status" class="mt-2">
                <input
                  v-model="actionState.notes"
                  type="text"
                  placeholder="Catatan (opsional)..."
                  class="w-full px-3 py-2 bg-white border border-stone-200 rounded-xl text-sm text-stone-700 placeholder-stone-400 focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-200 transition-all"
                />
              </div>

              <!-- Feedback -->
              <div v-if="actionState.feedback" class="mt-2 flex items-center gap-2">
                <div
                  class="w-full text-center px-3 py-2 rounded-xl text-xs font-semibold"
                  :class="actionState.feedback.type === 'ok'
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-red-50 text-red-700 border border-red-200'"
                >{{ actionState.feedback.msg }}</div>
              </div>
            </div>

            <!-- Payment Buttons -->
            <div
              v-if="drawer.data.status !== 'lunas' && drawer.data.status !== 'cancel'"
              class="grid grid-cols-1 gap-2 pt-1 border-t border-stone-200"
            >
              <!-- Bayar DP — hanya saat confirmed -->
              <button
                v-if="drawer.data.status === 'confirmed'"
                @click="processPayment('dp')"
                :disabled="actionState.isProcessingPayment"
                class="w-full flex items-center justify-center gap-2 py-3 bg-amber-500 hover:bg-amber-600 text-white text-sm font-black rounded-xl transition-all active:scale-95 disabled:opacity-50 uppercase tracking-wide"
              >
                <svg v-if="actionState.isProcessingPayment" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>
                </svg>
                Bayar DP — {{ fmt(drawer.data.dp_amount) }}
              </button>

              <!-- Bayar Lunas — hanya saat done -->
              <button
                v-if="drawer.data.status === 'done' && drawer.data.remaining_amount > 0"
                @click="processPayment('lunas')"
                :disabled="actionState.isProcessingPayment"
                class="w-full flex items-center justify-center gap-2 py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-black rounded-xl transition-all active:scale-95 disabled:opacity-50 uppercase tracking-wide"
              >
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
import api from '@/service/api'

// ── State ──────────────────────────────────────────────────
const bookings  = ref([])
const isLoading = ref(true)

const filters = reactive({
  search: '',
  status: '',
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
  selectedStatus: '',
  notes: '',
  feedback: null,   // { type: 'ok'|'err', msg: string }
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
  actionState.notes       = ''
  actionState.feedback    = null
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
      }
    )
    // Update local state
    drawer.data.status = actionState.selectedStatus
    actionState.notes  = ''
    showFeedback('ok', `✓ Status diperbarui ke "${actionState.selectedStatus.replace('_', ' ')}"`)
    fetchBookings()
  } catch (e) {
    const msg = e?.response?.data?.detail || 'Gagal memperbarui status.'
    showFeedback('err', `✗ ${msg}`)
    console.error('updateStatus:', e)
  } finally {
    actionState.isUpdatingStatus = false
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
onMounted(fetchBookings)
</script>