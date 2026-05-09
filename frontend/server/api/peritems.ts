export default cachedEventHandler(async (event) => {
  const query = getQuery(event)
  const stock_uuid = query.uuid as string

  if (!stock_uuid) {
    throw createError({ statusCode: 400, statusMessage: "UUID is required" })
  }

  const config = useRuntimeConfig()

  try {
    // 🔥 FAST FETCH (backend tetap source of truth)
    const response: any = await $fetch(
      `${config.public.apiBase}/stok/public/detail/${stock_uuid}`,
      {
        timeout: 5000,
        retry: 1,
      }
    )

    return response

  } catch (error: any) {
    const status = error?.response?.status

    if (status === 404) {
      throw createError({ statusCode: 404, statusMessage: "Produk tidak ditemukan" })
    }

    throw createError({ statusCode: 500, statusMessage: "Backend error" })
  }
}, {
  name: "product-detail-cache",

  // 🔥 cache per produk (aman & scalable)
  getKey: (event) => `product:${getQuery(event).uuid}:v2`,

  // 🔥 SHORT CACHE (karena sering berubah)
  maxAge: 30,          // 30 detik fresh cache
  staleMaxAge: 120,    // 2 menit fallback

  // 🔥 SWR penting untuk UX
  swr: true
})