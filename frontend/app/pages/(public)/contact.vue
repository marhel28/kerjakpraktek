<script setup lang="ts">
import { ref } from 'vue'
import PageBanner from '~/components/PageBanner.vue'

// ==========================================
// 1. DATA KONTEN HALAMAN & SEO
// ==========================================
const pageTitle = "Hubungi Kami"
const pageDescription = "Punya pertanyaan seputar produk CCTV, permintaan instalasi, atau butuh bantuan teknis? Tim Solvi Store siap membantu Anda 24/7."

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
    name: 'Email (Gmail)',
    value: 'cs@solvistore.com',
    link: 'mailto:cs@solvistore.com',
    icon: 'ph:envelope-duotone',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50'
  }
]

const socialMedias = [
  {
    id: 'instagram',
    name: 'Instagram',
    handle: '@solvi.store',
    link: 'https://instagram.com/solvi.store',
    icon: 'ph:instagram-logo-duotone',
    color: 'text-pink-600',
    bgColor: 'bg-pink-50'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    handle: '@solvi.cctv',
    link: 'https://tiktok.com/@solvi.cctv',
    icon: 'ph:tiktok-logo-duotone',
    color: 'text-gray-900',
    bgColor: 'bg-gray-100'
  },
  {
    id: 'facebook',
    name: 'Facebook',
    handle: 'Solvi Security Store',
    link: 'https://facebook.com/solvistore',
    icon: 'ph:facebook-logo-duotone',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50'
  }
]

// ==========================================
// 3. STATE UNTUK FORMULIR
// ==========================================
const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const isSubmitting = ref(false)

const submitForm = async () => {
  isSubmitting.value = true
  // Simulasi pengiriman data ke API (delay 1.5 detik)
  await new Promise(resolve => setTimeout(resolve, 1500))
  alert('Pesan berhasil dikirim! Tim kami akan segera membalas email Anda.')

  // Reset form
  form.value = { name: '', email: '', subject: '', message: '' }
  isSubmitting.value = false
}
</script>

<template>
  <div class="w-full bg-white pb-24">
    <Title>Kontak Kami - Solvi Store CCTV</Title>
    <Meta name="description" :content="pageDescription" />

    <PageBanner
      :title="pageTitle"
      :description="pageDescription"
      :breadcrumbs="breadcrumbLinks"
      :image="heroImage"
    />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-20">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24">

        <section class="flex flex-col gap-10">

          <div>
            <h2 class="text-3xl font-extrabold text-[#1d1d1f] tracking-tight mb-4">Mari Berbincang.</h2>
            <p class="text-gray-500 text-lg leading-relaxed">
              Pilih platform komunikasi yang paling nyaman bagi Anda. Kami selalu berusaha merespons secepat mungkin di jam kerja.
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <NuxtLink
              v-for="contact in contactMethods"
              :key="contact.id"
              :to="contact.link"
              target="_blank"
              class="group flex flex-col p-6 rounded-2xl border border-gray-200 transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] hover:-translate-y-1 hover:border-gray-300"
            >
              <div :class="`w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110 ${contact.bgColor}`">
                <Icon :name="contact.icon" :class="`w-6 h-6 ${contact.color}`" />
              </div>
              <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">{{ contact.name }}</h3>
              <p class="text-lg font-semibold text-[#1d1d1f]">{{ contact.value }}</p>
            </NuxtLink>
          </div>

          <hr class="border-gray-100" />

          <div>
            <h3 class="text-xl font-bold text-[#1d1d1f] mb-6">Ikuti Kami di Sosial Media</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
              <NuxtLink
                v-for="social in socialMedias"
                :key="social.id"
                :to="social.link"
                target="_blank"
                class="group flex flex-col items-center text-center p-6 rounded-2xl border border-gray-200 transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] hover:-translate-y-1 hover:border-gray-300 bg-gray-50/50 hover:bg-white"
              >
                <div :class="`w-10 h-10 rounded-full flex items-center justify-center mb-3 ${social.bgColor}`">
                  <Icon :name="social.icon" :class="`w-5 h-5 ${social.color}`" />
                </div>
                <h4 class="text-sm font-bold text-[#1d1d1f] mb-0.5">{{ social.name }}</h4>
                <p class="text-xs text-gray-500">{{ social.handle }}</p>
              </NuxtLink>
            </div>
          </div>

        </section>

        <section class="bg-gray-50 rounded-3xl p-8 lg:p-12 border border-gray-100 h-fit">
          <h3 class="text-2xl font-bold text-[#1d1d1f] mb-2">Kirim Pesan Langsung</h3>
          <p class="text-sm text-gray-500 mb-8">
            Isi formulir di bawah ini dan representatif kami akan menghubungi Anda melalui email.
          </p>

          <form @submit.prevent="submitForm" class="flex flex-col gap-6">

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-semibold text-[#1d1d1f] mb-2">Nama Lengkap</label>
                <UInput
                  v-model="form.name"
                  icon="i-heroicons-user"
                  placeholder="Cth: Budi Santoso"
                  size="lg"
                  color="gray"
                  variant="outline"
                  required
                  :ui="{ rounded: 'rounded-xl' }"
                />
              </div>

              <div>
                <label class="block text-sm font-semibold text-[#1d1d1f] mb-2">Alamat Email</label>
                <UInput
                  v-model="form.email"
                  type="email"
                  icon="i-heroicons-envelope"
                  placeholder="Cth: budi@gmail.com"
                  size="lg"
                  color="gray"
                  variant="outline"
                  required
                  :ui="{ rounded: 'rounded-xl' }"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-[#1d1d1f] mb-2">Subjek / Keperluan</label>
              <UInput
                v-model="form.subject"
                placeholder="Cth: Penawaran Harga Pemasangan 8 Titik CCTV"
                size="lg"
                color="gray"
                variant="outline"
                required
                :ui="{ rounded: 'rounded-xl' }"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-[#1d1d1f] mb-2">Isi Pesan</label>
              <UTextarea
                v-model="form.message"
                placeholder="Jelaskan kebutuhan Anda secara detail di sini..."
                :rows="5"
                size="lg"
                color="gray"
                variant="outline"
                required
                :ui="{ rounded: 'rounded-xl' }"
              />
            </div>

            <UButton
              type="submit"
              color="black"
              size="xl"
              block
              :loading="isSubmitting"
              class="mt-2 rounded-xl font-bold tracking-wide"
            >
              {{ isSubmitting ? 'Mengirim Pesan...' : 'Kirim Pesan Sekarang' }}
            </UButton>

          </form>
        </section>

      </div>
    </main>
  </div>
</template>

<style scoped>
div, section, main {
  font-family: var(--font-sans);
}
</style>
