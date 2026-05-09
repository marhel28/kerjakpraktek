import { defineEventHandler, getQuery, createError } from 'h3'

export default defineEventHandler(async (event) => {
  // 1. Ambil token dari query URL frontend
  const query = getQuery(event)
  const token = query.token

  if (!token) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Token verifikasi tidak ditemukan.'
    })
  }

  // 2. Base URL FastAPI (Sebaiknya gunakan runtimeConfig di nuxt.config.ts)
  // config.public.apiBase atau config.apiSecret
  const backendUrl = 'http://127.0.0.1:8000/auth/user/auth/verify-email'

  try {
    // 3. Tembak ke Backend FastAPI
    const response = await $fetch(backendUrl, {
      method: 'GET',
      params: { token }
    })

    // Kembalikan response sukses ke frontend
    return response

  } catch (error: any) {
    // 4. Tangkap dan teruskan pesan error dari FastAPI ke Frontend
    const statusCode = error.response?.status || 500
    // Ambil pesan 'detail' dari schema error bawaan FastAPI
    const errorMessage = error.response?._data?.detail || 'Terjadi kesalahan pada server saat verifikasi.'

    throw createError({
      statusCode: statusCode,
      message: errorMessage
    })
  }
})