 <template>
  <section v-if="!pending && data?.items && data.items.length > 0" class="w-full bg-white py-8 border-y border-gray-200/80">
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10">
      <!-- Header Flash Sale: Amazon Deal + Tokopedia Countdown -->
      <div class="flex flex-wrap items-center justify-between gap-4 pb-4 mb-6 border-b border-gray-100">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="w-2 h-6 bg-[#CC0C39] rounded-full" aria-hidden="true" />
            <h2 class="text-lg sm:text-xl font-bold tracking-tight text-gray-900 font-['Plus_Jakarta_Sans',sans-serif]">
              {{ data.title || 'Flash Sale Hari Ini' }}
            </h2>
          </div>

          <!-- Countdown Badges (Merah-Hitam Kontras) -->
          <div v-if="!isExpired" class="flex items-center gap-1 text-xs font-mono font-bold text-white">
            <span class="px-2 py-1 bg-[#111] rounded">{{ hours }}</span>
            <span class="text-gray-400 font-sans">:</span>
            <span class="px-2 py-1 bg-[#111] rounded">{{ minutes }}</span>
            <span class="text-gray-400 font-sans">:</span>
            <span class="px-2 py-1 bg-[#CC0C39] rounded animate-pulse">{{ seconds }}</span>
          </div>
        </div>

        <NuxtLink
          to="/promo"
          class="text-xs sm:text-sm font-bold text-[#03AC0E] hover:underline flex items-center gap-1 font-['Plus_Jakarta_Sans',sans-serif]"
        >
          Lihat Semua Promo
          <UIcon name="i-heroicons-arrow-right-20-solid" class="w-4 h-4" />
        </NuxtLink>
      </div>

      <!-- Grid Produk Flash Sale (Card Tokopedia Bersih) -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
        <NuxtLink
          v-for="item in data.items"
          :key="item.stock_uuid"
          :to="`/product/${item.slug}`"
          class="group bg-white border border-gray-200 hover:border-[#03AC0E] rounded-xl p-3 shadow-xs hover:shadow-sm transition-all flex flex-col justify-between"
        >
          <!-- Image Frame -->
          <div class="w-full aspect-square bg-[#F8F9FA] rounded-lg p-2 flex items-center justify-center overflow-hidden relative mb-2.5">
            <img
              :src="item.image"
              :alt="item.title"
              class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-200"
              loading="lazy"
            />
            <!-- Badge Diskon Merah Amazon -->
            <span class="absolute top-2 left-2 bg-[#CC0C39] text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow-2xs font-['Plus_Jakarta_Sans',sans-serif]">
              -{{ item.discount_percentage }}%
            </span>
          </div>

          <!-- Product Details -->
          <div>
            <h3 class="text-xs font-bold text-gray-900 group-hover:text-[#03AC0E] transition-colors line-clamp-2 leading-snug font-['Plus_Jakarta_Sans',sans-serif] mb-1.5">
              {{ item.title }}
            </h3>

            <!-- Price Structure -->
            <div class="space-y-0.5">
              <span class="text-sm sm:text-base font-bold text-[#CC0C39] block font-mono">
                {{ formatRupiah(item.price) }}
              </span>
              <span class="text-[11px] text-gray-400 line-through block font-mono">
                {{ formatRupiah(item.original_price) }}
              </span>
            </div>

            <!-- Progress Bar Stock -->
            <div class="mt-2.5 pt-2 border-t border-gray-100">
              <div class="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-[#CC0C39] rounded-full"
                  :style="{ width: `${item.is_almost_sold_out ? 85 : 40}%` }"
                />
              </div>
              <span class="text-[10px] text-gray-500 font-semibold mt-1 block">
                {{ item.is_almost_sold_out ? 'Segera Habis' : 'Tersedia' }}
              </span>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useFlashSale } from '~/composables/useFlashSale'

const { data, pending, hours, minutes, seconds, isExpired } = useFlashSale()

const formatRupiah = (val: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(val)
}
</script>