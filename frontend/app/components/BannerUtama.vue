<template>
  <section
    id="hero-banner"
    class="w-full relative  overflow-hidden group"
    aria-roledescription="carousel"
    @mouseenter="pauseAutoplay"
    @mouseleave="resumeAutoplay"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
  >
    <div class="relative w-full aspect-[21/9] sm:aspect-[16/9] lg:aspect-[21/7] xl:aspect-[1920/600] overflow-hidden">
      
      <div v-if="pending" class="absolute inset-0 bg-neutral-200 z-20 animate-pulse" />

      <div 
        v-if="extendedSlides.length > 0"
        class="flex w-full h-full will-change-transform touch-pan-y"
        :class="{ 'transition-transform duration-500 ease-out': isTransitioning }"
        :style="{ transform: `translateX(-${activeIndex * 100}%)` }"
        @transitionend="onTransitionEnd"
      >
        <div 
          v-for="(slide, index) in extendedSlides" 
          :key="slide._key"
          class="w-full h-full flex-shrink-0 relative"
          :aria-hidden="realActiveIndex !== getRealIndex(index)"
        >
          <NuxtLink :to="slide.link" class="block w-full h-full focus:outline-none">
            <NuxtImg
              :src="slide.image"
              :alt="slide.title"
              class="w-full h-full object-cover"
              width="1920"
              height="600"
              format="webp"
              quality="90"
              sizes="100vw sm:100vw md:100vw"
              :loading="isPriority(index) ? 'eager' : 'lazy'"
              :fetchpriority="isPriority(index) ? 'high' : 'auto'"
              :preload="isPriority(index)"
            />
          </NuxtLink>
        </div>
      </div>

      <div v-if="total > 1" class="absolute bottom-0 inset-x-0 h-10 md:h-16  pointer-events-none z-10" />

      <button
        class="nav-btn left-4"
        :class="total <= 1 ? 'hidden' : ''"
        aria-label="Slide Sebelumnya"
        @click="prev"
      >
        <UIcon name="i-heroicons-chevron-left-20-solid" class="w-6 h-6 md:w-7 md:h-7" />
      </button>

      <button
        class="nav-btn right-4"
        :class="total <= 1 ? 'hidden' : ''"
        aria-label="Slide Selanjutnya"
        @click="next"
      >
        <UIcon name="i-heroicons-chevron-right-20-solid" class="w-6 h-6 md:w-7 md:h-7" />
      </button>

      <div v-if="total > 1" class="absolute bottom-2 md:bottom-4 left-0 w-full flex justify-center gap-1.5 z-20 px-4">
        <button
          v-for="(_, i) in slides"
          :key="i"
          class="dot-indicator"
          :class="{ 'active': i === realActiveIndex }"
          :aria-label="`Slide ${i + 1}`"
          @click="goTo(i)"
        />
      </div>

    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// ─── Fetch Data ──────────────────────────────────────────────────
const { data: slides, pending } = await useFetch<any[]>('/api/banner', {
  key: 'banner:home',
  default: () => [],
  transform: (res) => {
    if (!res) return []
    return res
      .map(b => ({ id: b.id, title: b.t, link: b.l, image: b.img, pos: b.p }))
      .sort((a, b) => a.pos - b.pos)
  },
})

// ─── State Mekanik Infinite ──────────────────────────────────────
const activeIndex = ref(1) 
const isTransitioning = ref(true)
const isAnimating = ref(false) 
let timer: ReturnType<typeof setInterval> | null = null
const DELAY = 5000

const total = computed(() => slides.value?.length ?? 0)

const extendedSlides = computed(() => {
  if (total.value === 0) return []
  if (total.value === 1) return [{ ...slides.value[0], _key: 'single' }]

  const first = slides.value[0]
  const last = slides.value[total.value - 1]
  
  return [
    { ...last, _key: 'clone-last' }, 
    ...slides.value.map(s => ({ ...s, _key: s.id })), 
    { ...first, _key: 'clone-first' }
  ]
})

const realActiveIndex = computed(() => {
  if (total.value <= 1) return 0
  if (activeIndex.value === 0) return total.value - 1
  if (activeIndex.value === total.value + 1) return 0
  return activeIndex.value - 1
})

const getRealIndex = (index: number) => {
  if (total.value <= 1) return 0
  if (index === 0) return total.value - 1
  if (index === total.value + 1) return 0
  return index - 1
}

const isPriority = (index: number) => {
  return total.value > 1 ? index === 1 : index === 0
}

// ─── Logic Navigasi ─────────────────────────────────────────────
const next = () => {
  if (total.value <= 1 || isAnimating.value) return
  isAnimating.value = true
  isTransitioning.value = true
  activeIndex.value++
  resetTimer()
}

const prev = () => {
  if (total.value <= 1 || isAnimating.value) return
  isAnimating.value = true
  isTransitioning.value = true
  activeIndex.value--
  resetTimer()
}

const goTo = (index: number) => {
  if (isAnimating.value || realActiveIndex.value === index) return
  isAnimating.value = true
  isTransitioning.value = true
  activeIndex.value = index + 1
  resetTimer()
}

const onTransitionEnd = () => {
  isAnimating.value = false
  
  if (activeIndex.value >= total.value + 1) {
    isTransitioning.value = false 
    activeIndex.value = 1         
  } 
  else if (activeIndex.value <= 0) {
    isTransitioning.value = false 
    activeIndex.value = total.value 
  }
}

// ─── Touch / Swipe Support (Mobile) ─────────────────────────────
const touchStartX = ref(0)
const touchEndX = ref(0)

const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.changedTouches[0].screenX
  pauseAutoplay()
}

const handleTouchEnd = (e: TouchEvent) => {
  touchEndX.value = e.changedTouches[0].screenX
  const threshold = 40 
  const diff = touchStartX.value - touchEndX.value
  
  if (Math.abs(diff) > threshold) {
    if (diff > 0) next()
    else prev()
  }
  resumeAutoplay()
}

// ─── Autoplay Lifecycle ──────────────────────────────────────────
const startTimer = () => {
  if (total.value > 1 && !timer) timer = setInterval(next, DELAY)
}
const pauseAutoplay = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}
const resumeAutoplay = () => startTimer()
const resetTimer = () => { pauseAutoplay(); startTimer() }

watch(slides, (newVal) => {
  if (newVal.length <= 1) activeIndex.value = 0
  else activeIndex.value = 1
}, { immediate: true })

onMounted(() => startTimer())
onUnmounted(() => pauseAutoplay())
</script>

<style scoped>
/* Transisi Track Carousel sangat halus */
.ease-out {
  transition-timing-function: cubic-bezier(0.25, 1, 0.5, 1);
}

/* Memastikan browser tidak menghalangi scroll vertikal saat nge-swipe */
.touch-pan-y {
  touch-action: pan-y;
}

/* ── Tombol Navigasi Kiri / Kanan ── */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  color: #404040;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
  will-change: opacity;
}

@media (min-width: 768px) {
  .nav-btn { width: 3rem; height: 3rem; }
}

.group:hover .nav-btn {
  opacity: 1;
}

.nav-btn:hover {
  background-color: #ffffff;
  color: #000000;
  transform: translateY(-50%) scale(1.05);
}

.nav-btn:active {
  transform: translateY(-50%) scale(0.95);
}

@media (hover: none) {
  .nav-btn { display: none; }
}

/* ── Pagination Dots (Titik Bawah) ── */
.dot-indicator {
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  background-color: rgba(255, 255, 255, 0.4);
  border: none;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

/* Ukuran desktop */
@media (min-width: 768px) {
  .dot-indicator { width: 6px; height: 6px; }
}

.dot-indicator:hover {
  background-color: rgba(255, 255, 255, 0.9);
}

.dot-indicator.active {
  width: 14px;
  background-color: #ffffff;
}

/* Ukuran aktif desktop */
@media (min-width: 768px) {
  .dot-indicator.active { width: 20px; }
}
</style>