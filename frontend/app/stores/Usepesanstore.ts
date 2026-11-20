/**
 * stores/UsePesanStore.ts
 * ========================
 * Pinia store untuk sistem pesan customer ↔ admin.
 *
 * Flow "Chat dari Produk" (mirip Tokopedia):
 * 1. User klik "Chat" di halaman produk
 * 2. store.setPendingContext(ctx) — simpan info produk ke state
 * 3. router.push('/') — balik ke home
 * 4. FloatingChat di layout.vue watch store.pendingContext
 * → berubah = auto-open chat + tampil banner produk
 * 5. User kirim pesan → ctx di-embed ke body, lalu clearPendingContext()
 *
 * Realtime via WebSocket (ganti polling):
 * - initAfterLogin() -> connect() WebSocket
 * - WebSocket event 'new_message' -> _mergeMessages + update unreadCount
 * - WebSocket event 'message_read' -> _markLocalRead
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useChatSocket, __isWsListenerBound, __markWsListenerBound, __resetWsListenerBound } from '~/composables/useChatSocket'

// ── Types ──────────────────────────────────────────────────────────
export interface MessageImage {
  uuid: string
  image_url: string
  uploaded_at: string
}

export interface ProductContext {
  uuid: string
  title: string
  url: string
  image?: string
  price: number
  brand?: string
}

export interface ChatMessage {
  uuid: string
  conversation_id: string
  sender_role: 'user' | 'admin'
  sender_id: string
  body: string | null
  status: 'sent' | 'read'
  sent_at: string
  images: MessageImage[]
  /**
   * UI-only: tidak dari server. Di-inject saat sendMessage()
   * agar product card tampil di bubble pesan user.
   */
  _productContext?: ProductContext
}

export const usePesanStore = defineStore('pesan', () => {
  // ── State ────────────────────────────────────────────────────────
  const messages = ref<ChatMessage[]>([])
  const unreadCount = ref(0)
  const lastSentAt = ref<string | null>(null)
  const oldestSentAt = ref<string | null>(null)
  const hasMoreHistory = ref(true)
  const isLoadingHistory = ref(false)
  const isLoadingInitial = ref(false)
  const isSending = ref(false)

  /**
   * pendingContext — disimpan di store supaya persist lintas navigasi.
   * Set dari halaman produk, dibaca FloatingChat di layout.
   */
  const pendingContext = ref<ProductContext | null>(null)

  let isPopupOpen = false

  // ── WebSocket ────────────────────────────────────────────────────
  const { connect, disconnect, on } = useChatSocket()
  let wsInitialized = false

  // ── Computed ─────────────────────────────────────────────────────
  const sortedMessages = computed(() =>
    [...messages.value].sort(
      (a, b) => new Date(a.sent_at).getTime() - new Date(b.sent_at).getTime()
    )
  )

  // ── Helpers ───────────────────────────────────────────────────────
  function _mergeMessages(incoming: ChatMessage[]): number {
    let addedCount = 0
    const existingMap = new Map(messages.value.map(m => [m.uuid, m]))

    for (const msg of incoming) {
      if (existingMap.has(msg.uuid)) {
        // UPDATE STATUS PESAN LAMA!
        // Jika lawan bicara sudah membaca, sinkronkan statusnya (centang abu -> biru)
        const existing = existingMap.get(msg.uuid)!
        if (existing.status !== msg.status) {
          existing.status = msg.status
        }
      } else {
        messages.value.push(msg)
        addedCount++
      }
    }
    return addedCount
  }

  function _markLocalRead(ids: string[]) {
    const idSet = new Set(ids)
    messages.value = messages.value.map(m =>
      idSet.has(m.uuid) ? { ...m, status: 'read' } : m
    )
  }

  // ── Context actions ───────────────────────────────────────────────
  function setPendingContext(ctx: ProductContext) {
    pendingContext.value = ctx
  }

  function clearPendingContext() {
    pendingContext.value = null
  }

  // ── WebSocket Event Handlers ─────────────────────────────────────
  // Idempotent: initAfterLogin() dipanggil dari plugin + FloatingChat + login,
  // jadi listener hanya di-bind sekali untuk cegah pesan ganda.
  function _setupWebSocketListeners() {
    if (__isWsListenerBound()) return
    __markWsListenerBound()
    on('new_message', (msg: ChatMessage) => {
      _mergeMessages([msg])
      unreadCount.value = messages.value.filter(
        m => m.sender_role === 'admin' && m.status === 'sent'
      ).length
    })

    on('message_read', (payload: { message_ids: string[] }) => {
      _markLocalRead(payload.message_ids)
      unreadCount.value = messages.value.filter(
        m => m.sender_role === 'admin' && m.status === 'sent'
      ).length
    })

    on('connection_established', () => {
      console.log('[PesanStore] WebSocket connected, loading initial history...')
      loadInitialHistory()
    })
  }

  // ── Chat actions ──────────────────────────────────────────────────
  async function initAfterLogin() {
    if (wsInitialized) return
    wsInitialized = true
    try {
      const res = await $fetch<{ unread_count: number }>('/api/pesan?action=unread')
      unreadCount.value = res.unread_count
    } catch { /* silent */ }

    // Setup WebSocket listeners
    _setupWebSocketListeners()
    connect()
  }

  async function loadInitialHistory() {
    if (messages.value.length > 0 || isLoadingInitial.value) return
    isLoadingInitial.value = true
    try {
      const res = await $fetch<ChatMessage[]>('/api/pesan?action=history&limit=30')
      if (res.length) {
        messages.value = res
        oldestSentAt.value = res[0].sent_at
        lastSentAt.value = res[res.length - 1].sent_at
      }
      hasMoreHistory.value = res.length >= 30
    } catch (e) {
      console.error('[pesan] loadInitialHistory:', e)
    } finally {
      isLoadingInitial.value = false
    }
  }

  async function loadMoreHistory() {
    if (!hasMoreHistory.value || isLoadingHistory.value) return
    isLoadingHistory.value = true
    try {
      const qs = oldestSentAt.value
        ? `&before_sent_at=${encodeURIComponent(oldestSentAt.value)}&limit=30`
        : '&limit=30'
      const res = await $fetch<ChatMessage[]>(`/api/pesan?action=history${qs}`)
      if (res.length) {
        const existing = new Set(messages.value.map(m => m.uuid))
        const newOnes = res.filter(m => !existing.has(m.uuid))
        messages.value = [...newOnes, ...messages.value]
        oldestSentAt.value = res[0].sent_at
      }
      hasMoreHistory.value = res.length >= 30
    } catch (e) {
      console.error('[pesan] loadMoreHistory:', e)
    } finally {
      isLoadingHistory.value = false
    }
  }

  async function sendMessage(
    body: string,
    images: File[] = [],
    productContext?: ProductContext
  ): Promise<boolean> {
    if (isSending.value) return false
    isSending.value = true
    try {
      const form = new FormData()
      if (body.trim()) form.append('body', body.trim())
      images.slice(0, 2).forEach(f => form.append('images', f))

      const res = await $fetch<ChatMessage>('/api/pesan', { method: 'POST', body: form })

      messages.value.push({ ...res, _productContext: productContext })

      if (!lastSentAt.value || new Date(res.sent_at) > new Date(lastSentAt.value)) {
        lastSentAt.value = res.sent_at
      }

      return true
    } catch (e) {
      console.error('[pesan] sendMessage:', e)
      return false
    } finally {
      isSending.value = false
    }
  }

  async function markAllRead() {
    const ids = messages.value
      .filter(m => m.sender_role === 'admin' && m.status === 'sent')
      .map(m => m.uuid)

    // Tetap hilangkan badge meskipun tidak ada ID yang di layar (misal glitch)
    if (!ids.length) {
      if (unreadCount.value > 0) unreadCount.value = 0
      return
    }

    try {
      await $fetch('/api/pesan', { method: 'PATCH', body: { message_ids: ids } })
      _markLocalRead(ids)
      unreadCount.value = 0
    } catch (e) {
      console.error('[pesan] markAllRead:', e)
    }
  }

  function onPopupOpen() {
    isPopupOpen = true
    loadInitialHistory()
  }

  function onPopupClose() {
    isPopupOpen = false
  }

  function reset() {
    disconnect()
    __resetWsListenerBound()
    wsInitialized = false
    messages.value = []
    unreadCount.value = 0
    lastSentAt.value = null
    oldestSentAt.value = null
    hasMoreHistory.value = true
    pendingContext.value = null
    isPopupOpen = false
    isLoadingInitial.value = false
  }

  return {
    messages: sortedMessages,
    unreadCount,
    hasMoreHistory,
    isLoadingHistory,
    isLoadingInitial,
    isSending,
    pendingContext,

    setPendingContext,
    clearPendingContext,
    initAfterLogin,
    disconnect,
    loadMoreHistory,
    onPopupOpen,
    onPopupClose,
    startPassivePolling: initAfterLogin, // alias fallback backwards compatibility
    stopPolling: disconnect,
    sendMessage,
    markAllRead,
    reset,
  }
})