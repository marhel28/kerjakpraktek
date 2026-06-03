<script setup lang="ts">
import { ref } from 'vue'

useSeoMeta({
  title: 'Kebijakan Privasi - PasarCCTV',
  description: 'Kebijakan privasi PasarCCTV mengenai pengumpulan, penggunaan, dan perlindungan data pribadi serta keamanan sistem CCTV pelanggan.',
})

const activeSection = ref('pendahuluan')

const sections = [
  { id: 'pendahuluan', title: '1. Pendahuluan' },
  { id: 'pengumpulan-data', title: '2. Pengumpulan Data' },
  { id: 'penggunaan-data', title: '3. Penggunaan Data' },
  { id: 'keamanan-data', title: '4. Keamanan & Rekaman' },
  { id: 'pihak-ketiga', title: '5. Pihak Ketiga' },
  { id: 'hak-pengguna', title: '6. Hak Pengguna' },
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
        <h1 class="text-3xl md:text-4xl font-medium mb-4 tracking-tight text-white">Kebijakan Privasi</h1>
        <p class="text-gray-100 text-sm md:text-base max-w-2xl mx-auto leading-relaxed">
          Pembaruan Terakhir: 18 Mei 2026. Kami menghargai privasi data Anda selayaknya kami mengamankan aset fisik Anda.
        </p>
      </div>
    </div>

    <!-- Content Area -->
    <div class="max-w-[1000px] mx-auto px-4 -mt-10 relative z-20">
      <div class="flex flex-col md:flex-row gap-8">
        
        <!-- Sidebar Navigation (Desktop) -->
        <aside class="w-full md:w-64 shrink-0 hidden md:block">
          <div class="sticky top-24 bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
            <h3 class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-4 px-2">Daftar Isi</h3>
            <nav class="flex flex-col gap-1">
              <button
                v-for="sec in sections"
                :key="sec.id"
                @click="scrollTo(sec.id)"
                class="text-left px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all"
                :class="activeSection === sec.id ? 'bg-[#E6F7E9] text-[#03AC0E]' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
              >
                {{ sec.title }}
              </button>
            </nav>
            
            <div class="mt-6 pt-6 border-t border-gray-100 px-2">
              <h4 class="text-xs font-medium text-gray-900 mb-1.5">Butuh Bantuan?</h4>
              <p class="text-[11px] text-gray-500 mb-4 leading-relaxed">Tim support kami siap menjawab pertanyaan privasi Anda kapan saja.</p>
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
            <p class="mb-3">PasarCCTV ("Kami") berkomitmen tinggi untuk melindungi keamanan dan privasi data pribadi Pengguna ("Anda"). Sebagai platform penyedia layanan dan produk keamanan (CCTV & Access Control), kami menyadari betapa pentingnya kerahasiaan informasi bagi kelancaran bisnis maupun privasi hunian Anda.</p>
            <p>Kebijakan ini menjelaskan dengan transparan bagaimana kami mengumpulkan, menggunakan, menyimpan, dan melindungi informasi pribadi yang Anda berikan melalui situs web, aplikasi, maupun saat berinteraksi langsung dengan tim teknisi operasional kami.</p>
          </section>

          <section id="pengumpulan-data" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              2. Pengumpulan Data Pribadi
            </h2>
            <p class="mb-3">Kami mengumpulkan data yang relevan secara operasional semata-mata untuk menunjang kelancaran dan kualitas layanan, di antaranya:</p>
            <ul class="space-y-3 list-none pl-0">
              <li class="flex items-start gap-2.5 bg-gray-50 p-3 rounded-xl border border-gray-100">
                <UIcon name="i-tabler-check" class="w-5 h-5 text-[#03AC0E] shrink-0 mt-0.5" />
                <span class="text-sm"><strong class="font-medium">Data Akun & Profil:</strong> Nama lengkap, alamat email, nomor telepon WhatsApp, dan kata sandi yang telah dienkripsi secara aman.</span>
              </li>
              <li class="flex items-start gap-2.5 bg-gray-50 p-3 rounded-xl border border-gray-100">
                <UIcon name="i-tabler-check" class="w-5 h-5 text-[#03AC0E] shrink-0 mt-0.5" />
                <span class="text-sm"><strong class="font-medium">Data Transaksi & Lokasi:</strong> Alamat pengiriman logistik, alamat pengerjaan instalasi proyek, riwayat pemesanan, dan detail pembayaran (diproses ketat oleh payment gateway berlisensi).</span>
              </li>
              <li class="flex items-start gap-2.5 bg-gray-50 p-3 rounded-xl border border-gray-100">
                <UIcon name="i-tabler-check" class="w-5 h-5 text-[#03AC0E] shrink-0 mt-0.5" />
                <span class="text-sm"><strong class="font-medium">Data Teknis Pemasangan:</strong> Konfigurasi dasar sistem keamanan (Topologi, IP Network Camera) yang hanya diperlukan oleh teknisi untuk proses aktivasi garansi perangkat.</span>
              </li>
            </ul>
          </section>

          <section id="penggunaan-data" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              3. Penggunaan Data
            </h2>
            <p class="mb-4">Informasi yang kami kumpulkan akan dimanfaatkan secara ketat untuk fungsi operasional esensial berikut:</p>
            <ul class="list-disc pl-5 space-y-2.5 text-gray-600">
              <li>Memverifikasi transaksi pemesanan, memfasilitasi pengiriman barang, dan mengatur jadwal kehadiran teknisi lapangan ke properti Anda.</li>
              <li>Mendaftarkan perangkat keras (serial number DVR/NVR) ke dalam database garansi resmi jaringan distributor.</li>
              <li>Menghubungi Anda secara proaktif terkait pembaruan status pemesanan, jadwal *maintenance* rutin, atau bantuan respon teknis lanjutan.</li>
              <li>Peningkatan kualitas interaksi antarmuka (UX) platform kami menggunakan analitik data massal yang bersifat rahasia (*anonymized*).</li>
            </ul>
          </section>

          <section id="keamanan-data" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              4. Keamanan Data & Rekaman CCTV
            </h2>
            <div class="bg-[#FFF7E6] border border-[#f5e6c4] rounded-xl p-4 mb-5 shadow-sm">
              <div class="flex items-start gap-3">
                <UIcon name="i-tabler-shield-lock" class="w-5 h-5 text-[#B45309] shrink-0 mt-0.5" />
                <div class="text-[#B45309] text-[13px] leading-relaxed">
                  <strong class="font-medium">Kerahasiaan Mutlak Footage Rekaman:</strong> Teknisi lapangan PasarCCTV semata-mata mengonfigurasi jalur jaringan dan memastikan sudut *live view* berfungsi dengan tepat. Kami <strong class="font-medium">tidak akan pernah</strong> memiliki akses jarak jauh (remote), menyimpan salinan rekaman, mendistribusikan cuplikan aktivitas (*footage*), maupun memegang *password* admin akhir DVR/NVR Anda. Privasi rekaman adalah aset tak tersentuh yang menjadi kewenangan mutlak pelanggan.
                </div>
              </div>
            </div>
            <p class="mb-4">Secara infrastruktur digital, situs dan ekosistem database kami dilapisi protokol pengamanan terkini (Enkripsi tingkat tinggi dan SSL tersertifikasi) guna menangkis upaya akses curang atau pencurian informasi.</p>
          </section>

          <section id="pihak-ketiga" class="scroll-mt-28 mb-10">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              5. Pembagian Data dengan Pihak Ketiga
            </h2>
            <p class="mb-4">PasarCCTV menentang keras praktik jual beli basis data (*data brokerage*). Bagian kecil dari informasi Anda akan kami rujuk <strong>hanya untuk vendor yang krusial</strong>, seperti:</p>
            <ul class="list-disc pl-5 space-y-2.5 text-gray-600">
              <li><strong class="font-medium">Logistik / Ekspedisi Cepat:</strong> JNE, J&T, Sicepat (Membatasi hanya nama penerima, kontak aktif, dan titik lokasi koordinat logistik).</li>
              <li><strong class="font-medium">Payment Gateway Resmi:</strong> Midtrans (Mengelola *tokenisasi* angka transaksi—kami di platform ini tidak mencatat rincian nomor kartu kredit Anda).</li>
              <li><strong class="font-medium">Penegak Hukum Negara:</strong> Jika ada perintah undang-undang yang mewajibkan kami atau ketetapan peradilan resmi di wilayah yurisdiksi Indonesia demi penyelidikan tindak kriminal.</li>
            </ul>
          </section>

          <section id="hak-pengguna" class="scroll-mt-28">
            <h2 class="text-[18px] font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              6. Hak Pengguna
            </h2>
            <p class="mb-4">Anda selaku pengguna sah memiliki otonomi absolut terhadap data profil Anda. Anda berhak setiap saat untuk:</p>
            <ul class="list-disc pl-5 space-y-2.5 text-gray-600">
              <li>Minta dilakukannya pembaruan, perubahan, atau koreksi identitas akun.</li>
              <li>Mengajukan permohonan pemusnahan (penghapusan) profil Anda dari *database* aktif kami.</li>
              <li>Meminta salinan ringkasan informasi yang berkaitan dengan seluruh jejak histori transaksi di platform ini.</li>
            </ul>
            <p class="mt-4">Bila terdapat kekeliruan pemahaman pada kebijakan ini atau bila Anda mengkhawatirkan celah pada privasi instalasi sistem keamanan Anda, silakan menghubungi *Product Strategist* atau Manajer Support Operasional kami di halaman Hubungi Kami.</p>
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