<script setup lang="ts">
import type { PromoResponse } from "~/services/promo";

const props = defineProps<{
  promo: PromoResponse;
  featured?: boolean;
}>();

const formatRupiah = (n: number) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  })
    .format(n)
    .replace("Rp", "Rp ");

const promoTypeLabelMap: Record<string, { label: string; color: string }> = {
  percentage: { label: "% OFF", color: "bg-emerald-500" },
  fixed: { label: "POTONGAN", color: "bg-sky-500" },
  bogo: { label: "BELI & GRATIS", color: "bg-violet-500" },
  bundle_disc: { label: "BUNDLE", color: "bg-amber-500" },
  flash_sale: { label: "⚡ FLASH SALE", color: "bg-red-500" },
};

const typeInfo = computed(
  () =>
    promoTypeLabelMap[props.promo.promo_type] || { label: "PROMO", color: "bg-gray-500" }
);

const discountDisplay = computed(() => {
  if (
    props.promo.promo_type === "percentage" ||
    props.promo.promo_type === "flash_sale"
  ) {
    return `${props.promo.discount_value}%`;
  }
  if (props.promo.promo_type === "fixed") {
    return formatRupiah(props.promo.discount_value);
  }
  if (props.promo.promo_type === "bogo") {
    return `Beli ${props.promo.buy_quantity} Gratis ${props.promo.get_quantity}`;
  }
  return `${props.promo.discount_value}%`;
});

// Countdown timer
const timeLeft = ref("");
const timerInterval = ref<ReturnType<typeof setInterval> | null>(null);

const updateTimer = () => {
  const now = Date.now();
  const end = new Date(props.promo.valid_until).getTime();
  const diff = end - now;
  if (diff <= 0) {
    timeLeft.value = "Berakhir";
    if (timerInterval.value) clearInterval(timerInterval.value);
    return;
  }
  const d = Math.floor(diff / 86400000);
  const h = Math.floor((diff % 86400000) / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  if (d > 0) timeLeft.value = `${d}h ${h}j lagi`;
  else if (h > 0) timeLeft.value = `${h}j ${m}m lagi`;
  else timeLeft.value = `${m}m ${s}d lagi`;
};

onMounted(() => {
  updateTimer();
  if (props.promo.is_flash_sale) {
    timerInterval.value = setInterval(updateTimer, 1000);
  } else {
    updateTimer();
  }
});

onUnmounted(() => {
  if (timerInterval.value) clearInterval(timerInterval.value);
});

const quotaPercent = computed(() => {
  if (!props.promo.quota) return null;
  return Math.round((props.promo.used_count / props.promo.quota) * 100);
});
</script>

<template>
  <NuxtLink
    :to="`/promo/${promo.slug}`"
    class="group block relative overflow-hidden rounded-2xl transition-all duration-300"
    :class="featured ? 'shadow-xl' : 'shadow-md'"
  >
    <!-- Banner / Background -->
    <div class="relative h-44 overflow-hidden">
      <img
        v-if="promo.banner_url"
        :src="promo.banner_url"
        :alt="promo.name"
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
      />
      <div
        v-else
        class="w-full h-full bg-gradient-to-br from-slate-800 via-slate-700 to-slate-900 flex items-center justify-center"
      >
        <span class="text-5xl font-black text-white/20 tracking-tighter select-none"
          >PROMO</span
        >
      </div>

      <!-- Overlay gradient bottom -->
      <div
        class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"
      />

      <!-- Type badge -->
      <span
        class="absolute top-3 left-3 text-[10px] font-black px-2.5 py-1 rounded-full text-white tracking-widest uppercase"
        :class="typeInfo.color"
      >
        {{ typeInfo.label }}
      </span>

      <!-- Flash sale timer -->
      <div
        v-if="promo.is_flash_sale"
        class="absolute top-3 right-3 bg-black/80 backdrop-blur-sm text-red-400 text-[10px] font-bold px-2.5 py-1 rounded-full border border-red-500/30 flex items-center gap-1"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse inline-block" />
        {{ timeLeft }}
      </div>

      <!-- Discount display — big text on banner -->
      <div class="absolute bottom-3 left-4">
        <p
          class="text-white/70 text-[10px] font-semibold uppercase tracking-widest mb-0.5"
        >
          Hemat
        </p>
        <p class="text-white text-2xl font-black leading-none drop-shadow-lg">
          {{ discountDisplay }}
        </p>
      </div>
    </div>

    <!-- Card body -->
    <div class="bg-white p-4">
      <h3
        class="font-bold text-gray-900 text-sm leading-snug line-clamp-2 mb-2 group-hover:text-[#03AC0E] transition-colors"
      >
        {{ promo.name }}
      </h3>

      <!-- Min purchase info -->
      <div
        v-if="promo.min_purchase > 0"
        class="text-[11px] text-gray-500 mb-3 flex items-center gap-1"
      >
        <svg
          class="w-3 h-3 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        Min. belanja {{ formatRupiah(promo.min_purchase) }}
      </div>

      <!-- Quota bar for flash sale -->
      <div v-if="promo.is_flash_sale && quotaPercent !== null" class="mb-3">
        <div class="flex justify-between text-[10px] text-gray-500 mb-1">
          <span>Tersisa</span>
          <span class="font-bold text-red-500">{{ promo.remaining_quota }} item</span>
        </div>
        <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="
              quotaPercent > 70
                ? 'bg-red-500'
                : quotaPercent > 40
                ? 'bg-amber-400'
                : 'bg-emerald-500'
            "
            :style="`width: ${quotaPercent}%`"
          />
        </div>
      </div>

      <!-- Items preview (tiny thumbnails) -->
      <div v-if="promo.items.length > 0" class="flex gap-1.5 mb-3">
        <div
          v-for="item in promo.items.slice(0, 4)"
          :key="item.uuid"
          class="w-8 h-8 rounded-lg bg-gray-50 border border-gray-100 overflow-hidden shrink-0"
        >
          <img
            v-if="item.thumbnail_url"
            :src="item.thumbnail_url"
            :alt="item.item_name"
            class="w-full h-full object-cover"
          />
          <div
            v-else
            class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center"
          >
            <svg
              class="w-3 h-3 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
        </div>
        <div
          v-if="promo.items.length > 4"
          class="w-8 h-8 rounded-lg bg-gray-100 border border-gray-200 flex items-center justify-center"
        >
          <span class="text-[9px] font-bold text-gray-500"
            >+{{ promo.items.length - 4 }}</span
          >
        </div>
      </div>

      <!-- Footer: deadline + cta hint -->
      <div class="flex items-center justify-between">
        <span class="text-[10px] text-gray-400">
          s.d
          {{
            new Date(promo.valid_until).toLocaleDateString("id-ID", {
              day: "numeric",
              month: "short",
            })
          }}
        </span>
        <span
          class="text-[11px] font-bold text-[#03AC0E] flex items-center gap-0.5 group-hover:gap-1.5 transition-all"
        >
          Lihat
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </span>
      </div>
    </div>

    <!-- Valid/Invalid overlay -->
    <div
      v-if="!promo.is_valid"
      class="absolute inset-0 bg-black/60 flex items-center justify-center rounded-2xl backdrop-blur-[1px]"
    >
      <span
        class="bg-white/90 text-gray-800 text-xs font-black px-4 py-2 rounded-full tracking-widest uppercase"
        >Promo Berakhir</span
      >
    </div>
  </NuxtLink>
</template>
