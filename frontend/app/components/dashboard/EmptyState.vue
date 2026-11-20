<script setup lang="ts">
withDefaults(
  defineProps<{
    icon?: string;
    title: string;
    description?: string;
    ctaLabel?: string;
    ctaTo?: string;
  }>(),
  { icon: "i-heroicons-inbox", description: "", ctaLabel: "", ctaTo: "" }
);

const emit = defineEmits<{ cta: [] }>();
</script>

<template>
  <div
    class="bg-white border border-gray-200 rounded-xl p-10 md:p-14 text-center max-w-2xl mx-auto shadow-sm"
  >
    <div
      class="w-16 h-16 rounded-full bg-[#E6F7E9] text-[#03AC0E] flex items-center justify-center mx-auto mb-4"
    >
      <UIcon :name="icon" class="w-8 h-8" />
    </div>
    <h1 class="text-xl font-medium text-gray-900 mb-2">
      {{ title }}
    </h1>
    <p
      v-if="description"
      class="text-sm text-gray-500 mb-6 leading-relaxed max-w-md mx-auto"
    >
      {{ description }}
    </p>
    <NuxtLink
      v-if="ctaTo"
      :to="ctaTo"
      class="inline-flex items-center gap-2 bg-[#03AC0E] text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-[#028C0B] transition-colors shadow-sm"
    >
      {{ ctaLabel }}
    </NuxtLink>
    <button
      v-else-if="ctaLabel"
      type="button"
      class="inline-flex items-center gap-2 bg-[#03AC0E] text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-[#028C0B] transition-colors shadow-sm cursor-pointer"
      @click="emit('cta')"
    >
      {{ ctaLabel }}
    </button>
  </div>
</template>
