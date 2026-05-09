export default cachedEventHandler(async (event) => {
  const config = useRuntimeConfig()

  try {
    // 🔥 IMPORTANT: fetch super light (no retry in SSR path)
    const response: any = await $fetch(
      `${config.public.apiBase}/stok/public/brand-showcase`
    )

    // 🔥 return minimal payload only
    return response?.data ?? []

  } catch (error) {
    console.error("Brands fetch error:", error)
    return []
  }
}, {
  name: "brands-showcase",

  // 🔥 static cache key (GOOD)
  getKey: () => "brands:showcase",

  // 🔥 lebih agresif cache (biar SSR hampir tidak pernah hit API)
  maxAge: 600,        // 10 menit (lebih stabil dari 5 menit)
  staleMaxAge: 86400, // 1 hari fallback

  // 🔥 tetap aktifkan SWR
  swr: true
})