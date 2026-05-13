export default defineEventHandler(async (event) => {
  const product_uuid = getRouterParam(event, 'id')
  const query = getQuery(event)
  const category_slug = query.category_slug as string

  if (!product_uuid || !category_slug) {
    return { success: false, data: [] }
  }

  const config = useRuntimeConfig()

  try {
    const response = await $fetch(
      `${config.public.apiBase}/addons/bundle/${product_uuid}`,
      {
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
