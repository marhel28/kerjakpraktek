// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({

  runtimeConfig: {
    public: {
      apiBase: 'https://cctv-api.desa-sidomukti.com', 
      // http://127.0.0.1:8000 untuk devlops
      siteUrl: 'https://yourdomain.com',
      googleClientId: '',
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseKey: process.env.SUPABASE_ANON_KEY,
      adminSupabaseId:   process.env.NUXT_PUBLIC_ADMIN_SUPABASE_ID,
    }
  },

  future: {
    compatibilityVersion: 4,
  },

  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  css: [
    'leaflet/dist/leaflet.css',
    '~/assets/main.css',
  ],

  vite: {
    plugins: [
      tailwindcss()
    ],
    optimizeDeps: {
      include: ['leaflet']
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
    redirect: false,  // ← WAJIB false, kita pakai auth sistem sendiri
    types: './app/types/database.types.ts', 
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
    '/': { isr: 60 },
    // ── API cache ───────────────────────────────────────────────────
    '/api/peritems':       { cache: { maxAge: 60,  staleMaxAge: 300  } },
    '/api/recommendations':{ cache: { maxAge: 120, staleMaxAge: 600  } },
    '/api/banner':         { cache: { maxAge: 60,  staleMaxAge: 300  } },
    '/api/brands':         { cache: { maxAge: 30,  staleMaxAge: 120  } },
    '/api/getpopular':     { cache: { maxAge: 300, staleMaxAge: 600  } },

    // ── ISR ─────────────────────────────────────────────────────────
    '/product/**':  { isr: 60  },
    '/category/**': { isr: 300 },
    '/brands':      { isr: 30  },
    '/brands/**':   { isr: 60  },

    // ── Auth pages: COOP fix untuk Google GSI popup ─────────────────
    // Tanpa header ini Google Sign-In popup tidak bisa
    // postMessage balik ke parent window → error 400
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
    // Jika ada halaman forgot-password / reset-password yang pakai Google
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
  },

  fonts: {
    defaults: {
      weights: [400, 700, 900],
      styles: ['normal', 'italic'],
    },
  },

  build: {
    transpile: [
      'swiper'
    ]
  }
})