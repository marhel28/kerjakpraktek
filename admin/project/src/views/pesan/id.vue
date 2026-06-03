<template>
    <div class="flex flex-col h-full bg-white overflow-hidden">
  
      <!-- ── HEADER ─────────────────────────────────────────────────── -->
      <div class="flex items-center gap-3 px-4 md:px-6 py-3.5 border-b border-slate-100 shrink-0 bg-white">
  
        <!-- Back (mobile) -->
        <button
          @click="$emit('back')"
          class="md:hidden p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
  
        <!-- Avatar + nama -->
        <div
          class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold text-white shrink-0"
          :style="{ background: getAvatarColor(activeConv?.user_username) }"
        >
          {{ activeConv?.user_username?.charAt(0)?.toUpperCase() || '?' }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-slate-900 truncate">{{ activeConv?.user_username || '…' }}</p>
          <p class="text-xs text-slate-400">Customer</p>
        </div>
  
        <!-- Refresh -->
        <button
          @click="store.fetchInbox()"
          class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition"
          title="Refresh"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
  
      <!-- ── MESSAGES ────────────────────────────────────────────────── -->
      <div
        ref="scrollEl"
        class="flex-1 overflow-y-auto px-4 md:px-6 py-4 space-y-1 bg-slate-50"
        @scroll="onScroll"
      >
  
        <!-- Load more -->
        <div class="flex justify-center mb-3">
          <button
            v-if="store.hasMoreHistory && !store.loadingMore"
            @click="store.loadMoreHistory()"
            class="px-4 py-1.5 text-xs text-slate-500 bg-white border border-slate-200 hover:bg-slate-50 rounded-full transition font-medium shadow-sm"
          >
            ↑ Muat pesan lebih lama
          </button>
          <div v-if="store.loadingMore" class="flex items-center gap-2 text-xs text-slate-400">
            <svg class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            Memuat…
          </div>
        </div>
  
        <!-- Skeleton awal -->
        <template v-if="store.loadingMessages">
          <div v-for="i in 9" :key="i" class="flex gap-2.5 mb-3" :class="i % 3 === 0 ? 'flex-row-reverse' : ''">
            <div class="w-7 h-7 rounded-full bg-slate-200 animate-pulse shrink-0 self-end"></div>
            <div class="space-y-1.5 max-w-xs">
              <div class="h-10 rounded-2xl animate-pulse"
                :class="i % 3 === 0 ? 'bg-slate-300 w-44' : 'bg-slate-200 w-56'"></div>
            </div>
          </div>
        </template>
  
        <!-- Empty -->
        <div
          v-else-if="store.messages.length === 0"
          class="flex flex-col items-center justify-center py-16 text-slate-400"
        >
          <svg class="w-10 h-10 mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3v-3z" />
          </svg>
          <p class="text-sm">Belum ada pesan</p>
        </div>
  
        <!-- Messages list -->
        <template v-else>
          <template v-for="(msg, idx) in store.messages" :key="msg.uuid">
  
            <!-- Date divider -->
            <div v-if="showDateDivider(msg, idx)" class="flex items-center gap-3 my-4">
              <div class="flex-1 h-px bg-slate-200"></div>
              <span class="text-[11px] text-slate-400 font-medium px-2 bg-slate-50">
                {{ formatDateDivider(msg.sent_at) }}
              </span>
              <div class="flex-1 h-px bg-slate-200"></div>
            </div>
  
            <!-- Bubble wrapper -->
            <div
              class="flex gap-2.5 mb-1"
              :class="msg.sender_role === 'admin' ? 'flex-row-reverse' : 'flex-row'"
            >
              <!-- Avatar -->
              <div
                class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 self-end mb-0.5"
                :class="msg.sender_role === 'admin' ? 'bg-slate-900 text-white' : 'text-white'"
                :style="msg.sender_role !== 'admin' ? { background: getAvatarColor(activeConv?.user_username) } : {}"
              >
                {{ msg.sender_role === 'admin' ? 'A' : activeConv?.user_username?.charAt(0)?.toUpperCase() }}
              </div>
  
              <!-- Content -->
              <div class="max-w-[72%] space-y-1.5">
  
                <!-- ✅ Product context card (muncul jika pesan user embed metadata produk) -->
                <div
                  v-if="msg.sender_role === 'user' && getProductCtx(msg)"
                  class="bg-amber-50 border border-amber-200 rounded-2xl rounded-tl-sm px-3.5 py-3 shadow-sm"
                >
                  <p class="text-[10px] font-black text-amber-600 uppercase tracking-widest mb-2">
                    Tanya tentang produk
                  </p>
                  <div class="flex items-start gap-2.5">
                    <div class="flex-1 min-w-0 space-y-0.5">
                      <p class="text-sm font-bold text-slate-800 leading-tight">
                        {{ getProductCtx(msg).title }}
                      </p>
                      <p v-if="getProductCtx(msg).price" class="text-xs font-semibold text-emerald-700">
                        {{ getProductCtx(msg).price }}
                      </p>
                      <a
                        v-if="getProductCtx(msg).url"
                        :href="getProductCtx(msg).url"
                        target="_blank"
                        rel="noopener noreferrer"
                        @click.stop
                        class="inline-flex items-center gap-1 text-[11px] text-sky-600 hover:text-sky-700 font-medium mt-0.5 group"
                      >
                        Lihat produk
                        <svg class="w-3 h-3 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    </div>
                  </div>
                </div>
  
                <!-- ✅ Link produk biasa (jika tidak ada metadata embed, tapi ada URL produk di body) -->
                <div
                  v-else-if="msg.sender_role === 'user' && getProductLink(msg)"
                  class="bg-sky-50 border border-sky-200 rounded-2xl rounded-tl-sm px-3.5 py-3 shadow-sm"
                >
                  <p class="text-[10px] font-black text-sky-600 uppercase tracking-widest mb-1.5">
                    Link produk
                  </p>
                  <a
                    :href="getProductLink(msg).rawMatch"
                    target="_blank"
                    rel="noopener noreferrer"
                    @click.stop
                    class="inline-flex items-center gap-1 text-xs text-sky-700 hover:underline font-medium"
                  >
                    Buka halaman produk →
                  </a>
                </div>
  
                <!-- Images -->
                <div
                  v-if="msg.images?.length"
                  class="flex gap-1.5 flex-wrap"
                  :class="msg.sender_role === 'admin' ? 'justify-end' : ''"
                >
                  <img
                    v-for="img in msg.images"
                    :key="img.uuid"
                    :src="img.image_url"
                    @click="openLightbox(img.image_url)"
                    class="w-40 h-40 object-cover rounded-2xl cursor-pointer hover:opacity-90 transition border border-slate-200 shadow-sm"
                  />
                </div>
  
                <!-- Text bubble -->
                <div
                  v-if="getDisplayBody(msg)"
                  class="px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm whitespace-pre-wrap break-words"
                  :class="msg.sender_role === 'admin'
                    ? 'bg-slate-900 text-white rounded-tr-sm'
                    : 'bg-white border border-slate-200 text-slate-800 rounded-tl-sm'"
                >
                  {{ getDisplayBody(msg) }}
                </div>
  
                <!-- Timestamp + status -->
                <div
                  class="flex items-center gap-1.5 px-1"
                  :class="msg.sender_role === 'admin' ? 'justify-end' : ''"
                >
                  <span class="text-[10px] text-slate-400">{{ formatTime(msg.sent_at) }}</span>
  
                  <!-- Centang admin: abu = sent, biru = read -->
                  <template v-if="msg.sender_role === 'admin'">
                    <svg
                      class="w-3.5 h-3.5"
                      :class="msg.status === 'read' ? 'text-sky-400' : 'text-slate-300'"
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                    >
                      <path v-if="msg.status === 'read'"
                        stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
                        d="M4.5 12.75l4 4 9.5-9.5M9 12.75l4 4" />
                      <path v-else
                        stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
                        d="M4.5 12.75l4 4 9.5-9.5" />
                    </svg>
                  </template>
                </div>
              </div>
            </div>
  
          </template>
        </template>
  
        <!-- Anchor scroll bawah -->
        <div ref="bottomEl"></div>
      </div>
  
      <!-- ── INPUT AREA ─────────────────────────────────────────────── -->
      <div class="shrink-0 bg-white border-t border-slate-100 px-4 md:px-6 py-3">
  
        <!-- Preview gambar -->
        <div v-if="pendingImages.length > 0" class="flex gap-2 mb-2.5 flex-wrap">
          <div v-for="(img, i) in pendingImages" :key="i" class="relative group">
            <img :src="img.preview" class="w-14 h-14 object-cover rounded-xl border border-slate-200" />
            <button
              @click="removeImage(i)"
              class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-rose-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition text-[10px] font-bold shadow"
            >✕</button>
          </div>
        </div>
  
        <div class="flex items-end gap-2.5">
          <!-- Attach gambar -->
          <label class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition cursor-pointer shrink-0 self-center"
            :class="{ 'opacity-30 pointer-events-none': pendingImages.length >= 2 }"
            :title="pendingImages.length >= 2 ? 'Maks 2 gambar' : 'Lampirkan gambar'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
            <input type="file" accept="image/*" multiple class="hidden" @change="onFileChange" />
          </label>
  
          <!-- Textarea -->
          <textarea
            ref="textareaEl"
            v-model="inputText"
            @keydown.enter.exact.prevent="sendMessage"
            rows="1"
            placeholder="Ketik balasan…"
            class="flex-1 resize-none bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900/20 focus:border-slate-400 transition leading-relaxed max-h-36 overflow-y-auto"
            @input="autoResize"
          ></textarea>
  
          <!-- Send -->
          <button
            @click="sendMessage"
            :disabled="sending || (!inputText.trim() && pendingImages.length === 0)"
            class="p-2.5 rounded-xl transition shrink-0 self-center disabled:opacity-40 disabled:cursor-not-allowed"
            :class="inputText.trim() || pendingImages.length > 0
              ? 'bg-slate-900 text-white hover:bg-slate-700 active:scale-95'
              : 'bg-slate-100 text-slate-400'"
          >
            <svg v-if="!sending" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
          </button>
        </div>
  
        <p class="text-[11px] text-slate-400 mt-1.5 pl-12">
          Enter untuk kirim&nbsp;·&nbsp;Maks 2 gambar (5 MB)
        </p>
      </div>
  
      <!-- ── LIGHTBOX ────────────────────────────────────────────────── -->
      <Teleport to="body">
        <Transition name="fade">
          <div
            v-if="lightboxSrc"
            class="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4 cursor-zoom-out"
            @click="lightboxSrc = null"
          >
            <img
              :src="lightboxSrc"
              class="max-w-full max-h-full object-contain rounded-xl shadow-2xl"
              @click.stop
            />
            <button
              class="absolute top-4 right-4 w-9 h-9 bg-white/10 hover:bg-white/20 text-white rounded-full flex items-center justify-center transition"
              @click="lightboxSrc = null"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </Transition>
      </Teleport>
  
    </div>
  </template>
  
  <script setup>
  import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { useToastStore } from '@/stores/toast'
  import { useMessageStore, extractUserBody, parseProductContext, detectProductLink } from '@/stores/messageStore'
  
  defineEmits(['back'])
  
  const route = useRoute()
  const store = useMessageStore()
  const toastStore = useToastStore()
  
  const inputText     = ref('')
  const pendingImages = ref([])
  const sending       = ref(false)
  const scrollEl      = ref(null)
  const bottomEl      = ref(null)
  const textareaEl    = ref(null)
  const lightboxSrc   = ref(null)
  
  const convId = computed(() => route.params.id)
  
  const activeConv = computed(() =>
    store.conversations.find(c => c.uuid === convId.value)
  )
  
  // ── Buka conversation saat route berubah ──────────────────────────
  watch(convId, async (id) => {
    if (id) {
      await store.openConversation(id)
      await nextTick()
      scrollToBottom('instant')
    }
  }, { immediate: true })
  
  // ── Auto scroll saat pesan baru ───────────────────────────────────
  watch(() => store.messages.length, async (newLen, oldLen) => {
    if (newLen <= oldLen) return
    // Scroll hanya jika sudah di bawah
    if (!scrollEl.value) return
    const { scrollHeight, scrollTop, clientHeight } = scrollEl.value
    const nearBottom = scrollHeight - scrollTop - clientHeight < 200
    if (nearBottom) {
      await nextTick()
      scrollToBottom()
    }
  })
  
  function scrollToBottom(behavior = 'smooth') {
    bottomEl.value?.scrollIntoView({ behavior })
  }
  
  // Scroll ke atas → load more
  function onScroll(e) {
    if (e.target.scrollTop < 80 && store.hasMoreHistory && !store.loadingMore) {
      store.loadMoreHistory()
    }
  }
  
  // ── Helpers untuk render pesan ────────────────────────────────────
  
  /** Body bersih yang ditampilkan di bubble (strip metadata produk) */
  function getDisplayBody(msg) {
    if (msg.sender_role === 'user') return extractUserBody(msg.body)
    return msg.body || ''
  }
  
  /** Product context dari embed metadata (format FloatingChat) */
  function getProductCtx(msg) {
    if (msg.sender_role !== 'user') return null
    return parseProductContext(msg.body)
  }
  
  /** Fallback: deteksi URL produk di body mentah */
  function getProductLink(msg) {
    if (msg.sender_role !== 'user') return null
    // Jika sudah ada embed metadata, jangan tampil card ini
    if (parseProductContext(msg.body)) return null
    return detectProductLink(msg.body)
  }
  
  // ── Send ──────────────────────────────────────────────────────────
  async function sendMessage() {
    const body   = inputText.value.trim()
    const images = pendingImages.value.map(p => p.file)
  
    if (!body && images.length === 0) return
    if (images.length > 2) { toastStore.warning('Maksimal 2 gambar per pesan.'); return }
  
    sending.value = true
    try {
      await store.sendMessage(convId.value, body || null, images)
      inputText.value = ''
      pendingImages.value.forEach(p => URL.revokeObjectURL(p.preview))
      pendingImages.value = []
      if (textareaEl.value) textareaEl.value.style.height = 'auto'
      await nextTick()
      scrollToBottom()
    } catch (e) {
      toastStore.error('Gagal mengirim pesan.')
      console.error(e)
    } finally {
      sending.value = false
    }
  }
  
  // ── File input ────────────────────────────────────────────────────
  function onFileChange(e) {
    const files     = Array.from(e.target.files || [])
    const remaining = 2 - pendingImages.value.length
    files.slice(0, remaining).forEach(file => {
      pendingImages.value.push({ file, preview: URL.createObjectURL(file) })
    })
    e.target.value = ''
  }
  
  function removeImage(i) {
    URL.revokeObjectURL(pendingImages.value[i].preview)
    pendingImages.value.splice(i, 1)
  }
  
  function autoResize() {
    if (!textareaEl.value) return
    textareaEl.value.style.height = 'auto'
    textareaEl.value.style.height = textareaEl.value.scrollHeight + 'px'
  }
  
  function openLightbox(src) { lightboxSrc.value = src }
  
  // ── Avatar color ──────────────────────────────────────────────────
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
    return new Date(ts).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
  }
  
  function formatDateDivider(ts) {
    if (!ts) return ''
    const d   = new Date(ts)
    const now = new Date()
    if (d.toDateString() === now.toDateString()) return 'Hari ini'
    const yesterday = new Date(now)
    yesterday.setDate(now.getDate() - 1)
    if (d.toDateString() === yesterday.toDateString()) return 'Kemarin'
    return d.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  }
  
  function showDateDivider(msg, idx) {
    if (idx === 0) return true
    const prev = store.messages[idx - 1]
    return new Date(prev.sent_at).toDateString() !== new Date(msg.sent_at).toDateString()
  }
  
  onUnmounted(() => {
    pendingImages.value.forEach(p => URL.revokeObjectURL(p.preview))
  })
  </script>
  
  <style scoped>
  @reference "tailwindcss";
  
  .fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
  .fade-enter-from, .fade-leave-to       { opacity: 0; }
  
  div::-webkit-scrollbar       { width: 4px; }
  div::-webkit-scrollbar-track { background: transparent; }
  div::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 99px; }
  </style>