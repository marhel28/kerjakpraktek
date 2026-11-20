<script setup lang="ts">
defineProps<{ show: boolean }>();
const emit = defineEmits<{ close: [] }>();
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-scale">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="emit('close')" />
        <div
          class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden p-6 flex flex-col items-center text-center z-10 border border-gray-100"
        >
          <div
            class="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center text-[#03AC0E] mb-6 ring-8 ring-emerald-50"
          >
            <UIcon name="i-heroicons-check-circle" class="w-12 h-12 animate-pulse" />
          </div>
          <h3 class="text-lg font-black text-gray-900 mb-2">
            Pesanan Selesai!
          </h3>
          <p class="text-xs text-gray-500 font-semibold mb-6 leading-relaxed">
            Terima kasih telah berbelanja di PasarCctv. Semoga produk kami dapat memenuhi kebutuhan keamanan Anda.
          </p>
          <button
            class="w-full py-3 text-xs font-black text-white bg-gray-900 rounded-xl hover:bg-black transition-all uppercase tracking-widest shadow-lg shadow-gray-900/20"
            @click="emit('close')"
          >
            Selesai
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-scale-enter-active,
.modal-scale-leave-active {
  transition: opacity 0.25s ease;
}
.modal-scale-enter-active .relative,
.modal-scale-leave-active .relative {
  transition:
    transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
    opacity 0.25s ease;
}
.modal-scale-enter-from,
.modal-scale-leave-to {
  opacity: 0;
}
.modal-scale-enter-from .relative {
  transform: scale(0.9) translateY(12px);
}
.modal-scale-leave-to .relative {
  transform: scale(0.95);
}
</style>
