export default cachedEventHandler(async (event) => {
  const query = getQuery(event)
  const stock_uuid = query.uuid as string

  if (!stock_uuid) {
    throw createError({ statusCode: 400, statusMessage: 'UUID is required' })
  }

  const config = useRuntimeConfig()

  try {
    // 🔥 OPTIMASI 1: pakai $fetch native + timeout
    return await $fetch(`${config.public.apiBase}/stok/public/detail/${stock_uuid}`, {
      timeout: 5000, // cegah hanging request
      retry: 1,       // retry ringan
    })

  } catch (error: any) {
    // 🔥 OPTIMASI 2: bedakan error network vs not found
    const status = error?.response?.status

    if (status === 404) {
      throw createError({ statusCode: 404, statusMessage: 'Produk tidak ditemukan' })
    }

    throw createError({ statusCode: 500, statusMessage: 'Backend error' })
  }
}, {
  name: 'product-detail-cache',

  // 🔥 OPTIMASI 3: cache key lebih aman + ringan
  getKey: (event) => {
    const uuid = getQuery(event).uuid
    return `product:${uuid}` // prefix biar tidak collision
  },

  // 🔥 OPTIMASI 4: naikkan cache lifetime (ini paling ngaruh)
  maxAge: 300, // 5 menit (lebih stabil dari 60 detik)

  // 🔥 OPTIMASI 5: SWR tetap aktif
  swr: true
})