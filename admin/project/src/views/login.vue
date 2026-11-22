<template>
    <div
        class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8 font-sans selection:bg-indigo-100 selection:text-indigo-900">
        <div
            class="max-w-md w-full bg-white p-8 sm:p-10 rounded-2xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-300">

            <div class="text-center mb-8">
                <div class="flex justify-center items-center mb-4">
                    <img src="@/assets/pasarcctv.png" alt="PasarCCTV Logo" class="h-12 w-auto object-contain"
                        onerror="this.style.display='none'" />
                    <div
                        class="h-12 w-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold text-2xl shadow-sm fallback-icon">
                        P
                    </div>
                </div>
                <h2 class="text-2xl font-bold text-gray-800 tracking-tight">
                    Admin Marketplace
                </h2>
                <p class="mt-2 text-sm text-gray-500">
                    Masuk ke dashboard untuk mengelola sistem
                </p>
            </div>

            <div v-if="authStore.error" class="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl flex items-center gap-2">
                <svg class="w-5 h-5 flex-shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ authStore.error }}</span>
            </div>

            <form class="space-y-6" @submit.prevent="handleLogin">

                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700 mb-1.5">
                        Alamat email
                    </label>
                    <div class="relative">
                        <input id="email" v-model="email" type="email" required autocomplete="username"
                            placeholder="admin@pasarcctv.com"
                            class="block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all duration-200" />
                    </div>
                </div>

                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700 mb-1.5">
                        Kata sandi
                    </label>
                    <div class="relative">
                        <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" required
                            autocomplete="current-password" placeholder="••••••••"
                            class="block w-full pl-4 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all duration-200" />

                        <button type="button" @click="togglePassword"
                            :aria-label="showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
                            :aria-pressed="showPassword"
                            class="absolute inset-y-0 right-0 pr-4 flex items-center min-w-11 text-gray-400 hover:text-indigo-600 transition-colors">
                            <svg v-if="!showPassword" class="w-5 h-5" fill="none" viewBox="0 0 24 24"
                                stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                            <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                                stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                            </svg>
                        </button>
                    </div>
                </div>

                <div class="flex items-center justify-end mt-4">
                    <a :href="forgotPasswordUrl" target="_blank" rel="noopener noreferrer"
                        class="font-medium text-indigo-600 hover:text-indigo-500 transition-colors">
                        Lupa kata sandi?
                    </a>
                </div>

                <div class="pt-2">
                    <button type="submit" :disabled="isLoading"
                        class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 active:scale-95 transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed disabled:active:scale-100">
                        <span v-if="!isLoading">Masuk</span>
                        <template v-else>
                            <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                            </circle>
                            <path class="opacity-75" fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                            </path>
                            </svg>
                            <span>Sedang masuk...</span>
                        </template>
                    </button>
                </div>

            </form>
        </div>

    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePreviewStore } from '@/stores/previewStore'

const authStore = useAuthStore()
const router = useRouter()
const previewStore = usePreviewStore()

const forgotPasswordUrl = computed(() => previewStore.resolveUrl('/forgot-password'))

// State
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)

// Actions
const togglePassword = () => {
    showPassword.value = !showPassword.value
}

const handleLogin = async () => {
    if (!email.value || !password.value) return

    isLoading.value = true

    try {
        const success = await authStore.login(email.value, password.value)
        if (success) {
            router.push('/')
        }
    } catch (error) {
        console.error('Login error:', error)
    } finally {
        isLoading.value = false
    }
}
</script>

<style scoped>
/* Fallback CSS to hide the placeholder 'P' if the image successfully loads */
img:not([style*="display: none"])+.fallback-icon {
    display: none;
}
</style>