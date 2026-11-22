<script setup lang="ts">
/**
 * Top Progress Bar (NProgress-style)
 * - Shows during route transitions and fetch pending states
 * - Minimal, accessible, no layout shift
 */
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNuxtApp } from '#app'

const progress = ref(0)
const isVisible = ref(false)
const router = useRouter()
const nuxtApp = useNuxtApp()

let timer: number | null = null
let startTime = 0

function start() {
  if (isVisible.value) return
  isVisible.value = true
  progress.value = 0.1
  startTime = Date.now()
  tick()
}

function tick() {
  const elapsed = Date.now() - startTime
  // Simulate progress: fast at first, then slow down
  if (progress.value < 0.9) {
    progress.value = 0.1 + (0.8 * (1 - Math.exp(-elapsed / 800)))
    timer = window.requestAnimationFrame(tick)
  }
}

function done() {
  if (timer) {
    cancelAnimationFrame(timer)
    timer = null
  }
  progress.value = 1
  // Brief pause at 100% then hide
  setTimeout(() => {
    isVisible.value = false
    progress.value = 0
  }, 200)
}

function onRouteChange() {
  start()
  // Hook into Nuxt's page:finish / page:error
}

onMounted(() => {
  // Listen to Nuxt page hooks
  const stopStart = nuxtApp.hook('page:start', start)
  const stopFinish = nuxtApp.hook('page:finish', done)
  const stopError = nuxtApp.hook('page:error', done)

  // Also listen to router for SPA navigations
  router.beforeEach(() => start())
  router.afterEach(() => done())
  router.onError(() => done())

  onUnmounted(() => {
    stopStart()
    stopFinish()
    stopError()
    if (timer) cancelAnimationFrame(timer)
  })
})
</script>

<template>
  <div
    v-if="isVisible"
    class="fixed top-0 left-0 right-0 z-[100] h-1 bg-transparent pointer-events-none"
    role="progressbar"
    aria-valuenow="0"
    aria-valuemin="0"
    aria-valuemax="100"
    aria-label="Page loading progress"
  >
    <div
      class="h-full bg-primary-500 origin-left transform transition-transform duration-200 ease-out will-change-transform"
      :style="{ transform: `scaleX(${progress})` }"
    />
  </div>
</template>

<style scoped>
/* Ensure no layout shift */
.fixed {
  position: fixed;
}
</style>