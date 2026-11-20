<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  product: {
    id: string | number
    title: string
    price: number
    originalPrice: number
    image: string
    rating?: string | number
  }
}>()

const discountPercentage = computed(() => {
  if (!props.product.originalPrice || props.product.originalPrice <= props.product.price) return 0
  return Math.round(((props.product.originalPrice - props.product.price) / props.product.originalPrice) * 100)
})

function formatPrice(value: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value).replace('Rp', 'Rp')
}
</script>

<template>
  <NuxtLink
    :to="`/product/${product.id}`"
    class="flex flex-col bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-md hover:border-gray-300 transition-all duration-200 h-full"
  >
    <div class="aspect-square p-2 bg-white relative">
      <NuxtImg
        :src="product.image"
        :alt="product.title"
        format="webp"
        loading="lazy"
        class="w-full h-full object-contain"
      />
    </div>

    <div class="p-3 flex flex-col flex-1">
      <h3 class="text-[13px] text-gray-800 leading-snug line-clamp-2 mb-2 min-h-[38px]">
        {{ product.title }}
      </h3>

      <div class="mt-auto">
        <div class="text-base font-bold text-gray-900 leading-none mb-1">
          {{ formatPrice(product.price) }}
        </div>

        <div v-if="discountPercentage > 0" class="flex items-center gap-1 mb-2">
          <span class="bg-red-100 text-red-600 text-[10px] font-bold px-1 rounded">
            {{ discountPercentage }}%
          </span>
          <span class="text-[11px] text-gray-400 line-through">
            {{ formatPrice(product.originalPrice) }}
          </span>
        </div>
        <div v-else class="h-[18px] mb-2"></div>

        <div class="flex items-center gap-1 text-[11px] text-gray-500 mb-1">
          <Icon name="lucide:map-pin" size="12" class="text-red-600" />
          <span class="truncate">Jakarta Raya</span>
        </div>
        <div v-if="product.rating" class="text-[11px] text-gray-500 flex items-center gap-1">
          <Icon name="lucide:star" size="12" class="text-yellow-400 fill-yellow-400" />
          <span>{{ product.rating }}</span>
        </div>
      </div>
    </div>
  </NuxtLink>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
