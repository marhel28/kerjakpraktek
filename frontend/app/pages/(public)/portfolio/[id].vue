<script setup lang="ts">
/**
 * pages/portfolio/[id].vue
 */

import { ref, computed, onMounted } from "vue";
import type { ImageOut, ImageRole } from "~/composables/usePortfolio";

const route = useRoute();
const id = route.params.id as string;

const { data: project, status } = await usePortfolioProject(id);
const isPending = computed(() => status.value === "pending");

// 404 guard
if (!isPending.value && !project.value) {
  throw createError({ statusCode: 404, message: "Project tidak ditemukan." });
}

useSeoMeta({
  title: computed(() =>
    project.value
      ? `${project.value.title} | Portofolio CCTV PasarCctv`
      : "Detail Project | PasarCctv"
  ),
  description: computed(() => project.value?.problem ?? ""),
  ogImage: computed(() => project.value?.images?.[0]?.url ?? "/images/og-portfolio.jpg"),
});

// ── Gallery tabs ─────────────────────────────────────────────────
type GalleryTab = "all" | ImageRole;
const galleryTab = ref<GalleryTab>("all");

const galleryTabs: Array<{ label: string; value: GalleryTab }> = [
  { label: "Semua", value: "all" },
  { label: "Sebelum", value: "before" },
  { label: "Sesudah", value: "after" },
  { label: "Galeri", value: "gallery" },
  { label: "Cover", value: "cover" },
];

const visibleImages = computed<ImageOut[]>(() => {
  if (!project.value?.images?.length) return [];
  if (galleryTab.value === "all") return project.value.images;
  return project.value.images.filter((img) => img.role === galleryTab.value);
});

const activeTabs = computed(() =>
  galleryTabs.filter(
    (t) => t.value === "all" || project.value?.images?.some((img) => img.role === t.value)
  )
);

// ── Swiper breakpoints (object — JANGAN pakai JSON.stringify) ─────
// JSON.stringify menghasilkan string, Swiper butuh object JS murni.
// Swiper Web Components otomatis parse attribute object via Vue binding.
const swiperBreakpoints = {
  640: { slidesPerView: 1.5 },
  768: { slidesPerView: 2 },
  1024: { slidesPerView: 3 },
};

// ── Lightbox ─────────────────────────────────────────────────────
const lightboxIndex = ref<number | null>(null);
const lightboxImg = computed<ImageOut | null>(() =>
  lightboxIndex.value !== null ? visibleImages.value[lightboxIndex.value] ?? null : null
);

function openLightbox(idx: number) {
  lightboxIndex.value = idx;
}
function closeLightbox() {
  lightboxIndex.value = null;
}
function lightboxPrev() {
  if (lightboxIndex.value === null) return;
  lightboxIndex.value =
    (lightboxIndex.value - 1 + visibleImages.value.length) % visibleImages.value.length;
}
function lightboxNext() {
  if (lightboxIndex.value === null) return;
  lightboxIndex.value = (lightboxIndex.value + 1) % visibleImages.value.length;
}

onMounted(() => {
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") lightboxPrev();
    if (e.key === "ArrowRight") lightboxNext();
  });

  // Register Swiper Web Components
  if (typeof window !== "undefined" && !customElements.get("swiper-container")) {
    import("swiper/element/bundle").then(({ register }) => register());
  }
});

// ── Category color map ────────────────────────────────────────────
const catColor: Record<string, string> = {
  Residensial: "#4488ff",
  Komersial: "#ff8800",
  Retail: "#00c896",
  Korporat: "#aa44ff",
  "Fasilitas Umum": "#00b0ff",
  "F&B": "#ff4466",
  Manufaktur: "#ffcc00",
  Lainnya: "#888888",
};
const getCatColor = (cat: string) => catColor[cat] ?? "#888888";

// ── Package slug → route mapping ─────────────────────────────────
// Hanya slug yang sudah punya halaman di router yang boleh di-link.
// Tambahkan slug baru di sini seiring halaman dibuat.
const VALID_PACKAGE_SLUGS = new Set(["basic", "standard", "premium", "enterprise"]);
const packageRoute = computed(() => {
  const slug = project.value?.package_slug;
  // Ganti prefix sesuai struktur route kamu, misal /paket/ atau /kategori/
  // Jika route belum ada, return null supaya link tidak di-render
  return slug && VALID_PACKAGE_SLUGS.has(slug) ? `/paket/${slug}` : null;
});
</script>

<template>
  <main class="detail-root">
    <!-- ══════════════════════════════════════════════════════════
         BACK NAV
    ══════════════════════════════════════════════════════════════ -->
    <div class="breadcrumb">
      <div class="breadcrumb__inner">
        <NuxtLink to="/portfolio" class="breadcrumb__back">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path d="M19 12H5M12 5l-7 7 7 7" />
          </svg>
          Kembali ke Portofolio
        </NuxtLink>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         HERO PROJECT
    ══════════════════════════════════════════════════════════════ -->
    <section class="proj-hero">
      <div
        v-if="project?.images?.length"
        class="proj-hero__bg"
        :style="{
          backgroundImage: `url(${
            project.images.find((i) => i.role === 'cover')?.url ?? project.images[0]?.url
          })`,
        }"
      ></div>
      <div class="proj-hero__overlay"></div>

      <div v-if="isPending" class="proj-hero__skel"></div>

      <div v-else-if="project" class="proj-hero__inner">
        <div class="proj-hero__meta">
          <span
            class="proj-hero__cat"
            :style="{
              background: getCatColor(project.category) + '22',
              color: getCatColor(project.category),
              borderColor: getCatColor(project.category) + '44',
            }"
            >{{ project.category }}</span
          >
          <span v-if="project.is_featured" class="proj-hero__feat"
            >★ Featured Project</span
          >
        </div>

        <h1 class="proj-hero__title">{{ project.title }}</h1>

        <div class="proj-hero__stats">
          <div class="ph-stat">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"
              />
              <circle cx="12" cy="9" r="2.5" />
            </svg>
            {{ project.location }}
          </div>
          <div class="ph-stat">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M23 7l-7 5 7 5V7z" />
              <rect x="1" y="5" width="15" height="14" rx="2" />
            </svg>
            {{ project.cameras }} titik kamera
          </div>
          <div v-if="project.client_type" class="ph-stat">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
            </svg>
            {{ project.client_type }}
          </div>
          <!-- Hanya render jika route paket benar-benar ada -->
          <div v-if="packageRoute" class="ph-stat ph-stat--pkg">
            <NuxtLink :to="packageRoute">Lihat Paket →</NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         CASE STUDY  (PSR)
    ══════════════════════════════════════════════════════════════ -->
    <section
      v-if="project?.problem || project?.solution || project?.result"
      class="case-study"
    >
      <div class="case-study__inner">
        <div class="section-label">Studi Kasus</div>

        <div class="psr-row">
          <div v-if="project.problem" class="psr-block">
            <div class="psr-block__num">01</div>
            <div class="psr-block__tag psr-block__tag--problem">Masalah</div>
            <p class="psr-block__text">{{ project.problem }}</p>
          </div>
          <div v-if="project.solution" class="psr-block">
            <div class="psr-block__num">02</div>
            <div class="psr-block__tag psr-block__tag--solution">Solusi</div>
            <p class="psr-block__text">{{ project.solution }}</p>
          </div>
          <div v-if="project.result" class="psr-block">
            <div class="psr-block__num">03</div>
            <div class="psr-block__tag psr-block__tag--result">Hasil</div>
            <p class="psr-block__text">{{ project.result }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         GALLERY  dengan tab + Swiper
    ══════════════════════════════════════════════════════════════ -->
    <section v-if="project?.images?.length" class="gallery-section">
      <div class="gallery-section__inner">
        <div class="section-label">Dokumentasi</div>
        <h2 class="gallery-section__title">Galeri Foto</h2>

        <!-- Tab bar -->
        <div class="gallery-tabs" role="tablist">
          <button
            v-for="tab in activeTabs"
            :key="tab.value"
            class="gallery-tab"
            :class="{ 'gallery-tab--active': galleryTab === tab.value }"
            role="tab"
            @click="galleryTab = tab.value"
          >
            {{ tab.label }}
            <span class="gallery-tab__count">
              {{
                tab.value === "all"
                  ? project.images.length
                  : project.images.filter((i) => i.role === tab.value).length
              }}
            </span>
          </button>
        </div>

        <!--
          ClientOnly wajib — Swiper Web Components tidak bisa SSR.
          swiperBreakpoints di-bind sebagai object JS, BUKAN JSON.stringify.
          JSON.stringify menghasilkan string → Swiper error saat iterasi kunci.
        -->
        <ClientOnly v-if="visibleImages.length">
          <swiper-container
            :slides-per-view="1"
            :space-between="16"
            :grab-cursor="true"
            :loop="visibleImages.length > 3"
            :pagination="true"
            :navigation="true"
            :breakpoints.prop="swiperBreakpoints"
            class="gallery-swiper"
          >
            <swiper-slide
              v-for="(img, idx) in visibleImages"
              :key="img.id"
              class="gallery-slide"
            >
              <div class="gallery-thumb" @click="openLightbox(idx)">
                <img
                  :src="img.url"
                  :alt="img.alt_text ?? img.role"
                  class="gallery-thumb__img"
                  loading="lazy"
                />
                <div class="gallery-thumb__overlay">
                  <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
                  </svg>
                </div>
                <span
                  class="gallery-thumb__role"
                  :class="`gallery-thumb__role--${img.role}`"
                >
                  {{
                    img.role === "before"
                      ? "Sebelum"
                      : img.role === "after"
                      ? "Sesudah"
                      : img.role === "cover"
                      ? "Cover"
                      : "Galeri"
                  }}
                </span>
                <div v-if="img.alt_text" class="gallery-thumb__caption">
                  {{ img.alt_text }}
                </div>
              </div>
            </swiper-slide>
          </swiper-container>

          <template #fallback>
            <div class="gallery-skel-row">
              <div v-for="i in 3" :key="i" class="gallery-skel"></div>
            </div>
          </template>
        </ClientOnly>

        <div v-else class="gallery-empty">Belum ada foto untuk filter ini.</div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         LIGHTBOX
    ══════════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <Transition name="lb">
        <div v-if="lightboxImg" class="lightbox" @click.self="closeLightbox">
          <button class="lb-close" @click="closeLightbox" aria-label="Tutup">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
          <button
            class="lb-nav lb-nav--prev"
            @click="lightboxPrev"
            aria-label="Sebelumnya"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </button>
          <div class="lb-content">
            <img
              :src="lightboxImg.url"
              :alt="lightboxImg.alt_text ?? ''"
              class="lb-img"
            />
            <div v-if="lightboxImg.alt_text" class="lb-caption">
              {{ lightboxImg.alt_text }}
            </div>
            <div class="lb-counter">
              {{ (lightboxIndex ?? 0) + 1 }} / {{ visibleImages.length }}
            </div>
          </div>
          <button
            class="lb-nav lb-nav--next"
            @click="lightboxNext"
            aria-label="Berikutnya"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M9 18l6-6-6-6" />
            </svg>
          </button>
        </div>
      </Transition>
    </Teleport>

    <!-- ══════════════════════════════════════════════════════════
         REVIEWS terkait project ini
    ══════════════════════════════════════════════════════════════ -->
    <section v-if="project?.reviews?.length" class="review-section">
      <div class="review-section__inner">
        <div class="section-label">Ulasan Klien</div>
        <h2 class="review-section__title">Yang Mereka Katakan</h2>

        <div class="review-grid">
          <div
            v-for="rv in project.reviews.filter((r) => r.is_active)"
            :key="rv.id"
            class="review-card"
          >
            <div class="review-card__stars">
              <span v-for="s in rv.rating" :key="s" class="star">★</span>
              <span v-for="s in 5 - rv.rating" :key="'e' + s" class="star star--empty"
                >★</span
              >
            </div>
            <blockquote class="review-card__quote">"{{ rv.text }}"</blockquote>
            <div class="review-card__author">
              <div class="review-card__avatar">{{ rv.name.charAt(0).toUpperCase() }}</div>
              <div>
                <div class="review-card__name">{{ rv.name }}</div>
                <div v-if="rv.role" class="review-card__role">{{ rv.role }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         BOTTOM CTA
    ══════════════════════════════════════════════════════════════ -->
    <section class="detail-cta">
      <div class="detail-cta__inner">
        <div class="section-label">Mulai Sekarang</div>
        <h2 class="detail-cta__title">Ingin Hasil<br />Serupa?</h2>
        <div class="detail-cta__btns">
          <button class="btn btn--primary btn--lg">Konsultasi Gratis</button>
          <NuxtLink to="/portfolio" class="btn btn--outline btn--lg"
            >← Portofolio Lainnya</NuxtLink
          >
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
/* @import DIHAPUS — sudah ada di nuxt.config.ts > app.head.link */

.detail-root {
  --c-bg: #0a0a0a;
  --c-surface: #111111;
  --c-border: #222222;
  --c-muted: #444444;
  --c-text: #f0ede8;
  --c-sub: #888888;
  --c-red: #e8001d;
  --c-red-dim: #6b0010;
  --c-gold: #c9a84c;

  --f-display: "Barlow Condensed", Impact, sans-serif;
  --f-body: "DM Sans", "Helvetica Neue", sans-serif;
  --f-mono: "JetBrains Mono", monospace;

  background: var(--c-bg);
  color: var(--c-text);
  font-family: var(--f-body);
  min-height: 100svh;
  overflow-x: hidden;
}

.section-label {
  font-family: var(--f-mono);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--c-red);
  margin-bottom: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  font-family: var(--f-body);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  cursor: pointer;
  border: none;
  transition: all 0.18s;
}
.btn--primary {
  background: var(--c-red);
  color: #fff;
}
.btn--primary:hover {
  background: #c7001a;
}
.btn--outline {
  background: transparent;
  color: var(--c-text);
  border: 1px solid var(--c-muted);
}
.btn--outline:hover {
  border-color: var(--c-red);
  color: var(--c-red);
}
.btn--lg {
  padding: 1.1rem 2.5rem;
  font-size: 0.8rem;
}

/* ── Breadcrumb ───────────────────────────────────────────────── */
.breadcrumb {
  border-bottom: 1px solid var(--c-border);
  background: var(--c-surface);
}
.breadcrumb__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
}
.breadcrumb__back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-family: var(--f-mono);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-sub);
  text-decoration: none;
  transition: color 0.15s;
}
.breadcrumb__back:hover {
  color: var(--c-text);
}

/* ── Hero ─────────────────────────────────────────────────────── */
.proj-hero {
  position: relative;
  min-height: 55svh;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
  border-bottom: 1px solid var(--c-border);
}
.proj-hero__bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  filter: grayscale(0.3);
}
.proj-hero__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(0, 0, 0, 0.4) 60%,
    rgba(0, 0, 0, 0.6) 100%
  );
}
.proj-hero__skel {
  height: 55svh;
  background: linear-gradient(
    90deg,
    var(--c-surface) 25%,
    #1a1a1a 50%,
    var(--c-surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.proj-hero__inner {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  width: 100%;
  box-sizing: border-box;
}
.proj-hero__meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.proj-hero__cat {
  font-family: var(--f-mono);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 0.3rem 0.7rem;
  border: 1px solid;
}
.proj-hero__feat {
  font-family: var(--f-mono);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-gold);
  background: rgba(201, 168, 76, 0.1);
  padding: 0.3rem 0.6rem;
}
.proj-hero__title {
  font-family: var(--f-display);
  font-size: clamp(2rem, 5vw, 4rem);
  font-weight: 900;
  text-transform: uppercase;
  line-height: 1;
  letter-spacing: 0.01em;
  margin: 0 0 1.5rem;
  color: var(--c-text);
}
.proj-hero__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.ph-stat {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  color: var(--c-sub);
}
.ph-stat--pkg a {
  color: var(--c-red);
  text-decoration: none;
  font-weight: 600;
}

/* ── Case Study ───────────────────────────────────────────────── */
.case-study {
  background: var(--c-surface);
  border-bottom: 1px solid var(--c-border);
}
.case-study__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
}
.psr-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  border: 1px solid var(--c-border);
}
.psr-block {
  padding: 2.5rem 2rem;
  border-right: 1px solid var(--c-border);
  position: relative;
}
.psr-block:last-child {
  border-right: none;
}
.psr-block__num {
  font-family: var(--f-display);
  font-size: 4rem;
  font-weight: 900;
  line-height: 1;
  color: var(--c-border);
  margin-bottom: 0.75rem;
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  pointer-events: none;
  user-select: none;
}
.psr-block__tag {
  font-family: var(--f-mono);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  padding: 0.25rem 0.6rem;
  display: inline-block;
  margin-bottom: 1rem;
}
.psr-block__tag--problem {
  background: rgba(232, 162, 0, 0.1);
  color: #e8a200;
}
.psr-block__tag--solution {
  background: rgba(68, 136, 255, 0.1);
  color: #4488ff;
}
.psr-block__tag--result {
  background: rgba(0, 184, 107, 0.1);
  color: #00b86b;
}
.psr-block__text {
  font-size: 0.92rem;
  line-height: 1.7;
  color: var(--c-sub);
  margin: 0;
}

/* ── Gallery ──────────────────────────────────────────────────── */
.gallery-section {
  padding: 5rem 0;
}
.gallery-section__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}
.gallery-section__title {
  font-family: var(--f-display);
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 900;
  text-transform: uppercase;
  margin: 0 0 2rem;
}

.gallery-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--c-border);
}
.gallery-tab {
  font-family: var(--f-mono);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 0.5rem 1rem 0.75rem;
  background: transparent;
  border: none;
  color: var(--c-sub);
  cursor: pointer;
  position: relative;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.15s;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.gallery-tab:hover {
  color: var(--c-text);
}
.gallery-tab--active {
  color: var(--c-red);
  border-bottom-color: var(--c-red);
}
.gallery-tab__count {
  background: var(--c-border);
  color: var(--c-sub);
  font-size: 0.5rem;
  padding: 0.1rem 0.35rem;
  border-radius: 100px;
}
.gallery-tab--active .gallery-tab__count {
  background: var(--c-red-dim);
  color: var(--c-red);
}

.gallery-swiper {
  overflow: visible !important;
}

/* Skeleton fallback */
.gallery-skel-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.gallery-skel {
  aspect-ratio: 4/3;
  background: linear-gradient(
    90deg,
    var(--c-surface) 25%,
    #1a1a1a 50%,
    var(--c-surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.gallery-thumb {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
  cursor: zoom-in;
  background: #1a1a1a;
}
.gallery-thumb__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s ease;
}
.gallery-thumb:hover .gallery-thumb__img {
  transform: scale(1.05);
}
.gallery-thumb__overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  color: #fff;
}
.gallery-thumb:hover .gallery-thumb__overlay {
  opacity: 1;
}
.gallery-thumb__role {
  position: absolute;
  top: 0.6rem;
  left: 0.6rem;
  font-family: var(--f-mono);
  font-size: 0.52rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.2rem 0.45rem;
}
.gallery-thumb__role--before {
  background: rgba(232, 162, 0, 0.85);
  color: #000;
}
.gallery-thumb__role--after {
  background: rgba(0, 184, 107, 0.85);
  color: #000;
}
.gallery-thumb__role--cover {
  background: rgba(232, 0, 29, 0.85);
  color: #fff;
}
.gallery-thumb__role--gallery {
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
}
.gallery-thumb__caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.75);
  padding: 0.5rem 0.75rem;
  font-size: 0.72rem;
  color: #ccc;
  text-align: center;
}
.gallery-empty {
  text-align: center;
  padding: 3rem;
  color: var(--c-sub);
  border: 1px dashed var(--c-border);
  font-size: 0.85rem;
}

/* Swiper nav/pagination */
swiper-container::part(button-prev),
swiper-container::part(button-next) {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  color: var(--c-text);
  width: 36px;
  height: 36px;
  border-radius: 0;
}
swiper-container::part(pagination) {
  margin-top: 1.5rem;
}
swiper-container::part(bullet) {
  background: var(--c-border);
  opacity: 1;
}
swiper-container::part(bullet-active) {
  background: var(--c-red);
  width: 20px;
  border-radius: 3px;
}

/* ── Lightbox ─────────────────────────────────────────────────── */
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.96);
  display: flex;
  align-items: center;
  justify-content: center;
}
.lb-content {
  max-width: 90vw;
  max-height: 90svh;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.lb-img {
  max-width: 100%;
  max-height: 80svh;
  object-fit: contain;
  display: block;
}
.lb-caption {
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: var(--c-sub);
  text-align: center;
}
.lb-counter {
  margin-top: 0.5rem;
  font-family: var(--f-mono);
  font-size: 0.6rem;
  color: var(--c-muted);
  letter-spacing: 0.1em;
}
.lb-close {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  color: var(--c-text);
  width: 42px;
  height: 42px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  color: var(--c-text);
  width: 48px;
  height: 64px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.lb-nav--prev {
  left: 1.5rem;
}
.lb-nav--next {
  right: 1.5rem;
}
.lb-nav:hover {
  border-color: var(--c-red);
  color: var(--c-red);
}

.lb-enter-active,
.lb-leave-active {
  transition: opacity 0.2s;
}
.lb-enter-from,
.lb-leave-to {
  opacity: 0;
}

/* ── Reviews ──────────────────────────────────────────────────── */
.review-section {
  background: var(--c-surface);
  border-top: 1px solid var(--c-border);
  padding: 5rem 0;
}
.review-section__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}
.review-section__title {
  font-family: var(--f-display);
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 900;
  text-transform: uppercase;
  margin: 0 0 2.5rem;
}
.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
.review-card {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.review-card__stars {
  display: flex;
  gap: 2px;
}
.star {
  color: var(--c-gold);
  font-size: 0.85rem;
}
.star--empty {
  color: var(--c-border);
}
.review-card__quote {
  font-size: 0.93rem;
  line-height: 1.7;
  color: var(--c-sub);
  margin: 0;
  flex: 1;
}
.review-card__author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-top: 1px solid var(--c-border);
  padding-top: 1rem;
}
.review-card__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(232, 0, 29, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--f-display);
  font-size: 1rem;
  font-weight: 900;
  color: var(--c-red);
  flex-shrink: 0;
}
.review-card__name {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--c-text);
}
.review-card__role {
  font-size: 0.7rem;
  color: var(--c-sub);
}

/* ── Bottom CTA ───────────────────────────────────────────────── */
.detail-cta {
  padding: 6rem 2rem;
  text-align: center;
  border-top: 1px solid var(--c-border);
}
.detail-cta__inner {
  max-width: 600px;
  margin: 0 auto;
}
.detail-cta__title {
  font-family: var(--f-display);
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 900;
  text-transform: uppercase;
  line-height: 1;
  margin: 0 0 2.5rem;
}
.detail-cta__btns {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

@keyframes shimmer {
  from {
    background-position: 200% 0;
  }
  to {
    background-position: -200% 0;
  }
}

@media (max-width: 768px) {
  .psr-row {
    grid-template-columns: 1fr;
  }
  .psr-block {
    border-right: none;
    border-bottom: 1px solid var(--c-border);
  }
  .psr-block:last-child {
    border-bottom: none;
  }
  .psr-block__num {
    display: none;
  }
  .lb-nav {
    display: none;
  }
  .detail-cta__btns {
    flex-direction: column;
    align-items: center;
  }
  .gallery-skel-row {
    grid-template-columns: 1fr;
  }
}
</style>
