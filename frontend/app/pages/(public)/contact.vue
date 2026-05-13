<script setup lang="ts">
import PageBanner from '~/components/PageBanner.vue'

// ==========================================
// 1. DATA KONTEN HALAMAN & SEO
// ==========================================
const pageTitle = "Hubungi Kami"
const pageDescription = "Punya pertanyaan seputar produk CCTV, permintaan instalasi, atau butuh bantuan teknis? Tim kami siap membantu Anda 24/7."

const breadcrumbLinks = [
  { label: 'Home', to: '/' },
  { label: 'Kontak Kami' }
]

// Gambar banner bernuansa customer service / office yang elegan
const heroImage = "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1200"

// ==========================================
// 2. DATA KONTAK & SOSIAL MEDIA
// ==========================================
const contactMethods = [
  {
    id: 'whatsapp',
    name: 'WhatsApp',
    value: '+62 812-3456-7890',
    link: 'https://wa.me/6281234567890',
    icon: 'ph:whatsapp-logo-duotone',
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-50'
  },
  {
    id: 'email',
    name: 'Email',
    value: 'cs@pasarcctv.com',
    link: 'mailto:cs@pasarcctv.com',
    icon: 'ph:envelope-duotone',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50'
  }
]

const socialMedias = [
  {
    id: 'instagram',
    name: 'Instagram',
    handle: '@pasarcctv',
    link: 'https://instagram.com/pasarcctv',
    icon: 'ph:instagram-logo-duotone',
    color: 'text-pink-600',
    bgColor: 'bg-pink-50'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    handle: '@pasarcctv.id',
    link: 'https://tiktok.com/@pasarcctv.id',
    icon: 'ph:tiktok-logo-duotone',
    color: 'text-gray-900',
    bgColor: 'bg-gray-100'
  },
  {
    id: 'facebook',
    name: 'Facebook',
    handle: 'PasarCctv Official',
    link: 'https://facebook.com/pasarcctv',
    icon: 'ph:facebook-logo-duotone',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50'
  }
]
</script>

<template>
  <div class="w-full bg-gray-50/30 pb-24 min-h-screen">
    <Title>Kontak Kami - PasarCctv</Title>
    <Meta name="description" :content="pageDescription" />

    <PageBanner
      :title="pageTitle"
      :description="pageDescription"
      :breadcrumbs="breadcrumbLinks"
      :image="heroImage"
    />

    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
      <div class="flex flex-col items-center text-center mb-16">
        <h2 class="text-3xl md:text-4xl font-extrabold text-[#1d1d1f] tracking-tight mb-4">
          Mari Berbincang.
        </h2>
        <p class="text-gray-500 text-lg leading-relaxed max-w-2xl">
          Pilih platform komunikasi yang paling nyaman bagi Anda. Kami selalu berusaha merespons secepat mungkin pada jam kerja untuk memberikan solusi keamanan terbaik.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 mb-16">
        <NuxtLink
          v-for="contact in contactMethods"
          :key="contact.id"
          :to="contact.link"
          target="_blank"
          class="group flex flex-col items-center text-center p-8 lg:p-10 rounded-3xl bg-white border border-gray-100 shadow-sm transition-all duration-300 hover:shadow-[0_20px_40px_rgb(0,0,0,0.04)] hover:-translate-y-1 hover:border-gray-200"
        >
          <div :class="`w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3 ${contact.bgColor}`">
            <Icon :name="contact.icon" :class="`w-8 h-8 ${contact.color}`" />
          </div>
          <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-2">{{ contact.name }}</h3>
          <p class="text-xl lg:text-2xl font-bold text-[#1d1d1f]">{{ contact.value }}</p>
        </NuxtLink>
      </div>

      <div class="bg-white rounded-3xl p-8 lg:p-12 border border-gray-100 shadow-sm">
        <div class="text-center mb-10">
          <h3 class="text-2xl font-bold text-[#1d1d1f] mb-3">Ikuti Kami di Sosial Media</h3>
          <p class="text-gray-500">Dapatkan update promo, edukasi keamanan, dan portofolio instalasi terbaru.</p>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <NuxtLink
            v-for="social in socialMedias"
            :key="social.id"
            :to="social.link"
            target="_blank"
            class="group flex flex-col items-center text-center p-6 rounded-2xl border border-gray-100 bg-gray-50/50 transition-all duration-300 hover:bg-white hover:shadow-[0_10px_30px_rgb(0,0,0,0.05)] hover:-translate-y-1 hover:border-gray-200"
          >
            <div :class="`w-12 h-12 rounded-full flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110 ${social.bgColor}`">
              <Icon :name="social.icon" :class="`w-6 h-6 ${social.color}`" />
            </div>
            <h4 class="text-base font-bold text-[#1d1d1f] mb-1">{{ social.name }}</h4>
            <p class="text-sm text-gray-500 font-medium">{{ social.handle }}</p>
          </NuxtLink>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
div, section, main {
  font-family: var(--font-sans);
}
</style>
