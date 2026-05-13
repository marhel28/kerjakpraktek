<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 font-sans selection:bg-black selection:text-white"
  >
    <div
      class="w-full max-w-5xl bg-white border border-gray-200 shadow-xl rounded-xl overflow-hidden flex flex-col lg:flex-row"
    >
      <!-- ── Panel kiri (dekorasi) ──────────────────────────────── -->
      <div class="hidden lg:block lg:w-1/2 bg-black relative">
        <img
          src="https://daganghalal.blob.core.windows.net/44641/Product/cctv-installation-services-1745476968100.jpg"
          alt="PasarCctv Security"
          width="720"
          height="900"
          class="w-full h-full object-cover opacity-40 grayscale"
          loading="eager"
          fetchpriority="high"
        />
        <div
          class="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent"
          aria-hidden="true"
        />

        <div class="absolute bottom-16 left-12 right-12 text-white">
          <div class="flex flex-col leading-none mb-6">
            <span class="text-4xl font-black text-white tracking-tighter uppercase italic"
              >PasarCctv</span
            >
            <span class="text-xl font-light text-gray-400 tracking-[0.3em] uppercase mt-1"
              >CCTV</span
            >
            <div class="barcode-element-white mt-4" aria-hidden="true" />
          </div>
          <h1 class="text-3xl font-black uppercase tracking-tight leading-tight mb-3">
            Sistem Keamanan <br />
            <span class="text-red-600">Nomor 1</span> di Indonesia.
          </h1>
          <p class="text-gray-400 text-sm font-medium leading-relaxed max-w-sm">
            Masuk untuk mengakses produk original, layanan garansi resmi, dan penjadwalan
            instalasi teknisi profesional.
          </p>
        </div>
      </div>

      <!-- ── Panel kanan (form) ─────────────────────────────────── -->
      <div
        class="w-full lg:w-1/2 p-10 sm:p-16 flex flex-col justify-center bg-white relative"
      >
        <div class="absolute top-8 right-10 hidden sm:block" aria-hidden="true">
          <div class="barcode-element-black" />
        </div>

        <!-- Logo mobile -->
        <div class="mb-10 text-center lg:text-left">
          <div class="flex flex-col leading-none mb-6 lg:hidden items-center">
            <span class="text-3xl font-black text-black tracking-tighter uppercase italic"
              >PasarCctv</span
            >
            <span class="text-base font-light text-gray-500 tracking-[0.3em] uppercase"
              >CCTV</span
            >
          </div>
          <h2 class="text-2xl font-black text-black tracking-tight uppercase">
            Selamat Datang
          </h2>
          <p class="text-gray-500 text-xs font-bold mt-2 uppercase tracking-widest">
            Masuk ke akun belanja Anda
          </p>
        </div>

        <!-- Error message -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div
            v-if="errorMessage"
            role="alert"
            aria-live="polite"
            class="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 text-xs font-bold rounded-lg uppercase tracking-widest flex items-center gap-2"
          >
            <UIcon
              name="i-heroicons-exclamation-circle"
              class="w-4 h-4 flex-shrink-0"
              aria-hidden="true"
            />
            {{ errorMessage }}
          </div>
        </Transition>

        <!-- Form login -->
        <form @submit.prevent="handleLogin" class="space-y-5" novalidate>
          <!-- Email -->
          <div>
            <label
              for="login-email"
              class="block text-[10px] font-black uppercase tracking-widest text-black mb-2"
            >
              Email Pelanggan
            </label>
            <div class="relative">
              <span
                class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                aria-hidden="true"
              >
                <UIcon name="i-heroicons-envelope" class="w-5 h-5" />
              </span>
              <input
                id="login-email"
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

          <!-- Password -->
          <div>
            <div class="flex justify-between items-end mb-2">
              <label
                for="login-password"
                class="block text-[10px] font-black uppercase tracking-widest text-black"
              >
                Password
              </label>
              <NuxtLink
                to="/forgot-password"
                class="text-[10px] font-bold text-gray-500 hover:text-red-600 uppercase tracking-widest transition-colors"
              >
                Lupa Password?
              </NuxtLink>
            </div>
            <div class="relative">
              <span
                class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                aria-hidden="true"
              >
                <UIcon name="i-heroicons-lock-closed" class="w-5 h-5" />
              </span>
              <input
                id="login-password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                autocomplete="current-password"
                class="auth-input pl-12 pr-12"
                :disabled="isLoading"
                required
              />
              <button
                type="button"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black transition-colors"
                :aria-label="showPassword ? 'Sembunyikan password' : 'Tampilkan password'"
                :disabled="isLoading"
                @click="showPassword = !showPassword"
              >
                <UIcon
                  :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  class="w-5 h-5"
                  aria-hidden="true"
                />
              </button>
            </div>
          </div>

          <!-- Remember me -->
          <div class="flex items-center">
            <label class="flex items-center gap-3 cursor-pointer group">
              <div class="relative flex items-center justify-center">
                <input
                  v-model="rememberMe"
                  type="checkbox"
                  class="peer appearance-none w-4 h-4 border-2 border-gray-300 rounded-sm checked:bg-black checked:border-black transition-colors cursor-pointer"
                />
                <UIcon
                  name="i-heroicons-check"
                  class="absolute w-3 h-3 text-white opacity-0 peer-checked:opacity-100 pointer-events-none"
                  aria-hidden="true"
                />
              </div>
              <span
                class="text-[11px] font-bold text-gray-500 group-hover:text-black transition-colors uppercase tracking-wider"
              >
                Ingat Saya
              </span>
            </label>
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="isLoading"
            class="btn-primary w-full mt-6"
            :aria-busy="isLoading"
          >
            <UIcon
              v-if="isLoading"
              name="i-heroicons-arrow-path"
              class="w-4 h-4 animate-spin"
              aria-hidden="true"
            />
            <span>{{ isLoading ? "Memproses..." : "Masuk Sekarang" }}</span>
            <UIcon
              v-if="!isLoading"
              name="i-heroicons-arrow-right"
              class="w-4 h-4"
              aria-hidden="true"
            />
          </button>
        </form>

        <!-- Divider -->
        <div class="flex items-center my-8" aria-hidden="true">
          <div class="flex-grow border-t border-gray-200" />
          <span
            class="mx-4 text-[10px] font-black text-gray-400 uppercase tracking-widest"
            >Atau</span
          >
          <div class="flex-grow border-t border-gray-200" />
        </div>

        <!--
          Google Sign-In button container.
          id="google_btn_container" dipakai oleh Google GSI SDK untuk render tombol.
          min-h agar tidak ada layout shift saat button render.
        -->
        <div class="flex justify-center w-full min-h-[44px]">
          <div
            id="google_btn_container"
            :class="{ 'opacity-50 pointer-events-none': isLoading }"
            aria-label="Login dengan Google"
          />
        </div>

        <p
          class="text-center text-gray-500 mt-10 text-[11px] font-bold uppercase tracking-wider"
        >
          Belum punya akun?
          <NuxtLink
            to="/daftar"
            class="text-black font-black hover:text-red-600 transition-colors ml-1 border-b border-black hover:border-red-600 pb-0.5"
          >
            Daftar Disini
          </NuxtLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePesanStore } from "~/stores/UsePesanStore";
const pesanStore = usePesanStore();
import { ref, onMounted, onBeforeUnmount } from "vue";
const { setSupabaseSession } = useAuth();

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

// ─── Stores ───────────────────────────────────────────────────────
const cartStore = useCartStore();
const wishlistStore = useWishlistStore();

// ─── Route ────────────────────────────────────────────────────────
const route = useRoute();
const router = useRouter();

// 🆕 Cookie Supabase user ID
const supabaseUserId = useCookie("supabase_user");

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

    // 🆕 Simpan Supabase User ID ke cookie
    if (response.supabase?.user?.id) {
      supabaseUserId.value = response.supabase.user.id;
    }
    if (typeof response.initialUnread === "number") {
      pesanStore.unreadCount = response.initialUnread;
    }

    // Mulai polling pasif (2 menit) untuk jaga badge tetap segar
    pesanStore.startPassivePolling();
    await setSupabaseSession();
    await redirectAfterLogin();
  } catch (error: any) {
    errorMessage.value =
      error?.data?.detail ||
      error?.statusMessage ||
      "Kombinasi email dan password salah.";
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

    // 🆕 Simpan Supabase User ID ke cookie
    if (googleResponse.supabase?.user?.id) {
      supabaseUserId.value = googleResponse.supabase.user.id;
    }

    await setSupabaseSession();
    await redirectAfterLogin();
  } catch (error: any) {
    errorMessage.value =
      error?.data?.detail || error?.statusMessage || "Gagal masuk menggunakan Google.";
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
      width: 350,
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
@import "@/assets/main.css";

.auth-input {
  @apply w-full bg-gray-50 border border-gray-200 pr-4 py-3.5 text-sm font-semibold text-black placeholder-gray-400 focus:bg-white focus:border-black focus:ring-1 focus:ring-black outline-none transition-all disabled:opacity-50;
}

.btn-primary {
  @apply bg-black text-white py-4 text-xs font-black uppercase tracking-widest hover:bg-zinc-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed;
}

/* Ornamen barcode */
.barcode-element-white {
  height: 6px;
  width: 80px;
  background: linear-gradient(90deg, #fff 10px, transparent 10px),
    repeating-linear-gradient(
      90deg,
      transparent 0,
      transparent 12px,
      #fff 12px,
      #fff 14px
    );
  background-repeat: no-repeat, repeat;
}

.barcode-element-black {
  height: 8px;
  width: 60px;
  background: linear-gradient(90deg, #000 8px, transparent 8px),
    repeating-linear-gradient(
      90deg,
      transparent 0,
      transparent 10px,
      #000 10px,
      #000 12px
    );
  background-repeat: no-repeat, repeat;
}
</style>
