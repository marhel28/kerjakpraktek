<script setup lang="ts">
import { useUserStore } from "~/stores/user";
import { ref, onMounted, reactive, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

definePageMeta({ layout: "auth" });

const route = useRoute();
const router = useRouter();
const { logout } = useAuth();

const userStore = useUserStore();
const config = useRuntimeConfig();

const handleLogout = async () => {
  if (confirm("Apakah Anda yakin ingin keluar?")) {
    await logout();
  }
};

const isEditing = ref(false);
const isSaving = ref(false);

const form = reactive({
  username: "",
  email: "",
  nomertlp: "",
  alamat: "",
  provinsi: "",
  kabupaten: "",
  kecamatan: "",
  gender: "Laki-laki",
  birthdate: "",
});

const syncForm = () => {
  if (userStore.profile) {
    Object.assign(form, {
      username: userStore.profile.username || "",
      email: userStore.profile.email || "",
      nomertlp: userStore.profile.nomertlp || "",
      alamat: userStore.profile.alamat || "",
      provinsi: userStore.profile.provinsi || "",
      kabupaten: userStore.profile.kabupaten || "",
      kecamatan: userStore.profile.kecamatan || "",
      gender: (userStore.profile as any).gender || "Laki-laki",
      birthdate: (userStore.profile as any).birthdate || "",
    });
  }
};

onMounted(async () => {
  if (!userStore.profile) await userStore.fetchProfile();
  syncForm();
});

const userAvatar = computed(() => {
  const name = userStore.profile?.username || "Pengguna";
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=03AC0E&color=ffffff&bold=true`;
});

// ─── Indonesia Region API Logic (Hierarchical) ─────────────
const provinces = ref<any[]>([]);
const cities = ref<any[]>([]);
const districts = ref<any[]>([]);

const isLoadingRegions = reactive({
  provinces: false,
  cities: false,
  districts: false,
});

const fetchProvinces = async () => {
  isLoadingRegions.provinces = true;
  try {
    const res: any = await $fetch("https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json");
    provinces.value = res;
  } catch (err) {
    console.error("Gagal memuat provinsi:", err);
  } finally {
    isLoadingRegions.provinces = false;
  }
};

const fetchCities = async (provinceId: string) => {
  if (!provinceId) return;
  isLoadingRegions.cities = true;
  cities.value = [];
  districts.value = [];
  try {
    const res: any = await $fetch(`https://www.emsifa.com/api-wilayah-indonesia/api/regencies/${provinceId}.json`);
    cities.value = res;
  } catch (err) {
    console.error("Gagal memuat kota:", err);
  } finally {
    isLoadingRegions.cities = false;
  }
};

const fetchDistricts = async (cityId: string) => {
  if (!cityId) return;
  isLoadingRegions.districts = true;
  districts.value = [];
  try {
    const res: any = await $fetch(`https://www.emsifa.com/api-wilayah-indonesia/api/districts/${cityId}.json`);
    districts.value = res;
  } catch (err) {
    console.error("Gagal memuat kecamatan:", err);
  } finally {
    isLoadingRegions.districts = false;
  }
};

// State untuk ID seleksi (untuk API hierarchical)
const selectedIds = reactive({
  province: "",
  city: "",
  district: "",
});

// Watcher untuk sinkronisasi form string dengan ID API
watch(() => selectedIds.province, (newId) => {
  const p = provinces.value.find(x => x.id === newId);
  if (p) {
    form.provinsi = p.name;
    fetchCities(newId);
  }
});

watch(() => selectedIds.city, (newId) => {
  const c = cities.value.find(x => x.id === newId);
  if (c) {
    form.kabupaten = c.name;
    fetchDistricts(newId);
  }
});

watch(() => selectedIds.district, (newId) => {
  const d = districts.value.find(x => x.id === newId);
  if (d) {
    form.kecamatan = d.name;
  }
});

const handleSave = async () => {
  isSaving.value = true;
  const payload = {
    username: form.username,
    nomertlp: form.nomertlp,
    alamat: form.alamat,
    provinsi: form.provinsi,
    kabupaten: form.kabupaten,
    kecamatan: form.kecamatan,
  };
  
  const success = await userStore.updateProfile(payload);
  if (success) {
    alert("Profil berhasil diperbarui!");
    isEditing.value = false;
  }
  isSaving.value = false;
};

// Trigger fetch awal saat edit dinyalakan
watch(isEditing, (newVal) => {
  if (newVal && provinces.value.length === 0) {
    fetchProvinces();
  }
});

// Tabs Pengaturan Akun (Standar Tokopedia)
const tabs = [
  { label: "Biodata Diri", to: "/dashboard" },
  { label: "Daftar Alamat", to: "/dashboard/address" },
  { label: "Keamanan Akun", to: "/dashboard/change-password" },
  { label: "Notifikasi", to: "/dashboard/notifications" },
];
</script>

<template>
  <div class="min-h-screen bg-white font-sans">
    
    <!-- ══════════════════════════════════════════════════════════════════
         1. MOBILE OVERVIEW MENU (Only visible on mobile when view !== 'profile')
         ══════════════════════════════════════════════════════════════════ -->
    <div v-if="!$route.query.view" class="lg:hidden bg-gray-50/50 min-h-screen pb-12">
      <!-- Profile Card Banner -->
      <div class="bg-gradient-to-r from-[#03AC0E] to-[#028c0b] px-5 pt-7 pb-14 text-white relative rounded-b-2xl shadow-sm">
        <div class="flex items-center gap-3.5">
          <NuxtImg
            :src="userAvatar"
            class="w-14 h-14 rounded-full border-2 border-white/60 object-cover shadow-sm shrink-0"
            alt="Profile"
          />
          <div class="min-w-0 flex-1">
            <h2 class="text-base font-bold tracking-tight truncate flex items-center gap-1.5">
              {{ userStore.profile?.username || 'Pengguna' }}
              <UIcon name="i-heroicons-check-badge" class="w-4 h-4 text-emerald-200 shrink-0" />
            </h2>
            <p class="text-xs text-emerald-100 font-medium truncate mt-0.5">{{ userStore.profile?.email }}</p>
            <span class="inline-block mt-1 px-2 py-0.5 bg-white/20 text-[10px] font-semibold rounded-full">
              Member Reguler
            </span>
          </div>
        </div>
      </div>

      <div class="px-4 -mt-8 space-y-3.5 relative z-10">
        
        <!-- Dompet & Kupon Box (Tokopedia Style) -->
        <div class="bg-white rounded-xl border border-gray-200/80 shadow-sm p-3.5 divide-y divide-gray-100">
          <div class="flex items-center justify-between pb-2.5">
            <div class="flex items-center gap-2.5">
              <div class="w-7 h-7 rounded-lg bg-emerald-50 text-[#03AC0E] flex items-center justify-center">
                <UIcon name="i-heroicons-wallet" class="w-4 h-4" />
              </div>
              <div>
                <p class="text-[10px] text-gray-500 font-medium">Saldo PasarCctv</p>
                <p class="text-xs font-bold text-gray-900">Rp 0</p>
              </div>
            </div>
            <button class="text-[11px] font-bold text-[#03AC0E]">Top Up</button>
          </div>

          <div class="pt-2.5 grid grid-cols-2 gap-2">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                <UIcon name="i-heroicons-circle-stack" class="w-3.5 h-3.5" />
              </div>
              <div>
                <p class="text-[10px] text-gray-400 font-medium">Koin Reward</p>
                <p class="text-[11px] font-bold text-gray-800">0 Koin</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-lg bg-rose-50 text-rose-500 flex items-center justify-center">
                <UIcon name="i-heroicons-ticket" class="w-3.5 h-3.5" />
              </div>
              <div>
                <p class="text-[10px] text-gray-400 font-medium">Kupon Saya</p>
                <p class="text-[11px] font-bold text-[#03AC0E]">2 Kupon</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Membership Card -->
        <div class="bg-gradient-to-r from-emerald-500/10 via-emerald-50 to-teal-50 rounded-xl border border-emerald-200/70 p-3 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-emerald-100/80 flex items-center justify-center text-[#03AC0E]">
              <UIcon name="i-heroicons-sparkles" class="w-4 h-4" />
            </div>
            <div>
              <h4 class="text-xs font-bold text-emerald-950">PasarCctv Plus</h4>
              <p class="text-[10px] text-emerald-700 font-medium">Bebas Ongkir & Prioritas Servis</p>
            </div>
          </div>
          <span class="px-2 py-0.5 bg-emerald-600 text-white text-[10px] font-bold rounded">Aktif</span>
        </div>

        <!-- Transaksi Saya (Grid 3 Kolom Tokopedia) -->
        <div class="bg-white rounded-xl border border-gray-200/80 shadow-sm p-3.5">
          <h3 class="text-xs font-bold text-gray-900 mb-3">Aktivitas & Transaksi</h3>
          <div class="grid grid-cols-3 gap-2 text-center">
            <NuxtLink to="/dashboard/orders" class="p-2.5 rounded-lg hover:bg-gray-50 active:scale-95 transition-all">
              <div class="w-9 h-9 rounded-full bg-emerald-50 text-[#03AC0E] flex items-center justify-center mx-auto mb-1.5">
                <UIcon name="i-heroicons-shopping-bag" class="w-4 h-4" />
              </div>
              <span class="text-[11px] font-medium text-gray-800">Pesanan</span>
            </NuxtLink>
            <NuxtLink to="/dashboard/jasa" class="p-2.5 rounded-lg hover:bg-gray-50 active:scale-95 transition-all">
              <div class="w-9 h-9 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-1.5">
                <UIcon name="i-heroicons-wrench-screwdriver" class="w-4 h-4" />
              </div>
              <span class="text-[11px] font-medium text-gray-800">Jasa Servis</span>
            </NuxtLink>
            <NuxtLink to="/dashboard/wishlist" class="p-2.5 rounded-lg hover:bg-gray-50 active:scale-95 transition-all">
              <div class="w-9 h-9 rounded-full bg-rose-50 text-rose-500 flex items-center justify-center mx-auto mb-1.5">
                <UIcon name="i-heroicons-heart" class="w-4 h-4" />
              </div>
              <span class="text-[11px] font-medium text-gray-800">Wishlist</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Menu List (Kotak Masuk & Pengaturan Akun) -->
        <div class="bg-white rounded-xl border border-gray-200/80 shadow-sm overflow-hidden divide-y divide-gray-100">
          <!-- Chat -->
          <NuxtLink to="/dashboard/chat" class="flex items-center justify-between p-3.5 hover:bg-gray-50 transition-colors group">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center">
                <UIcon name="i-heroicons-chat-bubble-left-right" class="w-4 h-4" />
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-900">Chat & Bantuan</p>
                <p class="text-[10px] text-gray-400">Hubungi Customer Service</p>
              </div>
            </div>
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-300 group-hover:text-gray-600 transition-colors" />
          </NuxtLink>

          <!-- Biodata Diri (Toggles local view) -->
          <button @click="router.push('/dashboard?view=profile')" class="w-full flex items-center justify-between p-3.5 hover:bg-gray-50 transition-colors group text-left">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-emerald-50 text-[#03AC0E] flex items-center justify-center">
                <UIcon name="i-heroicons-user" class="w-4 h-4" />
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-900">Biodata Diri</p>
                <p class="text-[10px] text-gray-400">Ubah nama, email, nomor HP</p>
              </div>
            </div>
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-300 group-hover:text-gray-600 transition-colors" />
          </button>

          <!-- Daftar Alamat -->
          <NuxtLink to="/dashboard/address" class="flex items-center justify-between p-3.5 hover:bg-gray-50 transition-colors group">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                <UIcon name="i-heroicons-map-pin" class="w-4 h-4" />
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-900">Daftar Alamat</p>
                <p class="text-[10px] text-gray-400">Atur alamat pengiriman belanja</p>
              </div>
            </div>
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-300 group-hover:text-gray-600 transition-colors" />
          </NuxtLink>

          <!-- Keamanan Akun -->
          <NuxtLink to="/dashboard/change-password" class="flex items-center justify-between p-3.5 hover:bg-gray-50 transition-colors group">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                <UIcon name="i-heroicons-shield-check" class="w-4 h-4" />
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-900">Keamanan Akun</p>
                <p class="text-[10px] text-gray-400">Ganti password & proteksi akun</p>
              </div>
            </div>
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-300 group-hover:text-gray-600 transition-colors" />
          </NuxtLink>

          <!-- Notifikasi -->
          <NuxtLink to="/dashboard/notifications" class="flex items-center justify-between p-3.5 hover:bg-gray-50 transition-colors group">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
                <UIcon name="i-heroicons-bell" class="w-4 h-4" />
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-900">Notifikasi</p>
                <p class="text-[10px] text-gray-400">Info promo & pesanan</p>
              </div>
            </div>
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-300 group-hover:text-gray-600 transition-colors" />
          </NuxtLink>
        </div>

        <!-- Logout Button -->
        <button
          @click="handleLogout"
          class="w-full py-3 bg-white hover:bg-red-50 border border-red-200 text-red-600 font-bold text-xs rounded-xl shadow-sm transition-all flex items-center justify-center gap-2"
        >
          <UIcon name="i-heroicons-arrow-left-on-rectangle" class="w-4 h-4" />
          Keluar Dari Akun
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════════
         2. DESKTOP & MOBILE PROFILE FORM (Tokopedia Layout)
         ══════════════════════════════════════════════════════════════════ -->
    <div :class="[!$route.query.view ? 'hidden lg:block' : 'block']">
      
      <!-- MOBILE HEADER (Mobile only back navigation) -->
      <div class="lg:hidden flex items-center gap-3 px-4 py-3.5 border-b border-gray-200 bg-white sticky top-0 z-20">
        <button @click="router.push('/dashboard')" class="p-1 -ml-1 text-gray-500 hover:text-gray-900 transition-colors">
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        </button>
        <h1 class="text-sm font-bold text-gray-900">Biodata Diri</h1>
      </div>

      <!-- DESKTOP TABS (Tokopedia Account Settings Tabs) -->
      <div class="hidden lg:block border-b border-gray-200 bg-white">
        <div class="flex px-6">
          <NuxtLink
            v-for="tab in tabs"
            :key="tab.to"
            :to="tab.to"
            class="px-5 py-3.5 text-sm font-semibold whitespace-nowrap transition-colors relative"
            :class="[
              $route.path === tab.to 
                ? 'text-[#03AC0E]' 
                : 'text-gray-500 hover:text-gray-800'
            ]"
          >
            {{ tab.label }}
            <div v-if="$route.path === tab.to" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#03AC0E]"></div>
          </NuxtLink>
        </div>
      </div>

      <!-- MAIN PROFILE CONTAINER -->
      <div class="p-4 sm:p-6 lg:p-8">
        <div class="flex flex-col lg:flex-row gap-6 lg:gap-8 items-start">
          
          <!-- ── KOLOM KIRI: Foto Profil & Keamanan (Tokopedia Style) ── -->
          <div class="w-full lg:w-72 shrink-0 space-y-4">
            <!-- Box Foto Profil -->
            <div class="bg-white border border-gray-200/80 rounded-xl p-5 text-center shadow-sm">
              <div class="relative w-32 h-32 mx-auto rounded-full ring-4 ring-emerald-500/10 overflow-hidden mb-4 group bg-gray-50">
                <NuxtImg
                  :src="userAvatar"
                  class="w-full h-full object-cover"
                  alt="Avatar"
                />
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center text-white cursor-pointer">
                  <UIcon name="i-heroicons-camera" class="w-6 h-6 mb-1" />
                  <span class="text-[10px] font-medium">Ubah Foto</span>
                </div>
              </div>

              <button class="w-full py-2 px-3 bg-white border border-gray-300 hover:border-[#03AC0E] text-gray-700 hover:text-[#03AC0E] text-xs font-bold rounded-lg transition-colors shadow-sm">
                Pilih Foto
              </button>

              <p class="mt-3 text-[11px] text-gray-400 leading-relaxed text-center">
                Besar file: maks. 10.000.000 bytes (10 Megabytes). Format gambar: .JPG .JPEG .PNG .WEBP
              </p>
            </div>

            <!-- Box Keamanan Cepat (Tokopedia Security Card) -->
            <div class="bg-white border border-gray-200/80 rounded-xl p-4 shadow-sm space-y-3">
              <div class="flex items-center gap-2 text-gray-900 font-bold text-xs">
                <UIcon name="i-heroicons-shield-check" class="w-4 h-4 text-[#03AC0E]" />
                Keamanan & Proteksi
              </div>

              <NuxtLink
                to="/dashboard/change-password"
                class="w-full py-2 px-3 bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 text-xs font-semibold rounded-lg transition-colors flex items-center justify-between group"
              >
                <span>Ubah Kata Sandi</span>
                <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5 text-gray-400 group-hover:text-gray-700" />
              </NuxtLink>

              <div class="pt-2 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-500">
                <span>Status Akun</span>
                <span class="text-[#03AC0E] font-semibold flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#03AC0E]"></span>
                  Terlindungi
                </span>
              </div>
            </div>
          </div>

          <!-- ── KOLOM KANAN: Biodata Diri (Tokopedia Form / View) ── -->
          <div class="flex-1 w-full bg-white border border-gray-200/80 rounded-xl p-5 sm:p-7 shadow-sm">
            
            <!-- Header Kartu -->
            <div class="flex items-center justify-between pb-5 border-b border-gray-100">
              <div>
                <h2 class="text-base font-bold text-gray-900">Ubah Biodata Diri</h2>
                <p class="text-xs text-gray-500 mt-0.5">Kelola informasi profil Anda untuk kenyamanan bertransaksi.</p>
              </div>

              <button
                @click="isEditing = !isEditing"
                class="px-4 py-1.5 text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5"
                :class="isEditing ? 'bg-gray-100 hover:bg-gray-200 text-gray-700' : 'bg-emerald-50 hover:bg-emerald-100 text-[#03AC0E] border border-emerald-200/60'"
              >
                <UIcon :name="isEditing ? 'i-heroicons-x-mark' : 'i-heroicons-pencil'" class="w-3.5 h-3.5" />
                {{ isEditing ? 'Batal' : 'Ubah Profil' }}
              </button>
            </div>

            <!-- ── VIEW MODE (Saat Tidak Diedit) ── -->
            <div v-if="!isEditing" class="py-6 space-y-6 divide-y divide-gray-100">
              
              <!-- Bagian 1: Biodata Diri -->
              <div class="space-y-4">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider">Biodata Pribadi</h3>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 items-center">
                  <span class="text-xs text-gray-500">Nama Lengkap</span>
                  <div class="sm:col-span-2 flex items-center justify-between">
                    <span class="text-xs sm:text-sm font-semibold text-gray-900">{{ form.username || '-' }}</span>
                    <button @click="isEditing = true" class="text-xs text-[#03AC0E] font-medium hover:underline">Ubah</button>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 items-center">
                  <span class="text-xs text-gray-500">Tanggal Lahir</span>
                  <div class="sm:col-span-2 flex items-center justify-between">
                    <span class="text-xs sm:text-sm font-medium text-gray-800">{{ form.birthdate || 'Belum diatur' }}</span>
                    <button @click="isEditing = true" class="text-xs text-[#03AC0E] font-medium hover:underline">
                      {{ form.birthdate ? 'Ubah' : 'Tambah Tanggal Lahir' }}
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 items-center">
                  <span class="text-xs text-gray-500">Jenis Kelamin</span>
                  <div class="sm:col-span-2 flex items-center justify-between">
                    <span class="text-xs sm:text-sm font-medium text-gray-800">{{ form.gender || 'Laki-laki' }}</span>
                    <button @click="isEditing = true" class="text-xs text-[#03AC0E] font-medium hover:underline">Ubah</button>
                  </div>
                </div>
              </div>

              <!-- Bagian 2: Kontak -->
              <div class="pt-5 space-y-4">
                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider">Kontak & Verifikasi</h3>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 items-center">
                  <span class="text-xs text-gray-500">Email</span>
                  <div class="sm:col-span-2 flex items-center gap-2">
                    <span class="text-xs sm:text-sm font-semibold text-gray-900">{{ form.email }}</span>
                    <span class="px-2 py-0.5 bg-emerald-50 text-[#03AC0E] text-[10px] font-bold rounded border border-emerald-200/60">
                      Terverifikasi
                    </span>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 items-center">
                  <span class="text-xs text-gray-500">Nomor HP</span>
                  <div class="sm:col-span-2 flex items-center justify-between">
                    <span class="text-xs sm:text-sm font-semibold text-gray-900">{{ form.nomertlp || 'Belum ditambahkan' }}</span>
                    <button @click="isEditing = true" class="text-xs text-[#03AC0E] font-medium hover:underline">
                      {{ form.nomertlp ? 'Ubah' : 'Tambah Nomor HP' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Bagian 3: Alamat Utama -->
              <div class="pt-5 space-y-4">
                <div class="flex items-center justify-between">
                  <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider">Alamat Pengiriman Utama</h3>
                  <NuxtLink to="/dashboard/address" class="text-xs text-[#03AC0E] font-semibold hover:underline">
                    Kelola di Daftar Alamat &rarr;
                  </NuxtLink>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 items-start">
                  <span class="text-xs text-gray-500 pt-0.5">Wilayah</span>
                  <div class="sm:col-span-2">
                    <p class="text-xs sm:text-sm font-semibold text-gray-900">
                      {{ form.kabupaten ? `${form.kecamatan ? form.kecamatan + ', ' : ''}${form.kabupaten}, ${form.provinsi}` : 'Belum diatur' }}
                    </p>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 items-start">
                  <span class="text-xs text-gray-500 pt-0.5">Alamat Lengkap</span>
                  <div class="sm:col-span-2">
                    <p class="text-xs sm:text-sm text-gray-700 leading-relaxed">
                      {{ form.alamat || 'Belum ada alamat pengiriman lengkap tersimpan.' }}
                    </p>
                  </div>
                </div>
              </div>

            </div>

            <!-- ── EDIT MODE (Form Pengisian) ── -->
            <div v-else class="py-6 space-y-5">
              
              <!-- Input Nama -->
              <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-4 items-center">
                <label class="text-xs font-semibold text-gray-700">Nama Lengkap</label>
                <div class="sm:col-span-3">
                  <input
                    v-model="form.username"
                    type="text"
                    placeholder="Masukkan nama lengkap"
                    class="w-full bg-white border border-gray-300 rounded-lg px-3.5 py-2 text-xs sm:text-sm text-gray-900 focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none transition-all"
                  />
                </div>
              </div>

              <!-- Input Tanggal Lahir -->
              <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-4 items-center">
                <label class="text-xs font-semibold text-gray-700">Tanggal Lahir</label>
                <div class="sm:col-span-3">
                  <input
                    v-model="form.birthdate"
                    type="date"
                    class="w-full sm:w-64 bg-white border border-gray-300 rounded-lg px-3.5 py-2 text-xs sm:text-sm text-gray-900 focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none transition-all"
                  />
                </div>
              </div>

              <!-- Pilihan Jenis Kelamin -->
              <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-4 items-center">
                <label class="text-xs font-semibold text-gray-700">Jenis Kelamin</label>
                <div class="sm:col-span-3 flex items-center gap-6">
                  <label class="flex items-center gap-2 cursor-pointer text-xs font-medium text-gray-800">
                    <input type="radio" v-model="form.gender" value="Laki-laki" class="accent-[#03AC0E]" />
                    Laki-laki
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer text-xs font-medium text-gray-800">
                    <input type="radio" v-model="form.gender" value="Perempuan" class="accent-[#03AC0E]" />
                    Perempuan
                  </label>
                </div>
              </div>

              <!-- Input Nomor HP -->
              <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-4 items-center">
                <label class="text-xs font-semibold text-gray-700">Nomor HP</label>
                <div class="sm:col-span-3">
                  <input
                    v-model="form.nomertlp"
                    type="tel"
                    placeholder="Contoh: 081234567890"
                    class="w-full sm:w-80 bg-white border border-gray-300 rounded-lg px-3.5 py-2 text-xs sm:text-sm text-gray-900 focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none transition-all"
                  />
                </div>
              </div>

              <!-- Dropdown Wilayah Bertingkat -->
              <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-4 items-start">
                <label class="text-xs font-semibold text-gray-700 pt-2">Wilayah</label>
                <div class="sm:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                  <select
                    v-model="selectedIds.province"
                    class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-xs text-gray-800 focus:border-[#03AC0E] outline-none"
                  >
                    <option value="" disabled>{{ isLoadingRegions.provinces ? 'Memuat...' : 'Pilih Provinsi' }}</option>
                    <option v-for="p in provinces" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>

                  <select
                    v-model="selectedIds.city"
                    :disabled="!selectedIds.province"
                    class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-xs text-gray-800 focus:border-[#03AC0E] outline-none disabled:bg-gray-50 disabled:text-gray-400"
                  >
                    <option value="" disabled>{{ isLoadingRegions.cities ? 'Memuat...' : 'Pilih Kota/Kabupaten' }}</option>
                    <option v-for="c in cities" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>

                  <select
                    v-model="selectedIds.district"
                    :disabled="!selectedIds.city"
                    class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-xs text-gray-800 focus:border-[#03AC0E] outline-none disabled:bg-gray-50 disabled:text-gray-400"
                  >
                    <option value="" disabled>{{ isLoadingRegions.districts ? 'Memuat...' : 'Pilih Kecamatan' }}</option>
                    <option v-for="d in districts" :key="d.id" :value="d.id">{{ d.name }}</option>
                  </select>
                </div>
              </div>

              <!-- Input Alamat Lengkap -->
              <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-4 items-start">
                <label class="text-xs font-semibold text-gray-700 pt-2">Alamat Lengkap</label>
                <div class="sm:col-span-3">
                  <textarea
                    v-model="form.alamat"
                    rows="3"
                    placeholder="Nama jalan, nomor rumah, RT/RW, patokan"
                    class="w-full bg-white border border-gray-300 rounded-lg px-3.5 py-2 text-xs sm:text-sm text-gray-900 focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none transition-all"
                  ></textarea>
                </div>
              </div>

              <!-- Action Bar Simpan -->
              <div class="pt-5 border-t border-gray-100 flex items-center justify-end gap-3">
                <button
                  @click="isEditing = false"
                  type="button"
                  class="px-5 py-2 text-xs font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Batal
                </button>
                <button
                  @click="handleSave"
                  :disabled="isSaving"
                  class="px-7 py-2 text-xs font-bold text-white bg-[#03AC0E] hover:bg-[#028c0b] rounded-lg shadow-sm transition-all flex items-center gap-2"
                >
                  <UIcon v-if="isSaving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  {{ isSaving ? 'Menyimpan...' : 'Simpan Biodata' }}
                </button>
              </div>

            </div>

          </div>

        </div>
      </div>
    </div>
  </div>
</template>
