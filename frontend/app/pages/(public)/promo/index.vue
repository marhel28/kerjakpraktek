<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import type { PromoResponse, PromoListResponse } from "~/server/api/promo";

definePageMeta({ layout: "public" });

useSeoMeta({
  title: "Promo & Diskon — PasarCctv",
  description:
    "Kumpulan penawaran dan diskon terbaik untuk kamera CCTV serta layanan instalasi.",
});

const toast = useToast();

// ── State ────────────────────────────────────────────────────────
const activeTab = ref<"all" | "flash_sale" | "stock" | "service_package">("all");
const isLoading = ref(true);
const isLoadingMore = ref(false);
const currentPage = ref(1);
const pageSize = 12;

const allPromos = ref<PromoResponse[]>([]);
const flashSales = ref<PromoResponse[]>([]);
const totalPromos = ref(0);
const hasMore = ref(false);

// ── Fetch ────────────────────────────────────────────────────────
const loadPromos = async (reset = false) => {
  if (reset) {
    currentPage.value = 1;
    allPromos.value = [];
  }

  try {
    isLoading.value = reset;
    isLoadingMore.value = !reset;

    const target =
      activeTab.value === "all" || activeTab.value === "flash_sale"
        ? undefined
        : activeTab.value;

    const res = await $fetch<PromoListResponse>("/api/promo", {
      query: {
        action: "listPromos",
        target,
        page: currentPage.value,
        size: pageSize,
      },
    });

    if (reset) {
      allPromos.value = res.items;
    } else {
      allPromos.value.push(...res.items);
    }

    totalPromos.value = res.total;
    hasMore.value = allPromos.value.length < res.total;
  } catch (err) {
    toast.add({ title: "Gagal memuat promo", color: "red" });
  } finally {
    isLoading.value = false;
    isLoadingMore.value = false;
  }
};

const loadFlashSales = async () => {
  try {
    const res = await $fetch<PromoListResponse>("/api/promo", {
      query: {
        action: "listFlashSales",
        size: 6,
      },
    });
    flashSales.value = res.items;
  } catch {}
};

const loadMore = async () => {
  currentPage.value++;
  await loadPromos(false);
};

watch(activeTab, () => loadPromos(true));

onMounted(async () => {
  await Promise.all([loadPromos(true), loadFlashSales()]);
});

// ── Computed ─────────────────────────────────────────────────────
const displayedPromos = computed(() => {
  if (activeTab.value === "flash_sale") return flashSales.value;
  return allPromos.value;
});

// Tabs without icons, relying on typography
const tabItems = [
  { key: "all", label: "Semua Promo" },
  { key: "flash_sale", label: "Flash Sale" },
  { key: "stock", label: "Produk Fisik" },
  { key: "service_package", label: "Jasa Instalasi" },
];

// ── Hero countdown (from first flash sale) ───────────────────────
const heroFlashSale = computed(() =>
  flashSales.value.find((p) => p.is_flash_sale && p.is_valid)
);
const heroTimeLeft = ref({ h: "00", m: "00", s: "00" });

const updateHeroTimer = () => {
  if (!heroFlashSale.value) return;
  const diff = new Date(heroFlashSale.value.valid_until).getTime() - Date.now();
  if (diff <= 0) {
    heroTimeLeft.value = { h: "00", m: "00", s: "00" };
    return;
  }
  const h = String(Math.floor(diff / 3600000)).padStart(2, "0");
  const m = String(Math.floor((diff % 3600000) / 60000)).padStart(2, "0");
  const s = String(Math.floor((diff % 60000) / 1000)).padStart(2, "0");
  heroTimeLeft.value = { h, m, s };
};

let heroTimer: ReturnType<typeof setInterval>;
onMounted(() => {
  updateHeroTimer();
  heroTimer = setInterval(updateHeroTimer, 1000);
});
onUnmounted(() => clearInterval(heroTimer));
</script>

<template>
  <main class="min-h-screen bg-[#F3F4F5] text-gray-900 font-sans pb-16">
    <div class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-[1200px] mx-auto px-4 md:px-6 pt-5">
        <div class="flex items-center text-[12px] text-gray-500 mb-3 gap-2">
          <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors"
            >Beranda</NuxtLink
          >
          <span class="text-gray-300">/</span>
          <span class="text-gray-900 font-bold">Promo</span>
        </div>

        <h1 class="text-[20px] font-bold text-gray-900 leading-tight">
          Promo & Penawaran Spesial
        </h1>
        <p class="text-[13px] text-gray-500 mt-1">
          Kumpulan diskon terbaik untuk produk kamera CCTV dan layanan teknisi.
        </p>

        <div
          class="flex gap-6 mt-6 border-b border-gray-200 overflow-x-auto scrollbar-hide"
        >
          <button
            v-for="tab in tabItems"
            :key="tab.key"
            @click="activeTab = tab.key as typeof activeTab"
            :class="[
              'pb-3 text-[14px] whitespace-nowrap border-b-[3px] transition-colors relative font-bold',
              activeTab === tab.key
                ? 'border-[#03AC0E] text-[#03AC0E]'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            ]"
          >
            {{ tab.label }}
            <span
              v-if="tab.key === 'flash_sale' && flashSales.length > 0"
              class="ml-1.5 bg-[#EF144A] text-white text-[10px] px-1.5 py-0.5 rounded font-bold align-middle"
            >
              {{ flashSales.length }}
            </span>
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-[1200px] mx-auto px-4 md:px-6 py-6">
      <div
        v-if="heroFlashSale && activeTab !== 'flash_sale'"
        class="bg-white border border-[#EF144A]/20 rounded-lg p-5 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm relative overflow-hidden"
      >
        <div
          class="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-[#FFEAEA] to-transparent pointer-events-none"
        ></div>

        <div class="relative z-10">
          <div class="flex items-center gap-2 mb-1.5">
            <span
              class="bg-[#EF144A] text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider"
              >Flash Sale</span
            >
            <span class="text-[15px] font-bold text-gray-900">{{
              heroFlashSale.name
            }}</span>
          </div>
          <p class="text-[13px] text-gray-600">
            Harga spesial kuota terbatas. Segera checkout sebelum kehabisan!
          </p>
        </div>

        <div
          class="flex items-center gap-5 border-t sm:border-t-0 pt-4 sm:pt-0 border-gray-100 relative z-10"
        >
          <div class="flex flex-col sm:items-end">
            <span
              class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1.5"
              >Berakhir Dalam</span
            >
            <div class="flex items-center gap-1.5">
              <span
                class="w-8 h-8 flex items-center justify-center bg-[#EF144A] text-white font-bold text-[14px] rounded"
                >{{ heroTimeLeft.h }}</span
              >
              <span class="text-[#EF144A] font-bold text-[15px]">:</span>
              <span
                class="w-8 h-8 flex items-center justify-center bg-[#EF144A] text-white font-bold text-[14px] rounded"
                >{{ heroTimeLeft.m }}</span
              >
              <span class="text-[#EF144A] font-bold text-[15px]">:</span>
              <span
                class="w-8 h-8 flex items-center justify-center bg-[#EF144A] text-white font-bold text-[14px] rounded"
                >{{ heroTimeLeft.s }}</span
              >
            </div>
          </div>
          <NuxtLink
            :to="`/promo/${heroFlashSale.slug}`"
            class="bg-[#EF144A] text-white text-[13px] font-bold px-5 py-2.5 rounded-lg hover:bg-[#d61141] transition-colors whitespace-nowrap shadow-sm"
          >
            Lihat Promo
          </NuxtLink>
        </div>
      </div>

      <div class="flex items-end justify-between mb-4 mt-2">
        <h2 class="text-[16px] font-bold text-gray-900">
          {{
            activeTab === "all"
              ? "Semua Promo Aktif"
              : activeTab === "flash_sale"
              ? "Promo Flash Sale"
              : activeTab === "stock"
              ? "Promo Produk"
              : "Promo Jasa Instalasi"
          }}
        </h2>
        <span class="text-[12px] font-medium text-gray-500"
          >{{ displayedPromos.length }} Menampilkan hasil</span
        >
      </div>

      <div
        v-if="isLoading"
        class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 lg:gap-4 gap-3"
      >
        <div
          v-for="i in 8"
          :key="i"
          class="bg-white border border-gray-200 rounded-lg p-3"
        >
          <div class="aspect-square bg-gray-100 animate-pulse rounded mb-3"></div>
          <div class="h-4 bg-gray-200 animate-pulse rounded w-3/4 mb-2"></div>
          <div class="h-3 bg-gray-100 animate-pulse rounded w-1/2"></div>
        </div>
      </div>

      <div
        v-else-if="displayedPromos.length === 0"
        class="bg-white border border-gray-200 rounded-lg p-10 text-center"
      >
        <h3 class="text-[15px] font-bold text-gray-900 mb-1">
          Belum Ada Promo di Kategori Ini
        </h3>
        <p class="text-[13px] text-gray-500">
          Coba cek kategori lain atau kembali lagi nanti untuk penawaran terbaru.
        </p>
        <button
          @click="activeTab = 'all'"
          class="mt-5 border border-gray-300 bg-white text-gray-700 text-[13px] font-bold px-5 py-2.5 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Lihat Semua Promo
        </button>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 lg:gap-4 gap-3">
        <PromoCard
          v-for="(promo, idx) in displayedPromos"
          :key="promo.uuid"
          :promo="promo"
          :featured="idx === 0"
        />
      </div>

      <div v-if="hasMore && activeTab !== 'flash_sale'" class="mt-8 flex justify-center">
        <button
          @click="loadMore"
          :disabled="isLoadingMore"
          class="bg-white border border-gray-300 text-gray-700 text-[14px] font-bold px-8 py-2.5 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors shadow-sm"
        >
          {{
            isLoadingMore
              ? "Memuat..."
              : `Muat Lebih Banyak (${totalPromos - allPromos.length})`
          }}
        </button>
      </div>
    </div>

    <div class="max-w-[1200px] mx-auto px-4 md:px-6 mt-8">
      <div
        class="bg-white border border-gray-200 rounded-lg p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm"
      >
        <div>
          <h3 class="text-[14px] font-bold text-gray-900">Riwayat Pesanan Promo</h3>
          <p class="text-[12px] text-gray-500 mt-1">
            Pantau status pengiriman dan detail transaksi dari promo yang Anda ikuti.
          </p>
        </div>
        <NuxtLink
          to="/dashboard/promo-orders"
          class="bg-white border border-[#03AC0E] text-[#03AC0E] text-[13px] font-bold px-5 py-2.5 rounded-lg hover:bg-[#D6FFDE]/30 transition-colors whitespace-nowrap"
        >
          Cek Pesanan Saya
        </NuxtLink>
      </div>
    </div>
  </main>
</template>

<style scoped>
/* Utility untuk menyembunyikan scrollbar namun tetap bisa di-scroll di mobile */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
