// server/api/jasa/[id].get.ts

import {
    defineEventHandler,
    getRouterParam,
    createError,
    getHeader,
    getCookie
  } from 'h3'
  const config = useRuntimeConfig()
  export default defineEventHandler(async (event) => {
    const id = getRouterParam(event, 'id')
  
    if (!id) {
      throw createError({ statusCode: 400, statusMessage: 'Missing booking id' })
    }
  
    // ✅ ambil cookie raw (optional, kalau backend masih butuh)
    const cookie = getHeader(event, 'cookie') ?? ''
  
    // ✅ ambil token spesifik
    const token = getCookie(event, 'token')
  
    const backendUrl = config.public.apiBase ?? 'http://localhost:8000'
    const url = `${backendUrl}/user/bookings/${id}`
  
    const headers: Record<string, string> = {
      'content-type': 'application/json',
    }
  
    // ✅ inject bearer token
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  
    // optional: tetap forward cookie kalau perlu
    if (cookie) {
      headers['cookie'] = cookie
    }
  
    const res = await fetch(url, {
      method: 'GET',
      headers
    })
  
    const body = await res.json()
  
    if (!res.ok) {
      throw createError({
        statusCode: res.status,
        statusMessage: body?.detail || res.statusText,
        data: body,
      })
    }
  
    return body
  })