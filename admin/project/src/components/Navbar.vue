<template>
    <header
      class="sticky top-0  w-full bg-white/70 backdrop-blur-md border-b border-gray-200 transition-all duration-300">
      <div class="flex items-center justify-between h-16 px-4 md:px-6">
  
        <!-- Left: toggle + title -->
        <div class="flex items-center space-x-4">
          <button
            @click="$emit('toggle-sidebar')"
            class="p-2 -ml-2 text-gray-500 rounded-xl hover:bg-gray-100 hover:text-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500/50 active:scale-95"
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
  
          <!-- ── Notif Bell (existing) ───────────────────────────────── -->
          <button
            class="relative p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors active:scale-95"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
          </button>
  
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
                <a href="#"
                  class="block px-4 py-2 text-sm text-gray-600 hover:bg-indigo-50 hover:text-indigo-700 transition-colors">
                  Settings
                </a>
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
  import { ref } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import { useMessageStore } from '@/stores/messageStore'
  
  defineEmits(['toggle-sidebar'])
  
  const isProfileOpen  = ref(false)
  const auth           = useAuthStore()
  const messageStore   = useMessageStore()
  
  const closeProfile = () => {
    setTimeout(() => { isProfileOpen.value = false }, 150)
  }
  
  const handleLogout = async () => {
    await auth.logout()
  }
  </script>