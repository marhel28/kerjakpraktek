<template>
    <div class="flex h-screen bg-gray-50 overflow-hidden font-sans text-gray-800">
  
      <Sidebar :is-open="isSidebarOpen" @toggle="isSidebarOpen = !isSidebarOpen" />
  
      <div class="flex-1 flex flex-col w-0 overflow-hidden transition-all duration-300">
  
        <Navbar @toggle-sidebar="isSidebarOpen = !isSidebarOpen" :unread-count="messageStore.totalUnreadBadge" />
  
        <main class="flex-1 relative z-0 overflow-y-auto p-6 md:p-8">
          <router-view />
        </main>
  
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  import Sidebar from '@/components/Sidebar.vue'
  import Navbar from '@/components/Navbar.vue'
  import { useMessageStore } from '@/stores/messageStore'
  
  const isSidebarOpen  = ref(true)
  const messageStore   = useMessageStore()
  
  onMounted(() => {
    // Mulai polling inbox untuk badge unread di navbar
    messageStore.startInboxPolling()
  })
  
  onUnmounted(() => {
    // Bersihkan semua timer saat layout di-unmount (logout / route change besar)
    messageStore.destroy()
  })
  </script>