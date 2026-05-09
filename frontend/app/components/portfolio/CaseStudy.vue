<script setup lang="ts">
defineProps<{
  data: {
    clientType: string;
    title: string;
    problem: string;
    solution: string;
    result: string;
    beforeImage: string;
    afterImage: string;
  }
}>()
</script>

<template>
  <article class="bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden flex flex-col lg:flex-row">
    
    <div class="w-full lg:w-1/2 p-8 md:p-12 flex flex-col justify-center">
      <span class="text-xs font-bold tracking-widest text-red-600 uppercase mb-4">{{ data.clientType }}</span>
      <h2 class="text-2xl md:text-3xl font-black uppercase tracking-tight mb-8 leading-tight">
        {{ data.title }}
      </h2>
      
      <div class="space-y-6">
        <div>
          <h3 class="text-xs font-black tracking-widest text-gray-400 uppercase mb-2 flex items-center gap-2">
            <Icon name="lucide:x-circle" class="w-4 h-4 text-red-500" /> Tantangan
          </h3>
          <p class="text-sm font-medium text-gray-600 leading-relaxed">{{ data.problem }}</p>
        </div>
        
        <div>
          <h3 class="text-xs font-black tracking-widest text-gray-400 uppercase mb-2 flex items-center gap-2">
            <Icon name="lucide:check-circle-2" class="w-4 h-4 text-green-500" /> Solusi Padjajaran
          </h3>
          <p class="text-sm font-medium text-gray-600 leading-relaxed">{{ data.solution }}</p>
        </div>

        <div class="pt-4 border-t border-gray-100">
          <h3 class="text-xs font-black tracking-widest text-black uppercase mb-2">Hasil</h3>
          <p class="text-sm font-bold text-gray-800 leading-relaxed">{{ data.result }}</p>
        </div>
      </div>
    </div>

    <div class="w-full lg:w-1/2 relative bg-gray-100 min-h-[300px] lg:min-h-full group overflow-hidden">
      <NuxtImg 
        :src="data.afterImage" 
        alt="Hasil Pemasangan CCTV" 
        class="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
        loading="lazy"
        format="webp"
      />
      <div class="absolute inset-0 bg-black/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-500 backdrop-blur-sm z-10 p-8">
        <div class="text-center">
           <span class="text-white text-xs font-black tracking-widest uppercase mb-4 block">Kondisi Sebelumnya</span>
           <NuxtImg 
            :src="data.beforeImage" 
            alt="Sebelum Pemasangan" 
            class="w-full max-w-sm rounded-lg border-2 border-gray-700 shadow-2xl"
            loading="lazy"
          />
        </div>
      </div>
    </div>
  </article>
</template>