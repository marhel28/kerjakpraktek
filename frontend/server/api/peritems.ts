export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const uuid = query.uuid as string
  const slug = query.slug as string

  if (!uuid && !slug) {
    throw createError({
      statusCode: 400,
      statusMessage: "Identifier (uuid or slug) is required"
    })
  }

  const config = useRuntimeConfig()
  
  // Endpoint backend fleksibel: prioritaskan UUID, fallback ke Slug
  const endpoint = uuid 
    ? `${config.public.apiBase}/stok/public/detail/${uuid}`
    : `${config.public.apiBase}/stok/public/detail/slug/${slug}`

  try {
    const response = await $fetch(endpoint, {
        timeout: 5000,
        retry: 1
      }
    )

    if (!response) {
      throw createError({
        statusCode: 404,
        statusMessage: "Produk tidak ditemukan"
      })
    }

    return response

  } catch (error: any) {

    console.error("PRODUCT DETAIL ERROR:", {
      message: error?.message,
      status: error?.response?.status,
      data: error?.response?._data
    })

    const status = error?.response?.status

    if (status === 404) {
      throw createError({
        statusCode: 404,
        statusMessage: "Produk tidak ditemukan"
      })
    }

    throw createError({
      statusCode: status || 500,
      statusMessage: error?.message || "Backend error"
    })
  }
})