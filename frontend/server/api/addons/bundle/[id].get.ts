export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id') || ""
  const query = getQuery(event)
  const category_slug = query.category_slug as string

  if (!id || !category_slug) {
    return { success: false, data: [] }
  }

  const config = useRuntimeConfig()
  const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);

  try {
    const endpoint = isUuid 
      ? `${config.public.apiBase}/addons/bundle/${id}`
      : `${config.public.apiBase}/addons/bundle/slug/${id}`

    const response = await $fetch(endpoint, {
        query: { category_slug },
        timeout: 5000,
        retry: 1
      }
    )
    return response
  } catch (error: any) {
    console.error("ADDON BUNDLE ERROR:", error?.message)
    return { success: false, data: [] }
  }
})
