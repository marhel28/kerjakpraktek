<script setup lang="ts">
import { computed, ref, onBeforeUnmount } from "vue";

// --- SEO ---------------------------------------------------------
const siteUrl = useRuntimeConfig().public.siteUrl ?? "https://yourdomain.com";

useSeoMeta({
  title: "Brand Resmi CCTV dan Keamanan: Official Partner Store | PasarCctv",
  description:
    "Katalog resmi brand CCTV dan perangkat keamanan terbaik dunia: Dahua, Hikvision, Ezviz, Imou, Tapo, Tiandy, Seagate, WD, dan lainnya. 100% Original bergaransi resmi.",
  ogTitle: "Brand Resmi CCTV & Keamanan | PasarCctv",
  ogDescription:
    "Belanja kamera CCTV dan perlengkapan keamanan original langsung dari distributor resmi. Garansi resmi 1-2 tahun dengan dukungan teknisi profesional.",
  ogUrl: `${siteUrl}/brands`,
  ogType: "website",
});

// --- Data Tagline & Specialty Curation ---------------------------
const BRAND_METADATA: Record<string, { tagline: string; badge: string }> = {
  dahua: {
    tagline: "Spesialis Kamera Pengawas IP, XVR & Teknologi AI WizSense",
    badge: "Tier-1 Partner",
  },
  hikvision: {
    tagline: "Sistem Keamanan CCTV ColorVu & NVR 4K No. 1 Global",
    badge: "Authorized Distributor",
  },
  ezviz: {
    tagline: "Smart Home Camera & Perangkat Keamanan WiFi Praktis",
    badge: "Official Store",
  },
  imou: {
    tagline: "Kamera Pengawas Nirkabel dengan AI Human & Pet Detection",
    badge: "Official Partner",
  },
  tapo: {
    tagline: "Smart Security & IoT Terkoneksi dari TP-Link",
    badge: "Official Store",
  },
  tiandy: {
    tagline: "Pionir Kamera Pengawas Super Starlight Full Color Malam Hari",
    badge: "Official Partner",
  },
  glenz: {
    tagline: "Power Supply Jaring, Video Balun & Aksesori Instalasi CCTV",
    badge: "Distributor Resmi",
  },
  "tp-link": {
    tagline: "Switch PoE Gigabit, WiFi 6 Router & Access Point Komersial",
    badge: "Networking Partner",
  },
  seagate: {
    tagline: "Harddisk Surveillance SkyHawk Tahan Rekam 24/7 Nonstop",
    badge: "Storage Partner",
  },
  wd: {
    tagline: "Harddrive CCTV WD Purple dengan Teknologi AllFrame 4K",
    badge: "Storage Partner",
  },
  belden: {
    tagline: "Kabel UTP Cat6 & Coaxial Tembaga Murni Kualitas USA",
    badge: "Cabling Partner",
  },
};

// --- Fetch Data --------------------------------------------------
const { data: brandsData, pending, error, refresh } = await useFetch<any[]>("/api/brands", {
  key: "brands:index:v3",
  lazy: true,
  transform: (data) => {
    if (!data) return [];
    return data.map((b) => {
      const slug = (b.brand_slug || "").toLowerCase().trim();
      const meta = BRAND_METADATA[slug] || {
        tagline: `Solusi perangkat keamanan resmi bergaransi untuk ${b.brand_name}`,
        badge: "Official Partner",
      };

      return {
        id: b.brand_slug,
        name: b.brand_name,
        logo: b.brand_logo,
        tagline: meta.tagline,
        badge: meta.badge,
        total: b.total_items || 0,
        products: (b.products || []).slice(0, 8).map((p: any) => ({
          uuid: p.uuid,
          slug: p.slug,
          title: p.title,
          brand: b.brand_name,
          price: p.price,
          original_price: p.original_price || p.price,
          discount_percentage: p.discount_percentage || 0,
          image: p.image,
          terjual: p.terjual || 0,
          category: p.category || "",
          type: p.type || "",
        })),
      };
    });
  },
});

const allBrands = computed(() => brandsData.value || []);

// --- Search & Filter State ---------------------------------------
const searchQuery = ref("");
const selectedBrandFilter = ref("all");

const filteredBrands = computed(() => {
  let list = allBrands.value;

  if (selectedBrandFilter.value !== "all") {
    list = list.filter((b) => b.id === selectedBrandFilter.value);
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim();
    list = list.filter(
      (b) =>
        b.name.toLowerCase().includes(q) ||
        b.tagline.toLowerCase().includes(q) ||
        b.products.some((p: any) => p.title.toLowerCase().includes(q))
    );
  }

  return list;
});

const totalSkuAllBrands = computed(() =>
  allBrands.value.reduce((acc, b) => acc + (b.total || 0), 0)
);

// --- Drag to Scroll Logic ----------------------------------------
const isDragging = ref(false);
const hasDragged = ref(false);
const startX = ref(0);
const scrollLeft = ref(0);
let activeSlider: HTMLElement | null = null;

const doDrag = (e: MouseEvent) => {
  if (!isDragging.value || !activeSlider) return;
  e.preventDefault();
  const x = e.pageX - activeSlider.offsetLeft;
  const walk = (x - startX.value) * 1.5;
  if (Math.abs(walk) > 5) {
    hasDragged.value = true;
  }
  activeSlider.scrollLeft = scrollLeft.value - walk;
};

const stopDrag = () => {
  if (!isDragging.value) return;
  isDragging.value = false;
  activeSlider = null;
  window.removeEventListener("mousemove", doDrag);
  window.removeEventListener("mouseup", stopDrag);
  setTimeout(() => {
    hasDragged.value = false;
  }, 50);
};

const startDrag = (e: MouseEvent) => {
  isDragging.value = true;
  hasDragged.value = false;
  activeSlider = e.currentTarget as HTMLElement;
  startX.value = e.pageX - activeSlider.offsetLeft;
  scrollLeft.value = activeSlider.scrollLeft;
  window.addEventListener("mousemove", doDrag);
  window.addEventListener("mouseup", stopDrag);
};

const preventClickIfDragged = (e: Event) => {
  if (hasDragged.value) {
    e.preventDefault();
    e.stopPropagation();
  }
};

onBeforeUnmount(() => {
  window.removeEventListener("mousemove", doDrag);
  window.removeEventListener("mouseup", stopDrag);
});

// --- Button Scroll Helper ----------------------------------------
const scrollSlider = (brandId: string, direction: "left" | "right") => {
  const slider = document.getElementById(`slider-${brandId}`);
  if (slider) {
    const scrollAmount = 320;
    slider.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  }
};

const scrollToBrand = (brandSlug: string) => {
  selectedBrandFilter.value = "all";
  const el = document.getElementById(`brand-section-${brandSlug}`);
  if (el) {
    el.setAttribute("tabindex", "-1");
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    el.focus({ preventScroll: true });
  }
};
</script>

<template>
  <main class="brands-page min-h-screen bg-slate-50/70 text-slate-800">
    <!-- 1. Clean Light Header -->
    <header class="bg-white border-b border-slate-200/80 pt-6 pb-10 sm:pb-12 relative overflow-hidden">
      <div class="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Breadcrumbs -->
        <nav aria-label="Breadcrumb" class="flex items-center gap-2 text-xs text-slate-500 mb-4 font-medium">
          <NuxtLink to="/" class="hover:text-[#03AC0E] transition-colors">Beranda</NuxtLink>
          <UIcon name="i-tabler-chevron-right" class="w-3.5 h-3.5 text-slate-400" />
          <span class="text-[#03AC0E] font-medium">Brand Resmi</span>
        </nav>

        <div class="grid lg:grid-cols-12 gap-6 lg:gap-8 items-center">
          <div class="lg:col-span-8 space-y-3">
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E6F7E9] border border-[#C8E6CC] text-[#0D1B12] text-xs font-medium">
              <UIcon name="i-tabler-circle-check" class="w-4 h-4 text-[#03AC0E]" />
              <span>Official Store & Distributor Resmi</span>
            </div>

            <h1 class="text-2xl sm:text-3xl lg:text-4xl font-semibold tracking-tight text-slate-900 leading-tight">
              Brand Resmi CCTV & Security System
            </h1>

            <p class="text-slate-600 text-xs sm:text-sm max-w-2xl leading-relaxed">
              Katalog resmi perangkat keamanan dunia bergaransi prinsipal. 100% barang original, siap kirim dengan jaminan klaim garansi mudah dan dukungan teknisi tersertifikasi.
            </p>

            <!-- 4 Trust Badges -->
            <div class="pt-2 grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <div class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-200/80 text-xs font-medium text-slate-700">
                <UIcon name="i-tabler-shield-check" class="w-4 h-4 text-[#03AC0E] shrink-0" />
                <span>Garansi 1-2 Thn</span>
              </div>
              <div class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-200/80 text-xs font-medium text-slate-700">
                <UIcon name="i-tabler-tool" class="w-4 h-4 text-[#03AC0E] shrink-0" />
                <span>Teknisi Ahli</span>
              </div>
              <div class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-200/80 text-xs font-medium text-slate-700">
                <UIcon name="i-tabler-truck" class="w-4 h-4 text-[#03AC0E] shrink-0" />
                <span>Kirim Se-Indonesia</span>
              </div>
              <div class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-200/80 text-xs font-medium text-slate-700">
                <UIcon name="i-tabler-file-check" class="w-4 h-4 text-[#03AC0E] shrink-0" />
                <span>Faktur Resmi</span>
              </div>
            </div>
          </div>

          <!-- Quick Stats Panel -->
          <div class="lg:col-span-4 flex lg:justify-end">
            <div class="bg-white border border-slate-200 rounded-2xl p-5 w-full sm:max-w-xs shadow-xs space-y-3">
              <div class="flex items-center justify-between pb-2.5 border-b border-slate-100">
                <span class="text-xs text-slate-500 uppercase tracking-wider font-medium">Brand Resmi</span>
                <span class="text-xl font-medium text-slate-900">{{ allBrands.length || 11 }} Brand</span>
              </div>
              <div class="flex items-center justify-between pb-2.5 border-b border-slate-100">
                <span class="text-xs text-slate-500 uppercase tracking-wider font-medium">Total Katalog</span>
                <span class="text-xl font-medium text-[#03AC0E]">{{ totalSkuAllBrands }}+ SKU</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-slate-500 uppercase tracking-wider font-medium">Layanan Instalasi</span>
                <span class="text-xs font-medium bg-[#03AC0E] text-white px-2.5 py-0.5 rounded-full">Bandung & Cimahi</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 2. Brand Directory Bar & Search Controls -->
    <div class="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 -mt-6 relative z-20">
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 sm:p-5 space-y-4">
        <!-- Search bar + brand filter count -->
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div class="relative flex-1 max-w-md">
            <UIcon name="i-tabler-search" class="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Cari nama brand atau produk (mis: Dahua, NVR, Ezviz)..."
              class="w-full pl-10 pr-9 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#03AC0E] focus:bg-white text-slate-800 placeholder-slate-400 transition"
            />
            <button
              v-if="searchQuery"
              @click="searchQuery = ''"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label="Hapus pencarian"
            >
              <UIcon name="i-tabler-x" class="w-4 h-4" />
            </button>
          </div>

          <div class="text-xs text-slate-500 font-medium flex items-center gap-2">
            <span>Menampilkan <strong>{{ filteredBrands.length }}</strong> dari {{ allBrands.length }} Brand Resmi</span>
            <button
              v-if="selectedBrandFilter !== 'all' || searchQuery"
              @click="selectedBrandFilter = 'all'; searchQuery = ''"
              class="text-xs text-[#03AC0E] font-medium hover:underline"
            >
              Reset Filter
            </button>
          </div>
        </div>

        <!-- Quick Jump Brand Chips -->
        <div class="flex items-center gap-2 overflow-x-auto pb-1 hide-scrollbar pt-1">
          <button
            @click="selectedBrandFilter = 'all'"
            :class="[
              'px-3.5 py-1.5 rounded-full text-xs font-medium shrink-0 transition flex items-center gap-1.5 border',
              selectedBrandFilter === 'all'
                ? 'bg-[#03AC0E] text-white border-[#03AC0E] shadow-xs'
                : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
            ]"
          >
            <span>Semua Brand</span>
            <span :class="['text-[10px] px-1.5 py-0.5 rounded-full', selectedBrandFilter === 'all' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500']">{{ allBrands.length }}</span>
          </button>

          <button
            v-for="b in allBrands"
            :key="b.id"
            @click="scrollToBrand(b.id)"
            class="px-3 py-1.5 rounded-full text-xs font-medium shrink-0 transition flex items-center gap-2 bg-white hover:bg-[#E6F7E9] hover:text-[#03AC0E] hover:border-[#C8E6CC] border border-slate-200 text-slate-700 shadow-xs"
          >
            <img :src="b.logo" :alt="b.name" class="w-4 h-4 object-contain" />
            <span>{{ b.name }}</span>
            <span class="text-[10px] text-slate-400 font-normal">({{ b.total }})</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 3. Brand Showcase Sections -->
    <div class="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-12">
      <!-- Error State -->
      <div
        v-if="error"
        class="bg-white rounded-2xl border border-red-200 p-8 text-center max-w-md mx-auto my-12 shadow-sm"
      >
        <div class="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-3 text-red-500">
          <UIcon name="i-tabler-alert-triangle" class="w-6 h-6" />
        </div>
        <h3 class="text-base font-medium text-slate-900 mb-1">Gagal Memuat Katalog Brand</h3>
        <p class="text-xs text-slate-500 mb-4 leading-relaxed">
          Terjadi kesalahan saat memuat data. Silakan muat ulang halaman atau coba beberapa saat lagi.
        </p>
        <button
          @click="refresh()"
          class="px-4 py-2 rounded-xl bg-[#03AC0E] hover:bg-[#02930c] text-white text-xs font-medium transition shadow-xs"
        >
          Coba Lagi
        </button>
      </div>

      <!-- Loading Skeleton -->
      <div v-else-if="pending" class="space-y-8">
        <div v-for="i in 3" :key="i" class="bg-white rounded-2xl border border-slate-200 p-6 space-y-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <USkeleton class="w-16 h-16 rounded-xl" />
              <div class="space-y-2">
                <USkeleton class="w-32 h-6" />
                <USkeleton class="w-56 h-4" />
              </div>
            </div>
            <USkeleton class="w-28 h-9 rounded-lg" />
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <USkeleton v-for="j in 4" :key="j" class="h-64 rounded-xl" />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="filteredBrands.length === 0"
        class="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-md mx-auto my-12 shadow-sm"
      >
        <div class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
          <UIcon name="i-tabler-search" class="w-8 h-8" />
        </div>
        <h3 class="text-lg font-medium text-slate-900 mb-1">Brand Tidak Ditemukan</h3>
        <p class="text-sm text-slate-500 mb-6 leading-relaxed">
          Tidak ada brand atau produk yang cocok dengan pencarian "{{ searchQuery }}". Silakan periksa ejaan atau reset filter.
        </p>
        <button
          @click="searchQuery = ''; selectedBrandFilter = 'all'"
          class="px-4 py-2 rounded-xl bg-[#03AC0E] hover:bg-[#02930c] text-white text-sm font-medium transition shadow-xs"
        >
          Tampilkan Semua Brand
        </button>
      </div>

      <!-- Unified Brand Cards -->
      <div v-else class="space-y-8">
        <section
          v-for="brand in filteredBrands"
          :key="brand.id"
          :id="`brand-section-${brand.id}`"
          class="bg-white rounded-2xl border border-slate-200/90 shadow-xs hover:shadow-md transition-shadow overflow-hidden scroll-mt-24"
        >
          <!-- Brand Header Bar -->
          <div class="p-5 sm:p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white">
            <div class="flex items-center gap-4 min-w-0">
              <!-- Logo Container -->
              <NuxtLink
                :to="`/brands/${brand.id}`"
                class="w-16 h-16 sm:w-20 sm:h-20 bg-white rounded-xl border border-slate-200 p-2.5 flex items-center justify-center shrink-0 shadow-xs hover:border-[#03AC0E] transition"
              >
                <NuxtImg
                  :src="brand.logo"
                  :alt="brand.name"
                  class="max-h-full max-w-full object-contain"
                  loading="lazy"
                />
              </NuxtLink>

              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <NuxtLink :to="`/brands/${brand.id}`" class="hover:text-[#03AC0E] transition">
                    <h2 class="text-xl sm:text-2xl font-medium text-slate-900 tracking-tight leading-tight">
                      {{ brand.name }}
                    </h2>
                  </NuxtLink>
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-[#E6F7E9] text-[#03AC0E] border border-[#C8E6CC]">
                    <UIcon name="i-tabler-circle-check" class="w-3.5 h-3.5 text-[#03AC0E]" />
                    <span>{{ brand.badge }}</span>
                  </span>
                </div>

                <p class="text-xs sm:text-sm text-slate-500 mt-1 font-medium line-clamp-1">
                  {{ brand.tagline }}
                </p>

                <div class="flex items-center gap-3 mt-1.5 text-xs text-slate-500">
                  <span class="font-medium text-slate-800">{{ brand.total }} Produk Siap Kirim</span>
                  <span class="text-slate-300">•</span>
                  <span class="text-[#03AC0E] font-medium flex items-center gap-1">
                    <UIcon name="i-tabler-shield-check" class="w-3.5 h-3.5" />
                    Garansi Resmi Terjamin
                  </span>
                </div>
              </div>
            </div>

            <!-- Right Controls: Navigation Buttons + CTA -->
            <div class="flex items-center justify-between md:justify-end gap-3 shrink-0 pt-3 md:pt-0 border-t md:border-t-0 border-slate-100">
              <!-- Slider Arrows (Desktop only) -->
              <div v-if="brand.products.length > 3" class="hidden sm:flex items-center gap-1.5">
                <button
                  @click="scrollSlider(brand.id, 'left')"
                  :aria-controls="`slider-${brand.id}`"
                  class="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 flex items-center justify-center transition"
                  aria-label="Scroll Sebelumnya"
                >
                  <UIcon name="i-tabler-chevron-left" class="w-4 h-4" />
                </button>
                <button
                  @click="scrollSlider(brand.id, 'right')"
                  :aria-controls="`slider-${brand.id}`"
                  class="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 flex items-center justify-center transition"
                  aria-label="Scroll Selanjutnya"
                >
                  <UIcon name="i-tabler-chevron-right" class="w-4 h-4" />
                </button>
              </div>

              <NuxtLink
                :to="`/brands/${brand.id}`"
                class="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl bg-[#03AC0E] hover:bg-[#02930c] text-white text-xs sm:text-sm font-medium transition shadow-xs"
              >
                <span>Kunjungi Official Store</span>
                <UIcon name="i-tabler-arrow-right" class="w-4 h-4" />
              </NuxtLink>
            </div>
          </div>

          <!-- Product Showcase Slider -->
          <div class="p-4 sm:p-6 bg-slate-50/40 relative">
            <div v-if="brand.products && brand.products.length > 0">
              <div
                :id="`slider-${brand.id}`"
                class="custom-drag-area flex gap-4 overflow-x-auto pb-2 px-1 hide-scrollbar overscroll-contain"
                @mousedown="startDrag"
                @click.capture="preventClickIfDragged"
              >
                <!-- Product Card -->
                <div
                  v-for="product in brand.products"
                  :key="product.uuid"
                  class="w-[190px] sm:w-[220px] md:w-[240px] shrink-0 snap-start select-none flex flex-col h-auto"
                >
                  <CardPerItems
                    v-bind="product"
                    class="h-full"
                  />
                </div>

                <!-- Final Card: View All Products for this brand -->
                <NuxtLink
                  :to="`/brands/${brand.id}`"
                  class="w-[190px] sm:w-[220px] md:w-[240px] shrink-0 snap-start bg-white border border-slate-200 rounded-xl p-6 flex flex-col items-center justify-center text-center gap-3 hover:border-[#03AC0E] hover:bg-[#E6F7E9]/20 transition group shadow-xs"
                >
                  <div class="w-12 h-12 rounded-full bg-[#E6F7E9] text-[#03AC0E] group-hover:bg-[#03AC0E] group-hover:text-white flex items-center justify-center transition shadow-xs">
                    <UIcon name="i-tabler-arrow-right" class="w-5 h-5" />
                  </div>
                  <div>
                    <div class="text-sm font-medium text-slate-900 group-hover:text-[#03AC0E]">Lihat Semua</div>
                    <div class="text-xs text-slate-500 mt-0.5">Katalog {{ brand.name }} ({{ brand.total }} Produk)</div>
                  </div>
                </NuxtLink>
              </div>
            </div>

            <!-- Fallback if 0 products loaded -->
            <div v-else class="py-8 text-center text-slate-400 text-xs sm:text-sm">
              <p>Katalog produk {{ brand.name }} sedang dalam pembaruan inventaris.</p>
              <NuxtLink :to="`/brands/${brand.id}`" class="text-[#03AC0E] font-medium hover:underline mt-1 inline-block">
                Kunjungi halaman resmi {{ brand.name }}
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.custom-drag-area {
  -webkit-user-select: none;
  user-select: none;
}
.custom-drag-area * {
  -webkit-user-drag: none;
}
</style>
