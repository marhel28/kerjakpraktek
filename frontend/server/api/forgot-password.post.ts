import { defineEventHandler, readBody, createError } from 'h3'

const config = useRuntimeConfig()
const BACKEND = config.public.apiBase

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  try {
    const res = await $fetch(`${BACKEND}/auth/user/auth/forgot-password`, {
      method: 'POST',
      body: { email: body.email },
    })
    return res
  } catch (e: any) {
    throw createError({
      statusCode: e?.response?.status || 500,
      message: e?.data?.detail || 'Terjadi kesalahan. Coba lagi.',
    })
  }
})
