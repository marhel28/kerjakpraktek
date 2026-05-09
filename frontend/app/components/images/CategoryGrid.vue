<script setup lang="ts">
import CdnImage from '~/components/images/CdnImage.vue'

interface BannerItem {
  uuid: string
  title: string
  image_url: string
  route_link: string
  sort_order: number
}

const props = defineProps<{
  categories?: BannerItem[]  // data dari backend
}>()

// Mapping ke format yang dibutuhkan layout
const mappedCategories = computed(() =>
  (props.categories || []).map(banner => ({
    title: banner.title,
    link: banner.route_link,
    image: banner.image_url,
  }))
)
</script>

<template>
  <section
    v-if="mappedCategories.length"
    class="w-full bg-white"
    aria-label="Kategori Utama"
  >
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">

      <NuxtLink
        v-for="(cat, index) in mappedCategories"
        :key="index"
        :to="cat.link"
        class="group relative h-[250px] md:h-[300px] lg:h-[350px] w-full overflow-hidden flex items-center justify-center cursor-pointer"
      >
        <CdnImage
          :src="cat.image"
          :alt="`Kategori ${cat.title}`"
          fit="cover"
          class="absolute inset-0 w-full h-full transition-transform duration-700 ease-in-out group-hover:scale-110"
        />

        <div class="absolute inset-0 bg-black/40 transition-colors duration-300 group-hover:bg-black/50"></div>

        <div class="relative z-10 flex items-center gap-3 px-4 text-center">
          <Icon name="ph:asterisk-bold" class="w-4 h-4 md:w-5 md:h-5 text-white opacity-80" />

          <h3
            class="text-white font-black text-lg md:text-xl lg:text-2xl tracking-[0.1em] uppercase drop-shadow-md"
            style="font-family: 'Inter', sans-serif;"
          >
            {{ cat.title }}
          </h3>

          <Icon name="ph:asterisk-bold" class="w-4 h-4 md:w-5 md:h-5 text-white opacity-80" />
        </div>

      </NuxtLink>

    </div>
  </section>
</template>