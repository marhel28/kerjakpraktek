<template>
  <div class="relative group h-full flex items-center">

    <NuxtLink
      :to="isAuthenticated ? '/dashboard' : '/login'"
      class="flex items-center gap-2 hover:bg-gray-50 rounded-lg transition-colors p-1.5 cursor-pointer"
      aria-label="Menu Akun"
    >
      <Icon name="lucide:user" class="text-2xl lg:text-[26px] text-gray-700 group-hover:text-[#03AC0E] transition-colors" />

      <div class="hidden lg:flex flex-col leading-none ml-1">
        <span class="text-[11px] text-gray-500 font-medium mb-0.5">
          {{ isAuthenticated ? 'Welcome' : 'Sign In' }}
        </span>
        <span class="text-[13px] font-bold text-gray-900 tracking-tight line-clamp-1 group-hover:text-[#03AC0E] transition-colors">
          {{ isAuthenticated ? userName : 'Account' }}
        </span>
      </div>
    </NuxtLink>

    <div class="absolute right-0 top-full opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform origin-top-right scale-95 group-hover:scale-100 w-[280px] z-[100]">
      <div class="bg-white border border-gray-200 shadow-xl rounded-xl overflow-hidden flex flex-col font-sans mt-3">

        <template v-if="isAuthenticated">
          <div class="p-4 border-b border-gray-100 flex items-center gap-3 bg-white">
            <div class="w-10 h-10 bg-[#D6FFDE] rounded-full flex items-center justify-center shrink-0 border border-[#03AC0E]/20">
              <span class="text-[#03AC0E] font-bold text-lg">{{ userInitials }}</span>
            </div>
            <div class="flex flex-col">
              <span class="text-[14px] font-bold text-gray-900 leading-tight line-clamp-1">{{ userName }}</span>
              <span class="text-[10px] font-bold text-[#03AC0E] bg-[#D6FFDE]/50 px-2 py-0.5 rounded uppercase tracking-wider mt-1 w-fit">Premium Member</span>
            </div>
          </div>

          <nav class="flex flex-col py-2">
            <NuxtLink 
              to="/dashboard/notifications" 
              class="px-5 py-3 hover:bg-gray-50 flex items-center justify-between group/item transition-colors"
            >
              <div class="flex items-center gap-3">
                <div class="relative">
                  <Icon name="lucide:bell" class="w-[18px] h-[18px] text-gray-400 group-hover/item:text-[#03AC0E] transition-colors" />
                  <span 
                    v-if="unreadCount > 0"
                    class="absolute -top-1 -right-1 w-2 h-2 bg-[#EF144A] rounded-full animate-ping"
                  />
                </div>
                <span class="text-[13px] font-bold text-gray-700 group-hover/item:text-[#03AC0E] transition-colors">Notifikasi</span>
              </div>
              <transition name="badge-pop">
                <span 
                  v-if="unreadCount > 0"
                  class="bg-[#EF144A] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center shadow-sm"
                >
                  {{ unreadCount > 99 ? '99+' : unreadCount }}
                </span>
              </transition>
            </NuxtLink>

            <NuxtLink to="/dashboard/orders" class="px-5 py-3 hover:bg-gray-50 flex items-center justify-between group/item transition-colors">
              <div class="flex items-center gap-3">
                <Icon name="lucide:package" class="w-[18px] h-[18px] text-gray-400 group-hover/item:text-[#03AC0E] transition-colors" />
                <span class="text-[13px] font-bold text-gray-700 group-hover/item:text-[#03AC0E] transition-colors">Pesanan Saya</span>
              </div>
            </NuxtLink>

            <NuxtLink to="/wishlist" class="px-5 py-3 hover:bg-gray-50 flex items-center justify-between group/item transition-colors">
              <div class="flex items-center gap-3">
                <Icon name="lucide:heart" class="w-[18px] h-[18px] text-gray-400 group-hover/item:text-[#03AC0E] transition-colors" />
                <span class="text-[13px] font-bold text-gray-700 group-hover/item:text-[#03AC0E] transition-colors">Wishlist Barang</span>
              </div>
              <transition name="badge-pop">
                <span 
                  v-if="wishlistCount > 0"
                  class="bg-[#03AC0E] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center shadow-sm"
                >
                  {{ wishlistCount }}
                </span>
              </transition>
            </NuxtLink>
          </nav>

          <div class="p-3 border-t border-gray-100 bg-gray-50/50">
            <button @click="handleLogout" class="w-full flex items-center justify-center gap-2 py-2.5 bg-white border border-gray-300 hover:border-[#EF144A] hover:bg-[#EF144A]/5 text-gray-700 hover:text-[#EF144A] transition-all duration-300 rounded-lg text-[13px] font-bold group/btn">
              <Icon name="lucide:log-out" class="w-4 h-4 group-hover/btn:-translate-x-1 transition-transform" />
              Keluar Akun
            </button>
          </div>
        </template>

        <template v-else>
          <div class="p-6 flex flex-col items-center justify-center text-center bg-white">
            <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-4 border border-gray-100">
              <Icon name="lucide:lock" class="w-5 h-5 text-gray-400" />
            </div>
            <span class="text-[14px] font-bold text-gray-900 mb-1">Akses Terkunci</span>
            <p class="text-[12px] font-medium text-gray-500 mb-5 leading-relaxed">
              Silakan masuk untuk melihat pesanan, notifikasi, dan fitur akun lainnya.
            </p>
            <NuxtLink
              to="/login"
              class="w-full bg-[#03AC0E] text-white py-2.5 flex items-center justify-center gap-2 text-[13px] font-bold rounded-lg hover:bg-[#028c0b] transition-colors shadow-sm"
            >
              Masuk / Daftar
              <Icon name="lucide:arrow-right" class="w-4 h-4" />
            </NuxtLink>
          </div>
        </template>

      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useNotificationStore } from '~/stores/notificationStore'

import { useWishlistStore } from '~/stores/wishlist'

const token = useCookie('token')
const userDataCookie = useCookie('user_data')

const notificationStore = useNotificationStore()
const unreadCount = computed(() => notificationStore.unreadCount)

const wishlistStore = useWishlistStore()
const wishlistCount = computed(() => wishlistStore.count)

onMounted(() => {
  if (token.value) {
    wishlistStore.fetchWishlist()
  }
})

const isAuthenticated = computed(() => !!token.value)

const userName = computed(() => {
  if (!isAuthenticated.value || !userDataCookie.value) return "Account"
  if (userDataCookie.value.name) return userDataCookie.value.name
  if (userDataCookie.value.email) {
    const emailName = userDataCookie.value.email.split('@')[0]
    return emailName.charAt(0).toUpperCase() + emailName.slice(1)
  }
  return "Member"
})

const userInitials = computed(() => {
  const name = userName.value
  if (name === "Account" || name === "Member") return "U"
  const names = name.split(" ")
  if (names.length >= 2) return (names[0][0] + names[1][0]).toUpperCase()
  return name.substring(0, 2).toUpperCase()
})

const handleLogout = async () => {
  notificationStore.cleanup()
  token.value = null
  userDataCookie.value = null
  
  useCookie('sb_access_token').value = null
  useCookie('sb_refresh_token').value = null
  useCookie('supabase_user').value = null

  navigateTo('/login')
}
</script>

<style scoped>
.badge-pop-enter-active { animation: badge-pop-in 0.3s ease-out; }
.badge-pop-leave-active { animation: badge-pop-in 0.3s ease-in reverse; }

@keyframes badge-pop-in {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); opacity: 1; }
}
.animate-ping { animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite; }

@keyframes ping {
  75%, 100% { transform: scale(2); opacity: 0; }
}
</style>