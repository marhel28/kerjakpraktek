// composables/useChatUser.ts
import { useChatUserStore } from '~/stores/chatUserStore'

export const useChatUser = () => {
  const store = useChatUserStore()

  onMounted(async () => {
    await store.init()
  })

  return {
    // State
    messages: computed(() => store.messages),
    currentUserId: computed(() => store.currentUserId),
    currentUserRole: computed(() => store.currentUserRole),
    isLoading: computed(() => store.isLoading),
    isSending: computed(() => store.isSending),
    error: computed(() => store.error),
    isRealtimeConnected: computed(() => store.isRealtimeConnected),

    // Computed khusus admin
    chatUsers: computed(() => store.getChatUsers),
    getMessagesForUser: store.getMessagesForUser,

    // Actions
    sendMessage: store.sendMessage,
    markMessageAsRead: store.markMessageAsRead,
    markAllAsRead: store.markAllAsRead,
    fetchMessages: store.fetchMessages,
    subscribeToRealtime: store.subscribeToRealtime,
    unsubscribeFromRealtime: store.unsubscribeFromRealtime,

    // Lifecycle
    refresh: store.fetchMessages,
    cleanup: store.cleanup,
  }
}