// server/api/refresh.post.ts
import { defineEventHandler, getCookie, setCookie, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const refreshToken = getCookie(event, 'refresh_token')
  const config = useRuntimeConfig()
  if (!refreshToken) {
    throw createError({ statusCode: 401, message: 'No refresh token' })
  }

  try {
    const response: any = await $fetch(`${config.public.apiBase}/auth/user/auth/refresh`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${refreshToken}`,
      },
    })

    const isProd = process.env.NODE_ENV === 'production'

    if (response.access_token) {
      setCookie(event, 'token', response.access_token, {
        maxAge: 60 * 60 * 24 * 7,
        path: '/',
        httpOnly: false,
        secure: isProd,
        sameSite: 'lax',
      })
    }

    if (response.refresh_token) {
      setCookie(event, 'refresh_token', response.refresh_token, {
        maxAge: 60 * 60 * 24 * 30,
        path: '/',
        httpOnly: true,
        secure: isProd,
        sameSite: 'lax',
      })
    }

    return { success: true, access_token: response.access_token }

  } catch (error: any) {
    throw createError({ statusCode: 401, message: 'Refresh token expired' })
  }
})