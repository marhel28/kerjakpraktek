<script setup lang="ts">
import CardPerItems from '~/components/CardPerItems.vue'

interface Recommendation {
  uuid: string
  slug?: string
  title: string
  image?: string
  price: number
  original_price?: number
  discount_percentage?: number
  terjual?: number
  category?: string
  subcategory?: string
  brand?: string
  type?: string
  specs?: Record<string, any>
}

defineProps<{
  items: Recommendation[]
}>()
</script>

<template>
  <!--
    <section> dengan aria-labelledby + ItemList schema:
    Google dapat tampilkan produk terkait sebagai rich result
  -->
  <section
    v-if="items.length > 0"
    aria-labelledby="rec-heading"
    itemscope
    itemtype="https://schema.org/ItemList"
    class="rec-section"
  >
    <meta itemprop="name" content="Produk Serupa" />

    <!-- ── Header ──────────────────────────────────────────────── -->
    <div class="rec-header">
      <div class="rec-header__left">
        <!-- Aksen vertikal khas Tokopedia -->
        <span class="rec-header__accent" aria-hidden="true" />
        <h2 id="rec-heading" class="rec-header__title">
          Produk Serupa
        </h2>
      </div>

      <NuxtLink
        to="/search"
        class="rec-header__link"
        aria-label="Lihat semua produk serupa"
      >
        Lihat Semua
        <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" aria-hidden="true" />
      </NuxtLink>
    </div>

    <!-- ── Grid produk ──────────────────────────────────────────── -->
    <div
      class="rec-grid"
      role="list"
      aria-label="Daftar produk serupa"
    >
      <div
        v-for="(rec, index) in items"
        :key="rec.uuid"
        class="rec-item"
        :style="{ animationDelay: `${index * 45}ms` }"
        itemprop="itemListElement"
        itemscope
        itemtype="https://schema.org/ListItem"
        role="listitem"
      >
        <meta itemprop="position" :content="String(index + 1)" />
        <CardPerItems
          :uuid="rec.uuid"
          :slug="rec.slug"
          :image="rec.image || '/images/no-image.webp'"
          :brand="rec.brand || 'No Brand'"
          :title="rec.title"
          :price="rec.price"
          :original_price="rec.original_price || 0"
          :discount_percentage="rec.discount_percentage || 0"
          :terjual="rec.terjual || 0"
          :category="rec.category || 'general'"
          :subcategory="rec.subcategory || ''"
          :type="rec.type || ''"
          :specs="rec.specs || {}"
          class="h-full"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ── Section wrapper ─────────────────────────────────────────────── */
.rec-section {
  margin-top: 3rem;
  margin-bottom: 2rem;
}

/* ── Header ──────────────────────────────────────────────────────── */
.rec-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1.5px solid #f3f4f6;
}

.rec-header__left {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

/* Aksen vertikal merah-hijau khas Tokopedia */
.rec-header__accent {
  display: block;
  width: 4px;
  height: 1.4rem;
  border-radius: 4px;
  background: linear-gradient(180deg, #42b549 0%, #00aa5b 100%);
  flex-shrink: 0;
}

.rec-header__title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #111827;
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.rec-header__link {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #00aa5b;
  white-space: nowrap;
  transition: color 0.15s, gap 0.15s;
  flex-shrink: 0;
}
.rec-header__link:hover {
  color: #008f4c;
  gap: 5px;
}

/* ── Grid ────────────────────────────────────────────────────────── */
.rec-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .rec-grid { grid-template-columns: repeat(3, 1fr); gap: 0.875rem; }
}
@media (min-width: 768px) {
  .rec-grid { grid-template-columns: repeat(4, 1fr); }
}
@media (min-width: 1024px) {
  .rec-grid { grid-template-columns: repeat(5, 1fr); gap: 1rem; }
}

/* ── Item animasi masuk ──────────────────────────────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

.rec-item {
  opacity: 0;
  animation: fadeUp 0.38s ease-out forwards;
  display: flex;
  flex-direction: column;
}

/* ── Reduced motion ──────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .rec-item { animation: none; opacity: 1; }
}
</style>