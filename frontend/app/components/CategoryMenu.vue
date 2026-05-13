<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotificationStore } from '~/stores/notificationStore'

const route = useRoute()
const router = useRouter()

// ─── AUTH & USER DATA (Untuk Mobile Sidebar) ─────────────────────
const token = useCookie('token')
const userDataCookie = useCookie('user_data')
const isAuthenticated = computed(() => !!token.value)

const userName = computed(() => {
  if (!isAuthenticated.value || !userDataCookie.value) return "Guest"
  if (userDataCookie.value.name) return userDataCookie.value.name
  if (userDataCookie.value.email) {
    const emailName = userDataCookie.value.email.split('@')[0]
    return emailName.charAt(0).toUpperCase() + emailName.slice(1)
  }
  return "Member"
})

const handleLogout = async () => {
  // Clear stores & cookies
  const notificationStore = useNotificationStore()
  notificationStore.cleanup()
  
  token.value = null
  userDataCookie.value = null
  useCookie('sb_access_token').value = null
  useCookie('sb_refresh_token').value = null
  useCookie('supabase_user').value = null

  closeMobileSidebar()
  router.push('/login')
}

// 🔥 penting: state mount
const isMounted = ref(false)

// ─── SCROLL AUTO CLOSE ───────────────────────────────────────────
const handleScroll = () => {
  if (isOpen.value) {
    // Tutup jika scroll lebih dari 30% tinggi layar
    const threshold = window.innerHeight * 0.3
    if (window.scrollY > threshold) {
      isOpen.value = false
      isHovered.value = false
    }
  }
}

onMounted(() => {
  isMounted.value = true
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})

// ✅ SSR-safe fetch (TANPA await)
const { data: rawCategories, pending } = useFetch<any[]>('/api/category', {
  key: 'nav-categories',
  default: () => [],
  transform: (res) => {
    if (!res || !Array.isArray(res)) return []
    const map = new Map()
    res.forEach(item => {
      if (item.id && !map.has(item.id)) map.set(item.id, item)
    })
    return Array.from(map.values())
  }
})

// 🔒 state harus konsisten SSR & client
const isOpen = ref(route.path === '/')
const isHovered = ref(false)
const activeMobileCategory = ref<string | null>(null)

// Mobile
const isMobileSidebarOpen = ref(false)
const activeMobileSub = ref<string | null>(null)

const openMobileSidebar = () => {
  isMobileSidebarOpen.value = true
}

const closeMobileSidebar = () => {
  isMobileSidebarOpen.value = false
  activeMobileSub.value = null
}

defineExpose({ isOpen, openMobileSidebar, closeMobileSidebar })

const handleToggleMenu = () => {
  isOpen.value = !isOpen.value
}

watch(() => route.path, (newPath) => {

  if (newPath !== '/') {
    isOpen.value = false
    isHovered.value = false
    activeMobileCategory.value = null
  } else {
    isOpen.value = true
  }

  closeMobileSidebar()
}, { immediate: true })

const handleHover = (status: boolean) => {
  if (isOpen.value) isHovered.value = status
}
</script>

<template>
  <div class="category-main-container relative">
    <Transition name="fade">
      <div
        v-if="isHovered && isOpen"
        class="fixed inset-0 bg-black/60 backdrop-blur-[2px] z-[40] pointer-events-none"
      />
    </Transition>

    <div
      class="relative hidden lg:block w-[260px] font-sans z-[50]"
      @mouseenter="handleHover(true)"
      @mouseleave="handleHover(false)"
    >
      <button
        class="w-full flex items-center justify-between px-4 py-3.5 border/40"
        :class="isOpen ? 'bg-[#f8f9fa] border-b-0 rounded-t-lg' : 'bg-white rounded-lg shadow-sm'"
        @click="handleToggleMenu"
      >
        <div class="flex items-center gap-3">
          <UIcon name="i-heroicons-bars-3-bottom-left" aria-hidden="true" />
          <span class="font-bold text-[13px] uppercase">Browse Categories</span>
        </div>
        <UIcon
          name="i-heroicons-chevron-down"
          :class="isOpen ? 'rotate-180' : ''"
          class="transition-transform"
          aria-hidden="true"
        />
      </button>

      <Transition name="slide-up">
        <nav v-if="isOpen" class="absolute top-full left-0 w-full bg-white border border-gray-200 shadow-xl rounded-b-lg overflow-visible">
          <ul class="flex flex-col w-full relative">
            <li
              v-for="(cat, index) in rawCategories"
              :key="cat.id"
              class="relative border-b border-gray-50 last:border-none"
              @mouseenter="activeMobileCategory = cat.id"
              @mouseleave="activeMobileCategory = null"
            >
              <NuxtLink
                :to="`/category/${cat.slug}`"
                class="flex items-center justify-between px-4 py-3.5 hover:bg-green-50/50 group"
              >
                <div class="flex items-center gap-3">
                  <UIcon
                    :name="cat.icon"
                    :class="activeMobileCategory === cat.id ? 'text-[#03AC0E]' : 'text-gray-400'"
                    aria-hidden="true"
                  />
                  <span
                    class="text-[14px] font-medium"
                    :class="activeMobileCategory === cat.id ? 'text-[#03AC0E]' : 'text-gray-700'"
                  >
                    {{ cat.name }}
                  </span>
                </div>
                <UIcon v-if="cat.subcategories?.length" name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-300" aria-hidden="true" />
              </NuxtLink>

              <div
                v-if="cat.subcategories?.length && activeMobileCategory === cat.id"
                class="absolute left-full ml-1 w-[280px] bg-white border border-gray-100 shadow-[10px_0_30px_rgba(0,0,0,0.1)] rounded-xl py-3 px-2 z-[100]"
                :class="index >= 4 ? 'bottom-0' : 'top-0'"
              >
                <div class="px-5 py-2 mb-2 text-[11px] font-bold text-gray-400 uppercase tracking-widest border-b border-gray-50">
                  Sub Kategori
                </div>
                <ul class="space-y-0.5">
                  <li v-for="sub in cat.subcategories" :key="sub.slug">
                    <NuxtLink
                      :to="`/category/${cat.slug}/${sub.slug}`"
                      class="block px-5 py-3 text-[14px] text-gray-600 hover:bg-[#D6FFDE]/50 hover:text-[#03AC0E] rounded-lg transition-colors"
                    >
                      {{ sub.name }}
                    </NuxtLink>
                  </li>
                </ul>
              </div>
            </li>
          </ul>
        </nav>
      </Transition>
    </div>

    <Teleport to="body">
      <Transition name="fade-overlay">
        <div
          v-if="isMobileSidebarOpen"
          class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-[190] lg:hidden"
          aria-hidden="true"
          @click="closeMobileSidebar"
        />
      </Transition>

      <Transition name="slide-left">
        <div
          v-if="isMobileSidebarOpen"
          class="fixed inset-y-0 left-0 w-[85vw] max-w-[320px] bg-white z-[195] lg:hidden flex flex-col shadow-2xl"
          role="dialog"
          aria-modal="true"
        >
          <div class="flex items-center justify-between px-4 py-4 border-b border-gray-100 bg-white sticky top-0 z-10">
            <h2 class="text-[16px] font-bold text-gray-900">Menu Utama</h2>
            <button
              class="p-1.5 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="Tutup menu kategori"
              @click="closeMobileSidebar"
            >
              <UIcon name="i-heroicons-x-mark" class="w-6 h-6 text-gray-600" aria-hidden="true" />
            </button>
          </div>

          <div class="px-4 py-4 bg-white border-b border-gray-100 flex items-center gap-3">
            <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center border border-gray-200 overflow-hidden shrink-0">
              <UIcon v-if="!isAuthenticated" name="i-heroicons-user" class="w-6 h-6 text-gray-400" />
              <span v-else class="text-[#03AC0E] font-bold text-lg">{{ userName.substring(0, 2).toUpperCase() }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[14px] font-bold text-gray-900 truncate">{{ isAuthenticated ? userName : 'Selamat Datang!' }}</p>
              <NuxtLink v-if="!isAuthenticated" to="/login" class="text-[12px] font-bold text-[#03AC0E]" @click="closeMobileSidebar">Masuk / Daftar Akun</NuxtLink>
              <span v-else class="text-[11px] font-medium text-gray-500">Member Aktif</span>
            </div>
          </div>

          <div class="px-4 py-2 bg-gray-50 border-b border-gray-100">
            <span class="text-[11px] font-bold text-gray-500 uppercase tracking-widest">Kategori Produk</span>
          </div>

          <div v-if="pending" class="flex-1 p-4 space-y-2 bg-white">
            <div v-for="i in 6" :key="i" class="flex items-center gap-3 px-2 py-3">
              <USkeleton class="w-6 h-6 rounded-lg" />
              <USkeleton class="h-4 flex-1 rounded" />
            </div>
          </div>

          <div v-else class="flex-1 overflow-hidden flex bg-white">
            <div
              class="flex-1 overflow-y-auto overscroll-contain custom-scrollbar"
              :class="activeMobileSub ? 'w-[45%]' : 'w-full'"
              style="transition: width 0.25s ease"
            >
              <ul class="py-2 pb-20">
                <li v-for="cat in rawCategories" :key="cat.id">
                  <button
                    v-if="cat.subcategories?.length"
                    class="w-full flex items-center justify-between px-4 py-3.5 transition-colors"
                    :class="activeMobileSub === cat.id ? 'bg-[#D6FFDE]/30 text-[#03AC0E]' : 'text-gray-700 hover:bg-gray-50'"
                    @click="activeMobileSub = activeMobileSub === cat.id ? null : cat.id"
                  >
                    <div class="flex items-center gap-3 min-w-0">
                      <UIcon
                        :name="cat.icon"
                        class="w-5 h-5 flex-shrink-0 transition-colors"
                        :class="activeMobileSub === cat.id ? 'text-[#03AC0E]' : 'text-gray-400'"
                      />
                      <span class="text-[13px] font-bold truncate">{{ cat.name }}</span>
                    </div>
                    <UIcon
                      name="i-heroicons-chevron-right"
                      class="w-4 h-4 flex-shrink-0 transition-transform"
                      :class="activeMobileSub === cat.id ? 'rotate-90 text-[#03AC0E]' : 'text-gray-300'"
                    />
                  </button>

                  <NuxtLink
                    v-else
                    :to="`/category/${cat.slug}`"
                    class="flex items-center gap-3 px-4 py-3.5 text-gray-700 hover:bg-gray-50 transition-colors"
                    @click="closeMobileSidebar"
                  >
                    <UIcon :name="cat.icon" class="w-5 h-5 flex-shrink-0 text-gray-400" />
                    <span class="text-[13px] font-bold">{{ cat.name }}</span>
                  </NuxtLink>

                  <Transition name="accordion">
                    <ul
                      v-if="cat.subcategories?.length && activeMobileSub === cat.id"
                      class="bg-gray-50 border-l-[3px] border-[#03AC0E] ml-4 mr-3 rounded-r-lg mb-1 overflow-hidden"
                    >
                      <li>
                        <NuxtLink
                          :to="`/category/${cat.slug}`"
                          class="flex items-center gap-2 px-4 py-3 text-[12px] font-bold text-[#03AC0E] border-b border-gray-200"
                          @click="closeMobileSidebar"
                        >
                          <UIcon name="i-heroicons-squares-2x2" class="w-3.5 h-3.5" />
                          Semua {{ cat.name }}
                        </NuxtLink>
                      </li>
                      <li v-for="sub in cat.subcategories" :key="sub.slug">
                        <NuxtLink
                          :to="`/category/${cat.slug}/${sub.slug}`"
                          class="flex items-center gap-2 px-4 py-2.5 text-[12px] font-medium text-gray-600 hover:text-[#03AC0E] hover:bg-[#D6FFDE]/30 transition-colors"
                          @click="closeMobileSidebar"
                        >
                          <span class="w-1 h-1 rounded-full bg-gray-400 flex-shrink-0" />
                          {{ sub.name }}
                        </NuxtLink>
                      </li>
                    </ul>
                  </Transition>
                </li>
              </ul>
            </div>
          </div>

          <div class="border-t border-gray-200 p-4 bg-white safe-area-bottom shrink-0 shadow-[0_-4px_10px_rgba(0,0,0,0.02)]">
            <button
              v-if="isAuthenticated"
              @click="handleLogout"
              class="w-full flex items-center justify-center gap-2 py-3 bg-white border border-gray-300 text-gray-700 font-bold text-[13px] rounded-lg active:bg-red-50 active:text-[#EF144A] active:border-red-200 transition-colors"
            >
              <Icon name="lucide:log-out" class="w-4 h-4" />
              Keluar Akun
            </button>
            <NuxtLink
              v-else
              to="/category"
              class="flex items-center justify-center gap-2 w-full py-3 rounded-lg bg-gray-50 border border-gray-200 text-[13px] font-bold text-gray-700 active:bg-gray-100 transition-colors"
              @click="closeMobileSidebar"
            >
              <UIcon name="i-heroicons-tag" class="w-4 h-4" />
              Lihat Semua Kategori
            </NuxtLink>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
/* Desktop transitions — tidak berubah */
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(10px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
nav { backface-visibility: hidden; transform: translateZ(0); }
.absolute.left-full { display: block !important; animation: fadeIn 0.15s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateX(5px); } to { opacity: 1; transform: translateX(0); } }

/* ── Mobile transitions ─────────────────────────────── */
.fade-overlay-enter-active, .fade-overlay-leave-active { transition: opacity 0.3s ease; }
.fade-overlay-enter-from, .fade-overlay-leave-to { opacity: 0; }

.slide-left-enter-active { transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-left-leave-active { transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-left-enter-from  { transform: translateX(-100%); }
.slide-left-leave-to    { transform: translateX(-100%); }

.accordion-enter-active { transition: max-height 0.3s ease, opacity 0.3s ease; max-height: 600px; }
.accordion-leave-active { transition: max-height 0.2s ease, opacity 0.2s ease; }
.accordion-enter-from   { max-height: 0; opacity: 0; }
.accordion-leave-to     { max-height: 0; opacity: 0; }

.safe-area-bottom { padding-bottom: env(safe-area-inset-bottom, 16px); }

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 10px; }
</style>