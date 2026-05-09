import { cachedEventHandler } from 'nitro/runtime'

export default cachedEventHandler(async (event) => {
  const config = useRuntimeConfig()

  const data = await $fetch<any[]>(`${config.public.apiBase}/banner/`, {
    // Timeout agar tidak hang saat upstream lambat
    timeout: 5000,
  })

  // ─── Headers SEO-friendly ───────────────────────────────────────
  // s-maxage = CDN cache (Vercel/Cloudflare)
  // stale-while-revalidate = CDN sajikan cache lama sambil fetch baru
  // stale-if-error = CDN tetap sajikan cache lama saat upstream error
  setHeader(
    event,
    'Cache-Control',
    'public, max-age=60, s-maxage=300, stale-while-revalidate=600, stale-if-error=86400'
  )

  // ETag sederhana: jika data tidak berubah, browser/CDN skip download
  const etag = `"banner-${data?.length ?? 0}-${Date.now() % 60000}"`
  setHeader(event, 'ETag', etag)
  setHeader(event, 'Vary', 'Accept-Encoding')

  return data
}, {
  maxAge: 60,        // Nitro server cache: 60 detik
  staleMaxAge: 300,  // Sajikan stale selama 5 menit sambil revalidate
  getKey: () => 'banner:home', // Key eksplisit agar mudah di-invalidate
  shouldBypassCache: (event) => {
    // Bypass cache saat preview mode (mis. CMS preview)
    return getHeader(event, 'x-preview-mode') === '1'
  },
})