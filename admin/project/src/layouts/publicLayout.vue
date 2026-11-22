<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden font-sans text-gray-800 relative">

    <!-- Mobile Drawer Backdrop -->
    <Transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isMobileOpen"
        @click="closeMobile"
        class="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-xs lg:hidden"
      ></div>
    </Transition>

    <!-- Sidebar -->
    <Sidebar
      :is-collapsed="isCollapsed"
      :is-mobile-open="isMobileOpen"
      @toggle-collapse="toggleCollapse"
      @close-mobile="closeMobile"
    />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden transition-all duration-300">
      <Navbar :sidebar-open="isMobileOpen" @toggle-sidebar="handleToggleSidebar" />

      <main class="flex-1 relative z-0 overflow-y-auto p-4 sm:p-6 md:p-8">
        <router-view />
      </main>
    </div>

  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import Navbar from '@/components/Navbar.vue'
import { useMessageStore } from '@/stores/messageStore'
import { useSidebar } from '@/composables/useSidebar'

const { isCollapsed, isMobileOpen, toggleCollapse, toggleMobile, closeMobile } = useSidebar()
const messageStore = useMessageStore()

const handleToggleSidebar = () => {
  if (typeof window !== 'undefined' && window.innerWidth < 1024) {
    toggleMobile()
  } else {
    toggleCollapse()
  }
}

const handleKeydown = (e) => {
  if (e.key === 'Escape' && isMobileOpen.value) closeMobile()
}

onMounted(() => {
  messageStore.startInboxPolling()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  messageStore.destroy()
  window.removeEventListener('keydown', handleKeydown)
})
</script>
