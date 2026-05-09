// FILE: server/api/jasa/index.get.ts
import { defineEventHandler, getQuery, getRequestHeaders, getCookie, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const query = getQuery(event)
  const headers = getRequestHeaders(event)

  // 🔐 ambil token dari cookie
  const token = getCookie(event, 'token')

  if (!token) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized - Token tidak ditemukan',
    })
  }

  // 🔧 build query params
  const params = new URLSearchParams()
  if (query.status) params.set('status', String(query.status))
  if (query.sort) params.set('sort', String(query.sort))
  if (query.q) params.set('q', String(query.q))
  if (query.page) params.set('page', String(query.page))
  if (query.size) params.set('size', String(query.size))

  // 📡 forward headers
  const forwardHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`, // 🔥 WAJIB pakai bearer dari cookie
  }

  // optional: tetap forward cookie kalau backend butuh
  if (headers.cookie) {
    forwardHeaders['Cookie'] = headers.cookie
  }

  const url = `${config.public.apiBase}/user/bookings?${params.toString()}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: forwardHeaders,
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Backend error' }))
      throw createError({
        statusCode: response.status,
        statusMessage: err.detail || 'Gagal mengambil data booking',
      })
    }

    return await response.json()
  } catch (err: any) {
    if (err.statusCode) throw err

    throw createError({
      statusCode: 502,
      statusMessage: 'Tidak dapat terhubung ke server',
    })
  }
})