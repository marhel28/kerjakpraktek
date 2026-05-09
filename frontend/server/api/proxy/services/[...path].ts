export default defineEventHandler(async (event) => {
    const config = useRuntimeConfig()
    const path = event.context.params?.path || ''
    const method = event.method
    const query = getQuery(event)
  
    let body: any = undefined
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      body = await readBody(event)
    }
  
    const queryStr = Object.keys(query).length
      ? '?' + new URLSearchParams(query as any).toString()
      : ''
  
    const url = `${config.public.apiBase}/services/${path}${queryStr}`
  
    try {
        const response = await $fetch(url, {
          method: method as any,
          body,
          headers: {
            'Content-Type': 'application/json',
            // Forward auth cookie jika ada
            ...(getHeader(event, 'cookie')
              ? { cookie: getHeader(event, 'cookie')! }
              : {}),
            // WAJIB DITAMBAHKAN: Forward Authorization header (JWT Bearer)
            ...(getHeader(event, 'authorization')
              ? { authorization: getHeader(event, 'authorization')! }
              : {}),
          },
          timeout: 10_000,
        })
        return response
      } catch (err: any) {
         // ... handling error ...
      }
  })