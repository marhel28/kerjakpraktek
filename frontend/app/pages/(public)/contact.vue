<script setup lang="ts">
import { ref } from 'vue'

useSeoMeta({
  title: 'Kontak Bantuan & Operasional - PasarCCTV',
  description: 'Hubungi tim operasional dan support teknis PasarCCTV untuk kebutuhan instalasi maupun pembelian perangkat keamanan.',
})

const waSales = {
  name: 'WhatsApp Sales & Pembelian',
  value: '+62 811-XXXX-XXXX',
  link: 'https://wa.me/62811XXXXXXXXX',
  desc: 'Konsultasi produk, stok barang, pengiriman logistik, dan pertanyaan mengenai status pesanan Anda.',
  icon: 'i-tabler-brand-whatsapp'
}

const waSupport = {
  name: 'WhatsApp Teknisi & Instalasi',
  value: '+62 812-XXXX-XXXX',
  link: 'https://wa.me/62812XXXXXXXXX',
  desc: 'Jadwal kunjungan teknisi lapangan, kendala pemasangan, klaim garansi, dan request perbaikan.',
  icon: 'i-tabler-tools'
}

const otherContacts = [
  { name: 'Email Resmi', value: 'cs@pasarcctv.com', link: 'mailto:cs@pasarcctv.com', icon: 'i-tabler-mail' },
  { name: 'Telepon Kantor', value: '(022) 1234567', link: 'tel:0221234567', icon: 'i-tabler-phone' }
]

const socialMedias = [
  { name: 'Instagram', handle: '@pasarcctv', link: 'https://instagram.com/pasarcctv', icon: 'i-tabler-brand-instagram' },
  { name: 'TikTok', handle: '@pasarcctv.id', link: 'https://tiktok.com/@pasarcctv.id', icon: 'i-tabler-brand-tiktok' },
  { name: 'Facebook', handle: 'PasarCctv Official', link: 'https://facebook.com/pasarcctv', icon: 'i-tabler-brand-facebook' }
]
</script>

<template>
  <main class="bg-gray-50 min-h-screen pb-16 font-sans">
    <!-- Header Minimalis, Tokopedia Style Gradient -->
    <div class="bg-gradient-to-r from-[#03AC0E] to-[#028C0B] text-white pt-10 pb-20 px-4 relative overflow-hidden shadow-sm">
      <div class="max-w-[1000px] mx-auto relative z-10 text-center">
        <h1 class="text-2xl md:text-3xl font-medium mb-3 tracking-tight">Pusat Bantuan & Kontak Operasional</h1>
        <p class="text-white/90 text-sm md:text-base max-w-2xl mx-auto leading-relaxed">
          Pilih jalur komunikasi sesuai kebutuhan Anda. Tim kami siap merespons secara cepat pada jam operasional (Senin-Sabtu, 08:00 - 17:00).
        </p>
      </div>
    </div>

    <!-- Content Area -->
    <div class="max-w-[1000px] mx-auto px-4 -mt-12 relative z-20">
      
      <!-- Prioritas 1: WhatsApp Split (Actionable) -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-8">
        
        <!-- WA Sales -->
        <NuxtLink :to="waSales.link" target="_blank" v-motion-pop-visible-once class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 md:p-6 transition-all hover:border-[#03AC0E] hover:shadow-md group flex flex-col h-full">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-[#E6F7E9] flex items-center justify-center shrink-0 group-hover:bg-[#03AC0E] transition-colors">
              <UIcon :name="waSales.icon" class="w-6 h-6 text-[#03AC0E] group-hover:text-white transition-colors" />
            </div>
            <div>
              <h2 class="text-base font-medium text-gray-900 leading-tight mb-1">{{ waSales.name }}</h2>
              <span class="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full uppercase tracking-wider">Fast Response</span>
            </div>
          </div>
          <p class="text-[13px] text-gray-500 mb-5 flex-1">{{ waSales.desc }}</p>
          <div class="flex items-center justify-between mt-auto">
            <span class="text-[#03AC0E] font-medium text-lg tracking-tight">{{ waSales.value }}</span>
            <UIcon name="i-tabler-chevron-right" class="w-5 h-5 text-gray-300 group-hover:text-[#03AC0E] group-hover:translate-x-1 transition-all" />
          </div>
        </NuxtLink>

        <!-- WA Support -->
        <NuxtLink :to="waSupport.link" target="_blank" v-motion-pop-visible-once :delay="100" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 md:p-6 transition-all hover:border-[#03AC0E] hover:shadow-md group flex flex-col h-full">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-[#E6F7E9] flex items-center justify-center shrink-0 group-hover:bg-[#03AC0E] transition-colors">
              <UIcon :name="waSupport.icon" class="w-6 h-6 text-[#03AC0E] group-hover:text-white transition-colors" />
            </div>
            <div>
              <h2 class="text-base font-medium text-gray-900 leading-tight mb-1">{{ waSupport.name }}</h2>
              <span class="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full uppercase tracking-wider">Operasional & Teknisi</span>
            </div>
          </div>
          <p class="text-[13px] text-gray-500 mb-5 flex-1">{{ waSupport.desc }}</p>
          <div class="flex items-center justify-between mt-auto">
            <span class="text-[#03AC0E] font-medium text-lg tracking-tight">{{ waSupport.value }}</span>
            <UIcon name="i-tabler-chevron-right" class="w-5 h-5 text-gray-300 group-hover:text-[#03AC0E] group-hover:translate-x-1 transition-all" />
          </div>
        </NuxtLink>
        
      </div>

      <!-- Secondary Contacts & Socials Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Other Contacts -->
        <div class="lg:col-span-1 flex flex-col gap-4">
          <a v-for="contact in otherContacts" :key="contact.name" :href="contact.link" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex items-center gap-4 transition-all hover:border-[#03AC0E] group">
            <div class="w-10 h-10 rounded-lg bg-gray-50 flex items-center justify-center shrink-0">
              <UIcon :name="contact.icon" class="w-5 h-5 text-gray-500 group-hover:text-[#03AC0E] transition-colors" />
            </div>
            <div>
              <p class="text-[11px] font-medium text-gray-400 uppercase tracking-widest mb-0.5">{{ contact.name }}</p>
              <p class="text-[14px] font-medium text-gray-900">{{ contact.value }}</p>
            </div>
          </a>
        </div>

        <!-- Social Media -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-1 flex items-center gap-2">
            <UIcon name="i-tabler-broadcast" class="w-4 h-4 text-[#03AC0E]" />
            Ekosistem PasarCCTV
          </h3>
          <p class="text-[13px] text-gray-500 mb-6">Ikuti kami untuk melihat portofolio instalasi, edukasi keamanan, dan promo menarik mingguan.</p>
          
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <a v-for="social in socialMedias" :key="social.name" :href="social.link" target="_blank" class="flex flex-col items-center justify-center bg-gray-50 rounded-xl p-4 border border-gray-100 hover:border-gray-300 hover:bg-gray-100 transition-colors group">
              <UIcon :name="social.icon" class="w-7 h-7 text-gray-600 mb-2 group-hover:text-[#03AC0E] group-hover:-translate-y-0.5 transition-all" />
              <span class="text-sm font-medium text-gray-900">{{ social.name }}</span>
              <span class="text-[11px] text-gray-500">{{ social.handle }}</span>
            </a>
          </div>
        </div>

      </div>

    </div>
  </main>
</template>
