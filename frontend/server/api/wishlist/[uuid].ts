import {
  defineEventHandler,
  getRouterParam,
  getCookie,
  createError,
} from "h3"

// Shared cache dengan index.ts
const cache = (globalThis as any).__wishlistCache ??= new Map<string, { data: any; expire: number }>()

export default defineEventHandler(async (event) => {
  const method = event.node.req.method
  const config = useRuntimeConfig()
  const token = getCookie(event, "token")
  const wishlistUuid = getRouterParam(event, "uuid")

  // =========================
  // ❌ VALIDATION SAFETY
  // =========================
  if (!token) {
    throw createError({
      statusCode: 401,
      statusMessage: "Unauthorized",
    })
  }

  if (!wishlistUuid) {
    throw createError({
      statusCode: 400,
      statusMessage: "Wishlist UUID required",
    })
  }

  const headers = {
    Authorization: `Bearer ${token}`,
  }

  // =========================
  // 🔥 DELETE
  // =========================
  if (method === "DELETE") {
    try {
      const result = await $fetch(
        `${config.public.apiBase}/wishlist/${wishlistUuid}`,
        {
          method: "DELETE",
          headers,
          timeout: 10000,
        }
      )

      // Invalidate wishlist GET cache agar item tidak muncul lagi
      cache.delete(`wishlist:${token}`)

      return result
    } catch (error: any) {
      throw createError({
        statusCode: error?.response?.status || 500,
        statusMessage: error?.data?.detail || error.message || "Delete failed",
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