// server/api/search.ts
export default defineEventHandler(async (event) => {
    const config = useRuntimeConfig()
    const query = getQuery(event)
  
    try {
      // 🔥 PERBAIKAN: Tambahkan "/stok" sebelum "/public/list"
      const data = await $fetch(`${config.public.apiBase}/stok/public/list`, {
        query: query
      })
      
      return data
    } catch (error) {
      console.error("Elasticsearch Proxy Error:", error)
      return { status: "error", items: [], total: 0, suggestion: null, facets: {} }
    }
  })