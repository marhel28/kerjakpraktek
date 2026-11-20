<script setup lang="ts">
import { useUserStore } from "~/stores/user";
import { usePesanStore } from "~/stores/UsePesanStore";
import { computed, ref } from "vue";
import { useNotificationStore } from "~/stores/notificationStore";

const { logout } = useAuth();
const userStore = useUserStore();
const pesanStore = usePesanStore();
const notificationStore = useNotificationStore();

// Marketplace Color: #03AC0E (Tokopedia Green)

const navigationGroups = computed(() => [
  {
    title: "Kotak Masuk",
    items: [
      { label: "Chat CS", isChatAction: true, icon: "i-heroicons-chat-bubble-left-right" },
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

const userInitials = computed(() => {
  const name = userStore.profile?.username || "P";
  return name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
});

const showLogoutConfirm = ref(false);
const handleLogout = async () => {
  showLogoutConfirm.value = true;
};
</script>

<template>
  <aside class="w-full lg:w-[300px] flex-shrink-0 font-sans">
    <div class="flex flex-col gap-3.5 lg:sticky lg:top-[84px]">
      
      <!-- ── 1. Profile Section (Tokopedia Style) ── -->
      <div class="bg-white rounded-xl border border-gray-200/80 shadow-sm p-4">
        <div class="flex items-center gap-3">
          <div
            class="shrink-0 w-12 h-12 rounded-full bg-[#03AC0E] text-white flex items-center justify-center font-bold text-sm ring-2 ring-emerald-500/20"
          >
            {{ userInitials }}
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

      <!-- ── 4. Navigation Menu Grouped ── -->
      <div class="bg-white rounded-xl border border-gray-200/80 shadow-sm overflow-hidden py-2">
        <div v-for="(group, idx) in navigationGroups" :key="idx" class="mb-1.5 last:mb-0">
          <div class="px-4 py-1.5 flex items-center justify-between">
            <h3 class="text-[11px] font-bold text-gray-400 uppercase tracking-wider">{{ group.title }}</h3>
          </div>
          
          <div class="flex flex-col">
            <template v-for="item in group.items" :key="item.label">
              <!-- Chat Trigger Button (Open Floating Chat directly) -->
              <button
                v-if="(item as any).isChatAction"
                type="button"
                @click="pesanStore.onPopupOpen()"
                class="group flex items-center justify-between px-4 py-2.5 transition-all hover:bg-gray-50 rounded-xl mx-2 font-medium text-left cursor-pointer"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <UIcon
                    :name="item.icon"
                    class="w-4 h-4 text-gray-400 group-hover:text-[#03AC0E] transition-colors shrink-0"
                  />
                  <span class="text-xs font-semibold text-gray-700 group-hover:text-[#03AC0E] truncate">
                    {{ item.label }}
                  </span>
                </div>
                <span class="text-[10px] bg-emerald-50 text-[#03AC0E] font-extrabold px-1.5 py-0.5 rounded-md uppercase">Live</span>
              </button>

              <!-- Standard Nav Link -->
              <NuxtLink
                v-else
                :to="(item as any).to"
                :exact="(item as any).exact"
                class="group flex items-center justify-between px-4 py-2.5 transition-all hover:bg-gray-50 rounded-xl mx-2 font-medium"
                active-class="active-item"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <UIcon
                    :name="item.icon"
                    class="w-4 h-4 text-gray-400 group-hover:text-[#03AC0E] group-[.active-item]:text-[#03AC0E] transition-colors shrink-0"
                  />
                  <span class="text-xs font-semibold text-gray-700 group-hover:text-[#03AC0E] group-[.active-item]:text-[#03AC0E] group-[.active-item]:font-extrabold truncate">
                    {{ item.label }}
                  </span>
                </div>
                <div class="flex items-center gap-1">
                  <span
                    v-if="(item as any).to === '/dashboard/notifications' && notificationStore.unreadCount > 0"
                    class="min-w-5 h-5 px-1 flex items-center justify-center rounded-full bg-red-500 text-white text-[10px] font-bold"
                  >{{ notificationStore.unreadCount > 9 ? '9+' : notificationStore.unreadCount }}</span>
                  <UIcon
                    name="i-heroicons-chevron-right"
                    class="w-3.5 h-3.5 text-gray-300 group-hover:text-[#03AC0E] group-[.active-item]:text-[#03AC0E] transition-colors"
                  />
                </div>
              </NuxtLink>
            </template>
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

    <!-- Modal Konfirmasi Logout -->
    <Teleport to="body">
      <div
        v-if="showLogoutConfirm"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-xs"
        @click.self="showLogoutConfirm = false"
      >
        <div class="w-full max-w-sm bg-white rounded-2xl p-6 shadow-xl border border-gray-100 text-center">
          <div class="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-4">
            <UIcon name="i-heroicons-arrow-left-on-rectangle" class="w-6 h-6" />
          </div>
          <h3 class="text-base font-bold text-gray-900 mb-1">Keluar dari Akun?</h3>
          <p class="text-xs text-gray-500 mb-6 leading-relaxed">
            Anda harus masuk kembali untuk mengakses pesanan dan data akun.
          </p>
          <div class="flex items-center gap-3">
            <button
              @click="showLogoutConfirm = false"
              class="flex-1 py-2.5 px-4 rounded-xl border border-gray-200 text-xs font-bold text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Batal
            </button>
            <button
              @click="logout(); showLogoutConfirm = false"
              class="flex-1 py-2.5 px-4 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-colors shadow-sm"
            >
              Ya, Keluar
            </button>
          </div>
        </div>
      </div>
    </Teleport>
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
