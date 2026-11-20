<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useUserStore } from "~/stores/user";

definePageMeta({ layout: "auth" });
const config = useRuntimeConfig();
const userStore = useUserStore();
const API_BASE = `${config.public.apiBase}/cek/shipping`;
const toast = useToast();

const addresses = ref<any[]>([]);
const isLoading = ref(true);
const isModalOpen = ref(false);
const isSaving = ref(false);
const isSearching = ref(false);
const isDeleting = ref<string | null>(null);

const searchQuery = ref("");
const searchResults = ref<any[]>([]);
let searchTimeout: ReturnType<typeof setTimeout> | null = null;

const form = reactive({ 
  id: "", 
  location_id: "", 
  zip_code: "", 
  full_address: "", 
  province: "", 
  city: "", 
  district: "", 
  subdistrict: "", 
  label: "", 
  is_default: false 
});

const tabs = [
  { label: "Biodata Diri", to: "/dashboard" },
  { label: "Daftar Alamat", to: "/dashboard/address" },
  { label: "Keamanan Akun", to: "/dashboard/change-password" },
  { label: "Notifikasi", to: "/dashboard/notifications" },
];

const getToken = () => useCookie("token").value;

const fetchAddresses = async () => {
  isLoading.value = true;
  try {
    const response: any = await $fetch(`${API_BASE}/address`, { 
      method: "GET", 
      headers: { Authorization: `Bearer ${getToken()}` } 
    });
    addresses.value = response.data || [];
  } catch (err) { 
    console.error("Gagal mengambil alamat:", err); 
  } finally { 
    isLoading.value = false; 
  }
};

const handleSearchLocation = (e: Event) => {
  const query = (e.target as HTMLInputElement).value;
  searchQuery.value = query;
  if (query.length < 3) { searchResults.value = []; return; }
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(async () => {
    isSearching.value = true;
    try {
      const response: any = await $fetch(`${API_BASE}/lokasi`, { 
        method: "GET", 
        query: { q: query, limit: 10 }, 
        headers: { Authorization: `Bearer ${getToken()}` } 
      });
      searchResults.value = response.data || [];
    } catch (err) { 
      searchResults.value = []; 
    } finally { 
      isSearching.value = false; 
    }
  }, 400);
};

const selectLocation = (loc: any) => {
  Object.assign(form, { 
    location_id: loc.id.toString(), 
    zip_code: loc.zip, 
    label: loc.label, 
    province: loc.province, 
    city: loc.city, 
    district: loc.district, 
    subdistrict: loc.subdistrict 
  });
  searchQuery.value = loc.label; 
  searchResults.value = [];
};

const saveAddress = async () => {
  if (!form.location_id) return;
  isSaving.value = true;
  try {
    const method = form.id ? "PUT" : "POST";
    const url = form.id ? `${API_BASE}/address/${form.id}` : `${API_BASE}/address`;
    await $fetch(url, { 
      method, 
      headers: { Authorization: `Bearer ${getToken()}` }, 
      body: { ...form, id: undefined } 
    });
    isModalOpen.value = false; 
    await fetchAddresses();
    toast.add({ title: "Berhasil", description: form.id ? "Alamat berhasil diperbarui." : "Alamat baru berhasil ditambahkan.", color: "success" });
  } catch (err) { 
    toast.add({ title: "Gagal Menyimpan", description: "Gagal menyimpan alamat. Silakan coba lagi.", color: "error" }); 
  } finally { 
    isSaving.value = false; 
  }
};

const deleteTargetId = ref<string | null>(null);

const requestDeleteAddress = (id: string) => {
  deleteTargetId.value = id;
};

const deleteAddress = async () => {
  const id = deleteTargetId.value;
  if (!id) return;
  deleteTargetId.value = null;
  isDeleting.value = id;
  try {
    await $fetch(`${API_BASE}/address/${id}`, { 
      method: "DELETE", 
      headers: { Authorization: `Bearer ${getToken()}` } 
    });
    await fetchAddresses();
    toast.add({ title: "Berhasil Dihapus", description: "Alamat berhasil dihapus.", color: "success" });
  } catch (err) { 
    toast.add({ title: "Gagal Menghapus", description: "Gagal menghapus alamat.", color: "error" });  
  } finally { 
    isDeleting.value = null; 
  }
};

const setAsDefault = async (address: any) => {
  if (address.is_default) return;
  try {
    await $fetch(`${API_BASE}/address/${address.uuid || address.id}`, { 
      method: "PUT", 
      headers: { Authorization: `Bearer ${getToken()}` }, 
      body: { ...address, is_default: true } 
    });
    await fetchAddresses();
  } catch (err) { 
    console.error(err); 
  }
};

const openAddModal = () => {
  Object.assign(form, { 
    id: "", 
    location_id: "", 
    zip_code: "", 
    full_address: "", 
    province: "", 
    city: "", 
    district: "", 
    subdistrict: "", 
    label: "", 
    is_default: addresses.value.length === 0 
  });
  searchQuery.value = ""; 
  searchResults.value = []; 
  isModalOpen.value = true;
};

const openEditModal = (address: any) => {
  Object.assign(form, { 
    id: address.uuid || address.id, 
    location_id: address.location_id, 
    zip_code: address.zip_code, 
    full_address: address.full_address, 
    province: address.province || "", 
    city: address.city || "", 
    district: address.district || "", 
    subdistrict: address.subdistrict || "", 
    label: address.label || "", 
    is_default: address.is_default 
  });
  searchQuery.value = form.label; 
  isModalOpen.value = true;
};

onMounted(async () => {
  if (!userStore.profile) await userStore.fetchProfile();
  await fetchAddresses();
});
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- MOBILE HEADER -->
    <div class="lg:hidden flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-white sticky top-0 z-10">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/dashboard')" class="p-1 -ml-1 text-gray-400 hover:text-gray-900 transition-colors">
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        </button>
        <h1 class="text-base font-bold text-gray-900">Daftar Alamat</h1>
      </div>
      <button @click="openAddModal" class="p-2 bg-[#03AC0E]/10 text-[#03AC0E] active:bg-[#03AC0E]/20 rounded-lg transition-all flex items-center justify-center">
        <UIcon name="i-heroicons-plus" class="w-5 h-5" />
      </button>
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
      <!-- Desktop Title Area (Hidden on Mobile) -->
      <div class="hidden lg:flex flex-col sm:flex-row sm:items-center justify-between gap-6 mb-8">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Daftar Alamat</h2>
          <p class="text-xs text-gray-400 mt-1 uppercase tracking-widest font-bold">Kelola tujuan pengiriman Anda</p>
        </div>
        <button @click="openAddModal" class="px-6 py-3 bg-[#03AC0E] text-white text-sm font-bold rounded-lg hover:bg-[#028a0b] transition-all flex items-center justify-center gap-2 shadow-sm">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Tambah Alamat Baru
        </button>
      </div>

      <!-- ADDRESS LIST -->
      <div class="space-y-4">
        <div v-if="isLoading" class="space-y-4">
          <div v-for="i in 3" :key="i" class="h-32 bg-gray-50 rounded-xl animate-pulse"></div>
        </div>

        <DashboardEmptyState
          v-else-if="!addresses.length"
          icon="i-heroicons-map-pin"
          title="Belum Ada Alamat"
          description="Tambahkan alamat pengiriman utama untuk mempercepat proses checkout pesanan Anda."
          cta-label="Tambah Alamat Baru"
          @cta="openAddModal"
        />

        <div v-else class="space-y-4">
          <div v-for="addr in addresses" :key="addr.uuid || addr.id" 
            class="bg-white border rounded-xl p-4 sm:p-6 transition-all"
            :class="addr.is_default ? 'border-[#03AC0E] bg-emerald-50/10' : 'border-gray-200'"
          >
            <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4 sm:gap-6">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-sm font-bold text-gray-900 uppercase tracking-tight">{{ addr.label || 'Alamat' }}</h3>
                  <span v-if="addr.is_default" class="px-2 py-0.5 bg-emerald-50 text-emerald-600 text-[10px] font-bold rounded border border-emerald-100 uppercase tracking-widest">Utama</span>
                </div>
                <p class="text-sm font-bold text-gray-900 mb-1">{{ userStore.profile?.username || 'Penerima' }}</p>
                <p class="text-xs text-gray-500 leading-relaxed max-w-2xl">{{ addr.full_address }}</p>
                <p class="text-xs font-bold text-gray-400 mt-2 uppercase tracking-widest">{{ addr.city }}, {{ addr.zip_code }}</p>
              </div>

              <div class="flex items-center gap-6 pt-4 lg:pt-0 lg:border-l lg:pl-8 border-gray-100 justify-end sm:justify-start">
                <button @click="openEditModal(addr)" class="text-sm font-bold text-[#03AC0E] hover:underline">Ubah</button>
                <button v-if="!addr.is_default" @click="setAsDefault(addr)" class="text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">Pilih Utama</button>
                <button v-if="!addr.is_default" @click="requestDeleteAddress(addr.uuid || addr.id)" class="text-gray-300 hover:text-red-600 transition-colors">
                  <UIcon name="i-heroicons-trash" class="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL FORM -->
    <Teleport to="body">
      <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="isModalOpen = false"></div>
        <div class="relative w-full max-w-lg bg-white rounded-xl shadow-2xl overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-base font-bold text-gray-900">{{ form.id ? 'Ubah Alamat' : 'Tambah Alamat Baru' }}</h2>
            <button @click="isModalOpen = false" class="text-gray-400 hover:text-gray-900">
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
            </button>
          </div>

          <div class="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
            <div class="space-y-2">
              <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Cari Lokasi (Kota/Kecamatan)</label>
              <div class="relative">
                <input v-model="searchQuery" @input="handleSearchLocation" type="text" placeholder="Masukkan minimal 3 karakter"
                  class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-[#03AC0E] text-sm font-medium outline-none transition-all"
                />
                <div v-if="searchResults.length > 0" class="absolute left-0 right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl z-50 max-h-48 overflow-y-auto">
                  <button v-for="res in searchResults" :key="res.id" @click="selectLocation(res)"
                    class="w-full text-left px-4 py-3 hover:bg-gray-50 transition-all border-b border-gray-50 last:border-0">
                    <p class="text-xs font-bold text-gray-900 uppercase tracking-tight">{{ res.label }}</p>
                    <p class="text-[9px] text-gray-400 mt-0.5">ZIP: {{ res.zip }}</p>
                  </button>
                </div>
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Alamat Lengkap</label>
              <textarea v-model="form.full_address" rows="3" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-[#03AC0E] text-sm font-medium outline-none transition-all resize-none" placeholder="Nama Jalan, No. Rumah, RT/RW"></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Label Alamat</label>
                <input v-model="form.label" type="text" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-[#03AC0E] text-sm font-medium outline-none transition-all" placeholder="Rumah/Kantor" />
              </div>
              <div class="space-y-2">
                <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Kode Pos</label>
                <input v-model="form.zip_code" readonly type="text" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm font-medium outline-none" />
              </div>
            </div>

            <label class="flex items-center gap-3 cursor-pointer group">
              <input type="checkbox" v-model="form.is_default" class="w-4 h-4 rounded text-[#03AC0E] focus:ring-[#03AC0E] border-gray-300" />
              <span class="text-xs font-bold text-gray-600 group-hover:text-gray-900 transition-colors">Jadikan Alamat Utama</span>
            </label>
          </div>

          <div class="p-6 bg-gray-50 border-t border-gray-100 flex justify-end gap-3">
            <button @click="isModalOpen = false" class="px-6 py-2.5 text-xs font-bold text-gray-500 hover:text-gray-900 transition-colors">Batal</button>
            <button @click="saveAddress" :disabled="isSaving || !form.location_id" class="px-10 py-2.5 bg-[#03AC0E] text-white text-xs font-black rounded-lg hover:bg-[#028a0b] disabled:opacity-50 transition-all flex items-center gap-2 shadow-sm">
              <UIcon v-if="isSaving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              Simpan Alamat
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- MODAL KONFIRMASI HAPUS -->
    <Teleport to="body">
      <div v-if="deleteTargetId" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="deleteTargetId = null"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden p-6 flex flex-col items-center text-center z-10 border border-gray-100">
          <div class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center text-red-600 mb-4 ring-8 ring-red-50/50">
            <UIcon name="i-heroicons-trash" class="w-8 h-8" />
          </div>
          <h3 class="text-base font-bold text-gray-900 mb-2">Hapus Alamat?</h3>
          <p class="text-xs text-gray-500 mb-6 leading-relaxed">Alamat yang dihapus tidak dapat dikembalikan.</p>
          <div class="flex gap-3 w-full">
            <button @click="deleteTargetId = null" class="flex-1 py-3 text-xs font-bold text-gray-500 bg-gray-50 border border-gray-200 rounded-xl hover:bg-gray-100 transition-all">Batal</button>
            <button @click="deleteAddress" class="flex-1 py-3 text-xs font-black text-white bg-red-600 rounded-xl hover:bg-red-700 transition-all shadow-lg shadow-red-600/20">Ya, Hapus</button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
