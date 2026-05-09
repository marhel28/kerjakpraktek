<script setup lang="ts">
defineProps<{
  testi: {
    id: number;
    name: string;
    role: string;
    rating: number;
    text: string;
  }
}>()
</script>

<template>
  <div class="bg-gray-50 border border-gray-100 p-8 rounded-xl relative">
    <Icon name="lucide:quote" class="absolute top-6 right-6 w-8 h-8 text-gray-200" />
    
    <div class="flex gap-1 mb-4">
      <Icon 
        v-for="i in 5" 
        :key="i"
        name="lucide:star" 
        class="w-4 h-4" 
        :class="i <= testi.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'"
      />
    </div>

    <p class="text-sm font-medium text-gray-700 leading-relaxed mb-6 italic">
      "{{ testi.text }}"
    </p>

    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-black rounded-full flex items-center justify-center text-white text-sm font-black">
        {{ testi.name.charAt(0) }}
      </div>
      <div>
        <h4 class="text-xs font-black uppercase tracking-wider text-black">{{ testi.name }}</h4>
        <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400">{{ testi.role }}</p>
      </div>
    </div>
  </div>
</template>