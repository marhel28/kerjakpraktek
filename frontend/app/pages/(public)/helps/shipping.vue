<template>
  <main class="bg-[#F7F8F9] min-h-screen pb-16 font-['Open_Sans',sans-serif] text-gray-900">
    <!-- ════════════════════════════════════════════════════════════
         HERO RESI TRACKER: Amazon-Style Search Header
         ════════════════════════════════════════════════════════════ -->
    <header class="bg-white border-b border-gray-200 pt-8 pb-10 px-4 sm:px-6 lg:px-8">
      <div class="max-w-4xl mx-auto">
        <!-- Breadcrumb -->
        <nav aria-label="Breadcrumb" class="mb-4 flex items-center gap-2 text-xs font-medium text-gray-500 font-['Plus_Jakarta_Sans',sans-serif]">
          <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
          <span class="text-gray-300">/</span>
          <NuxtLink to="/help" class="hover:text-[#03AC0E] transition-colors">Pusat Bantuan</NuxtLink>
          <span class="text-gray-300">/</span>
          <span class="text-gray-800">Lacak Pengiriman</span>
        </nav>

        <div class="text-center max-w-xl mx-auto mb-6">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#E6F7E9] text-[#03AC0E] border border-[#C8E6CC] mb-3 font-['Plus_Jakarta_Sans',sans-serif]">
            <UIcon name="i-heroicons-truck" class="w-4 h-4 shrink-0" />
            <span>Pelacakan Ekspedisi Resmi</span>
          </span>
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-gray-900 font-['Plus_Jakarta_Sans',sans-serif]">
            Lacak Paket & Status Resi
          </h1>
          <p class="text-xs sm:text-sm text-gray-600 mt-2 leading-relaxed">
            Masukkan nomor resi ekspedisi (JNE, J&T, SiCepat, TIKI, POS, AnterAja) atau ID Pesanan Anda untuk memeriksa posisi pengiriman.
          </p>
        </div>

        <!-- Input Resi + Select Kurir -->
        <div class="max-w-2xl mx-auto bg-white border border-gray-300 rounded-xl p-2 shadow-sm flex flex-col sm:flex-row gap-2">
          <!-- Dropdown Kurir -->
          <div class="sm:w-44 shrink-0">
            <select
              v-model="selectedCourier"
              class="w-full h-11 px-3 bg-gray-50 border border-gray-200 rounded-lg text-xs font-bold text-gray-900 outline-none focus:border-[#03AC0E] font-['Plus_Jakarta_Sans',sans-serif]"
            >
              <option value="auto">Auto-Detect</option>
              <option value="jne">JNE Express</option>
              <option value="jnt">J&T Express</option>
              <option value="sicepat">SiCepat</option>
              <option value="tiki">TIKI</option>
              <option value="pos">POS Indonesia</option>
              <option value="anteraja">AnterAja</option>
            </select>
          </div>

          <!-- Input Field -->
          <div class="relative flex-1">
            <input
              v-model="waybillInput"
              type="text"
              placeholder="Contoh: JP1234567890 / 001234567890..."
              class="w-full h-11 pl-3.5 pr-10 bg-transparent text-sm text-gray-900 outline-none font-mono placeholder:font-sans placeholder:text-gray-400"
              @keyup.enter="handleTrack"
            />
            <button
              v-if="waybillInput"
              type="button"
              class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black p-1"
              @click="waybillInput = ''"
            >
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            </button>
          </div>

          <!-- Submit Button -->
          <button
            type="button"
            :disabled="isLoading || !waybillInput.trim()"
            class="h-11 px-6 bg-[#03AC0E] hover:bg-[#028C0B] text-white text-xs font-black uppercase tracking-wider rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer shrink-0 font-['Plus_Jakarta_Sans',sans-serif]"
            @click="handleTrack"
          >
            <UIcon v-if="isLoading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            <span>{{ isLoading ? "Melacak..." : "Lacak Paket" }}</span>
          </button>
        </div>

        <!-- Popular Courier Chips -->
        <div class="max-w-2xl mx-auto mt-4 flex flex-wrap items-center justify-center gap-2 text-xs text-gray-500">
          <span class="font-medium font-['Plus_Jakarta_Sans',sans-serif]">Ekspedisi Rekanan:</span>
          <span class="px-2 py-0.5 bg-gray-100 rounded text-gray-700 font-bold">J&T</span>
          <span class="px-2 py-0.5 bg-gray-100 rounded text-gray-700 font-bold">JNE</span>
          <span class="px-2 py-0.5 bg-gray-100 rounded text-gray-700 font-bold">SiCepat</span>
          <span class="px-2 py-0.5 bg-gray-100 rounded text-gray-700 font-bold">TIKI</span>
          <span class="px-2 py-0.5 bg-gray-100 rounded text-gray-700 font-bold">GoSend/Grab</span>
        </div>
      </div>
    </header>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">
      <!-- Error Box -->
      <div
        v-if="errorMessage"
        class="border border-[#c40000] bg-white rounded-xl p-4 shadow-sm flex items-start gap-3"
      >
        <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5 text-[#c40000] shrink-0 mt-0.5" />
        <div>
          <h4 class="text-xs font-bold text-[#c40000] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
            Pelacakan Tidak Ditemukan
          </h4>
          <p class="text-xs text-gray-700 mt-0.5">
            {{ errorMessage }}
          </p>
          <p class="text-[11px] text-gray-500 mt-2">
            Catatan: Nomor resi yang baru diinput admin biasanya membutuhkan waktu 1-3 jam untuk aktif di server ekspedisi.
          </p>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════
           TRACKING RESULT: Amazon Progress + Tokopedia Timeline Card
           ════════════════════════════════════════════════════════════ -->
      <div v-if="trackingData" class="space-y-6">
        <!-- Status Summary Card -->
        <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-xs">
          <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-100">
            <div>
              <span class="text-[10px] uppercase font-bold text-gray-400 tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                Nomor Resi
              </span>
              <div class="flex items-center gap-2 mt-0.5">
                <span class="text-base sm:text-lg font-black font-mono text-gray-900">
                  {{ trackingData.waybill }}
                </span>
                <span class="px-2 py-0.5 bg-[#E6F7E9] text-[#03AC0E] border border-[#C8E6CC] text-[11px] font-bold rounded">
                  {{ trackingData.courier }}
                </span>
              </div>
            </div>

            <!-- Status Badge -->
            <div>
              <span
                class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-['Plus_Jakarta_Sans',sans-serif]"
                :class="trackingData.isDelivered ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'"
              >
                <UIcon :name="trackingData.isDelivered ? 'i-heroicons-check-circle' : 'i-heroicons-arrow-path'" class="w-4 h-4" />
                <span>{{ trackingData.isDelivered ? 'TERKIRIM (DELIVERED)' : 'DALAM PERJALANAN' }}</span>
              </span>
            </div>
          </div>

          <!-- Progress Bar 4-Step -->
          <div class="py-6">
            <div class="grid grid-cols-4 gap-2 text-center text-xs">
              <div class="flex flex-col items-center">
                <div class="w-7 h-7 rounded-full bg-[#03AC0E] text-white flex items-center justify-center font-bold text-xs mb-1">
                  ✓
                </div>
                <span class="font-bold text-gray-900 text-[11px]">Diproses</span>
              </div>
              <div class="flex flex-col items-center">
                <div class="w-7 h-7 rounded-full bg-[#03AC0E] text-white flex items-center justify-center font-bold text-xs mb-1">
                  ✓
                </div>
                <span class="font-bold text-gray-900 text-[11px]">Diserahkan</span>
              </div>
              <div class="flex flex-col items-center">
                <div
                  class="w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs mb-1"
                  :class="trackingData.isDelivered ? 'bg-[#03AC0E] text-white' : 'bg-blue-600 text-white animate-pulse'"
                >
                  {{ trackingData.isDelivered ? '✓' : '3' }}
                </div>
                <span class="font-bold text-gray-900 text-[11px]">Transit Hub</span>
              </div>
              <div class="flex flex-col items-center">
                <div
                  class="w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs mb-1"
                  :class="trackingData.isDelivered ? 'bg-[#03AC0E] text-white' : 'bg-gray-200 text-gray-500'"
                >
                  {{ trackingData.isDelivered ? '✓' : '4' }}
                </div>
                <span class="font-bold text-gray-900 text-[11px]">Diterima</span>
              </div>
            </div>
          </div>

          <!-- Meta Ringkasan Paket -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-gray-100 text-xs">
            <div>
              <span class="text-gray-400 block text-[10px] uppercase font-semibold">Pengirim</span>
              <span class="font-bold text-gray-800">{{ trackingData.summary.shipper_name || 'PasarCCTV Official' }}</span>
            </div>
            <div>
              <span class="text-gray-400 block text-[10px] uppercase font-semibold">Penerima</span>
              <span class="font-bold text-gray-800">{{ trackingData.summary.receiver_name || '-' }}</span>
            </div>
            <div>
              <span class="text-gray-400 block text-[10px] uppercase font-semibold">Kota Asal</span>
              <span class="font-bold text-gray-800">{{ trackingData.summary.origin || 'KOTA BOGOR' }}</span>
            </div>
            <div>
              <span class="text-gray-400 block text-[10px] uppercase font-semibold">Tujuan</span>
              <span class="font-bold text-gray-800">{{ trackingData.summary.destination || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- Manifest Timeline -->
        <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-xs">
          <h3 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-6 font-['Plus_Jakarta_Sans',sans-serif]">
            Riwayat Perjalanan Paket
          </h3>

          <TrackingTimeline
            v-if="trackingData.manifests && trackingData.manifests.length > 0"
            :manifests="trackingData.manifests"
          />

          <div v-else class="text-center py-6 text-gray-400 text-xs">
            Belum ada data riwayat perjalanan dari ekspedisi.
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════
           PANDUAN & ALUR RESI PASARCCTV
           ════════════════════════════════════════════════════════════ -->
      <section class="bg-white border border-gray-200 rounded-xl p-6 sm:p-8 shadow-xs">
        <h2 class="text-base font-bold text-gray-900 mb-4 font-['Plus_Jakarta_Sans',sans-serif]">
          Alur Pengiriman & Pemberian Nomor Resi
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 text-xs text-gray-600">
          <div class="p-4 rounded-lg bg-gray-50 border border-gray-200/70">
            <span class="w-5 h-5 rounded-full bg-black text-white text-[10px] font-bold flex items-center justify-center mb-2 font-['Plus_Jakarta_Sans',sans-serif]">1</span>
            <h3 class="font-bold text-gray-900 mb-1 font-['Plus_Jakarta_Sans',sans-serif]">Checkout & Pembayaran</h3>
            <p>Setelah Anda membayar pesanan, tim gudang kami menyiapkan unit, memeriksa segel garansi resmi, dan melakukan packing bubble berlapis.</p>
          </div>

          <div class="p-4 rounded-lg bg-gray-50 border border-gray-200/70">
            <span class="w-5 h-5 rounded-full bg-black text-white text-[10px] font-bold flex items-center justify-center mb-2 font-['Plus_Jakarta_Sans',sans-serif]">2</span>
            <h3 class="font-bold text-gray-900 mb-1 font-['Plus_Jakarta_Sans',sans-serif]">Penyerahan ke Kurir</h3>
            <p>Paket diserahkan ke gerai ekspedisi rekanan sebelum pukul 17.00 WIB. Admin memasukkan nomor resi resmi ke sistem PasarCCTV.</p>
          </div>

          <div class="p-4 rounded-lg bg-gray-50 border border-gray-200/70">
            <span class="w-5 h-5 rounded-full bg-black text-white text-[10px] font-bold flex items-center justify-center mb-2 font-['Plus_Jakarta_Sans',sans-serif]">3</span>
            <h3 class="font-bold text-gray-900 mb-1 font-['Plus_Jakarta_Sans',sans-serif]">Notifikasi & Pelacakan</h3>
            <p>Nomor resi otomatis tertera di menu Pesanan Saya dan dikirimkan via WhatsApp. Anda dapat memantau pergerakan posisi paket di halaman ini.</p>
          </div>
        </div>

        <div class="mt-6 p-4 rounded-lg bg-[#E6F7E9] border border-[#C8E6CC] flex items-center justify-between flex-wrap gap-3">
          <div class="text-xs text-gray-700">
            <span class="font-bold text-gray-900 block">Butuh bantuan kendala pengiriman atau resi macet?</span>
            Hubungi Customer Service pengiriman kami via WhatsApp.
          </div>
          <a
            href="https://wa.me/6282117779003?text=Halo%20PasarCCTV,%20saya%20ingin%20cek%20status%20resi%20pengiriman."
            target="_blank"
            rel="noopener"
            class="px-4 py-2 bg-[#03AC0E] hover:bg-[#028C0B] text-white text-xs font-bold rounded-lg transition-colors font-['Plus_Jakarta_Sans',sans-serif]"
          >
            Chat CS Pengiriman
          </a>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import TrackingTimeline from '~/components/shipping/TrackingTimeline.vue'
import { ref } from 'vue'

useSeoMeta({
  title: 'Lacak Pengiriman & Cek Resi — PasarCCTV',
  description: 'Lacak status kiriman pesanan kamera CCTV, DVR, NVR dan aksesoris resmi via JNE, J&T, SiCepat, TIKI, dan POS Indonesia.',
})

const waybillInput = ref('')
const selectedCourier = ref('auto')
const isLoading = ref(false)
const errorMessage = ref('')
const trackingData = ref<any>(null)

const handleTrack = async () => {
  const cleanWaybill = waybillInput.value.trim()
  if (!cleanWaybill) return

  isLoading.value = true
  errorMessage.value = ''
  trackingData.value = null

  try {
    const res = await $fetch<any>('/api/shipping/track', {
      method: 'POST',
      body: {
        waybill: cleanWaybill,
        courier: selectedCourier.value === 'auto' ? undefined : selectedCourier.value,
      },
    })
    trackingData.value = res
  } catch (err: any) {
    errorMessage.value = err?.statusMessage || 'Nomor resi tidak ditemukan atau belum terdaftar di sistem ekspedisi.'
  } finally {
    isLoading.value = false
  }
}
</script>