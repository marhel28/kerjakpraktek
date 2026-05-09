import { isTokenExpired } from '@/utils/auth'

export default defineNuxtRouteMiddleware(async (to) => {
  const token = useCookie('token')
  const refreshTokenCookie = useCookie('refresh_token')
  const user = useCookie('user_data') 

  const { refreshToken } = useAuth()
  const isPromoDetail = to.name === 'promo-id'
  const isProtected =
  to.path.startsWith('/dashboard') ||
  to.path.startsWith('/orders') ||
  to.path.startsWith('/payment') ||
  isPromoDetail
  // 1. 🔒 protect route
  if (!token.value && isProtected) {
    return navigateTo('/login')
  }

  // 2. 🔁 redirect login page jika sudah login
  if (token.value && (to.path === '/login' || to.path === '/daftar')) {
    return navigateTo('/')
  }

  // 3. 🔥 expired check
  if (token.value && isTokenExpired(token.value)) {
    const success = await refreshToken()

    // JIKA REFRESH GAGAL
    if (!success) {
      // BERSIHKAN COOKIE SECARA LOKAL
      token.value = null
      refreshTokenCookie.value = null
      user.value = null

      // 🔥 PERBAIKAN: Redirect ke '/' hanya jika user tidak sedang di '/'
      if (to.path !== '/') {
        return navigateTo('/') 
      }
      // Jika to.path === '/', tidak perlu return navigateTo, 
      // Nuxt akan otomatis membiarkan user stay di halaman ini sebagai Guest.
    }
  }
})