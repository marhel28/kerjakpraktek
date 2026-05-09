// composables/useChat.ts
import { useNotificationStore } from '~/stores/notificationStore'

export const useChat = () => {
  const store = useNotificationStore()
  
  // Auto-init store saat composable dipakai
  onMounted(async () => {
    await store.init()
  })
  
  return {
    // State
    notifications: computed(() => store.notifications),
    isLoading: computed(() => store.isLoading),
    error: computed(() => store.error),
    isRealtimeConnected: computed(() => store.isRealtimeConnected),
    
    // Computed
    unreadNotifications: computed(() => store.unreadNotifications),
    unreadCount: computed(() => store.unreadCount),
    readNotifications: computed(() => store.readNotifications),
    
    // Actions
    fetchNotifications: store.fetchNotifications,
    markAsRead: store.markAsRead,
    markAllAsRead: store.markAllAsRead,
    deleteNotification: store.deleteNotification,
    
    // Realtime
    subscribeToRealtime: store.subscribeToRealtime,
    unsubscribeFromRealtime: store.unsubscribeFromRealtime,
    
    // Lifecycle
    refresh: store.fetchNotifications,
    cleanup: store.cleanup,
  }
}