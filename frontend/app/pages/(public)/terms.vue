<script setup lang="ts">
import { ref } from 'vue'

useSeoMeta({
  title: 'Syarat dan Ketentuan - PasarCCTV',
  description: 'Syarat dan ketentuan penggunaan layanan, transaksi, instalasi, dan garansi di PasarCCTV.',
})

const activeSection = ref('pendahuluan')

const sections = [
  { id: 'pendahuluan', title: '1. Pendahuluan' },
  { id: 'definisi', title: '2. Definisi' },
  { id: 'transaksi', title: '3. Layanan & Transaksi' },
  { id: 'instalasi', title: '4. Kebijakan Instalasi' },
  { id: 'garansi', title: '5. Garansi & Retur' },
  { id: 'tanggung-jawab', title: '6. Batasan Tanggung Jawab' },
]

const scrollTo = (id: string) => {
  activeSection.value = id
  const el = document.getElementById(id)
  if (el) {
    const y = el.getBoundingClientRect().top + window.scrollY - 100
    window.scrollTo({ top: y, behavior: 'smooth' })
  }
}
</script>

<template>
  <main class="bg-gray-50 min-h-screen pb-16 font-jakarta">
    <!-- Header Hero -->
    <div class="bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm text-white pt-16 pb-20 px-4 relative overflow-hidden">
      <!-- Aksen Cahaya Hijau -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full blur-[100px] opacity-20 transform translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
      
      <div class="max-w-[1000px] mx-auto relative z-10 text-center">
        <h1 class="text-3xl md:text-4xl font-medium mb-4 tracking-tight text-white">Syarat & Ketentuan</h1>
        <p class="text-gray-100 text-sm md:text-base max-w-2xl mx-auto leading-relaxed">
          Pembaruan Terakhir: 18 Mei 2026. Harap baca dengan saksama sebelum menggunakan layanan PasarCCTV.
        </p>
      </div>
    </div>

    <!-- Content Area -->
    <div class="max-w-[1000px] mx-auto px-4 -mt-10 relative z-20">
      <div class="flex flex-col md:flex-row gap-8">
        
        <!-- Sidebar Navigation (Desktop) -->
        <aside class="w-full md:w-64 shrink-0 hidden md:block">
          <div class="sticky top-24 bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 px-2">Daftar Isi</h3>
            <nav class="flex flex-col gap-1">
              <button
                v-for="sec in sections"
                :key="sec.id"
                @click="scrollTo(sec.id)"
                class="text-left px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all"
                :class="activeSection === sec.id ? 'bg-[#E6F7E9] text-[#03AC0E] font-medium' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
              >
                {{ sec.title }}
              </button>
            </nav>
            
            <div class="mt-6 pt-6 border-t border-gray-100 px-2">
              <h4 class="text-xs font-medium text-gray-900 mb-1.5">Butuh Bantuan?</h4>
              <p class="text-[11px] text-gray-500 mb-4 leading-relaxed">Tim support kami siap membantu operasional Anda kapan saja.</p>
              <NuxtLink to="/contact" class="flex items-center justify-center w-full bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm text-white py-2.5 rounded-xl text-[13px] font-medium hover:bg-[#028C0B] transition-colors shadow-sm">
                <UIcon name="i-tabler-message-circle" class="w-4 h-4 mr-2" />
                Hubungi Kami
              </NuxtLink>
            </div>
          </div>
        </aside>

        <!-- Main Document -->
        <article class="flex-1 bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-10 text-gray-700 text-sm leading-relaxed">
          
          <section id="pendahuluan" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              1. Pendahuluan
            </h2>
            <p class="mb-3">Selamat datang di PasarCCTV. Syarat & Ketentuan ini mengatur akses dan penggunaan Anda atas situs web, aplikasi seluler, dan seluruh layanan yang disediakan oleh PasarCCTV.</p>
            <p>Dengan mendaftar, mengakses, atau menggunakan layanan kami, Anda menyatakan bahwa Anda telah membaca, memahami, dan menyetujui untuk terikat oleh seluruh isi Syarat & Ketentuan ini. Ketentuan ini dibuat secara lugas untuk memastikan keamanan transaksi bersama. Jika Anda tidak menyetujui, harap untuk tidak menggunakan layanan kami.</p>
          </section>

          <section id="definisi" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              2. Definisi
            </h2>
            <ul class="space-y-3 list-none pl-0">
              <li class="flex items-start gap-2.5 bg-gray-50 p-3 rounded-xl border border-gray-100">
                <UIcon name="i-tabler-check" class="w-5 h-5 text-[#03AC0E] shrink-0 mt-0.5" />
                <span class="text-sm"><strong class="font-medium">PasarCCTV:</strong> PT Pasar Keamanan Indonesia selaku distributor resmi dan pengelola platform.</span>
              </li>
              <li class="flex items-start gap-2.5 bg-gray-50 p-3 rounded-xl border border-gray-100">
                <UIcon name="i-tabler-check" class="w-5 h-5 text-[#03AC0E] shrink-0 mt-0.5" />
                <span class="text-sm"><strong class="font-medium">Pengguna:</strong> Setiap pihak (pembeli, teknisi, vendor, owner bisnis) yang mengakses dan menggunakan layanan PasarCCTV.</span>
              </li>
              <li class="flex items-start gap-2.5 bg-gray-50 p-3 rounded-xl border border-gray-100">
                <UIcon name="i-tabler-check" class="w-5 h-5 text-[#03AC0E] shrink-0 mt-0.5" />
                <span class="text-sm"><strong class="font-medium">Layanan Instalasi:</strong> Jasa pemasangan sistem keamanan komprehensif yang dilakukan oleh teknisi mitra resmi bersertifikat kami.</span>
              </li>
            </ul>
          </section>

          <section id="transaksi" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              3. Layanan & Transaksi
            </h2>
            <p class="mb-4">PasarCCTV menyediakan platform integrasi satu atap untuk pengadaan perangkat keamanan (CCTV, Access Control, dll) beserta jasa instalasinya. Kami mengutamakan integritas dalam setiap transaksi operasional.</p>
            <ul class="list-disc pl-5 space-y-2.5 text-gray-600">
              <li>Harga yang tertera pada platform menggunakan mata uang Rupiah (IDR) dan dapat berubah sewaktu-waktu sesuai ketentuan distributor utama.</li>
              <li>Sistem akan memverifikasi pembayaran secara otomatis (Midtrans). Dilarang keras melakukan transfer ke rekening pribadi atas nama individu manapun.</li>
              <li>Barang yang dikirim telah melalui proses <em>Quality Control</em> (QC) operasional yang ketat.</li>
              <li>Pesanan yang sudah diproses oleh sistem tidak dapat dibatalkan sepihak tanpa persetujuan dari manajer operasional PasarCCTV.</li>
            </ul>
          </section>

          <section id="instalasi" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              4. Kebijakan Instalasi & Pemasangan
            </h2>
            <div class="bg-[#FFF7E6] border border-[#f5e6c4] rounded-xl p-4 mb-5 shadow-sm">
              <div class="flex items-start gap-3">
                <UIcon name="i-tabler-alert-triangle" class="w-5 h-5 text-[#B45309] shrink-0 mt-0.5" />
                <div class="text-[#B45309] text-[13px] leading-relaxed">
                  <strong class="font-medium">Penting untuk Operational Clarity:</strong> Teknisi kami hanya mengerjakan lingkup kerja (SOW) yang telah disepakati dan dibayar dalam sistem. Penambahan titik kamera, penarikan kabel ekstra, atau modifikasi lapangan yang tidak ada dalam estimasi awal akan dikenakan biaya <em>add-on</em>.
                </div>
              </div>
            </div>
            <ul class="list-disc pl-5 space-y-2.5 text-gray-600">
              <li>Teknisi akan hadir sesuai jadwal operasional yang dipilih pada saat checkout.</li>
              <li>Pembeli wajib memastikan keamanan area dan ketersediaan akses saat teknisi tiba di lokasi.</li>
              <li>Pembatalan sepihak pada hari-H oleh pembeli akan menyebabkan <em>Booking Fee</em> hangus, demi menghargai waktu operasional teknisi lapangan.</li>
              <li>PasarCCTV menjamin garansi kerapian instalasi pengerjaan selama 30 hari.</li>
            </ul>
          </section>

          <section id="garansi" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              5. Garansi & Retur
            </h2>
            <p class="mb-4">Kepercayaan dan keandalan produk adalah prioritas. Kami hanya menjual perangkat bergaransi resmi.</p>
            <ul class="list-disc pl-5 space-y-2.5 text-gray-600">
              <li>Masa garansi perangkat elektronik berkisar antara 1 hingga 3 tahun (bergantung kebijakan pabrikan/distributor utama).</li>
              <li>Klaim penukaran barang cacat pabrik (<em>Defect on Arrival</em>) wajib dilakukan maksimal 7x24 jam sejak barang tiba, disertai dengan video <em>unboxing</em> tanpa jeda.</li>
              <li><strong class="font-medium">Garansi Void (Hangus)</strong> jika kerusakan disebabkan oleh: lonjakan arus listrik (petir/konslet), bencana alam, kesalahan penggunaan ekstrem, segel distributor rusak, atau masuknya air ke perangkat <em>indoor</em>.</li>
            </ul>
          </section>

          <section id="tanggung-jawab" class="scroll-mt-28">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              6. Batasan Tanggung Jawab
            </h2>
            <p class="mb-4">PasarCCTV dibebaskan dari tuntutan kerugian material atau immaterial yang diakibatkan oleh hal-hal di luar kendali kami:</p>
            <ul class="list-disc pl-5 space-y-2.5 text-gray-600">
              <li>Kegagalan sistem akibat <em>force majeure</em> (bencana alam massal, kerusuhan, pemadaman listrik berkepanjangan).</li>
              <li>Penyalahgunaan data privasi/rekaman video CCTV. Pengelolaan akses rekaman menjadi tanggung jawab penuh pihak pembeli selaku <em>owner</em> sistem.</li>
              <li>Kerusakan yang diakibatkan oleh modifikasi atau pemeliharaan sistem oleh teknisi lepas (pihak ketiga) di luar mitra resmi PasarCCTV.</li>
            </ul>
          </section>

        </article>
      </div>
    </div>
  </main>
</template>

<style scoped>
.font-jakarta {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
</style>