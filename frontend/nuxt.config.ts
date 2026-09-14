import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({

  runtimeConfig: {
    supabaseUrl: process.env.SUPABASE_URL,
    supabaseKey: process.env.SUPABASE_ANON_KEY,
    adminSupabaseId: process.env.NUXT_PUBLIC_ADMIN_SUPABASE_ID,
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? (process.env.VERCEL ? 'https://cctv-api.desa-sidomukti.com' : 'http://localhost:8000'),
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL ?? 'http://localhost:3000',
      googleClientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID ?? '',
    }
  },

  future: {
    compatibilityVersion: 4,
  },

  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  experimental: {
    appManifest: false,
  },

  css: [
    '~/assets/main.css',
  ],

  // ✅ Vercel: preset otomatis terdeteksi, tapi eksplisit lebih aman
  nitro: {
    preset: process.env.VERCEL ? 'vercel' : 'node-server',
    storage: {
      cache: {
        driver: 'memory',
      },
    },
    prerender: {
      crawlLinks: false,
      routes: [],
    },
    compressPublicAssets: true,
    minify: true,
  },

  vite: {
    server: {
      headers: {
        'Cross-Origin-Opener-Policy': 'unsafe-none',
        'Cross-Origin-Embedder-Policy': 'unsafe-none',
      }
    },
    plugins: [
      tailwindcss()
    ],
    optimizeDeps: {
      include: ['leaflet']
    },
    build: {
      // ✅ Hindari chunk terlalu besar (Vercel limit ~50MB per function)
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          manualChunks: {
            leaflet: ['leaflet'],
            swiper: ['swiper', 'swiper/vue', 'swiper/modules'],
            vendor: ['@supabase/supabase-js'],
          }
        }
      }
    }
  },

  modules: [
    '@nuxt/fonts',
    '@nuxt/icon',
    '@nuxt/image',
    '@pinia/nuxt',
    '@nuxt/ui',
    '@nuxtjs/leaflet',
    "@nuxtjs/supabase",
    '@vueuse/motion/nuxt'
  ],

  supabase: {
    url: process.env.SUPABASE_URL,
    key: process.env.SUPABASE_ANON_KEY,
    redirect: false,
    types: 'app/types/database.types.ts',
    // ✅ Disable auto token refresh karena app punya JWT auth sendiri.
    // Ini menghilangkan error "Failed to fetch" dari Supabase saat offline/dev lokal.
    cookieOptions: {
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
    },
    clientOptions: {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
        detectSessionInUrl: false,
      }
    }
  },

  app: {
    head: {
      title: 'PasarCCTV - Jasa Pasang & Marketplace CCTV Terlengkap',
      htmlAttrs: {
        lang: 'id',
      },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Pusat kamera keamanan CCTV, IP Camera, Smart Home, NVR, DVR, dan aksesoris terlengkap. Layanan pasang CCTV profesional Jabodetabek & Bandung dengan garansi resmi.' },
        { name: 'keywords', content: 'cctv, pasang cctv, cctv murah, kamera keamanan, smart home, ip camera, cctv bandung, cctv jakarta' },
        { name: 'robots', content: 'index, follow' },
        { property: 'og:site_name', content: 'PasarCCTV' },
        { property: 'og:type', content: 'website' },
        { property: 'og:title', content: 'PasarCCTV - Jasa Pasang & Marketplace CCTV Terlengkap' },
        { property: 'og:description', content: 'Belanja perangkat CCTV berkualitas dan paket instalasi bergaransi resmi dengan harga terbaik di PasarCCTV.' },
        { property: 'og:image', content: '/pasarcctv.png' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: 'PasarCCTV - Jasa Pasang & Marketplace CCTV Terlengkap' },
        { name: 'twitter:description', content: 'Belanja perangkat CCTV berkualitas dan paket instalasi bergaransi resmi dengan harga terbaik di PasarCCTV.' },
        { name: 'twitter:image', content: '/pasarcctv.png' },
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
      ],
    },
  },

  routeRules: {
    // ✅ Static information pages — edge SWR cache
    '/about':        { swr: 3600 },
    '/contact':      { swr: 3600 },
    '/terms':        { swr: 3600 },
    '/privacy':      { swr: 3600 },

    // ✅ Edge caching with SWR for dynamic pages
    '/':             { swr: 300 },
    '/brands/**':    { swr: 600 },
    '/help/**':      { swr: 600 },
    '/store-locator':{ swr: 3600 },

    // ✅ Assets cache immutable
    '/_nuxt/**':     { headers: { 'Cache-Control': 'public, max-age=31536000, immutable' } },

    // ✅ API cache — pakai memory driver (sudah dikonfigurasi di atas)
    '/api/peritems':        { cache: { maxAge: 60,  staleMaxAge: 300 } },
    '/api/recommendations': { cache: { maxAge: 120, staleMaxAge: 600 } },
    '/api/banner':          { cache: { maxAge: 60,  staleMaxAge: 300 } },
    '/api/brands':          { cache: { maxAge: 30,  staleMaxAge: 120 } },
    '/api/getpopular':      { cache: { maxAge: 300, staleMaxAge: 600 } },

    // ✅ Auth pages: COOP fix untuk Google GSI popup
    '/login': {
      headers: {
        'Cross-Origin-Opener-Policy':   'unsafe-none',
        'Cross-Origin-Embedder-Policy': 'unsafe-none',
      },
    },
    '/daftar': {
      headers: {
        'Cross-Origin-Opener-Policy':   'unsafe-none',
        'Cross-Origin-Embedder-Policy': 'unsafe-none',
      },
    },
    '/forgot-password': {
      headers: {
        'Cross-Origin-Opener-Policy':   'unsafe-none',
        'Cross-Origin-Embedder-Policy': 'unsafe-none',
      },
    },
  },

  image: {
    format: ['webp', 'avif', 'png', 'jpg'],
    domains: [
      'daganghalal.blob.core.windows.net',
      'png.pngtree.com',
      'cdn.pixabay.com',
      'images.unsplash.com',
      'cdn.desa-sidomukti.com'
    ],
    screens: {
      xs: 320,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
    },
    provider: 'ipx',
    quality: 80,
    densities: [1, 2],
  },

  fonts: {
    families: [
      { name: 'Plus Jakarta Sans', provider: 'google', weights: [400, 500, 600, 700, 800, 900], subsets: ['latin'] },
      { name: 'Open Sans', provider: 'google', weights: [400, 600, 700], subsets: ['latin'] },
    ],
    defaults: {
      weights: [400, 500, 600, 700, 800, 900],
      styles: ['normal', 'italic'],
      subsets: ['latin'],
    },
  },

  build: {
    transpile: ['swiper']
  },

  vue: {
    config: {
      warnHandler() {}
    },
    compilerOptions: {
      isCustomElement: (tag) => tag.startsWith('swiper-')
    }
  }

})