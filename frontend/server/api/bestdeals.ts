import { getQuery } from 'h3'

export default cachedEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const query = getQuery(event)

  const limit = Math.min(Number(query.limit) || 12, 50)

  try {
    const data = await $fetch(`${config.public.apiBase}/stok/public/best-deals`, {
      query: { limit },
      timeout: 4000,
    })

    return data

  } catch (error) {
    console.error('[BFF] Best Deals error:', error)
    return { items: [], total: 0 }
  }
}, {
  name: 'best-deals',
  getKey: () => 'best-deals:home',
  maxAge: 300,       // 5 menit fresh
  staleMaxAge: 600,  // 10 menit stale-while-revalidate
  swr: true,
})
