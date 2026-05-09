export async function apiFetch(event, url: string, options: any = {}) {
    const config = useRuntimeConfig()
  
    let accessToken = getCookie(event, "access_token")
    let refreshToken = getCookie(event, "refresh_token")
  
    // 🔥 function untuk hit backend
    const doRequest = async (token: string | null) => {
      return await $fetch(url, {
        baseURL: config.public.backendUrl,
        ...options,
        headers: {
          ...(options.headers || {}),
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      })
    }
  
    try {
      // 🚀 request pertama
      return await doRequest(accessToken)
  
    } catch (err: any) {
      // 🔥 kalau token expired
      if (err?.response?.status === 401 && refreshToken) {
        try {
          // 🔁 call refresh API
          const refreshRes: any = await $fetch("/auth/refresh", {
            baseURL: config.public.backendUrl,
            method: "POST",
            body: { refresh_token: refreshToken }
          })
  
          // ✅ simpan token baru
          setCookie(event, "access_token", refreshRes.access_token, {
            httpOnly: true,
            secure: true,
            sameSite: "lax"
          })
  
          setCookie(event, "refresh_token", refreshRes.refresh_token, {
            httpOnly: true,
            secure: true,
            sameSite: "lax"
          })
  
          // 🔁 retry request pakai token baru
          return await doRequest(refreshRes.access_token)
  
        } catch (refreshErr) {
          // ❌ refresh gagal → logout
          deleteCookie(event, "access_token")
          deleteCookie(event, "refresh_token")
  
          throw createError({
            statusCode: 401,
            statusMessage: "Session expired"
          })
        }
      }
  
      throw err
    }
  }