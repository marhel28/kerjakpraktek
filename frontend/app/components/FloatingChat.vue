<template>
  <aside
    ref="chatContainer"
    class="fixed bottom-6 right-6 z-[100] font-sans"
    :style="{ transform: `translate3d(${position.x}px, ${position.y}px, 0)` }"
    aria-label="Customer Support Chat"
  >
    <Transition
      enter-active-class="transition duration-300 ease-out transform origin-bottom-right"
      enter-from-class="scale-95 opacity-0 translate-y-4"
      enter-to-class="scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-200 ease-in transform origin-bottom-right"
      leave-from-class="scale-100 opacity-100 translate-y-0"
      leave-to-class="scale-95 opacity-0 translate-y-4"
    >
      <div
        v-if="isOpen"
        class="absolute bottom-20 right-0 w-[350px] sm:w-[380px] bg-white border border-gray-200 shadow-2xl rounded-2xl overflow-hidden flex flex-col h-[540px] max-h-[85vh]"
      >
        <!-- ── Header ─────────────────────────────────────────── -->
        <header
          class="bg-black text-white p-4 flex justify-between items-start cursor-move select-none shrink-0"
          @mousedown="onDragStart"
          @touchstart.passive="onDragStart"
        >
          <div class="flex gap-3 items-center pointer-events-none">
            <div
              class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center shrink-0 border border-white/20"
            >
              <Icon name="lucide:headset" class="w-5 h-5 text-white" />
            </div>
            <div class="flex flex-col">
              <span class="text-sm font-black uppercase tracking-widest italic"
                >PasarCctv Support</span
              >
              <span class="text-[10px] text-gray-400 font-medium"
                >Online • Siap Membantu</span
              >
              <div class="barcode-element-mini mt-1.5" />
            </div>
          </div>
          <button
            @click.stop="closeChat"
            class="text-gray-400 hover:text-white transition-colors p-1 pointer-events-auto"
            aria-label="Tutup Chat"
          >
            <Icon name="lucide:x" class="w-5 h-5" />
          </button>
        </header>

        <!-- ── Banner Produk ──────────────────────────────────── -->
        <!-- Muncul saat ada pendingContext yang belum dikirim -->
        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-[90px]"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 max-h-[90px]"
          leave-to-class="opacity-0 max-h-0"
        >
          <div
            v-if="showProductBanner"
            class="bg-amber-50 border-b border-amber-200 px-3 py-2.5 flex items-center gap-3 shrink-0 overflow-hidden"
          >
            <img
              v-if="store.pendingContext!.image"
              :src="store.pendingContext!.image"
              class="w-11 h-11 object-cover rounded-xl shrink-0 border border-amber-200 bg-white"
              :alt="store.pendingContext!.title"
            />
            <div class="flex-1 min-w-0">
              <p
                class="text-[9px] font-black text-amber-600 uppercase tracking-widest leading-none mb-0.5"
              >
                Tanya tentang produk
              </p>
              <p class="text-[12px] font-black text-gray-900 truncate leading-tight">
                {{ store.pendingContext!.brand ? store.pendingContext!.brand + ' ' : ''
                }}{{ store.pendingContext!.title }}
              </p>
              <p class="text-[11px] font-bold text-green-700 leading-tight">
                {{ formatPrice(store.pendingContext!.price) }}
              </p>
            </div>
            <button
              @click="dismissBanner"
              class="w-6 h-6 bg-amber-200 hover:bg-amber-300 rounded-full flex items-center justify-center shrink-0 transition-colors"
              title="Tutup"
              aria-label="Tutup banner produk"
            >
              <Icon name="lucide:x" class="w-3.5 h-3.5 text-amber-800" />
            </button>
          </div>
        </Transition>

        <!-- ── Messages Area ──────────────────────────────────── -->
        <main
          ref="messagesContainer"
          class="flex-1 overflow-y-auto p-4 bg-gray-50 flex flex-col gap-3 custom-scrollbar"
          @scroll="onScroll"
        >
          <!-- Load more -->
          <div class="text-center min-h-[24px]">
            <button
              v-if="store.hasMoreHistory && !store.isLoadingHistory"
              @click="loadMore"
              class="text-[10px] font-bold text-gray-400 uppercase tracking-widest hover:text-black transition-colors"
            >
              Muat pesan lebih lama ↑
            </button>
            <div v-else-if="store.isLoadingHistory" class="flex justify-center">
              <Icon name="lucide:loader-2" class="w-4 h-4 text-gray-300 animate-spin" />
            </div>
            <span
              v-else
              class="text-[10px] font-bold text-gray-300 uppercase tracking-widest"
            >
              Awal percakapan
            </span>
          </div>

          <!-- Initial loading skeleton -->
          <div
            v-if="store.isLoadingInitial"
            class="flex flex-col items-center justify-center flex-1 gap-2"
          >
            <Icon name="lucide:loader-2" class="w-6 h-6 text-gray-300 animate-spin" />
            <span class="text-[10px] text-gray-400 font-medium"
              >Memuat riwayat pesan...</span
            >
          </div>

          <!-- Welcome message (selalu tampil) -->
          <div v-if="!store.isLoadingInitial" class="flex gap-2 max-w-[85%] self-start">
            <div
              class="w-6 h-6 bg-black rounded-full flex items-center justify-center shrink-0 mt-1"
            >
              <Icon name="lucide:bot" class="w-3.5 h-3.5 text-white" />
            </div>
            <div
              class="bg-white border border-gray-200 p-3 rounded-2xl rounded-tl-sm shadow-sm"
            >
              <p class="text-xs font-medium text-gray-800 leading-relaxed">
                Halo! Selamat datang di <strong>PasarCctv</strong>.<br /><br />
                Silakan ketik pertanyaan Anda seputar produk, klaim garansi, atau kendala
                lainnya.
              </p>
            </div>
          </div>

          <!-- Messages list -->
          <template v-if="!store.isLoadingInitial">
            <div v-for="msg in store.messages" :key="msg.uuid" class="flex w-full">
              <!-- User bubble (kanan) -->
              <div
                v-if="msg.sender_role === 'user'"
                class="flex flex-col max-w-[85%] self-end ml-auto"
              >
                <div class="bg-black text-white p-3 rounded-2xl rounded-tr-sm shadow-sm">
                  <!-- Product context card di dalam bubble -->
                  <div
                    v-if="msg._productContext"
                    class="mb-2.5 bg-white/10 border border-white/20 rounded-xl p-2.5 flex gap-2.5 items-center"
                  >
                    <img
                      v-if="msg._productContext.image"
                      :src="msg._productContext.image"
                      class="w-10 h-10 object-cover rounded-lg shrink-0 bg-white/10"
                      :alt="msg._productContext.title"
                    />
                    <div class="min-w-0 flex-1">
                      <p
                        class="text-[9px] font-bold text-white/50 uppercase tracking-wider leading-none mb-0.5"
                      >
                        Tanya produk
                      </p>
                      <p class="text-[11px] font-bold text-white truncate">
                        {{
                          msg._productContext.brand
                            ? msg._productContext.brand + " "
                            : ""
                        }}{{ msg._productContext.title }}
                      </p>
                      <p class="text-[10px] font-semibold text-green-300">
                        {{ formatPrice(msg._productContext.price) }}
                      </p>
                      <a
                        :href="msg._productContext.url"
                        target="_blank"
                        rel="noopener"
                        class="text-[9px] text-blue-300 hover:text-blue-200 underline underline-offset-2"
                        >Lihat produk →</a
                      >
                    </div>
                  </div>

                  <!-- Body: strip metadata '---' sebelum render -->
                  <p
                    v-if="extractUserBody(msg.body)"
                    class="text-xs font-medium leading-relaxed whitespace-pre-wrap"
                  >
                    {{ extractUserBody(msg.body) }}
                  </p>

                  <!-- Gambar attachment -->
                  <div v-if="msg.images?.length" class="mt-2 flex gap-1.5 flex-wrap">
                    <img
                      v-for="img in msg.images"
                      :key="img.uuid"
                      :src="img.image_url"
                      class="w-24 h-24 object-cover rounded-xl cursor-pointer hover:opacity-90 transition-opacity"
                      @click="openLightbox(img.image_url)"
                    />
                  </div>
                </div>
                <div class="flex items-center justify-end gap-1 mt-1">
                  <span class="text-[9px] text-gray-400">{{
                    formatTime(msg.sent_at)
                  }}</span>
                  <Icon
                    v-if="msg.status === 'read'"
                    name="lucide:check-check"
                    class="w-3 h-3 text-blue-500"
                  />
                  <Icon v-else name="lucide:check" class="w-3 h-3 text-gray-400" />
                </div>
              </div>

              <!-- Admin bubble (kiri) -->
              <div v-else class="flex gap-2 max-w-[85%] self-start">
                <div
                  class="w-6 h-6 bg-black rounded-full flex items-center justify-center shrink-0 mt-1"
                >
                  <Icon name="lucide:headset" class="w-3.5 h-3.5 text-white" />
                </div>
                <div class="flex flex-col">
                  <div
                    class="bg-white border border-gray-200 p-3 rounded-2xl rounded-tl-sm shadow-sm"
                  >
                    <p
                      class="text-xs font-medium text-gray-800 leading-relaxed whitespace-pre-wrap"
                    >
                      {{ msg.body }}
                    </p>
                    <div v-if="msg.images?.length" class="mt-2 flex gap-1.5 flex-wrap">
                      <img
                        v-for="img in msg.images"
                        :key="img.uuid"
                        :src="img.image_url"
                        class="w-24 h-24 object-cover rounded-xl cursor-pointer hover:opacity-90 transition-opacity"
                        @click="openLightbox(img.image_url)"
                      />
                    </div>
                  </div>
                  <span class="text-[9px] text-gray-400 mt-1">{{
                    formatTime(msg.sent_at)
                  }}</span>
                </div>
              </div>
            </div>
          </template>

          <!-- Typing dots saat isSending -->
          <div v-if="store.isSending" class="flex gap-2 max-w-[85%] self-start">
            <div
              class="w-6 h-6 bg-black rounded-full flex items-center justify-center shrink-0 mt-1"
            >
              <Icon name="lucide:headset" class="w-3.5 h-3.5 text-white" />
            </div>
            <div
              class="bg-white border border-gray-200 px-4 py-3.5 rounded-2xl rounded-tl-sm shadow-sm"
            >
              <div class="flex gap-1 items-center">
                <span
                  class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                  style="animation-delay: 0ms"
                />
                <span
                  class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                  style="animation-delay: 150ms"
                />
                <span
                  class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                  style="animation-delay: 300ms"
                />
              </div>
            </div>
          </div>

          <div ref="bottomAnchor" class="h-0 w-full" />
        </main>

        <!-- ── Footer ─────────────────────────────────────────── -->
        <footer class="p-3 bg-white border-t border-gray-100 shrink-0">
          <!-- Belum login -->
          <div
            v-if="!isAuthenticated"
            class="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center"
          >
            <Icon name="lucide:lock" class="w-6 h-6 mx-auto mb-2 text-gray-400" />
            <p class="text-[11px] font-bold text-gray-600 mb-3 uppercase tracking-wider">
              Login untuk memulai percakapan
            </p>
            <NuxtLink
              to="/login"
              class="block w-full bg-black text-white py-2.5 text-[11px] font-black uppercase tracking-widest hover:bg-red-600 transition-colors rounded-lg"
            >
              Masuk Sekarang
            </NuxtLink>
          </div>

          <!-- Form kirim -->
          <div v-else class="flex flex-col gap-2">
            <!-- Preview gambar terpilih -->
            <div v-if="selectedImages.length" class="flex gap-2 flex-wrap">
              <div
                v-for="(img, i) in selectedImages"
                :key="i"
                class="relative w-14 h-14 rounded-xl overflow-hidden border-2 border-black"
              >
                <img
                  :src="img.preview"
                  class="w-full h-full object-cover"
                  :alt="`Preview ${i + 1}`"
                />
                <button
                  @click="removeImage(i)"
                  class="absolute top-0.5 right-0.5 w-4 h-4 bg-black text-white rounded-full text-[9px] flex items-center justify-center hover:bg-red-600"
                >
                  ✕
                </button>
              </div>
            </div>

            <div class="flex items-end gap-2">
              <!-- Attach -->
              <button
                type="button"
                :disabled="selectedImages.length >= 2"
                @click="imageInput?.click()"
                class="p-2 text-gray-400 hover:text-black transition-colors shrink-0 mb-0.5 disabled:opacity-30"
                :title="selectedImages.length >= 2 ? 'Maks 2 gambar' : 'Lampirkan gambar'"
              >
                <Icon name="lucide:paperclip" class="w-5 h-5" />
              </button>

              <input
                ref="imageInput"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                multiple
                class="hidden"
                @change="onImageSelected"
              />

              <!-- Textarea -->
              <div class="relative flex-1">
                <textarea
                  ref="textareaRef"
                  v-model="newMessage"
                  :placeholder="showProductBanner
                    ? `Tanya tentang ${store.pendingContext!.title}...`
                    : 'Ketik pesan...'"
                  rows="1"
                  class="w-full bg-white border-2 border-black rounded-2xl py-2.5 pl-4 pr-10 text-xs font-medium focus:outline-none resize-none custom-scrollbar"
                  style="max-height: 80px; overflow-y: auto"
                  @keydown.enter.exact.prevent="handleSend"
                  @input="autoResize"
                />
                <button
                  type="button"
                  :disabled="
                    (!newMessage.trim() && !selectedImages.length) || store.isSending
                  "
                  @click="handleSend"
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-black disabled:text-gray-300 transition-colors"
                >
                  <Icon
                    v-if="store.isSending"
                    name="lucide:loader-2"
                    class="w-4 h-4 animate-spin"
                  />
                  <Icon v-else name="lucide:send-horizonal" class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Transition>

    <!-- ── FAB Toggle ─────────────────────────────────────────── -->
    <button
      @mousedown="onDragStart"
      @touchstart.passive="onDragStart"
      @click="handleToggle"
      class="relative flex items-center justify-center w-14 h-14 bg-black text-white rounded-full shadow-[0_10px_40px_rgba(0,0,0,0.3)] hover:scale-110 hover:bg-zinc-800 transition-all duration-300 touch-none cursor-move ml-auto"
      :aria-expanded="isOpen"
      aria-label="Toggle Live Chat"
    >
      <Icon
        :name="isOpen ? 'lucide:x' : 'lucide:headset'"
        class="w-6 h-6 transition-transform duration-300 pointer-events-none"
        :class="isOpen ? 'rotate-90' : 'rotate-0'"
      />
      <span
        v-if="!isOpen && store.unreadCount > 0"
        class="absolute -top-1 -right-1 min-w-[20px] h-5 px-1.5 bg-red-600 text-white text-[10px] font-black rounded-full flex items-center justify-center border-2 border-white pointer-events-none"
        >{{ store.unreadCount > 9 ? "9+" : store.unreadCount }}</span
      >
    </button>

    <!-- ── Lightbox ───────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="lightboxUrl"
          class="fixed inset-0 z-[200] bg-black/85 flex items-center justify-center cursor-zoom-out"
          @click="lightboxUrl = null"
        >
          <img
            :src="lightboxUrl"
            class="max-w-[90vw] max-h-[90vh] rounded-xl object-contain shadow-2xl"
            @click.stop
          />
          <button
            class="absolute top-4 right-4 w-9 h-9 bg-white/10 hover:bg-white/20 text-white rounded-full flex items-center justify-center transition-colors"
            @click="lightboxUrl = null"
          >
            <Icon name="lucide:x" class="w-5 h-5" />
          </button>
        </div>
      </Transition>
    </Teleport>
  </aside>
</template>

<script setup lang="ts">
/**
 * components/FloatingChat.vue
 * ============================
 * Marketplace-grade floating chat. Diletakkan di layouts/default.vue.
 *
 * Auto-open flow (dari halaman produk):
 *   product/[uuid].vue:
 *     1. store.setPendingContext(ctx)  ← simpan info produk
 *     2. router.push('/')              ← navigasi ke home
 *   FloatingChat (di layout, sudah mounted):
 *     3. watch(store.pendingContext)   ← berubah = auto openChat()
 *     4. Banner kuning muncul di atas messages
 *     5. User ketik + kirim → ctx di-embed ke body, banner hilang
 */

import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { usePesanStore, type ProductContext } from '~/stores/UsePesanStore'

const store = usePesanStore()

// ── Auth ───────────────────────────────────────────────────────────
const authToken      = useCookie('token')
const isAuthenticated = computed(() => !!authToken.value)

// ── UI refs ────────────────────────────────────────────────────────
const isOpen            = ref(false)
const newMessage        = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const bottomAnchor      = ref<HTMLElement | null>(null)
const imageInput        = ref<HTMLInputElement | null>(null)
const textareaRef       = ref<HTMLTextAreaElement | null>(null)
const lightboxUrl       = ref<string | null>(null)
const selectedImages    = ref<{ file: File; preview: string }[]>([])

/**
 * bannerDismissed — user bisa nutup banner tanpa kirim.
 * Reset setiap kali pendingContext berubah ke produk baru.
 */
const bannerDismissed = ref(false)

/** Banner tampil jika: ada pendingContext DAN belum di-dismiss DAN konteks belum pernah dikirim */
const contextSentUuids = ref<Set<string>>(new Set())

const showProductBanner = computed(() =>
  !!store.pendingContext &&
  !bannerDismissed.value &&
  !contextSentUuids.value.has(store.pendingContext.uuid)
)

// ── Drag & drop ────────────────────────────────────────────────────
const position     = ref({ x: 0, y: 0 })
const isDragging   = ref(false)
const hasDragged   = ref(false)
const dragStartPos = { x: 0, y: 0 }

// ── Scroll load-more lock ──────────────────────────────────────────
let scrollLoadLock = false

// ── Helpers ────────────────────────────────────────────────────────
function formatPrice(value: number) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(value || 0).replace('Rp', 'Rp ')
}

function formatTime(dateString: string) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
}

/**
 * Ekstrak teks user: strip metadata produk '---' yang disisipkan ke body.
 * Bubble hanya tampil teks yang user ketik, bukan metadata untuk admin.
 */
function extractUserBody(body: string | null): string {
  if (!body) return ''
  const sep = body.indexOf('\n\n---\n')
  return sep !== -1 ? body.slice(0, sep).trim() : body.trim()
}

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 80) + 'px'
}

// ── Scroll ─────────────────────────────────────────────────────────
const onScroll = async () => {
  if (!messagesContainer.value || scrollLoadLock) return
  if (messagesContainer.value.scrollTop < 60 && store.hasMoreHistory) {
    scrollLoadLock = true
    const prevH = messagesContainer.value.scrollHeight
    await store.loadMoreHistory()
    await nextTick()
    if (messagesContainer.value)
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight - prevH
    scrollLoadLock = false
  }
}

const loadMore = async () => {
  if (!messagesContainer.value) return
  const prevH = messagesContainer.value.scrollHeight
  await store.loadMoreHistory()
  await nextTick()
  if (messagesContainer.value)
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight - prevH
}

const scrollToBottom = async (behavior: ScrollBehavior = 'smooth') => {
  await nextTick()
  bottomAnchor.value?.scrollIntoView({ behavior })
}

// Auto-scroll saat pesan baru masuk
watch(
  () => store.messages.length,
  async (newLen, oldLen) => {
    if (!isOpen.value || newLen <= oldLen) return
    const el = messagesContainer.value
    if (!el) return
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 150
    if (nearBottom) {
      scrollToBottom()
      if (store.unreadCount > 0) store.markAllRead()
    }
  }
)

// ── Open / Close ───────────────────────────────────────────────────
const openChat = async () => {
  isOpen.value = true
  store.onPopupOpen()
  await nextTick()
  scrollToBottom('instant')
  if (store.unreadCount > 0) store.markAllRead()
  await nextTick()
  textareaRef.value?.focus()
}

const closeChat = () => {
  isOpen.value = false
  store.onPopupClose()
}

/**
 * ✅ Watch pendingContext dari store.
 * Ketika halaman produk set context lalu navigate ke home,
 * store sudah berubah dan FloatingChat langsung bereaksi.
 */
watch(
  () => store.pendingContext,
  async (ctx, prevCtx) => {
    if (!ctx) return
    // Produk baru → reset dismiss flag
    if (ctx.uuid !== prevCtx?.uuid) {
      bannerDismissed.value = false
    }
    // Auto-open chat
    if (!isOpen.value) {
      await openChat()
    }
  }
)

const dismissBanner = () => {
  bannerDismissed.value = true
}

const handleToggle = (e: MouseEvent | TouchEvent) => {
  if (hasDragged.value) { e.preventDefault(); e.stopPropagation(); return }
  if (isOpen.value) closeChat()
  else openChat()
}

// ── Images ─────────────────────────────────────────────────────────
const onImageSelected = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  const slots = 2 - selectedImages.value.length
  Array.from(input.files).slice(0, slots).forEach(file => {
    selectedImages.value.push({ file, preview: URL.createObjectURL(file) })
  })
  input.value = ''
}

const removeImage = (i: number) => {
  URL.revokeObjectURL(selectedImages.value[i].preview)
  selectedImages.value.splice(i, 1)
}

const openLightbox = (url: string) => { lightboxUrl.value = url }

// ── Send ───────────────────────────────────────────────────────────
const handleSend = async () => {
  const bodyText = newMessage.value.trim()
  const files    = selectedImages.value.map(i => i.file)

  if (!bodyText && !files.length) return
  if (!isAuthenticated.value || store.isSending) return

  // Ambil konteks hanya jika banner aktif (belum dismiss & belum dikirim)
  const ctx = showProductBanner.value ? store.pendingContext : null

  /**
   * Embed metadata produk di bawah body sebagai teks terstruktur.
   * Admin membacanya di panel mereka (bisa diparse jadi card).
   * Format dipisah '---' supaya extractUserBody() bisa strip saat render bubble.
   */
  let finalBody = bodyText
  if (ctx) {
    const meta = [
      `\n\n---`,
      `🏷️ Produk: ${ctx.brand ? ctx.brand + ' ' : ''}${ctx.title}`,
      `💰 Harga: ${formatPrice(ctx.price)}`,
      `🆔 UUID: ${ctx.uuid}`,
      `🔗 URL: ${ctx.url}`,
    ].join('\n')
    finalBody = (bodyText + meta).trim()
  }

  const success = await store.sendMessage(finalBody, files, ctx ?? undefined)

  if (success) {
    newMessage.value = ''
    selectedImages.value.forEach(i => URL.revokeObjectURL(i.preview))
    selectedImages.value = []

    if (textareaRef.value) textareaRef.value.style.height = 'auto'

    // Tandai uuid ini sudah dikirim → banner tidak akan muncul lagi untuk produk ini
    if (ctx) {
      contextSentUuids.value.add(ctx.uuid)
      // Clear dari store supaya bersih
      store.clearPendingContext()
    }

    scrollToBottom()
  }
}

// ── Drag ───────────────────────────────────────────────────────────
const onDragStart = (e: MouseEvent | TouchEvent) => {
  if (e instanceof MouseEvent && e.button !== 0) return
  isDragging.value = true
  hasDragged.value = false
  const cx = e instanceof TouchEvent ? e.touches[0].clientX : e.clientX
  const cy = e instanceof TouchEvent ? e.touches[0].clientY : e.clientY
  dragStartPos.x = cx - position.value.x
  dragStartPos.y = cy - position.value.y
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('mouseup', onDragEnd)
  document.addEventListener('touchend', onDragEnd)
}

const onDrag = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return
  const cx = e instanceof TouchEvent ? e.touches[0].clientX : e.clientX
  const cy = e instanceof TouchEvent ? e.touches[0].clientY : e.clientY
  const nx = cx - dragStartPos.x
  const ny = cy - dragStartPos.y
  if (Math.abs(nx - position.value.x) > 3 || Math.abs(ny - position.value.y) > 3) {
    hasDragged.value = true
    if (e.cancelable) e.preventDefault()
  }
  position.value.x = nx
  position.value.y = ny
}

const onDragEnd = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('mouseup', onDragEnd)
  document.removeEventListener('touchend', onDragEnd)
}

// ── Lifecycle ──────────────────────────────────────────────────────
onMounted(() => {
  if (isAuthenticated.value) store.startPassivePolling()
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('mouseup', onDragEnd)
  document.removeEventListener('touchend', onDragEnd)
  selectedImages.value.forEach(i => URL.revokeObjectURL(i.preview))
})
</script>

<style scoped>
.barcode-element-mini {
  height: 4px;
  width: 40px;
  background: linear-gradient(90deg, #fff 6px, transparent 6px),
    repeating-linear-gradient(90deg, transparent 0, transparent 8px, #fff 8px, #fff 10px);
  background-repeat: no-repeat, repeat;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: #000;
}
</style>
