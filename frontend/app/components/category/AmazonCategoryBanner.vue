<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useFetch } from '#app'
import BannerImageLink from '~/components/banner/BannerImageLink.vue'

interface BannerItem {
  uuid: string
  image_url: string
  alt_text?: string
  target_url: string
  order: number
}

interface ImageSectionResponse {
  status: string
  source?: string
  data: {
    uuid: string
    identifier: string
    title: string
    mode: string
    is_active: boolean
    items: BannerItem[]
  }
}

const props = defineProps<{
  categoryTitle: string
  parentCategory?: string | null
  activeSlug?: string
}>()

const route = useRoute()

// Determine active category slug from route or props
const resolvedSlug = computed(() => {
  if (props.activeSlug) return props.activeSlug
  const rawSlug = route.params.slug as string | string[] | undefined
  const slugArray = Array.isArray(rawSlug)
    ? rawSlug.filter(Boolean)
    : rawSlug ? [rawSlug] : []
  return slugArray.length > 0 ? slugArray[slugArray.length - 1]!.toLowerCase() : 'semua-kategori'
})

// Fetch category-specific banner section (identifier: "category:{slug}")
const sectionIdentifier = computed(() => `category:${resolvedSlug.value}`)

const { data: sectionData, pending } = await useFetch<any>(() => `/api/banner/${encodeURIComponent(sectionIdentifier.value)}`, {
  default: () => null,
  watch: [sectionIdentifier],
})

// Process banner items from API response
const bannerItems = computed<BannerItem[]>(() => {
  const res = sectionData.value as unknown as ImageSectionResponse
  if (res?.status === 'success' && res.data?.items?.length) {
    return res.data.items
      .filter(item => item.image_url)
      .sort((a, b) => a.order - b.order)
  }
  return []
})

// Check if we have valid admin banner
const hasAdminBanner = computed(() => bannerItems.value.length > 0)

// Layout mode from admin (default: asymRight for Amazon asymmetric style)
const layoutMode = computed(() => {
  const res = sectionData.value as unknown as ImageSectionResponse
  return res?.data?.mode || 'asymRight'
})

// Fallback copy per category (can be extended)
const fallbackCopy = computed(() => {
  const slug = resolvedSlug.value
  const title = props.categoryTitle || slug.replace(/-/g, ' ').toUpperCase()
  
  const copyMap: Record<string, { subtitle: string; description: string; ctaText: string; ctaUrl: string }> = {
    'kamera-cctv': {
      subtitle: 'Official Catalog / Original Garansi Resmi',
      description: 'Koleksi lengkap kamera CCTV, IP Camera, DVR/NVR & aksesoris instalasi terbaik dengan harga distributor resmi.',
      ctaText: 'Lihat Paket Hemat Instalasi',
      ctaUrl: '/category/paket-cctv'
    },
    'ip-camera': {
      subtitle: 'Official Catalog / Original Garansi Resmi',
      description: 'IP Camera berkualitas tinggi untuk keamanan modern. Support ColorVu, DarkFighter, Smart Detection.',
      ctaText: 'Beli IP Camera',
      ctaUrl: '/category/ip-camera'
    },
    'dvr-nvr': {
      subtitle: 'Official Catalog / Original Garansi Resmi',
      description: 'DVR & NVR standar industri untuk rekaman 24/7. Kompatibel semua brand kamera utama.',
      ctaText: 'Beli DVR/NVR',
      ctaUrl: '/category/dvr-nvr'
    },
    'aksesoris-cctv': {
      subtitle: 'Official Catalog / Original Garansi Resmi',
      description: 'Kabel, konektor, power supply, hard disk, dan aksesoris instalasi CCTV lengkap.',
      ctaText: 'Beli Aksesoris',
      ctaUrl: '/category/aksesoris-cctv'
    }
  }
  
  return copyMap[slug] || {
    subtitle: 'Official Catalog / Original Garansi Resmi',
    description: `Koleksi lengkap ${title.toLowerCase()} dengan garansi resmi distributor.`,
    ctaText: `Lihat Semua ${title}`,
    ctaUrl: `/category/${slug}`
  }
})

// Trust badges
const trustBadges = [
  { icon: 'i-heroicons-shield-check', text: 'Garansi 1-3 Tahun', color: 'text-amber-400' },
  { icon: 'i-heroicons-truck', text: 'Siap Kirim Cepat', color: 'text-amber-400' },
  { icon: 'i-heroicons-wrench-screwdriver', text: 'Support Teknisi', color: 'text-amber-400' }
]
</script>

<template>
  <div class="relative w-full bg-[#131A22] text-white border-b border-neutral-800 select-none overflow-hidden">
    <div class="max-w-[1400px] mx-auto px-4 md:px-6 py-6 md:py-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
      
      <!-- Copy Section: High contrast, sharp typography -->
      <div class="max-w-xl flex flex-col gap-2">
        <div class="flex items-center gap-2 text-xs font-semibold text-neutral-400 uppercase tracking-wider">
          <span>Official Catalog</span>
          <span class="text-neutral-600">/</span>
          <span class="text-amber-400 font-bold">Original Garansi Resmi</span>
        </div>

        <h1 class="text-2xl md:text-3xl lg:text-4xl font-black text-white tracking-tight leading-tight">
          {{ categoryTitle }}
        </h1>

        <p class="text-xs md:text-sm text-neutral-300 leading-relaxed">
          {{ fallbackCopy.description }}
        </p>

        <!-- Trust Badges -->
        <div class="flex flex-wrap items-center gap-2.5 pt-2">
          <div
            v-for="badge in trustBadges"
            :key="badge.icon"
            class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-neutral-800/80 border border-neutral-700 rounded text-[11px] font-medium text-neutral-200"
          >
            <UIcon :name="badge.icon" class="w-3.5 h-3.5" :class="badge.color" />
            <span>{{ badge.text }}</span>
          </div>
        </div>
      </div>

      <!-- Right Side: Admin Banner OR Fallback Promo Callout -->
      <div
        v-if="hasAdminBanner"
        class="shrink-0 w-full md:max-w-[520px]"
        :class="layoutMode === 'featureWide' || layoutMode === 'heroStrip' ? 'md:max-w-full' : ''"
      >
        <!-- Admin-uploaded banner images -->
        <div
          v-if="layoutMode === 'featureWide' || layoutMode === 'heroStrip'"
          class="relative rounded-lg overflow-hidden"
          style="aspect-ratio: 21/9;"
        >
          <BannerImageLink
            v-for="item in bannerItems"
            :key="item.uuid"
            :image-url="item.image_url"
            :target-url="item.target_url"
            :alt-text="item.alt_text || categoryTitle"
            class="absolute inset-0"
          />
        </div>
        <div
          v-else
          class="grid gap-3"
          :class="{
            'md:grid-cols-2': layoutMode === 'double' || layoutMode === 'asymLeft' || layoutMode === 'asymRight',
            'md:grid-cols-3': layoutMode === 'triple' || layoutMode === 'mixed',
            'md:grid-cols-4': layoutMode === 'quad',
            'grid-cols-1': true
          }"
        >
          <BannerImageLink
            v-for="item in bannerItems"
            :key="item.uuid"
            :image-url="item.image_url"
            :target-url="item.target_url"
            :alt-text="item.alt_text || categoryTitle"
            class="rounded-lg overflow-hidden"
            style="aspect-ratio: 16/9;"
          />
        </div>
      </div>

      <!-- Fallback Promo Callout (when no admin banner) -->
      <div
        v-else
        class="shrink-0 bg-[#232F3E] border border-neutral-700/80 rounded-lg p-4 md:p-5 flex flex-col gap-2.5 max-w-sm"
      >
        <div class="flex items-center justify-between gap-4">
          <span class="px-2 py-0.5 bg-[#CC0C39] text-white font-black text-[10px] tracking-wider uppercase rounded">
            Special Deal
          </span>
          <span class="text-xs text-neutral-400">Periode Terbatas</span>
        </div>
        <p class="text-sm font-bold text-white leading-snug">
          Paket Hemat Instalasi CCTV & Smart Security Bergaransi
        </p>
        <p class="text-xs text-neutral-400">
          Diskon s/d 40% untuk pembelian paket bundled + jasa pemasangan profesional.
        </p>
        <NuxtLink
          :to="fallbackCopy.ctaUrl"
          class="mt-2 inline-flex items-center justify-center gap-1.5 px-4 py-2 bg-amber-400 hover:bg-amber-500 text-neutral-950 font-bold text-xs rounded border border-amber-500 transition-colors"
        >
          <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" />
          {{ fallbackCopy.ctaText }}
        </NuxtLink>
      </div>

    </div>
  </div>
</template>
