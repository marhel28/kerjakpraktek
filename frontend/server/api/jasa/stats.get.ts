import {
    defineEventHandler,
    getCookie,
    createError
  } from 'h3'
  
  export default defineEventHandler(async (event) => {
    const config = useRuntimeConfig()
  
    const token = getCookie(event, 'token')
  
    if (!token) {
      throw createError({ statusCode: 401, statusMessage: 'Unauthorized' })
    }
  
    const url = `${config.public.apiBase}/user/bookings/stats/summary`
  
    try {
      const res = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })
  
      if (!res.ok) {
        throw createError({
          statusCode: res.status,
          statusMessage: 'Gagal mengambil stats'
        })
      }
  
      return await res.json()
  
    } catch (err: any) {
      if (err.statusCode) throw err
  
      throw createError({
        statusCode: 502,
        statusMessage: 'Backend tidak tersedia'
      })
    }
  })