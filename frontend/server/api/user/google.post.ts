export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const config = useRuntimeConfig();

  try {
    // PERBAIKAN DI SINI: URL yang benar sesuai router FastAPI Anda
    const response: any = await $fetch(`${config.public.apiBase}/auth/user/auth/google`, {
      method: "POST",
      body: {
        id_token: body.id_token,
      },
    });

    // Set cookie
    setCookie(event, "token", response.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production', // Jangan paksa secure di localhost (HTTP)
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60, // 1 jam
    });

    setCookie(event, "refresh_token", response.refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });

    return response;
  } catch (err: any) {
    console.error("Nitro Google Auth Error:", err.data || err.message);
    throw createError({
      statusCode: 401,
      statusMessage: err?.data?.detail || "Google login failed",
    });
  }
});