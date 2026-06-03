<script setup lang="ts">
import { computed, ref } from "vue";

// ─── SEO ─────────────────────────────────────────────────────────
const siteUrl = useRuntimeConfig().public.siteUrl ?? "https://yourdomain.com";

useSeoMeta({
  title: "Brand Resmi CCTV & Keamanan — Authorized Partner | PasarCctv",
  description:
    "Eksplorasi koleksi brand CCTV terbaik di dunia: Dahua, Imou, Ezviz, Hikvision. Produk 100% Original, Garansi Resmi, dan Dukungan Teknis Prioritas.",
  ogTitle: "Brand Resmi CCTV | PasarCctv",
  ogDescription:
    "Katalog brand CCTV original bergaransi resmi. Dahua, Imou, Ezviz, dan lebih banyak lagi.",
  ogUrl: `${siteUrl}/brands`,
  ogType: "website",
  twitterCard: "summary_large_image",
});

// ─── Fetch Data ──────────────────────────────────────────────────
const { data: brandsData, pending } = await useFetch<any[]>("/api/brands", {
  key: "brands:index:v2",
  lazy: true,
  transform: (data) => {
    if (!data) return [];
    return data.map((b) => ({
      id: b.brand_slug,
      name: b.brand_name,
      logo: b.brand_logo,
      tagline: b.tagline || `Authorized Technology Partner for ${b.brand_name}`,
      total: b.total_items,
      products: (b.products || []).slice(0, 6).map((p: any) => ({
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
      })),
    }));
  },
});

const brands = computed(() => brandsData.value || []);

// ─── Drag to Scroll Logic ────────────────────────────────────────
const isDragging = ref(false);
const startX = ref(0);
const scrollLeft = ref(0);
let activeSlider: HTMLElement | null = null;

const startDrag = (e: MouseEvent) => {
  isDragging.value = true;
  activeSlider = e.currentTarget as HTMLElement;
  startX.value = e.pageX - activeSlider.offsetLeft;
  scrollLeft.value = activeSlider.scrollLeft;
};

const stopDrag = () => {
  isDragging.value = false;
  activeSlider = null;
};

const doDrag = (e: MouseEvent) => {
  if (!isDragging.value || !activeSlider) return;
  e.preventDefault();
  const x = e.pageX - activeSlider.offsetLeft;
  const walk = (x - startX.value) * 1.5;
  activeSlider.scrollLeft = scrollLeft.value - walk;
};
</script>

<template>
  <main class="brands-page min-h-screen bg-[#F8FAFC]">
    <!-- ─── PREMIUM HERO SECTION ─── -->
    <header class="relative overflow-hidden bg-[#111] py-12 lg:py-20">
      <!-- Background Elements -->
      <div class="absolute inset-0 z-0">
        <div class="absolute top-0 left-1/4 w-96 h-96 bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm/10 rounded-full blur-[120px]"></div>
        <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px]"></div>
        <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 pointer-events-none"></div>
      </div>

      <div class="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-10">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="hero-content">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-6">
              <div class="w-2 h-2 rounded-full bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm animate-pulse"></div>
              <span class="text-[10px] font-black text-white/80 uppercase tracking-[0.2em]">Official Brand Partners</span>
            </div>
            
            <h1 class="text-4xl lg:text-6xl font-black text-white mb-6 leading-[1.1] tracking-tight">
              Teknologi Keamanan <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#03AC0E] to-emerald-400">Kelas Dunia.</span>
            </h1>
            
            <p class="text-gray-400 text-lg leading-relaxed max-w-xl mb-10">
              Kami bekerja sama secara eksklusif dengan produsen global untuk menghadirkan sistem keamanan tercanggih dengan jaminan keaslian 100%.
            </p>

            <div class="flex flex-wrap gap-4">
              <div class="bg-white/5 border border-white/10 backdrop-blur-md rounded-2xl p-5 min-w-[140px]">
                <div class="text-3xl font-black text-white mb-1">{{ brands.length || 0 }}</div>
                <div class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Brand Resmi</div>
              </div>
              <div class="bg-white/5 border border-white/10 backdrop-blur-md rounded-2xl p-5 min-w-[140px]">
                <div class="text-3xl font-black text-white mb-1">
                  {{ brands.reduce((s, b) => s + (b.total || 0), 0) }}+
                </div>
                <div class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Produk Tersedia</div>
              </div>
            </div>
          </div>

          <!-- Feature Cards Desktop -->
          <div class="hidden lg:grid grid-cols-2 gap-4">
            <div class="p-6 rounded-3xl bg-gradient-to-br from-white/5 to-transparent border border-white/10 backdrop-blur-sm">
              <div class="w-12 h-12 rounded-2xl bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm/20 flex items-center justify-center mb-4">
                <UIcon name="i-heroicons-check-badge" class="w-6 h-6 text-[#03AC0E]" />
              </div>
              <h3 class="text-white font-bold mb-2">Garansi Resmi</h3>
              <p class="text-gray-500 text-sm">Semua produk didukung oleh garansi resmi produsen.</p>
            </div>
            <div class="p-6 rounded-3xl bg-gradient-to-br from-white/5 to-transparent border border-white/10 backdrop-blur-sm mt-8">
              <div class="w-12 h-12 rounded-2xl bg-blue-500/20 flex items-center justify-center mb-4">
                <UIcon name="i-heroicons-wrench-screwdriver" class="w-6 h-6 text-blue-400" />
              </div>
              <h3 class="text-white font-bold mb-2">Technical Support</h3>
              <p class="text-gray-500 text-sm">Bantuan teknis langsung dari ahli bersertifikat.</p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- ─── BRANDS CATALOG SECTION ─── -->
    <div class="max-w-[1400px] mx-auto px-4 lg:px-10 -mt-8 lg:-mt-12 relative z-20">
      
      <!-- Skeleton Loading -->
      <div v-if="pending" class="space-y-10">
        <div v-for="i in 3" :key="i" class="bg-white rounded-3xl p-8 border border-gray-100 flex flex-col lg:flex-row gap-8">
          <USkeleton class="w-full lg:w-[280px] h-64 rounded-2xl" />
          <div class="flex-1 space-y-4">
            <USkeleton class="h-8 w-1/3" />
            <div class="flex gap-4">
              <USkeleton v-for="j in 4" :key="j" class="w-48 h-64 rounded-xl" />
            </div>
          </div>
        </div>
      </div>

      <!-- Main List -->
      <div v-else class="flex flex-col gap-10 lg:gap-16 pb-20">
        <section 
          v-for="(brand, idx) in brands" 
          :key="brand.id"
          class="brand-row group"
        >
          <div class="flex flex-col lg:flex-row lg:items-stretch gap-6 lg:gap-10">
            <!-- Brand Sidebar Card -->
            <div class="lg:w-[320px] shrink-0">
              <NuxtLink 
                :to="`/brands/${brand.id}`"
                class="block h-full bg-white border border-gray-100 rounded-[32px] p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_50px_rgba(50,205,50,0.1)] hover:border-[#03AC0E]/30 transition-all duration-500"
              >
                <div class="aspect-[4/3] bg-gray-50 rounded-2xl flex items-center justify-center p-6 mb-6 group-hover:bg-white transition-colors border border-transparent group-hover:border-gray-50">
                  <NuxtImg 
                    :src="brand.logo" 
                    :alt="brand.name"
                    class="w-full h-full object-contain filter grayscale group-hover:grayscale-0 transition-all duration-500"
                  />
                </div>

                <div class="space-y-4">
                  <div class="flex items-center gap-2">
                    <h2 class="text-2xl font-black text-gray-900 leading-tight">{{ brand.name }}</h2>
                    <UIcon name="i-heroicons-check-circle-solid" class="w-5 h-5 text-blue-500" />
                  </div>
                  <p class="text-sm text-gray-500 leading-relaxed font-medium">
                    {{ brand.tagline }}
                  </p>
                  
                  <div class="pt-6 border-t border-gray-50 flex items-center justify-between">
                    <div class="flex flex-col">
                      <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Katalog</span>
                      <span class="text-sm font-black text-gray-900">{{ brand.total }} SKU</span>
                    </div>
                    <div class="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center group-hover:bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm group-hover:text-white transition-all transform group-hover:translate-x-1">
                      <UIcon name="i-heroicons-arrow-right" class="w-5 h-5" />
                    </div>
                  </div>
                </div>
              </NuxtLink>
            </div>

            <!-- Product Showcase -->
            <div class="flex-1 min-w-0 flex flex-col justify-center">
              <div class="flex items-center justify-between mb-4 lg:mb-6 px-2">
                <h3 class="text-sm font-black text-gray-400 uppercase tracking-[0.15em]">Pilihan Terlaris</h3>
                <NuxtLink :to="`/brands/${brand.id}`" class="text-xs font-bold text-[#03AC0E] hover:underline flex items-center gap-1">
                  Lihat Semua
                  <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5" />
                </NuxtLink>
              </div>

              <div 
                class="flex gap-4 overflow-x-auto pb-6 px-1 hide-scrollbar snap-x snap-mandatory cursor-grab active:cursor-grabbing overscroll-contain"
                @mousedown="startDrag"
                @mouseleave="stopDrag"
                @mouseup="stopDrag"
                @mousemove="doDrag"
              >
                <div 
                  v-for="product in brand.products" 
                  :key="product.uuid"
                  class="w-[180px] md:w-[220px] shrink-0 snap-start select-none"
                >
                  <CardPerItems 
                    v-bind="product" 
                    class="h-full bg-white border border-gray-100 hover:border-[#03AC0E]/50 hover:shadow-xl hover:shadow-green-500/5 transition-all duration-300 rounded-2xl pointer-events-auto"
                  />
                </div>

                <!-- Explore More Card -->
                <NuxtLink 
                  :to="`/brands/${brand.id}`"
                  class="w-[180px] md:w-[220px] shrink-0 snap-start bg-white border border-dashed border-gray-200 rounded-2xl flex flex-col items-center justify-center gap-3 hover:bg-green-50 hover:border-[#03AC0E] transition-all group/more pointer-events-auto"
                >
                  <div class="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center group-hover/more:bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm group-hover/more:text-white transition-all shadow-sm">
                    <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" />
                  </div>
                  <div class="text-center">
                    <div class="text-sm font-black text-gray-900">Eksplorasi</div>
                    <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-0.5">Semua {{ brand.name }}</div>
                  </div>
                </NuxtLink>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Empty State -->
      <div v-if="!pending && !brands.length" class="bg-white rounded-[40px] p-20 text-center border border-gray-100 shadow-sm">
        <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-6 text-gray-300">
          <UIcon name="i-heroicons-building-storefront" class="w-12 h-12" />
        </div>
        <h2 class="text-2xl font-black text-gray-900 mb-2">Katalog Sedang Diperbarui</h2>
        <p class="text-gray-500 max-w-sm mx-auto leading-relaxed">
          Kami sedang mensinkronkan data mitra resmi kami. Silakan kembali dalam beberapa saat.
        </p>
      </div>

    </div>
  </main>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

.brands-page {
  font-family: 'Plus Jakarta Sans', sans-serif;
  letter-spacing: -0.01em;
}

.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Glassmorphism subtle effect */
.backdrop-blur-md {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* Custom Scroll behavior */
.overscroll-contain {
  overscroll-behavior-x: contain;
}

/* Anti-aliasing for premium feel */
* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
