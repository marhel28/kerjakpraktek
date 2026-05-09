export default cachedEventHandler(async (event) => {
  const config = useRuntimeConfig()

  try {
    // 🔥 FAST FETCH (backend hanya fallback)
    const data = await $fetch(
      `${config.public.apiBase}/stok/public/megamenu-collections`,
      {
        timeout: 5000,
        retry: 1,
      }
    )

    return data

  } catch (error) {
    console.error("API Error Megamenu:", error)

    // 🔥 fallback agar UI tetap hidup
    return {
      status: "error",
      data: []
    }
  }
}, {
  name: "megamenu-collections",

  // 🔥 CACHE KEY STATIC (karena global data)
  getKey: () => "megamenu:collections",

  // 🔥 CACHE SUPER AGRESIF (INI KUNCI SPEED)
  maxAge: 3600 * 6,      // 6 jam memory cache
  staleMaxAge: 86400,    // 1 hari fallback cache

  // 🔥 SWR tetap aktif (instant render)
  swr: true
})