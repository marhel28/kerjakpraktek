/**
 * server/api/notifications.ts
 * Proxy Nuxt → FastAPI untuk notifikasi user.
 * Token diambil dari cookie, tidak dikirim dari browser.
 */

import {
  defineEventHandler,
  readBody,
  getQuery,
  getCookie,
  createError,
  getMethod,
} from 'h3'

const config = useRuntimeConfig()
const BACKEND = `${config.public.apiBase}`

function getToken(event: any): string {
  const token = getCookie(event, 'token')
  if (!token) throw createError({ statusCode: 401, message: 'Tidak terautentikasi.' })
  return token
}

function jsonHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  const token = getToken(event)

  if (method === 'GET') {
    const query = getQuery(event)
    const params = new URLSearchParams()
    params.set('limit', (query.limit as string) || '50')
    return await $fetch(`${BACKEND}/notifications?${params.toString()}`, {
      headers: jsonHeaders(token),
    })
  }

  if (method === 'PATCH') {
    const body = await readBody(event)
    const id = Number(body?.id)
    if (!Number.isInteger(id)) {
      throw createError({ statusCode: 400, message: 'id notifikasi tidak valid.' })
    }
    return await $fetch(`${BACKEND}/notifications/${id}/read`, {
      method: 'PATCH',
      headers: jsonHeaders(token),
    })
  }

  if (method === 'POST') {
    return await $fetch(`${BACKEND}/notifications/read-all`, {
      method: 'POST',
      headers: jsonHeaders(token),
    })
  }

  if (method === 'DELETE') {
    const query = getQuery(event)
    const id = Number(query.id)
    if (!Number.isInteger(id)) {
      throw createError({ statusCode: 400, message: 'id notifikasi tidak valid.' })
    }
    await $fetch(`${BACKEND}/notifications/${id}`, {
      method: 'DELETE',
      headers: jsonHeaders(token),
    })
    return { success: true }
  }

  throw createError({ statusCode: 405, message: 'Method tidak diizinkan.' })
})
