import { defineEventHandler } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://127.0.0.1:8000'

  try {
    const data = await $fetch(`${apiBase}/promos/flash-sale/active`, {
      method: 'GET',
    })
    return data
  } catch (err: any) {
    // Fallback bila promo belum ada
    return {
      status: 'empty',
      items: [],
      remaining_seconds: 0,
    }
  }
})