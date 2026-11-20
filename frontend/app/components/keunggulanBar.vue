<template>
  <!--
    Section border atas-bawah tipis untuk memberikan batas yang jelas
    jika diletakkan di bawah Header atau Banner utama.
  -->
  <section class="w-full bg-white border-b border-gray-100 py-6 lg:py-8 font-sans">
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">

        <div
          v-for="(feature, index) in features"
          :key="index"
          class="flex items-center gap-4 group cursor-default"
        >
          <!-- ICON CONTAINER -->
          <!-- Menggunakan warna hijau persis seperti referensi dan efek scale saat di-hover -->
          <div class="flex-shrink-0 text-[#03AC0E] transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3">
            <Icon :name="feature.icon" class="w-10 h-10 lg:w-[42px] lg:h-[42px]" />
          </div>

          <!-- TEXT CONTAINER -->
          <div class="flex flex-col justify-center">
            <h3 class="text-[14px] lg:text-[15px] font-bold text-gray-900 leading-tight mb-0.5">
              {{ feature.title }}
            </h3>
            <p class="text-[12px] lg:text-[13px] text-gray-500 font-medium leading-tight">
              {{ feature.subtitle }}
            </p>
          </div>

        </div>

      </div>

    </div>
  </section>
</template>

<script setup>
// Data fitur keunggulan resmi PasarCCTV Bandung & Jawa Barat
const features = [
  {
    icon: 'lucide:truck',
    title: 'Pengiriman Cepat',
    subtitle: 'Bisa Instan & Sameday Bandung'
  },
  {
    icon: 'lucide:shield-check',
    title: 'Garansi Resmi 100%',
    subtitle: 'Distributor Resmi & Unit Original'
  },
  {
    icon: 'lucide:wrench',
    title: 'Teknisi Berpengalaman',
    subtitle: 'Siap Pasang & Setting di Lokasi'
  },
  {
    icon: 'lucide:headset',
    title: 'Konsultasi Teknis',
    subtitle: 'Bantuan Panduan & Purna Jual'
  }
]
</script>
