<template>
  <div
    class="min-h-screen flex flex-col bg-gray-50 text-gray-900 font-sans selection:bg-blue-200 selection:text-blue-900 relative"
  >
    <header class="sticky top-0 z-50 shadow-sm">
      <AppNavbar />
      <ClientOnly>
        <FloatingChat />
      </ClientOnly>
    </header>

    <main class="flex-g row overflow-x-hidden flex flex-col">
      <div class="w-full mx-auto pb-6 flex-grow">
        <slot />
      </div>
    </main>

    <footer
      class="mt-auto transition-colors duration-300"
      :class="
        isStoreLocator ? 'bg-zinc-900 border-t-0' : 'bg-white border-t border-gray-200'
      "
      aria-labelledby="footer-heading"
    >
      <h2 id="footer-heading" class="sr-only">Footer</h2>

      <div
        class="border-b"
        :class="isStoreLocator ? 'border-zinc-800' : 'border-gray-100'"
      >
        <div
          class="max-w-[1440px] mx-auto grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 divide-x divide-y lg:divide-y-0"
          :class="isStoreLocator ? 'divide-zinc-800' : 'divide-gray-100'"
        >
          <NuxtLink
            v-for="feature in serviceFeatures"
            :key="feature.name"
            :to="feature.to"
            class="flex flex-col items-center justify-center py-8 px-4 transition-colors group text-center"
            :class="
              isStoreLocator
                ? 'bg-zinc-900 hover:bg-zinc-800'
                : 'bg-gray-50/50 hover:bg-gray-100'
            "
          >
            <Icon
              :name="feature.icon"
              class="w-8 h-8 mb-3 group-hover:scale-110 transition-all duration-300"
              :class="
                isStoreLocator
                  ? 'text-zinc-500 group-hover:text-[#00AA5B]'
                  : 'text-gray-600 group-hover:text-blue-600'
              "
              aria-hidden="true"
            />
            <span
              class="text-[11px] font-bold uppercase tracking-widest"
              :class="isStoreLocator ? 'text-gray-300' : 'text-gray-800'"
            >
              {{ feature.name }}
            </span>
          </NuxtLink>
        </div>
      </div>

      <div class="max-w-[1440px] mx-auto px-6 lg:px-10 py-16">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 lg:gap-8">
          <div class="lg:col-span-2 space-y-6">
            <NuxtLink to="/" class="inline-flex flex-col gap-1 group" aria-label="Home">
              <div class="flex items-center gap-2">
                <div
                  class="p-2 rounded-lg transition-colors"
                  :class="
                    isStoreLocator
                      ? 'bg-zinc-800 group-hover:bg-[#00AA5B]'
                      : 'bg-gray-900 group-hover:bg-blue-600'
                  "
                >
                  <Icon name="i-lucide-camera" class="w-6 h-6 text-white" />
                </div>
                <span
                  class="text-2xl font-black tracking-tighter uppercase"
                  :class="isStoreLocator ? 'text-white' : 'text-gray-900'"
                >
                  PasarCCTV
                </span>
              </div>
              <div
                class="barcode-element mt-1 opacity-70 group-hover:opacity-100 transition-opacity"
                :class="isStoreLocator ? 'text-zinc-700' : 'text-gray-900'"
              ></div>
            </NuxtLink>

            <p
              class="text-sm leading-relaxed max-w-sm"
              :class="isStoreLocator ? 'text-zinc-400' : 'text-gray-500'"
            >
              Marketplace spesialis sistem keamanan nomor 1 di Indonesia. Menyediakan
              produk original dengan garansi resmi dan jasa instalasi profesional.
            </p>

            <div class="flex gap-3 pt-2">
              <UButton
                to="#"
                target="_blank"
                icon="i-simple-icons-instagram"
                :color="isStoreLocator ? 'white' : 'gray'"
                variant="ghost"
                class="rounded-full transition-colors"
                :class="isStoreLocator ? 'hover:bg-zinc-800' : 'hover:bg-gray-100'"
                aria-label="Instagram"
              />
              <UButton
                to="#"
                target="_blank"
                icon="i-simple-icons-facebook"
                :color="isStoreLocator ? 'white' : 'gray'"
                variant="ghost"
                class="rounded-full transition-colors"
                :class="isStoreLocator ? 'hover:bg-zinc-800' : 'hover:bg-gray-100'"
                aria-label="Facebook"
              />
              <UButton
                to="#"
                target="_blank"
                icon="i-simple-icons-whatsapp"
                :color="isStoreLocator ? 'white' : 'gray'"
                variant="ghost"
                class="rounded-full transition-colors"
                :class="isStoreLocator ? 'hover:bg-zinc-800' : 'hover:bg-gray-100'"
                aria-label="WhatsApp"
              />
            </div>
          </div>

          <nav v-for="group in footerLinks" :key="group.title" :aria-label="group.title">
            <h3
              class="font-bold mb-6 text-[11px] uppercase tracking-widest"
              :class="isStoreLocator ? 'text-white' : 'text-gray-900'"
            >
              {{ group.title }}
            </h3>
            <ul class="space-y-4">
              <li v-for="link in group.links" :key="link.name">
                <NuxtLink
                  :to="link.to"
                  class="text-sm hover:translate-x-1 transition-all duration-200 inline-block font-medium"
                  :class="
                    isStoreLocator
                      ? 'text-zinc-400 hover:text-[#00AA5B]'
                      : 'text-gray-500 hover:text-blue-600'
                  "
                >
                  {{ link.name }}
                </NuxtLink>
              </li>
            </ul>
          </nav>
        </div>

        <div
          class="mt-16 pt-8 border-t flex flex-col md:flex-row justify-between items-center gap-4"
          :class="isStoreLocator ? 'border-zinc-800' : 'border-gray-100'"
        >
          <p
            class="text-[10px] uppercase tracking-widest font-bold text-center md:text-left"
            :class="isStoreLocator ? 'text-zinc-500' : 'text-gray-400'"
          >
            &copy; {{ new Date().getFullYear() }} Padjajaran CCTV / PasarCCTV. All Rights
            Reserved.
          </p>
          <div
            class="flex flex-wrap justify-center gap-4 md:gap-6 text-[10px] uppercase tracking-widest font-bold"
            :class="isStoreLocator ? 'text-zinc-500' : 'text-gray-400'"
          >
            <NuxtLink
              to="/privacy"
              class="transition-colors"
              :class="isStoreLocator ? 'hover:text-white' : 'hover:text-gray-900'"
              >Kebijakan Privasi</NuxtLink
            >
            <NuxtLink
              to="/terms"
              class="transition-colors"
              :class="isStoreLocator ? 'hover:text-white' : 'hover:text-gray-900'"
              >Syarat & Ketentuan</NuxtLink
            >
          </div>
        </div>
      </div>
    </footer>

    <CompareBadge />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router"; // Import composable router

// Deteksi apakah pengguna sedang berada di halaman store-locator
const route = useRoute();
const isStoreLocator = computed(() => route.path.includes("/store-locator"));

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
      { name: "Paket Project", to: "/portofolio" },
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
