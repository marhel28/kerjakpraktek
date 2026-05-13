import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({

  runtimeConfig: {
    supabaseUrl: process.env.SUPABASE_URL,
    supabaseKey: process.env.SUPABASE_ANON_KEY,
    adminSupabaseId: process.env.NUXT_PUBLIC_ADMIN_SUPABASE_ID,
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL ?? 'http://localhost:3000',
      googleClientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID ?? '',
    }
  },

  future: {
    compatibilityVersion: 4,
  },

  compatibilityDate: '2025-07-15',
  // devtools: { enabled: false }, // ✅ Matikan di production

  css: [
    'leaflet/dist/leaflet.css',
    '~/assets/main.css',
  ],

  // ✅ Vercel: preset otomatis terdeteksi, tapi eksplisit lebih aman
  nitro: {
    preset: 'vercel',
    storage: {
      cache: {
        driver: 'memory', // ✅ Vercel tidak punya persistent filesystem
      },
    },
    // ✅ Vercel Edge/Serverless — pastikan bundle tidak terlalu besar
    minify: true,
  },

  vite: {
    server: {
      headers: {
        'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
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
    "@nuxtjs/supabase"
  ],

  supabase: {
    url: process.env.SUPABASE_URL,
    key: process.env.SUPABASE_ANON_KEY,
    redirect: false,
    types: 'app/types/database.types.ts',
  },

  app: {
    head: {
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
      ],
    },
  },

  routeRules: {
    // ✅ API cache — pakai memory driver (sudah dikonfigurasi di atas)
    '/api/peritems':        { cache: { maxAge: 60,  staleMaxAge: 300 } },
    '/api/recommendations': { cache: { maxAge: 120, staleMaxAge: 600 } },
    '/api/banner':          { cache: { maxAge: 60,  staleMaxAge: 300 } },
    '/api/brands':          { cache: { maxAge: 30,  staleMaxAge: 120 } },
    '/api/getpopular':      { cache: { maxAge: 300, staleMaxAge: 600 } },

    // ✅ Auth pages: COOP fix untuk Google GSI popup
    '/login': {
      headers: {
        'Cross-Origin-Opener-Policy':   'same-origin-allow-popups',
        'Cross-Origin-Embedder-Policy': 'unsafe-none',
      },
    },
    '/daftar': {
      headers: {
        'Cross-Origin-Opener-Policy':   'same-origin-allow-popups',
        'Cross-Origin-Embedder-Policy': 'unsafe-none',
      },
    },
    '/forgot-password': {
      headers: {
        'Cross-Origin-Opener-Policy':   'same-origin-allow-popups',
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
    defaults: {
      weights: [400, 700, 900],
      styles: ['normal', 'italic'],
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