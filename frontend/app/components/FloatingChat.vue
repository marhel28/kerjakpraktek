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
          class="bg-[#0D1B12] text-white p-4 flex justify-between items-start cursor-move select-none shrink-0"
          @mousedown="onDragStart"
          @touchstart.passive="onDragStart"
        >
          <div class="flex gap-3 items-center pointer-events-none">
            <div
              v-if="activeTab === 'bot'"
              class="w-10 h-10 bg-[#03AC0E]/20 rounded-full flex items-center justify-center shrink-0 border border-[#03AC0E]/30"
            >
              <Icon name="lucide:bot" class="w-5 h-5 text-[#03AC0E]" />
            </div>
            <div
              v-else
              class="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center shrink-0 border border-white/20"
            >
              <Icon name="lucide:headset" class="w-5 h-5 text-white" />
            </div>
            <div class="flex flex-col">
              <span class="text-sm font-medium tracking-wide uppercase italic text-white"
                >{{ activeTab === 'bot' ? 'PasarBot AI' : 'Pesan Admin' }}</span
              >
              <span class="text-[10px] text-gray-300 font-normal"
                >{{ activeTab === 'bot' ? 'Online • Jawaban Instan' : 'Online • Siap Membantu' }}</span
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

        <!-- ── Segmented Tab (Forest Green Style) ──────────────── -->
        <div class="bg-gray-50 p-1 flex border-b border-gray-200 shrink-0">
          <button
            @click="activeTab = 'bot'"
            class="flex-1 text-center py-2 text-xs font-medium rounded-lg transition-all duration-200"
            :class="activeTab === 'bot' ? 'bg-[#0D1B12] text-white shadow-sm' : 'text-gray-600 hover:bg-gray-150'"
          >
            <Icon name="lucide:sparkles" class="w-3.5 h-3.5 inline-block mr-1.5 -mt-0.5" />
            PasarBot AI
          </button>
          <button
            @click="activeTab = 'admin'"
            class="flex-1 text-center py-2 text-xs font-medium rounded-lg transition-all duration-200 relative"
            :class="activeTab === 'admin' ? 'bg-[#0D1B12] text-white shadow-sm' : 'text-gray-600 hover:bg-gray-150'"
          >
            <Icon name="lucide:user" class="w-3.5 h-3.5 inline-block mr-1.5 -mt-0.5" />
            Tanya Admin
            <span
              v-if="store.unreadCount > 0"
              class="absolute top-1.5 right-2 w-2 h-2 bg-red-600 rounded-full"
            />
          </button>
        </div>

        <!-- ── Banner Produk (Hanya untuk Tanya Admin) ────────── -->
        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-[90px]"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 max-h-[90px]"
          leave-to-class="opacity-0 max-h-0"
        >
          <div
            v-if="activeTab === 'admin' && showProductBanner"
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

        <!-- ── Messages Area ─────────────────────────────────────── -->
        <!-- TAB 1: Chatbot (PasarBot AI) -->
        <main
          v-if="activeTab === 'bot'"
          ref="messagesContainer"
          class="flex-1 overflow-y-auto p-4 bg-gray-50 flex flex-col gap-3 custom-scrollbar"
        >
          <div v-for="msg in chatbotStore.messages" :key="msg.uuid" class="flex flex-col w-full">
            <!-- User bubble (kanan) -->
            <div
              v-if="msg.role === 'user'"
              class="flex flex-col max-w-[85%] self-end ml-auto"
            >
              <div class="bg-[#0D1B12] text-white px-3.5 py-2.5 rounded-2xl rounded-tr-sm shadow-sm">
                <p class="text-xs leading-relaxed whitespace-pre-wrap">{{ msg.content }}</p>
              </div>
              <span class="text-[9px] text-gray-400 mt-1 self-end">{{ formatTime(msg.sent_at) }}</span>
            </div>

            <!-- Bot bubble (kiri) -->
            <div v-else class="flex gap-2 max-w-[90%] self-start">
              <div class="w-7 h-7 bg-[#03AC0E] rounded-full flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                <Icon name="lucide:bot" class="w-4 h-4 text-white" />
              </div>
              <div class="flex flex-col flex-1 min-w-0">
                <!-- Main reply bubble -->
                <div class="bg-white border border-gray-200 px-3.5 py-2.5 rounded-2xl rounded-tl-sm shadow-sm">
                  <p
                    class="text-xs text-gray-800 leading-relaxed"
                    v-html="renderMarkdown(msg.content)"
                  />

                  <!-- Quick Action: CS Handoff in Welcome Message -->
                  <div v-if="msg.uuid === 'welcome-msg-bot'" class="mt-3 pt-3 border-t border-gray-150 flex flex-col gap-2">
                    <div class="bg-[#03AC0E]/5 border border-[#03AC0E]/20 rounded-xl p-2.5 flex items-center justify-between gap-3">
                      <div class="flex-1 min-w-0">
                        <p class="text-[11px] font-bold text-[#0D1B12]">Butuh bantuan manusia? 📞</p>
                        <p class="text-[10px] text-gray-500 leading-tight">Hubungi tim Customer Service / Admin kami secara langsung.</p>
                      </div>
                      <button
                        @click="handleCSRequest"
                        class="bg-[#0D1B12] hover:bg-[#03AC0E] text-white text-[10px] font-extrabold px-3 py-2 rounded-lg transition-all shrink-0 uppercase tracking-wider active:scale-95"
                      >
                        Hubungi CS
                      </button>
                    </div>
                  </div>

                  <!-- ── Product Cards (RAG Recommendations) ─────── -->
                  <div
                    v-if="msg.products && msg.products.length"
                    class="mt-3 pt-3 border-t border-gray-100"
                  >
                    <p class="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-2">Produk Terkait</p>
                    <div class="flex flex-col gap-2">
                      <div
                        v-for="prod in msg.products.slice(0, 4)"
                        :key="prod.uuid"
                        class="flex gap-2.5 items-center bg-gray-50 hover:bg-[#03AC0E]/5 border border-gray-150 hover:border-[#03AC0E]/30 rounded-xl p-2 transition-all duration-200 cursor-pointer group"
                        @click="navigateTo(`/product/${prod.uuid}`)"
                      >
                        <!-- Thumbnail -->
                        <div class="w-11 h-11 rounded-lg overflow-hidden shrink-0 bg-gray-100 border border-gray-200">
                          <img
                            v-if="prod.image"
                            :src="prod.image"
                            :alt="prod.title"
                            class="w-full h-full object-cover"
                          />
                          <div v-else class="w-full h-full flex items-center justify-center">
                            <Icon name="lucide:camera" class="w-4 h-4 text-gray-300" />
                          </div>
                        </div>

                        <!-- Info -->
                        <div class="flex-1 min-w-0">
                          <p class="text-[8px] font-bold text-[#03AC0E] uppercase tracking-wider leading-none mb-0.5">
                            {{ prod.brand || 'NO BRAND' }}
                          </p>
                          <p class="text-[11px] font-semibold text-gray-900 leading-snug truncate">
                            {{ prod.title }}
                          </p>
                          <div class="flex items-center gap-1.5 mt-0.5">
                            <span class="text-[11px] font-bold text-[#028C0B]">{{ formatPrice(prod.price) }}</span>
                            <span
                              v-if="prod.discount_percentage"
                              class="text-[8px] bg-red-50 text-red-600 border border-red-100 px-1.5 py-0.5 rounded-full font-bold"
                            >
                              -{{ prod.discount_percentage }}%
                            </span>
                          </div>
                        </div>

                        <!-- CTA Arrow -->
                        <Icon
                          name="lucide:chevron-right"
                          class="w-4 h-4 text-gray-300 group-hover:text-[#03AC0E] transition-colors shrink-0"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ── Timestamp ─────────────────────────────────── -->
                <span class="text-[9px] text-gray-400 mt-1 ml-0.5">{{ formatTime(msg.sent_at) }}</span>

                <!-- ── Feedback Bar ───────────────────────────────── -->
                <div
                  v-if="msg.uuid !== 'welcome-msg-bot' && msg.feedback === null"
                  class="flex items-center gap-2 mt-1.5"
                >
                  <span class="text-[9px] text-gray-400">Apakah ini membantu?</span>
                  <button
                    @click="handleFeedback(msg, true)"
                    class="flex items-center gap-1 text-[9px] text-gray-400 hover:text-green-600 transition-colors px-1.5 py-0.5 rounded-full hover:bg-green-50"
                    title="Ya, membantu"
                  >
                    <Icon name="lucide:thumbs-up" class="w-3 h-3" />
                    <span>Ya</span>
                  </button>
                  <button
                    @click="handleFeedback(msg, false)"
                    class="flex items-center gap-1 text-[9px] text-gray-400 hover:text-red-500 transition-colors px-1.5 py-0.5 rounded-full hover:bg-red-50"
                    title="Tidak membantu"
                  >
                    <Icon name="lucide:thumbs-down" class="w-3 h-3" />
                    <span>Tidak</span>
                  </button>
                </div>

                <!-- Feedback submitted confirmation -->
                <div
                  v-else-if="msg.uuid !== 'welcome-msg-bot' && msg.feedback === 'satisfied'"
                  class="flex items-center gap-1 mt-1.5 text-[9px] text-green-600"
                >
                  <Icon name="lucide:check-circle" class="w-3 h-3" />
                  <span>Terima kasih! 😊</span>
                </div>

                <!-- ── Escalation Panel ───────────────────────────── -->
                <Transition
                  enter-active-class="transition-all duration-300 ease-out"
                  enter-from-class="opacity-0 translate-y-1"
                  enter-to-class="opacity-100 translate-y-0"
                >
                  <div
                    v-if="(msg.needs_escalation || msg.feedback === 'unsatisfied') && msg.uuid !== 'welcome-msg-bot'"
                    class="mt-2 bg-amber-50 border border-amber-200 rounded-xl p-3"
                  >
                    <p class="text-[11px] font-semibold text-amber-800 mb-1.5">
                      Butuh bantuan lebih lanjut?
                    </p>
                    <p class="text-[10px] text-amber-700 mb-2.5 leading-relaxed">
                      Tim Admin kami siap membantu Kakak secara langsung.
                    </p>
                    <button
                      @click="handleEscalate(msg)"
                      :disabled="chatbotStore.isEscalating"
                      class="w-full bg-[#03AC0E] hover:bg-[#028C0B] disabled:opacity-60 text-white text-[11px] font-bold py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5"
                    >
                      <Icon v-if="chatbotStore.isEscalating" name="lucide:loader-2" class="w-3.5 h-3.5 animate-spin" />
                      <Icon v-else name="lucide:headset" class="w-3.5 h-3.5" />
                      {{ chatbotStore.isEscalating ? 'Meneruskan...' : 'Teruskan ke Admin' }}
                    </button>
                  </div>
                </Transition>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="chatbotStore.isSending" class="flex gap-2 max-w-[85%] self-start">
            <div class="w-7 h-7 bg-[#03AC0E] rounded-full flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
              <Icon name="lucide:bot" class="w-4 h-4 text-white" />
            </div>
            <div class="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm">
              <div class="flex gap-1 items-center">
                <span class="w-1.5 h-1.5 bg-[#03AC0E]/60 rounded-full animate-bounce" style="animation-delay: 0ms" />
                <span class="w-1.5 h-1.5 bg-[#03AC0E]/60 rounded-full animate-bounce" style="animation-delay: 120ms" />
                <span class="w-1.5 h-1.5 bg-[#03AC0E]/60 rounded-full animate-bounce" style="animation-delay: 240ms" />
              </div>
            </div>
          </div>
          <div ref="bottomAnchor" class="h-0 w-full" />
        </main>

        <!-- TAB 2: Live Support Admin -->
        <main
          v-else
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
              <Icon name="lucide:headset" class="w-3.5 h-3.5 text-white" />
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
          <!-- Belum login (hanya untuk tab admin) -->
          <div
            v-if="activeTab === 'admin' && !isAuthenticated"
            class="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center"
          >
            <Icon name="lucide:lock" class="w-6 h-6 mx-auto mb-2 text-gray-400" />
            <p class="text-[11px] font-bold text-gray-600 mb-3 uppercase tracking-wider">
              Login untuk Tanya Admin
            </p>
            <NuxtLink
              to="/login"
              class="block w-full bg-black text-white py-2.5 text-[11px] font-black uppercase tracking-widest hover:bg-[#03AC0E] transition-colors rounded-lg"
            >
              Masuk Sekarang
            </NuxtLink>
          </div>

          <!-- Form kirim (untuk tab bot, ATAU tab admin saat sudah login) -->
          <div v-else class="flex flex-col gap-2">
            <!-- Autocomplete Suggestions (Hanya untuk PasarBot AI) -->
            <div v-if="activeTab === 'bot'" class="relative shrink-0">
              <!-- Gradient fade kanan: tanda ada konten lebih -->
              <div
                class="pointer-events-none absolute right-0 top-0 bottom-1.5 w-8 bg-gradient-to-l from-white to-transparent z-10"
              />
              <div
                ref="suggestionsScrollRef"
                class="flex gap-2 overflow-x-auto pb-1.5 px-0.5 scroll-smooth suggestions-scroll"
                style="-webkit-overflow-scrolling: touch; scroll-behavior: smooth;"
              >
                <!-- CS Help Button -->
                <button
                  @click="handleCSRequest"
                  class="bg-amber-50 hover:bg-amber-100 border border-amber-200 text-amber-800 text-[11px] font-black px-3.5 py-1.5 rounded-full shrink-0 transition-all shadow-sm flex items-center gap-1 active:scale-95"
                >
                  <Icon name="lucide:headset" class="w-3.5 h-3.5 animate-pulse" />
                  Customer Service 📞
                </button>

                <button
                  v-for="sug in chatbotStore.suggestions"
                  :key="sug"
                  @click="sendSuggestion(sug)"
                  class="bg-[#03AC0E]/5 hover:bg-[#03AC0E]/10 border border-[#03AC0E]/20 text-[#0D1B12] hover:text-[#03AC0E] text-[11px] font-bold px-3 py-1.5 rounded-full shrink-0 transition-all shadow-sm max-w-[200px] truncate active:scale-95"
                >
                  {{ sug }}
                </button>
              </div>
            </div>

            <!-- Preview gambar terpilih (hanya untuk Tanya Admin) -->
            <div v-if="activeTab === 'admin' && selectedImages.length" class="flex gap-2 flex-wrap">
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
              <!-- Attach (hanya untuk Tanya Admin) -->
              <button
                v-if="activeTab === 'admin'"
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
                  :placeholder="activeTab === 'bot'
                    ? 'Tanya PasarBot AI...'
                    : (showProductBanner ? `Tanya tentang ${store.pendingContext!.title}...` : 'Ketik pesan...')"
                  rows="1"
                  class="w-full bg-white border-2 border-black rounded-2xl py-2.5 pl-4 pr-10 text-xs font-medium focus:outline-none resize-none custom-scrollbar"
                  style="max-height: 80px; overflow-y: auto"
                  @keydown.enter.exact.prevent="handleSend"
                  @input="autoResize"
                />
                <button
                  type="button"
                  :disabled="
                    (!newMessage.trim() && (activeTab === 'bot' || !selectedImages.length)) || 
                    (activeTab === 'admin' ? store.isSending : chatbotStore.isSending)
                  "
                  @click="handleSend"
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-black disabled:text-gray-300 transition-colors"
                >
                  <Icon
                    v-if="activeTab === 'admin' ? store.isSending : chatbotStore.isSending"
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
      class="relative flex items-center justify-center w-14 h-14 bg-[#03AC0E] text-white rounded-full shadow-[0_10px_40px_rgba(3,172,14,0.35)] hover:scale-110 hover:bg-[#028C0B] transition-all duration-300 touch-none cursor-move ml-auto"
      :aria-expanded="isOpen"
      aria-label="Toggle Live Chat"
    >
      <Icon
        :name="isOpen ? 'lucide:x' : 'lucide:message-circle'"
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
 * Updated to support both Live Support Admin and PasarBot AI (RAG).
 */

import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { usePesanStore } from '~/stores/UsePesanStore'
import { useChatbotStore } from '~/stores/UseChatbotStore'

const store = usePesanStore()
const chatbotStore = useChatbotStore()

// ── Active Tab ─────────────────────────────────────────────────────
const activeTab = ref<'bot' | 'admin'>('bot')

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
const lightboxUrl          = ref<string | null>(null)
const selectedImages       = ref<{ file: File; preview: string }[]>([])
const suggestionsScrollRef = ref<HTMLElement | null>(null)

/**
 * bannerDismissed — user bisa nutup banner tanpa kirim.
 */
const bannerDismissed = ref(false)

/** Banner tampil jika: ada pendingContext DAN belum di-dismiss DAN konteks belum pernah dikirim */
const contextSentUuids = ref<Set<string>>(new Set())

const showProductBanner = computed(() =>
  activeTab.value === 'admin' &&
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
 * Basic markdown parser to render bold text and links properly.
 */
function renderMarkdown(text: string | null): string {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br />')
}

/**
 * Ekstrak teks user: strip metadata produk '---' yang disisipkan ke body.
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
  if (activeTab.value !== 'admin') return
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
    if (!isOpen.value || activeTab.value !== 'admin' || newLen <= oldLen) return
    const el = messagesContainer.value
    if (!el) return
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 150
    if (nearBottom) {
      scrollToBottom()
      if (store.unreadCount > 0) store.markAllRead()
    }
  }
)

watch(
  () => chatbotStore.messages.length,
  async (newLen, oldLen) => {
    if (!isOpen.value || activeTab.value !== 'bot' || newLen <= oldLen) return
    scrollToBottom()
  }
)

// Watch activeTab changes to init corresponding stores
watch(activeTab, async (newTab) => {
  if (newTab === 'bot') {
    chatbotStore.init()
  } else {
    store.onPopupOpen()
    if (store.unreadCount > 0) store.markAllRead()
  }
  await nextTick()
  scrollToBottom('instant')
  newMessage.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
})

// ── Open / Close ───────────────────────────────────────────────────
const openChat = async () => {
  isOpen.value = true
  if (activeTab.value === 'bot') {
    chatbotStore.init()
  } else {
    store.onPopupOpen()
    if (store.unreadCount > 0) store.markAllRead()
  }
  await nextTick()
  scrollToBottom('instant')
  await nextTick()
  textareaRef.value?.focus()
}

const closeChat = () => {
  isOpen.value = false
  if (activeTab.value === 'admin') {
    store.onPopupClose()
  }
}

/**
 * Watch pendingContext dari store.
 */
watch(
  () => store.pendingContext,
  async (ctx, prevCtx) => {
    if (!ctx) return
    if (ctx.uuid !== prevCtx?.uuid) {
      bannerDismissed.value = false
    }
    // Switch to admin tab if we get a product context to query human support
    activeTab.value = 'admin'
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
  if (activeTab.value !== 'admin') return
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

// ── Autocomplete / Suggestions ─────────────────────────────────────
let suggestionsTimeout: any = null

watch(
  [newMessage, activeTab, isOpen],
  ([newVal, newTab, open]) => {
    if (newTab === 'bot' && open) {
      clearTimeout(suggestionsTimeout)
      suggestionsTimeout = setTimeout(() => {
        chatbotStore.fetchSuggestions(newVal)
      }, 150)
    }
  },
  { immediate: true }
)

const sendSuggestion = async (sug: string) => {
  if (chatbotStore.isSending) return
  newMessage.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  await chatbotStore.sendMessage(sug)
  await chatbotStore.fetchSuggestions('')
  scrollToBottom()
}

// ── Send ───────────────────────────────────────────────────────────
const handleSend = async () => {
  const bodyText = newMessage.value.trim()
  
  if (activeTab.value === 'bot') {
    if (!bodyText || chatbotStore.isSending) return
    newMessage.value = ''
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
    await chatbotStore.sendMessage(bodyText)
    scrollToBottom()
  } else {
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
}

// ── Feedback & Escalation ──────────────────────────────────────────
const handleFeedback = async (msg: any, satisfied: boolean) => {
  // Optimistic UI update happens inside store
  const lastUserMsg = [...chatbotStore.messages]
    .reverse()
    .find(m => m.role === 'user' && m.uuid !== 'welcome-msg-bot')

  await chatbotStore.submitFeedback(
    msg.uuid,
    satisfied,
    lastUserMsg?.content,
    msg.knowledge_uuid
  )

  // If thumbs down → escalation panel will show via msg.feedback === 'unsatisfied'
}

const handleEscalate = async (msg: any) => {
  if (!isAuthenticated.value) {
    // User is not logged in: show guidance and switch tab
    chatbotStore.messages.push({
      uuid: 'cs-rep-' + Math.random().toString(36).substr(2, 6),
      role: 'model',
      content: 'Tentu Kak! Untuk tersambung ke layanan Customer Service / Admin kami, Kakak perlu **login/masuk** terlebih dahulu. Saya alihkan ke tab **Tanya Admin** ya Kak.',
      sent_at: new Date().toISOString(),
      feedback: null,
    } as any)
    
    scrollToBottom()
    setTimeout(() => {
      activeTab.value = 'admin'
      scrollToBottom('smooth')
    }, 2000)
    return
  }

  const lastUserMsg = [...chatbotStore.messages]
    .reverse()
    .find(m => m.role === 'user')

  const escalateMsg = await chatbotStore.escalateToAdmin(lastUserMsg?.content)

  // Add system message in bot tab
  chatbotStore.messages.push({
    uuid: 'escalated-' + Math.random().toString(36).substr(2, 6),
    role: 'model',
    content: escalateMsg,
    sent_at: new Date().toISOString(),
    feedback: null,
  } as any)

  // Switch to Admin tab after short delay
  setTimeout(async () => {
    activeTab.value = 'admin'
    await nextTick()
    scrollToBottom('smooth')
  }, 1200)
}

const handleCSRequest = async () => {
  if (isAuthenticated.value) {
    // User is logged in: add message and escalate
    chatbotStore.messages.push({
      uuid: 'cs-req-' + Math.random().toString(36).substr(2, 6),
      role: 'user',
      content: 'Saya butuh bantuan Customer Service / Admin.',
      sent_at: new Date().toISOString(),
    } as any)
    scrollToBottom()
    await handleEscalate({ uuid: 'cs-esc' })
  } else {
    // User is not logged in: show guidance and switch tab
    chatbotStore.messages.push({
      uuid: 'cs-req-' + Math.random().toString(36).substr(2, 6),
      role: 'user',
      content: 'Saya butuh bantuan Customer Service / Admin.',
      sent_at: new Date().toISOString(),
    } as any)
    
    chatbotStore.messages.push({
      uuid: 'cs-rep-' + Math.random().toString(36).substr(2, 6),
      role: 'model',
      content: 'Tentu Kak! Untuk tersambung ke layanan Customer Service / Admin kami, Kakak perlu **login/masuk** terlebih dahulu. Saya alihkan ke tab **Tanya Admin** ya Kak.',
      sent_at: new Date().toISOString(),
      feedback: null,
    } as any)
    
    scrollToBottom()
    setTimeout(() => {
      activeTab.value = 'admin'
      scrollToBottom('smooth')
    }, 2000)
  }
}


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

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Suggestions scroll - scrollbar tipis yang muncul saat hover */
.suggestions-scroll::-webkit-scrollbar {
  height: 3px;
}
.suggestions-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.suggestions-scroll::-webkit-scrollbar-thumb {
  background-color: transparent;
  border-radius: 10px;
  transition: background-color 0.2s;
}
.suggestions-scroll:hover::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
}
.suggestions-scroll {
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}
.suggestions-scroll:hover {
  scrollbar-color: #d1d5db transparent;
}
</style>
