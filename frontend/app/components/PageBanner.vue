<script setup lang="ts">
interface Props {
  title: string
  description?: string
  breadcrumbs?: { label: string; to?: string }[]
  image?: string // Tambahan prop untuk gambar CDN
}

defineProps<Props>()
</script>

<template>
  <header
    class="relative w-full border-b border-gray-200 overflow-hidden"
    :class="image ? 'py-16 md:py-20 bg-gray-900' : 'py-8 bg-white'"
  >
    <template v-if="image">
      <NuxtImg
        :src="image"
        :alt="`Banner ${title}`"
        loading="lazy"
        format="webp"
        quality="80"
        class="absolute inset-0 w-full h-full object-cover z-0"
      />
      <div class="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-black/10 z-10"></div>
    </template>

    <div class="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

      <nav
        v-if="breadcrumbs && breadcrumbs.length"
        class="flex text-sm mb-4 gap-2"
        :class="image ? 'text-gray-300' : 'text-gray-500'"
      >
        <template v-for="(crumb, index) in breadcrumbs" :key="index">
          <NuxtLink
            v-if="crumb.to"
            :to="crumb.to"
            class="transition-colors"
            :class="image ? 'hover:text-white' : 'hover:text-black'"
          >
            {{ crumb.label }}
          </NuxtLink>
          <span
            v-else
            class="font-medium"
            :class="image ? 'text-white' : 'text-gray-900'"
          >
            {{ crumb.label }}
          </span>
          <span
            v-if="index < breadcrumbs.length - 1"
            :class="image ? 'text-gray-600' : 'text-gray-300'"
          >
            /
          </span>
        </template>
      </nav>

      <h1
        class="text-3xl md:text-5xl font-extrabold tracking-tight uppercase"
        :class="image ? 'text-white' : 'text-gray-900'"
      >
        {{ title }}
      </h1>

      <p
        v-if="description"
        class="mt-3 text-base md:text-lg max-w-2xl"
        :class="image ? 'text-gray-200' : 'text-gray-500'"
      >
        {{ description }}
      </p>

    </div>
  </header>
</template>

<style scoped>
header {
  font-family: var(--font-sans);
}
</style>
