import { defineEventHandler, readBody, setCookie, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const config = useRuntimeConfig()
  const BACKEND = config.public.apiBase

  try {
    const response: any = await $fetch(`${BACKEND}/auth/user/auth/google`, {
      method: 'POST',
      body: {
        id_token: body.id_token,
      },
    })

    const isProd = process.env.NODE_ENV === 'production'

    // ── 2. Set cookies (sama persis dengan login.post.ts) ───────────
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

    if (response.user) {
      setCookie(event, 'user_data', JSON.stringify(response.user), {
        maxAge: 60 * 60 * 24 * 7,
        path: '/',
        httpOnly: false,
        secure: isProd,
        sameSite: 'lax',
      })
    }

    // ── 3. ONE-SHOT: ambil unread count pakai token yang baru didapat
    let initialUnread = 0
    if (response.access_token) {
      try {
        const unreadRes: any = await $fetch(`${BACKEND}/messages/unread`, {
          headers: { Authorization: `Bearer ${response.access_token}` },
        })
        initialUnread = unreadRes?.unread_count ?? 0
      } catch {
        initialUnread = 0
      }
    }

    // ── 4. Return ke FE
    return {
      success: true,
      message: 'Login Google berhasil',
      user: response.user,
      initialUnread,
    }

  } catch (err: any) {
    console.error("Nitro Google Auth Error:", err.data || err.message);
    throw createError({
      statusCode: err.response?.status || 401,
      message: err?.data?.detail || err?.data?.message || "Google login failed",
    });
  }
})