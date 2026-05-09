import {
    defineEventHandler,
    getRouterParam,
    getQuery,
    createError,
    getHeader,
    getCookie
  } from 'h3'
  const config = useRuntimeConfig()
  export default defineEventHandler(async (event) => {
    const id    = getRouterParam(event, 'id')
    const query = getQuery(event)
  
    if (!id) {
      throw createError({ statusCode: 400, statusMessage: 'Missing booking id' })
    }
  
    const paymentType = query.payment_type ? String(query.payment_type) : undefined
  
    if (!paymentType || !['dp', 'lunas'].includes(paymentType)) {
      throw createError({
        statusCode: 400,
        statusMessage: 'payment_type harus dp atau lunas'
      })
    }
  
    const backendUrl = config.public.apiBase ?? 'http://localhost:8000'
    const url = `${backendUrl}/user/bookings/${id}/pay?payment_type=${paymentType}`
  
    // ✅ ambil cookie & token
    const cookie = getHeader(event, 'cookie') ?? ''
    const token  = getCookie(event, 'token')
  
    const headers: Record<string, string> = {
      'content-type': 'application/json',
    }
  
    // ✅ inject bearer token (INI WAJIB)
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  
    // optional: forward cookie juga
    if (cookie) {
      headers['cookie'] = cookie
    }
  
    const res = await fetch(url, {
      method: 'POST',
      headers,
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