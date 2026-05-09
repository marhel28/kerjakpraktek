export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const query = getQuery(event)

  const qStr = String(query.q || "").trim()
  const type = String(query.type || "all")

  // 🔥 guard clause (already correct, tetap dipertahankan)
  if (qStr.length < 2) {
    return {
      items: [],
      categories: [],
      brands: [],
      suggestion: null
    }
  }

  try {
    // 🔥 FAST REQUEST OPTIMIZED
    const response: any = await $fetch(
      `${config.public.apiBase}/stok/public/autocomplete`,
      {
        query: {
          q: qStr,
          type
        },
        timeout: 3000,
        retry: 1
      }
    )

    return response?.data ?? {
      items: [],
      categories: [],
      brands: [],
      suggestion: null
    }

  } catch (error) {
    console.error("Smart Search Proxy Error:", error)

    return {
      items: [],
      categories: [],
      brands: [],
      suggestion: null
    }
  }
})