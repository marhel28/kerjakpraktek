<script setup>
const route = useRoute()
</script>

<template>
  <UApp>
    <NuxtLayout :name="route.meta.layout || 'public'">
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>