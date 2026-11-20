<script setup lang="ts">
interface Props {
  query?: string
  totalResults?: number
  selectedCategory?: string | null
  selectedBrand?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  query: '',
  totalResults: 0,
  selectedCategory: null,
  selectedBrand: null
})

const queryDisplay = computed(() => {
  if (props.query && props.query.trim()) {
    return `"${props.query.trim()}"`
  }
  if (props.selectedCategory) {
    return `Kategori: ${props.selectedCategory}`
  }
  if (props.selectedBrand) {
    return `Brand: ${props.selectedBrand}`
  }
  return 'Semua Produk'
})
</script>

<template>
  <header class="bg-[#131A22] text-white border-b border-neutral-800">
    <div class="max-w-[1400px] mx-auto px-4 md:px-6 py-5 md:py-7">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div class="space-y-2">
          <div class="flex items-center gap-2 text-xs font-medium text-[#FF9900]">
            <span class="inline-flex items-center gap-1 bg-[#232F3E] px-2.5 py-1 rounded border border-neutral-700">
              <span class="w-1.5 h-1.5 rounded-full bg-[#FF9900]" />
              HASIL PENCARIAN
            </span>
            <span class="text-neutral-400">
              Ditemukan {{ totalResults.toLocaleString('id-ID') }} produk
            </span>
          </div>

          <h1 class="text-xl md:text-2xl lg:text-3xl font-bold tracking-tight text-white line-clamp-1">
            {{ queryDisplay }}
          </h1>

          <div class="flex flex-wrap items-center gap-2 pt-1 text-xs text-neutral-300">
            <span class="inline-flex items-center gap-1 bg-white/10 px-2 py-0.5 rounded text-neutral-200">
              <UIcon name="i-heroicons-shield-check-solid" class="w-3.5 h-3.5 text-[#FF9900]" />
              Garansi Resmi
            </span>
            <span class="inline-flex items-center gap-1 bg-white/10 px-2 py-0.5 rounded text-neutral-200">
              <UIcon name="i-heroicons-truck-solid" class="w-3.5 h-3.5 text-[#FF9900]" />
              Siap Kirim Cepat
            </span>
            <span class="inline-flex items-center gap-1 bg-white/10 px-2 py-0.5 rounded text-neutral-200">
              <UIcon name="i-heroicons-wrench-screwdriver-solid" class="w-3.5 h-3.5 text-[#FF9900]" />
              Teknisi Tersedia
            </span>
          </div>
        </div>

        <div class="hidden lg:flex items-center gap-3 bg-[#232F3E] border border-neutral-700/80 rounded-lg p-3.5 max-w-sm text-xs">
          <div class="w-10 h-10 rounded bg-[#FF9900]/10 flex items-center justify-center shrink-0">
            <UIcon name="i-heroicons-magnifying-glass-solid" class="w-5 h-5 text-[#FF9900]" />
          </div>
          <div class="space-y-0.5">
            <p class="font-semibold text-white">Butuh bantuan mencari item?</p>
            <p class="text-neutral-300 text-[11px]">Gunakan filter spesifikasi di sisi kiri untuk mempersempit pencarian.</p>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>