<script setup lang="ts">
import { useUserStore } from '~/stores/user'
import { computed } from 'vue'

const userStore = useUserStore()

// Ambil dari username, bukan role, agar inisial fotonya benar
const userAvatar = computed(() => {
  const name = userStore.profile?.username || 'Pengguna'
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=03AC0E&color=fff&bold=true`
})

// Dinamis styling untuk Badge Role (Corporate vs User)
const isCorporate = computed(() => {
  const role = userStore.profile?.role?.toLowerCase() || ''
  return role === 'corporate' || role === 'coorporate'
})

const roleBadgeClass = computed(() => {
  if (isCorporate.value) {
    // Style Premium B2B untuk Corporate (Warna Biru Profesional)
    return 'bg-blue-50 text-blue-700 border border-blue-200'
  }
  // Style Default B2C untuk User Biasa (Warna Hijau Marketplace)
  return 'bg-green-50 text-[#03AC0E] border border-green-200'
})

const roleLabel = computed(() => {
  if (isCorporate.value) return 'Mitra Corporate'
  return 'Akun Personal'
})
</script>

<template>
  <aside class="w-full lg:w-[280px] flex-shrink-0">
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden sticky top-24">
      
      <!-- ── Profile Section ─────────────────────────────────────── -->
      <div class="p-6 border-b border-gray-100 flex items-center gap-4">
        
        <!-- Skeleton Loading -->
        <template v-if="userStore.isLoading && !userStore.profile">
          <div class="w-14 h-14 rounded-full bg-gray-100 animate-pulse flex-shrink-0"></div>
          <div class="flex flex-col gap-2 w-full">
            <div class="w-24 h-4 bg-gray-100 animate-pulse rounded"></div>
            <div class="w-20 h-5 bg-gray-100 animate-pulse rounded-full"></div>
          </div>
        </template>
        
        <!-- User Info -->
        <template v-else>
          <NuxtImg 
            :src="userAvatar" 
            class="w-14 h-14 rounded-full border border-gray-100 object-cover shadow-sm flex-shrink-0" 
            alt="User Avatar"
          />
          <div class="flex flex-col overflow-hidden">
            <h2 class="font-extrabold text-gray-900 truncate capitalize text-lg leading-tight mb-1.5">
              {{ userStore.profile?.username || 'Pengguna' }}
            </h2>
            <div class="flex items-center">
              <span 
                class="px-2.5 py-1 text-[10px] font-bold rounded-full flex items-center gap-1.5"
                :class="roleBadgeClass"
              >
                <!-- Icon Corporate -->
                <svg v-if="isCorporate" class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M19 2H9c-1.103 0-2 .897-2 2v5.586l-4.707 4.707A1 1 0 0 0 2 15v6a1 1 0 0 0 1 1h18a1 1 0 0 0 1-1V4c0-1.103-.897-2-2-2zM9 4h10v16H11v-5H9v5H4v-4.586l3-3V4z"/><path d="M11 6h6v2h-6zm0 4h6v2h-6z"/></svg>
                <!-- Icon Personal -->
                <svg v-else class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z"/><path d="M12 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"/><path d="M12 14c-3.328 0-6 1.841-6 3.633V18h12v-.367C18 15.841 15.328 14 12 14z"/></svg>
                
                {{ roleLabel }}
              </span>
            </div>
          </div>
        </template>
      </div>

      <!-- ── Navigation Section ──────────────────────────────────── -->
      <nav class="flex flex-col p-3 space-y-1">
        
        <!-- Biodata Diri (exactActiveClass penting agar tidak menyala di sub-route) -->
        <NuxtLink 
          to="/dashboard" 
          exact-active-class="bg-[#E5F7E6] text-[#03AC0E] font-bold" 
          class="w-full px-4 py-3 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors duration-200"
        >
          Biodata Diri
        </NuxtLink>
        
        <NuxtLink 
          to="/dashboard/address" 
          active-class="bg-[#E5F7E6] text-[#03AC0E] font-bold" 
          class="w-full px-4 py-3 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors duration-200"
        >
          Daftar Alamat
        </NuxtLink>

        <NuxtLink 
          to="/dashboard/orders" 
          active-class="bg-[#E5F7E6] text-[#03AC0E] font-bold" 
          class="w-full px-4 py-3 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors duration-200"
        >
          Daftar Transaksi
        </NuxtLink>

        <!-- Tambahan Route Booking Jasa -->
        <NuxtLink 
          to="/dashboard/jasa" 
          active-class="bg-[#E5F7E6] text-[#03AC0E] font-bold" 
          class="w-full px-4 py-3 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors duration-200"
        >
          Booking Jasa & Servis
        </NuxtLink>
        
        <NuxtLink 
          v-if="isCorporate"
          to="/dashboard/invoices" 
          active-class="bg-blue-50 text-blue-700 font-bold" 
          class="w-full px-4 py-3 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors duration-200"
        >
          Faktur / Invoice B2B
        </NuxtLink>

        <NuxtLink 
          to="/dashboard/wishlist" 
          active-class="bg-[#E5F7E6] text-[#03AC0E] font-bold" 
          class="w-full px-4 py-3 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors duration-200"
        >
          Wishlist Barang
        </NuxtLink>

      </nav>
      
    </div>
  </aside>
</template>