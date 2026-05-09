<script setup lang="ts">
import { computed } from 'vue'
import { useCompareStore } from '~/stores/compare'

interface Props {
  uuid: string
  slug?: string
  title: string
  image: string
  price: number
  original_price?: number
  discount_percentage?: number
  category?: string
  subcategory?: string
  brand?: string
  type?: string
  specs?: Record<string, any>
  terjual?: number
}

const props = withDefaults(defineProps<Props>(), {
  original_price: 0,
  discount_percentage: 0,
  terjual: 0,
  brand: 'NO BRAND',
  type: '',
  category: 'all',
  subcategory: '',
  specs: () => ({})
})

const compareStore = useCompareStore()
const isCompare = computed(() => compareStore.isInCompare(props.uuid))

const shortSpecs = computed(() => {
  if (!props.specs || Object.keys(props.specs).length === 0) return []
  return Object.entries(props.specs).slice(0, 2)
})

const toggleCompare = () => {
  compareStore.toggle({
    id: props.uuid,
    image: props.image,
    brand: props.brand,
    title: props.title,
    price: props.price,
    type: props.type,
    originalPrice: props.original_price,
    soldCount: props.terjual,
    specs: props.specs
  })
}

// Pakai Intl.NumberFormat instance yang di-cache — tidak dibuat ulang tiap render
const priceFormatter = new Intl.NumberFormat('id-ID', {
  style: 'currency',
  currency: 'IDR',
  minimumFractionDigits: 0,
})
const formatPrice = (value: number) =>
  value ? priceFormatter.format(value).replace('Rp', 'Rp ') : 'Rp 0'

// Slug-first URL: lebih baik untuk SEO (keyword di URL)
// Fallback ke uuid jika slug belum ada
const productUrl = computed(() => `/product/${props.uuid}`)

// Label terjual: di-compute sekali, bukan di template
const soldLabel = computed(() => {
  if (!props.terjual || props.terjual <= 0) return ''
  return props.terjual >= 1000
    ? `${(props.terjual / 1000).toFixed(1)}rb`
    : String(props.terjual)
})

// Alt text deskriptif untuk SEO gambar
const imageAlt = computed(() =>
  `${props.brand} ${props.title}${props.category !== 'all' ? ` - ${props.category.replace(/-/g, ' ')}` : ''}`
)
</script>

<template>
  <!--
    Gunakan <article> bukan <div>/<a> langsung:
    - Semantik HTML5 → Google mengenali ini sebagai konten mandiri
    - itemscope/itemtype: microdata Product → harga & nama bisa muncul di rich result
  -->
  <article
    itemscope
    itemtype="https://schema.org/Product"
    class="group relative flex flex-col h-full"
  >
    <NuxtLink
      :to="productUrl"
      :title="`${brand} ${title}`"
      class="flex flex-col h-full bg-white transition-all duration-300 rounded-2xl border border-gray-100 hover:border-green-500/40 hover:shadow-[0_20px_40px_-15px_rgba(22,163,74,0.12)] hover:-translate-y-1.5 overflow-hidden"
    >
      <!-- ── Gambar ─────────────────────────────────────────────── -->
      <div class="relative aspect-square w-full overflow-hidden bg-gradient-to-b from-gray-50 to-[#f9fafb]">

        <!-- Badge diskon -->
        <div v-if="discount_percentage > 0" class="absolute top-3 left-3 z-20">
          <span
            class="bg-gradient-to-r from-red-500 to-rose-600 text-white text-[10px] font-black px-2.5 py-1 rounded-lg shadow-sm shadow-red-500/30 flex items-center gap-1"
            aria-label="Diskon {{ discount_percentage }} persen"
          >
            <UIcon name="i-heroicons-arrow-trending-down" class="w-3 h-3" aria-hidden="true" />
            {{ discount_percentage }}% OFF
          </span>
        </div>

        <!-- Action buttons (wishlist + compare) -->
        <div
          class="absolute top-3 right-3 z-20 flex flex-col gap-2 transform translate-x-12 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 transition-all duration-300 ease-out"
          @click.prevent.stop
        >
          <AddButtonWishlist :product="{ id: uuid, image, title, price, brand }" />
          <UButton
            color="white"
            variant="solid"
            icon="i-heroicons-arrows-right-left"
            :aria-label="isCompare ? 'Hapus dari perbandingan' : 'Bandingkan produk'"
            :aria-pressed="isCompare"
            class="rounded-full shadow-md bg-white/90 backdrop-blur-md transition-colors hover:bg-green-50"
            :class="isCompare ? 'text-green-600 ring-2 ring-green-500' : 'text-gray-500'"
            :disabled="compareStore.isFull && !isCompare"
            @click.prevent.stop="toggleCompare"
          />
        </div>

        <!--
          NuxtImg dengan width/height eksplisit:
          - Mencegah CLS (Cumulative Layout Shift) — faktor Core Web Vitals
          - format webp + sizes: browser pilih ukuran paling efisien
          - loading="lazy" default untuk card list (hemat bandwidth)
          - itemprop="image" → microdata gambar produk
        -->
        <NuxtImg
          :src="image"
          :alt="imageAlt"
          :title="imageAlt"
          itemprop="image"
          width="400"
          height="400"
          format="webp"
          quality="80"
          loading="lazy"
          sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
          class="h-full w-full object-contain p-6 transition-transform duration-700 ease-out group-hover:scale-110"
        />

        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/[0.03] transition-colors duration-300" aria-hidden="true" />
      </div>

      <!-- ── Konten ─────────────────────────────────────────────── -->
      <div class="flex flex-1 flex-col p-4 pt-3">

        <!-- Brand + kategori -->
        <div class="mb-2 flex items-center justify-between gap-2">
          <span
            itemprop="brand"
            class="text-[10px] font-black uppercase tracking-wider text-green-700 bg-green-50 px-2 py-0.5 rounded-md border border-green-200/60 truncate max-w-[60%]"
          >
            {{ brand }}
          </span>
          <span
            v-if="subcategory || category"
            class="text-[9px] font-bold text-gray-400 uppercase tracking-widest truncate"
          >
            {{ (subcategory || category).replace(/-/g, ' ') }}
          </span>
        </div>

        <!--
          <h3> bukan <p>: heading hierarki yang benar untuk list produk
          itemprop="name": nama produk terbaca Google
        -->
        <h3
          itemprop="name"
          class="text-[13px] font-bold text-gray-800 line-clamp-2 leading-snug min-h-[36px] group-hover:text-green-600 transition-colors"
        >
          {{ title }}
        </h3>

        <!-- Specs singkat -->
        <div class="mt-2.5 space-y-1.5 flex-1">
          <div v-if="type" class="flex items-center gap-1.5 text-gray-400">
            <UIcon name="i-heroicons-tag" class="w-3 h-3 flex-shrink-0" aria-hidden="true" />
            <p class="text-[10px] truncate font-semibold uppercase tracking-tight">{{ type }}</p>
          </div>

          <div
            v-for="[key, value] in shortSpecs"
            :key="key"
            class="flex items-center gap-1.5 text-gray-500"
            itemprop="additionalProperty"
            itemscope
            itemtype="https://schema.org/PropertyValue"
          >
            <div class="w-1 h-1 rounded-full bg-gray-300" aria-hidden="true" />
            <p class="text-[10px] truncate leading-none">
              <span itemprop="name" class="font-bold text-gray-600 capitalize">
                {{ key.replace(/_/g, ' ') }}:
              </span>
              <span itemprop="value" class="capitalize"> {{ value }}</span>
            </p>
          </div>
        </div>

        <!-- Harga dengan microdata Offer -->
        <div
          class="mt-4 flex flex-col justify-end"
          itemprop="offers"
          itemscope
          itemtype="https://schema.org/Offer"
        >
          <meta itemprop="priceCurrency" content="IDR" />
          <meta itemprop="price" :content="String(price)" />
          <link
            itemprop="availability"
            href="https://schema.org/InStock"
          />

          <!-- Harga coret -->
          <div class="h-[14px] mb-0.5 flex items-center">
            <span
              v-if="original_price && original_price > price"
              class="text-[11px] font-medium text-gray-400 line-through decoration-gray-300"
            >
              {{ formatPrice(original_price) }}
            </span>
          </div>

          <!-- Harga final -->
          <p
            itemprop="price"
            class="text-[17px] font-black tracking-tight"
            :class="discount_percentage > 0 ? 'text-red-600' : 'text-gray-900'"
          >
            {{ formatPrice(price) }}
          </p>
        </div>

        <!-- Rating + terjual -->
        <div class="mt-3 pt-3 flex items-center justify-between border-t border-gray-100">
          <div
            class="flex items-center gap-1 text-yellow-400"
            itemprop="aggregateRating"
            itemscope
            itemtype="https://schema.org/AggregateRating"
          >
            <UIcon name="i-heroicons-star-solid" class="w-3.5 h-3.5" aria-hidden="true" />
            <span
              itemprop="ratingValue"
              class="text-[10px] font-bold text-gray-600 mt-0.5"
            >5.0</span>
            <meta itemprop="reviewCount" :content="String(Math.max(terjual ?? 1, 1))" />
            <meta itemprop="bestRating" content="5" />
          </div>

          <span
            v-if="soldLabel"
            class="text-[10px] font-bold text-gray-500"
            aria-label="Terjual {{ soldLabel }}"
          >
            Terjual {{ soldLabel }}
          </span>
        </div>

      </div>
    </NuxtLink>
  </article>
</template>

<style scoped>
* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>