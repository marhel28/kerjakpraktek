// stores/notificationStore.ts
import { defineStore } from 'pinia'
import type { RealtimeChannel } from '@supabase/supabase-js'

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
  // ─── Dependencies ────────────────────────────────────
  const supabase = useSupabaseClient()
  const user = useSupabaseUser()
  const { getSupabaseUserId, setSupabaseSession } = useAuth()
  
  // ─── State ───────────────────────────────────────────
  const notifications = ref<Notification[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isRealtimeConnected = ref(false)
  const realtimeChannel = ref<RealtimeChannel | null>(null)
  
  // Flag untuk mencegah double initialization
  let isInitialized = false

  // ─── Computed ────────────────────────────────────────
  const unreadNotifications = computed(() => {
    return notifications.value.filter(n => n.read_at === null)
  })

  const unreadCount = computed(() => {
    return unreadNotifications.value.length
  })

  const readNotifications = computed(() => {
    return notifications.value.filter(n => n.read_at !== null)
  })

  // ─── Helper: Get User ID ─────────────────────────────
  const getUserId = (): string => {
    const cookieId = getSupabaseUserId()
    if (cookieId) return cookieId
    
    if (user.value?.id) return user.value.id
    
    return ''
  }

  // ─── Actions ─────────────────────────────────────────
  
  const fetchNotifications = async () => {
    const userId = getUserId()
    
    if (!userId) {
      console.warn('❌ [Store] No user ID')
      return
    }

    console.log('📥 [Store] Fetching notifications for:', userId)
    isLoading.value = true
    error.value = null

    try {
      const { data, error: fetchError } = await supabase
        .from('notifications')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50)

      if (fetchError) throw fetchError

      console.log('✅ [Store] Fetched:', data?.length || 0, 'notifications')
      notifications.value = data || []
    } catch (e: any) {
      console.error('❌ [Store] Fetch error:', e)
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  const markAsRead = async (notificationId: number) => {
    const userId = getUserId()
    if (!userId) return

    try {
      const now = new Date().toISOString()
      
      const { error: updateError } = await supabase
        .from('notifications')
        .update({ read_at: now })
        .eq('id', notificationId)
        .eq('user_id', userId)

      if (updateError) throw updateError

      // Update local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        notifications.value[index] = {
          ...notifications.value[index],
          read_at: now
        }
      }
    } catch (e: any) {
      console.error('❌ [Store] Mark as read error:', e)
    }
  }

  const markAllAsRead = async () => {
    const userId = getUserId()
    if (!userId) return

    try {
      const now = new Date().toISOString()
      const unreadIds = unreadNotifications.value.map(n => n.id)

      if (unreadIds.length === 0) return

      const { error: updateError } = await supabase
        .from('notifications')
        .update({ read_at: now })
        .in('id', unreadIds)
        .eq('user_id', userId)

      if (updateError) throw updateError

      // Update local state
      notifications.value = notifications.value.map(n => ({
        ...n,
        read_at: n.read_at || now
      }))
    } catch (e: any) {
      console.error('❌ [Store] Mark all read error:', e)
    }
  }

  const deleteNotification = async (notificationId: number) => {
    const userId = getUserId()
    if (!userId) return

    try {
      const { error: deleteError } = await supabase
        .from('notifications')
        .delete()
        .eq('id', notificationId)
        .eq('user_id', userId)

      if (deleteError) throw deleteError

      // Remove from state
      notifications.value = notifications.value.filter(n => n.id !== notificationId)
    } catch (e: any) {
      console.error('❌ [Store] Delete error:', e)
    }
  }

  // ─── Realtime ────────────────────────────────────────

  const subscribeToRealtime = () => {
    const userId = getUserId()
    
    if (!userId) {
      console.warn('❌ [Store] Cannot subscribe: No user ID')
      return
    }

    // Cleanup existing channel
    if (realtimeChannel.value) {
      supabase.removeChannel(realtimeChannel.value)
    }

    console.log('📡 [Store] Subscribing to realtime for:', userId)

    const channel = supabase
      .channel(`notifications-store-${userId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'notifications',
          filter: `user_id=eq.${userId}`
        },
        (payload: any) => {
          console.log('📨 [Store REALTIME] New notification:', payload.new.title)
          notifications.value.unshift(payload.new as Notification)
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'notifications',
          filter: `user_id=eq.${userId}`
        },
        (payload: any) => {
          const index = notifications.value.findIndex(n => n.id === payload.new.id)
          if (index !== -1) {
            notifications.value[index] = payload.new as Notification
          }
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'DELETE',
          schema: 'public',
          table: 'notifications',
          filter: `user_id=eq.${userId}`
        },
        (payload: any) => {
          notifications.value = notifications.value.filter(
            n => n.id !== payload.old.id
          )
        }
      )
      .subscribe((status) => {
        console.log('📡 [Store] Realtime status:', status)
        isRealtimeConnected.value = status === 'SUBSCRIBED'
      })

    realtimeChannel.value = channel
  }

  const unsubscribeFromRealtime = () => {
    if (realtimeChannel.value) {
      supabase.removeChannel(realtimeChannel.value)
      realtimeChannel.value = null
      isRealtimeConnected.value = false
    }
  }

  // ─── Initialize ──────────────────────────────────────

  const init = async () => {
    // Cegah double init
    if (isInitialized) {
      console.log('⚠️ [Store] Already initialized, skipping')
      return
    }
    
    console.log('🚀 [Store] Initializing...')
    
    const userId = getUserId()
    
    if (!userId) {
      // Coba restore session
      await setSupabaseSession()
      await nextTick()
      
      const restoredId = getUserId()
      if (!restoredId) {
        console.log('⏳ [Store] Waiting for authentication...')
        return
      }
    }
    
    isInitialized = true
    await fetchNotifications()
    subscribeToRealtime()
    
    console.log('✅ [Store] Initialized successfully')
  }

  const cleanup = () => {
    console.log('💀 [Store] Cleanup')
    unsubscribeFromRealtime()
    notifications.value = []
    isInitialized = false
    isLoading.value = false
    error.value = null
  }

  // ─── Watchers ────────────────────────────────────────

  // Watch user login/logout
  watch(() => user.value?.id, (newId, oldId) => {
    if (oldId && !newId) {
      // User logged out
      cleanup()
    } else if (newId && newId !== oldId) {
      // User logged in or changed
      isInitialized = false
      init()
    }
  })

  return {
    // State
    notifications,
    isLoading,
    error,
    isRealtimeConnected,
    
    // Computed
    unreadNotifications,
    unreadCount,
    readNotifications,
    
    // Actions
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    
    // Realtime
    subscribeToRealtime,
    unsubscribeFromRealtime,
    
    // Lifecycle
    init,
    cleanup,
    
    // Helper
    getUserId,
  }
})