<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { usePesanStore } from '~/stores/UsePesanStore'

definePageMeta({ layout: "auth" });
useHead({ title: "Messenger — PasarCctv" });

const store = usePesanStore()
const authToken = useCookie('token')
const isAuthenticated = computed(() => !!authToken.value)

// ── UI state ─────────────────────────────────────────────────────
const newMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const bottomAnchor = ref<HTMLElement | null>(null)
const imageInput = ref<HTMLInputElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const lightboxUrl = ref<string | null>(null)
const selectedImages = ref<{ file: File; preview: string }[]>([])
const isAtBottom = ref(true)
const bannerDismissed = ref(false)
const contextSentUuids = ref<Set<string>>(new Set())

const tabs = [
  { label: "Biodata Diri", to: "/dashboard" },
  { label: "Daftar Alamat", to: "/dashboard/address" },
  { label: "Keamanan", to: "/dashboard/change-password" },
  { label: "Notifikasi", to: "/dashboard/notifications" },
  { label: "Pesanan Saya", to: "/dashboard/orders" },
  { label: "Layanan Jasa", to: "/dashboard/jasa" },
];

// ── Banner Logic ─────────────────────────────────────────────────
const showProductBanner = computed(() =>
  !!store.pendingContext &&
  !bannerDismissed.value &&
  !contextSentUuids.value.has(store.pendingContext.uuid)
)

// ── Logic: Message Grouping ──────────────────────────────────────
const groupedMessages = computed(() => {
  const groups: { date: string; messages: any[] }[] = []
  store.messages.forEach(msg => {
    const date = new Date(msg.sent_at).toLocaleDateString('id-ID', { 
      day: 'numeric', month: 'long', year: 'numeric' 
    })
    const lastGroup = groups[groups.length - 1]
    if (lastGroup && lastGroup.date === date) {
      lastGroup.messages.push(msg)
    } else {
      groups.push({ date, messages: [msg] })
    }
  })
  return groups
})

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
  return new Date(dateString).toLocaleTimeString('id-ID', { 
    hour: '2-digit', minute: '2-digit', hour12: false 
  })
}

function extractUserBody(body: string | null): string {
  if (!body) return ''
  const sep = body.indexOf('\n\n---\n')
  return sep !== -1 ? body.slice(0, sep).trim() : body.trim()
}

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 150) + 'px'
}

// ── Scrolling Logic ────────────────────────────────────────────────
const scrollToBottom = async (behavior: ScrollBehavior = 'smooth') => {
  await nextTick()
  if (bottomAnchor.value) {
    bottomAnchor.value.scrollIntoView({ behavior })
  }
}

const handleScroll = () => {
  if (!messagesContainer.value) return
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  isAtBottom.value = scrollHeight - scrollTop - clientHeight < 100
  
  if (scrollTop < 50 && store.hasMoreHistory && !store.isLoadingHistory) {
    const prevH = scrollHeight
    store.loadMoreHistory().then(() => {
      nextTick(() => {
        if (messagesContainer.value)
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight - prevH
      })
    })
  }
}

watch(() => store.messages.length, (newLen, oldLen) => {
  if (newLen > oldLen && isAtBottom.value) {
    scrollToBottom()
  }
})

// ── Actions ────────────────────────────────────────────────────────
const handleSend = async () => {
  const bodyText = newMessage.value.trim()
  const files = selectedImages.value.map(i => i.file)

  if (!bodyText && !files.length) return
  if (!isAuthenticated.value || store.isSending) return

  const ctx = showProductBanner.value ? store.pendingContext : null
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
    
    if (ctx) {
      contextSentUuids.value.add(ctx.uuid)
      store.clearPendingContext()
    }
    
    scrollToBottom()
  }
}

const onImageSelected = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  const limit = 4 - selectedImages.value.length
  Array.from(input.files).slice(0, limit).forEach(file => {
    selectedImages.value.push({ file, preview: URL.createObjectURL(file) })
  })
  input.value = ''
}

const removeImage = (i: number) => {
  URL.revokeObjectURL(selectedImages.value[i].preview)
  selectedImages.value.splice(i, 1)
}

const openLightbox = (url: string) => { lightboxUrl.value = url }

onMounted(async () => {
  if (isAuthenticated.value) {
    // Aktifkan mode chat (ambil history & set polling aktif)
    store.onPopupOpen()
    store.markAllRead()
    setTimeout(() => scrollToBottom('instant'), 100)
  }
})

onUnmounted(() => {
  selectedImages.value.forEach(i => URL.revokeObjectURL(i.preview))
  // Kembalikan ke mode pasif/idle
  store.onPopupClose()
})
</script>

<template>
  <div class="h-[calc(100vh-140px)] flex flex-col bg-white overflow-hidden rounded-xl border border-gray-200 shadow-sm relative">
    
    <!-- TABS (Marketplace style) -->
    <div class="border-b border-gray-200 overflow-x-auto no-scrollbar shrink-0 bg-white">
      <div class="flex px-4 sm:px-8">
        <NuxtLink
          v-for="tab in tabs"
          :key="tab.to"
          :to="tab.to"
          class="px-4 py-4 text-[11px] sm:text-sm font-bold whitespace-nowrap transition-colors relative"
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

    <!-- Messenger Header -->
    <header class="px-6 py-4 border-b border-gray-100 bg-white flex items-center justify-between shrink-0 z-10">
      <div class="flex items-center gap-4">
        <div class="relative">
          <div class="w-10 h-10 bg-[#03AC0E] rounded-full flex items-center justify-center text-white shadow-sm">
            <UIcon name="i-heroicons-headset" class="w-6 h-6" />
          </div>
          <div class="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-500 border-2 border-white rounded-full"></div>
        </div>
        <div>
          <h2 class="text-sm font-black text-gray-900 tracking-tight">Customer Service PasarCctv</h2>
          <p class="text-[10px] text-emerald-600 font-bold uppercase tracking-widest flex items-center gap-1">
            <span class="relative flex h-1.5 w-1.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
            </span>
            Online • Aktif
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button class="p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-50">
          <UIcon name="i-heroicons-phone" class="w-5 h-5" />
        </button>
        <button class="p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-50">
          <UIcon name="i-heroicons-information-circle" class="w-5 h-5" />
        </button>
      </div>
    </header>

    <!-- Product Banner -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="-translate-y-full opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="-translate-y-full opacity-0"
    >
      <div v-if="showProductBanner" class="absolute top-[110px] inset-x-0 z-20 bg-amber-50 border-b border-amber-100 px-6 py-3 flex items-center gap-4 shadow-sm">
        <div class="w-12 h-12 bg-white rounded-lg border border-amber-200 p-1 shrink-0 overflow-hidden">
          <img :src="store.pendingContext!.image" class="w-full h-full object-contain" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-[9px] font-black text-amber-600 uppercase tracking-widest leading-none mb-1">Menanyakan Produk</p>
          <h4 class="text-sm font-black text-gray-900 truncate leading-tight">{{ store.pendingContext!.title }}</h4>
          <p class="text-xs font-bold text-emerald-700 leading-tight">{{ formatPrice(store.pendingContext!.price) }}</p>
        </div>
        <button @click="bannerDismissed = true" class="p-2 text-amber-400 hover:text-amber-600 transition-colors">
          <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
        </button>
      </div>
    </Transition>

    <!-- Chat Area -->
    <main
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-6 flex flex-col gap-8 bg-[#f9fafb] custom-scrollbar scroll-smooth"
      @scroll="handleScroll"
    >
      <!-- History Loading Indicator -->
      <div v-if="store.isLoadingHistory" class="flex justify-center py-4">
        <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 text-gray-400 animate-spin" />
      </div>

      <!-- Messages Groups -->
      <template v-for="group in groupedMessages" :key="group.date">
        <!-- Date Separator -->
        <div class="flex items-center justify-center gap-4 my-2">
          <div class="h-px bg-gray-200 flex-1"></div>
          <span class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] px-2 bg-white rounded-full border border-gray-100 py-0.5">
            {{ group.date }}
          </span>
          <div class="h-px bg-gray-200 flex-1"></div>
        </div>

        <div v-for="(msg, idx) in group.messages" :key="msg.uuid" 
          class="flex flex-col group/msg"
          :class="[msg.sender_role === 'user' ? 'items-end' : 'items-start']"
        >
          <!-- Message Bubble Wrapper -->
          <div class="max-w-[85%] sm:max-w-[70%] flex gap-3"
            :class="[msg.sender_role === 'user' ? 'flex-row-reverse' : 'flex-row']"
          >
            <!-- Avatar for Admin -->
            <div v-if="msg.sender_role !== 'user'" class="w-8 h-8 rounded-full bg-black flex items-center justify-center shrink-0 mt-1 shadow-sm">
              <UIcon name="i-heroicons-headset" class="w-4 h-4 text-white" />
            </div>

            <div class="flex flex-col" :class="[msg.sender_role === 'user' ? 'items-end' : 'items-start']">
              <!-- Bubble -->
              <div 
                class="relative px-4 py-3 rounded-xl shadow-sm text-sm font-medium leading-relaxed"
                :class="[
                  msg.sender_role === 'user' 
                    ? 'bg-black text-white rounded-tr-none' 
                    : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none'
                ]"
              >
                <!-- Context Info in Bubble -->
                <div v-if="msg._productContext" class="mb-3 p-3 bg-white/10 rounded-xl border border-white/20 flex gap-3 items-center">
                   <div class="w-10 h-10 bg-white rounded-lg p-0.5 shrink-0 overflow-hidden">
                     <img :src="msg._productContext.image" class="w-full h-full object-contain" />
                   </div>
                   <div class="flex-1 min-w-0">
                     <p class="text-[9px] font-bold text-white/50 uppercase leading-none mb-1">Detail Produk</p>
                     <p class="text-[11px] font-bold text-white truncate leading-tight">{{ msg._productContext.title }}</p>
                     <p class="text-[10px] font-black text-green-300 leading-tight">{{ formatPrice(msg._productContext.price) }}</p>
                   </div>
                   <NuxtLink :to="msg._productContext.url" target="_blank" class="text-[10px] font-black text-blue-300 hover:underline shrink-0 px-2">LIHAT</NuxtLink>
                </div>

                <!-- Text Content -->
                <p class="whitespace-pre-wrap">{{ extractUserBody(msg.body) }}</p>

                <!-- Images Content -->
                <div v-if="msg.images?.length" class="mt-3 grid gap-2" :class="msg.images.length > 1 ? 'grid-cols-2' : 'grid-cols-1'">
                  <div 
                    v-for="img in msg.images" 
                    :key="img.uuid"
                    class="relative aspect-square rounded-xl overflow-hidden cursor-pointer hover:opacity-90 transition-opacity bg-gray-100 border border-black/5"
                    @click="openLightbox(img.image_url)"
                  >
                    <img :src="img.image_url" class="w-full h-full object-cover" />
                  </div>
                </div>
              </div>

              <!-- Meta: Time & Status -->
              <div class="flex items-center gap-2 mt-1.5 px-1 opacity-0 group-hover/msg:opacity-100 transition-opacity">
                <span class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">{{ formatTime(msg.sent_at) }}</span>
                <UIcon v-if="msg.sender_role === 'user'" 
                  :name="msg.status === 'read' ? 'i-heroicons-check-badge' : 'i-heroicons-check'" 
                  class="w-3.5 h-3.5" 
                  :class="msg.status === 'read' ? 'text-blue-500' : 'text-gray-300'" 
                />
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Typing Indicator -->
      <div v-if="store.isSending" class="flex gap-3 items-start max-w-[70%]">
        <div class="w-8 h-8 rounded-full bg-black flex items-center justify-center shrink-0 shadow-sm">
          <UIcon name="i-heroicons-ellipsis-horizontal" class="w-5 h-5 text-white" />
        </div>
        <div class="bg-white border border-gray-100 px-4 py-3 rounded-xl rounded-tl-none shadow-sm">
          <div class="flex gap-1.5 items-center h-4">
            <span class="w-1.5 h-1.5 bg-[#03AC0E] rounded-full animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-1.5 h-1.5 bg-[#03AC0E] rounded-full animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-1.5 h-1.5 bg-[#03AC0E] rounded-full animate-bounce" style="animation-delay: 300ms"></span>
          </div>
        </div>
      </div>

      <div ref="bottomAnchor" class="h-px w-full shrink-0" />
    </main>

    <!-- Footer Input -->
    <footer class="p-4 bg-white border-t border-gray-100 shrink-0">
      <div class="max-w-4xl mx-auto flex flex-col gap-3">
        <!-- Image Previews -->
        <TransitionGroup 
          tag="div" 
          v-if="selectedImages.length" 
          class="flex gap-3 px-2"
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="scale-90 opacity-0"
          enter-to-class="scale-100 opacity-100"
        >
          <div v-for="(img, i) in selectedImages" :key="img.preview" class="relative group">
            <div class="w-16 h-16 rounded-xl overflow-hidden border-2 border-[#03AC0E] shadow-sm">
              <img :src="img.preview" class="w-full h-full object-cover" />
            </div>
            <button 
              @click="removeImage(i)" 
              class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs shadow-md border-2 border-white hover:bg-red-600 transition-colors"
            >
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            </button>
          </div>
        </TransitionGroup>

        <!-- Input Bar -->
        <div class="flex items-end gap-3 px-2">
          <button
            @click="imageInput?.click()"
            class="p-2.5 text-gray-400 hover:text-[#03AC0E] transition-colors rounded-xl hover:bg-gray-50 shrink-0"
            :disabled="selectedImages.length >= 4"
            title="Kirim Gambar"
          >
            <UIcon name="i-heroicons-paper-clip" class="w-6 h-6" />
          </button>
          <input ref="imageInput" type="file" accept="image/*" multiple class="hidden" @change="onImageSelected" />

          <div class="relative flex-1 group">
            <textarea
              ref="textareaRef"
              v-model="newMessage"
              placeholder="Ketik pesan di sini..."
              rows="1"
              class="w-full bg-gray-50 border-2 border-transparent focus:border-[#03AC0E] focus:bg-white rounded-xl py-3 px-4 pr-12 text-sm font-medium focus:outline-none resize-none transition-all custom-scrollbar max-h-40"
              @keydown.enter.exact.prevent="handleSend"
              @input="autoResize"
            />
            <button
              @click="handleSend"
              :disabled="(!newMessage.trim() && !selectedImages.length) || store.isSending"
              class="absolute right-2 bottom-1.5 p-2 text-[#03AC0E] disabled:text-gray-300 transition-all hover:scale-110 active:scale-95"
            >
              <UIcon :name="store.isSending ? 'i-heroicons-arrow-path' : 'i-heroicons-paper-airplane'" 
                class="w-6 h-6" 
                :class="{'animate-spin': store.isSending}" 
              />
            </button>
          </div>
        </div>

        <p class="text-[9px] text-gray-400 font-bold uppercase tracking-widest text-center">
          Pesan Anda dienkripsi dan aman bersama PasarCctv
        </p>
      </div>
    </footer>

    <!-- Lightbox -->
    <Teleport to="body">
      <Transition 
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 backdrop-blur-0"
        enter-to-class="opacity-100 backdrop-blur-md"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100 backdrop-blur-md"
        leave-to-class="opacity-0 backdrop-blur-0"
      >
        <div v-if="lightboxUrl" class="fixed inset-0 z-[500] bg-black/90 flex items-center justify-center p-4" @click="lightboxUrl = null">
          <img :src="lightboxUrl" class="max-w-full max-h-full object-contain rounded-lg shadow-2xl" />
          <button class="absolute top-6 right-6 text-white/50 hover:text-white p-2 transition-colors">
            <UIcon name="i-heroicons-x-mark" class="w-10 h-10" />
          </button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 10px; }
.custom-scrollbar:hover::-webkit-scrollbar-thumb { background: #d1d5db; }
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

@keyframes bubble-in {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
.group\/msg {
  animation: bubble-in 0.2s ease-out;
}
</style>
