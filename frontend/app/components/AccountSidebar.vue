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
    title: "Profil Saya",
    items: [
      { label: "Biodata Diri", to: "/dashboard", icon: "i-heroicons-user", exact: true },
      { label: "Daftar Alamat", to: "/dashboard/address", icon: "i-heroicons-map-pin" },
      { label: "Keamanan", to: "/dashboard/change-password", icon: "i-heroicons-shield-check" },
    ]
  },
  {
    title: "Transaksi",
    items: [
      { label: "Pesanan Saya", to: "/dashboard/orders", icon: "i-heroicons-shopping-bag" },
      { label: "Layanan Jasa", to: "/dashboard/jasa", icon: "i-heroicons-wrench-screwdriver" },
      { label: "Barang Favorit", to: "/dashboard/wishlist", icon: "i-heroicons-heart" },
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
    <div class="flex flex-col gap-4 lg:sticky lg:top-[84px]">
      
      <!-- ── 1. Profile Section ── -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden p-4">
        <div class="flex items-center gap-3">
          <div class="shrink-0 relative">
            <NuxtImg
              :src="userAvatar"
              class="w-12 h-12 rounded-full border border-gray-100 object-cover"
              alt="Avatar"
            />
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-sm font-bold text-gray-900 truncate tracking-tight">
              {{ userStore.profile?.username || "Pengguna" }}
            </h2>
            <div class="flex items-center gap-1.5 mt-0.5">
              <UIcon name="i-heroicons-check-badge" class="w-3.5 h-3.5 text-blue-500" />
              <span class="text-[11px] text-gray-500 font-medium">Verified User</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── 2. Membership Banner ── -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden p-4">
        <div class="bg-emerald-50 rounded-lg p-3 border border-emerald-100">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-sparkles" class="w-5 h-5 text-emerald-600" />
              <span class="text-xs font-black text-emerald-900 uppercase tracking-wider">PasarCctv Plus</span>
            </div>
          </div>
          <p class="text-[11px] text-emerald-700 leading-relaxed font-medium">Nikmati Gratis Ongkir tanpa batas!</p>
          <button class="mt-2 text-[10px] font-bold text-emerald-600 hover:underline">Pelajari Selengkapnya</button>
        </div>
      </div>

      <!-- ── 3. Navigation Menu Grouped ── -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden py-2">
        <div v-for="(group, idx) in navigationGroups" :key="idx" class="mb-2 last:mb-0">
          <div class="px-4 py-2 flex items-center justify-between cursor-pointer group" @click="group.isOpen = !group.isOpen">
             <h3 class="text-xs font-bold text-gray-900 uppercase tracking-wider">{{ group.title }}</h3>
             <UIcon name="i-heroicons-chevron-down" class="w-4 h-4 text-gray-400 transition-transform" />
          </div>
          
          <div class="flex flex-col">
            <NuxtLink
              v-for="item in group.items"
              :key="item.to"
              :to="item.to"
              :exact="item.exact"
              class="group flex items-center gap-3 px-6 py-2.5 transition-colors"
              active-class="active-item"
            >
              <span class="text-sm font-medium text-gray-600 group-hover:text-[#03AC0E] group-[.active-item]:text-[#03AC0E] group-[.active-item]:font-bold">
                {{ item.label }}
              </span>
            </NuxtLink>
          </div>
          <div v-if="idx < navigationGroups.length - 1" class="mx-4 mt-2 border-b border-gray-100"></div>
        </div>

        <!-- Logout Section -->
        <div class="mt-2 pt-2 border-t border-gray-100 px-4">
          <button
            @click="handleLogout"
            class="w-full flex items-center gap-3 py-3 text-gray-500 hover:text-red-600 transition-colors"
          >
            <UIcon name="i-heroicons-arrow-left-on-rectangle" class="w-5 h-5" />
            <span class="text-sm font-bold">Keluar</span>
          </button>
        </div>
      </div>

    </div>
  </aside>
</template>

<style scoped>
.active-item {
  position: relative;
}
.active-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background-color: #03AC0E;
  border-radius: 0 4px 4px 0;
}
</style>

