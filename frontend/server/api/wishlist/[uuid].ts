import {
  defineEventHandler,
  getRouterParam,
  getCookie,
  createError,
} from "h3"

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
          timeout: 5000,
        }
      )

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