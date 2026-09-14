import { defineEventHandler, readBody, getCookie, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const method = event.node.req.method
  const token = getCookie(event, 'token')
  const config = useRuntimeConfig()
  const BACKEND = config.public.apiBase as string

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  try {
    if (method === 'GET') {
      return await $fetch(`${BACKEND}/settings/promo-popup`, {
        method: 'GET',
        headers,
        timeout: 5000,
      })
    }

    if (method === 'PUT') {
      const body = await readBody(event)
      return await $fetch(`${BACKEND}/settings/promo-popup`, {
        method: 'PUT',
        headers,
        body,
      })
    }
  } catch (error: any) {
    if (method === 'GET') {
      return {
        success: true,
        data: {
          image_url: '',
          route: '',
          is_active: false,
        },
      }
    }
    throw createError({
      statusCode: error.response?.status || 500,
      statusMessage: error.data?.detail || 'Terjadi kesalahan pada server'
    })
  }
})
