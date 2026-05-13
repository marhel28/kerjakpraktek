import {
  defineEventHandler,
  readBody,
  getCookie,
  createError,
} from "h3"

const cache = new Map<string, { data: any; expire: number }>()

export default defineEventHandler(async (event) => {
  const method = event.node.req.method
  const config = useRuntimeConfig()
  const token = getCookie(event, "token")

  // =========================
  // ❌ NO TOKEN → FAST EXIT
  // =========================
  if (!token) {
    if (method === "GET") return []
    throw createError({
      statusCode: 401,
      statusMessage: "Unauthorized",
    })
  }

  const headers = {
    Authorization: `Bearer ${token}`,
  }

  // =========================
  // 🔥 GET (CACHED + FAST)
  // =========================
  if (method === "GET") {
    const cacheKey = `wishlist:${token}`
    const now = Date.now()

    // ✔ return cache kalau masih valid
    const cached = cache.get(cacheKey)
    if (cached && cached.expire > now) {
      return cached.data
    }

    try {
      const data = await $fetch(`${config.public.apiBase}/wishlist`, {
        headers,
        timeout: 10000,
      })

      // ✔ simpan cache 30 detik
      cache.set(cacheKey, {
        data,
        expire: now + 30 * 1000,
      })

      return data
    } catch (error) {
      console.error("Wishlist GET error:", error)
      return []
    }
  }

  // =========================
  // 🔥 POST (NO CACHE)
  // =========================
  if (method === "POST") {
    const body = await readBody(event)

    try {
      const result = await $fetch(`${config.public.apiBase}/wishlist`, {
        method: "POST",
        headers,
        body,
        timeout: 10000,
      })

      // ❌ invalidate cache setelah update
      cache.delete(`wishlist:${token}`)

      return result
    } catch (error: any) {
      throw createError({
        statusCode: error?.response?.status || 500,
        statusMessage: error?.message || "Wishlist error",
      })
    }
  }

  // =========================
  // ❌ METHOD NOT ALLOWED
  // =========================
  throw createError({
    statusCode: 405,
    statusMessage: "Method not allowed",
  })
})