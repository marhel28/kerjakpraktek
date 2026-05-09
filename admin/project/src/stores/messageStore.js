/**
 * stores/messageStore.js
 * ─────────────────────────────────────────────────────────────────
 * Pinia store untuk sistem pesan admin.
 *
 * Polling:
 *   - Inbox  : setiap 8 detik (badge unread di navbar)
 *   - Chat   : setiap 3 detik saat conversation aktif terbuka
 *
 * Mark-read otomatis:
 *   - Saat openConversation() → semua pesan user status=sent di-mark read
 *   - Saat pollChat() dapat pesan user baru → langsung mark read
 *
 * Product context (mengikuti FloatingChat user — doc 5):
 *   User mengirim pesan dengan metadata embed di bawah separator "\n\n---\n":
 *     <teks user>\n\n---\n🏷️ Produk: ...\n💰 Harga: ...\n🆔 UUID: ...\n🔗 URL: ...
 *
 *   Helper yang diekspor:
 *     extractUserBody(body)   → teks bersih tanpa metadata
 *     parseProductContext(body) → objek { title, price, uuid, url } atau null
 *     detectProductLink(body) → deteksi URL produk di body mentah
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/service/api'

// ─────────────────────────────────────────────────────────────────
// Pure helpers — diekspor agar bisa dipakai di template
// ─────────────────────────────────────────────────────────────────

/** Kembalikan teks pesan user, tanpa metadata produk yang di-embed. */
export function extractUserBody(body) {
  if (!body) return ''
  const sep = body.indexOf('\n\n---\n')
  return sep !== -1 ? body.slice(0, sep).trim() : body.trim()
}

/**
 * Parse metadata produk dari body pesan user.
 * Return null jika tidak ada separator atau tidak ada field Produk.
 */
export function parseProductContext(body) {
  if (!body) return null
  const sep = body.indexOf('\n\n---\n')
  if (sep === -1) return null

  const meta = body.slice(sep + 5)
  const get  = (prefix) => {
    const line = meta.split('\n').find(l => l.startsWith(prefix))
    return line ? line.slice(prefix.length).trim() : null
  }

  const title = get('🏷️ Produk:')
  if (!title) return null

  return {
    title,
    price: get('💰 Harga:'),
    uuid:  get('🆔 UUID:'),
    url:   get('🔗 URL:'),
  }
}

/**
 * Deteksi URL produk internal di dalam body (fallback jika tidak ada embed metadata).
 * Sesuaikan pola regex dengan struktur URL project kamu.
 */
const PRODUCT_PATTERNS = [
  /\/produk\/([a-f0-9-]{36})/i,
  /\/product\/([a-f0-9-]{36})/i,
  /[?&]id=([a-f0-9-]{36})/i,
]

export function detectProductLink(body) {
  if (!body) return null
  for (const pat of PRODUCT_PATTERNS) {
    const m = body.match(pat)
    if (m) return { uuid: m[1], rawMatch: m[0] }
  }
  return null
}

// ─────────────────────────────────────────────────────────────────
// Store
// ─────────────────────────────────────────────────────────────────

export const useMessageStore = defineStore('message', () => {

  // ── State ──────────────────────────────────────────────────────
  const conversations   = ref([])
  const activeConvId    = ref(null)
  const messages        = ref([])
  const totalUnread     = ref(0)

  const loadingInbox    = ref(false)
  const loadingMessages = ref(false)
  const loadingMore     = ref(false)
  const hasMoreHistory  = ref(true)

  let inboxPollTimer = null
  let chatPollTimer  = null
  const lastSentAt   = ref(null)

  // ── Computed ───────────────────────────────────────────────────
  const totalUnreadBadge = computed(() =>
    conversations.value.reduce((sum, c) => sum + (c.unread_by_admin || 0), 0)
  )

  // ── INBOX ──────────────────────────────────────────────────────

  async function fetchInbox() {
    try {
      const { data } = await api.get('/messages/admin/inbox', {
        params: { skip: 0, limit: 50 },
      })
      conversations.value = data || []
      totalUnread.value   = conversations.value.reduce(
        (sum, c) => sum + (c.unread_by_admin || 0), 0
      )
    } catch (e) {
      console.error('[messageStore] fetchInbox:', e)
    }
  }

  function startInboxPolling() {
    stopInboxPolling()
    fetchInbox()
    inboxPollTimer = setInterval(fetchInbox, 10000)
  }

  function stopInboxPolling() {
    if (inboxPollTimer) { clearInterval(inboxPollTimer); inboxPollTimer = null }
  }

  // ── CHAT ──────────────────────────────────────────────────────

  async function openConversation(convId) {
    stopChatPolling()
    activeConvId.value    = convId
    messages.value        = []
    lastSentAt.value      = null
    hasMoreHistory.value  = true
    loadingMessages.value = true

    try {
      const { data } = await api.get(`/messages/admin/${convId}/history`, {
        params: { limit: 30 },
      })
      messages.value = data || []
      if (messages.value.length > 0) {
        lastSentAt.value = messages.value[messages.value.length - 1].sent_at
      }
      hasMoreHistory.value = (data?.length || 0) >= 30
    } catch (e) {
      console.error('[messageStore] openConversation:', e)
    } finally {
      loadingMessages.value = false
    }

    // ✅ Mark semua pesan user yang belum terbaca begitu chat dibuka
    await _markAllUserMessagesRead(convId)

    startChatPolling(convId)
  }

  async function loadMoreHistory() {
    if (!activeConvId.value || loadingMore.value || !hasMoreHistory.value) return
    const oldest = messages.value[0]
    if (!oldest) return

    loadingMore.value = true
    try {
      const { data } = await api.get(`/messages/admin/${activeConvId.value}/history`, {
        params: { before_sent_at: oldest.sent_at, limit: 30 },
      })
      if (data?.length) messages.value = [...data, ...messages.value]
      hasMoreHistory.value = (data?.length || 0) >= 30
    } catch (e) {
      console.error('[messageStore] loadMoreHistory:', e)
    } finally {
      loadingMore.value = false
    }
  }

  async function pollChat() {
    if (!activeConvId.value) return
    try {
      const params = lastSentAt.value ? { after_sent_at: lastSentAt.value } : {}
      const { data } = await api.get(`/messages/admin/${activeConvId.value}/poll`, { params })
      const newMsgs  = data?.messages || []

      if (newMsgs.length > 0) {
        messages.value   = [...messages.value, ...newMsgs]
        lastSentAt.value = newMsgs[newMsgs.length - 1].sent_at

        // ✅ Pesan user baru langsung di-mark read
        const userIds = newMsgs
          .filter(m => m.sender_role === 'user')
          .map(m => m.uuid)
        if (userIds.length) await _markRead(activeConvId.value, userIds)
      }
    } catch (e) {
      console.error('[messageStore] pollChat:', e)
    }
  }

  function startChatPolling(convId) {
    stopChatPolling()
    chatPollTimer = setInterval(() => {
      if (activeConvId.value === convId) pollChat()
    }, 3000)
  }

  function stopChatPolling() {
    if (chatPollTimer) { clearInterval(chatPollTimer); chatPollTimer = null }
  }

  // ── SEND ──────────────────────────────────────────────────────

  async function sendMessage(convId, body, images = []) {
    const form = new FormData()
    if (body) form.append('body', body)
    images.forEach(img => form.append('images', img))

    const { data } = await api.post(`/messages/admin/${convId}/send`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    messages.value   = [...messages.value, data]
    lastSentAt.value = data.sent_at

    await fetchInbox()
    return data
  }

  // ── MARK READ (internal) ─────────────────────────────────────

  async function _markRead(convId, messageIds) {
    if (!messageIds?.length) return
    try {
      await api.patch(`/messages/admin/${convId}/read`, { message_ids: messageIds })

      const idSet = new Set(messageIds)
      messages.value = messages.value.map(m =>
        idSet.has(m.uuid) ? { ...m, status: 'read' } : m
      )

      conversations.value = conversations.value.map(c =>
        c.uuid === convId ? { ...c, unread_by_admin: 0 } : c
      )
      totalUnread.value = conversations.value.reduce(
        (sum, c) => sum + (c.unread_by_admin || 0), 0
      )
    } catch (_) { /* silent */ }
  }

  async function _markAllUserMessagesRead(convId) {
    const ids = messages.value
      .filter(m => m.sender_role === 'user' && m.status === 'sent')
      .map(m => m.uuid)
    await _markRead(convId, ids)
  }

  // Public alias
  async function markAdminRead(convId, messageIds = null) {
    const ids = messageIds
      || messages.value.filter(m => m.sender_role === 'user' && m.status === 'sent').map(m => m.uuid)
    await _markRead(convId, ids)
  }

  // ── CLEANUP ──────────────────────────────────────────────────

  function closeConversation() {
    stopChatPolling()
    activeConvId.value = null
    messages.value     = []
    lastSentAt.value   = null
  }

  function destroy() {
    stopInboxPolling()
    stopChatPolling()
  }

  return {
    conversations, activeConvId, messages, totalUnread,
    loadingInbox, loadingMessages, loadingMore, hasMoreHistory, lastSentAt,
    totalUnreadBadge,
    fetchInbox, startInboxPolling, stopInboxPolling,
    openConversation, loadMoreHistory,
    sendMessage, markAdminRead,
    closeConversation, destroy,
    // helpers
    extractUserBody, parseProductContext, detectProductLink,
  }
})