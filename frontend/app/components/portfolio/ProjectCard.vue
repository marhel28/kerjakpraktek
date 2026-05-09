<script setup lang="ts">
const props = defineProps<{
  project: {
    id: number;
    title: string;
    category: string;
    cameras: number;
    location: string;
    image: string;
    packageSlug: string;
  }
}>()

const handleUsePackage = () => {
  // Logic untuk add to cart atau redirect ke detail paket
  const router = useRouter()
  router.push(`/produk/${props.project.packageSlug}`)
}
</script>

<template>
  <div class="group relative bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col h-full">
    
    <div class="relative h-56 overflow-hidden bg-gray-100">
      <NuxtImg 
        :src="project.image" 
        :alt="project.title"
        class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        loading="lazy"
        format="webp"
      />
      <div class="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-md text-[10px] font-black uppercase tracking-widest text-black">
        {{ project.category }}
      </div>
    </div>

    <div class="p-5 flex flex-col flex-grow">
      <h3 class="text-lg font-black tracking-tight uppercase leading-tight mb-4 group-hover:text-red-600 transition-colors">
        {{ project.title }}
      </h3>
      
      <div class="flex items-center gap-4 text-xs font-bold text-gray-500 uppercase tracking-wider mb-6 mt-auto">
        <span class="flex items-center gap-1.5">
          <Icon name="lucide:video" class="w-4 h-4 text-gray-400" />
          {{ project.cameras }} Titik
        </span>
        <span class="flex items-center gap-1.5">
          <Icon name="lucide:map-pin" class="w-4 h-4 text-gray-400" />
          {{ project.location }}
        </span>
      </div>

      <button 
        @click="handleUsePackage"
        class="w-full py-3 bg-gray-50 border border-gray-200 text-black text-[11px] font-black uppercase tracking-widest hover:bg-black hover:text-white hover:border-black transition-colors rounded"
      >
        Lihat Paket Serupa
      </button>
    </div>
  </div>
</template>