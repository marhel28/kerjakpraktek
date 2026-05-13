/**
 * server/api/pesan.ts
 * ====================
 * Proxy layer antara Nuxt FE dan FastAPI backend untuk sistem pesan.
 *
 * Rules:
 * - GET  /api/pesan?action=history&before_sent_at=   → load history (lazy/load-more)
 * - GET  /api/pesan?action=poll&after_sent_at=       → polling pesan baru
 * - GET  /api/pesan?action=unread                    → badge count (polling ringan)
 * - POST /api/pesan         { body, images[] }       → kirim pesan (multipart)
 * - PATCH /api/pesan        { message_ids[] }        → mark as read
 *
 * Semua request forward Authorization dari cookie 'token'.
 * Server-side proxy agar token tidak expose di network tab browser.
 */

import {
    defineEventHandler,
    readBody,
    readMultipartFormData,
    getQuery,
    getCookie,
    createError,
    getMethod,
  } from 'h3'
  const config = useRuntimeConfig();
  const BACKEND = `${config.public.apiBase}`
  
  // ── Helper: ambil token dari cookie ───────────────────────────────
  function getToken(event: any): string {
    const token = getCookie(event, 'token')
    if (!token) {
      throw createError({ statusCode: 401, message: 'Tidak terautentikasi.' })
    }
    return token
  }
  
  // ── Helper: headers JSON standar ──────────────────────────────────
  function jsonHeaders(token: string) {
    return {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  }
  
  export default defineEventHandler(async (event) => {
    const method = getMethod(event)
    const token = getToken(event)
  
    // ════════════════════════════════════════════════════════════════
    // GET — history | poll | unread
    // ════════════════════════════════════════════════════════════════
    if (method === 'GET') {
      const query = getQuery(event)
      const action = query.action as string
  
      // ── GET ?action=history&before_sent_at=<ISO>&limit=30 ─────────
      // Load pesan lama (lazy load saat scroll ke atas)
      if (action === 'history') {
        const params = new URLSearchParams()
        if (query.before_sent_at) params.set('before_sent_at', query.before_sent_at as string)
        params.set('limit', (query.limit as string) || '30')
  
        return await $fetch(`${BACKEND}/messages/history?${params.toString()}`, {
          headers: jsonHeaders(token),
        })
      }
  
      // ── GET ?action=poll&after_sent_at=<ISO> ──────────────────────
      // Polling pesan baru (cursor-based, ringan)
      if (action === 'poll') {
        const params = new URLSearchParams()
        if (query.after_sent_at) params.set('after_sent_at', query.after_sent_at as string)
  
        return await $fetch(`${BACKEND}/messages/poll?${params.toString()}`, {
          headers: jsonHeaders(token),
        })
      }
  
      // ── GET ?action=unread ─────────────────────────────────────────
      // Badge count — sangat ringan, hanya 1 angka
      if (action === 'unread') {
        return await $fetch(`${BACKEND}/messages/unread`, {
          headers: jsonHeaders(token),
        })
      }
  
      throw createError({ statusCode: 400, message: 'action tidak valid.' })
    }
  
    // ════════════════════════════════════════════════════════════════
    // POST — kirim pesan (multipart form: body + images)
    // ════════════════════════════════════════════════════════════════
    if (method === 'POST') {
      // Baca multipart dari FE
      const parts = await readMultipartFormData(event)
      if (!parts) throw createError({ statusCode: 400, message: 'Form data kosong.' })
  
      // Forward ke backend sebagai FormData baru
      const form = new FormData()
      for (const part of parts) {
        if (part.name === 'images' && part.data) {
          // Rekonstruksi File dari buffer
          const blob = new Blob([part.data], { type: part.type || 'image/jpeg' })
          form.append('images', blob, part.filename || 'image.jpg')
        } else if (part.name === 'body' && part.data) {
          form.append('body', part.data.toString('utf-8'))
        }
      }
  
      return await $fetch(`${BACKEND}/messages/send`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }, // tanpa Content-Type, biar FormData set boundary
        body: form,
      })
    }
  
    // ════════════════════════════════════════════════════════════════
    // PATCH — mark as read
    // ════════════════════════════════════════════════════════════════
    if (method === 'PATCH') {
      const body = await readBody(event)
  
      return await $fetch(`${BACKEND}/messages/read`, {
        method: 'PATCH',
        headers: jsonHeaders(token),
        body: JSON.stringify(body),
      })
    }
  
    throw createError({ statusCode: 405, message: 'Method tidak diizinkan.' })
  })