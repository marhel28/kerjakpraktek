<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
</script>

<template>
  <Transition name="toast">
    <div v-if="toastStore.show" :class="[
      'fixed bottom-6 right-6 z-[10000] flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-xl text-sm font-semibold transition-all border font-sans',
      toastStore.type === 'success' ? 'bg-gray-900 border-gray-800 text-white' : 
      toastStore.type === 'error' ? 'bg-red-50 border-red-200 text-red-700' :
      toastStore.type === 'warning' ? 'bg-amber-50 border-amber-200 text-amber-700' :
      'bg-blue-50 border-blue-200 text-blue-700'
    ]">
      <div :class="[
        'w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold',
        toastStore.type === 'success' ? 'bg-indigo-500 text-white' : 
        toastStore.type === 'error' ? 'bg-red-200 text-red-700' :
        toastStore.type === 'warning' ? 'bg-amber-200 text-amber-700' :
        'bg-blue-200 text-blue-700'
      ]">
        <span v-if="toastStore.type === 'success'">✓</span>
        <span v-else-if="toastStore.type === 'error'">✕</span>
        <span v-else-if="toastStore.type === 'warning'">!</span>
        <span v-else>i</span>
      </div>
      <span>{{ toastStore.message }}</span>
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}
</style>
