<script setup lang="ts">
import { useUserStore } from "~/stores/user";
import { computed } from "vue";

const { logout } = useAuth();
const userStore = useUserStore();

// Marketplace Color: #03AC0E (Tokopedia Green)

const navigationGroups = computed(() => [
  {
    title: "Kotak Masuk",
    items: [
      { label: "Chat", to: "/dashboard/chat", icon: "i-heroicons-chat-bubble-left-right" },
      { label: "Pesan Bantuan", to: "/dashboard/help", icon: "i-heroicons-question-mark-circle" },
    ]
  },
  {
    title: "Pembelian",
    items: [
      { label: "Pesanan Saya", to: "/dashboard/orders", icon: "i-heroicons-shopping-bag" },
      { label: "Layanan Jasa Teknisi", to: "/dashboard/jasa", icon: "i-heroicons-wrench-screwdriver" },
      { label: "Barang Favorit", to: "/dashboard/wishlist", icon: "i-heroicons-heart" },
    ]
  },
  {
    title: "Profil Saya",
    items: [
      { label: "Biodata Diri", to: "/dashboard", icon: "i-heroicons-user", exact: true },
      { label: "Daftar Alamat", to: "/dashboard/address", icon: "i-heroicons-map-pin" },
      { label: "Keamanan Akun", to: "/dashboard/change-password", icon: "i-heroicons-shield-check" },
      { label: "Notifikasi", to: "/dashboard/notifications", icon: "i-heroicons-bell" },
    ]
  }
]);

const userAvatar = computed(() => {
  const name = userStore.profile?.username || "Pengguna";
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=03AC0E&color=fff&bold=true`;
});

const handleLogout = async () => {
  if (confirm("Apakah Anda yakin ingin keluar?")) {
    await logout();
  }
};
</script>

<template>
  <aside class="w-full lg:w-[300px] flex-shrink-0 font-sans">
    <div class="flex flex-col gap-3.5 lg:sticky lg:top-[84px]">
      
      <!-- ── 1. Profile Section (Tokopedia Style) ── -->
      <div class="bg-white rounded-xl border border-gray-200/80 shadow-sm p-4">
        <div class="flex items-center gap-3">
          <div class="shrink-0 relative">
            <NuxtImg
              :src="userAvatar"
              class="w-12 h-12 rounded-full border border-gray-100 ring-2 ring-emerald-500/20 object-cover"
              alt="Avatar"
            />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <h2 class="text-sm font-bold text-gray-900 truncate tracking-tight">
                {{ userStore.profile?.username || "Pengguna" }}
              </h2>
              <NuxtLink
                to="/dashboard"
                class="text-gray-400 hover:text-[#03AC0E] transition-colors p-1"
                title="Ubah Profil"
              >
                <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
              </NuxtLink>
            </div>
            <div class="flex items-center gap-1.5 mt-0.5">
              <UIcon name="i-heroicons-check-badge" class="w-3.5 h-3.5 text-[#03AC0E]" />
              <span class="text-[11px] text-gray-500 font-medium">Member Terverifikasi</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── 2. Dompet & Kupon (Tokopedia Saldo & Koin Box) ── -->
      <div class="bg-white rounded-xl border border-gray-200/80 shadow-sm p-3.5 divide-y divide-gray-100">
        <!-- Saldo Akun -->
        <div class="flex items-center justify-between pb-2.5">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-emerald-50 text-[#03AC0E] flex items-center justify-center">
              <UIcon name="i-heroicons-wallet" class="w-4 h-4" />
            </div>
            <div>
              <p class="text-[11px] text-gray-500 font-medium">Saldo PasarCctv</p>
              <p class="text-xs font-bold text-gray-900">Rp 0</p>
            </div>
          </div>
          <button class="text-[11px] font-bold text-[#03AC0E] hover:underline">
            Top Up
          </button>
        </div>

        <!-- Koin & Kupon -->
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

      <!-- ── 3. Membership Card (Tokopedia PLUS) ── -->
      <div class="bg-gradient-to-br from-emerald-500/10 via-emerald-50 to-teal-50 rounded-xl border border-emerald-200/60 shadow-sm p-3.5">
        <div class="flex items-center justify-between mb-1.5">
          <div class="flex items-center gap-1.5">
            <UIcon name="i-heroicons-sparkles" class="w-4 h-4 text-emerald-600" />
            <span class="text-xs font-bold text-emerald-950 uppercase tracking-wider">PasarCctv Plus</span>
          </div>
          <span class="px-1.5 py-0.5 bg-emerald-600 text-white text-[9px] font-black rounded uppercase">Aktif</span>
        </div>
        <p class="text-[11px] text-emerald-800 leading-snug font-medium">Gratis ongkir tanpa batas & diskon jasa teknisi</p>
      </div>

      <!-- ── 4. Navigation Menu Grouped ── -->
      <div class="bg-white rounded-xl border border-gray-200/80 shadow-sm overflow-hidden py-2">
        <div v-for="(group, idx) in navigationGroups" :key="idx" class="mb-1.5 last:mb-0">
          <div class="px-4 py-1.5 flex items-center justify-between">
            <h3 class="text-[11px] font-bold text-gray-400 uppercase tracking-wider">{{ group.title }}</h3>
          </div>
          
          <div class="flex flex-col">
            <NuxtLink
              v-for="item in group.items"
              :key="item.to"
              :to="item.to"
              :exact="item.exact"
              class="group flex items-center gap-3 px-4 py-2 transition-colors hover:bg-gray-50"
              active-class="active-item"
            >
              <UIcon
                :name="item.icon"
                class="w-4 h-4 text-gray-400 group-hover:text-[#03AC0E] group-[.active-item]:text-[#03AC0E] transition-colors"
              />
              <span class="text-xs font-medium text-gray-600 group-hover:text-[#03AC0E] group-[.active-item]:text-[#03AC0E] group-[.active-item]:font-bold">
                {{ item.label }}
              </span>
            </NuxtLink>
          </div>
          <div v-if="idx < navigationGroups.length - 1" class="mx-4 my-1.5 border-b border-gray-100"></div>
        </div>

        <!-- Logout Section -->
        <div class="mt-2 pt-2 border-t border-gray-100 px-4">
          <button
            @click="handleLogout"
            class="w-full flex items-center gap-3 py-2 text-gray-500 hover:text-red-600 transition-colors"
          >
            <UIcon name="i-heroicons-arrow-left-on-rectangle" class="w-4 h-4" />
            <span class="text-xs font-bold">Keluar</span>
          </button>
        </div>
      </div>

    </div>
  </aside>
</template>

<style scoped>
.active-item {
  position: relative;
  background-color: #f0fdf4;
}
.active-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: #03AC0E;
  border-radius: 0 4px 4px 0;
}
</style>
