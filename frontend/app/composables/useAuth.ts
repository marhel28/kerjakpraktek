// composables/useAuth.ts
export const useAuth = () => {
  const token = useCookie('token')
  const refreshTokenCookie = useCookie('refresh_token')
  const userDataCookie = useCookie<any>('user_data')

  const refreshToken = async () => {
    try {
      const res: any = await $fetch('/api/refresh', {
        method: 'POST',
        body: { refresh_token: refreshTokenCookie.value },
      })
      token.value = res.access_token
      refreshTokenCookie.value = res.refresh_token
      return true
    } catch {
      return false
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await $fetch('/api/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token.value}` },
        })
      }
    } catch {
      console.warn('Logout API ditolak')
    } finally {
      try {
        const { useChatSocket } = await import('~/composables/useChatSocket')
        useChatSocket().disconnect()
      } catch { /* abaikan */ }
      try {
        const { usePesanStore } = await import('~/stores/UsePesanStore')
        usePesanStore().reset()
      } catch { /* abaikan */ }
      try {
        const { useNotificationSocket } = await import('~/composables/useNotificationSocket')
        useNotificationSocket().disconnect()
      } catch { /* abaikan */ }

      token.value = null
      refreshTokenCookie.value = null
      userDataCookie.value = null

      if (import.meta.client) {
        window.location.href = '/login'
      }
    }
  }

  return { refreshToken, logout }
}
