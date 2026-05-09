<template>
  <div class="min-h-screen bg-[#F5F6F8] pb-20">
    <!-- Main Dashboard Layout -->
    <div class="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Mobile Header / Back Button (Hanya tampil di mobile) -->
      <div class="lg:hidden flex items-center gap-3 mb-6">
        <button
          @click="$router.back()"
          class="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm border border-gray-100 text-gray-700 hover:bg-gray-50 active:scale-95 transition-all"
        >
          <Icon name="lucide:arrow-left" class="w-5 h-5" />
        </button>
        <h1 class="text-xl font-extrabold text-gray-900">Notifikasi</h1>
      </div>

      <div class="flex flex-col lg:flex-row gap-6 lg:gap-8 items-start">
        <!-- ── Sidebar Component ───────────────────────────────────── -->
        <AccountSidebar class="hidden lg:block sticky top-24" />

        <!-- ── Main Content Area ─────────────────────────────────── -->
        <main class="flex-1 w-full flex flex-col gap-4">
          <!-- Notif Container -->
          <div
            class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col min-h-[600px] relative"
          >
            <!-- Sticky Header Notif -->
            <div
              class="px-6 py-5 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white/80 backdrop-blur-md z-10"
            >
              <div class="flex items-center gap-3">
                <h2 class="text-lg font-extrabold text-gray-900 hidden lg:block">
                  Notifikasi Anda
                </h2>
                <!-- Badge Count -->
                <span
                  v-if="unreadCount > 0"
                  class="bg-red-500 text-white text-[10px] font-black px-2 py-0.5 rounded-full"
                >
                  {{ unreadCount }} Baru
                </span>
              </div>

              <button
                v-if="unreadCount > 0"
                @click="markAllAsRead"
                class="text-sm text-[#03AC0E] hover:text-green-700 font-bold transition-colors flex items-center gap-1.5"
              >
                <Icon name="lucide:check-check" class="w-4 h-4" />
                Tandai semua dibaca
              </button>
            </div>

            <!-- Loading State -->
            <div
              v-if="isLoading"
              class="flex-1 flex flex-col items-center justify-center py-20"
            >
              <Icon
                name="lucide:loader-2"
                class="w-10 h-10 animate-spin text-[#03AC0E] mb-4"
              />
              <p class="text-sm text-gray-500 font-medium">Memuat notifikasi...</p>
            </div>

            <!-- Error State -->
            <div
              v-else-if="error"
              class="flex-1 flex flex-col items-center justify-center py-20 px-4 text-center"
            >
              <div
                class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-4"
              >
                <Icon name="lucide:alert-circle" class="w-8 h-8 text-red-500" />
              </div>
              <h3 class="text-lg font-bold text-gray-900 mb-2">Gagal Memuat Data</h3>
              <p class="text-gray-500 mb-6 max-w-sm">{{ error }}</p>
              <button
                @click="refresh"
                class="px-6 py-2.5 bg-[#03AC0E] text-white font-bold rounded-xl hover:bg-green-600 transition-colors shadow-sm active:scale-95"
              >
                Coba Lagi
              </button>
            </div>

            <!-- Empty State -->
            <div
              v-else-if="notifications.length === 0"
              class="flex-1 flex flex-col items-center justify-center py-20 px-4 text-center"
            >
              <div
                class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6"
              >
                <Icon name="lucide:bell-ring" class="w-10 h-10 text-gray-300" />
              </div>
              <h3 class="text-lg font-bold text-gray-900 mb-1.5">Belum ada notifikasi</h3>
              <p class="text-gray-500 text-sm max-w-sm">
                Pemberitahuan seputar transaksi, promo, dan info penting akan muncul di
                sini.
              </p>
            </div>

            <!-- Notifications List -->
            <div v-else class="flex flex-col">
              <div
                v-for="notification in notifications"
                :key="notification.id"
                class="group relative flex items-start gap-4 p-5 transition-all duration-200 border-b border-gray-50 last:border-0 cursor-pointer"
                :class="
                  !notification.read_at ? 'bg-[#E5F7E6]/30' : 'bg-white hover:bg-gray-50'
                "
                @click="handleNotificationClick(notification)"
              >
                <!-- Unread Indicator Line (kiri) -->
                <div
                  v-if="!notification.read_at"
                  class="absolute left-0 top-0 bottom-0 w-1 bg-[#03AC0E] rounded-r-full"
                ></div>

                <!-- Icon berdasarkan type -->
                <div class="flex-shrink-0 mt-0.5">
                  <div
                    class="w-12 h-12 rounded-full flex items-center justify-center shadow-sm border border-white"
                    :class="getNotificationIconBg(notification.type)"
                  >
                    <Icon
                      :name="getNotificationIcon(notification.type)"
                      class="w-5 h-5"
                      :class="getNotificationIconColor(notification.type)"
                    />
                  </div>
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-3 mb-1">
                    <h3
                      class="text-[14px] font-bold truncate pr-2 transition-colors group-hover:text-[#03AC0E]"
                      :class="notification.read_at ? 'text-gray-700' : 'text-gray-900'"
                    >
                      {{ notification.title }}
                    </h3>

                    <!-- Unread Dot Mobile -->
                    <span
                      v-if="!notification.read_at"
                      class="w-2.5 h-2.5 bg-[#03AC0E] rounded-full flex-shrink-0 mt-1 shadow-sm lg:hidden"
                    />
                  </div>

                  <p
                    class="text-[13px] leading-relaxed line-clamp-2"
                    :class="
                      notification.read_at ? 'text-gray-500' : 'text-gray-700 font-medium'
                    "
                  >
                    {{ notification.content }}
                  </p>

                  <div class="flex items-center justify-between mt-3">
                    <time
                      class="text-[11px] font-medium flex items-center gap-1.5"
                      :class="notification.read_at ? 'text-gray-400' : 'text-[#03AC0E]'"
                      :datetime="notification.created_at"
                    >
                      <Icon name="lucide:clock" class="w-3.5 h-3.5" />
                      {{ formatTime(notification.created_at) }}
                    </time>

                    <!-- Action Buttons (Muncul saat di hover di desktop) -->
                    <div
                      class="opacity-100 lg:opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center gap-4"
                    >
                      <button
                        v-if="!notification.read_at"
                        @click.stop="markAsRead(notification.id)"
                        class="text-[11px] text-[#03AC0E] hover:text-green-700 font-bold tracking-wide"
                      >
                        Tandai Dibaca
                      </button>
                      <button
                        @click.stop="deleteNotification(notification.id)"
                        class="text-[11px] text-gray-400 hover:text-red-500 font-bold tracking-wide transition-colors"
                      >
                        Hapus
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>

    <!-- ── Realtime Status Indicator ────────────────────────────────── -->
    <div
      v-if="isRealtimeConnected !== null"
      class="fixed bottom-6 right-6 z-50 transition-all duration-500"
    >
      <div
        class="flex items-center gap-2.5 px-4 py-2 rounded-full text-xs font-bold shadow-xl border backdrop-blur-md"
        :class="
          isRealtimeConnected
            ? 'bg-green-50/90 text-[#03AC0E] border-green-100'
            : 'bg-red-50/90 text-red-600 border-red-100'
        "
      >
        <span class="relative flex h-2.5 w-2.5">
          <span
            v-if="isRealtimeConnected"
            class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#03AC0E] opacity-75"
          ></span>
          <span
            class="relative inline-flex rounded-full h-2.5 w-2.5"
            :class="isRealtimeConnected ? 'bg-[#03AC0E]' : 'bg-red-500'"
          ></span>
        </span>
        {{ isRealtimeConnected ? "Realtime Terhubung" : "Koneksi Terputus" }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Pastikan fungsi ini merujuk ke store/composable yang Anda miliki (contoh di atas menggunakan useChat, sesuaikan jika butuh useNotificationStore)
const {
  notifications,
  isLoading,
  error,
  unreadCount,
  isRealtimeConnected,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  refresh,
} = useChat();

// ─── Helper Functions ─────────────────────────────────────────────

const getNotificationIcon = (type?: string): string => {
  switch (type) {
    case "order":
      return "lucide:shopping-bag";
    case "promo":
      return "lucide:badge-percent"; // Icon yang lebih modern
    case "chat":
      return "lucide:message-square"; // Icon yang lebih modern
    case "system":
      return "lucide:zap"; // Icon zap untuk info sistem yang cepat
    default:
      return "lucide:bell";
  }
};

const getNotificationIconBg = (type?: string): string => {
  switch (type) {
    case "order":
      return "bg-emerald-100";
    case "promo":
      return "bg-orange-100";
    case "chat":
      return "bg-blue-100";
    case "system":
      return "bg-purple-100";
    default:
      return "bg-gray-100";
  }
};

const getNotificationIconColor = (type?: string): string => {
  switch (type) {
    case "order":
      return "text-emerald-600";
    case "promo":
      return "text-orange-600";
    case "chat":
      return "text-blue-600";
    case "system":
      return "text-purple-600";
    default:
      return "text-gray-600";
  }
};

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return "Baru saja";
  if (minutes < 60) return `${minutes} menit yang lalu`;
  if (hours < 24) return `${hours} jam yang lalu`;
  if (days < 7) return `${days} hari yang lalu`;

  return date.toLocaleDateString("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
};

const handleNotificationClick = (notification: any) => {
  // Tandai dibaca saat diklik
  if (!notification.read_at) {
    markAsRead(notification.id);
  }

  // Navigasi jika ada URL
  if (notification.metadata?.url) {
    navigateTo(notification.metadata.url);
  }
};

// ─── SEO ─────────────────────────────────────────────────────────
useHead({
  title: "Notifikasi",
  meta: [
    {
      name: "description",
      content: "Lihat semua notifikasi Anda",
    },
  ],
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Custom scrollbar untuk container jika list notifikasi di scroll (opsional) */
main ::-webkit-scrollbar {
  width: 6px;
}
main ::-webkit-scrollbar-track {
  background: transparent;
}
main ::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 20px;
}
</style>
