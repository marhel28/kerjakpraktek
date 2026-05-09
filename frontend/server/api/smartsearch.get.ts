import { defineEventHandler, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const q = query.q as string

  // Jangan hit API jika karakter kurang dari 2 (hemat resource)
  if (!q || q.length < 2) {
    return { suggestion: null, categories: [], items: [] }
  }

  // Gunakan runtimeConfig untuk URL backend FastAPI (atur di nuxt.config.ts)
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiBase || 'http://127.0.0.1:8000'

  try {
    // Tembak endpoint Elasticsearch yang sudah kita buat di FastAPI sebelumnya
    // Batasi size=5 karena ini hanya untuk dropdown autocomplete
    const response: any = await $fetch(`${apiUrl}/stok/public/list`, {
      params: { 
        q: q, 
        size: 5 
      }
    })

    const data = response.data || response

    // Ekstrak facet kategori (ambil 3 kategori teratas saja)
    const categoryFacets = data.facets?.categories || {}
    const topCategories = Object.keys(categoryFacets)
      .sort((a, b) => categoryFacets[b] - categoryFacets[a]) // Urutkan dari jumlah produk terbanyak
      .slice(0, 3)

    return {
      suggestion: data.suggestion,
      categories: topCategories,
      items: data.items || []
    }
  } catch (error) {
    console.error("SmartSearch Proxy Error:", error)
    return { suggestion: null, categories: [], items: [] }
  }
})