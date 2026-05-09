export default cachedEventHandler(async (event) => {
  const config = useRuntimeConfig()

  try {
    const response = await $fetch<{
      status: string
      source: string
      data: string[]
    }>(`${config.public.apiBase}/stok/public/trending-searches`, {
      timeout: 5000,
      retry: 1,
    })

    return response?.data ?? []

  } catch (error) {
    console.warn(
      "[Nuxt BFF] Trending fallback triggered",
      error
    )

    return [
      "CCTV outdoor",
      "paket murah",
      "kamera wifi",
      "dahua 2mp",
      "dvr 8 channel"
    ]
  }
}, {
  name: "trending-searches",

  // 🔥 CACHE KEY STATIC (global trending)
  getKey: () => "trending:searches",

  // 🔥 CACHE 1 JAM (sesuai kebutuhan kamu)
  maxAge: 3600,        // 1 jam fresh cache
  staleMaxAge: 7200,   // 2 jam fallback cache

  // 🔥 SWR tetap aktif biar UX instant
  swr: true
})