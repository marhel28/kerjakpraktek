<script setup>
const route = useRoute()
</script>

<template>
  <NuxtLayout :name="route.meta.layout || 'public'">
    <NuxtPage />
  </NuxtLayout>
</template>