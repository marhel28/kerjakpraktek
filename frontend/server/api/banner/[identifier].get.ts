/**
 * Nitro API Handler — /api/banner/[identifier]
 * Path: server/api/banner/[identifier].get.ts
 */

import { defineEventHandler, getRouterParam, createError } from 'h3'
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase || 'http://localhost:8000'

export default defineEventHandler(async (event) => {
  const raw = getRouterParam(event, 'identifier')
  const identifier = decodeURIComponent(raw ?? '').trim()

  if (!identifier) {
    throw createError({ statusCode: 400, statusMessage: 'Identifier diperlukan' })
  }

  try {
    const response = await $fetch(
      `${BACKEND_URL}/image-sections/public/${encodeURIComponent(identifier)}`,
      {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        timeout: 5000,
      }
    )
    return response
  } catch (err: any) {
    if (err?.response?.status === 404 || err?.statusCode === 404) {
      return { status: 'success', source: 'backend', data: null }
    }
    console.error(`[BannerAPI] Error identifier="${identifier}":`, err?.message)
    return { status: 'error', source: 'backend', data: null }
  }
})