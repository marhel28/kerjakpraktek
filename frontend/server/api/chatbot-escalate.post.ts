/**
 * server/api/chatbot-escalate.post.ts
 * =====================================
 * Proxy: POST /api/chatbot-escalate → POST /chatbot/escalate
 */
import { defineEventHandler, readBody, getCookie, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'token')
  if (!token) {
    throw createError({ statusCode: 401, message: 'Tidak terautentikasi.' })
  }

  const config = useRuntimeConfig()
  const BACKEND = config.public.apiBase as string
  const body = await readBody(event)

  return await $fetch(`${BACKEND}/chatbot/escalate`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
})
