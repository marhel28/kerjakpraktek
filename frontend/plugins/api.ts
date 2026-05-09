export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  
  const token = useCookie('token')
  const refreshToken = useCookie('refresh_token')

  const api = $fetch.create({
    baseURL: config.public.apiBase,

    // =========================
    // REQUEST: inject token
    // =========================
    onRequest({ options }) {
      if (token.value) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token.value}`,
        }
      }
    },

    // =========================
    // RESPONSE ERROR
    // =========================
    async onResponseError({ request, options, response }) {
      // hanya handle unauthorized
      if (response.status !== 401) {
        return
      }

      // 🔥 CEGAH LOOPING: Abaikan 401 jika request-nya mengarah ke logout atau refresh
      const reqUrl = request.toString()
      if (reqUrl.includes('/logout') || reqUrl.includes('/refresh')) {
        return 
      }

      console.warn('401 → trying refresh token...')

      try {
        if (!refreshToken.value) throw new Error('No refresh token')

        // =========================
        // CALL REFRESH
        // =========================
        const res: any = await $fetch('/api/refresh', {
          method: 'POST',
          body: {
            refresh_token: refreshToken.value,
          },
        })

        // =========================
        // UPDATE COOKIES
        // =========================
        token.value = res.access_token
        refreshToken.value = res.refresh_token

        // =========================
        // RETRY ORIGINAL REQUEST
        // =========================
        return await $fetch(request, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${res.access_token}`,
          },
        })

      } catch (err) {
        console.warn('Refresh gagal → hapus sesi')

        // clear cookies
        token.value = null
        refreshToken.value = null

        // 🔥 Redirect aman, hindari error SSR router.push
        if (import.meta.client) {
          window.location.href = '/login'
        }
      }
    },
  })

  return {
    provide: {
      api,
    },
  }
})