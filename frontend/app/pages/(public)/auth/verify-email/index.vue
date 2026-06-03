<template>
    <div
        class="min-h-screen bg-gray-50 flex items-center justify-center p-4 font-sans text-gray-800 selection:bg-green-100 selection:text-green-900">

        <main
            class="w-full max-w-md bg-white rounded-2xl shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] border border-gray-100 p-8 text-center relative overflow-hidden transition-all duration-300">

            <div class="absolute top-0 left-0 w-full h-1.5" :class="accentColor"></div>

            <div v-if="status === 'loading'" class="flex flex-col items-center animate-in fade-in duration-500">
                <div class="relative flex items-center justify-center w-20 h-20 mb-6">
                    <div class="absolute inset-0 border-4 border-gray-100 rounded-full"></div>
                    <div
                        class="absolute inset-0 border-4 border-[#03AC0E] rounded-full border-t-transparent animate-spin">
                    </div>
                    <UIcon name="i-heroicons-envelope" class="w-8 h-8 text-[#03AC0E] animate-pulse"
                        aria-hidden="true" />
                </div>
                <h1 class="text-xl font-extrabold text-gray-900 mb-2 tracking-tight">Memverifikasi Email...</h1>
                <p class="text-sm font-medium text-gray-500 leading-relaxed">
                    Mohon tunggu sebentar, kami sedang memvalidasi token keamanan Anda.
                </p>
            </div>

            <div v-else-if="status === 'success'" class="flex flex-col items-center animate-in zoom-in-95 duration-500">
                <div class="w-20 h-20 bg-[#E6F7E9] rounded-full flex items-center justify-center mb-6 shadow-inner">
                    <UIcon name="i-heroicons-check-circle-solid" class="w-12 h-12 text-[#03AC0E]" aria-hidden="true" />
                </div>
                <h1 class="text-xl font-extrabold text-gray-900 mb-2 tracking-tight">Email Berhasil Diverifikasi!</h1>
                <p class="text-sm font-medium text-gray-500 leading-relaxed mb-8">
                    Terima kasih, akun Anda kini sudah aktif sepenuhnya. Anda sudah bisa melakukan login dan mulai
                    bertransaksi.
                </p>

                <NuxtLink to="/auth/login"
                    class="w-full bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm hover:bg-[#008f4c] text-white font-bold py-3.5 px-4 rounded-xl transition-all shadow-md shadow-green-500/20 flex items-center justify-center gap-2 active:scale-[0.98]">
                    Lanjut ke Halaman Login
                    <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
                </NuxtLink>
            </div>

            <div v-else class="flex flex-col items-center animate-in zoom-in-95 duration-500">
                <div class="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mb-6 shadow-inner">
                    <UIcon name="i-heroicons-x-circle-solid" class="w-12 h-12 text-red-500" aria-hidden="true" />
                </div>
                <h1 class="text-xl font-extrabold text-gray-900 mb-2 tracking-tight">Verifikasi Gagal</h1>
                <p
                    class="text-sm font-bold text-red-600 bg-red-50 py-2 px-4 rounded-lg w-full mb-4 border border-red-100">
                    {{ errorMessage }}
                </p>
                <p class="text-xs font-medium text-gray-500 leading-relaxed mb-8">
                    Link verifikasi mungkin sudah kadaluarsa atau tidak valid. Silakan masuk ke akun Anda untuk meminta
                    ulang link verifikasi.
                </p>

                <div class="flex flex-col gap-3 w-full">
                    <NuxtLink to="/login"
                        class="w-full bg-gray-900 hover:bg-gray-800 text-white font-bold py-3.5 px-4 rounded-xl transition-all flex items-center justify-center active:scale-[0.98]">
                        Ke Halaman Login
                    </NuxtLink>
                    <NuxtLink to="/"
                        class="w-full bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-bold py-3.5 px-4 rounded-xl transition-all flex items-center justify-center active:scale-[0.98]">
                        Kembali ke Beranda
                    </NuxtLink>
                </div>
            </div>

        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

type VerifyStatus = 'loading' | 'success' | 'error'

const route = useRoute()
const status = ref<VerifyStatus>('loading')
const errorMessage = ref('')

const accentColor = computed(() => {
  if (status.value === 'success') return 'bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm'
  if (status.value === 'error') return 'bg-red-500'
  return 'bg-gray-200'
})

useHead({
  title: 'Verifikasi Email - PasarCCTV',
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

onMounted(async () => {
  const token = route.query.token as string

  if (!token) {
    status.value = 'error'
    errorMessage.value = 'Token verifikasi tidak valid atau kosong.'
    return
  }

  try {
    // Tembak ke API Server Nuxt lokal, bukan lagi ke FastAPI langsung
    await $fetch('/api/user/verify-email', {
      method: 'GET',
      params: { token }
    })

    // Jika tidak ada error yang dilempar dari server Nuxt, berarti sukses
    status.value = 'success'

  } catch (error: any) {
    status.value = 'error'
    // Ambil pesan error yang dilempar oleh createError() di server/api
    errorMessage.value = error.data?.message || error.message || 'Link verifikasi tidak valid atau sudah kadaluarsa.'
  }
})
</script>

<style scoped>
/* Transisi masuk agar UI tidak kaku (mirip native app) */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px) scale(0.98);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.animate-in {
    animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>