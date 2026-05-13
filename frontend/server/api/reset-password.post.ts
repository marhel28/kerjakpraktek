import { defineEventHandler, readBody, createError } from 'h3'

const config = useRuntimeConfig()
const BACKEND = config.public.apiBase

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  try {
    const res = await $fetch(`${BACKEND}/auth/user/auth/reset-password`, {
      method: 'POST',
      body: { token: body.token, new_password: body.new_password },
    })
    return res
  } catch (e: any) {
    throw createError({
      statusCode: e?.response?.status || 400,
      message: e?.data?.detail || 'Link tidak valid atau sudah kadaluarsa.',
    })
  }
})
