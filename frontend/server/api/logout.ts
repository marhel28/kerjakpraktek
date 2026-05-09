import { defineEventHandler, getHeader, deleteCookie } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const authHeader = getHeader(event, 'authorization')

  if (authHeader) {
    try {
      await $fetch(`${config.public.apiBase}/auth/user/auth/logout`, { 
        method: 'POST',
        headers: {
          Authorization: authHeader
        }
      })
    } catch (error: any) {
      // 🔥 PERBAIKAN: Kita abaikan error 401 karena itu hal yang wajar 
      // (artinya token sudah mati duluan di backend).
      // Kita hanya log jika errornya selain 401 (misal 500 Server Down).
      if (error.statusCode !== 401) {
        console.warn('Backend FastAPI gagal memproses logout:', error.message)
      }
    }
  }

  // Hapus cookie sesi
  deleteCookie(event, 'token', { path: '/' }) 
  deleteCookie(event, 'refresh_token', { path: '/' }) // Tambahkan ini agar refresh token juga bersih
  deleteCookie(event, 'user_data', { path: '/' }) // Atau 'user', sesuaikan dengan namamu

  return {
    success: true,
    message: 'Sesi dibersihkan.'
  }
})