<template>
  <div class="relative group h-full flex items-center">
    <!-- Bell Button -->
    <NuxtLink
      :to="isAuthenticated ? '/dashboard/notifications' : '/login'"
      class="relative flex items-center gap-2 hover:bg-gray-50 rounded-lg transition-colors p-1.5 cursor-pointer"
      aria-label="Notifikasi"
    >
      <Icon
        name="lucide:bell"
        class="text-2xl lg:text-[26px] text-gray-700 group-hover:text-[#03AC0E] transition-colors"
      />
      <!-- Badge -->
      <span
        v-if="isAuthenticated && unreadCount > 0"
        class="absolute top-0 right-0 min-w-[18px] h-[18px] px-1 bg-[#EF144A] text-white text-[10px] font-black rounded-full flex items-center justify-center border-2 border-white shadow-sm pointer-events-none"
      >
        {{ unreadCount > 9 ? "9+" : unreadCount }}
      </span>
    </NuxtLink>

    <!-- Dropdown Panel -->
    <div
      class="absolute right-0 top-full opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform origin-top-right scale-95 group-hover:scale-100 w-[320px] z-[100]"
    >
      <div
        class="bg-white border border-gray-200 shadow-xl rounded-xl overflow-hidden flex flex-col font-sans mt-3"
      >
        <template v-if="isAuthenticated">
          <!-- Header -->
          <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between bg-white">
            <span class="text-[13px] font-black text-gray-900">Notifikasi</span>
            <button
              v-if="unreadCount > 0"
              @click="markAllAsRead"
              class="text-[11px] font-bold text-[#03AC0E] hover:underline"
            >
              Tandai dibaca semua
            </button>
          </div>

          <!-- Notification Items List -->
          <div class="max-h-[300px] overflow-y-auto divide-y divide-gray-100 custom-scrollbar">
            <div v-if="isLoading" class="p-8 text-center">
              <Icon name="lucide:loader-2" class="w-5 h-5 text-gray-300 animate-spin mx-auto mb-2" />
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Memuat...</span>
            </div>

            <div v-else-if="notifications.length === 0" class="p-8 text-center text-gray-400 text-xs">
              Belum ada notifikasi baru.
            </div>

            <template v-else>
              <div
                v-for="notif in notifications"
                :key="notif.id"
                @click="handleNotificationClick(notif)"
                class="px-4 py-3 hover:bg-gray-50 flex items-start gap-3 transition-colors cursor-pointer relative"
                :class="!notif.read_at ? 'bg-emerald-50/10' : ''"
              >
                <!-- Left green bar for unread -->
                <div v-if="!notif.read_at" class="absolute left-0 top-0 bottom-0 w-0.5 bg-[#03AC0E]"></div>

                <!-- Icon -->
                <div
                  class="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center border border-gray-100 text-gray-400 flex-shrink-0"
                >
                  <Icon :name="getNotificationIcon(notif.type)" class="w-4 h-4" />
                </div>

                <!-- Detail -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between gap-2 mb-0.5">
                    <span class="text-[11px] font-bold text-gray-900 truncate leading-tight">
                      {{ notif.title }}
                    </span>
                    <span class="text-[8px] font-bold text-gray-400 uppercase whitespace-nowrap">
                      {{ formatTime(notif.created_at) }}
                    </span>
                  </div>
                  <p
                    class="text-[10px] leading-relaxed line-clamp-2"
                    :class="!notif.read_at ? 'text-gray-900 font-bold' : 'text-gray-500 font-medium'"
                  >
                    {{ notif.content }}
                  </p>
                </div>
              </div>
            </template>
          </div>

          <!-- Footer -->
          <NuxtLink
            to="/dashboard/notifications"
            class="block w-full text-center py-2.5 text-[11px] font-bold text-[#03AC0E] hover:text-[#028c0b] hover:bg-gray-50 transition-colors border-t border-gray-100 uppercase tracking-wider"
          >
            Lihat Semua Notifikasi
          </NuxtLink>
        </template>

        <template v-else>
          <!-- Unauthenticated Menu -->
          <div class="p-6 flex flex-col items-center justify-center text-center bg-white">
            <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-4 border border-gray-100">
              <Icon name="lucide:lock" class="w-5 h-5 text-gray-400" />
            </div>
            <span class="text-[14px] font-bold text-gray-900 mb-1">Akses Terkunci</span>
            <p class="text-[12px] font-medium text-gray-500 mb-5 leading-relaxed">
              Silakan masuk untuk melihat update notifikasi pesanan dan akun Anda.
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

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useNotificationStore } from '~/stores/notificationStore'

const token = useCookie('token')
const notificationStore = useNotificationStore()

const isAuthenticated = computed(() => !!token.value)
const unreadCount = computed(() => notificationStore.unreadCount)
const isLoading = computed(() => notificationStore.isLoading)
const notifications = computed(() => notificationStore.notifications.slice(0, 5))

// onMounted init di-handle terpusat oleh plugin 01.realtime.client.ts

const getNotificationIcon = (type?: string): string => {
  switch (type) {
    case 'order':
      return 'lucide:shopping-bag'
    case 'promo':
      return 'lucide:badge-percent'
    case 'chat':
      return 'lucide:message-square'
    case 'system':
      return 'lucide:settings'
    default:
      return 'lucide:bell'
  }
}

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  
  if (minutes < 1) return 'Baru saja'
  if (minutes < 60) return `${minutes}m`
  if (hours < 24) return `${hours}j`
  return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', timeZoneName: 'short' })
}

const handleNotificationClick = (notif: any) => {
  if (!notif.read_at) {
    notificationStore.markAsRead(notif.id)
  }
  const targetUrl = notif.metadata?.url || notif.metadata?.action_url
  if (targetUrl) {
    navigateTo(targetUrl)
  }
}

const markAllAsRead = () => {
  notificationStore.markAllAsRead()
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: #94a3b8;
}
</style>
