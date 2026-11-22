<template>
  <div class="min-h-screen bg-gray-50 py-10 sm:py-14 px-4 flex flex-col justify-center font-['Open_Sans',sans-serif]">
    <AmazonAuthCard
      hero-image="https://daganghalal.blob.core.windows.net/44641/Product/cctv-installation-services-1745476968100.jpg"
    >
      <!-- Header Tagline -->
      <template #header-tagline>
        <h1 class="text-2xl font-black text-black tracking-tight uppercase font-['Plus_Jakarta_Sans',sans-serif]">
          Masuk Akun
        </h1>
        <p class="text-gray-500 text-xs font-bold mt-1 uppercase tracking-widest font-['Plus_Jakarta_Sans',sans-serif]">
          Akses portal layanan & belanja CCTV
        </p>
      </template>

      <!-- Form Login: Amazon Single-Column Card with PasarCctv Colors (Hitam/Putih/Merah) -->
      <template #form>
        <!-- Alert Sukses Pendaftaran dari Query URL -->
        <div
          v-if="isRegisteredNotice"
          class="bg-green-50 border border-green-300 p-3.5 rounded-md mb-4 flex items-start gap-2.5"
          role="status"
        >
          <UIcon name="i-heroicons-check-circle" class="w-4 h-4 text-green-700 shrink-0 mt-0.5" />
          <p class="text-xs text-green-900 leading-relaxed font-bold">
            Pendaftaran berhasil. Silakan masuk menggunakan email dan kata sandi Anda.
          </p>
        </div>

        <!-- Error alert -->
        <AmazonAlertError v-if="errorMessage" :message="errorMessage" />

        <form @submit.prevent="handleLogin" class="space-y-4" novalidate>
          <!-- Email Input -->
          <div>
            <label
              for="login-email"
              class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]"
            >
              Email Pelanggan
            </label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" aria-hidden="true">
                <UIcon name="i-heroicons-envelope" class="w-4 h-4" />
              </span>
              <input
                id="login-email"
                v-model="email"
                type="email"
                autocomplete="email"
                required
                placeholder="nama@email.com"
                :disabled="isLoading"
                class="auth-input pl-10"
              />
            </div>
          </div>

          <!-- Password Input -->
          <div>
            <div class="flex justify-between items-center mb-1.5">
              <label
                for="login-password"
                class="block text-[11px] font-black uppercase tracking-wider text-black font-['Plus_Jakarta_Sans',sans-serif]"
              >
                Kata Sandi
              </label>
              <NuxtLink
                to="/forgot-password"
                class="text-[11px] font-bold text-gray-500 hover:text-red-600 transition-colors uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]"
              >
                Lupa Password?
              </NuxtLink>
            </div>

            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" aria-hidden="true">
                <UIcon name="i-heroicons-lock-closed" class="w-4 h-4" />
              </span>
              <input
                id="login-password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                placeholder="••••••••"
                :disabled="isLoading"
                class="auth-input pl-10 pr-10"
                @keyup="checkCapsLock"
                @keydown="checkCapsLock"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black p-1 transition-colors"
                :aria-label="showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
                :disabled="isLoading"
                @click="showPassword = !showPassword"
              >
                <UIcon
                  :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  class="w-4 h-4"
                  aria-hidden="true"
                />
              </button>
            </div>
          </div>

          <!-- Remember Me & Caps Lock Warning -->
          <div class="flex items-center justify-between pt-1">
            <label class="flex items-center gap-2 cursor-pointer group select-none">
              <input
                v-model="rememberMe"
                type="checkbox"
                class="w-4 h-4 rounded border-gray-300 text-black focus:ring-black cursor-pointer"
              />
              <span class="text-xs font-bold text-gray-600 group-hover:text-black transition-colors uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                Ingat Saya
              </span>
            </label>

            <!-- Caps Lock Alert -->
            <span v-if="isCapsLockOn" class="text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 flex items-center gap-1">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-3 h-3" />
              Caps Lock Aktif
            </span>
          </div>

          <!-- Submit Button: PasarCctv Solid Black Primary -->
          <button
            type="submit"
            :disabled="isLoading"
            class="auth-btn-primary w-full mt-2"
            :aria-busy="isLoading"
          >
            <UIcon
              v-if="isLoading"
              name="i-heroicons-arrow-path"
              class="w-4 h-4 animate-spin mr-2 inline"
              aria-hidden="true"
            />
            <span>{{ isLoading ? "Memproses..." : "Masuk Sekarang" }}</span>
            <UIcon
              v-if="!isLoading"
              name="i-heroicons-arrow-right"
              class="w-4 h-4 ml-1.5 inline"
              aria-hidden="true"
            />
          </button>
        </form>
      </template>

      <!-- Secondary Actions: Google Sign-In -->
      <template #secondary-actions>
        <div class="flex justify-center w-full min-h-[44px]">
          <div
            id="google_btn_container"
            :class="{ 'opacity-50 pointer-events-none': isLoading }"
            aria-label="Login dengan Google"
          />
        </div>
      </template>

      <!-- Footer: Link Buat Akun Baru + Bantuan CS -->
      <template #footer-links>
        <p class="text-xs font-bold text-gray-500 uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif] mb-3">
          Belum punya akun?
          <NuxtLink
            to="/daftar"
            class="text-black font-black hover:text-red-600 transition-colors ml-1 border-b border-black hover:border-red-600 pb-0.5"
          >
            Daftar Disini
          </NuxtLink>
        </p>

        <!-- Quick Help Escape Hatch -->
        <div class="pt-3 border-t border-gray-100 flex flex-wrap items-center justify-center gap-3 text-xs text-gray-500 font-medium">
          <NuxtLink to="/help" class="hover:text-[#03AC0E] transition-colors flex items-center gap-1">
            <UIcon name="i-heroicons-question-mark-circle" class="w-3.5 h-3.5" />
            <span>Pusat Bantuan</span>
          </NuxtLink>
          <span>•</span>
          <a
            href="https://wa.me/6282218828108?text=Halo%20Teknisi%20PasarCCTV,%20saya%20mengalami%20kendala%20masuk%20akun."
            target="_blank"
            rel="noopener"
            class="hover:text-[#03AC0E] transition-colors flex items-center gap-1"
          >
            <UIcon name="i-heroicons-chat-bubble-left-right" class="w-3.5 h-3.5" />
            <span>Bantuan Login via WA</span>
          </a>
        </div>
      </template>
    </AmazonAuthCard>
  </div>
</template>

<script setup lang="ts">
import AmazonAuthCard from "~/components/auth/AmazonAuthCard.vue";
import AmazonAlertError from "~/components/auth/AmazonAlertError.vue";
import { usePesanStore } from "~/stores/UsePesanStore";
import { useAuth } from "~/composables/useAuth";
import { ref, onMounted, onBeforeUnmount, computed } from "vue";

const pesanStore = usePesanStore();


// ─── SEO ─────────────────────────────────────────────────────────
useSeoMeta({
  title: "Login — PasarCctv",
  description:
    "Masuk ke akun PasarCctv untuk akses produk original dan layanan garansi resmi.",
  robots: "noindex, nofollow",
});

useHead({
  script: [
    {
      src: "https://accounts.google.com/gsi/client",
      async: true,
      defer: true,
      key: "google-gsi",
    },
  ],
});

// ─── Config ───────────────────────────────────────────────────────
const config = useRuntimeConfig();
const GOOGLE_CLIENT_ID = config.public.googleClientId as string;

// ─── State ────────────────────────────────────────────────────────
const email = ref("");
const password = ref("");
const showPassword = ref(false);
const rememberMe = ref(false);
const isLoading = ref(false);
const errorMessage = ref("");
const isCapsLockOn = ref(false);

const checkCapsLock = (e: KeyboardEvent) => {
  isCapsLockOn.value = e.getModifierState("CapsLock");
};

// ─── Stores ───────────────────────────────────────────────────────
const cartStore = useCartStore();
const wishlistStore = useWishlistStore();

// ─── Route ────────────────────────────────────────────────────────
const route = useRoute();
const router = useRouter();
const isRegisteredNotice = computed(() => route.query.registered === "1");

const redirectAfterLogin = async () => {
  try {
    await Promise.all([cartStore.mergeCartOnLogin(), wishlistStore.fetchWishlist()]);
  } catch {
    // Sync gagal tidak halangi redirect
  }
  const redirectTo = (route.query.redirect as string) || "/";
  await router.push(redirectTo);
};

// ─── Login via email ──────────────────────────────────────────────
const handleLogin = async () => {
  if (isLoading.value) return;
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await $fetch("/api/login", {
      method: "POST",
      body: { email: email.value, password: password.value },
    });

    if (typeof response.initialUnread === "number") {
      pesanStore.unreadCount = response.initialUnread;
    }

    pesanStore.initAfterLogin();
    await redirectAfterLogin();
  } catch (error: any) {
    errorMessage.value =
      error?.data?.detail ||
      error?.statusMessage ||
      "Kombinasi email dan kata sandi salah. Silakan coba lagi.";
  } finally {
    isLoading.value = false;
  }
};

// ─── Login via Google ─────────────────────────────────────────────
const handleGoogleCallback = async (response: any) => {
  if (isLoading.value) return;
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const googleResponse = await $fetch("/api/user/google", {
      method: "POST",
      body: { id_token: response.credential },
    });

    if (typeof googleResponse.initialUnread === "number") {
      pesanStore.unreadCount = googleResponse.initialUnread;
    }

    pesanStore.initAfterLogin();
    await redirectAfterLogin();
  } catch (error: any) {
    errorMessage.value =
      error?.data?.message ||
      error?.data?.detail ||
      error?.statusMessage ||
      "Gagal masuk menggunakan akun Google.";
  } finally {
    isLoading.value = false;
  }
};

// ─── Inisialisasi Google GSI ──────────────────────────────────────
let gsiCleanup: (() => void) | null = null;

const initGoogleGsi = () => {
  if (!window.google?.accounts?.id) return false;

  window.google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: handleGoogleCallback,
    ux_mode: "popup",
    cancel_on_tap_outside: false,
  });

  const container = document.getElementById("google_btn_container");
  if (container) {
    window.google.accounts.id.renderButton(container, {
      theme: "outline",
      size: "large",
      text: "continue_with",
      width: 320,
      logo_alignment: "center",
    });
  }

  return true;
};

onMounted(() => {
  if (initGoogleGsi()) return;

  const script = document.querySelector<HTMLScriptElement>(
    'script[src="https://accounts.google.com/gsi/client"]'
  );

  if (script) {
    const onLoad = () => {
      initGoogleGsi();
      script.removeEventListener("load", onLoad);
    };
    script.addEventListener("load", onLoad);
    gsiCleanup = () => script.removeEventListener("load", onLoad);
  } else {
    let attempts = 0;
    const MAX_ATTEMPTS = 30;
    const timer = setInterval(() => {
      attempts++;
      if (initGoogleGsi() || attempts >= MAX_ATTEMPTS) {
        clearInterval(timer);
      }
    }, 100);
    gsiCleanup = () => clearInterval(timer);
  }
});

onBeforeUnmount(() => {
  gsiCleanup?.();
  try {
    window.google?.accounts?.id?.cancel();
  } catch {
    /* noop */
  }
});
</script>

<style scoped>
/* Scoped styles now use global design tokens from main.css via .auth-input and .auth-btn-primary classes */
</style>