<template>
  <div class="min-h-screen bg-[#F7F8FC] font-sans pb-12">
    
    <!-- ── Header ─────────────────────────────── -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
        <div class="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                </div>
                <div>
                    <h1 class="text-lg font-bold text-gray-900 tracking-tight leading-none">Tim & Jadwal</h1>
                    <p class="text-xs text-gray-400 mt-0.5">Manajemen teknisi, operasional & libur</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <button @click="openTechModal()"
                    class="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 active:scale-95 transition-all shadow-sm">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Tambah Teknisi
                </button>
            </div>
        </div>
    </div>

    <div class="max-w-screen-2xl mx-auto px-6 py-8">
      
      <!-- ── Capacity Summary ──────────────────────── -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm relative overflow-hidden group">
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <svg class="w-12 h-12 text-indigo-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
          </div>
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Total Teknisi Aktif</p>
          <p class="text-3xl font-black text-gray-900">{{ activeTechCount }} <span class="text-xs font-bold text-gray-400 uppercase ml-1">Personil</span></p>
          <div class="mt-4 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-[11px] font-bold text-emerald-600 uppercase tracking-wide">Siap Bertugas</span>
          </div>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm relative overflow-hidden group">
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <svg class="w-12 h-12 text-blue-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Potensi Kapasitas / Slot</p>
          <p class="text-3xl font-black text-gray-900">{{ activeTechCount }} <span class="text-xs font-bold text-gray-400 uppercase ml-1">Booking</span></p>
          <p class="mt-4 text-[11px] font-medium text-gray-500 leading-tight">Sesuai jumlah teknisi yang tersedia di lapangan saat ini.</p>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm relative overflow-hidden group">
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <svg class="w-12 h-12 text-amber-600" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/></svg>
          </div>
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Max Kapasitas Harian</p>
          <p class="text-3xl font-black text-gray-900">{{ activeTechCount * 3 }} <span class="text-xs font-bold text-gray-400 uppercase ml-1">Titik Jasa</span></p>
          <p class="mt-4 text-[11px] font-medium text-gray-500 leading-tight">Total slot yang bisa diambil (Pagi, Siang, Sore).</p>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex items-center gap-1 bg-gray-200/50 p-1 rounded-xl w-fit mb-8 border border-gray-200 shadow-sm">
        <button 
          v-for="tab in tabs" :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-6 py-2 text-sm font-bold rounded-lg transition-all duration-200',
            activeTab === tab.id 
              ? 'bg-white text-gray-900 shadow-md ring-1 ring-gray-200' 
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- ── TAB 1: TEKNISI ────────────────────────────────────────── -->
      <div v-if="activeTab === 'technicians'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-bold text-gray-800">Daftar Teknisi</h2>
        </div>

        <div v-if="loading.tech" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm animate-pulse">
            <div class="flex items-center gap-4 mb-4">
              <div class="w-16 h-16 bg-gray-100 rounded-xl" />
              <div class="flex-1">
                <div class="h-4 bg-gray-100 rounded-full w-2/3 mb-2" />
                <div class="h-3 bg-gray-50 rounded-full w-1/3" />
              </div>
            </div>
            <div class="h-10 bg-gray-50 rounded-lg" />
          </div>
        </div>

        <div v-else-if="technicians.length === 0" class="bg-white rounded-xl p-12 border border-dashed border-gray-200 text-center">
          <div class="w-16 h-16 bg-gray-50 rounded-xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/></svg>
          </div>
          <p class="text-gray-500 font-medium">Belum ada teknisi terdaftar.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="tech in technicians" :key="tech.uuid" class="group bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-all duration-300 relative overflow-hidden">
            <div class="absolute top-0 right-0 p-4">
              <span :class="tech.is_active ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-red-50 text-red-600 border-red-100'" class="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border shadow-sm">
                {{ tech.is_active ? 'Aktif' : 'Nonaktif' }}
              </span>
            </div>
            
            <div class="flex items-center gap-5 mb-6">
              <div class="w-20 h-20 rounded-xl bg-gray-50 border border-gray-100 shadow-sm overflow-hidden shrink-0 flex items-center justify-center">
                <img v-if="tech.picture_url" :src="tech.picture_url" alt="Foto teknisi" class="w-full h-full object-cover" />
                <svg v-else class="w-8 h-8 text-gray-300" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
              </div>
              <div class="min-w-0">
                <h3 class="text-lg font-bold text-gray-900 truncate tracking-tight">{{ tech.name }}</h3>
                <p class="text-xs font-mono font-bold text-gray-400 mt-0.5 tracking-wider">{{ tech.id_employee }}</p>
              </div>
            </div>

            <div class="space-y-3 mb-6">
              <div class="flex items-center gap-3 text-gray-600 p-2 bg-gray-50 rounded-lg">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                <span class="text-sm font-semibold tracking-tight">{{ tech.phone || '-' }}</span>
              </div>
            </div>

            <div class="flex items-center gap-2 pt-2 border-t border-gray-50">
              <button @click="openTechModal(tech)" class="flex-1 py-2 text-xs font-bold text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition active:scale-95">
                Edit Profil
              </button>
              <button @click="viewSchedule(tech)" class="flex-1 py-2 text-xs font-bold text-indigo-600 hover:bg-indigo-50 rounded-lg transition active:scale-95 border border-indigo-100">
                Lihat Jadwal
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ── TAB 2: OPERASIONAL ────────────────────────────────────── -->
      <div v-if="activeTab === 'hours'" class="max-w-3xl">
        <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="p-6 border-b border-gray-100">
            <h2 class="text-lg font-bold text-gray-900 tracking-tight">Jam Operasional Mingguan</h2>
            <p class="text-xs text-gray-400 mt-0.5">Konfigurasi waktu operasional dan batas booking harian</p>
          </div>
          
          <div v-if="loading.hours" class="p-6 space-y-4">
            <div v-for="i in 7" :key="i" class="h-16 bg-gray-50 rounded-lg animate-pulse" />
          </div>

          <div v-else class="divide-y divide-gray-50">
            <div v-for="(h, idx) in sortedHours" :key="h.day_of_week" class="p-5 flex items-center justify-between hover:bg-gray-50/50 transition-colors">
              <div class="flex items-center gap-6">
                <div class="w-16 text-sm font-bold text-gray-400 uppercase tracking-wider">{{ dayNames[h.day_of_week] }}</div>
                <div class="flex items-center gap-4">
                  <div 
                    @click="toggleDay(h)"
                    :class="h.is_open ? 'bg-indigo-600' : 'bg-gray-200'" 
                    class="w-11 h-6 rounded-full relative cursor-pointer transition-all duration-300"
                  >
                    <div :class="h.is_open ? 'translate-x-5' : 'translate-x-0'" class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform duration-300" />
                  </div>
                  <span :class="h.is_open ? 'text-indigo-600 font-bold' : 'text-gray-300 font-medium'" class="text-xs uppercase tracking-widest">{{ h.is_open ? 'Buka' : 'Tutup' }}</span>
                </div>
              </div>

              <div class="flex items-center gap-4" v-if="h.is_open">
                <div class="flex flex-col items-end">
                  <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Jam Kerja</p>
                  <input 
                    v-model="h.hours" 
                    @change="updateHours(h)"
                    class="w-32 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-bold text-gray-700 text-center focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                    placeholder="08:00-17:00"
                  />
                </div>
                <div class="flex flex-col items-end">
                  <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Batas Manual (Optional)</p>
                  <div class="flex items-center gap-2">
                    <input 
                      v-model.number="h.max_bookings" 
                      @change="updateHours(h)"
                      type="number"
                      class="w-20 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-bold text-gray-700 text-center focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                    />
                    <div class="group relative">
                      <svg class="w-4 h-4 text-gray-300 cursor-help" fill="currentColor" viewBox="0 0 20 20"><path d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"/></svg>
                      <div class="absolute bottom-full right-0 mb-2 w-48 p-2 bg-gray-900 text-[10px] text-white rounded shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                        Sistem menggunakan jumlah teknisi aktif ({{ activeTechCount }}) sebagai batas booking. <br><br>Isi nilai > 0 jika ingin membatasi lebih ketat (Misal: max 2 saja). Isi 0 untuk menggunakan jumlah teknisi.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── TAB 3: HARI LIBUR ────────────────────────────────────── -->
      <div v-if="activeTab === 'holidays'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-bold text-gray-800">Kalender Libur Layanan</h2>
          <button @click="openHolidayModal" class="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg transition shadow-sm active:scale-95">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/></svg>
            Tambah Hari Libur
          </button>
        </div>

        <div v-if="loading.holidays" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="h-32 bg-white rounded-xl border border-gray-200 animate-pulse" />
        </div>

        <div v-else-if="holidays.length === 0" class="bg-white rounded-xl p-12 border border-dashed border-gray-200 text-center text-gray-400 font-medium">
          Belum ada hari libur yang dikonfigurasi.
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="h in holidays" :key="h.uuid" class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm flex flex-col justify-between group hover:shadow-md transition-all">
            <div>
              <div class="flex items-center justify-between mb-4">
                <div class="px-2.5 py-1 bg-red-50 text-red-600 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-red-100">Libur</div>
                <button @click="deleteHoliday(h)" class="p-1.5 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                </button>
              </div>
              <h4 class="text-lg font-bold text-gray-900 tracking-tight">{{ formatFullDate(h.holiday_date) }}</h4>
              <p class="text-xs text-gray-400 mt-1 line-clamp-2 leading-relaxed">{{ h.description || 'Tidak ada keterangan' }}</p>
            </div>
            <div class="mt-4 pt-4 border-t border-gray-50 text-[10px] font-bold text-gray-300 uppercase tracking-widest">
              Ditambah: {{ formatDateShort(h.created_at) }}
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ── MODALS ────────────────────────────────────────────────── -->

    <!-- Tech Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="modals.tech.isOpen" class="fixed inset-0 z-[10000] flex items-center justify-center p-4 sm:p-6">
          <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="modals.tech.isOpen = false" />
          <div class="modal-card relative bg-white w-full max-w-lg rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
            <div class="p-6 border-b border-gray-100 flex items-center justify-between">
              <h3 class="text-lg font-bold text-gray-900 tracking-tight">{{ modals.tech.data.uuid ? 'Edit Teknisi' : 'Tambah Teknisi Baru' }}</h3>
              <button @click="modals.tech.isOpen = false" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400 transition-colors">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <div class="p-6 space-y-6">
              <!-- Profile Picture -->
              <div class="flex items-center gap-6">
                <div class="w-20 h-20 rounded-xl bg-gray-50 border border-dashed border-gray-200 flex items-center justify-center overflow-hidden relative group">
                  <img v-if="modals.tech.data.picture_url" :src="modals.tech.data.picture_url" alt="Pratinjau foto teknisi" class="w-full h-full object-cover" />
                  <svg v-else class="w-8 h-8 text-gray-200" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                  <div class="absolute inset-0 bg-gray-900/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
                    <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                  </div>
                  <input type="file" @change="handleTechPicture" class="absolute inset-0 opacity-0 cursor-pointer" accept="image/*" />
                </div>
                <div class="flex-1">
                  <p class="text-sm font-bold text-gray-900 mb-1">Foto Profil</p>
                  <p class="text-xs text-gray-400 leading-relaxed">Gunakan foto formal ukuran 1:1. Maks 2MB.</p>
                  <div v-if="modals.tech.isUploading" class="mt-2 text-[10px] font-bold text-indigo-500 animate-pulse uppercase tracking-widest">Uploading...</div>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div class="col-span-2">
                  <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Nama Lengkap</label>
                  <input v-model="modals.tech.data.name" type="text" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all" placeholder="Contoh: Budi Santoso" />
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">ID Pegawai</label>
                  <input v-model="modals.tech.data.id_employee" type="text" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-mono font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all" placeholder="PJC-001" />
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">WhatsApp</label>
                  <input v-model="modals.tech.data.phone" type="text" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all" placeholder="08xxx" />
                </div>
              </div>

              <div class="flex items-center gap-3 p-4 bg-gray-50 rounded-xl border border-gray-100">
                <div 
                  @click="modals.tech.data.is_active = !modals.tech.data.is_active"
                  :class="modals.tech.data.is_active ? 'bg-indigo-600' : 'bg-gray-300'" 
                  class="w-11 h-6 rounded-full relative cursor-pointer transition-all duration-300"
                >
                  <div :class="modals.tech.data.is_active ? 'translate-x-5' : 'translate-x-0'" class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform duration-300" />
                </div>
                <div class="flex-1">
                  <p class="text-sm font-bold text-gray-800">{{ modals.tech.data.is_active ? 'Status: Aktif' : 'Status: Nonaktif' }}</p>
                  <p class="text-[10px] text-gray-400 font-medium">Teknisi nonaktif tidak akan muncul di opsi penugasan</p>
                </div>
              </div>
            </div>

            <div class="p-6 bg-gray-50 flex items-center gap-3 border-t border-gray-100">
              <button @click="modals.tech.isOpen = false" class="flex-1 py-2.5 text-sm font-bold text-gray-400 hover:text-gray-600 transition uppercase tracking-widest">Batal</button>
              <button @click="saveTechnician" :disabled="modals.tech.isSaving" class="flex-[2] py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-lg shadow-sm transition-all active:scale-95 disabled:opacity-50 uppercase tracking-widest">
                {{ modals.tech.isSaving ? 'Menyimpan...' : 'Simpan Perubahan' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Holiday Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="modals.holiday.isOpen" class="fixed inset-0 z-[10000] flex items-center justify-center p-4 sm:p-6">
          <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="modals.holiday.isOpen = false" />
          <div class="modal-card relative bg-white w-full max-w-md rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
            <div class="p-6 border-b border-gray-100 flex items-center justify-between">
              <h3 class="text-lg font-bold text-gray-900 tracking-tight">Atur Libur Layanan</h3>
              <button @click="modals.holiday.isOpen = false" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400 transition-colors">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
            <div class="p-6 space-y-6">
              <div>
                <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Tanggal Libur</label>
                <input v-model="modals.holiday.data.date" type="date" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all cursor-pointer" />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Keterangan</label>
                <textarea v-model="modals.holiday.data.description" rows="3" class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-medium text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all" placeholder="Contoh: Libur Nasional / Training Internal..."></textarea>
              </div>
            </div>
            <div class="p-6 bg-gray-50 flex items-center gap-3 border-t border-gray-100">
              <button @click="modals.holiday.isOpen = false" class="flex-1 py-2.5 text-sm font-bold text-gray-400 hover:text-gray-600 transition uppercase tracking-widest">Batal</button>
              <button @click="saveHoliday" :disabled="modals.holiday.isSaving" class="flex-[2] py-2.5 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded-lg shadow-sm transition-all active:scale-95 disabled:opacity-50 uppercase tracking-widest">
                {{ modals.holiday.isSaving ? 'Menyimpan...' : 'Simpan Libur' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Schedule Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="modals.schedule.isOpen" class="fixed inset-0 z-[10000] flex items-center justify-center p-4 sm:p-6">
          <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="modals.schedule.isOpen = false" />
          <div class="modal-card relative bg-white w-full max-w-2xl rounded-2xl shadow-2xl border border-gray-100 overflow-hidden flex flex-col max-h-[90vh]">
            <div class="p-6 border-b border-gray-100 flex items-center justify-between bg-white sticky top-0 z-10">
              <div>
                <h3 class="text-lg font-bold text-gray-900 tracking-tight">Jadwal Penugasan</h3>
                <p class="text-xs text-gray-400 mt-0.5">{{ modals.schedule.techName }} ({{ modals.schedule.techId }})</p>
              </div>
              <button @click="modals.schedule.isOpen = false" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400 transition-colors">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <div class="flex-1 overflow-y-auto p-6 bg-gray-50/30">
              <div v-if="modals.schedule.loading" class="space-y-4">
                <div v-for="i in 3" :key="i" class="h-20 bg-gray-100 rounded-xl animate-pulse" />
              </div>

              <div v-else-if="modals.schedule.bookings.length === 0" class="py-12 text-center text-gray-400">
                <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/></svg>
                </div>
                <p class="font-medium text-sm">Tidak ada jadwal penugasan aktif.</p>
              </div>

              <div v-else class="space-y-4">
                <div v-for="b in modals.schedule.bookings" :key="b.uuid" class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all">
                  <div class="flex items-center justify-between mb-3">
                    <div class="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider border shadow-sm" :class="getStatusStyle(b.status)">
                      {{ b.status }}
                    </div>
                    <div class="text-xs font-mono font-bold text-gray-400">#{{ b.booking_number }}</div>
                  </div>
                  
                  <div class="grid grid-cols-2 gap-4">
                    <div class="flex items-center gap-3">
                      <div class="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                      </div>
                      <div>
                        <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest leading-none mb-1">Tanggal</div>
                        <div class="text-sm font-bold text-gray-700 leading-none">{{ formatFullDate(b.scheduled_date) }}</div>
                      </div>
                    </div>
                    <div class="flex items-center gap-3">
                      <div class="p-2 bg-blue-50 rounded-lg text-blue-600">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                      </div>
                      <div>
                        <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest leading-none mb-1">Slot Waktu</div>
                        <div class="text-sm font-bold text-gray-700 leading-none">{{ b.time_slot }}</div>
                      </div>
                    </div>
                  </div>

                  <div class="mt-4 pt-4 border-t border-gray-50 flex items-start gap-3">
                    <svg class="w-4 h-4 text-gray-300 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/><path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                    <p class="text-xs text-gray-500 font-medium leading-relaxed">{{ b.address }}, {{ b.district }}, {{ b.city }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="p-4 bg-gray-50 border-t border-gray-100 shrink-0">
              <button @click="modals.schedule.isOpen = false" class="w-full py-2.5 text-sm font-bold text-gray-500 hover:text-gray-700 transition uppercase tracking-widest">Tutup Jadwal</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/service/api'

const toastStore = useToastStore()

// ── State ──────────────────────────────────────────────────
const activeTab = ref('technicians')
const tabs = [
  { id: 'technicians', label: 'Teknisi' },
  { id: 'hours',       label: 'Jam Operasional' },
  { id: 'holidays',    label: 'Hari Libur' },
]

const dayNames = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']

const technicians = ref([])
const holidays    = ref([])
const hours       = ref([])

const activeTechCount = computed(() => {
  return technicians.value.filter(t => t.is_active).length || 0
})

const loading = reactive({
  tech: true,
  hours: true,
  holidays: true
})

const modals = reactive({
  tech: {
    isOpen: false,
    isSaving: false,
    isUploading: false,
    data: { uuid: null, name: '', id_employee: '', phone: '', picture_url: '', is_active: true }
  },
  holiday: {
    isOpen: false,
    isSaving: false,
    data: { date: '', description: '' }
  },
  schedule: {
    isOpen: false,
    loading: false,
    bookings: [],
    techName: '',
    techId: ''
  }
})

// ── Fetching ───────────────────────────────────────────────
const fetchAll = async () => {
  fetchTech()
  fetchHours()
  fetchHolidays()
}

const fetchTech = async () => {
  loading.tech = true
  try {
    const res = await api.get('/admin/service/technicians?active_only=false')
    technicians.value = res.data
  } catch (e) { console.error(e) }
  finally { loading.tech = false }
}

const fetchHours = async () => {
  loading.hours = true
  try {
    const res = await api.get('/admin/service/hours')
    hours.value = res.data
  } catch (e) { console.error(e) }
  finally { loading.hours = false }
}

const fetchHolidays = async () => {
  loading.holidays = true
  try {
    const res = await api.get('/admin/service/holidays')
    holidays.value = res.data
  } catch (e) { console.error(e) }
  finally { loading.holidays = false }
}

// ── Technician Management ──────────────────────────────────
const openTechModal = (tech = null) => {
  if (tech) {
    modals.tech.data = { ...tech }
  } else {
    modals.tech.data = { uuid: null, name: '', id_employee: '', phone: '', picture_url: '', is_active: true }
  }
  modals.tech.isOpen = true
}

const handleTechPicture = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  modals.tech.isUploading = true
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const res = await api.post('/admin/service/technicians/upload-picture', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    modals.tech.data.picture_url = res.data.url
  } catch (e) {
    toastStore.error('Gagal upload gambar: ' + (e.response?.data?.detail || e.message))
  } finally {
    modals.tech.isUploading = false
  }
}

const saveTechnician = async () => {
  const { uuid, ...payload } = modals.tech.data
  if (!payload.name || !payload.id_employee) {
    toastStore.warning('Nama dan ID Pegawai wajib diisi.')
    return
  }
  
  modals.tech.isSaving = true
  try {
    if (uuid) {
      await api.patch(`/admin/service/technicians/${uuid}`, payload)
    } else {
      await api.post('/admin/service/technicians', payload)
    }
    modals.tech.isOpen = false
    fetchTech()
    toastStore.success('Profil teknisi berhasil disimpan.')
  } catch (e) {
    toastStore.error('Gagal menyimpan: ' + (e.response?.data?.detail || e.message))
  } finally {
    modals.tech.isSaving = false
  }
}

const viewSchedule = async (tech) => {
  modals.schedule.techName = tech.name
  modals.schedule.techId = tech.id_employee
  modals.schedule.isOpen = true
  modals.schedule.loading = true
  modals.schedule.bookings = []
  
  try {
    const res = await api.get(`/admin/service/technicians/${tech.uuid}`)
    modals.schedule.bookings = res.data.bookings || []
  } catch (e) {
    console.error(e)
    toastStore.error('Gagal mengambil jadwal teknisi')
  } finally {
    modals.schedule.loading = false
  }
}

const getStatusStyle = (status) => {
  const s = status.toLowerCase()
  if (s === 'pending') return 'bg-amber-50 text-amber-600 border-amber-100'
  if (s === 'confirmed') return 'bg-blue-50 text-blue-600 border-blue-100'
  if (s === 'dp_paid') return 'bg-indigo-50 text-indigo-600 border-indigo-100'
  if (s === 'progress') return 'bg-purple-50 text-purple-600 border-purple-100'
  if (s === 'done' || s === 'lunas') return 'bg-emerald-50 text-emerald-600 border-emerald-100'
  if (s === 'cancel') return 'bg-red-50 text-red-600 border-red-100'
  return 'bg-gray-50 text-gray-400 border-gray-100'
}

// ── Operational Hours ──────────────────────────────────────
const sortedHours = computed(() => {
  return [...hours.value].sort((a, b) => a.day_of_week - b.day_of_week)
})

const toggleDay = async (h) => {
  h.is_open = !h.is_open
  await updateHours(h)
}

const updateHours = async (h) => {
  try {
    await api.patch(`/admin/service/hours/${h.day_of_week}`, {
      is_open: h.is_open,
      hours: h.hours,
      max_bookings: h.max_bookings
    })
    toastStore.success('Jam operasional berhasil diupdate.')
  } catch (e) {
    toastStore.error('Gagal update jam operasional: ' + (e.response?.data?.detail || e.message))
    fetchHours() // revert
  }
}

// ── Holiday Management ─────────────────────────────────────
const openHolidayModal = () => {
  modals.holiday.data = { date: '', description: '' }
  modals.holiday.isOpen = true
}

const saveHoliday = async () => {
  if (!modals.holiday.data.date) return
  modals.holiday.isSaving = true
  try {
    await api.post('/admin/service/holidays', {
      holiday_date: modals.holiday.data.date,
      description: modals.holiday.data.description
    })
    modals.holiday.isOpen = false
    fetchHolidays()
    toastStore.success('Hari libur berhasil disimpan.')
  } catch (e) {
    toastStore.error('Gagal menyimpan libur: ' + (e.response?.data?.detail || e.message))
  } finally {
    modals.holiday.isSaving = false
  }
}

const deleteHoliday = async (h) => {
  if (!confirm(`Hapus libur pada ${formatFullDate(h.holiday_date)}?`)) return
  try {
    await api.delete(`/admin/service/holidays/${h.uuid}`)
    fetchHolidays()
    toastStore.success('Hari libur berhasil dihapus.')
  } catch (e) {
    toastStore.error('Gagal menghapus: ' + (e.response?.data?.detail || e.message))
  }
}

// ── Helpers ────────────────────────────────────────────────
const formatFullDate = (d) => {
  return new Date(d).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
}

const formatDateShort = (d) => {
  return new Date(d).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })
}

onMounted(fetchAll)
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .5; }
}

/* Modal Animation */
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.25s ease;
}
.modal-fade-enter-active .modal-card, .modal-fade-leave-active .modal-card {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .modal-card {
  transform: scale(0.95) translateY(12px);
  opacity: 0;
}
.modal-fade-leave-to .modal-card {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}
</style>
