<script setup lang="ts">
import { computed } from 'vue'
import { useBannerRoute } from '~/composables/useBannerRoute'

interface Props {
  targetUrl?: string | null
  imageUrl: string
  altText?: string | null
  aspectRatioClass?: string
  priority?: boolean
  imageClass?: string
  width?: number | string
  height?: number | string
}

const props = withDefaults(defineProps<Props>(), {
  targetUrl: '/',
  altText: 'Promosi Banner CCTV',
  aspectRatioClass: 'aspect-[21/9] sm:aspect-[24/9] md:aspect-[32/10] lg:aspect-[1920/540]',
  priority: false,
  imageClass: '',
  width: '1920',
  height: '540'
})

const { resolveBannerLink } = useBannerRoute()
const resolved = computed(() => resolveBannerLink(props.targetUrl))
</script>

<template>
  <component
    :is="resolved.isExternal ? 'a' : 'NuxtLink'"
    :[resolved.isExternal?'href':'to']="resolved.href"
    :target="resolved.target"
    :rel="resolved.rel"
    class="block relative w-full overflow-hidden focus:outline-none group select-none"
    :class="props.aspectRatioClass"
  >
    <NuxtImg
      :src="props.imageUrl"
      :alt="props.altText || 'Banner PasarCCTV'"
      :width="props.width"
      :height="props.height"
      format="webp"
      quality="85"
      :loading="props.priority ? 'eager' : 'lazy'"
      :fetchpriority="props.priority ? 'high' : 'auto'"
      sizes="100vw sm:100vw md:100vw"
      class="w-full h-full object-cover object-center transition-transform duration-500 ease-out group-hover:scale-[1.01]"
      :class="props.imageClass"
    />
    <slot />
  </component>
</template>