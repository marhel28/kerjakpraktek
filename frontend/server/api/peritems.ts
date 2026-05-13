export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const stock_uuid = query.uuid as string

  if (!stock_uuid) {
    throw createError({
      statusCode: 400,
      statusMessage: "UUID is required"
    })
  }

  const config = useRuntimeConfig()

  try {
    const response = await $fetch(
      `${config.public.apiBase}/stok/public/detail/${stock_uuid}`,
      {
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