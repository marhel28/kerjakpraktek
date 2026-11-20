<script setup lang="ts">
import { useUserStore } from "~/stores/user";
import { useWishlistStore } from "~/stores/wishlist";
import { useNotificationStore } from "~/stores/notificationStore";
import { useOrderStatus } from "~/composables/useOrderStatus";
import { usePesanStore } from "~/stores/UsePesanStore";
import { ref, onMounted, reactive, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

definePageMeta({ layout: "auth" });

const { getOrderStatus } = useOrderStatus();
const pesanStore = usePesanStore();

const route = useRoute();
const router = useRouter();
const { logout } = useAuth();
const userStore = useUserStore();
const wishlistStore = useWishlistStore();
const notifStore = useNotificationStore();
const config = useRuntimeConfig();
const toast = useToast();

const activeTab = ref<"overview" | "profile">("overview");

// ─── Metrics & Summary ───────────────────────────────────────────
const pendingOrdersCount = ref(0);
const activeBookingsCount = ref(0);
const recentOrders = ref<any[]>([]);
const isLoadingMetrics = ref(true);

// Computed: Pesanan aktif yang butuh action user (pending_payment, pending, processing, shipped)
const activeOrder = computed(() => {
  if (!recentOrders.value.length) return null;
  const activeStatuses = ["pending_payment", "pending", "processing", "shipped", "dispatched"];
  return recentOrders.value.find((o: any) => activeStatuses.includes(o.status?.toLowerCase())) || null;
});

// Computed: shortcut yang relevan jika tidak ada pesanan aktif
const fallbackShortcuts = [
  { label: "Lacak Pengiriman", to: "/dashboard/orders", icon: "i-heroicons-truck", color: "bg-blue-50 text-blue-600" },
  { label: "Jadwal Pasang CCTV", to: "/dashboard/jasa", icon: "i-heroicons-calendar-days", color: "bg-emerald-50 text-emerald-600" },
  { label: "Konsultasi Teknis", action: "chat", icon: "i-heroicons-chat-bubble-left-right", color: "bg-amber-50 text-amber-600" },
] as const;

const fetchDashboardData = async () => {
  isLoadingMetrics.value = true;
  try {
    const token = useCookie("token").value;
    if (!token) return;

    // Fetch transactions
    const txRes: any = await $fetch(`${config.public.apiBase}/transaksi/my/all`, {
      headers: { Authorization: `Bearer ${token}` },
      query: { limit: 5, sort: "desc" },
    }).catch(() => null);

    if (txRes?.success && Array.isArray(txRes.data)) {
      recentOrders.value = txRes.data;
      pendingOrdersCount.value = txRes.data.filter(
        (t: any) => t.status === "pending_payment" || t.status === "pending"
      ).length;
    }

    // Fetch service booking count
    const bookRes: any = await $fetch(`${config.public.apiBase}/user/booking/my`, {
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => null);

    if (bookRes?.success && Array.isArray(bookRes.data)) {
      activeBookingsCount.value = bookRes.data.filter(
        (b: any) => b.status !== "completed" && b.status !== "cancelled"
      ).length;
    }
  } catch (err) {
    // silent fail
  } finally {
    isLoadingMetrics.value = false;
  }
};

// ─── Profile Form Logic ──────────────────────────────────────────
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
  fetchDashboardData();
  if (wishlistStore.fetchWishlist) {
    wishlistStore.fetchWishlist();
  }
});

const userAvatar = computed(() => {
  const name = userStore.profile?.username || "Pengguna";
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=03AC0E&color=ffffff&bold=true`;
});

// ─── Region Logic (Indonesia) ────────────────────────────────────
const provinces = ref<any[]>([]);
const cities = ref<any[]>([]);
const districts = ref<any[]>([]);

const isLoadingRegions = reactive({
  provinces: false,
  cities: false,
  districts: false,
});

const selectedIds = reactive({
  province: "",
  city: "",
  district: "",
});

const fetchProvinces = async () => {
  isLoadingRegions.provinces = true;
  try {
    const res: any = await $fetch("https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json");
    provinces.value = res || [];
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
    cities.value = res || [];
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
    districts.value = res || [];
  } catch (err) {
    console.error("Gagal memuat kecamatan:", err);
  } finally {
    isLoadingRegions.districts = false;
  }
};

const onProvinceChange = async () => {
  const prov = provinces.value.find((p) => p.id === selectedIds.province);
  form.provinsi = prov ? prov.name : "";
  selectedIds.city = "";
  selectedIds.district = "";
  form.kabupaten = "";
  form.kecamatan = "";
  cities.value = [];
  districts.value = [];
  if (selectedIds.province) {
    await fetchCities(selectedIds.province);
  }
};

const onCityChange = async () => {
  const c = cities.value.find((item) => item.id === selectedIds.city);
  form.kabupaten = c ? c.name : "";
  selectedIds.district = "";
  form.kecamatan = "";
  districts.value = [];
  if (selectedIds.city) {
    await fetchDistricts(selectedIds.city);
  }
};

const onDistrictChange = () => {
  const d = districts.value.find((item) => item.id === selectedIds.district);
  form.kecamatan = d ? d.name : "";
};

const handleEditClick = async () => {
  isEditing.value = true;
  activeTab.value = "profile";
  if (provinces.value.length === 0) {
    await fetchProvinces();
  }
};

const handleCancel = () => {
  isEditing.value = false;
  syncForm();
};

const handleSaveProfile = async () => {
  isSaving.value = true;
  try {
    const token = useCookie("token").value;
    const res: any = await $fetch(`${config.public.apiBase}/user/profile`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: {
        username: form.username,
        nomertlp: form.nomertlp,
        alamat: form.alamat,
        provinsi: form.provinsi,
        kabupaten: form.kabupaten,
        kecamatan: form.kecamatan,
        gender: form.gender,
        birthdate: form.birthdate,
      },
    });

    if (res.success || res.status) {
      await userStore.fetchProfile();
      syncForm();
      isEditing.value = false;
      toast.add({
        title: "Berhasil Disimpan",
        description: "Data profil akun Anda berhasil diperbarui.",
        color: "success",
        icon: "i-heroicons-check-circle",
      });
    }
  } catch (err: any) {
    toast.add({
      title: "Gagal Menyimpan",
      description: err.data?.message || "Terjadi kendala saat memperbarui profil.",
      color: "error",
      icon: "i-heroicons-x-circle",
    });
  } finally {
    isSaving.value = false;
  }
};

function formatPrice(val: number) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(val || 0);
}
</script>

<template>
  <div class="font-['Plus_Jakarta_Sans',sans-serif] text-gray-900">
    <!-- Top Greeting Banner (Tokopedia Style) -->
    <div class="bg-gradient-to-r from-emerald-800 to-[#03AC0E] p-6 text-white rounded-t-xl relative overflow-hidden">
      <div class="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex items-center gap-3.5">
          <img
            :src="userAvatar"
            alt="Avatar"
            class="w-14 h-14 rounded-full border-2 border-white shadow-sm object-cover bg-white shrink-0"
          />
          <div>
            <div class="flex items-center gap-2">
              <h1 class="text-lg sm:text-xl font-black tracking-tight">
                Halo, {{ userStore.profile?.username || "Pelanggan PasarCCTV" }}!
              </h1>
              <span class="bg-white/20 text-[10px] uppercase tracking-wider font-extrabold px-2 py-0.5 rounded-full backdrop-blur-xs">
                Member Resmi
              </span>
            </div>
            <p class="text-xs text-emerald-100 mt-0.5 flex items-center gap-1.5">
              <UIcon name="i-heroicons-envelope" class="w-3.5 h-3.5" />
              {{ userStore.profile?.email || "Akun Terverifikasi" }}
            </p>
          </div>
        </div>

        <!-- Quick Switch Tab -->
        <div class="flex bg-black/20 p-1 rounded-xl backdrop-blur-xs text-xs font-bold w-full sm:w-auto">
          <button
            type="button"
            class="flex-1 sm:flex-none py-1.5 px-4 rounded-lg transition-all"
            :class="activeTab === 'overview' ? 'bg-white text-gray-900 shadow-xs' : 'text-white hover:bg-white/10'"
            @click="activeTab = 'overview'"
          >
            Ringkasan Akun
          </button>
          <button
            type="button"
            class="flex-1 sm:flex-none py-1.5 px-4 rounded-lg transition-all"
            :class="activeTab === 'profile' ? 'bg-white text-gray-900 shadow-xs' : 'text-white hover:bg-white/10'"
            @click="activeTab = 'profile'"
          >
            Biodata Diri
          </button>
        </div>
      </div>
    </div>

    <!-- ── 1. OVERVIEW TAB: Amazon Account Hub x Tokopedia Summary ── -->
    <div v-if="activeTab === 'overview'" class="p-6 space-y-8 bg-gray-50/50">
      <!-- 4 Core Metric Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
        <NuxtLink
          to="/dashboard/orders"
          class="bg-white p-4 rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all group cursor-pointer"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Menunggu Bayar</span>
            <div class="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <UIcon name="i-heroicons-clock" class="w-4 h-4" />
            </div>
          </div>
          <div class="text-xl sm:text-2xl font-bold text-gray-900">
            {{ pendingOrdersCount }}
          </div>
          <span class="text-[11px] text-[#03AC0E] font-bold group-hover:underline flex items-center gap-1 mt-1">
            Lihat Pesanan
            <UIcon name="i-heroicons-arrow-right" class="w-3 h-3" />
          </span>
        </NuxtLink>

        <NuxtLink
          to="/dashboard/jasa"
          class="bg-white p-4 rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all group cursor-pointer"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Jasa Teknisi</span>
            <div class="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <UIcon name="i-heroicons-wrench-screwdriver" class="w-4 h-4" />
            </div>
          </div>
          <div class="text-xl sm:text-2xl font-bold text-gray-900">
            {{ activeBookingsCount }}
          </div>
          <span class="text-[11px] text-[#03AC0E] font-bold group-hover:underline flex items-center gap-1 mt-1">
            Jadwal Pemasangan
            <UIcon name="i-heroicons-arrow-right" class="w-3 h-3" />
          </span>
        </NuxtLink>

        <NuxtLink
          to="/dashboard/wishlist"
          class="bg-white p-4 rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all group cursor-pointer"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Wishlist</span>
            <div class="w-8 h-8 rounded-xl bg-red-50 text-red-600 flex items-center justify-center">
              <UIcon name="i-heroicons-heart" class="w-4 h-4" />
            </div>
          </div>
          <div class="text-xl sm:text-2xl font-bold text-gray-900">
            {{ wishlistStore.count || 0 }}
          </div>
          <span class="text-[11px] text-[#03AC0E] font-bold group-hover:underline flex items-center gap-1 mt-1">
            Barang Disimpan
            <UIcon name="i-heroicons-arrow-right" class="w-3 h-3" />
          </span>
        </NuxtLink>

        <NuxtLink
          to="/dashboard/notifications"
          class="bg-white p-4 rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all group cursor-pointer"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Notifikasi</span>
            <div class="w-8 h-8 rounded-xl bg-emerald-50 text-[#03AC0E] flex items-center justify-center">
              <UIcon name="i-heroicons-bell" class="w-4 h-4" />
            </div>
          </div>
          <div class="text-xl sm:text-2xl font-bold text-gray-900">
            {{ notifStore.unreadCount || 0 }}
          </div>
          <span class="text-[11px] text-[#03AC0E] font-bold group-hover:underline flex items-center gap-1 mt-1">
            Lihat Pesan
            <UIcon name="i-heroicons-arrow-right" class="w-3 h-3" />
          </span>
        </NuxtLink>
      </div>

      <!-- Tracking Pesanan Aktif / Quick Shortcuts -->
      <div>
        <!-- Jika ada pesanan aktif: banner status + action -->
        <div
          v-if="activeOrder"
          class="bg-white rounded-2xl border border-gray-200 shadow-2xs overflow-hidden"
        >
          <div class="px-5 sm:px-6 py-4 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] text-white flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
                <UIcon name="i-heroicons-truck" class="w-5 h-5" />
              </div>
              <div>
                <p class="text-[11px] font-bold uppercase tracking-widest opacity-80">Pesanan Sedang Berjalan</p>
                <p class="text-sm font-bold tracking-tight">#{{ activeOrder.order_id }}</p>
              </div>
            </div>
            <span
              class="text-[10px] uppercase font-bold px-2.5 py-1 rounded-full border bg-white text-[#03AC0E] border-white"
            >
              {{ getOrderStatus(activeOrder.status, activeOrder.shipment?.delivery_status).label }}
            </span>
          </div>
          <div class="p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div class="space-y-1.5">
              <p class="text-sm text-gray-700 font-medium">Total Belanja: <span class="font-bold text-gray-900">{{ formatPrice(activeOrder.gross_amount) }}</span></p>
              <p class="text-xs text-gray-500 flex items-center gap-1.5">
                <UIcon name="i-heroicons-calendar" class="w-3.5 h-3.5" />
                {{ new Date(activeOrder.created_at || '').toLocaleDateString("id-ID", { day: "2-digit", month: "short", year: "numeric" }) }}
                <span v-if="activeOrder.shipment?.waybill_number" class="mx-1">•</span>
                <span v-if="activeOrder.shipment?.waybill_number" class="font-bold text-[#03AC0E]">Resi: {{ activeOrder.shipment.waybill_number }}</span>
              </p>
            </div>
            <div class="flex items-center gap-2">
              <NuxtLink
                :to="`/dashboard/orders/${activeOrder.order_id}`"
                class="px-5 py-2.5 bg-white border border-gray-200 text-gray-700 text-xs font-bold rounded-xl hover:bg-gray-50 transition-colors"
              >
                Lacak Pesanan
              </NuxtLink>
              <NuxtLink
                v-if="['pending_payment','pending'].includes((activeOrder.status||'').toLowerCase())"
                :to="`/payment/${activeOrder.order_id}`"
                class="px-5 py-2.5 bg-[#03AC0E] text-white text-xs font-bold rounded-xl hover:bg-[#028a0b] transition-colors shadow-sm"
              >
                Bayar Sekarang
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Jika tidak ada pesanan aktif: 3 shortcut minimal -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <NuxtLink
            v-for="sc in fallbackShortcuts"
            :key="sc.label"
            :to="(sc as any).to || undefined"
            :class="!(sc as any).to ? 'cursor-pointer' : ''"
            class="p-4 bg-white rounded-2xl border border-gray-200 shadow-2xs hover:border-[#03AC0E] hover:shadow-sm transition-all flex items-center gap-3.5 group"
            @click="(sc as any).action === 'chat' ? pesanStore.onPopupOpen() : undefined"
          >
            <div :class="['p-2.5 rounded-xl shrink-0 transition-colors', sc.color]">
              <UIcon :name="sc.icon" class="w-5 h-5" />
            </div>
            <span class="text-sm font-bold text-gray-900 group-hover:text-[#03AC0E] transition-colors">{{ sc.label }}</span>
          </NuxtLink>
        </div>
      </div>

      <!-- Pesanan Terbaru Ringkas -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5 sm:p-6 shadow-2xs space-y-4">
        <div class="flex items-center justify-between border-b border-gray-100 pb-3">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-receipt-percent" class="w-5 h-5 text-[#03AC0E]" />
            <h3 class="text-sm font-extrabold text-gray-900">
              Aktivitas Pesanan Terakhir
            </h3>
          </div>
          <NuxtLink to="/dashboard/orders" class="text-xs font-bold text-[#03AC0E] hover:underline flex items-center gap-1">
            Lihat Semua
            <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5" />
          </NuxtLink>
        </div>

        <div v-if="isLoadingMetrics" class="py-8 text-center text-xs text-gray-400 font-semibold">
          Memuat aktivitas pesanan...
        </div>

        <div v-else-if="!recentOrders.length" class="py-8 text-center space-y-2">
          <UIcon name="i-heroicons-inbox" class="w-8 h-8 text-gray-300 mx-auto" />
          <p class="text-xs text-gray-500 font-medium">Belum ada riwayat pesanan dalam akun ini.</p>
          <NuxtLink to="/search" class="inline-block text-xs font-bold text-[#03AC0E] hover:underline">
            Mulai Belanja Paket CCTV &rarr;
          </NuxtLink>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div
            v-for="order in recentOrders"
            :key="order.order_id"
            class="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5"
          >
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-gray-900">#{{ order.order_id }}</span>
                <span
                  class="text-[10px] uppercase font-bold px-2 py-0.5 rounded-md border"
                  :class="getOrderStatus(order.status, order.shipment?.delivery_status).badge"
                >
                  {{ getOrderStatus(order.status, order.shipment?.delivery_status).label }}
                </span>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                Total Belanja: <strong class="text-gray-900 font-bold">{{ formatPrice(order.gross_amount) }}</strong>
              </p>
            </div>
            <NuxtLink
              :to="`/dashboard/orders/${order.order_id}`"
              class="text-xs font-bold text-gray-700 hover:text-[#03AC0E] border border-gray-200 rounded-lg px-3 py-1.5 self-start sm:self-auto transition-colors"
            >
              Rincian
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <!-- ── 2. PROFILE TAB: Clean Tokopedia Identity Form ── -->
    <div v-else class="p-6 space-y-6">
      <div class="flex items-center justify-between border-b border-gray-100 pb-4">
        <div>
          <h2 class="text-base font-extrabold text-gray-900 tracking-tight">
            Biodata Diri Pengguna
          </h2>
          <p class="text-xs text-gray-500 mt-0.5">
            Informasi ini digunakan untuk pengiriman pesanan dan verifikasi garansi resmi.
          </p>
        </div>
        <button
          v-if="!isEditing"
          type="button"
          class="bg-[#03AC0E] hover:bg-[#028b0b] text-white text-xs font-bold py-2 px-4 rounded-xl shadow-xs active:scale-95 transition-all flex items-center gap-1.5"
          @click="handleEditClick"
        >
          <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
          Ubah Biodata
        </button>
      </div>

      <form @submit.prevent="handleSaveProfile" class="space-y-5">
        <!-- Readonly / Active Display -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          <div class="space-y-1.5">
            <label class="text-xs font-bold text-gray-600 uppercase tracking-wider">Nama Lengkap</label>
            <input
              v-model="form.username"
              type="text"
              :disabled="!isEditing"
              required
              class="w-full text-xs font-bold border border-gray-300 rounded-xl px-3.5 py-2.5 outline-none transition-colors disabled:bg-gray-50 disabled:text-gray-500 focus:border-[#03AC0E]"
            />
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-bold text-gray-600 uppercase tracking-wider">Email Akun</label>
            <input
              v-model="form.email"
              type="email"
              disabled
              class="w-full text-xs font-bold border border-gray-200 bg-gray-50 text-gray-400 rounded-xl px-3.5 py-2.5 outline-none cursor-not-allowed"
            />
            <span class="text-[10px] text-gray-400">Email akun tidak dapat diubah sembarangan demi keamanan.</span>
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-bold text-gray-600 uppercase tracking-wider">Nomor WhatsApp / HP</label>
            <input
              v-model="form.nomertlp"
              type="tel"
              :disabled="!isEditing"
              placeholder="08xxxxxxxxxx"
              class="w-full text-xs font-bold border border-gray-300 rounded-xl px-3.5 py-2.5 outline-none transition-colors disabled:bg-gray-50 disabled:text-gray-500 focus:border-[#03AC0E]"
            />
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-bold text-gray-600 uppercase tracking-wider">Jenis Kelamin</label>
            <select
              v-model="form.gender"
              :disabled="!isEditing"
              class="w-full text-xs font-bold border border-gray-300 rounded-xl px-3.5 py-2.5 outline-none transition-colors disabled:bg-gray-50 disabled:text-gray-500 focus:border-[#03AC0E]"
            >
              <option value="Laki-laki">Laki-laki</option>
              <option value="Perempuan">Perempuan</option>
            </select>
          </div>
        </div>

        <!-- Alamat Domisili -->
        <div class="pt-4 border-t border-gray-100 space-y-4">
          <h3 class="text-xs font-extrabold uppercase tracking-wider text-gray-700">
            Alamat & Wilayah Pengiriman Utama
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5 sm:gap-4">
            <!-- Provinsi -->
            <div class="space-y-1.5">
              <label class="text-xs font-bold text-gray-600">Provinsi</label>
              <select
                v-if="isEditing"
                v-model="selectedIds.province"
                class="w-full text-xs font-bold border border-gray-300 rounded-xl px-3 py-2.5 outline-none focus:border-[#03AC0E]"
                @change="onProvinceChange"
              >
                <option value="">-- Pilih Provinsi --</option>
                <option v-for="p in provinces" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
              <input
                v-else
                :value="form.provinsi || '-'"
                disabled
                class="w-full text-xs font-bold border border-gray-200 bg-gray-50 text-gray-600 rounded-xl px-3 py-2.5"
              />
            </div>

            <!-- Kota / Kab -->
            <div class="space-y-1.5">
              <label class="text-xs font-bold text-gray-600">Kota / Kabupaten</label>
              <select
                v-if="isEditing"
                v-model="selectedIds.city"
                :disabled="!cities.length"
                class="w-full text-xs font-bold border border-gray-300 rounded-xl px-3 py-2.5 outline-none focus:border-[#03AC0E] disabled:bg-gray-100"
                @change="onCityChange"
              >
                <option value="">-- Pilih Kota/Kabupaten --</option>
                <option v-for="c in cities" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
              <input
                v-else
                :value="form.kabupaten || '-'"
                disabled
                class="w-full text-xs font-bold border border-gray-200 bg-gray-50 text-gray-600 rounded-xl px-3 py-2.5"
              />
            </div>

            <!-- Kecamatan -->
            <div class="space-y-1.5">
              <label class="text-xs font-bold text-gray-600">Kecamatan</label>
              <select
                v-if="isEditing"
                v-model="selectedIds.district"
                :disabled="!districts.length"
                class="w-full text-xs font-bold border border-gray-300 rounded-xl px-3 py-2.5 outline-none focus:border-[#03AC0E] disabled:bg-gray-100"
                @change="onDistrictChange"
              >
                <option value="">-- Pilih Kecamatan --</option>
                <option v-for="d in districts" :key="d.id" :value="d.id">{{ d.name }}</option>
              </select>
              <input
                v-else
                :value="form.kecamatan || '-'"
                disabled
                class="w-full text-xs font-bold border border-gray-200 bg-gray-50 text-gray-600 rounded-xl px-3 py-2.5"
              />
            </div>
          </div>

          <!-- Alamat Detail -->
          <div class="space-y-1.5">
            <label class="text-xs font-bold text-gray-600">Alamat Lengkap / Patokan Gedung</label>
            <textarea
              v-model="form.alamat"
              rows="3"
              :disabled="!isEditing"
              placeholder="Contoh: Jl. Baros No. 12, RT 02/05, Kelurahan Utama, Cimahi Selatan"
              class="w-full text-xs font-medium border border-gray-300 rounded-xl p-3 outline-none transition-colors disabled:bg-gray-50 disabled:text-gray-500 focus:border-[#03AC0E]"
            />
          </div>
        </div>

        <!-- Action Button when Editing -->
        <div v-if="isEditing" class="pt-4 border-t border-gray-100 flex items-center justify-end gap-3">
          <button
            type="button"
            class="px-5 py-2.5 rounded-xl border border-gray-300 text-xs font-bold text-gray-700 hover:bg-gray-100 transition-colors"
            @click="handleCancel"
          >
            Batal
          </button>
          <button
            type="submit"
            :disabled="isSaving"
            class="px-6 py-2.5 rounded-xl bg-[#03AC0E] hover:bg-[#028b0b] active:bg-[#027509] text-white text-xs font-bold transition-all shadow-xs active:scale-95 disabled:bg-gray-300 flex items-center gap-2"
          >
            <UIcon v-if="isSaving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            {{ isSaving ? "Menyimpan..." : "Simpan Perubahan" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>