export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()

  const path = event.context.params?.path || ''
  const method = event.method

  const query = getQuery(event)

  let body: any

  if (['POST', 'PUT', 'PATCH'].includes(method)) {
    body = await readBody(event)
  }

  const queryStr = Object.keys(query).length
    ? `?${new URLSearchParams(query as Record<string, string>).toString()}`
    : ''

  const url = `${config.public.apiBase}/services/${path}${queryStr}`

  try {
    return await $fetch(url, {
      method: method as any,

      body,

      headers: {
        ...(getHeader(event, 'cookie')
          ? { cookie: getHeader(event, 'cookie')! }
          : {}),

        ...(getHeader(event, 'authorization')
          ? { authorization: getHeader(event, 'authorization')! }
          : {}),
      },

      timeout: 10000,
    })
  } catch (error: any) {
    console.error('[API Proxy Error]', error)

    throw createError({
      statusCode: error?.statusCode || 500,
      statusMessage:
        error?.statusMessage || 'Internal Server Error',
      data: error?.data || null,
    })
  }
})