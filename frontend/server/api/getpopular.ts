import { getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const query = getQuery(event)

  const limit = Math.min(Number(query.limit) || 10, 50)

  try {
    const data = await $fetch(`${config.public.apiBase}/stok/public/popular`, {
      query: { limit },
      timeout: 4000,
    })

    return data

  } catch (error) {
    console.error('POPULAR API ERROR:', error)

    return {
      items: [],
      total: 0,
    }
  }
})