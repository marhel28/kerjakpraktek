<template>
    <header
      class="sticky top-0 z-40 w-full bg-white/70 backdrop-blur-md border-b border-gray-200 transition-all duration-300">
      <div class="flex items-center justify-between h-16 px-4 md:px-6">
  
        <!-- Left: toggle + title -->
        <div class="flex items-center space-x-4">
          <button
            @click="$emit('toggle-sidebar')"
            class="p-2 -ml-2 text-gray-500 rounded-xl hover:bg-gray-100 hover:text-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500/50 active:scale-95"
            title="Toggle sidebar (Alt + S)"
          >
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 class="hidden sm:block text-lg font-semibold text-gray-800 tracking-tight">Dashboard</h1>
        </div>
  
        <!-- Center: search -->
        <div class="flex-1 max-w-md px-6 hidden md:block">
          <div class="relative group">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3">
              <svg
                class="w-4 h-4 text-gray-400 group-focus-within:text-indigo-500 transition-colors"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </span>
            <input
              type="text"
              placeholder="Search data, transactions, or stock..."
              class="w-full py-2 pl-10 pr-4 text-sm text-gray-800 bg-gray-100/80 border-transparent rounded-full focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 transition-all duration-200 shadow-sm"
            />
          </div>
        </div>
  
        <!-- Right: actions -->
        <div class="flex items-center space-x-1 md:space-x-2 shrink-0">

          <!-- ── Preview Website Button ──────────────────────────────── -->
          <a
            :href="previewStore.previewUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 hover:text-indigo-700 rounded-xl transition-all active:scale-95 border border-indigo-100/80 shadow-sm"
            title="Buka Preview Website"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            <span class="hidden sm:inline">Preview Web</span>
          </a>

          <!-- ── Notif Pesan ─────────────────────────────────────────── -->
          <RouterLink
            to="/pesan"
            class="relative p-2 text-gray-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors active:scale-95"
            title="Pesan"
          >
            <!-- Icon chat -->
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
  
            <!-- Badge unread -->
            <Transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="scale-0 opacity-0"
              enter-to-class="scale-100 opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="scale-100 opacity-100"
              leave-to-class="scale-0 opacity-0"
            >
              <span
                v-if="messageStore.totalUnreadBadge > 0"
                class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-rose-500 text-white text-[10px] font-black rounded-full flex items-center justify-center border-2 border-white leading-none pointer-events-none"
              >
                {{ messageStore.totalUnreadBadge > 99 ? '99+' : messageStore.totalUnreadBadge }}
              </span>
            </Transition>
          </RouterLink>
  
          <!-- ── Notif Bell (Dynamic Dropdown) ───────────────────────── -->
          <div class="relative" id="notification-dropdown-container">
            <button
              @click="toggleNotifications"
              class="relative p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-all duration-200 active:scale-95"
              title="Notifikasi"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <!-- Badge unread -->
              <Transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="scale-0 opacity-0"
                enter-to-class="scale-100 opacity-100"
                leave-active-class="transition duration-150 ease-in"
                leave-from-class="scale-100 opacity-100"
                leave-to-class="scale-0 opacity-0"
              >
                <span
                  v-if="notificationStore.unreadCount > 0"
                  class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-red-500 text-white text-[10px] font-black rounded-full flex items-center justify-center border-2 border-white leading-none pointer-events-none"
                >
                  {{ notificationStore.unreadCount > 99 ? '99+' : notificationStore.unreadCount }}
                </span>
              </Transition>
            </button>

            <!-- Dropdown Menu -->
            <Transition
              enter-active-class="transition ease-out duration-200"
              enter-from-class="transform opacity-0 scale-95 -translate-y-2"
              enter-to-class="transform opacity-100 scale-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <div
                v-show="isNotificationsOpen"
                class="absolute right-0 mt-3 w-80 md:w-96 bg-white rounded-2xl shadow-xl border border-gray-100 z-[99] origin-top-right flex flex-col max-h-[480px]"
              >
                <!-- Dropdown Header -->
                <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <span class="text-sm font-bold text-gray-800">Notifikasi</span>
                    <span 
                      v-if="notificationStore.unreadCount > 0" 
                      class="px-2 py-0.5 bg-indigo-50 text-indigo-600 text-xs font-semibold rounded-full"
                    >
                      {{ notificationStore.unreadCount }} Baru
                    </span>
                  </div>
                  <button 
                    v-if="notificationStore.unreadCount > 0"
                    @click="notificationStore.markAllAsRead"
                    class="text-xs font-medium text-slate-500 hover:text-indigo-600 hover:underline transition-colors focus:outline-none"
                  >
                    Tandai semua dibaca
                  </button>
                </div>

                <!-- Dropdown Items -->
                <div class="overflow-y-auto flex-1 divide-y divide-gray-50 scrollbar-thin">
                  <!-- Empty State -->
                  <div 
                    v-if="notificationStore.notifications.length === 0" 
                    class="flex flex-col items-center justify-center py-10 px-4 text-center"
                  >
                    <div class="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center mb-3">
                      <svg class="w-6 h-6 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                    </div>
                    <p class="text-xs font-semibold text-slate-700">Tidak ada notifikasi</p>
                    <p class="text-[11px] text-slate-400 mt-0.5">Semua info pesanan dan transaksi akan muncul di sini.</p>
                  </div>

                  <!-- Notification List -->
                  <div 
                    v-for="item in notificationStore.notifications" 
                    :key="item.id"
                    @click="handleNotifClick(item)"
                    class="p-4 flex gap-3 cursor-pointer transition-all relative select-none border-l-4"
                    :class="item.read_at === null ? 'bg-indigo-50/50 hover:bg-indigo-50/80 border-indigo-500' : 'bg-white hover:bg-slate-50 border-transparent'"
                  >
                    <!-- Icon based on type or fallback -->
                    <div class="shrink-0">
                      <div 
                        class="w-8 h-8 rounded-full flex items-center justify-center"
                        :class="{
                          'bg-indigo-100 text-indigo-600': item.type === 'order' || !item.type,
                          'bg-emerald-100 text-emerald-600': item.type === 'system',
                          'bg-amber-100 text-amber-600': item.type === 'promo'
                        }"
                      >
                        <!-- Order/Default Icon -->
                        <svg v-if="item.type === 'order' || !item.type" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                        </svg>
                        <!-- Promo Icon -->
                        <svg v-else-if="item.type === 'promo'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5a2 2 0 10-2 2h2zm0 0h4l-1 5h-3m0-5H8l1 5h3m-6 5h12v-5H6v5z" />
                        </svg>
                        <!-- System Icon -->
                        <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                    </div>

                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-start justify-between gap-1">
                        <p 
                          class="text-xs font-bold text-gray-800 line-clamp-1"
                          :class="{'text-indigo-950 font-black': item.read_at === null}"
                        >
                          {{ item.title }}
                        </p>
                        <span class="text-[10px] text-gray-400 shrink-0 whitespace-nowrap pt-0.5">
                          {{ formatTimeAgo(item.created_at) }}
                        </span>
                      </div>
                      <p 
                        class="text-[11px] text-gray-500 mt-1 leading-relaxed line-clamp-2"
                        :class="{'text-gray-700': item.read_at === null}"
                      >
                        {{ item.content }}
                      </p>
                    </div>

                    <!-- Unread dot indicator -->
                    <div v-if="item.read_at === null" class="absolute right-4 bottom-4 w-1.5 h-1.5 bg-indigo-600 rounded-full"></div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <!-- ── Profile ─────────────────────────────────────────────── -->
          <div class="relative">
            <button
              @click="isProfileOpen = !isProfileOpen"
              @blur="closeProfile"
              class="flex items-center space-x-2 focus:outline-none active:scale-95 transition-transform ml-1"
            >
              <img
                class="w-8 h-8 rounded-full object-cover ring-2 ring-transparent hover:ring-indigo-100 transition-all shadow-sm"
                src="https://ui-avatars.com/api/?name=Admin&background=4F46E5&color=fff"
                alt="Admin Profile"
              />
            </button>
  
            <Transition
              enter-active-class="transition ease-out duration-200"
              enter-from-class="transform opacity-0 scale-95 -translate-y-2"
              enter-to-class="transform opacity-100 scale-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <div
                v-show="isProfileOpen"
                class="absolute right-0 mt-3 w-48 bg-white rounded-2xl shadow-xl border border-gray-100 py-1.5 z-50 origin-top-right"
              >
                <div class="px-4 py-2 border-b border-gray-100 mb-1">
                  <p class="text-sm font-semibold text-gray-800">Admin User</p>
                  <p class="text-xs text-gray-500 truncate">admin@pasarcctv.com</p>
                </div>
                <a href="#"
                  class="block px-4 py-2 text-sm text-gray-600 hover:bg-indigo-50 hover:text-indigo-700 transition-colors">
                  My Profile
                </a>
                <a href="/settings/couriers"
                  class="block px-4 py-2 text-sm text-gray-600 hover:bg-indigo-50 hover:text-indigo-700 transition-colors">
                  Settings
                </a>
                <RouterLink to="/settings/preview"
                  class="block px-4 py-2 text-sm text-gray-600 hover:bg-indigo-50 hover:text-indigo-700 transition-colors">
                  Pengaturan Preview
                </RouterLink>
                <div class="border-t border-gray-100 my-1"></div>
                <button
                  @click="handleLogout"
                  class="w-full text-left block px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                >
                  Logout
                </button>
              </div>
            </Transition>
          </div>
  
        </div>
      </div>
    </header>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import { useMessageStore } from '@/stores/messageStore'
  import { useNotificationStore } from '@/stores/notificationStore'
  import { useToastStore } from '@/stores/toast'
  import { usePreviewStore } from '@/stores/previewStore'

  defineEmits(['toggle-sidebar'])

  const router = useRouter()
  const isProfileOpen = ref(false)
  const isNotificationsOpen = ref(false)
  const auth = useAuthStore()
  const messageStore = useMessageStore()
  const notificationStore = useNotificationStore()
  const toastStore = useToastStore()
  const previewStore = usePreviewStore()
  
  const closeProfile = () => {
    setTimeout(() => { isProfileOpen.value = false }, 150)
  }
  
  const handleLogout = async () => {
    await auth.logout()
  }

  const toggleNotifications = () => {
    isNotificationsOpen.value = !isNotificationsOpen.value
    if (isNotificationsOpen.value) {
      isProfileOpen.value = false
    }
  }

  const handleNotifClick = async (item) => {
    // 1. Mark as read in store/backend
    if (item.read_at === null) {
      await notificationStore.markAsRead(item.id)
    }
    
    // 2. Close dropdown
    isNotificationsOpen.value = false
    
    // 3. Extract action URL safely (supports string or object metadata)
    let actionUrl = ''
    if (item.metadata) {
      try {
        const meta = typeof item.metadata === 'string' ? JSON.parse(item.metadata) : item.metadata
        actionUrl = meta.action_url || meta.url || (meta.order_id ? `/transaksi/${meta.order_id}` : '')
      } catch (e) {
        console.error('Gagal memproses metadata notifikasi:', e)
      }
    }
    
    // Fallback to direct action_url field
    if (!actionUrl && item.action_url) {
      actionUrl = item.action_url
    }
    
    // 4. Navigate using Vue Router
    if (actionUrl) {
      if (!actionUrl.startsWith('/')) {
        actionUrl = '/' + actionUrl
      }
      console.log('Navigating to:', actionUrl)
      router.push(actionUrl)
    } else {
      console.warn('Tidak ada url navigasi untuk notifikasi ini:', item)
    }
  }

  // Click outside handler
  const handleClickOutside = (e) => {
    const notifContainer = document.getElementById('notification-dropdown-container')
    if (notifContainer && !notifContainer.contains(e.target)) {
      isNotificationsOpen.value = false
    }
  }

  // Helper time ago
  function formatTimeAgo(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Baru saja'
    if (diffMins < 60) return `${diffMins}m lalu`
    if (diffHours < 24) return `${diffHours}j lalu`
    return `${diffDays}d lalu`
  }

  // Watch for new notifications
  watch(() => notificationStore.unreadCount, (newCount, oldCount) => {
    if (newCount > oldCount && oldCount !== undefined) {
      const latestNotif = notificationStore.notifications[0]
      if (latestNotif) {
        toastStore.info(latestNotif.title || 'Ada notifikasi baru')
      }
    }
  })

  onMounted(() => {
    window.addEventListener('click', handleClickOutside)
    notificationStore.startPolling(15000) // Poll every 15 seconds
  })

  onUnmounted(() => {
    window.removeEventListener('click', handleClickOutside)
    notificationStore.stopPolling()
  })
  </script>
