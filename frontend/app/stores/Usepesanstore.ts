/**
 * stores/usePesanStore.ts
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
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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

const POLL_ACTIVE_MS  = 3_000
const POLL_PASSIVE_MS = 2 * 60_000

export const usePesanStore = defineStore('pesan', () => {

  // ── State ────────────────────────────────────────────────────────
  const messages         = ref<ChatMessage[]>([])
  const unreadCount      = ref(0)
  const lastSentAt       = ref<string | null>(null)
  const oldestSentAt     = ref<string | null>(null)
  const hasMoreHistory   = ref(true)
  const isLoadingHistory = ref(false)
  const isLoadingInitial = ref(false)
  const isSending        = ref(false)
  
  // Flag untuk mematikan/menyalakan timer polling secara pintar
  const isPollingPaused  = ref(false) 

  /**
   * pendingContext — disimpan di store supaya persist lintas navigasi.
   * Set dari halaman produk, dibaca FloatingChat di layout.
   */
  const pendingContext = ref<ProductContext | null>(null)

  let pollTimer: ReturnType<typeof setTimeout> | null = null
  let isPopupOpen = false
  let pollCycleCount = 0 // Untuk rotasi antara polling pesan baru vs sync status

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

  // ── Smart Polling Logic ───────────────────────────────────────────
  function evaluatePollingState() {
    // Kondisi 1: Chat masih kosong (belum pernah ada interaksi) -> STOP
    if (messages.value.length === 0) {
      isPollingPaused.value = true
      return
    }

    const lastMsg = sortedMessages.value[sortedMessages.value.length - 1]
    
    // Kondisi 2: Pesan terakhir dari admin DAN popup sedang ditutup -> STOP
    // (Jika popup terbuka, biarkan jalan agar pesan susulan admin tetap masuk live)
    if (lastMsg && lastMsg.sender_role === 'admin' && !isPopupOpen) {
      isPollingPaused.value = true
      return
    }

    // Selain itu -> JALAN
    isPollingPaused.value = false
  }

  // ── Chat actions ──────────────────────────────────────────────────

  async function initAfterLogin() {
    try {
      const res = await $fetch<{ unread_count: number }>('/api/pesan?action=unread')
      unreadCount.value = res.unread_count
      
      // Pancing _scheduleNextPoll, nanti dia akan mengevaluasi sendiri
      // apakah perlu pasif polling atau langsung stop (misal chat masih kosong)
      _scheduleNextPoll()
    } catch { /* silent */ }
  }

  async function loadInitialHistory() {
    if (messages.value.length > 0 || isLoadingInitial.value) return
    isLoadingInitial.value = true
    try {
      const res = await $fetch<ChatMessage[]>('/api/pesan?action=history&limit=30')
      if (res.length) {
        messages.value     = res
        oldestSentAt.value = res[0].sent_at
        lastSentAt.value   = res[res.length - 1].sent_at
      }
      hasMoreHistory.value = res.length >= 30
      
      // Evaluasi setelah history termuat
      evaluatePollingState()
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
        const newOnes  = res.filter(m => !existing.has(m.uuid))
        messages.value     = [...newOnes, ...messages.value]
        oldestSentAt.value = res[0].sent_at
      }
      hasMoreHistory.value = res.length >= 30
    } catch (e) {
      console.error('[pesan] loadMoreHistory:', e)
    } finally {
      isLoadingHistory.value = false
    }
  }

  async function _doPoll() {
    try {
      pollCycleCount++
      
      // ROTASI OPTIMASI:
      // - Tiap 5x poll (15 detik), ambil 30 pesan terakhir untuk sync status (sent -> read)
      // - Selain itu, cukup ambil pesan baru saja (action=poll) -> SANGAT RINGAN
      const isSyncCycle = pollCycleCount % 5 === 0
      const hasMessages = messages.value.length > 0
      
      let endpoint = '/api/pesan?action=history&limit=30'
      
      if (!isSyncCycle && hasMessages && lastSentAt.value) {
        endpoint = `/api/pesan?action=poll&after_sent_at=${encodeURIComponent(lastSentAt.value)}`
      }

      const res = await $fetch<ChatMessage[]>(endpoint)

      if (res.length) {
        const added = _mergeMessages(res)
        
        if (added > 0) {
          const sorted = [...messages.value].sort((a, b) => new Date(a.sent_at).getTime() - new Date(b.sent_at).getTime())
          lastSentAt.value = sorted[sorted.length - 1].sent_at
        }

        // Kalkulasi unread terpusat dari state lokal
        unreadCount.value = messages.value.filter(
          m => m.sender_role === 'admin' && m.status === 'sent'
        ).length
      }
    } catch { /* silent */ }
  }

  async function _doPollUnread() {
    try {
      const res = await $fetch<{ unread_count: number }>('/api/pesan?action=unread')
      unreadCount.value = res.unread_count
    } catch { /* silent */ }
  }

  function _scheduleNextPoll() {
    if (pollTimer) clearTimeout(pollTimer)

    // Cek apakah polling sedang mode istirahat
    evaluatePollingState()
    if (isPollingPaused.value) {
      console.log("[pesan] Polling dihentikan sementara (Idle).")
      return // Jangan set timeout baru
    }

    const ms = isPopupOpen ? POLL_ACTIVE_MS : POLL_PASSIVE_MS
    pollTimer = setTimeout(async () => {
      if (isPopupOpen) await _doPoll()
      else await _doPollUnread()
      
      _scheduleNextPoll()
    }, ms)
  }

  function onPopupOpen() {
    isPopupOpen = true
    isPollingPaused.value = false // Paksa jalan karena user sedang memantau
    _scheduleNextPoll()
    loadInitialHistory()
  }

  function onPopupClose() {
    isPopupOpen = false
    if (pollTimer) clearTimeout(pollTimer)
    // Panggil schedule untuk evaluasi (kemungkinan besar akan mati jika admin yang membalas terakhir)
    _scheduleNextPoll() 
  }

  function startPassivePolling() {
    if (pollTimer) return
    _scheduleNextPoll()
  }

  function stopPolling() {
    if (pollTimer) { clearTimeout(pollTimer); pollTimer = null }
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

      isPollingPaused.value = false // Paksa nyala karena user baru kirim
      await _doPoll()
      _scheduleNextPoll() // Restart timer tancap gas

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

  function reset() {
    stopPolling()
    messages.value       = []
    unreadCount.value    = 0
    lastSentAt.value     = null
    oldestSentAt.value   = null
    hasMoreHistory.value = true
    pendingContext.value = null
    isPopupOpen          = false
    isPollingPaused.value= false
  }

  return {
    messages: sortedMessages,
    unreadCount,
    hasMoreHistory,
    isLoadingHistory,
    isLoadingInitial,
    isSending,
    pendingContext,
    isPollingPaused, // di-expose barangkali butuh ditrack di Vue DevTools

    setPendingContext,
    clearPendingContext,
    initAfterLogin,
    loadMoreHistory,
    onPopupOpen,
    onPopupClose,
    startPassivePolling,
    stopPolling,
    sendMessage,
    markAllRead,
    reset,
  }
})