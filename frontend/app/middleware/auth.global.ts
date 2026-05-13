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
    to.path.startsWith('/wishlist') ||
    isPromoDetail

  const isAuthPage =
    to.path === '/login' ||
    to.path === '/daftar'

  // 🔒 protect route
  if (!token.value && isProtected) {
    return navigateTo('/login')
  }

  // 🔥 expired token
  if (token.value && isTokenExpired(token.value)) {
    const success = await refreshToken()

    if (!success) {
      token.value = null
      refreshTokenCookie.value = null
      user.value = null

      if (to.path !== '/') {
        return navigateTo('/')
      }
    }
  }

  // ✅ user sudah login buka halaman auth
  if (token.value && isAuthPage) {
    setPageLayout('auth')

    // atau redirect
    return navigateTo('/')
  }
})