/**
 * server/api/chatbot.post.ts
 * ===========================
 * Proxy layer antara Nuxt FE dan FastAPI backend untuk sistem chatbot RAG (PasarBot).
 * POST /api/chatbot { message, history[] } -> kirim kueri chat
 *
 * Server-side proxy agar token tidak expose di network tab browser.
 */

import { defineEventHandler, readBody, getCookie } from 'h3'

export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'token')
  const config = useRuntimeConfig()
  const BACKEND = config.public.apiBase as string

  const body = await readBody(event)

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return await $fetch(`${BACKEND}/chatbot/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
})
