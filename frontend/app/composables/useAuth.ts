// composables/useAuth.ts
import { useSupabaseClient } from '#imports'

export const useAuth = () => {
  const token = useCookie('token')
  const refreshTokenCookie = useCookie('refresh_token')
  const userDataCookie = useCookie<any>('user_data')
  const sbAccessToken = useCookie('sb_access_token')
  const sbRefreshToken = useCookie('sb_refresh_token')
  const supabaseUserId = useCookie('supabase_user') // 🆕 Cookie baru

  // 🎯 Ambil Supabase User ID langsung dari cookie (NO DECODE!)
  const getSupabaseUserId = (): string => {
    const id = supabaseUserId.value
    if (id) {
      return id
    }
    return ''
  }

  const setSupabaseSession = async () => {
    if (!sbAccessToken.value || !sbRefreshToken.value) return
    try {
      const supabase = useSupabaseClient()
      const { data, error } = await supabase.auth.setSession({
        access_token: sbAccessToken.value,
        refresh_token: sbRefreshToken.value,
      })
      
      if (error) {
        return false
      }
      
     
      
      // 🆕 Simpan user ID ke cookie
      if (data.user?.id) {
        supabaseUserId.value = data.user.id
        console.log('💾 Saved supabase_user cookie:', data.user.id)
      }
      
      return true
    } catch (err) {
      console.error('❌ Error:', err)
      return false
    }
  }

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
      // Clear semua cookies
      token.value = null
      refreshTokenCookie.value = null
      userDataCookie.value = null
      sbAccessToken.value = null
      sbRefreshToken.value = null
      supabaseUserId.value = null // 🆕 Clear juga

      if (import.meta.client) {
        try {
          const supabase = useSupabaseClient()
          await supabase.auth.signOut()
        } catch {}
        window.location.href = '/login'
      }
    }
  }

  return {
    getSupabaseUserId,
    setSupabaseSession,
    refreshToken,
    logout,
  }
}