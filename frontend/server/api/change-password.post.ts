import { defineEventHandler, readBody, getRequestHeaders, createError } from 'h3'

const config = useRuntimeConfig()
const BACKEND = config.public.apiBase

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const headers = getRequestHeaders(event)
  const auth = headers.authorization || headers.Authorization

  if (!auth) {
    throw createError({ statusCode: 401, message: 'Unauthorized' })
  }

  try {
    const res = await $fetch(`${BACKEND}/auth/user/users/me/change-password`, {
      method: 'POST',
      headers: { Authorization: auth as string },
      body: { old_password: body.old_password, new_password: body.new_password },
    })
    return res
  } catch (e: any) {
    throw createError({
      statusCode: e?.response?.status || 400,
      message: e?.data?.detail || 'Gagal mengganti password.',
    })
  }
})
