/**
 * server/api/chatbot-feedback.post.ts
 * =====================================
 * Proxy: POST /api/chatbot-feedback → POST /chatbot/feedback
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

  return await $fetch(`${BACKEND}/chatbot/feedback`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
})
