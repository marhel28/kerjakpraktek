<script setup lang="ts">
import { ref } from 'vue'

useSeoMeta({
  title: 'Informasi Pengiriman & Lacak Resi - PasarCCTV',
  description: 'Cek status pengiriman, jadwal operasional kurir, dan lacak resi pesanan PasarCCTV Anda dengan mudah.',
})

const noResi = ref('')

const lacakResi = () => {
  if (!noResi.value) return
  // Redirect ke cekresi.com dan mem-bypass query noresi
  const url = `https://cekresi.com/?noresi=${encodeURIComponent(noResi.value.trim())}`
  window.open(url, '_blank')
}
</script>

<template>
  <main class="bg-gray-50 min-h-screen pb-16 font-jakarta">
    <!-- Header Hero -->
    <div class="bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm text-white pt-16 pb-20 px-4 relative overflow-hidden">
      <!-- Aksen Cahaya Hijau Premium -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full blur-[100px] opacity-20 transform translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
      
      <div class="max-w-[1000px] mx-auto relative z-10 text-center">
        <h1 class="text-3xl md:text-4xl font-medium mb-4 tracking-tight text-white">Pengiriman & Lacak Resi</h1>
        <p class="text-gray-100 text-sm md:text-base max-w-2xl mx-auto leading-relaxed">
          Pahami jadwal pengiriman kami dan pantau perjalanan pesanan perangkat keamanan Anda.
        </p>
      </div>
    </div>

    <!-- Content Area -->
    <div class="max-w-[1000px] mx-auto px-4 -mt-10 relative z-20">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Kolom Kiri: Info Pengiriman -->
        <div class="lg:col-span-2 flex flex-col gap-6">
          
          <article class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8">
            <h2 class="text-[18px] font-medium text-gray-900 mb-5 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              Jadwal Operasional Pengiriman
            </h2>
            <div class="space-y-4 text-sm text-gray-600 leading-relaxed">
              <p>
                Pesanan yang telah terverifikasi sebelum batas waktu operasional (cut-off) akan diproses dan diserahkan ke pihak ekspedisi pada hari yang sama. Kami bekerja sama dengan mitra logistik terpercaya untuk memastikan keamanan paket perangkat Anda.
              </p>
              
              <div class="bg-gray-50 rounded-xl p-4 md:p-5 border border-gray-100 mt-4">
                <ul class="space-y-3.5">
                  <li class="flex items-start justify-between border-b border-gray-200 pb-2.5">
                    <span class="font-medium text-gray-700">Senin - Jumat</span>
                    <span class="text-gray-900 font-medium">Cut-off 15:00 WIB</span>
                  </li>
                  <li class="flex items-start justify-between border-b border-gray-200 pb-2.5">
                    <span class="font-medium text-gray-700">Sabtu</span>
                    <span class="text-gray-900 font-medium">Cut-off 12:00 WIB</span>
                  </li>
                  <li class="flex items-start justify-between">
                    <span class="font-medium text-gray-700">Minggu & Libur Nasional</span>
                    <span class="text-[#B45309] font-medium">Tidak ada pengiriman</span>
                  </li>
                </ul>
              </div>
            </div>
          </article>

          <article class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8">
            <h2 class="text-[18px] font-medium text-gray-900 mb-6 flex items-center gap-2">
              <span class="w-1 h-5 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm rounded-full inline-block"></span>
              Alur Penginputan Resi
            </h2>
            
            <div class="space-y-0">
              <!-- Step 1 -->
              <div class="flex gap-4 relative">
                <div class="flex flex-col items-center relative z-10">
                  <div class="w-9 h-9 rounded-full bg-[#E6F7E9] flex items-center justify-center text-[#03AC0E] font-medium text-sm border-2 border-white shadow-sm">1</div>
                  <div class="w-0.5 h-full bg-gray-100 my-1 absolute top-9 bottom-[-10px]"></div>
                </div>
                <div class="pb-8 pt-1.5">
                  <h3 class="font-medium text-gray-900 mb-1.5 text-sm">Pesanan Diproses</h3>
                  <p class="text-sm text-gray-500 leading-relaxed">Tim gudang kami menyiapkan pesanan, melakukan <em>Quality Control</em> fisik, dan mengemas paket dengan standar keamanan (bubble wrap ganda).</p>
                </div>
              </div>

              <!-- Step 2 -->
              <div class="flex gap-4 relative">
                <div class="flex flex-col items-center relative z-10">
                  <div class="w-9 h-9 rounded-full bg-[#E6F7E9] flex items-center justify-center text-[#03AC0E] font-medium text-sm border-2 border-white shadow-sm">2</div>
                  <div class="w-0.5 h-full bg-gray-100 my-1 absolute top-9 bottom-[-10px]"></div>
                </div>
                <div class="pb-8 pt-1.5">
                  <h3 class="font-medium text-gray-900 mb-1.5 text-sm">Paket Diserahkan ke Ekspedisi</h3>
                  <p class="text-sm text-gray-500 leading-relaxed">Paket diserahkan secara kolektif ke pihak kurir/ekspedisi (JNE, Sicepat, J&T, dsb) pada sore hari sesuai jadwal operasional kami.</p>
                </div>
              </div>

              <!-- Step 3 -->
              <div class="flex gap-4 relative">
                <div class="flex flex-col items-center relative z-10">
                  <div class="w-9 h-9 rounded-full bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm flex items-center justify-center text-white font-medium text-sm shadow-sm ring-4 ring-[#E6F7E9]">3</div>
                </div>
                <div class="pb-2 pt-1.5">
                  <h3 class="font-medium text-gray-900 mb-1.5 text-sm">Resi Diupdate (Malam Hari)</h3>
                  <p class="text-sm text-gray-500 leading-relaxed">Pihak ekspedisi mengeluarkan nomor resi resmi. Kami akan menginput nomor resi tersebut ke dalam sistem PasarCCTV pada malam hari dan status pesanan Anda akan berubah menjadi "Dikirim".</p>
                </div>
              </div>
            </div>
            
          </article>

        </div>

        <!-- Kolom Kanan: Widget Lacak Resi -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sticky top-24">
            <div class="w-12 h-12 bg-[#E6F7E9] rounded-xl flex items-center justify-center mb-5">
              <UIcon name="i-tabler-truck" class="w-6 h-6 text-[#03AC0E]" />
            </div>
            
            <h3 class="font-medium text-gray-900 text-[18px] mb-2 tracking-tight">Lacak Paket Anda</h3>
            <p class="text-[13px] text-gray-500 mb-6 leading-relaxed">
              Jika status pesanan Anda sudah <strong class="font-medium">Dikirim</strong>, masukkan nomor resi yang tertera pada pesanan untuk memantau posisi paket menggunakan CekResi.com.
            </p>

            <form @submit.prevent="lacakResi" class="space-y-4">
              <div>
                <label for="resi" class="sr-only">Nomor Resi</label>
                <input 
                  id="resi"
                  v-model="noResi"
                  type="text" 
                  placeholder="Contoh: JP321948811" 
                  class="w-full border border-gray-200 rounded-xl px-4 py-3.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#03AC0E] focus:border-transparent transition-all"
                  required
                />
              </div>
              <button 
                type="submit"
                class="w-full bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm text-[#03AC0E] font-medium py-3.5 rounded-xl hover:bg-gray-900 transition-colors flex items-center justify-center gap-2"
              >
                Cek Posisi Paket
                <UIcon name="i-tabler-external-link" class="w-4 h-4" />
              </button>
            </form>

            <div class="mt-6 pt-5 border-t border-gray-100">
              <div class="flex items-start gap-3 bg-[#FFF7E6] p-3.5 rounded-xl border border-[#f5e6c4]">
                <UIcon name="i-tabler-info-circle" class="w-5 h-5 text-[#B45309] shrink-0 mt-0.5" />
                <p class="text-xs text-[#B45309] leading-relaxed">
                  Status pengiriman ekspedisi mungkin membutuhkan waktu <strong class="font-medium">1x24 jam</strong> untuk terupdate di sistem setelah nomor resi diinput.
                </p>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  </main>
</template>

<style scoped>
.font-jakarta {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
</style>