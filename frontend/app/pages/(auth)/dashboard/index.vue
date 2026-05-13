<script setup lang="ts">
import { useUserStore } from "~/stores/user";
import { ref, onMounted, reactive, computed, watch } from "vue";

definePageMeta({ layout: "auth" });

const userStore = useUserStore();
const config = useRuntimeConfig();
const API_ONGKIR = `${config.public.apiBase}/ongkir`;

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

const tabs = [
  { label: "Biodata Diri", to: "/dashboard" },
  { label: "Daftar Alamat", to: "/dashboard/address" },
  { label: "Keamanan", to: "/dashboard/change-password" },
  { label: "Notifikasi", to: "/dashboard/notifications" },
  { label: "Pesanan Saya", to: "/dashboard/orders" },
  { label: "Layanan Jasa", to: "/dashboard/jasa" },
];
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- TABS -->
    <div class="border-b border-gray-200 overflow-x-auto no-scrollbar">
      <div class="flex px-8">
        <NuxtLink
          v-for="tab in tabs"
          :key="tab.to"
          :to="tab.to"
          class="px-6 py-4 text-sm font-black whitespace-nowrap transition-colors relative"
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
    <div class="p-6 sm:p-10">
      <div class="flex flex-col lg:flex-row gap-8">
        
        <!-- SIDEBAR PHOTO -->
        <div class="w-full lg:w-64 shrink-0">
          <div class="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <div class="aspect-square rounded-xl overflow-hidden bg-gray-50 flex items-center justify-center mb-5 border border-gray-100 relative group">
              <NuxtImg :src="userAvatar" class="w-full h-full object-cover" alt="Profile" />
              <div class="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
                <UIcon name="i-heroicons-camera" class="w-8 h-8 text-white" />
              </div>
            </div>
            <button class="w-full py-2 bg-white border border-gray-200 text-[#03AC0E] text-[11px] font-black rounded-lg hover:border-[#03AC0E] transition-all uppercase tracking-widest">
              Pilih Foto
            </button>
            <p class="mt-4 text-[9px] text-gray-400 font-bold text-center uppercase tracking-tight">
              Format: JPG, PNG, JPEG. Max 10MB.
            </p>
          </div>
        </div>

        <!-- MAIN FORM -->
        <div class="flex-1 max-w-4xl">
          <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            <div class="p-6 sm:p-8">
              
              <!-- HEADER -->
              <div class="flex items-center justify-between mb-8 pb-6 border-b border-gray-100">
                <div>
                  <h3 class="text-base font-black text-gray-900 uppercase tracking-widest">Biodata Diri</h3>
                  <p class="text-[10px] text-gray-400 font-bold mt-1">Lengkapi informasi akun Anda untuk kemudahan transaksi.</p>
                </div>
                <button 
                  @click="isEditing = !isEditing"
                  class="px-4 py-1.5 text-[11px] font-black rounded-lg transition-all uppercase tracking-widest"
                  :class="isEditing ? 'bg-gray-100 text-gray-500' : 'bg-[#03AC0E]/10 text-[#03AC0E] hover:bg-[#03AC0E]/20'"
                >
                  {{ isEditing ? 'Batal' : 'Edit Profil' }}
                </button>
              </div>

              <!-- FIELDS -->
              <div class="space-y-8">
                
                <!-- NAMA -->
                <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-8 items-center">
                  <label class="text-[11px] font-black text-gray-400 uppercase tracking-widest">Nama Lengkap</label>
                  <div class="sm:col-span-3">
                    <input 
                      v-if="isEditing" 
                      v-model="form.username" 
                      type="text"
                      class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm font-bold text-black focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none"
                    />
                    <p v-else class="text-sm font-black text-gray-900">{{ form.username || '-' }}</p>
                  </div>
                </div>

                <!-- EMAIL (READONLY) -->
                <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-8 items-center">
                  <label class="text-[11px] font-black text-gray-400 uppercase tracking-widest">Email</label>
                  <div class="sm:col-span-3 flex items-center gap-3">
                    <span class="text-sm font-black text-gray-900">{{ form.email }}</span>
                    <span class="px-2 py-0.5 bg-emerald-50 text-[#03AC0E] text-[9px] font-black rounded border border-emerald-100 uppercase tracking-widest">Terverifikasi</span>
                  </div>
                </div>

                <!-- NOMOR HP -->
                <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-8 items-center">
                  <label class="text-[11px] font-black text-gray-400 uppercase tracking-widest">Nomor HP</label>
                  <div class="sm:col-span-3">
                    <input 
                      v-if="isEditing" 
                      v-model="form.nomertlp" 
                      type="text"
                      class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm font-bold text-black focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none"
                    />
                    <p v-else class="text-sm font-black text-gray-900">{{ form.nomertlp || '-' }}</p>
                  </div>
                </div>

                <!-- WILAYAH -->
                <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-8 items-start">
                  <label class="text-[11px] font-black text-gray-400 uppercase tracking-widest pt-2">Wilayah</label>
                  <div class="sm:col-span-3">
                    <div v-if="isEditing" class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <select v-model="selectedIds.province" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-xs font-bold text-black focus:border-[#03AC0E] outline-none">
                        <option value="" disabled>{{ isLoadingRegions.provinces ? 'Memuat...' : 'Pilih Provinsi' }}</option>
                        <option v-for="p in provinces" :key="p.id" :value="p.id">{{ p.name }}</option>
                      </select>
                      <select v-model="selectedIds.city" :disabled="!selectedIds.province" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-xs font-bold text-black focus:border-[#03AC0E] outline-none disabled:opacity-50">
                        <option value="" disabled>{{ isLoadingRegions.cities ? 'Memuat...' : 'Pilih Kota' }}</option>
                        <option v-for="c in cities" :key="c.id" :value="c.id">{{ c.name }}</option>
                      </select>
                      <select v-model="selectedIds.district" :disabled="!selectedIds.city" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-xs font-bold text-black focus:border-[#03AC0E] outline-none disabled:opacity-50">
                        <option value="" disabled>{{ isLoadingRegions.districts ? 'Memuat...' : 'Pilih Kecamatan' }}</option>
                        <option v-for="d in districts" :key="d.id" :value="d.id">{{ d.name }}</option>
                      </select>
                    </div>
                    <div v-else>
                      <p class="text-sm font-black text-gray-900">{{ form.kabupaten || '-' }}</p>
                      <p class="text-[11px] text-gray-400 font-bold uppercase tracking-widest mt-1">{{ form.kecamatan }} • {{ form.provinsi }}</p>
                    </div>
                  </div>
                </div>

                <!-- ALAMAT -->
                <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-8 items-start">
                  <label class="text-[11px] font-black text-gray-400 uppercase tracking-widest pt-2">Alamat Lengkap</label>
                  <div class="sm:col-span-3">
                    <textarea 
                      v-if="isEditing" 
                      v-model="form.alamat" 
                      rows="3"
                      class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm font-bold text-black focus:border-[#03AC0E] focus:ring-1 focus:ring-[#03AC0E] outline-none"
                    ></textarea>
                    <p v-else class="text-sm font-bold text-gray-600 leading-relaxed">{{ form.alamat || '-' }}</p>
                  </div>
                </div>

                <!-- SAVE BUTTON -->
                <div v-if="isEditing" class="pt-6 border-t border-gray-100 flex justify-end">
                  <button 
                    @click="handleSave" 
                    :disabled="isSaving"
                    class="px-10 py-2.5 bg-[#03AC0E] text-white text-[11px] font-black rounded-lg hover:bg-[#028a0b] transition-all uppercase tracking-widest shadow-lg shadow-emerald-100 flex items-center gap-2"
                  >
                    <UIcon v-if="isSaving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                    Simpan Perubahan
                  </button>
                </div>

              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
