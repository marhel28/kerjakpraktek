<script setup lang="ts">
/**
 * pages/portfolio/index.vue
 */

import { ref, computed, onMounted } from "vue";
import type { ProjectCategory, ProjectListOut } from "~/composables/usePortfolio";

useSeoMeta({
  title: "Portofolio Pemasangan CCTV Profesional | PasarCctv",
  description:
    "Lihat hasil kerja nyata PasarCctv. Dari rumah mewah hingga pabrik, instalasi rapi bergaransi. 1200+ titik kamera terpasang.",
  ogTitle: "Portofolio Instalasi CCTV | PasarCctv",
  ogImage: "/images/og-portfolio.jpg",
  robots: "index, follow",
});

// ── Data ─────────────────────────────────────────────────────────
const { data, status } = await usePortfolioPage();
const isPending = computed(() => status.value === "pending");

// ── Filter kategori ───────────────────────────────────────────────
const categories: Array<{ label: string; value: ProjectCategory | "all" }> = [
  { label: "Semua", value: "all" },
  { label: "Residensial", value: "Residensial" },
  { label: "Komersial", value: "Komersial" },
  { label: "Retail", value: "Retail" },
  { label: "Korporat", value: "Korporat" },
  { label: "Fasilitas", value: "Fasilitas Umum" },
  { label: "F&B", value: "F&B" },
  { label: "Manufaktur", value: "Manufaktur" },
];
const activeCategory = ref<ProjectCategory | "all">("all");

const filteredProjects = computed<ProjectListOut[]>(() => {
  if (!data.value?.projects) return [];
  if (activeCategory.value === "all") return data.value.projects;
  return data.value.projects.filter((p) => p.category === activeCategory.value);
});

// ── Before/After slider ──────────────────────────────────────────
const sliderPos = ref(50);
let dragging = false;

function onSliderMove(e: MouseEvent | TouchEvent) {
  if (!dragging) return;
  const container = e.currentTarget as HTMLElement;
  const rect = container.getBoundingClientRect();
  const clientX = "touches" in e ? e.touches[0].clientX : e.clientX;
  const pct = Math.min(100, Math.max(0, ((clientX - rect.left) / rect.width) * 100));
  sliderPos.value = pct;
}

// ── Kontak WhatsApp & Fallback Visual ────────────────────────────
const whatsappConsultUrl = computed(() => {
  const msg = "Halo PasarCctv & Teknisi Padjajaran CCTV, saya tertarik dengan portofolio instalasi dan ingin konsultasi/survei lokasi."
  return `https://wa.me/6282218828108?text=${encodeURIComponent(msg)}`
})

const featuredBeforeImage = computed(() => {
  return data.value?.featured?.before_image || '/images/portfolio/before-cables.jpg'
})
const featuredAfterImage = computed(() => {
  return data.value?.featured?.after_image || '/images/portfolio/after-conduit.jpg'
})

// ── Swiper: register Web Components sekali di client ─────────────
// isCustomElement di nuxt.config.ts menghilangkan Vue warning,
// register() di sini mengaktifkan elemen-nya di DOM.
onMounted(async () => {
  if (typeof window !== "undefined" && !customElements.get("swiper-container")) {
    const { register } = await import("swiper/element/bundle");
    register();
  }
});
</script>

<template>
  <main class="portfolio-root">
    <!-- ══════════════════════════════════════════════════════════
         HERO
    ══════════════════════════════════════════════════════════════ -->
    <section class="hero">
      <div class="hero__noise" aria-hidden="true"></div>
      <div class="hero__glow" aria-hidden="true"></div>

      <div class="ticker" aria-hidden="true">
        <div class="ticker__track">
          <span v-for="n in 8" :key="n">
            INSTALASI CCTV &nbsp;·&nbsp; SECURITY SYSTEM &nbsp;·&nbsp; MONITORING 24 JAM
            &nbsp;·&nbsp; GARANSI RESMI &nbsp;·&nbsp;&nbsp;
          </span>
        </div>
      </div>

      <div class="hero__inner">
        <span class="hero__badge">Portofolio Instalasi</span>

        <h1 class="hero__title">
          Standar<br />
          <em class="hero__accent">Enterprise.</em><br />
          Harga<br />
          Terjangkau.
        </h1>

        <p class="hero__sub">
          1.200+ titik kamera terpasang. Ditenagai oleh tim teknisi bersertifikasi <strong>Padjajaran CCTV</strong>, kami tidak hanya menjual produk — kami mendesain <strong>rasa aman</strong> untuk Anda.
        </p>

        <div class="hero__cta">
          <NuxtLink to="/services/booking" class="btn btn--primary">
            Konsultasi Gratis
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
          </NuxtLink>
          <a href="#featured" class="btn btn--ghost">
            Lihat Hasil Kerja
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
          </a>
        </div>

        <div class="hero__stats">
          <div class="stat">
            <span class="stat__num">1.200<sup>+</sup></span>
            <span class="stat__label">Titik Kamera</span>
          </div>
          <div class="stat__div"></div>
          <div class="stat">
            <span class="stat__num">99<sup>%</sup></span>
            <span class="stat__label">Kepuasan Klien</span>
          </div>
          <div class="stat__div"></div>
          <div class="stat">
            <span class="stat__num">12<sup>+</sup></span>
            <span class="stat__label">Tahun Pengalaman</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         FEATURED CASE STUDY
    ══════════════════════════════════════════════════════════════ -->
    <section id="featured" class="featured">
      <div class="section-label">Case Study Unggulan</div>

      <div v-if="isPending" class="featured__skeleton"></div>

      <div v-else-if="data?.featured" class="featured__card">
        <div class="featured__head">
          <span class="featured__badge">{{ data.featured.client_type }}</span>
          <h2 class="featured__title">{{ data.featured.title }}</h2>
        </div>

        <div
          v-if="featuredBeforeImage || featuredAfterImage"
          class="ba-slider"
          @mousedown="dragging = true"
          @mouseup="dragging = false"
          @mouseleave="dragging = false"
          @mousemove="onSliderMove"
          @touchstart="dragging = true"
          @touchend="dragging = false"
          @touchmove="onSliderMove"
        >
          <img
            v-if="featuredAfterImage"
            :src="featuredAfterImage"
            alt="Sesudah instalasi"
            class="ba-slider__img ba-slider__img--after"
          />
          <div class="ba-slider__before" :style="{ width: sliderPos + '%' }">
            <img
              v-if="featuredBeforeImage"
              :src="featuredBeforeImage"
              alt="Sebelum instalasi"
              class="ba-slider__img"
            />
          </div>
          <div class="ba-handle" :style="{ left: sliderPos + '%' }">
            <span class="ba-handle__label ba-handle__label--l">Sebelum</span>
            <div class="ba-handle__line"></div>
            <div class="ba-handle__knob">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path d="M9 18l-6-6 6-6M15 6l6 6-6 6" />
              </svg>
            </div>
            <div class="ba-handle__line"></div>
            <span class="ba-handle__label ba-handle__label--r">Sesudah</span>
          </div>
        </div>

        <div class="psr-grid">
          <div class="psr-card psr-card--problem">
            <span class="psr-card__icon">⚠</span>
            <h3 class="psr-card__head">Masalah</h3>
            <p class="psr-card__body">{{ data.featured.problem }}</p>
          </div>
          <div class="psr-card psr-card--solution">
            <span class="psr-card__icon">⚙</span>
            <h3 class="psr-card__head">Solusi</h3>
            <p class="psr-card__body">{{ data.featured.solution }}</p>
          </div>
          <div class="psr-card psr-card--result">
            <span class="psr-card__icon">✓</span>
            <h3 class="psr-card__head">Hasil</h3>
            <p class="psr-card__body">{{ data.featured.result }}</p>
          </div>
        </div>

        <div class="featured__foot">
          <NuxtLink :to="`/portfolio/${data.featured.id}`" class="btn btn--outline">
            Lihat Detail Project Ini
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
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         GALLERY GRID
    ══════════════════════════════════════════════════════════════ -->
    <section class="gallery">
      <div class="gallery__head">
        <div class="section-label">Galeri Project</div>
        <h2 class="gallery__title">Rekam Jejak Kami</h2>
        <p class="gallery__sub">
          Dari perumahan hingga fasilitas industri — setiap project dikerjakan dengan
          standar kelistrikan dan kerapian instalasi tertinggi.
        </p>
      </div>

      <div class="cat-tabs" role="tablist">
        <button
          v-for="cat in categories"
          :key="cat.value"
          class="cat-tab"
          :class="{ 'cat-tab--active': activeCategory === cat.value }"
          role="tab"
          :aria-selected="activeCategory === cat.value"
          @click="activeCategory = cat.value"
        >
          {{ cat.label }}
        </button>
      </div>

      <div v-if="isPending" class="proj-grid">
        <div v-for="i in 6" :key="i" class="proj-card proj-card--skel"></div>
      </div>

      <div v-else-if="filteredProjects.length" class="proj-grid">
        <NuxtLink
          v-for="project in filteredProjects"
          :key="project.id"
          :to="`/portfolio/${project.id}`"
          class="proj-card"
        >
          <div class="proj-card__img-wrap">
            <img
              v-if="project.cover_image"
              :src="project.cover_image"
              :alt="project.title"
              class="proj-card__img"
              loading="lazy"
            />
            <div v-else class="proj-card__img-placeholder">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1"
              >
                <circle cx="11" cy="11" r="8" />
                <circle cx="11" cy="11" r="3" />
                <path d="M21 21l-4.35-4.35" />
              </svg>
            </div>
            <div class="proj-card__overlay"></div>
            <span class="proj-card__cat">{{ project.category }}</span>
            <span v-if="project.is_featured" class="proj-card__feat">★ Featured</span>
          </div>
          <div class="proj-card__body">
            <h3 class="proj-card__title">{{ project.title }}</h3>
            <div class="proj-card__meta">
              <span class="proj-card__loc">
                <svg
                  width="12"
                  height="12"
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
              </span>
              <span class="proj-card__cam">
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M23 7l-7 5 7 5V7z" />
                  <rect x="1" y="5" width="15" height="14" rx="2" />
                </svg>
                {{ project.cameras }} kamera
              </span>
            </div>
            <div class="proj-card__arrow">
              Lihat Detail
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </NuxtLink>
      </div>

      <div v-else class="gallery__empty">
        <span>Belum ada project dalam kategori ini.</span>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         TESTIMONIAL SWIPER
    ══════════════════════════════════════════════════════════════ -->
    <section class="testi-section">
      <div class="testi-section__bg" aria-hidden="true"></div>

      <div class="testi-section__inner">
        <div class="section-label section-label--light">Kata Klien</div>
        <h2 class="testi-section__title">Kepuasan Mereka,<br />Reputasi Kami.</h2>

        <div v-if="isPending" class="testi-skel-row">
          <div v-for="i in 3" :key="i" class="testi-skel"></div>
        </div>

        <!--
          ClientOnly wajib: Swiper Web Components tidak bisa di-SSR.
          Tanpa ini, Nuxt akan mencoba render swiper-container di server
          dan tetap error walau isCustomElement sudah di-set.
        -->
        <ClientOnly v-else-if="data?.testimonials?.length">
          <swiper-container
            :slides-per-view="1"
            :space-between="24"
            :grab-cursor="true"
            :loop="true"
            :autoplay-delay="4500"
            :autoplay-disable-on-interaction="true"
            :pagination="true"
            :breakpoints.prop="{
              640: { slidesPerView: 1.2 },
              768: { slidesPerView: 2 },
              1024: { slidesPerView: 3 },
            }"
            class="testi-swiper"
          >
            <swiper-slide
              v-for="testi in data.testimonials"
              :key="testi.id"
              class="testi-slide"
            >
              <div class="testi-card">
                <div class="testi-card__stars">
                  <span v-for="s in testi.rating" :key="s" class="star">★</span>
                  <span
                    v-for="s in 5 - testi.rating"
                    :key="'e' + s"
                    class="star star--empty"
                    >★</span
                  >
                </div>
                <blockquote class="testi-card__quote">"{{ testi.text }}"</blockquote>
                <div class="testi-card__author">
                  <div class="testi-card__avatar">
                    {{ testi.name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="testi-card__name">{{ testi.name }}</div>
                    <div v-if="testi.role" class="testi-card__role">{{ testi.role }}</div>
                  </div>
                </div>
              </div>
            </swiper-slide>
          </swiper-container>

          <!-- Fallback saat JS belum load (SSR hydration gap) -->
          <template #fallback>
            <div class="testi-skel-row">
              <div v-for="i in 3" :key="i" class="testi-skel"></div>
            </div>
          </template>
        </ClientOnly>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         BOTTOM CTA
    ══════════════════════════════════════════════════════════════ -->
    <section class="bottom-cta">
      <div class="bottom-cta__inner">
        <div class="bottom-cta__label">Mulai Sekarang</div>
        <h2 class="bottom-cta__title">Butuh Sistem Keamanan<br />Seperti di Atas?</h2>
        <p class="bottom-cta__sub">
          Jadwalkan survey lokasi bersama teknisi resmi <strong>Padjajaran CCTV</strong>. Kami hitung kebutuhan kabel, posisi kamera
          ideal, dan estimasi biaya — transparan tanpa komitmen.
        </p>
        <div class="bottom-cta__btns">
          <NuxtLink to="/services/booking" class="btn btn--primary btn--lg">
            Jadwalkan Survey Gratis
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </NuxtLink>
          <a :href="whatsappConsultUrl" target="_blank" rel="noopener" class="btn btn--wa btn--lg">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
            </svg>
            Chat WhatsApp Teknisi
          </a>
          <NuxtLink to="/kategori/paket-cctv" class="btn btn--outline btn--lg">
            Lihat Paket Pemasangan
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         MOBILE STICKY CTA
    ══════════════════════════════════════════════════════════════ -->
    <div class="mobile-cta" role="complementary" aria-label="Tombol aksi portofolio">
      <NuxtLink to="/services/booking" class="mobile-cta__btn mobile-cta__btn--primary">
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
      </NuxtLink>
      <a :href="whatsappConsultUrl" target="_blank" rel="noopener" class="mobile-cta__btn mobile-cta__btn--wa">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
        </svg>
        <span>Tanya Teknisi</span>
      </a>
    </div>
  </main>
</template>

<style scoped>
/* ══════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   @import DIHAPUS dari sini — sudah dipindah ke nuxt.config.ts (app.head)
══════════════════════════════════════════════════════════════════ */
.portfolio-root {
  --c-bg: #0a0a0a;
  --c-surface: #111111;
  --c-border: #222222;
  --c-muted: #444444;
  --c-text: #f0ede8;
  --c-sub: #888888;
  --c-red: #e8001d;
  --c-red-dim: #6b0010;
  --c-gold: #c9a84c;

  --f-display: "Barlow Condensed", "Impact", sans-serif;
  --f-body: "DM Sans", "Helvetica Neue", sans-serif;
  --f-mono: "JetBrains Mono", monospace;

  background: var(--c-bg);
  color: var(--c-text);
  font-family: var(--f-body);
  min-height: 100vh;
  overflow-x: hidden;
  padding-bottom: 80px;
}

@media (min-width: 768px) {
  .portfolio-root {
    padding-bottom: 0;
  }
}

/* ── Utility ─────────────────────────────────────────────────── */
.section-label {
  font-family: var(--f-mono);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--c-red);
  margin-bottom: 1rem;
}
.section-label--light {
  color: #ff6b7a;
}

/* ── Buttons ─────────────────────────────────────────────────── */
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
  transition: all 0.18s ease;
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
  padding: 1.125rem 2.5rem;
  font-size: 0.8rem;
}

/* ══════════════════════════════════════════════════════════════════
   HERO
══════════════════════════════════════════════════════════════════ */
.hero {
  position: relative;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  background: var(--c-bg);
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
  width: 700px;
  height: 700px;
  background: radial-gradient(circle, rgba(232, 0, 29, 0.15) 0%, transparent 65%);
  pointer-events: none;
}

.ticker {
  position: relative;
  z-index: 2;
  overflow: hidden;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--c-border);
}
.ticker__track {
  display: flex;
  white-space: nowrap;
  animation: ticker-scroll 28s linear infinite;
  font-family: var(--f-mono);
  font-size: 0.6rem;
  letter-spacing: 0.15em;
  color: var(--c-muted);
}
@keyframes ticker-scroll {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-50%);
  }
}

.hero__inner {
  position: relative;
  z-index: 3;
  max-width: 1200px;
  margin: 0 auto;
  padding: 5rem 2rem 6rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.hero__badge {
  display: inline-block;
  font-family: var(--f-mono);
  font-size: 0.6rem;
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
  font-size: clamp(4rem, 12vw, 9rem);
  font-weight: 900;
  line-height: 0.92;
  text-transform: uppercase;
  letter-spacing: -0.01em;
  margin: 0 0 2rem;
  color: var(--c-text);
}
.hero__accent {
  font-style: italic;
  color: var(--c-red);
}
.hero__sub {
  max-width: 520px;
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--c-sub);
  margin-bottom: 2.5rem;
}
.hero__sub strong {
  color: var(--c-text);
  font-weight: 600;
}
.hero__cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 3.5rem;
}

.hero__stats {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--c-border);
}
.stat__num {
  display: block;
  font-family: var(--f-display);
  font-size: 2.5rem;
  font-weight: 900;
  line-height: 1;
  color: var(--c-text);
}
.stat__num sup {
  font-size: 1.2rem;
  color: var(--c-red);
}
.stat__label {
  display: block;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-sub);
  margin-top: 0.2rem;
}
.stat__div {
  width: 1px;
  height: 2.5rem;
  background: var(--c-border);
}

/* ══════════════════════════════════════════════════════════════════
   FEATURED
══════════════════════════════════════════════════════════════════ */
.featured {
  max-width: 1200px;
  margin: 0 auto;
  padding: 5rem 2rem;
}
.featured__skeleton {
  height: 600px;
  background: linear-gradient(
    90deg,
    var(--c-surface) 25%,
    #1a1a1a 50%,
    var(--c-surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}
.featured__card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
}
.featured__head {
  padding: 2.5rem 2.5rem 2rem;
  border-bottom: 1px solid var(--c-border);
}
.featured__badge {
  font-family: var(--f-mono);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--c-red);
  background: rgba(232, 0, 29, 0.08);
  padding: 0.25rem 0.6rem;
  display: inline-block;
  margin-bottom: 0.75rem;
}
.featured__title {
  font-family: var(--f-display);
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 900;
  text-transform: uppercase;
  line-height: 1.1;
  letter-spacing: 0.01em;
  color: var(--c-text);
  margin: 0;
}

/* Before/After */
.ba-slider {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 7;
  overflow: hidden;
  cursor: ew-resize;
  user-select: none;
}
.ba-slider__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.ba-slider__before {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  overflow: hidden;
}
.ba-slider__before .ba-slider__img {
  position: relative;
  width: auto;
  min-width: 100vw;
}
.ba-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
  z-index: 5;
}
.ba-handle__line {
  flex: 1;
  width: 2px;
  background: #fff;
}
.ba-handle__knob {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--c-red);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  color: #fff;
}
.ba-handle__label {
  position: absolute;
  top: 12px;
  font-family: var(--f-mono);
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 0.2rem 0.5rem;
  white-space: nowrap;
}
.ba-handle__label--l {
  right: calc(100% + 8px);
}
.ba-handle__label--r {
  left: calc(100% + 8px);
}

/* PSR */
.psr-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid var(--c-border);
}
.psr-card {
  padding: 2rem;
  border-right: 1px solid var(--c-border);
}
.psr-card:last-child {
  border-right: none;
}
.psr-card__icon {
  display: block;
  font-size: 1.4rem;
  margin-bottom: 0.75rem;
}
.psr-card--problem .psr-card__icon {
  color: #e8a200;
}
.psr-card--solution .psr-card__icon {
  color: #4488ff;
}
.psr-card--result .psr-card__icon {
  color: #00b86b;
}
.psr-card__head {
  font-family: var(--f-display);
  font-size: 0.9rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0 0 0.75rem;
  color: var(--c-sub);
}
.psr-card__body {
  font-size: 0.9rem;
  line-height: 1.65;
  color: var(--c-sub);
  margin: 0;
}
.featured__foot {
  padding: 1.5rem 2.5rem;
  border-top: 1px solid var(--c-border);
  display: flex;
  justify-content: flex-end;
}

/* ══════════════════════════════════════════════════════════════════
   GALLERY
══════════════════════════════════════════════════════════════════ */
.gallery {
  padding: 5rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
.gallery__head {
  text-align: center;
  margin-bottom: 3rem;
}
.gallery__title {
  font-family: var(--f-display);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.01em;
  margin: 0 0 1rem;
}
.gallery__sub {
  color: var(--c-sub);
  max-width: 520px;
  margin: 0 auto;
  font-size: 0.95rem;
  line-height: 1.7;
}

.cat-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2.5rem;
  justify-content: center;
}
.cat-tab {
  font-family: var(--f-mono);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 0.5rem 1rem;
  border: 1px solid var(--c-border);
  background: transparent;
  color: var(--c-sub);
  cursor: pointer;
  transition: all 0.15s;
}
.cat-tab:hover {
  border-color: var(--c-muted);
  color: var(--c-text);
}
.cat-tab--active {
  background: var(--c-red);
  border-color: var(--c-red);
  color: #fff;
}

.proj-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
}
.proj-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: border-color 0.2s, transform 0.2s;
}
.proj-card:hover {
  border-color: var(--c-muted);
  transform: translateY(-3px);
}
.proj-card--skel {
  height: 350px;
  background: linear-gradient(
    90deg,
    var(--c-surface) 25%,
    #1a1a1a 50%,
    var(--c-surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.proj-card__img-wrap {
  position: relative;
  aspect-ratio: 16/10;
  overflow: hidden;
  background: #1a1a1a;
}
.proj-card__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.proj-card:hover .proj-card__img {
  transform: scale(1.04);
}
.proj-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, transparent 50%);
}
.proj-card__img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--c-border);
}
.proj-card__cat {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  font-family: var(--f-mono);
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  background: rgba(0, 0, 0, 0.75);
  color: var(--c-sub);
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--c-border);
}
.proj-card__feat {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  font-family: var(--f-mono);
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  background: var(--c-red);
  color: #fff;
  padding: 0.25rem 0.5rem;
}
.proj-card__body {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.proj-card__title {
  font-family: var(--f-display);
  font-size: 1.05rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  line-height: 1.2;
  margin: 0;
  color: var(--c-text);
}
.proj-card__meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
.proj-card__loc,
.proj-card__cam {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  color: var(--c-sub);
}
.proj-card__arrow {
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid var(--c-border);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-red);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: gap 0.2s;
}
.proj-card:hover .proj-card__arrow {
  gap: 0.7rem;
}
.gallery__empty {
  text-align: center;
  padding: 4rem;
  color: var(--c-sub);
  font-size: 0.9rem;
  border: 1px dashed var(--c-border);
}

/* ══════════════════════════════════════════════════════════════════
   TESTIMONIALS
══════════════════════════════════════════════════════════════════ */
.testi-section {
  position: relative;
  overflow: hidden;
  background: #0d0d0d;
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
  padding: 5rem 0;
}
.testi-section__bg {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 59px,
      var(--c-border) 60px
    ),
    repeating-linear-gradient(90deg, transparent, transparent 59px, var(--c-border) 60px);
  opacity: 0.3;
  pointer-events: none;
}
.testi-section__inner {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}
.testi-section__title {
  font-family: var(--f-display);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 900;
  text-transform: uppercase;
  line-height: 1;
  margin: 0 0 3rem;
  color: var(--c-text);
}
.testi-skel-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.testi-skel {
  height: 200px;
  background: linear-gradient(90deg, #141414 25%, #1c1c1c 50%, #141414 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.testi-swiper-wrap {
  overflow: hidden;
}
.testi-swiper {
  overflow: visible !important;
}
.testi-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  padding: 1.75rem;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: border-color 0.2s;
}
.testi-card:hover {
  border-color: var(--c-muted);
}
.testi-card__stars {
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
.testi-card__quote {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--c-sub);
  margin: 0;
  flex: 1;
  font-style: normal;
}
.testi-card__author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-top: 1px solid var(--c-border);
  padding-top: 1rem;
}
.testi-card__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--c-red-dim);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--f-display);
  font-size: 1rem;
  font-weight: 900;
  color: var(--c-red);
  flex-shrink: 0;
}
.testi-card__name {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--c-text);
}
.testi-card__role {
  font-size: 0.7rem;
  color: var(--c-sub);
  margin-top: 0.1rem;
}

swiper-container::part(pagination) {
  margin-top: 2rem;
}
swiper-container::part(bullet) {
  background: var(--c-border);
  opacity: 1;
  width: 6px;
  height: 6px;
}
swiper-container::part(bullet-active) {
  background: var(--c-red);
  width: 20px;
  border-radius: 3px;
}

/* ══════════════════════════════════════════════════════════════════
   BOTTOM CTA
══════════════════════════════════════════════════════════════════ */
.bottom-cta {
  padding: 6rem 2rem;
  text-align: center;
  background: var(--c-bg);
}
.bottom-cta__inner {
  max-width: 720px;
  margin: 0 auto;
}
.bottom-cta__label {
  font-family: var(--f-mono);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--c-red);
  margin-bottom: 1.25rem;
}
.bottom-cta__title {
  font-family: var(--f-display);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 900;
  text-transform: uppercase;
  line-height: 1;
  margin: 0 0 1.25rem;
  color: var(--c-text);
}
.bottom-cta__sub {
  color: var(--c-sub);
  font-size: 1rem;
  line-height: 1.7;
  margin-bottom: 2.5rem;
}
.bottom-cta__btns {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

.btn--wa {
  background: #03ac0e;
  color: #fff;
  border: 1px solid #03ac0e;
}
.btn--wa:hover {
  background: #028a0b;
  border-color: #028a0b;
  color: #fff;
}

/* ── Mobile Sticky CTA ────────────────────────────────────────── */
.mobile-cta {
  display: flex;
  gap: 0.5rem;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.75rem;
  padding-bottom: calc(0.75rem + env(safe-area-inset-bottom));
  background: rgba(10, 10, 10, 0.94);
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
  padding: 0.85rem 1rem;
  border: none;
  cursor: pointer;
  text-decoration: none;
  font-family: var(--f-body);
  font-size: 0.68rem;
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
.mobile-cta__btn--wa {
  background: #03ac0e;
  color: #fff;
}

/* ══════════════════════════════════════════════════════════════════
   SHIMMER
══════════════════════════════════════════════════════════════════ */
@keyframes shimmer {
  from {
    background-position: 200% 0;
  }
  to {
    background-position: -200% 0;
  }
}

/* ══════════════════════════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .hero__stats {
    gap: 1.25rem;
  }
  .psr-grid {
    grid-template-columns: 1fr;
  }
  .psr-card {
    border-right: none;
    border-bottom: 1px solid var(--c-border);
  }
  .psr-card:last-child {
    border-bottom: none;
  }
  .ba-slider {
    aspect-ratio: 4/3;
  }
  .proj-grid {
    grid-template-columns: 1fr;
  }
  .testi-skel-row {
    grid-template-columns: 1fr;
  }
  .featured__head {
    padding: 1.5rem;
  }
  .featured__foot {
    padding: 1rem 1.5rem;
  }
  .psr-card {
    padding: 1.5rem;
  }
  .bottom-cta__btns {
    flex-direction: column;
    align-items: center;
  }
}
</style>
