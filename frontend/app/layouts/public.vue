<template>
  <div
    class="min-h-screen flex flex-col bg-gray-50 text-gray-900 font-sans selection:bg-green-100 selection:text-green-900 relative"
  >
    <AppNavbar />

    <main class="flex-grow overflow-x-hidden flex flex-col">
      <div class="w-full mx-auto pb-6 flex-grow">
        <slot />
      </div>
    </main>

    <footer
      class="mt-auto bg-[#0D1B12] text-gray-200 border-t border-[#1A3322]"
      aria-labelledby="footer-heading"
    >
      <h2 id="footer-heading" class="sr-only">Footer PasarCCTV</h2>

      <!-- Bar Keunggulan Layanan (5 Kolom Tokopedia Style) -->
      <div class="border-b border-[#183020] bg-[#112317]">
        <div
          class="max-w-[1440px] mx-auto grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 divide-x divide-y lg:divide-y-0 divide-[#1B3624]"
        >
          <NuxtLink
            v-for="feature in serviceFeatures"
            :key="feature.name"
            :to="feature.to"
            class="flex flex-col items-center justify-center py-7 px-4 transition-all duration-200 group text-center hover:bg-[#152B1D]"
          >
            <Icon
              :name="feature.icon"
              class="w-7 h-7 mb-2.5 text-[#03AC0E] group-hover:scale-110 group-hover:text-[#22c55e] transition-all duration-300"
              aria-hidden="true"
            />
            <span
              class="text-[11px] font-bold uppercase tracking-widest text-gray-300 group-hover:text-white transition-colors"
            >
              {{ feature.name }}
            </span>
          </NuxtLink>
        </div>
      </div>

      <!-- Konten Utama Footer -->
      <div class="max-w-[1440px] mx-auto px-6 lg:px-10 py-14 sm:py-16">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 lg:gap-8">
          
          <!-- Kolom 1 & 2: Identitas Brand -->
          <div class="lg:col-span-2 space-y-5">
            <NuxtLink to="/" class="inline-flex flex-col gap-1 group" aria-label="Home PasarCCTV">
              <div class="flex items-center gap-2.5">
                <div class="p-2 rounded-xl bg-[#03AC0E] text-white shadow-sm flex items-center justify-center">
                  <Icon name="i-lucide-camera" class="w-6 h-6 text-white" />
                </div>
                <div>
                  <span class="text-2xl font-black tracking-tight uppercase text-white">
                    Pasar<span class="text-[#03AC0E]">CCTV</span>
                  </span>
                </div>
              </div>
            </NuxtLink>

            <p class="text-sm leading-relaxed max-w-sm text-gray-400">
              Pusat distributor resmi dan marketplace sistem keamanan terpercaya di Bandung & Indonesia. 
              Melayani pengadaan perangkat original, instalasi teknisi tersertifikasi, dan garansi purna jual resmi.
            </p>

            <!-- Social Media Icons -->
            <div class="flex gap-2.5 pt-2">
              <NuxtLink
                to="#"
                target="_blank"
                class="w-9 h-9 rounded-full bg-[#183020] hover:bg-[#03AC0E] text-gray-300 hover:text-white flex items-center justify-center transition-all duration-200"
                aria-label="Instagram"
              >
                <Icon name="i-simple-icons-instagram" class="w-4 h-4" />
              </NuxtLink>
              <NuxtLink
                to="#"
                target="_blank"
                class="w-9 h-9 rounded-full bg-[#183020] hover:bg-[#03AC0E] text-gray-300 hover:text-white flex items-center justify-center transition-all duration-200"
                aria-label="Facebook"
              >
                <Icon name="i-simple-icons-facebook" class="w-4 h-4" />
              </NuxtLink>
              <NuxtLink
                to="#"
                target="_blank"
                class="w-9 h-9 rounded-full bg-[#183020] hover:bg-[#03AC0E] text-gray-300 hover:text-white flex items-center justify-center transition-all duration-200"
                aria-label="WhatsApp"
              >
                <Icon name="i-simple-icons-whatsapp" class="w-4 h-4" />
              </NuxtLink>
            </div>
          </div>

          <!-- Kolom Navigasi -->
          <nav v-for="group in footerLinks" :key="group.title" :aria-label="group.title">
            <h3 class="font-bold mb-5 text-xs uppercase tracking-widest text-white flex items-center gap-1.5">
              <span class="w-1.5 h-3 bg-[#03AC0E] rounded-full" />
              {{ group.title }}
            </h3>
            <ul class="space-y-3">
              <li v-for="link in group.links" :key="link.name">
                <NuxtLink
                  :to="link.to"
                  class="text-sm text-gray-400 hover:text-[#03AC0E] hover:translate-x-1 transition-all duration-200 inline-block font-medium"
                >
                  {{ link.name }}
                </NuxtLink>
              </li>
            </ul>
          </nav>
        </div>

        <!-- Baris Bawah: Hak Cipta & Kebijakan -->
        <div
          class="mt-14 pt-8 border-t border-[#183020] flex flex-col md:flex-row justify-between items-center gap-4"
        >
          <p class="text-xs text-gray-400 text-center md:text-left">
            &copy; {{ new Date().getFullYear() }} <span class="text-white font-semibold">PasarCCTV Indonesia</span>. Hak Cipta Dilindungi.
          </p>
          <div
            class="flex flex-wrap justify-center gap-5 text-xs font-medium text-gray-400"
          >
            <NuxtLink
              to="/privacy"
              class="hover:text-white transition-colors"
            >
              Kebijakan Privasi
            </NuxtLink>
            <span class="text-gray-600">&bull;</span>
            <NuxtLink
              to="/terms"
              class="hover:text-white transition-colors"
            >
              Syarat &amp; Ketentuan
            </NuxtLink>
            <span class="text-gray-600">&bull;</span>
            <NuxtLink
              to="/store-locator"
              class="hover:text-white transition-colors"
            >
              Lokasi Toko Bandung
            </NuxtLink>
          </div>
        </div>
      </div>
    </footer>

    <CompareBadge />
    <ClientOnly>
      <LazyFloatingChat />
      <LazyPromoPopup />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router"; // Import composable router

const route = useRoute();
const isStoreLocator = computed(() => route.path.includes("/store-locator"));

// Cek apakah halaman harus bersih dari banner iklan (untuk konversi/operasional)
const isNoBannerRoute = computed(() => {
  const p = route.path;
  return p.includes("/checkout") || 
         p.includes("/store-locator") || 
         p.includes("/layanan/booking");
});

interface Feature {
  name: string;
  icon: string;
  to: string;
}

interface FooterLinkGroup {
  title: string;
  links: { name: string; to: string }[];
}

const serviceFeatures: Feature[] = [
  { name: "Kontak Kami", icon: "i-lucide-phone-call", to: "/contact" },
  { name: "Status Pesanan", icon: "i-lucide-package", to: "/dashboard/orders" },
  { name: "Pengiriman", icon: "i-lucide-truck", to: "/help/shipping" },
  { name: "Lokasi Toko", icon: "i-lucide-map-pin", to: "/store-locator" },
  { name: "Bantuan", icon: "i-lucide-help-circle", to: "/help" },
];

const footerLinks: FooterLinkGroup[] = [
  {
    title: "Layanan",
    links: [
      { name: "Instalasi CCTV", to: "/layanan/booking?category=installation" },
      { name: "Maintenance & Service", to: "/layanan/booking?category=maintenance" },
      { name: "Konsultasi Keamanan", to: "/layanan/booking?category=consultation" },
      { name: "Paket Project", to: "/portfolio" },
    ],
  },
  {
    title: "Bantuan",
    links: [
      { name: "Cara Belanja", to: "/helps/cara-belanja" },
      { name: "Pengiriman & Resi", to: "/helps/shipping" },
      { name: "Komplain Pelanggan", to: "/helps/support" },
    ],
  },
  {
    title: "Perusahaan",
    links: [
      { name: "Tentang Kami", to: "/about" },
      { name: "Karir", to: "/careers" },
      { name: "Syarat & Ketentuan", to: "/terms" },
      { name: "Kebijakan Privasi", to: "/privacy" },
    ],
  },
];
</script>

<style scoped>
/* Diubah ke currentColor agar bisa mengikuti warna text secara dinamis (dark/light mode) */
.barcode-element {
  height: 8px;
  width: 90px;
  background: repeating-linear-gradient(
    to right,
    currentColor,
    currentColor 2px,
    transparent 2px,
    transparent 4px,
    currentColor 4px,
    currentColor 5px,
    transparent 5px,
    transparent 8px
  );
}

html,
body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}
</style>
