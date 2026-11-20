<script setup lang="ts">
defineProps<{ show: boolean; orderId: string; loading: boolean }>();
const emit = defineEmits<{ confirm: []; close: [] }>();
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
            class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center text-[#03AC0E] mb-4 ring-8 ring-emerald-50/50"
          >
            <UIcon name="i-heroicons-question-mark-circle" class="w-10 h-10" />
          </div>
          <h3 class="text-base font-black text-gray-900 mb-2">
            Konfirmasi Barang Sampai
          </h3>
          <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-6 leading-relaxed">
            Apakah barang pesanan dengan ID<br />
            <span
              class="font-mono text-gray-900 font-black tracking-tight text-xs bg-gray-100 px-2 py-1 rounded"
              >{{ orderId }}</span
            ><br />
            sudah sampai dengan baik?
          </p>
          <div class="flex gap-3 w-full">
            <button
              class="flex-1 py-3 text-xs font-bold text-gray-500 bg-gray-50 border border-gray-200 rounded-xl hover:bg-gray-100 transition-all uppercase tracking-widest"
              @click="emit('close')"
            >
              Batal
            </button>
            <button
              :disabled="loading"
              class="flex-1 py-3 text-xs font-black text-white bg-[#03AC0E] rounded-xl hover:bg-[#028a0b] transition-all flex items-center justify-center gap-2 shadow-lg shadow-[#03AC0E]/20 disabled:opacity-50 uppercase tracking-widest"
              @click="emit('confirm')"
            >
              <UIcon
                v-if="loading"
                name="i-heroicons-arrow-path"
                class="w-4 h-4 animate-spin"
              /><span v-else>Ya, Sampai</span>
            </button>
          </div>
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
