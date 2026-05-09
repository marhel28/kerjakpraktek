// server/api/main-bottom.ts
export default defineEventHandler(async () => {
    const config = useRuntimeConfig()
    const url = `${config.public.apiBase}/main-bottom/public`
    const data = await $fetch(url)
    return data
  })