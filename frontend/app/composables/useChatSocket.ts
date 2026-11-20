import { ref, onUnmounted } from 'vue'
import { useCookie } from '#imports'
import { useRuntimeConfig } from '#imports'

// Singleton WebSocket composable untuk chat realtime
export const useChatSocket = () => {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const reconnecting = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 10
  const baseReconnectDelay = 1000 // 1 detik

  const handlers = new Map<string, Set<Function>>()
  const config = useRuntimeConfig()
  const token = useCookie('token')

  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  function getWsUrl(): string {
    const base = config.public.apiBase || 'http://localhost:8000'
    const wsBase = base.replace('http://', 'ws://').replace('https://', 'wss://')
    const userId = getSupabaseUserId()
    return `${wsBase}/ws/chat/${userId}?token=${token.value || ''}`
  }

  function getSupabaseUserId(): string {
    // Ambil dari cookie supabase_user yang di-set saat login
    const supabaseUserId = useCookie('supabase_user')
    return supabaseUserId.value || ''
  }

  function connect() {
    if (ws.value?.readyState === WebSocket.OPEN) return
    if (reconnecting.value) return

    const userId = getSupabaseUserId()
    if (!userId || !token.value) {
      console.warn('[WS Chat] Cannot connect: missing userId or token')
      return
    }

    reconnecting.value = true
    const url = getWsUrl()

    try {
      ws.value = new WebSocket(url)
    } catch (e) {
      console.error('[WS Chat] Failed to create WebSocket:', e)
      scheduleReconnect()
      return
    }

    ws.value.onopen = () => {
      connected.value = true
      reconnecting.value = false
      reconnectAttempts.value = 0
      console.log('[WS Chat] Connected to chat server')
    }

    ws.value.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        const type = message.type
        const data = message.data

        if (type && handlers.has(type)) {
          handlers.get(type)!.forEach((fn) => {
            try {
              fn(data)
            } catch (e) {
              console.error(`[WS Chat] Handler error for ${type}:`, e)
            }
          })
        }
      } catch (e) {
        console.error('[WS Chat] Failed to parse message:', e)
      }
    }

    ws.value.onclose = (event) => {
      connected.value = false
      if (!reconnecting.value) {
        console.log(`[WS Chat] Disconnected (code: ${event.code})`)
        scheduleReconnect()
      }
    }

    ws.value.onerror = (error) => {
      console.error('[WS Chat] WebSocket error:', error)
    }
  }

  function scheduleReconnect() {
    if (reconnecting.value) return
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      console.warn('[WS Chat] Max reconnect attempts reached')
      return
    }

    reconnecting.value = true
    reconnectAttempts.value++
    const delay = Math.min(
      baseReconnectDelay * Math.pow(1.5, reconnectAttempts.value - 1),
      30000
    )

    console.log(`[WS Chat] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.value})`)

    reconnectTimer = setTimeout(() => {
      reconnecting.value = false
      connect()
    }, delay)
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    reconnecting.value = false
    reconnectAttempts.value = 0
    if (ws.value) {
      ws.value.close(1000, 'Client disconnect')
      ws.value = null
    }
    connected.value = false
  }

  function on(type: string, handler: Function) {
    if (!handlers.has(type)) {
      handlers.set(type, new Set())
    }
    handlers.get(type)!.add(handler)
  }

  function off(type: string, handler: Function) {
    handlers.get(type)?.delete(handler)
  }

  function send(data: object) {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    } else {
      console.warn('[WS Chat] Cannot send: not connected')
    }
  }

  // Auto-reconnect when token changes (e.g., after login/refresh)
  let previousToken = token.value
  const checkTokenChange = () => {
    if (token.value && token.value !== previousToken) {
      previousToken = token.value
      if (connected.value) {
        disconnect()
      }
      setTimeout(connect, 100)
    }
  }

  // Watch for token changes
  const stopWatch = () => {}
  if (import.meta.client) {
    // Use setInterval as simple watch for token changes
    setInterval(checkTokenChange, 2000)
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    disconnect,
    on,
    off,
    send,
    connected,
    reconnecting,
  }
}