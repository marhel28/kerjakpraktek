<template>
  <div
    class="min-h-[100dvh] sm:min-h-screen flex items-center justify-center bg-white sm:bg-gray-50 sm:py-12 sm:px-4 font-sans selection:bg-black selection:text-white"
  >
    <div
      class="w-full h-[100dvh] sm:h-auto max-w-5xl sm:max-h-[95vh] bg-white sm:border border-gray-200 sm:shadow-xl sm:rounded-xl overflow-hidden flex flex-col lg:flex-row relative"
    >
      <div class="hidden lg:block lg:w-5/12 bg-black relative">
        <img
          src="https://static.jakmall.id/2023/12/images/products/e92af9/original/xiaomi-kamera-cctv-smart-google-home-alexa-360-rotation-full-hd-c200.png"
          alt="Padjajaran CCTV Security"
          class="w-full h-full object-cover opacity-50 mix-blend-luminosity grayscale"
        />
        <div
          class="absolute inset-0 bg-gradient-to-tr from-black via-black/60 to-transparent"
        ></div>

        <div class="absolute top-12 left-12">
          <div class="flex flex-col leading-none">
            <span class="text-3xl font-black text-white tracking-tighter uppercase italic"
              >Padjajaran</span
            >
            <span class="text-lg font-light text-gray-400 tracking-[0.3em] uppercase mt-1"
              >CCTV</span
            >
          </div>
        </div>

        <div class="absolute bottom-16 left-12 right-12 text-white">
          <div class="barcode-element-white mb-6"></div>
          <h1 class="text-4xl font-black uppercase tracking-tighter leading-[1.1] mb-5">
            Ekosistem <br />
            <span class="text-red-600">Keamanan</span> & <br />
            Layanan <span class="text-red-600">Teknis.</span>
          </h1>
          <p class="text-gray-400 text-sm font-medium leading-relaxed max-w-sm">
            Satu portal terpadu untuk pengadaan unit CCTV original, klaim garansi, dan
            pemesanan jasa teknisi ahli bersertifikat.
          </p>

          <div class="mt-8 flex flex-col gap-3">
            <div
              v-for="(step, i) in steps"
              :key="i"
              class="flex items-center gap-3 transition-opacity duration-300"
              :class="currentStep === i ? 'opacity-100' : 'opacity-40'"
            >
              <div
                class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black shrink-0 transition-colors"
                :class="
                  currentStep > i
                    ? 'bg-red-600 text-white'
                    : currentStep === i
                    ? 'bg-white text-black'
                    : 'border border-gray-600 text-gray-600'
                "
              >
                <template v-if="currentStep > i">✓</template>
                <template v-else>{{ i + 1 }}</template>
              </div>
              <span class="text-xs font-bold uppercase tracking-wider">{{ step }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="w-full lg:w-7/12 flex flex-col h-full overflow-hidden bg-white">
        <div
          class="lg:hidden sticky top-0 z-20 bg-white/85 backdrop-blur-md border-b border-gray-100 px-5 py-4 flex items-center justify-between shrink-0"
        >
          <div class="flex flex-col leading-none">
            <span class="text-xl font-black text-black tracking-tighter uppercase italic"
              >Padjajaran</span
            >
            <span
              class="text-[10px] font-light text-gray-500 tracking-[0.3em] uppercase mt-1"
              >CCTV</span
            >
          </div>
          <span
            class="text-[10px] font-black bg-black text-white px-2.5 py-1 rounded-sm tracking-widest"
          >
            {{ currentStep + 1 }}/{{ steps.length }}
          </span>
        </div>

        <div class="flex-1 overflow-y-auto px-5 py-8 sm:p-14 custom-scrollbar relative">
          <div class="absolute top-8 right-10 hidden sm:block">
            <div class="barcode-element-black"></div>
          </div>

          <div class="mb-8">
            <div class="flex items-center gap-3 mb-1">
              <h2
                class="text-2xl sm:text-3xl font-black text-black tracking-tight uppercase"
              >
                {{ currentStep === 0 ? "Buat Akun" : "Lengkapi Profil" }}
              </h2>
              <span
                class="hidden lg:inline-block text-[10px] font-black bg-black text-white px-2 py-1 tracking-widest"
              >
                {{ currentStep + 1 }}/{{ steps.length }}
              </span>
            </div>
            <p
              class="text-gray-500 text-[9px] sm:text-[10px] uppercase tracking-[0.3em] sm:tracking-[0.4em] font-black"
            >
              {{ currentStep === 0 ? "Data Akun Utama" : "Info Pengiriman & Tipe Akun" }}
            </p>
          </div>

          <form
            v-if="currentStep === 0"
            @submit.prevent="handleRegister"
            class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5"
          >
            <div
              v-if="errorMsg"
              class="md:col-span-2 bg-red-50 border border-red-200 p-4 rounded-lg sm:rounded-none"
            >
              <p class="text-red-700 text-xs font-black uppercase tracking-wider">
                ⚠ {{ errorMsg }}
              </p>
            </div>

            <div class="group md:col-span-2">
              <label class="custom-label"
                >Username <span class="text-red-600">*</span></label
              >
              <input
                type="text"
                placeholder="username_kamu"
                class="custom-input"
                v-model="form.username"
                minlength="3"
                maxlength="50"
                required
                autocomplete="username"
              />
              <p class="text-gray-400 text-[10px] mt-1.5 font-semibold">
                Min. 3 karakter, maks. 50 karakter.
              </p>
            </div>

            <div class="group md:col-span-2">
              <label class="custom-label"
                >Email Korespondensi <span class="text-red-600">*</span></label
              >
              <input
                type="email"
                placeholder="email@contoh.com"
                class="custom-input"
                v-model="form.email"
                required
                autocomplete="email"
              />
            </div>

            <div class="group">
              <label class="custom-label"
                >Buat Password <span class="text-red-600">*</span></label
              >
              <input
                type="password"
                placeholder="••••••••"
                class="custom-input"
                v-model="form.password"
                minlength="6"
                required
                autocomplete="new-password"
              />
              <p class="text-gray-400 text-[10px] mt-1.5 font-semibold">
                Min. 6 karakter.
              </p>
            </div>

            <div class="group">
              <label class="custom-label"
                >Konfirmasi Password <span class="text-red-600">*</span></label
              >
              <input
                type="password"
                placeholder="••••••••"
                class="custom-input"
                v-model="form.confirmPassword"
                required
                autocomplete="new-password"
              />
              <p
                v-if="passwordMismatch"
                class="text-red-600 text-[10px] mt-2 font-black uppercase tracking-widest"
              >
                ✗ Password tidak cocok!
              </p>
            </div>

            <div class="md:col-span-2 mt-4 sm:mt-6">
              <button
                type="submit"
                class="w-full bg-black text-white py-4 sm:py-4 rounded-xl sm:rounded-none text-xs font-black uppercase tracking-widest hover:bg-zinc-800 transition-colors flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
                :disabled="
                  loading ||
                  passwordMismatch ||
                  !form.username ||
                  !form.email ||
                  !form.password
                "
              >
                <Icon
                  v-if="loading"
                  name="lucide:loader-2"
                  class="w-5 h-5 animate-spin"
                />
                <template v-else>
                  Daftar & Lanjutkan
                  <Icon name="lucide:arrow-right" class="w-4 h-4" />
                </template>
              </button>
            </div>

            <div
              class="md:col-span-2 bg-gray-50 border border-gray-200 p-4 text-center rounded-lg sm:rounded-none"
            >
              <p
                class="text-gray-500 text-[10px] font-bold uppercase tracking-wider leading-relaxed"
              >
                Setelah daftar, Anda akan melengkapi info pengiriman & tipe akun.<br
                  class="hidden sm:block"
                />
                Cek email untuk verifikasi sebelum login.
              </p>
            </div>
          </form>

          <form
            v-if="currentStep === 1"
            @submit.prevent="handleProfileUpdate"
            class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5"
          >
            <div
              v-if="errorMsg"
              class="md:col-span-2 bg-red-50 border border-red-200 p-4 rounded-lg sm:rounded-none"
            >
              <p class="text-red-700 text-xs font-black uppercase tracking-wider">
                ⚠ {{ errorMsg }}
              </p>
            </div>

            <div
              class="md:col-span-2 bg-green-50 border border-green-300 p-4 rounded-lg sm:rounded-none"
            >
              <p
                class="text-green-800 text-[11px] font-black uppercase tracking-wider leading-relaxed"
              >
                ✓ Akun berhasil dibuat! Link verifikasi dikirim ke
                <span class="text-green-900 border-b border-green-900 pb-0.5">{{
                  form.email
                }}</span
                >. <br class="hidden sm:block" />Lengkapi profil Anda di bawah ini
                (opsional).
              </p>
            </div>

            <div class="md:col-span-2 group">
              <label class="custom-label">Tipe Akun</label>
              <select class="custom-select" v-model="profile.user_type">
                <option value="biasa">Personal (Perorangan)</option>
                <option value="corporate">
                  Corporate (Perusahaan / Instansi / Proyek)
                </option>
              </select>
            </div>

            <div class="group md:col-span-2">
              <label class="custom-label">Nomor WhatsApp (Aktif)</label>
              <div class="relative">
                <span
                  class="absolute left-4 top-1/2 -translate-y-1/2 text-black font-black text-sm"
                  >+62</span
                >
                <input
                  type="tel"
                  placeholder="812xxxxx"
                  class="custom-input pl-14"
                  v-model="profile.nomertlp"
                  @input="formatPhone"
                  maxlength="15"
                />
              </div>
            </div>

            <div class="md:col-span-2 mt-2 mb-1">
              <div class="flex items-center gap-4">
                <span
                  class="text-[10px] font-black text-black uppercase tracking-[0.2em] sm:tracking-[0.3em] whitespace-nowrap"
                  >Titik Lokasi Pengiriman</span
                >
                <div class="w-full h-[1px] bg-gray-200"></div>
              </div>
            </div>

            <div class="group">
              <label class="custom-label">Provinsi</label>
              <select
                class="custom-select"
                v-model="profile.provinsi"
                @change="onProvinceChange"
              >
                <option value="" disabled selected>Pilih Provinsi</option>
                <option v-for="prov in provinces" :key="prov.id" :value="prov.name">
                  {{ prov.name }}
                </option>
              </select>
            </div>

            <div class="group">
              <label class="custom-label">Kota / Kabupaten</label>
              <select
                class="custom-select"
                v-model="profile.kabupaten"
                @change="onRegencyChange"
                :disabled="!selectedProvinceId"
              >
                <option value="" disabled selected>Pilih Kabupaten</option>
                <option v-for="reg in regencies" :key="reg.id" :value="reg.name">
                  {{ reg.name }}
                </option>
              </select>
            </div>

            <div class="group md:col-span-2">
              <label class="custom-label">Kecamatan</label>
              <select
                class="custom-select"
                v-model="profile.kecamatan"
                :disabled="!selectedRegencyId"
              >
                <option value="" disabled selected>Pilih Kecamatan</option>
                <option v-for="dist in districts" :key="dist.id" :value="dist.name">
                  {{ dist.name }}
                </option>
              </select>
            </div>

            <div class="group md:col-span-2">
              <label class="custom-label"
                >Alamat Lengkap (Detail Jalan / No. Rumah)</label
              >
              <textarea
                placeholder="Contoh: Jl. Sudirman No. 123, Blok A..."
                class="custom-input min-h-[100px] py-4 resize-none"
                v-model="profile.alamat"
              ></textarea>
            </div>

            <div class="md:col-span-2 mt-4 flex flex-col-reverse sm:flex-row gap-3">
              <button
                type="button"
                class="flex-1 border border-gray-300 text-black py-4 rounded-xl sm:rounded-none text-xs font-black uppercase tracking-widest hover:bg-gray-50 transition-colors active:scale-[0.98]"
                @click="skipToLogin"
              >
                Lewati & Login
              </button>
              <button
                type="submit"
                class="flex-1 bg-black text-white py-4 rounded-xl sm:rounded-none text-xs font-black uppercase tracking-widest hover:bg-zinc-800 transition-colors flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
                :disabled="loadingProfile"
              >
                <Icon
                  v-if="loadingProfile"
                  name="lucide:loader-2"
                  class="w-5 h-5 animate-spin"
                />
                <template v-else>
                  Simpan & Login
                  <Icon name="lucide:arrow-right" class="w-4 h-4" />
                </template>
              </button>
            </div>
          </form>

          <p
            class="text-center text-gray-500 mt-10 text-[11px] font-bold uppercase tracking-wider pb-6 sm:pb-0"
          >
            Sudah memiliki akun?
            <NuxtLink
              to="/login"
              class="text-black font-black hover:text-red-600 transition-colors ml-1 border-b border-black hover:border-red-600 pb-0.5 inline-block mt-1 sm:mt-0"
            >
              Login Sistem
            </NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";

// ─── SEO ──────────────────────────────────────────────────────────
useHead({
  title: "Daftar Akun - Padjajaran CCTV",
  meta: [
    {
      name: "description",
      content:
        "Daftar akun Padjajaran CCTV untuk kemudahan belanja produk keamanan, pengadaan proyek, dan jasa instalasi.",
    },
  ],
});

// ─── State Wizard ─────────────────────────────────────────────────
const steps = ["Data Akun", "Profil & Lokasi"];
const currentStep = ref(0);

// ─── Step 1: Register (UserCreate) ────────────────────────────────
const form = ref({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
});

// ─── Step 2: Profile Update (UserProfileUpdate) ───────────────────
const profile = ref({
  user_type: "biasa",
  nomertlp: "",
  alamat: "",
  provinsi: "",
  kabupaten: "",
  kecamatan: "",
});

// ─── Auth State ───────────────────────────────────────────────────
const accessToken = ref("");

// ─── UI State ─────────────────────────────────────────────────────
const loading = ref(false);
const loadingProfile = ref(false);
const errorMsg = ref("");

// ─── Wilayah State ────────────────────────────────────────────────
const provinces = ref([]);
const regencies = ref([]);
const districts = ref([]);
const selectedProvinceId = ref("");
const selectedRegencyId = ref("");

// ─── Computed ─────────────────────────────────────────────────────
const passwordMismatch = computed(
  () =>
    form.value.password !== form.value.confirmPassword &&
    form.value.confirmPassword.length > 0
);

// ─── Phone Formatter ──────────────────────────────────────────────
const formatPhone = () => {
  let val = profile.value.nomertlp.replace(/\D/g, "");
  if (val.startsWith("62")) val = val.substring(2);
  if (val.startsWith("0")) val = val.substring(1);
  profile.value.nomertlp = val;
};

// ─── Wilayah API (Emsifa) ─────────────────────────────────────────
const fetchProvinces = async () => {
  try {
    const res = await axios.get(
      "https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json"
    );
    provinces.value = res.data;
  } catch (err) {
    console.error("Gagal mengambil provinsi", err);
  }
};

const onProvinceChange = async () => {
  profile.value.kabupaten = "";
  profile.value.kecamatan = "";
  regencies.value = [];
  districts.value = [];
  selectedProvinceId.value = "";
  selectedRegencyId.value = "";

  const prov = provinces.value.find((p) => p.name === profile.value.provinsi);
  if (!prov) return;
  selectedProvinceId.value = prov.id;

  try {
    const res = await axios.get(
      `https://www.emsifa.com/api-wilayah-indonesia/api/regencies/${prov.id}.json`
    );
    regencies.value = res.data;
  } catch (err) {
    console.error("Gagal mengambil kabupaten", err);
  }
};

const onRegencyChange = async () => {
  profile.value.kecamatan = "";
  districts.value = [];
  selectedRegencyId.value = "";

  const reg = regencies.value.find((r) => r.name === profile.value.kabupaten);
  if (!reg) return;
  selectedRegencyId.value = reg.id;

  try {
    const res = await axios.get(
      `https://www.emsifa.com/api-wilayah-indonesia/api/districts/${reg.id}.json`
    );
    districts.value = res.data;
  } catch (err) {
    console.error("Gagal mengambil kecamatan", err);
  }
};

onMounted(() => fetchProvinces());

// ─── STEP 1: Register → POST /auth/register ───────────────────────
const handleRegister = async () => {
  errorMsg.value = "";
  if (passwordMismatch.value) return;

  loading.value = true;
  try {
    await axios.post("/api/auth/register", {
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
    });

    const loginRes = await axios.post("/api/auth/login", {
      email: form.value.email,
      password: form.value.password,
    });
    accessToken.value = loginRes.data.access_token;

    currentStep.value = 1;
    // Scroll ke atas saat pindah step di mobile
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    const detail = err.response?.data?.detail;
    if (Array.isArray(detail)) {
      errorMsg.value = detail.map((d) => d.msg).join(", ");
    } else if (typeof detail === "string") {
      errorMsg.value = detail;
    } else {
      errorMsg.value = "Registrasi gagal. Coba lagi.";
    }
  } finally {
    loading.value = false;
  }
};

// ─── STEP 2: Update Profil → PATCH /users/me ──────────────────────
const handleProfileUpdate = async () => {
  errorMsg.value = "";
  loadingProfile.value = true;

  const payload = {};
  if (profile.value.nomertlp) payload.nomertlp = profile.value.nomertlp;
  if (profile.value.alamat) payload.alamat = profile.value.alamat;
  if (profile.value.provinsi) payload.provinsi = profile.value.provinsi;
  if (profile.value.kabupaten) payload.kabupaten = profile.value.kabupaten;
  if (profile.value.kecamatan) payload.kecamatan = profile.value.kecamatan;

  try {
    if (Object.keys(payload).length > 0) {
      await axios.patch("/api/users/me", payload, {
        headers: { Authorization: `Bearer ${accessToken.value}` },
      });
    }
    navigateTo("/login?registered=1");
  } catch (err) {
    const detail = err.response?.data?.detail;
    errorMsg.value = typeof detail === "string" ? detail : "Gagal menyimpan profil.";
  } finally {
    loadingProfile.value = false;
  }
};

// ─── Skip langsung ke Login ───────────────────────────────────────
const skipToLogin = () => navigateTo("/login?registered=1");
</script>

<style scoped>
.custom-label {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #000000;
  margin-bottom: 8px;
  display: block;
}

.custom-input,
.custom-select {
  width: 100%;
  padding: 14px 16px;
  background-color: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 12px; /* Lebih halus di mobile */
  font-size: 13px;
  font-weight: 600;
  color: #000000;
  transition: all 0.2s ease;
}

@media (min-width: 640px) {
  .custom-input,
  .custom-select {
    border-radius: 0; /* Kembali ke gaya edge kotak di desktop */
  }
}

.custom-input:focus,
.custom-select:focus {
  background-color: #ffffff;
  border-color: #000000;
  outline: none;
  box-shadow: 0 0 0 1px #000000;
}

.custom-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23000000' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 12px center;
  background-repeat: no-repeat;
  background-size: 1rem;
}

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

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background: #000000;
}
</style>
