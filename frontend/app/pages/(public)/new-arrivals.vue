<script setup lang="ts">
/**
 * Halaman New Arrivals - PasarCctv
 * Halaman ini bertindak sebagai parent yang mengontrol state awal filtering
 */
import ListProduct from '~/components/product/ListProduct.vue'

// 1. Meta Data & SEO
const pageTitle = "New Arrivals CCTV & Keamanan"
const pageDescription = "Jelajahi koleksi produk keamanan terbaru di PasarCctv. Dari IP Camera AI hingga NVR tercanggih, temukan teknologi terbaru untuk keamanan Anda."
const siteName = "PasarCctv"

useSeoMeta({
  title: `${pageTitle} - ${siteName}`,
  ogTitle: `${pageTitle} - ${siteName}`,
  description: pageDescription,
  ogDescription: pageDescription,
  ogImage: 'https://images.unsplash.com/photo-1557862921-37829c790f19?q=80&w=1200',
  twitterCard: 'summary_large_image',
})

// 2. Konfigurasi Halaman
// Pastikan ID 'new_arrivals' ada di dalam array categories pada komponen ListProduct.vue
const autoCheckCategory = ['new_arrivals']
const defaultSorting = "terbaru"

const breadcrumbLinks = [
  { label: 'Beranda', to: '/' },
  { label: 'Produk', to: '/products' },
  { label: 'New Arrivals' }
]

const heroImage = "https://images.unsplash.com/photo-1557862921-37829c790f19?q=80&w=1200"
</script>

<template>
  <div class="new-arrivals-page">
    <Head>
      <link rel="canonical" href="https://pasarcctv.com/new-arrivals" />
    </Head>

    <ListProduct
      :title="pageTitle"
      :description="pageDescription"
      :breadcrumbs="breadcrumbLinks"
      :image="heroImage"
      :initial-sort="defaultSorting"
      :initial-categories="autoCheckCategory"
    />
  </div>
</template>

<style scoped>
/* Transisi halaman halus */
.new-arrivals-page {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
