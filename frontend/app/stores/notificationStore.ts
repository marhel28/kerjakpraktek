// stores/notificationStore.ts
import { defineStore } from 'pinia'
import { getBackendUserId } from '~/utils/session'

export interface Notification {
  id: number
  user_id: string
  title: string
  content: string
  read_at: string | null
  created_at: string
  type?: 'order' | 'system' | 'promo' | 'chat'
  metadata?: Record<string, any>
}

export const useNotificationStore = defineStore('notifications', () => {
  const toast = useToast()
  const socket = useNotificationSocket()

  // ─── State ───────────────────────────────────────────
  const notifications = ref<Notification[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isRealtimeConnected = ref(false)

  let isInitialized = false
  let handlersBound = false

  // ─── Computed ────────────────────────────────────────
  const unreadNotifications = computed(() =>
    notifications.value.filter(n => n.read_at === null)
  )
  const unreadCount = computed(() => unreadNotifications.value.length)
  const readNotifications = computed(() =>
    notifications.value.filter(n => n.read_at !== null)
  )

  // ─── Helper: UUID user backend ──────────────────────
  const getUserId = (): string => getBackendUserId()

  function upsertIncoming(item: Notification) {
    const index = notifications.value.findIndex(n => n.id === item.id)
    if (index !== -1) {
      notifications.value[index] = item
      return
    }
    notifications.value.unshift(item)
  }

  function showToast(item: Notification) {
    try {
      const targetUrl = item.metadata?.url || item.metadata?.action_url
      toast.add({
        title: item.title,
        description: item.content,
        icon: 'i-heroicons-bell',
        color: 'success',
        timeout: 5000,
        callback: targetUrl ? () => navigateTo(targetUrl) : undefined,
      })
    } catch (e) {
      console.error('Toast failed', e)
    }
  }

  // ─── Actions ─────────────────────────────────────────
  const fetchNotifications = async () => {
    isLoading.value = true
    error.value = null
    try {
      const data = await $fetch<Notification[]>('/api/notifications')
      notifications.value = data || []
    } catch (e: any) {
      console.error('[Store] Fetch error:', e)
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  const markAsRead = async (notificationId: number) => {
    try {
      const now = new Date().toISOString()
      await $fetch('/api/notifications', {
        method: 'PATCH',
        body: { id: notificationId },
      })
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        const current = notifications.value[index]!
        notifications.value[index] = {
          id: current.id,
          user_id: current.user_id,
          title: current.title,
          content: current.content,
          read_at: now,
          created_at: current.created_at,
          type: current.type,
          metadata: current.metadata,
        }
      }
    } catch (e: any) {
      console.error('[Store] Mark as read error:', e)
    }
  }

  const markAllAsRead = async () => {
    if (unreadNotifications.value.length === 0) return
    try {
      const now = new Date().toISOString()
      await $fetch('/api/notifications', { method: 'POST' })
      notifications.value = notifications.value.map(n => ({
        ...n,
        read_at: n.read_at || now,
      }))
    } catch (e: any) {
      console.error('[Store] Mark all read error:', e)
    }
  }

  const deleteNotification = async (notificationId: number) => {
    try {
      await $fetch('/api/notifications', {
        method: 'DELETE',
        query: { id: notificationId },
      })
      notifications.value = notifications.value.filter(n => n.id !== notificationId)
    } catch (e: any) {
      console.error('[Store] Delete error:', e)
    }
  }

  // ─── Realtime ────────────────────────────────────────
  const subscribeToRealtime = () => {
    if (!getUserId()) return

    if (!handlersBound) {
      socket.on('notification.created', (data: Notification) => {
        upsertIncoming(data)
        showToast(data)
      })
      socket.on('notification.updated', (data: Notification) => {
        upsertIncoming(data)
      })
      socket.on('notification.deleted', (data: { id: number }) => {
        notifications.value = notifications.value.filter(n => n.id !== data.id)
      })
      handlersBound = true
    }

    socket.connect()
  }

  const unsubscribeFromRealtime = () => {
    socket.disconnect()
    isRealtimeConnected.value = false
  }

  watch(socket.connected, (value) => {
    isRealtimeConnected.value = value
  })

  // ─── Initialize ──────────────────────────────────────
  const init = async () => {
    if (isInitialized) return
    if (!getUserId()) return
    isInitialized = true
    await fetchNotifications()
    subscribeToRealtime()
  }

  const cleanup = () => {
    unsubscribeFromRealtime()
    notifications.value = []
    isInitialized = false
    isLoading.value = false
    error.value = null
  }

  watch(getUserId, (newId, oldId) => {
    if (oldId && !newId) {
      cleanup()
    } else if (newId && newId !== oldId) {
      isInitialized = false
      init()
    }
  })

  return {
    notifications,
    isLoading,
    error,
    isRealtimeConnected,

    unreadNotifications,
    unreadCount,
    readNotifications,

    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,

    subscribeToRealtime,
    unsubscribeFromRealtime,

    init,
    cleanup,

    getUserId,
  }
})
