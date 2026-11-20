<template>
  <div
    v-if="message"
    role="alert"
    aria-live="polite"
    class="border border-[#c40000] bg-white rounded-md p-3.5 mb-4 shadow-sm flex items-start gap-3"
  >
    <div class="text-[#c40000] shrink-0 mt-0.5" aria-hidden="true">
      <svg class="w-5 h-5 fill-current" viewBox="0 0 24 24">
        <path
          d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"
        />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <h4 class="text-sm font-bold text-[#c40000] leading-tight mb-1 font-['Plus_Jakarta_Sans',sans-serif]">
        {{ title }}
      </h4>
      <p class="text-xs text-[#0F1111] leading-relaxed font-['Open_Sans',sans-serif]">
        {{ message }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    message: string
  }>(),
  {
    title: 'Terjadi Kendala',
  }
)
</script>