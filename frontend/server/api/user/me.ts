// server/api/user/me.ts
export default defineEventHandler(async (event) => {
    const method = event.node.req.method
    const config = useRuntimeConfig()
    const backendUrl = config.apiBase || config.public.apiBase || 'http://localhost:8000'
    
    // Ambil token dari cookie (yang di-set saat login)
    const token = getCookie(event, 'token')
    
    if (!token) {
      throw createError({ statusCode: 401, statusMessage: 'Unauthorized' })
    }
  
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  
    try {
      if (method === 'GET') {
        // Hit GET /me di FastAPI
        const response = await $fetch(`${backendUrl}/me`, { headers })
        return response
      } 
      
      if (method === 'PATCH') {
        const body = await readBody(event)
        // Hit PATCH /me di FastAPI
        const response = await $fetch(`${backendUrl}/me`, {
          method: 'PATCH',
          headers,
          body
        })
        return response
      }
    } catch (error: any) {
      throw createError({
        statusCode: error.response?.status || 500,
        statusMessage: error.data?.detail || 'Terjadi kesalahan pada server'
      })
    }
  })