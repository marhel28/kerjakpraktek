<script setup lang="ts">
import { ref, computed } from 'vue'

// SEO & Meta Tags
useSeoMeta({
  title: 'Portofolio Pemasangan CCTV Profesional | Padjajaran CCTV',
  description: 'Lihat hasil kerja Padjajaran CCTV. Dari rumah mewah hingga gudang logistik, kami memberikan instalasi sistem keamanan terbaik, rapi, dan bergaransi.',
  ogTitle: 'Portofolio Pemasangan CCTV | Padjajaran CCTV',
  ogImage: '/images/portfolio-banner.jpg',
  robots: 'index, follow'
})

// Simulasi Data Fetching dari API Backend (SSR Friendly)
const { data, status } = await useAsyncData('portfolio-data', async () => {
  // Simulasi delay jaringan 800ms untuk melihat efek skeleton
  await new Promise(resolve => setTimeout(resolve, 800))
  
  return {
    featured: {
      clientType: 'Pabrik & Manufaktur',
      title: 'Sistem Keamanan Terintegrasi Pabrik Tekstil 2 Ha',
      problem: 'Area pabrik sangat luas dengan banyak titik buta (blind spot), sering terjadi kehilangan aset, dan sistem lama sering offline karena kabel putus digigit tikus.',
      solution: 'Instalasi 64 titik Kamera IP 5MP dengan sistem kabel Fiber Optic tertanam (Conduit PVC), NVR redundant, dan UPS backup 4 jam.',
      result: 'Zero blind spot di area produksi, pemantauan realtime dari HQ di Jakarta, dan tidak ada lagi downtime sistem dalam 6 bulan terakhir.',
      beforeImage: 'https://images.unsplash.com/photo-1565626423378-eb2bb4d33454?auto=format&fit=crop&q=80&w=800',
      afterImage: 'https://images.unsplash.com/photo-1586528116311-ad8ed7c663be?auto=format&fit=crop&q=80&w=800'
    },
    projects: [
      { id: 1, title: 'Instalasi Rumah Mewah Pondok Indah', category: 'Residensial', cameras: 16, location: 'Jakarta Selatan', image: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&q=80&w=600', packageSlug: 'paket-premium-16-ch' },
      { id: 2, title: 'Monitoring Gudang Logistik', category: 'Komersial', cameras: 32, location: 'Cikarang', image: 'https://images.unsplash.com/photo-1586528116311-ad8ed7c663be?auto=format&fit=crop&q=80&w=600', packageSlug: 'paket-gudang-32-ch' },
      { id: 3, title: 'Keamanan Minimarket 24 Jam', category: 'Retail', cameras: 8, location: 'Bandung', image: 'https://images.unsplash.com/photo-1601597111158-2fceff292cdc?auto=format&fit=crop&q=80&w=600', packageSlug: 'paket-toko-8-ch' },
      { id: 4, title: 'Perkantoran Sudirman', category: 'Korporat', cameras: 24, location: 'Jakarta Pusat', image: 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=600', packageSlug: 'custom-quote' },
      { id: 5, title: 'Klinik Kesehatan', category: 'Fasilitas Umum', cameras: 12, location: 'Bogor', image: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80&w=600', packageSlug: 'paket-standard-12-ch' },
      { id: 6, title: 'Cafe & Resto', category: 'F&B', cameras: 6, location: 'Depok', image: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&q=80&w=600', packageSlug: 'paket-usaha-6-ch' },
    ],
    testimonials: [
      { id: 1, name: 'Bpk. Hendra', role: 'Pemilik Gudang', rating: 5, text: 'Kerjanya sangat rapi, kabel tidak ada yang berantakan karena dimasukkan ke pipa semua. Teknisi juga ramah menjelaskan cara pakai aplikasinya.' },
      { id: 2, name: 'Ibu Sarah', role: 'Warga Cluster', rating: 5, text: 'Awalnya ragu beli online, tapi ternyata layanannya sekelas perusahaan besar. CCTV jernih, malam hari tetap kelihatan berwarna.' },
      { id: 3, name: 'Toko Makmur', role: 'Retailer', rating: 5, text: 'Instalasi cepat tidak mengganggu pelanggan toko. Harga jujur sesuai paket di website tanpa biaya siluman.' },
    ]
  }
})

const isPending = computed(() => status.value === 'pending')
</script>

<template>
  <main class="font-sans text-gray-900 bg-gray-50 min-h-screen pb-20">
    
    <section class="relative bg-black text-white pt-24 pb-32 px-4 overflow-hidden">
      <div class="absolute inset-0 opacity-30 mix-blend-overlay" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E');"></div>
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-red-600/20 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/3"></div>
      
      <div class="max-w-5xl mx-auto relative z-10 text-center">
        <span class="inline-block py-1 px-3 border border-gray-700 bg-gray-800/50 rounded-full text-xs font-bold tracking-widest text-gray-300 uppercase mb-6">
          Portofolio Instalasi
        </span>
        <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tight leading-tight mb-6">
          Standar <span class="text-red-600">Enterprise</span>.<br/> Harga Terjangkau.
        </h1>
        <p class="text-gray-400 text-lg md:text-xl font-medium max-w-2xl mx-auto mb-10">
          Lebih dari 1,200 titik kamera telah kami pasang. Kami tidak hanya menjual produk, kami mendesain rasa aman untuk Anda.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink to="/jasa-instalasi" class="bg-white text-black px-8 py-4 text-sm font-black uppercase tracking-widest hover:bg-gray-200 transition-colors flex items-center justify-center gap-2">
            Konsultasi Gratis <Icon name="lucide:arrow-right" class="w-4 h-4" />
          </NuxtLink>
          <NuxtLink to="#featured" class="border border-gray-700 hover:bg-gray-800 text-white px-8 py-4 text-sm font-bold uppercase tracking-widest transition-colors flex items-center justify-center gap-2">
            Lihat Hasil Kerja <Icon name="lucide:chevron-down" class="w-4 h-4" />
          </NuxtLink>
        </div>
      </div>
    </section>

    <section id="featured" class="max-w-7xl mx-auto px-4 -mt-16 relative z-20">
      <div v-if="isPending" class="h-[600px] w-full bg-gray-200 animate-pulse rounded-2xl"></div>
      <PortfolioCaseStudy v-else-if="data?.featured" :data="data.featured" />
    </section>

    <section class="max-w-7xl mx-auto px-4 py-24">
      <div class="text-center mb-16">
        <h2 class="text-3xl font-black uppercase tracking-tight mb-4">Galeri Project</h2>
        <p class="text-gray-500 font-medium max-w-xl mx-auto">
          Dari perumahan hingga fasilitas komersial, teknisi kami dilatih untuk bekerja cepat, bersih, dan sesuai standar keamanan kelistrikan.
        </p>
      </div>

      <div v-if="isPending" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="h-[350px] bg-gray-200 animate-pulse rounded-xl"></div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PortfolioProjectCard 
          v-for="project in data?.projects" 
          :key="project.id" 
          :project="project" 
        />
      </div>
    </section>

    <section class="bg-white border-y border-gray-200 py-24">
      <div class="max-w-7xl mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="text-3xl font-black uppercase tracking-tight mb-2">Apa Kata Klien?</h2>
          <p class="text-gray-500 font-medium">Reputasi kami dibangun di atas kepuasan mereka.</p>
        </div>

        <div v-if="isPending" class="flex gap-6 overflow-hidden">
           <div v-for="i in 3" :key="i" class="h-48 min-w-[300px] w-full bg-gray-100 animate-pulse rounded-xl"></div>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <PortfolioTestimonialCard 
            v-for="testi in data?.testimonials" 
            :key="testi.id" 
            :testi="testi" 
          />
        </div>
      </div>
    </section>

    <section class="max-w-5xl mx-auto px-4 py-24 text-center">
      <h2 class="text-4xl font-black uppercase tracking-tight mb-6">Butuh Sistem Keamanan Serupa?</h2>
      <p class="text-gray-500 font-medium mb-10 max-w-2xl mx-auto">
        Jadwalkan survey lokasi bersama tim ahli kami. Kami bantu hitung kebutuhan kabel, posisi kamera ideal, dan estimasi biaya tanpa komitmen.
      </p>
      <div class="flex flex-col sm:flex-row justify-center gap-4">
        <button class="bg-black text-white px-8 py-4 text-xs font-black uppercase tracking-widest hover:bg-gray-800 transition-colors">
          Jadwalkan Survey Lokasi
        </button>
        <NuxtLink to="/kategori/paket-cctv" class="bg-white border-2 border-gray-200 text-black px-8 py-4 text-xs font-black uppercase tracking-widest hover:border-black transition-colors">
          Lihat Daftar Paket Pemasangan
        </NuxtLink>
      </div>
    </section>

  </main>
</template>