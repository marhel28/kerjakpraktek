<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 font-sans">
    <div class="w-full max-w-5xl bg-white border border-gray-200 shadow-xl rounded-xl overflow-hidden flex flex-col lg:flex-row">

      <!-- Panel kiri -->
      <div class="hidden lg:block lg:w-1/2 bg-black relative">
        <img
          src="https://daganghalal.blob.core.windows.net/44641/Product/cctv-installation-services-1745476968100.jpg"
          alt="PasarCctv Security"
          width="720" height="900"
          class="w-full h-full object-cover opacity-40 grayscale"
          loading="eager"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" aria-hidden="true" />
        <div class="absolute bottom-16 left-12 right-12 text-white">
          <span class="text-4xl font-black tracking-tighter uppercase italic">PasarCctv</span>
          <h2 class="text-3xl font-black uppercase tracking-tight leading-tight mt-6">
            Lupa Password?<br />
            <span class="text-red-600">Tenang aja.</span>
          </h2>
          <p class="text-gray-400 text-sm font-medium leading-relaxed max-w-sm mt-3">
            Masukkan email yang terdaftar dan kami kirimkan link reset password. Link berlaku <strong class="text-white">5 menit</strong>.
          </p>
        </div>
      </div>

      <!-- Panel kanan -->
      <div class="w-full lg:w-1/2 p-10 sm:p-16 flex flex-col justify-center bg-white">

        <div class="mb-10">
          <NuxtLink to="/login" class="inline-flex items-center gap-1.5 text-[11px] font-black uppercase tracking-widest text-gray-400 hover:text-black transition-colors mb-8">
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            Kembali ke Login
          </NuxtLink>

          <h1 class="text-2xl font-black text-black tracking-tight uppercase">Reset Password</h1>
          <p class="text-gray-500 text-xs font-bold mt-2 uppercase tracking-widest">
            Kami kirim link ke email kamu
          </p>
        </div>

        <!-- Success state -->
        <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100">
          <div v-if="sent" class="text-center py-8">
            <div class="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-5">
              <UIcon name="i-heroicons-envelope-open" class="w-8 h-8 text-green-600" />
            </div>
            <h2 class="text-xl font-black text-black uppercase tracking-tight mb-3">Cek Email Kamu</h2>
            <p class="text-gray-500 text-sm leading-relaxed max-w-xs mx-auto mb-1">
              Jika email <strong class="text-black">{{ sentEmail }}</strong> terdaftar, link reset password telah dikirim.
            </p>
            <p class="text-gray-400 text-xs font-bold uppercase tracking-widest mt-1">Link berlaku 5 menit</p>

            <!-- Countdown resend -->
            <div v-if="countdown > 0" class="mt-8 text-[11px] font-bold text-gray-400 uppercase tracking-widest">
              Kirim ulang dalam {{ countdown }}s
            </div>
            <button v-else @click="resetForm" class="mt-8 text-[11px] font-black text-black uppercase tracking-widest border-b border-black hover:border-gray-400 hover:text-gray-600 transition-colors pb-0.5">
              Kirim Ulang
            </button>
          </div>
        </Transition>

        <!-- Form state -->
        <template v-if="!sent">
          <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0 -translate-y-1" enter-to-class="opacity-100">
            <div v-if="errorMessage" role="alert" class="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 text-xs font-bold rounded-lg uppercase tracking-widest flex items-center gap-2">
              <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 flex-shrink-0" />
              {{ errorMessage }}
            </div>
          </Transition>

          <form @submit.prevent="handleSubmit" class="space-y-5" novalidate>
            <div>
              <label for="fp-email" class="block text-[10px] font-black uppercase tracking-widest text-black mb-2">
                Email Terdaftar
              </label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <UIcon name="i-heroicons-envelope" class="w-5 h-5" />
                </span>
                <input
                  id="fp-email"
                  v-model="email"
                  type="email"
                  placeholder="email@contoh.com"
                  autocomplete="email"
                  class="auth-input pl-12"
                  :disabled="isLoading"
                  required
                />
              </div>
            </div>

            <button type="submit" :disabled="isLoading || !email" class="btn-primary w-full mt-6" :aria-busy="isLoading">
              <UIcon v-if="isLoading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <span>{{ isLoading ? 'Mengirim...' : 'Kirim Link Reset' }}</span>
              <UIcon v-if="!isLoading" name="i-heroicons-paper-airplane" class="w-4 h-4" />
            </button>
          </form>
        </template>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Lupa Password — PasarCctv',
  description: 'Reset password akun PasarCctv kamu via email. Link berlaku 5 menit.',
  robots: 'noindex, nofollow',
})

const email     = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const sent      = ref(false)
const sentEmail = ref('')
const countdown = ref(0)

let countdownTimer: ReturnType<typeof setInterval> | null = null

const startCountdown = () => {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0 && countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

const resetForm = () => {
  sent.value = false
  email.value = ''
  errorMessage.value = ''
}

const handleSubmit = async () => {
  if (isLoading.value || !email.value) return
  isLoading.value = true
  errorMessage.value = ''

  try {
    await $fetch('/api/forgot-password', {
      method: 'POST',
      body: { email: email.value.toLowerCase().trim() },
    })
    sentEmail.value = email.value.toLowerCase().trim()
    sent.value = true
    startCountdown()
  } catch (e: any) {
    // Backend selalu return generic message untuk keamanan
    // Tapi tetap tampilkan jika ada network error
    errorMessage.value = e?.data?.message || e?.statusMessage || 'Terjadi kesalahan. Coba lagi.'
  } finally {
    isLoading.value = false
  }
}

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<style scoped>
@reference "tailwindcss";
.auth-input {
  @apply w-full bg-gray-50 border border-gray-200 pr-4 py-3.5 text-sm font-semibold text-black placeholder-gray-400 focus:bg-white focus:border-black focus:ring-1 focus:ring-black outline-none transition-all disabled:opacity-50;
}
.btn-primary {
  @apply bg-black text-white py-4 text-xs font-black uppercase tracking-widest hover:bg-zinc-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
