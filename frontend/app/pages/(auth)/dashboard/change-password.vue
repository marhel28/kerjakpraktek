<script setup lang="ts">
import { ref, computed } from 'vue';

definePageMeta({ layout: "auth" });
useSeoMeta({ title: 'Keamanan Akun — PasarCctv', robots: 'noindex, nofollow' })

const token = useCookie('token')
const userDataCookie = useCookie<any>('user_data')

const isGoogleUser = computed(() => {
  try {
    const u = typeof userDataCookie.value === 'string' ? JSON.parse(userDataCookie.value) : userDataCookie.value
    return u?.user_type === 'google'
  } catch { return false }
})

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const done = ref(false)

const tabs = [
  { label: "Biodata Diri", to: "/dashboard" },
  { label: "Daftar Alamat", to: "/dashboard/address" },
  { label: "Keamanan Akun", to: "/dashboard/change-password" },
  { label: "Notifikasi", to: "/dashboard/notifications" },
];

const canSubmit = computed(() => oldPassword.value.length > 0 && newPassword.value.length >= 6 && newPassword.value === confirmPassword.value)

const strength = computed(() => {
  const p = newPassword.value; if (!p) return 0;
  let s = 0; if (p.length >= 6) s++; if (p.length >= 10) s++; if (/[A-Z]/.test(p) && /[0-9]/.test(p)) s++; if (/[^A-Za-z0-9]/.test(p)) s++;
  return s
})

const strengthConfig = computed(() => {
  if (strength.value <= 1) return { color: 'bg-red-500', label: 'Lemah' }
  if (strength.value === 2) return { color: 'bg-amber-500', label: 'Cukup' }
  if (strength.value === 3) return { color: 'bg-blue-500', label: 'Kuat' }
  return { color: 'bg-green-500', label: 'Sangat Kuat' }
})

const resetForm = () => { oldPassword.value = ''; newPassword.value = ''; confirmPassword.value = ''; done.value = false; errorMessage.value = ''; }

const handleSubmit = async () => {
  if (!canSubmit.value || isLoading.value) return
  isLoading.value = true; errorMessage.value = ''
  try {
    await $fetch('/api/change-password', { method: 'POST', headers: { Authorization: `Bearer ${token.value}` }, body: { old_password: oldPassword.value, new_password: newPassword.value } })
    done.value = true
  } catch (e: any) { errorMessage.value = e?.data?.message || 'Password lama salah.' } finally { isLoading.value = false }
}
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- MOBILE HEADER -->
    <div class="lg:hidden flex items-center gap-4 px-6 py-4 border-b border-gray-100 bg-white sticky top-0 z-10">
      <button @click="$router.push('/dashboard')" class="p-1 -ml-1 text-gray-400 hover:text-gray-900 transition-colors">
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </button>
      <h1 class="text-base font-black text-gray-900 uppercase tracking-wider">Keamanan Akun</h1>
    </div>

    <!-- TABS (Desktop Only) -->
    <div class="hidden lg:block border-b border-gray-200 overflow-x-auto no-scrollbar">
      <div class="flex px-8">
        <NuxtLink
          v-for="tab in tabs"
          :key="tab.to"
          :to="tab.to"
          class="px-6 py-4 text-sm font-bold whitespace-nowrap transition-colors relative"
          :class="[
            $route.path === tab.to 
              ? 'text-[#03AC0E]' 
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          {{ tab.label }}
          <div v-if="$route.path === tab.to" class="absolute bottom-0 left-0 right-0 h-1 bg-[#03AC0E] rounded-t-full"></div>
        </NuxtLink>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="p-4 sm:p-8">
      <div class="max-w-2xl">
        <header class="hidden lg:block mb-8">
          <h2 class="text-xl font-bold text-gray-900">Ganti Password</h2>
          <p class="text-xs text-gray-400 mt-1 uppercase tracking-widest font-bold">Gunakan password yang kuat & unik</p>
        </header>

        <main>
          <div v-if="isGoogleUser" class="p-8 text-center space-y-4 border border-gray-200 rounded-xl">
            <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto">
              <UIcon name="i-heroicons-information-circle" class="w-6 h-6" />
            </div>
            <p class="text-sm font-bold text-gray-900">Login via Google</p>
            <p class="text-xs text-gray-500 leading-relaxed">Akun Anda terhubung dengan Google. Password dikelola secara otomatis oleh Google.</p>
          </div>

          <div v-else>
            <Transition name="fade" mode="out-in">
              <div v-if="done" class="text-center py-10 space-y-6 border border-gray-200 rounded-xl">
                <div class="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
                  <UIcon name="i-heroicons-check-circle" class="w-8 h-8" />
                </div>
                <h2 class="text-lg font-bold text-gray-900">Password Diperbarui</h2>
                <button @click="resetForm" class="text-sm font-bold text-[#03AC0E] hover:underline">Ganti Lagi</button>
              </div>

              <form v-else @submit.prevent="handleSubmit" class="space-y-8">
                <div v-if="errorMessage" class="text-xs font-bold text-red-500 text-center bg-red-50 py-3 rounded-lg border border-red-100 uppercase tracking-widest">
                  {{ errorMessage }}
                </div>

                <!-- Inputs -->
                <div class="space-y-6">
                  <div class="space-y-2">
                    <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Password Sekarang</label>
                    <div class="relative">
                      <input v-model="oldPassword" :type="showOld ? 'text' : 'password'" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-[#03AC0E] text-sm font-medium outline-none transition-all" />
                      <button type="button" @click="showOld = !showOld" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-900">
                        <UIcon :name="showOld ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div class="space-y-2">
                    <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Password Baru</label>
                    <div class="relative">
                      <input v-model="newPassword" :type="showNew ? 'text' : 'password'" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-[#03AC0E] text-sm font-medium outline-none transition-all" />
                      <button type="button" @click="showNew = !showNew" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-900">
                        <UIcon :name="showNew ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
                      </button>
                    </div>
                    <!-- Strength -->
                    <div v-if="newPassword" class="flex gap-1 pt-2">
                      <div v-for="i in 4" :key="i" class="h-1 flex-1 rounded-full transition-all" :class="strength >= i ? strengthConfig.color : 'bg-gray-100'" />
                    </div>
                    <div v-if="newPassword" class="text-[10px] font-bold text-gray-400">Kekuatan Password: <span :class="strengthConfig.color.replace('bg-', 'text-')">{{ strengthConfig.label }}</span></div>
                  </div>

                  <div class="space-y-2">
                    <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Konfirmasi Password Baru</label>
                    <div class="relative">
                      <input v-model="confirmPassword" :type="showConfirm ? 'text' : 'password'" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-[#03AC0E] text-sm font-medium outline-none transition-all" />
                      <button type="button" @click="showConfirm = !showConfirm" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-900">
                        <UIcon :name="showConfirm ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>

                <button type="submit" :disabled="isLoading || !canSubmit" class="w-full py-4 bg-[#03AC0E] text-white text-sm font-black rounded-lg hover:bg-[#028a0b] disabled:opacity-30 transition-all flex items-center justify-center gap-3 shadow-sm">
                  <UIcon v-if="isLoading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  Simpan Perubahan
                </button>
              </form>
            </Transition>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(5px); }
</style>
