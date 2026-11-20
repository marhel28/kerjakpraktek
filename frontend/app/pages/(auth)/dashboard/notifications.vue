<script setup lang="ts">
definePageMeta({ layout: "auth" });

const {
  notifications,
  isLoading,
  unreadCount,
  isRealtimeConnected,
  markAsRead,
  markAllAsRead,
  deleteNotification,
} = useChat();

const tabs = [
  { label: "Biodata Diri", to: "/dashboard" },
  { label: "Daftar Alamat", to: "/dashboard/address" },
  { label: "Keamanan Akun", to: "/dashboard/change-password" },
  { label: "Notifikasi", to: "/dashboard/notifications" },
];

const getNotificationIcon = (type?: string): string => {
  switch (type) {
    case "order": return "i-heroicons-shopping-bag";
    case "promo": return "i-heroicons-receipt-percent";
    case "chat": return "i-heroicons-chat-bubble-left-right";
    case "system": return "i-heroicons-bolt";
    default: return "i-heroicons-bell";
  }
};

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  if (minutes < 1) return "Baru saja";
  if (minutes < 60) return `${minutes}m`;
  if (hours < 24) return `${hours}j`;
  return date.toLocaleDateString("id-ID", { day: "numeric", month: "short" });
};

const handleNotificationClick = (notification: any) => {
  if (!notification.read_at) markAsRead(notification.id);
  const targetUrl = notification.metadata?.url || notification.metadata?.action_url;
  if (targetUrl) navigateTo(targetUrl);
};

useHead({ title: "Notifikasi — PasarCctv" });
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- MOBILE HEADER -->
    <div class="lg:hidden flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-white sticky top-0 z-10">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/dashboard')" class="p-1 -ml-1 text-gray-400 hover:text-gray-900 transition-colors">
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        </button>
        <h1 class="text-base font-bold text-gray-900">Notifikasi</h1>
      </div>
      <button v-if="unreadCount > 0" @click="markAllAsRead" class="text-xs font-black text-[#03AC0E] hover:underline uppercase tracking-wider">
        Baca Semua
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
      <header class="hidden lg:flex items-center justify-between gap-6 mb-8">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Notifikasi</h2>
          <p class="text-xs text-gray-400 mt-1 uppercase tracking-widest font-bold">Update aktivitas akun Anda</p>
        </div>
        <button v-if="unreadCount > 0" @click="markAllAsRead" class="text-sm font-bold text-[#03AC0E] hover:underline transition-colors">
          Tandai dibaca semua
        </button>
      </header>

      <main class="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
        <div v-if="isLoading" class="p-12 text-center">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-gray-200 animate-spin mx-auto mb-4" />
          <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Memuat...</p>
        </div>

        <DashboardEmptyState
          v-else-if="notifications.length === 0"
          icon="i-heroicons-bell"
          title="Belum Ada Notifikasi"
          description="Pemberitahuan terkait pesanan, booking jasa, dan promo akan muncul di sini."
        />

        <div v-else class="divide-y divide-gray-100">
          <div v-for="notif in notifications" :key="notif.id" @click="handleNotificationClick(notif)"
            class="flex items-start gap-4 p-6 transition-all hover:bg-gray-50 cursor-pointer relative group"
            :class="!notif.read_at ? 'bg-emerald-50/10' : ''"
          >
            <!-- Unread Dot -->
            <div v-if="!notif.read_at" class="absolute left-0 top-0 bottom-0 w-1 bg-[#03AC0E]"></div>
            
            <div class="w-10 h-10 rounded-lg bg-gray-50 flex items-center justify-center border border-gray-200 flex-shrink-0">
              <UIcon :name="getNotificationIcon(notif.type)" class="w-5 h-5 text-gray-400" />
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-4 mb-1">
                <h3 class="text-sm font-bold text-gray-900 truncate tracking-tight">{{ notif.title }}</h3>
                <span class="text-[10px] font-bold text-gray-400 uppercase whitespace-nowrap">{{ formatTime(notif.created_at) }}</span>
              </div>
              <p class="text-xs leading-relaxed line-clamp-2" :class="!notif.read_at ? 'text-gray-900 font-bold' : 'text-gray-500 font-medium'">
                {{ notif.content }}
              </p>
              
              <div class="flex items-center gap-4 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                <button @click.stop="deleteNotification(notif.id)" class="text-[10px] font-black text-gray-400 hover:text-red-600 uppercase tracking-widest">Hapus</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Realtime Connection Status -->
    <div v-if="isRealtimeConnected !== null" class="fixed bottom-6 right-6 z-[110]">
      <div class="flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-gray-200 shadow-xl">
        <div class="w-1.5 h-1.5 rounded-full" :class="isRealtimeConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></div>
        <span class="text-[10px] font-bold text-gray-600 uppercase tracking-widest">{{ isRealtimeConnected ? 'Live' : 'Offline' }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
