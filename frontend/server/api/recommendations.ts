export default cachedEventHandler(async (event) => {
    const query = getQuery(event)
    const uuid = query.uuid as string
    const slug = query.slug as string
    const config = useRuntimeConfig()
    
    if (!uuid && !slug) return { data: [] }
    
    try {
      const apiUrl = config.public.apiBase || 'http://127.0.0.1:8000'
      
      // Gunakan endpoint yang sesuai
      const endpoint = uuid 
        ? `${apiUrl}/stok/public/recommendations/${uuid}`
        : `${apiUrl}/stok/public/recommendations/slug/${slug}`

      const response = await $fetch(endpoint)
      return response
    } catch (error) {
      return { data: [] }
    }
  }, {
    name: 'product-recommendations-cache',
    getKey: (event) => {
        const q = getQuery(event)
        return String(q.uuid || q.slug)
    },
    maxAge: 120,
    swr: true
  })