<script setup lang="ts">
/**
 * pages/about-us/index.vue
 * Tema: dark editorial – konsisten dengan pages/portfolio/index.vue
 * Data: ditarik dari server/api/about.ts → FastAPI → Redis cache
 */

import { ref, computed } from "vue";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Pagination, Autoplay } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";

// ── Types (mirroring backend schemas/about.py) ───────────────────
interface StatItem {
  id: string;
  value: string;
  label: string;
  order: number;
}

interface ValueItem {
  id: string;
  icon: string;
  title: string;
  desc: string;
  order: number;
}

interface GalleryItem {
  id: string;
  cdn_url: string;
  alt: string;
  order: number;
}

interface AboutPageData {
  id: string;
  is_active: boolean;
  hero_badge_text: string;
  hero_heading: string;
  hero_subheading: string | null;
  cta_heading: string;
  cta_body: string | null;
  cta_primary_text: string;
  cta_secondary_text: string;
  cta_secondary_url: string;
  stats: StatItem[];
  values: ValueItem[];
  gallery: GalleryItem[];
}

// ── SEO ──────────────────────────────────────────────────────────
const siteUrl = useRuntimeConfig().public.siteUrl ?? "https://pasarcctv.com";

useSeoMeta({
  title: "Tentang PasarCctv | Spesialis Pemasangan CCTV Premium",
  description:
    "Berhenti bertaruh pada keamanan aset Anda. PasarCctv memberikan instalasi standar enterprise, rapi, tanpa blind-spot, dan bergaransi ganti baru.",
  ogTitle: "Investasi Ketenangan Pikiran bersama PasarCctv",
  ogDescription:
    "Lebih dari 1,200 titik terpasang sempurna. Kami mendesain sistem keamanan yang bekerja 24/7 tanpa henti.",
  ogImage: "/images/about-og.jpg",
  robots: "index, follow",
});

useHead({
  link: [{ rel: "canonical", href: `${siteUrl}/about-us` }],
  script: [
    {
      type: "application/ld+json",
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        name: "PasarCctv",
        description:
          "Layanan instalasi sistem keamanan dan CCTV profesional standar enterprise.",
        url: `${siteUrl}/about-us`,
        telephone: "+6281234567890",
        priceRange: "$$",
        address: {
          "@type": "PostalAddress",
          addressLocality: "Indonesia",
          addressCountry: "ID",
        },
      }),
    },
  ],
});

// ── Data fetch (via Nitro proxy → FastAPI → Redis) ────────────────
const { data, status } = await useFetch<AboutPageData>("/api/about", {
  lazy: false,
});

const isPending = computed(() => status.value === "pending");

const swiperModules = [Pagination, Autoplay];

// ── Icon map lucide → inline SVG path ────────────────────────────
// Karena di portfolio tidak pakai Nuxt Icon, kita pakai inline SVG
const iconPaths: Record<string, string> = {
  "lucide:shield-alert": "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zM12 8v4M12 16h.01",
  "lucide:zap": "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
  "lucide:badge-check":
    "M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76zM9 12l2 2 4-4",
  "lucide:smartphone":
    "M17 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zM12 18h.01",
  "lucide:shield-check": "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zM9 12l2 2 4-4",
  "lucide:eye":
    "M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
  "lucide:lock":
    "M19 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2zM7 11V7a5 5 0 0 1 10 0v4",
  "lucide:camera":
    "M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2zM12 17a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
};

function getIconPath(name: string): string {
  return iconPaths[name] ?? iconPaths["lucide:shield-check"];
}

// ── Fallback data (kalau API belum ada) ──────────────────────────
const fallbackStats: StatItem[] = [
  { id: "1", value: "1,200+", label: "Kamera Aktif", order: 0 },
  { id: "2", value: "500+", label: "Klien Terlindungi", order: 1 },
  { id: "3", value: "100%", label: "Kabel Dalam Pipa", order: 2 },
  { id: "4", value: "1 Thn", label: "Garansi Ganti Baru", order: 3 },
];

const fallbackValues: ValueItem[] = [
  {
    id: "1",
    icon: "lucide:shield-alert",
    title: "Zero Blind-Spot Design",
    desc:
      "Kami mensimulasikan sudut pandang kamera untuk memastikan tidak ada celah bagi penyusup yang luput dari pantauan.",
    order: 0,
  },
  {
    id: "2",
    icon: "lucide:zap",
    title: "Kelistrikan Anti-Sabotase",
    desc:
      "Instalasi kabel menggunakan jalur tertutup (conduit) yang mustahil dipotong sembarangan.",
    order: 1,
  },
  {
    id: "3",
    icon: "lucide:badge-check",
    title: "Hanya Barang Original",
    desc:
      "Kami menjamin 100% keaslian perangkat Hikvision, Dahua, dll. Firmware bisa di-update resmi, anti-hack, bergaransi pabrik.",
    order: 2,
  },
  {
    id: "4",
    icon: "lucide:smartphone",
    title: "Pantau Dari Genggaman",
    desc:
      "Kami pastikan sistem terhubung ke HP Anda sebelum teknisi pulang. Pantau aset berharga dari mana saja, kapan saja.",
    order: 3,
  },
];

const displayStats = computed(() =>
  data.value?.stats?.length ? data.value.stats : fallbackStats
);
const displayValues = computed(() =>
  data.value?.values?.length ? data.value.values : fallbackValues
);
const displayGallery = computed(() => data.value?.gallery ?? []);

const heroBadge = computed(() => data.value?.hero_badge_text ?? "Partner Keamanan Anda");
const heroHeading = computed(
  () => data.value?.hero_heading ?? "Jangan Pertaruhkan Aset Anda Pada Instalasi Amatir."
);
const heroSub = computed(
  () =>
    data.value?.hero_subheading ??
    "Kami bukan sekadar tukang tarik kabel. PasarCctv mendesain, memasang, dan memastikan sistem keamanan Anda beroperasi prima untuk investasi ketenangan bertahun-tahun."
);
const ctaHeading = computed(
  () => data.value?.cta_heading ?? "Garansi Ganti Baru Tanpa Debat"
);
const ctaBody = computed(
  () =>
    data.value?.cta_body ??
    "Kamera mati tiba-tiba? NVR rusak? Kami berikan jaminan ganti unit baru (bukan servis) di tahun pertama. Kami yang repot urus ke pabrik, Anda tetap tenang memantau."
);
const ctaPrimary = computed(
  () => data.value?.cta_primary_text ?? "Jadwalkan Survey Gratis"
);
const ctaSecondary = computed(
  () => data.value?.cta_secondary_text ?? "Lihat Harga Paket"
);
const ctaSecUrl = computed(() => data.value?.cta_secondary_url ?? "/services/booking");
</script>

<template>
  <main class="about-root">
    <!-- ══════════════════════════════════════════════════════
         TICKER
    ══════════════════════════════════════════════════════════ -->
    <div class="ticker" aria-hidden="true">
      <div class="ticker__track">
        <span v-for="n in 8" :key="n">
          INSTALASI CCTV &nbsp;·&nbsp; SECURITY SYSTEM &nbsp;·&nbsp; MONITORING 24 JAM
          &nbsp;·&nbsp; GARANSI RESMI &nbsp;·&nbsp;&nbsp;
        </span>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════
         HERO
    ══════════════════════════════════════════════════════════ -->
    <section class="hero">
      <div class="hero__noise" aria-hidden="true"></div>
      <div class="hero__glow" aria-hidden="true"></div>

      <div class="hero__inner">
        <span class="badge">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            aria-hidden="true"
          >
            <path :d="getIconPath('lucide:shield-check')" />
          </svg>
          {{ heroBadge }}
        </span>

        <!-- Skeleton heading -->
        <template v-if="isPending">
          <div class="skel skel--h1"></div>
          <div class="skel skel--p"></div>
        </template>
        <template v-else>
          <h1 class="hero__title">
            <!-- Pisah heading menjadi dramatik dengan highlight kata kunci -->
            Jangan Pertaruhkan<br />
            Aset Anda Pada<br />
            <em class="hero__strike">Instalasi Amatir</em>.
          </h1>
          <p class="hero__sub">{{ heroSub }}</p>
        </template>

        <div class="hero__cta">
          <button class="btn btn--primary">
            {{ ctaPrimary }}
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
          <NuxtLink :to="ctaSecUrl" class="btn btn--ghost">
            {{ ctaSecondary }}
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M12 5v14M5 12l7 7 7-7" />
            </svg>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════
         STATS BAR
    ══════════════════════════════════════════════════════════ -->
    <section class="stats-bar">
      <div class="stats-bar__inner">
        <template v-if="isPending">
          <div v-for="i in 4" :key="i" class="skel skel--stat"></div>
        </template>
        <template v-else>
          <div v-for="(stat, idx) in displayStats" :key="stat.id" class="stat-item">
            <span class="stat-item__value">{{ stat.value }}</span>
            <span class="stat-item__label">{{ stat.label }}</span>
            <div v-if="idx < displayStats.length - 1" class="stat-item__div"></div>
          </div>
        </template>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════
         VALUES — MENGAPA MEMILIH KAMI
    ══════════════════════════════════════════════════════════ -->
    <section class="values">
      <div class="values__inner">
        <div class="values__head">
          <div class="section-label">Komitmen Kami</div>
          <h2 class="values__title">Mengapa Memilih Kami?</h2>
          <p class="values__sub">
            1x pemasangan yang benar menghemat jutaan rupiah biaya perbaikan di masa
            depan.
          </p>
        </div>

        <div class="values__grid">
          <!-- Skeleton -->
          <template v-if="isPending">
            <div v-for="i in 4" :key="i" class="val-card val-card--skel"></div>
          </template>

          <div v-else v-for="val in displayValues" :key="val.id" class="val-card">
            <div class="val-card__icon-wrap">
              <svg
                width="26"
                height="26"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="val-card__icon"
                aria-hidden="true"
              >
                <path :d="getIconPath(val.icon)" />
              </svg>
            </div>
            <h3 class="val-card__title">{{ val.title }}</h3>
            <p class="val-card__desc">{{ val.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════
         GALLERY SWIPER
    ══════════════════════════════════════════════════════════ -->
    <section class="gallery-section">
      <div class="gallery-section__head">
        <div class="section-label section-label--light">Kualitas Di Lapangan</div>
        <h2 class="gallery-section__title">Transparan. Rapi. Estetik.</h2>
        <p class="gallery-section__sub">
          Bukti nyata hasil kerja tim spesialis kami di setiap proyek.
        </p>
      </div>

      <!-- Skeleton gallery -->
      <div v-if="isPending" class="gallery-skel-row">
        <div v-for="i in 3" :key="i" class="gallery-skel"></div>
      </div>

      <!-- Gallery kosong (belum ada upload) → tampilkan placeholder tipografi -->
      <div v-else-if="!displayGallery.length" class="gallery-empty">
        <span class="gallery-empty__icon">📷</span>
        <p>Galeri sedang dipersiapkan.</p>
      </div>

      <!-- Swiper dengan gambar dari CDN -->
      <div v-else class="gallery-swiper-wrap">
        <Swiper
          :modules="swiperModules"
          :slides-per-view="1.15"
          :space-between="16"
          :centered-slides="true"
          :loop="true"
          :autoplay="{ delay: 3500, disableOnInteraction: false }"
          :pagination="{ clickable: true, dynamicBullets: true }"
          :breakpoints="{
            640: { slidesPerView: 2, spaceBetween: 20, centeredSlides: false },
            1024: { slidesPerView: 3.4, spaceBetween: 24, centeredSlides: false },
          }"
          class="gallery-swiper"
        >
          <SwiperSlide v-for="img in displayGallery" :key="img.id" class="gallery-slide">
            <div class="gallery-card">
              <img
                :src="img.cdn_url"
                :alt="img.alt"
                class="gallery-card__img"
                loading="lazy"
              />
              <div class="gallery-card__overlay"></div>
              <div class="gallery-card__caption">
                <span class="gallery-card__dot"></span>
                <span>{{ img.alt }}</span>
              </div>
            </div>
          </SwiperSlide>
        </Swiper>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════
         ABOUT NARRATIVE  (story section)
    ══════════════════════════════════════════════════════════ -->
    <section class="story">
      <div class="story__inner">
        <div class="story__left">
          <div class="section-label">Tentang Kami</div>
          <h2 class="story__title">
            Bukan Sekadar<br />
            <em class="story__accent">Tukang Kabel.</em>
          </h2>
          <div class="story__bar"></div>
        </div>
        <div class="story__right">
          <p>
            PasarCctv lahir dari frustrasi nyata: terlalu banyak instalasi amatir
            yang meninggalkan blind-spot, kabel semrawut, dan garansi kosong.
          </p>
          <p>
            Kami hadir dengan standar berbeda — setiap kabel masuk dalam conduit tertutup,
            setiap sudut kamera disimulasikan sebelum dipasang, dan setiap sistem ditest
            end-to-end sebelum teknisi meninggalkan lokasi.
          </p>
          <p>
            Lebih dari <strong>1.200 titik kamera</strong> kini menjaga rumah, toko,
            pabrik, dan fasilitas publik — beroperasi 24/7 tanpa keluhan.
          </p>
          <div class="story__tags">
            <span class="tag">Hikvision Partner</span>
            <span class="tag">Dahua Certified</span>
            <span class="tag">IP Camera Specialist</span>
            <span class="tag">NVR / DVR Setup</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════
         CTA GARANSI
    ══════════════════════════════════════════════════════════ -->
    <section class="cta-section">
      <div class="cta-section__glow" aria-hidden="true"></div>
      <div class="cta-section__inner">
        <div class="cta-section__icon-wrap" aria-hidden="true">
          <svg
            width="40"
            height="40"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path :d="getIconPath('lucide:shield-check')" />
          </svg>
        </div>

        <template v-if="isPending">
          <div class="skel skel--cta-h"></div>
          <div class="skel skel--cta-p"></div>
        </template>
        <template v-else>
          <h2 class="cta-section__title">{{ ctaHeading }}</h2>
          <p class="cta-section__body">{{ ctaBody }}</p>
        </template>

        <!-- Desktop buttons -->
        <div class="cta-section__btns cta-section__btns--desktop">
          <button class="btn btn--dark">{{ ctaPrimary }}</button>
          <NuxtLink :to="ctaSecUrl" class="btn btn--light">{{ ctaSecondary }}</NuxtLink>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════
         MOBILE STICKY CTA
    ══════════════════════════════════════════════════════════ -->
    <div class="mobile-cta" role="complementary" aria-label="Tombol aksi utama">
      <button class="mobile-cta__btn mobile-cta__btn--primary">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
        >
          <path
            d="M8 2v3M16 2v3M3 8h18M5 3h14a2 2 0 0 1 2 2v15a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zM10 12h4M12 10v4"
          />
        </svg>
        <span>Survey Gratis</span>
      </button>
      <NuxtLink :to="ctaSecUrl" class="mobile-cta__btn mobile-cta__btn--secondary">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
        >
          <path
            d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4zM3 6h18M16 10a4 4 0 0 1-8 0"
          />
        </svg>
        <span>Pilih Paket</span>
      </NuxtLink>
    </div>
  </main>
</template>

<style scoped>
/* ════════════════════════════════════════════════════════════
   DESIGN TOKENS  – konsisten dengan portfolio/index.vue
════════════════════════════════════════════════════════════ */
.about-root {
  --c-bg: #0a0a0a;
  --c-surface: #111111;
  --c-border: #222222;
  --c-muted: #444444;
  --c-text: #f0ede8;
  --c-sub: #888888;
  --c-red: #e8001d;
  --c-red-dim: #6b0010;

  --f-display: "Barlow Condensed", "Impact", sans-serif;
  --f-body: "DM Sans", "Helvetica Neue", sans-serif;
  --f-mono: "JetBrains Mono", monospace;

  background: var(--c-bg);
  color: var(--c-text);
  font-family: var(--f-body);
  min-height: 100vh;
  overflow-x: hidden;

  /* Extra padding bottom mobile agar sticky CTA tidak nutup konten */
  padding-bottom: 80px;
}

@media (min-width: 768px) {
  .about-root {
    padding-bottom: 0;
  }
}

/* ── Utilities ─────────────────────────────────────────────── */
.section-label {
  font-family: var(--f-mono);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--c-red);
  margin-bottom: 0.75rem;
}
.section-label--light {
  color: #ff6b7a;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.75rem;
  font-family: var(--f-body);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  cursor: pointer;
  border: none;
  transition: all 0.18s ease;
  white-space: nowrap;
}
.btn--primary {
  background: var(--c-red);
  color: #fff;
}
.btn--primary:hover {
  background: #c7001a;
  transform: translateY(-1px);
}
.btn--ghost {
  background: transparent;
  color: var(--c-text);
  border: 1px solid var(--c-border);
}
.btn--ghost:hover {
  border-color: var(--c-muted);
}
.btn--dark {
  background: #000;
  color: #fff;
}
.btn--dark:hover {
  background: #1a1a1a;
}
.btn--light {
  background: #fff;
  color: var(--c-red);
}
.btn--light:hover {
  background: #f0ede8;
}

/* Skeleton */
.skel {
  background: linear-gradient(90deg, #1a1a1a 25%, #242424 50%, #1a1a1a 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 3px;
}
.skel--h1 {
  height: 120px;
  margin-bottom: 1.5rem;
}
.skel--p {
  height: 60px;
  max-width: 520px;
}
.skel--stat {
  height: 60px;
  flex: 1;
  min-width: 80px;
}
.skel--cta-h {
  height: 56px;
  max-width: 500px;
  margin: 0 auto 1rem;
}
.skel--cta-p {
  height: 80px;
  max-width: 560px;
  margin: 0 auto 2rem;
}

@keyframes shimmer {
  from {
    background-position: 200% 0;
  }
  to {
    background-position: -200% 0;
  }
}

/* ════════════════════════════════════════════════════════════
   TICKER
════════════════════════════════════════════════════════════ */
.ticker {
  overflow: hidden;
  border-bottom: 1px solid var(--c-border);
  background: var(--c-bg);
  position: relative;
  z-index: 10;
}
.ticker__track {
  display: flex;
  white-space: nowrap;
  animation: ticker-scroll 28s linear infinite;
  font-family: var(--f-mono);
  font-size: 0.58rem;
  letter-spacing: 0.15em;
  color: var(--c-muted);
  padding: 0.55rem 0;
}
@keyframes ticker-scroll {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-50%);
  }
}

/* ════════════════════════════════════════════════════════════
   HERO
════════════════════════════════════════════════════════════ */
.hero {
  position: relative;
  min-height: 92svh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
  border-bottom: 1px solid var(--c-border);
}
.hero__noise {
  position: absolute;
  inset: 0;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  pointer-events: none;
}
.hero__glow {
  position: absolute;
  top: -20%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(232, 0, 29, 0.18) 0%, transparent 65%);
  pointer-events: none;
}
.hero__inner {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
  padding: 5rem 1.5rem 5rem;
  width: 100%;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-family: var(--f-mono);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--c-sub);
  border: 1px solid var(--c-border);
  padding: 0.35rem 0.75rem;
  margin-bottom: 2rem;
}
.hero__title {
  font-family: var(--f-display);
  font-size: clamp(3.2rem, 11vw, 8rem);
  font-weight: 900;
  line-height: 0.92;
  text-transform: uppercase;
  letter-spacing: -0.01em;
  margin: 0 0 2rem;
  color: var(--c-text);
}
.hero__strike {
  /* strikethrough merah – same trick as portfolio hero */
  font-style: italic;
  color: var(--c-red);
  text-decoration: line-through;
  text-decoration-thickness: 4px;
}
.hero__sub {
  max-width: 520px;
  font-size: 1rem;
  line-height: 1.75;
  color: var(--c-sub);
  margin-bottom: 2.5rem;
}
.hero__cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

/* ════════════════════════════════════════════════════════════
   STATS BAR
════════════════════════════════════════════════════════════ */
.stats-bar {
  border-bottom: 1px solid var(--c-border);
  background: var(--c-surface);
}
.stats-bar__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
  justify-content: space-around;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  flex: 1;
  min-width: 80px;
}
.stat-item__value {
  font-family: var(--f-display);
  font-size: clamp(1.8rem, 5vw, 3rem);
  font-weight: 900;
  line-height: 1;
  color: var(--c-text);
  letter-spacing: -0.02em;
}
.stat-item__label {
  font-family: var(--f-mono);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-sub);
  margin-top: 0.3rem;
}
.stat-item__div {
  position: absolute;
  right: 0;
  top: 10%;
  height: 80%;
  width: 1px;
  background: var(--c-border);
}

/* ════════════════════════════════════════════════════════════
   VALUES
════════════════════════════════════════════════════════════ */
.values {
  padding: 5rem 0;
  border-bottom: 1px solid var(--c-border);
}
.values__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}
.values__head {
  margin-bottom: 3rem;
}
.values__title {
  font-family: var(--f-display);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 900;
  text-transform: uppercase;
  line-height: 1;
  margin: 0 0 0.75rem;
}
.values__sub {
  color: var(--c-sub);
  font-size: 0.95rem;
  max-width: 480px;
}
.values__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1px;
  border: 1px solid var(--c-border);
}
.val-card {
  background: var(--c-surface);
  padding: 2rem;
  border: none;
  transition: background 0.2s;
}
.val-card:hover {
  background: #161616;
}
.val-card--skel {
  height: 180px;
  background: linear-gradient(90deg, #111 25%, #1a1a1a 50%, #111 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.val-card__icon-wrap {
  width: 48px;
  height: 48px;
  border: 1px solid var(--c-border);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
  color: var(--c-red);
  transition: background 0.2s, border-color 0.2s;
}
.val-card:hover .val-card__icon-wrap {
  background: var(--c-red);
  border-color: var(--c-red);
  color: #fff;
}
.val-card__icon {
  transition: color 0.2s;
}
.val-card__title {
  font-family: var(--f-display);
  font-size: 1rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.6rem;
  color: var(--c-text);
}
.val-card:hover .val-card__title {
  color: var(--c-red);
}
.val-card__desc {
  font-size: 0.85rem;
  line-height: 1.7;
  color: var(--c-sub);
  margin: 0;
}

/* ════════════════════════════════════════════════════════════
   GALLERY
════════════════════════════════════════════════════════════ */
.gallery-section {
  padding: 5rem 0;
  background: #0d0d0d;
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
  overflow: hidden;
}
.gallery-section__head {
  max-width: 1200px;
  margin: 0 auto 2.5rem;
  padding: 0 1.5rem;
}
.gallery-section__title {
  font-family: var(--f-display);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 900;
  text-transform: uppercase;
  margin: 0 0 0.5rem;
}
.gallery-section__sub {
  color: var(--c-sub);
  font-size: 0.9rem;
}
.gallery-skel-row {
  display: flex;
  gap: 1rem;
  padding: 0 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}
.gallery-skel {
  flex: 1;
  height: 280px;
  background: linear-gradient(90deg, #141414 25%, #1c1c1c 50%, #141414 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.gallery-empty {
  text-align: center;
  padding: 4rem 1.5rem;
  color: var(--c-sub);
}
.gallery-empty__icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}
.gallery-swiper-wrap {
  width: 100%;
}
.gallery-swiper {
  padding: 0 1.5rem 3.5rem !important;
  max-width: 1400px;
  margin: 0 auto;
}
.gallery-slide {
  height: auto;
}
.gallery-card {
  position: relative;
  width: 100%;
  aspect-ratio: 4/5;
  overflow: hidden;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
}
@media (min-width: 768px) {
  .gallery-card {
    aspect-ratio: 1;
  }
}
.gallery-card__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.8s ease, opacity 0.3s;
  opacity: 0.8;
}
.gallery-card:hover .gallery-card__img {
  transform: scale(1.07);
  opacity: 1;
}
.gallery-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75) 0%, transparent 55%);
}
.gallery-card__caption {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--f-mono);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #fff;
}
.gallery-card__dot {
  width: 6px;
  height: 6px;
  background: var(--c-red);
  border-radius: 50%;
  flex-shrink: 0;
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.7);
  }
}

:deep(.swiper-pagination-bullet) {
  background-color: rgba(255, 255, 255, 0.3);
  width: 6px;
  height: 6px;
  transition: all 0.3s ease;
}
:deep(.swiper-pagination-bullet-active) {
  background-color: var(--c-red);
  width: 24px;
  border-radius: 3px;
}

/* ════════════════════════════════════════════════════════════
   STORY / NARRATIVE
════════════════════════════════════════════════════════════ */
.story {
  padding: 5rem 0;
  border-bottom: 1px solid var(--c-border);
}
.story__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
}
@media (min-width: 768px) {
  .story__inner {
    grid-template-columns: 1fr 1.6fr;
    gap: 5rem;
    align-items: start;
  }
}
.story__title {
  font-family: var(--f-display);
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 900;
  text-transform: uppercase;
  line-height: 0.95;
  margin: 0 0 1.5rem;
}
.story__accent {
  font-style: italic;
  color: var(--c-red);
}
.story__bar {
  width: 48px;
  height: 3px;
  background: var(--c-red);
}
.story__right p {
  font-size: 0.95rem;
  line-height: 1.8;
  color: var(--c-sub);
  margin-bottom: 1.2rem;
}
.story__right p:last-of-type {
  margin-bottom: 0;
}
.story__right strong {
  color: var(--c-text);
  font-weight: 600;
}
.story__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 2rem;
}
.tag {
  font-family: var(--f-mono);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.35rem 0.7rem;
  border: 1px solid var(--c-border);
  color: var(--c-sub);
  transition: all 0.15s;
}
.tag:hover {
  border-color: var(--c-red);
  color: var(--c-red);
}

/* ════════════════════════════════════════════════════════════
   CTA GARANSI
════════════════════════════════════════════════════════════ */
.cta-section {
  position: relative;
  background: var(--c-red);
  color: #fff;
  padding: 5rem 1.5rem;
  text-align: center;
  overflow: hidden;
}
.cta-section__glow {
  position: absolute;
  bottom: -40%;
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  height: 400px;
  background: radial-gradient(ellipse, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
  pointer-events: none;
}
.cta-section__inner {
  position: relative;
  z-index: 1;
  max-width: 680px;
  margin: 0 auto;
}
.cta-section__icon-wrap {
  width: 64px;
  height: 64px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}
.cta-section__title {
  font-family: var(--f-display);
  font-size: clamp(2rem, 6vw, 3.5rem);
  font-weight: 900;
  text-transform: uppercase;
  line-height: 1;
  margin: 0 0 1.25rem;
}
.cta-section__body {
  font-size: 0.95rem;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 2.5rem;
}
.cta-section__btns--desktop {
  display: none;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}
@media (min-width: 768px) {
  .cta-section__btns--desktop {
    display: flex;
  }
}

/* ════════════════════════════════════════════════════════════
   MOBILE STICKY CTA
════════════════════════════════════════════════════════════ */
.mobile-cta {
  display: flex;
  gap: 0.5rem;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.75rem;
  padding-bottom: calc(0.75rem + env(safe-area-inset-bottom));
  background: rgba(10, 10, 10, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid var(--c-border);
  z-index: 100;
}
@media (min-width: 768px) {
  .mobile-cta {
    display: none;
  }
}
.mobile-cta__btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.9rem 1rem;
  border: none;
  cursor: pointer;
  text-decoration: none;
  font-family: var(--f-body);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border-radius: 8px;
  transition: transform 0.15s, opacity 0.15s;
}
.mobile-cta__btn:active {
  transform: scale(0.96);
  opacity: 0.9;
}
.mobile-cta__btn--primary {
  background: var(--c-red);
  color: #fff;
}
.mobile-cta__btn--secondary {
  background: #fff;
  color: #0a0a0a;
}
</style>
