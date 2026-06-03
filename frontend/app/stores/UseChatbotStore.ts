/**
 * stores/UseChatbotStore.ts
 * =========================
 * Pinia store untuk PasarBot AI (RAG).
 * Mendukung: chat, suggestions, feedback (👍/👎), escalation ke Admin.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface BotProduct {
  uuid: string
  title: string
  slug: string
  price: number
  original_price?: number
  discount_percentage?: number
  image?: string
  brand?: string
  type?: string
  specs?: Record<string, any>
}

export interface BotMessage {
  uuid: string
  role: 'user' | 'model'
  content: string
  sent_at: string
  products?: BotProduct[]
  needs_escalation?: boolean
  feedback?: 'satisfied' | 'unsatisfied' | null
  knowledge_uuid?: string  // Jika dijawab dari knowledge base
}

export const useChatbotStore = defineStore('chatbot', () => {
  const messages = ref<BotMessage[]>([])
  const isSending = ref(false)
  const suggestions = ref<string[]>([])
  const isEscalating = ref(false)

  // System welcome message
  const welcomeMessage: BotMessage = {
    uuid: 'welcome-msg-bot',
    role: 'model',
    content:
      '👋 Halo Kak! Selamat datang di **PasarCCTV**.\n\n' +
      'Saya **PasarBot** — asisten AI toko kami. Siap membantu Kakak menemukan kamera keamanan, CCTV, atau aksesori yang paling sesuai.\n\n' +
      '💬 Silakan ketik produk atau pertanyaan Kakak, misalnya:\n' +
      '*"kamera outdoor 5MP"*, *"CCTV WiFi untuk rumah"*, *"harga Hikvision"*',
    sent_at: new Date().toISOString(),
  }

  function init() {
    if (messages.value.length === 0) {
      messages.value = [{ ...welcomeMessage }]
    }
    // Fetch initial suggestions
    fetchSuggestions('')
  }

  async function sendMessage(text: string): Promise<boolean> {
    if (isSending.value || !text.trim()) return false
    isSending.value = true

    const userMsgUuid = 'user-' + Math.random().toString(36).substr(2, 9)
    const userMsg: BotMessage = {
      uuid: userMsgUuid,
      role: 'user',
      content: text.trim(),
      sent_at: new Date().toISOString(),
    }
    messages.value.push(userMsg)

    // Prepare history (exclude welcome + current message)
    const historyPayload = messages.value
      .filter(m => m.uuid !== 'welcome-msg-bot' && m.uuid !== userMsgUuid)
      .map(m => ({ role: m.role, content: m.content }))

    try {
      const res = await $fetch<{
        reply: string
        products: BotProduct[]
        needs_escalation: boolean
      }>('/api/chatbot', {
        method: 'POST',
        body: { message: text.trim(), history: historyPayload },
      })

      const botMsgUuid = 'bot-' + Math.random().toString(36).substr(2, 9)
      messages.value.push({
        uuid: botMsgUuid,
        role: 'model',
        content: res.reply,
        sent_at: new Date().toISOString(),
        products: res.products || [],
        needs_escalation: res.needs_escalation || false,
        feedback: null,
      })

      return true
    } catch (e) {
      console.error('[chatbot] Failed to send message:', e)
      messages.value.push({
        uuid: 'error-msg-' + Math.random().toString(36).substr(2, 9),
        role: 'model',
        content:
          'Maaf Kak, terjadi kendala saat menghubungkan ke PasarBot. ' +
          'Silakan coba kirim kembali pesan Kakak, atau hubungi Admin kami. 🙏',
        sent_at: new Date().toISOString(),
        needs_escalation: true,
        feedback: null,
      })
      return false
    } finally {
      isSending.value = false
    }
  }

  async function fetchSuggestions(q?: string) {
    try {
      const qStr = q && q.trim() ? `?q=${encodeURIComponent(q.trim())}` : ''
      const res = await $fetch<{ suggestions: string[] }>(`/api/suggestions${qStr}`)
      suggestions.value = res.suggestions || []
    } catch (_e) {
      // Silent fail — suggestions bukan fitur kritis
      suggestions.value = []
    }
  }

  async function submitFeedback(
    msgUuid: string,
    satisfied: boolean,
    query?: string,
    knowledgeUuid?: string
  ): Promise<void> {
    // Update lokal state dulu (optimistic update)
    const msg = messages.value.find(m => m.uuid === msgUuid)
    let botReply = ''
    if (msg) {
      msg.feedback = satisfied ? 'satisfied' : 'unsatisfied'
      botReply = msg.content
    }

    try {
      await $fetch('/api/chatbot-feedback', {
        method: 'POST',
        body: {
          message_uuid: msgUuid,
          satisfied,
          query,
          knowledge_uuid: knowledgeUuid,
          bot_reply: botReply,
        },
      })
    } catch (e) {
      console.warn('[chatbot] Failed to submit feedback:', e)
    }
  }

  async function escalateToAdmin(lastQuery?: string): Promise<string> {
    isEscalating.value = true
    try {
      const res = await $fetch<{ ok: boolean; message: string }>(
        '/api/chatbot-escalate',
        {
          method: 'POST',
          body: { last_query: lastQuery },
        }
      )
      return res.message || 'Percakapan diteruskan ke Admin.'
    } catch (e) {
      console.warn('[chatbot] Escalation failed:', e)
      return 'Silakan chat langsung di tab "Tanya Admin" ya Kak.'
    } finally {
      isEscalating.value = false
    }
  }

  function reset() {
    messages.value = [{ ...welcomeMessage }]
    isSending.value = false
    suggestions.value = []
    isEscalating.value = false
  }

  return {
    messages,
    isSending,
    suggestions,
    isEscalating,
    init,
    sendMessage,
    fetchSuggestions,
    submitFeedback,
    escalateToAdmin,
    reset,
  }
})
