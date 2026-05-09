<template>
    <div class="flex h-full bg-slate-50 overflow-hidden">
  
      <!-- ── INBOX SIDEBAR ─────────────────────────────────────────── -->
      <aside
        class="w-80 shrink-0 bg-white border-r border-slate-100 flex flex-col overflow-hidden"
        :class="{ 'hidden md:flex': $route.params.id }"
      >
        <!-- Header -->
        <div class="px-5 pt-6 pb-4 border-b border-slate-100">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-slate-900 rounded-xl flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h2 class="text-base font-bold text-slate-900">Pesan</h2>
            </div>
            <span
              v-if="store.totalUnreadBadge > 0"
              class="px-2 py-0.5 bg-rose-500 text-white text-xs font-bold rounded-full min-w-[24px] text-center"
            >
              {{ store.totalUnreadBadge > 99 ? '99+' : store.totalUnreadBadge }}
            </span>
          </div>
  
          <!-- Search -->
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" fill="none"
              stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0" />
            </svg>
            <input
              v-model="search"
              type="text"
              placeholder="Cari percakapan…"
              class="w-full pl-8 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900/20 focus:border-slate-400 transition"
            />
          </div>
        </div>
  
        <!-- Conversation List -->
        <div class="flex-1 overflow-y-auto">
          <!-- Skeleton -->
          <template v-if="store.loadingInbox && store.conversations.length === 0">
            <div v-for="i in 7" :key="i" class="flex items-start gap-3 px-4 py-3.5 border-b border-slate-50">
              <div class="w-10 h-10 rounded-full bg-slate-100 animate-pulse shrink-0"></div>
              <div class="flex-1 space-y-2 pt-1">
                <div class="h-3 bg-slate-100 rounded animate-pulse w-2/3"></div>
                <div class="h-2.5 bg-slate-100 rounded animate-pulse w-full"></div>
              </div>
            </div>
          </template>
  
          <!-- Empty -->
          <div v-else-if="filteredConversations.length === 0"
            class="flex flex-col items-center justify-center py-16 text-slate-400">
            <svg class="w-10 h-10 mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p class="text-sm">Belum ada percakapan</p>
          </div>
  
          <!-- List -->
          <button
            v-for="conv in filteredConversations"
            :key="conv.uuid"
            @click="openChat(conv.uuid)"
            class="w-full flex items-start gap-3 px-4 py-3.5 border-b border-slate-50 hover:bg-slate-50 transition-colors text-left relative"
            :class="{
              'bg-slate-50 border-l-[3px] border-l-slate-900 pl-[13px]': $route.params.id === conv.uuid
            }"
          >
            <!-- Avatar -->
            <div class="relative shrink-0">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white"
                :style="{ background: getAvatarColor(conv.user_username) }"
              >
                {{ conv.user_username?.charAt(0)?.toUpperCase() || '?' }}
              </div>
              <!-- Unread badge -->
              <span
                v-if="conv.unread_by_admin > 0"
                class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-rose-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center"
              >
                {{ conv.unread_by_admin > 9 ? '9+' : conv.unread_by_admin }}
              </span>
            </div>
  
            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2 mb-0.5">
                <span
                  class="text-sm truncate"
                  :class="conv.unread_by_admin > 0 ? 'font-bold text-slate-900' : 'font-semibold text-slate-700'"
                >
                  {{ conv.user_username }}
                </span>
                <span class="text-[11px] text-slate-400 shrink-0">{{ formatTime(conv.last_message_at) }}</span>
              </div>
              <p
                class="text-xs truncate leading-relaxed"
                :class="conv.unread_by_admin > 0 ? 'text-slate-700 font-medium' : 'text-slate-400'"
              >
                {{ conv.last_message_preview || 'Belum ada pesan' }}
              </p>
            </div>
          </button>
        </div>
      </aside>
  
      <!-- ── CHAT AREA ──────────────────────────────────────────────── -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
  
        <!-- Placeholder saat belum pilih conversation -->
        <div v-if="!$route.params.id" class="flex-1 flex flex-col items-center justify-center text-slate-400 select-none">
          <div class="w-20 h-20 rounded-3xl bg-slate-100 flex items-center justify-center mb-4">
            <svg class="w-9 h-9 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <p class="text-base font-semibold text-slate-500 mb-1">Pilih percakapan</p>
          <p class="text-sm text-slate-400 text-center max-w-[220px]">
            Klik nama pengguna di kiri untuk mulai membalas
          </p>
        </div>
  
        <!-- Nested route: [id].vue di-render di sini -->
        <router-view v-else @back="closeChat" />
      </div>
  
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useMessageStore } from '@/stores/messageStore'
  
  const router = useRouter()
  const route  = useRoute()
  const store  = useMessageStore()
  
  const search = ref('')
  
  const filteredConversations = computed(() => {
    const q = search.value.toLowerCase().trim()
    if (!q) return store.conversations
    return store.conversations.filter(c =>
      c.user_username?.toLowerCase().includes(q) ||
      c.last_message_preview?.toLowerCase().includes(q)
    )
  })
  
  function openChat(convId) {
    router.push(`/pesan/${convId}`)
  }
  
  function closeChat() {
    store.closeConversation()
    router.push('/pesan')
  }
  
  // Avatar color deterministik dari nama
  function getAvatarColor(name = '') {
    const colors = [
      'linear-gradient(135deg,#667eea,#764ba2)',
      'linear-gradient(135deg,#f093fb,#f5576c)',
      'linear-gradient(135deg,#4facfe,#00f2fe)',
      'linear-gradient(135deg,#43e97b,#38f9d7)',
      'linear-gradient(135deg,#fa709a,#fee140)',
      'linear-gradient(135deg,#a18cd1,#fbc2eb)',
      'linear-gradient(135deg,#fccb90,#d57eeb)',
      'linear-gradient(135deg,#a1c4fd,#c2e9fb)',
    ]
    let hash = 0
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
    return colors[Math.abs(hash) % colors.length]
  }
  
  function formatTime(ts) {
    if (!ts) return ''
    const d   = new Date(ts)
    const now = new Date()
    if (d.toDateString() === now.toDateString())
      return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
    const yesterday = new Date(now)
    yesterday.setDate(now.getDate() - 1)
    if (d.toDateString() === yesterday.toDateString()) return 'Kemarin'
    return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'short' })
  }
  
  onMounted(() => {
    if (store.conversations.length === 0) store.fetchInbox()
  })
  </script>
  
  <style scoped>
  @reference "tailwindcss";
  aside::-webkit-scrollbar       { width: 4px; }
  aside::-webkit-scrollbar-track { background: transparent; }
  aside::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 99px; }
  </style>