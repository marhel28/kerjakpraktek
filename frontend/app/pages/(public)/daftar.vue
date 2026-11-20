<template>
  <div class="min-h-screen bg-gray-50 py-10 sm:py-14 px-4 flex flex-col justify-center font-['Open_Sans',sans-serif]">
    <AmazonAuthCard
      :is-registration="true"
      hero-image="https://static.jakmall.id/2023/12/images/products/e92af9/original/xiaomi-kamera-cctv-smart-google-home-alexa-360-rotation-full-hd-c200.png"
    >
      <!-- Header Tagline -->
      <template #header-tagline>
        <h1 class="text-2xl font-black text-black tracking-tight uppercase font-['Plus_Jakarta_Sans',sans-serif]">
          {{ currentStep === 0 ? "Buat Akun" : "Lengkapi Profil" }}
        </h1>
        <p class="text-gray-500 text-xs font-bold mt-1 uppercase tracking-widest font-['Plus_Jakarta_Sans',sans-serif]">
          {{ currentStep === 0 ? "Data Akun Utama Pelanggan" : "Info Pengiriman & Tipe Akun" }}
        </p>
      </template>

      <!-- Form Content -->
      <template #form>
        <!-- Error alert -->
        <AmazonAlertError v-if="errorMsg" :message="errorMsg" />

        <!-- Sukses Step 1 Banner -->
        <div
          v-if="currentStep === 1"
          class="bg-green-50 border border-green-300 p-3.5 rounded-md mb-4 flex items-start gap-2.5"
          role="status"
        >
          <UIcon name="i-heroicons-check-circle" class="w-4 h-4 text-green-700 shrink-0 mt-0.5" />
          <p class="text-xs text-green-900 leading-relaxed font-bold">
            Akun berhasil dibuat! Tautan verifikasi telah dikirim ke <span class="underline">{{ form.email }}</span>.
          </p>
        </div>

        <!-- STEP 0: Register Utama -->
        <form v-if="currentStep === 0" @submit.prevent="handleRegister" class="space-y-4" novalidate>
          <!-- Username Input -->
          <div>
            <label for="reg-username" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">
              Username <span class="text-red-600">*</span>
            </label>
            <input
              id="reg-username"
              v-model="form.username"
              type="text"
              autocomplete="username"
              required
              minlength="3"
              maxlength="50"
              placeholder="username_kamu"
              :disabled="loading"
              class="auth-input px-3.5"
            />
            <p class="text-[10px] text-gray-500 mt-1 font-semibold">Min. 3 karakter, maks. 50 karakter.</p>
          </div>

          <!-- Email Input with inline validation -->
          <div>
            <label for="reg-email" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">
              Email Korespondensi <span class="text-red-600">*</span>
            </label>
            <input
              id="reg-email"
              v-model="form.email"
              type="email"
              autocomplete="email"
              required
              placeholder="email@contoh.com"
              :disabled="loading"
              class="auth-input px-3.5"
              :class="{ 'border-red-400 focus:border-red-500 focus:ring-red-500': emailError }"
              @blur="validateEmail"
            />
            <p v-if="emailError" class="text-xs text-red-600 mt-1 font-semibold">{{ emailError }}</p>
          </div>

          <!-- Password Input with toggle + caps + live rules -->
          <div>
            <label for="reg-password" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">
              Buat Password <span class="text-red-600">*</span>
            </label>
            <div class="relative">
              <input
                id="reg-password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                minlength="6"
                placeholder="••••••••"
                :disabled="loading"
                class="auth-input px-3.5 pr-10"
                @keyup="checkCapsLock"
                @keydown="checkCapsLock"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black p-1 transition-colors"
                :aria-label="showPassword ? 'Sembunyikan password' : 'Tampilkan password'"
                @click="showPassword = !showPassword"
              >
                <UIcon :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
              </button>
            </div>
            <!-- Live password rules -->
            <ul v-if="form.password.length > 0" class="mt-2 space-y-1 text-[11px] font-medium">
              <li class="flex items-center gap-1.5" :class="form.password.length >= 6 ? 'text-green-700' : 'text-gray-400'">
                <UIcon :name="form.password.length >= 6 ? 'i-heroicons-check-circle-solid' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" />
                Minimal 6 karakter
              </li>
              <li class="flex items-center gap-1.5" :class="hasNumber ? 'text-green-700' : 'text-gray-400'">
                <UIcon :name="hasNumber ? 'i-heroicons-check-circle-solid' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" />
                Mengandung angka
              </li>
            </ul>
            <span v-if="isCapsLockOn" class="inline-flex items-center gap-1 mt-1.5 text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-3 h-3" /> Caps Lock Aktif
            </span>
          </div>

          <!-- Konfirmasi Password with toggle -->
          <div>
            <label for="reg-confirm" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">
              Konfirmasi Password <span class="text-red-600">*</span>
            </label>
            <div class="relative">
              <input
                id="reg-confirm"
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                placeholder="••••••••"
                :disabled="loading"
                class="auth-input px-3.5 pr-10"
                @keyup="checkCapsLock"
                @keydown="checkCapsLock"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black p-1 transition-colors"
                :aria-label="showConfirmPassword ? 'Sembunyikan password' : 'Tampilkan password'"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <UIcon :name="showConfirmPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
              </button>
            </div>
            <p v-if="passwordMismatch" class="text-xs text-red-600 mt-1 font-bold">✗ Password tidak cocok!</p>
            <p v-else-if="form.confirmPassword.length > 0 && !passwordMismatch" class="text-xs text-green-700 mt-1 font-semibold flex items-center gap-1">
              <UIcon name="i-heroicons-check-circle-solid" class="w-3.5 h-3.5" /> Password cocok
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading || passwordMismatch || !form.username || !form.email || !form.password || !!emailError"
            class="auth-btn-primary w-full mt-2"
            :aria-busy="loading"
          >
            <UIcon
              v-if="loading"
              name="i-heroicons-arrow-path"
              class="w-4 h-4 animate-spin mr-2 inline"
              aria-hidden="true"
            />
            <span>{{ loading ? "Memproses..." : "Daftar & Lanjutkan" }}</span>
            <UIcon
              v-if="!loading"
              name="i-heroicons-arrow-right"
              class="w-4 h-4 ml-1.5 inline"
              aria-hidden="true"
            />
          </button>
        </form>

        <!-- STEP 1: Profil & Lokasi -->
        <form v-if="currentStep === 1" @submit.prevent="handleProfileUpdate" class="space-y-4" novalidate>
          <div>
            <label for="profile-usertype" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">
              Tipe Akun
            </label>
            <select id="profile-usertype" v-model="profile.user_type" class="auth-input px-3.5">
              <option value="biasa">Personal (Perorangan)</option>
              <option value="corporate">Corporate (Perusahaan / Instansi / Proyek)</option>
            </select>
          </div>

          <div>
            <label for="profile-wa" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">
              Nomor WhatsApp (Aktif)
            </label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-black font-black text-xs">+62</span>
              <input
                id="profile-wa"
                v-model="profile.nomertlp"
                type="tel"
                placeholder="812xxxxx"
                maxlength="15"
                class="auth-input pl-12 pr-3.5"
                @input="formatPhone"
              />
            </div>
          </div>

          <div>
            <label for="profile-prov" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">Provinsi</label>
            <select id="profile-prov" v-model="profile.provinsi" class="auth-input px-3.5" @change="onProvinceChange">
              <option value="" disabled selected>Pilih Provinsi</option>
              <option v-for="prov in provinces" :key="prov.id" :value="prov.name">{{ prov.name }}</option>
            </select>
          </div>

          <div>
            <label for="profile-kab" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">Kota / Kabupaten</label>
            <select id="profile-kab" v-model="profile.kabupaten" class="auth-input px-3.5" :disabled="!selectedProvinceId" @change="onRegencyChange">
              <option value="" disabled selected>Pilih Kabupaten</option>
              <option v-for="reg in regencies" :key="reg.id" :value="reg.name">{{ reg.name }}</option>
            </select>
          </div>

          <div>
            <label for="profile-kec" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">Kecamatan</label>
            <select id="profile-kec" v-model="profile.kecamatan" class="auth-input px-3.5" :disabled="!selectedRegencyId">
              <option value="" disabled selected>Pilih Kecamatan</option>
              <option v-for="dist in districts" :key="dist.id" :value="dist.name">{{ dist.name }}</option>
            </select>
          </div>

          <div>
            <label for="profile-alamat" class="block text-[11px] font-black uppercase tracking-wider text-black mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">Alamat Lengkap (Jalan / No. Rumah)</label>
            <textarea id="profile-alamat" v-model="profile.alamat" placeholder="Contoh: Jl. Sudirman No. 123, Blok A..." class="auth-input !h-auto min-h-[80px] py-2.5 px-3.5 resize-none" />
          </div>

          <div class="flex gap-2.5 pt-2">
            <button type="button" class="flex-1 border border-gray-300 text-black h-[42px] rounded-md text-xs font-black uppercase tracking-wider hover:bg-gray-100 transition-colors font-['Plus_Jakarta_Sans',sans-serif]" @click="skipToLogin">Lewati</button>
            <button type="submit" :disabled="loadingProfile" class="flex-1 auth-btn-primary" :aria-busy="loadingProfile">
              <UIcon v-if="loadingProfile" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin mr-1.5" />
              <span>{{ loadingProfile ? "Menyimpan..." : "Simpan & Lanjut" }}</span>
            </button>
          </div>
        </form>
      </template>

      <!-- Footer -->
      <template #footer-links>
        <p class="text-xs font-bold text-gray-500 uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif] mb-3">
          Sudah memiliki akun?
          <NuxtLink to="/login" class="text-black font-black hover:text-red-600 transition-colors ml-1 border-b border-black hover:border-red-600 pb-0.5">Login Sistem</NuxtLink>
        </p>
        <div class="pt-3 border-t border-gray-100 flex flex-wrap items-center justify-center gap-3 text-xs text-gray-500 font-medium">
          <NuxtLink to="/help" class="hover:text-[#03AC0E] transition-colors flex items-center gap-1">
            <UIcon name="i-heroicons-question-mark-circle" class="w-3.5 h-3.5" />
            <span>Pusat Bantuan</span>
          </NuxtLink>
          <span>•</span>
          <a href="https://wa.me/6282218828108?text=Halo%20PasarCCTV,%20saya%20butuh%20bantuan%20pendaftaran%20akun." target="_blank" rel="noopener" class="hover:text-[#03AC0E] transition-colors flex items-center gap-1">
            <UIcon name="i-heroicons-chat-bubble-left-right" class="w-3.5 h-3.5" />
            <span>Bantuan Daftar via WA</span>
          </a>
        </div>
      </template>
    </AmazonAuthCard>
  </div>
</template>

<script setup lang="ts">
import AmazonAuthCard from "~/components/auth/AmazonAuthCard.vue";
import AmazonAlertError from "~/components/auth/AmazonAlertError.vue";
import { ref, computed, onMounted } from "vue";
import axios from "axios";

useHead({
  title: "Daftar Akun — PasarCctv",
  meta: [{ name: "description", content: "Daftar akun PasarCctv untuk kemudahan belanja produk keamanan, pengadaan proyek, dan jasa instalasi bergaransi resmi." }],
});

const config = useRuntimeConfig();
const BASE_URL = (config.public.apiBase as string) || "http://127.0.0.1:8000";

const currentStep = ref(0);
const form = ref({ username: "", email: "", password: "", confirmPassword: "" });
const profile = ref({ user_type: "biasa", nomertlp: "", alamat: "", provinsi: "", kabupaten: "", kecamatan: "" });
const accessToken = ref("");
const loading = ref(false);
const loadingProfile = ref(false);
const errorMsg = ref("");
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const isCapsLockOn = ref(false);
const emailError = ref("");

const checkCapsLock = (e: KeyboardEvent) => {
  isCapsLockOn.value = e.getModifierState("CapsLock");
};

const validateEmail = () => {
  const val = form.value.email.trim();
  if (!val) { emailError.value = ""; return; }
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  emailError.value = re.test(val) ? "" : "Format email tidak valid.";
};

const hasNumber = computed(() => /\d/.test(form.value.password));

interface WilayahItem { id: string; name: string; }
const provinces = ref<WilayahItem[]>([]);
const regencies = ref<WilayahItem[]>([]);
const districts = ref<WilayahItem[]>([]);
const selectedProvinceId = ref("");
const selectedRegencyId = ref("");

const passwordMismatch = computed(() => form.value.password !== form.value.confirmPassword && form.value.confirmPassword.length > 0);

const formatPhone = () => {
  let val = profile.value.nomertlp.replace(/\D/g, "");
  if (val.startsWith("62")) val = val.substring(2);
  if (val.startsWith("0")) val = val.substring(1);
  profile.value.nomertlp = val;
};

const fetchProvinces = async () => {
  try {
    const res = await axios.get<WilayahItem[]>("https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json");
    provinces.value = res.data;
  } catch (err) { console.error("Gagal mengambil data provinsi", err); }
};

const onProvinceChange = async () => {
  profile.value.kabupaten = ""; profile.value.kecamatan = ""; regencies.value = []; districts.value = []; selectedProvinceId.value = ""; selectedRegencyId.value = "";
  const prov = provinces.value.find((p) => p.name === profile.value.provinsi);
  if (!prov) return; selectedProvinceId.value = prov.id;
  try { const res = await axios.get<WilayahItem[]>(`https://www.emsifa.com/api-wilayah-indonesia/api/regencies/${prov.id}.json`); regencies.value = res.data; } catch (err) { console.error("Gagal mengambil data kabupaten", err); }
};

const onRegencyChange = async () => {
  profile.value.kecamatan = ""; districts.value = []; selectedRegencyId.value = "";
  const reg = regencies.value.find((r) => r.name === profile.value.kabupaten);
  if (!reg) return; selectedRegencyId.value = reg.id;
  try { const res = await axios.get<WilayahItem[]>(`https://www.emsifa.com/api-wilayah-indonesia/api/districts/${reg.id}.json`); districts.value = res.data; } catch (err) { console.error("Gagal mengambil data kecamatan", err); }
};

onMounted(() => { fetchProvinces(); });

const handleRegister = async () => {
  validateEmail();
  if (emailError.value) return;
  errorMsg.value = "";
  if (passwordMismatch.value) return;
  loading.value = true;
  try {
    await axios.post(`${BASE_URL}/auth/user/auth/register`, { username: form.value.username, email: form.value.email, password: form.value.password });
    const loginRes = await axios.post(`${BASE_URL}/auth/user/auth/login`, { email: form.value.email, password: form.value.password });
    accessToken.value = loginRes.data.access_token;
    currentStep.value = 1;
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err: any) {
    const detail = err.response?.data?.detail;
    if (Array.isArray(detail)) errorMsg.value = detail.map((d: any) => d.msg).join(", ");
    else if (typeof detail === "string") errorMsg.value = detail;
    else errorMsg.value = "Pendaftaran akun gagal. Silakan periksa data Anda.";
  } finally { loading.value = false; }
};

const handleProfileUpdate = async () => {
  errorMsg.value = ""; loadingProfile.value = true;
  const payload: Record<string, string> = {};
  if (profile.value.nomertlp) payload.nomertlp = profile.value.nomertlp;
  if (profile.value.alamat) payload.alamat = profile.value.alamat;
  if (profile.value.provinsi) payload.provinsi = profile.value.provinsi;
  if (profile.value.kabupaten) payload.kabupaten = profile.value.kabupaten;
  if (profile.value.kecamatan) payload.kecamatan = profile.value.kecamatan;
  try {
    if (Object.keys(payload).length > 0) await axios.patch(`${BASE_URL}/auth/user/users/me`, payload, { headers: { Authorization: `Bearer ${accessToken.value}` } });
    navigateTo("/login?registered=1");
  } catch (err: any) {
    const detail = err.response?.data?.detail;
    errorMsg.value = typeof detail === "string" ? detail : "Gagal memperbarui profil.";
  } finally { loadingProfile.value = false; }
};

const skipToLogin = () => navigateTo("/login?registered=1");
</script>

<style scoped>
/* Scoped styles now use global design tokens from main.css via .auth-input and .auth-btn-primary classes */
</style>