export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000'

  try {
    const data = await $fetch(
      `${apiBase}/category/`,
      {
        headers: {
          'Cache-Control': 'no-cache'
        },
        timeout: 5000,
      }
    )

    setHeader(event, 'Cache-Control', 'public, max-age=60')
    return data
  } catch (err: any) {
    console.error('Failed to fetch categories from backend:', err?.message)
    return []
  }
})