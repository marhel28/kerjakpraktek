import { ref, onMounted, onUnmounted } from 'vue'

const STORAGE_KEY = 'admin_sidebar_collapsed'

const isCollapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')
const isMobileOpen = ref(false)

export function useSidebar() {
  const toggleCollapse = () => {
    isCollapsed.value = !isCollapsed.value
    localStorage.setItem(STORAGE_KEY, String(isCollapsed.value))
  }

  const toggleMobile = () => {
    isMobileOpen.value = !isMobileOpen.value
  }

  const closeMobile = () => {
    isMobileOpen.value = false
  }

  const handleResize = () => {
    if (window.innerWidth >= 1024 && isMobileOpen.value) {
      isMobileOpen.value = false
    }
  }

  onMounted(() => {
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })

  return {
    isCollapsed,
    isMobileOpen,
    toggleCollapse,
    toggleMobile,
    closeMobile
  }
}
