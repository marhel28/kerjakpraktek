import { ref } from 'vue'
import { useCookie, useRuntimeConfig } from '#imports'
import { getBackendUserId } from '~/utils/session'

// Singleton: satu socket notifikasi untuk seluruh aplikasi.
const ws = ref<WebSocket | null>(null)
const connected = ref(false)
const reconnecting = ref(false)
let reconnectAttempts = 0
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let manualClose = false
const handlers = new Map<string, Set<(data: any) => void>>()

const MAX_ATTEMPTS = 10
const BASE_DELAY = 1000

function clearReconnectTimer() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
}

function getWsUrl(): string | null {
  const config = useRuntimeConfig()
  const token = useCookie<string | null>('token').value
  if (!token) return null

  const userId = getBackendUserId(token)
  if (!userId) return null

  const base = String(config.public.apiBase || 'http://localhost:8000').replace(/\/$/, '')
  const wsBase = base.replace(/^http:\/\//, 'ws://').replace(/^https:\/\//, 'wss://')
  return `${wsBase}/ws/notifications/${userId}?token=${encodeURIComponent(token)}`
}

function scheduleReconnect() {
  if (manualClose) return
  if (reconnectAttempts >= MAX_ATTEMPTS) {
    reconnecting.value = false
    return
  }
  clearReconnectTimer()
  reconnecting.value = true
  reconnectAttempts++
  const delay = Math.min(BASE_DELAY * Math.pow(1.5, reconnectAttempts - 1), 30000)
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    reconnecting.value = false
    connect()
  }, delay)
}

function connect() {
  if (typeof window === 'undefined') return
  if (ws.value?.readyState === WebSocket.OPEN) return
  if (ws.value?.readyState === WebSocket.CONNECTING) return

  const url = getWsUrl()
  if (!url) return

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

  socket.onopen = () => {
    connected.value = true
    reconnecting.value = false
    reconnectAttempts = 0
  }

  socket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data)
      const type = message?.type
      if (type && handlers.has(type)) {
        handlers.get(type)!.forEach((fn) => {
          try {
            fn(message.data)
          } catch (e) {
            console.error(`[WS Notif] Handler error for ${type}:`, e)
          }
        })
      }
    } catch (e) {
      console.error('[WS Notif] Failed to parse message:', e)
    }
  }

  socket.onclose = (event) => {
    connected.value = false
    reconnecting.value = false
    if (ws.value === socket) ws.value = null
    if (manualClose || event.code === 1000) return
    if (event.code === 1008) return // token ditolak — butuh login ulang
    scheduleReconnect()
  }

  socket.onerror = () => {
    try { socket.close() } catch { /* abaikan */ }
  }
}

function disconnect() {
  manualClose = true
  clearReconnectTimer()
  reconnecting.value = false
  reconnectAttempts = 0
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
  if (!handlers.has(type)) handlers.set(type, new Set())
  handlers.get(type)!.add(handler)
}

function off(type: string, handler: (data: any) => void) {
  handlers.get(type)?.delete(handler)
}

export const useNotificationSocket = () => ({
  connect,
  disconnect,
  on,
  off,
  connected,
  reconnecting,
})
