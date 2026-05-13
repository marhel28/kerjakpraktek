/**
 * server/api/login.post.ts
 * =========================
 * Login handler + ambil unread count sekali (one-shot) saat login.
 *
 * Rules:
 * - Setelah login sukses, hit /messages/unread SEKALI di server side
 * - Hasilnya dibalikkan ke FE dalam response { ..., initialUnread: N }
 * - FE (usePesanStore) langsung set unreadCount dari nilai ini — tanpa fetch extra
 * - Selanjutnya polling pasif (2 menit) yang jaga badge tetap segar
 */

import { defineEventHandler, readBody, setCookie, createError } from 'h3'
const config = useRuntimeConfig();
const BACKEND = config.public.apiBase

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  try {
    // ── 1. Login ke backend ────────────────────────────────────────
    const response: any = await $fetch(`${BACKEND}/auth/user/auth/login`, {
      method: 'POST',
      body: {
        email: body.email,
        password: body.password,
      },
    })

    const isProd = process.env.NODE_ENV === 'production'

    // ── 2. Set cookies ─────────────────────────────────────────────
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

    if (response.supabase?.access_token) {
      setCookie(event, 'sb_access_token', response.supabase.access_token, {
        maxAge: 60 * 60,
        path: '/',
        httpOnly: false,
        secure: isProd,
        sameSite: 'lax',
      })
    }

    if (response.supabase?.refresh_token) {
      setCookie(event, 'sb_refresh_token', response.supabase.refresh_token, {
        maxAge: 60 * 60 * 24 * 7,
        path: '/',
        httpOnly: false,
        secure: isProd,
        sameSite: 'lax',
      })
    }

    // ── 3. ONE-SHOT: ambil unread count pakai token yang baru didapat
    //    Dilakukan server-side agar FE langsung punya angka badge
    //    tanpa harus fetch sendiri setelah login.
    let initialUnread = 0
    if (response.access_token) {
      try {
        const unreadRes: any = await $fetch(`${BACKEND}/messages/unread`, {
          headers: { Authorization: `Bearer ${response.access_token}` },
        })
        initialUnread = unreadRes?.unread_count ?? 0
      } catch {
        // Jangan gagalkan login kalau endpoint pesan error
        initialUnread = 0
      }
    }

    // ── 4. Return ke FE ───────────────────────────────────────────
    return {
      success: true,
      message: 'Login berhasil',
      user: response.user,
      hasSupabase: !!response.supabase,
      initialUnread,   // ← FE langsung set ke store
    }

  } catch (error: any) {
    const msg =
      error.data?.detail ||
      error.data?.message ||
      'Email atau password salah.'

    throw createError({
      statusCode: error.response?.status || 401,
      message: msg,
    })
  }
})