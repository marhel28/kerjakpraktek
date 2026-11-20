<script setup lang="ts">
// Redirect /produk/:id → /product/:id (301 alias transparan)
const route = useRoute()
const id = route.params.id as string
await navigateTo(`/product/${id}`, { redirectCode: 301 })
</script>
<template><div /></template>