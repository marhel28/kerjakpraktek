export default cachedEventHandler(async (event) => {
  const config = useRuntimeConfig()

  try {
    const data = await $fetch(`${config.public.apiBase}/brands/`, {
      timeout: 5000,
      retry: 1,
    })

    return data

  } catch (error) {
    console.error("Logo banner error:", error)

    // fallback aman biar UI tidak kosong
    return []
  }
}, {
  name: "logobanner",

  // 🔥 cache key static (global data)
  getKey: () => "logobanner:brands",

  // 🔥 CACHE LEBIH AGRESIF (karena jarang berubah)
  maxAge: 3600,        // 1 jam fresh cache
  staleMaxAge: 86400,  // 1 hari fallback cache

  // 🔥 SWR biar instant UI
  swr: true
})