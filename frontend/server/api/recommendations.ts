export default cachedEventHandler(async (event) => {
    const query = getQuery(event)
    const stock_uuid = query.uuid
    const config = useRuntimeConfig()
    
    if (!stock_uuid) return { data: [] }
    
    try {
      const apiUrl = config.public.apiBase || 'http://127.0.0.1:8000'
      // Endpoint Elasticsearch yang sudah kita buat sebelumnya
      const response = await $fetch(`${apiUrl}/stok/public/recommendations/${stock_uuid}`)
      return response
    } catch (error) {
      return { data: [] } // Fallback kosong jika ES gagal/belum ada data
    }
  }, {
    name: 'product-recommendations-cache',
    getKey: (event) => String(getQuery(event).uuid),
    maxAge: 120, // Cache lebih lama (2 menit) untuk rekomendasi
    swr: true
  })