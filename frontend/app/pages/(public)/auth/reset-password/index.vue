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
            Buat Password<br />
            <span class="text-red-600">Baru Kamu.</span>
          </h2>
          <p class="text-gray-400 text-sm font-medium leading-relaxed max-w-sm mt-3">
            Buat password baru yang kuat dan mudah kamu ingat.
          </p>
        </div>
      </div>

      <!-- Panel kanan -->
      <div class="w-full lg:w-1/2 p-10 sm:p-16 flex flex-col justify-center bg-white">

        <!-- Invalid token state -->
        <div v-if="tokenInvalid" class="text-center py-8">
          <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-5">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-500" />
          </div>
          <h1 class="text-xl font-black text-black uppercase tracking-tight mb-3">Link Kadaluarsa</h1>
          <p class="text-gray-500 text-sm leading-relaxed max-w-xs mx-auto mb-8">
            Link reset password tidak valid atau sudah kadaluarsa (berlaku 5 menit).
          </p>
          <NuxtLink to="/forgot-password" class="btn-primary inline-flex items-center gap-2 px-8 py-4">
            <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
            Minta Link Baru
          </NuxtLink>
        </div>

        <!-- Success state -->
        <div v-else-if="done" class="text-center py-8">
          <div class="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-5">
            <UIcon name="i-heroicons-check-badge" class="w-8 h-8 text-green-600" />
          </div>
          <h1 class="text-xl font-black text-black uppercase tracking-tight mb-3">Password Berhasil Diubah</h1>
          <p class="text-gray-500 text-sm leading-relaxed max-w-xs mx-auto mb-8">
            Password baru kamu sudah aktif. Silakan login sekarang.
          </p>
          <NuxtLink to="/login" class="btn-primary inline-flex items-center gap-2 px-8 py-4">
            <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-4 h-4" />
            Login Sekarang
          </NuxtLink>
        </div>

        <!-- Form state -->
        <template v-else-if="token">
          <div class="mb-10">
            <h1 class="text-2xl font-black text-black tracking-tight uppercase">Password Baru</h1>
            <p class="text-gray-500 text-xs font-bold mt-2 uppercase tracking-widest">
              Buat password yang kuat (min. 6 karakter)
            </p>
          </div>

          <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0 -translate-y-1" enter-to-class="opacity-100">
            <div v-if="errorMessage" role="alert" class="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 text-xs font-bold rounded-lg uppercase tracking-widest flex items-center gap-2">
              <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 flex-shrink-0" />
              {{ errorMessage }}
            </div>
          </Transition>

          <form @submit.prevent="handleSubmit" class="space-y-5" novalidate>
            <div>
              <label for="rp-password" class="block text-[10px] font-black uppercase tracking-widest text-black mb-2">
                Password Baru
              </label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <UIcon name="i-heroicons-lock-closed" class="w-5 h-5" />
                </span>
                <input
                  id="rp-password"
                  v-model="newPassword"
                  :type="showNew ? 'text' : 'password'"
                  placeholder="Min. 6 karakter"
                  autocomplete="new-password"
                  class="auth-input pl-12 pr-12"
                  :disabled="isLoading"
                  minlength="6"
                  required
                />
                <button type="button" @click="showNew = !showNew" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black transition-colors">
                  <UIcon :name="showNew ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-5 h-5" />
                </button>
              </div>
            </div>

            <div>
              <label for="rp-confirm" class="block text-[10px] font-black uppercase tracking-widest text-black mb-2">
                Konfirmasi Password
              </label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <UIcon name="i-heroicons-lock-closed" class="w-5 h-5" />
                </span>
                <input
                  id="rp-confirm"
                  v-model="confirmPassword"
                  :type="showConfirm ? 'text' : 'password'"
                  placeholder="Ulangi password baru"
                  autocomplete="new-password"
                  class="auth-input pl-12 pr-12"
                  :class="confirmPassword && newPassword !== confirmPassword ? 'border-red-400 focus:border-red-500 focus:ring-red-500' : ''"
                  :disabled="isLoading"
                  required
                />
                <button type="button" @click="showConfirm = !showConfirm" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black transition-colors">
                  <UIcon :name="showConfirm ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-5 h-5" />
                </button>
              </div>
              <p v-if="confirmPassword && newPassword !== confirmPassword" class="mt-1.5 text-[11px] font-bold text-red-500 uppercase tracking-wider">
                Password tidak cocok
              </p>
            </div>

            <!-- Password strength indicator -->
            <div v-if="newPassword" class="space-y-1.5">
              <div class="flex gap-1">
                <div v-for="i in 4" :key="i" class="h-1 flex-1 rounded-full transition-colors"
                  :class="strength >= i ? strengthColor : 'bg-gray-200'" />
              </div>
              <p class="text-[11px] font-bold uppercase tracking-wider" :class="strengthTextColor">
                {{ strengthLabel }}
              </p>
            </div>

            <button type="submit"
              :disabled="isLoading || !canSubmit"
              class="btn-primary w-full mt-6"
              :aria-busy="isLoading"
            >
              <UIcon v-if="isLoading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <span>{{ isLoading ? 'Menyimpan...' : 'Simpan Password Baru' }}</span>
              <UIcon v-if="!isLoading" name="i-heroicons-check" class="w-4 h-4" />
            </button>
          </form>
        </template>

        <!-- No token / loading -->
        <div v-else class="text-center py-8">
          <div class="w-8 h-8 border-2 border-black border-t-transparent rounded-full animate-spin mx-auto" />
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Reset Password — PasarCctv',
  description: 'Buat password baru untuk akun PasarCctv kamu.',
  robots: 'noindex, nofollow',
})

const route = useRoute()
const router = useRouter()

const token          = computed(() => route.query.token as string | undefined)
const newPassword    = ref('')
const confirmPassword= ref('')
const showNew        = ref(false)
const showConfirm    = ref(false)
const isLoading      = ref(false)
const errorMessage   = ref('')
const done           = ref(false)
const tokenInvalid   = ref(false)

const canSubmit = computed(() =>
  newPassword.value.length >= 6 &&
  newPassword.value === confirmPassword.value
)

// Password strength
const strength = computed(() => {
  const p = newPassword.value
  if (!p) return 0
  let s = 0
  if (p.length >= 6)  s++
  if (p.length >= 10) s++
  if (/[A-Z]/.test(p) && /[0-9]/.test(p)) s++
  if (/[^A-Za-z0-9]/.test(p)) s++
  return s
})

const strengthColor = computed(() => {
  if (strength.value <= 1) return 'bg-red-400'
  if (strength.value === 2) return 'bg-yellow-400'
  if (strength.value === 3) return 'bg-blue-400'
  return 'bg-green-500'
})

const strengthTextColor = computed(() => {
  if (strength.value <= 1) return 'text-red-500'
  if (strength.value === 2) return 'text-yellow-600'
  if (strength.value === 3) return 'text-blue-600'
  return 'text-green-600'
})

const strengthLabel = computed(() => {
  if (strength.value <= 1) return 'Lemah'
  if (strength.value === 2) return 'Cukup'
  if (strength.value === 3) return 'Kuat'
  return 'Sangat Kuat'
})

const handleSubmit = async () => {
  if (!canSubmit.value || isLoading.value) return
  isLoading.value = true
  errorMessage.value = ''

  try {
    await $fetch('/api/reset-password', {
      method: 'POST',
      body: { token: token.value, new_password: newPassword.value },
    })
    done.value = true
  } catch (e: any) {
    const msg = e?.data?.message || e?.statusMessage || ''
    if (msg.toLowerCase().includes('valid') || msg.toLowerCase().includes('kadaluarsa')) {
      tokenInvalid.value = true
    } else {
      errorMessage.value = msg || 'Gagal menyimpan password. Coba lagi.'
    }
  } finally {
    isLoading.value = false
  }
}

// Jika tidak ada token di URL, redirect ke forgot-password
onMounted(() => {
  if (!token.value) router.replace('/forgot-password')
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
