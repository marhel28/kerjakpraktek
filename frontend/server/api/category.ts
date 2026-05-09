export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()

  const data = await $fetch(
    `${config.public.apiBase}/category/`,
    {
      headers: {
        // optional: bypass cache dari backend proxy lain
        'Cache-Control': 'no-cache'
      }
    }
  )

  setHeader(event, 'Cache-Control', 'public, max-age=60')

  return data
})