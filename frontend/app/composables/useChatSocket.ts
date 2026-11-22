import { ref } from 'vue'
import { useCookie, useRuntimeConfig } from '#imports'
import { getBackendUserId } from '~/utils/session'

// ── Module-level singleton state ─────────────────────────────────────
// Semua pemanggil useChatSocket() berbagi satu koneksi + handler yang sama.
// Ini mencegah socket ganda saat store + komponen memanggil composable.
const ws = ref<WebSocket | null>(null)
const connected = ref(false)
const reconnecting = ref(false)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 10
const baseReconnectDelay = 1000 // 1 detik
const handlers = new Map<string, Set<(data: any) => void>>()

let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let manualClose = false
let listenersBound = false

function clearReconnectTimer() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
}

function getWsUrl(): string | null {
  const config = useRuntimeConfig()
  const token = useCookie<string | null>('token')
  const tokenValue = token.value
  const userId = getBackendUserId(tokenValue)
  if (!userId || !tokenValue) {
    return null
  }
  const base = String(config.public.apiBase || 'http://localhost:8000').replace(/\/$/, '')
  const wsBase = base.replace(/^http:\/\//, 'ws://').replace(/^https:\/\//, 'wss://')
  return `${wsBase}/ws/chat/${userId}?token=${encodeURIComponent(tokenValue)}`
}

// Singleton WebSocket composable untuk chat realtime
export const useChatSocket = () => {
  function connect() {
    if (typeof window === 'undefined') return
    if (ws.value?.readyState === WebSocket.OPEN) return
    if (ws.value?.readyState === WebSocket.CONNECTING) return

    const url = getWsUrl()
    if (!url) {
      return
    }

    manualClose = false
    clearReconnectTimer()

    let socket: WebSocket
    try {
      socket = new WebSocket(url)
    } catch {
      scheduleReconnect()
      return
    }
    ws.value = socket
    reconnecting.value = true

    socket.onopen = () => {
      connected.value = true
      reconnecting.value = false
      reconnectAttempts.value = 0
    }

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        const type = message?.type
        const data = message?.data
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

    socket.onclose = (event) => {
      connected.value = false
      reconnecting.value = false
      if (ws.value === socket) ws.value = null
      // 1000 = normal close (logout), 1008 = auth gagal → jangan retry buta
      if (manualClose || event.code === 1000) return
      if (event.code === 1008) {
        console.warn('[WS Chat] Auth rejected (1008), stop reconnect. Relogin dibutuhkan.')
        return
      }
      scheduleReconnect()
    }

    socket.onerror = () => {
      // onclose akan menyusul dan memicu reconnect; cukup tutup socket rusak
      try { socket.close() } catch { /* abaikan */ }
    }
  }

  function scheduleReconnect() {
    if (manualClose) return
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      console.warn('[WS Chat] Max reconnect attempts reached')
      reconnecting.value = false
      return
    }
    clearReconnectTimer()
    reconnecting.value = true
    reconnectAttempts.value++
    const delay = Math.min(
      baseReconnectDelay * Math.pow(1.5, reconnectAttempts.value - 1),
      30000,
    )
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      reconnecting.value = false
      connect()
    }, delay)
  }

  function disconnect() {
    manualClose = true
    clearReconnectTimer()
    reconnecting.value = false
    reconnectAttempts.value = 0
    if (ws.value) {
      try {
        if (ws.value.readyState === WebSocket.OPEN) {
          ws.value.close(1000, 'Client disconnect')
        }
      } catch { /* abaikan */ }
      ws.value = null
    }
    connected.value = false
  }

  function on(type: string, handler: (data: any) => void) {
    if (!handlers.has(type)) {
      handlers.set(type, new Set())
    }
    handlers.get(type)!.add(handler)
  }

  function off(type: string, handler: (data: any) => void) {
    handlers.get(type)?.delete(handler)
  }

  function send(data: object) {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    }
  }

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

// Dipakai store untuk mencegah double-binding listener saat initAfterLogin
// dipanggil berulang (plugin + FloatingChat + login).
export function __isWsListenerBound() {
  return listenersBound
}
export function __markWsListenerBound() {
  listenersBound = true
}
export function __resetWsListenerBound() {
  listenersBound = false
  handlers.clear()
}
