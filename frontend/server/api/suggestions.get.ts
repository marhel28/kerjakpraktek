/**
 * server/api/suggestions.get.ts
 * ==============================
 * Proxy layer untuk mengambil auto-complete suggestions chatbot.
 * GET /api/suggestions?q=... -> kirim query saran
 *
 * Semua request forward Authorization dari cookie 'token'.
 */

import { defineEventHandler, getQuery, getCookie } from 'h3'

export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'token')
  const config = useRuntimeConfig()
  const BACKEND = config.public.apiBase as string

  const query = getQuery(event)
  const qStr = query.q ? `?q=${encodeURIComponent(String(query.q))}` : ''

  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return await $fetch(`${BACKEND}/chatbot/suggestions${qStr}`, {
    method: 'GET',
    headers,
  })
})

