<template>
  <div class="min-h-screen flex flex-col bg-white text-gray-900 font-sans relative">
    <header class="sticky top-0 z-30 shadow-sm bg-white">
      <AppNavbar hide-sub-nav />
      <ClientOnly>
        <FloatingChat />
      </ClientOnly>
    </header>

    <!-- CONTENT -->
    <main class="flex-1 bg-white lg:bg-gray-50/50 pb-20">
      <div class="max-w-[1200px] mx-auto px-4 lg:px-0 py-4 lg:py-8">
        <div class="flex flex-col lg:flex-row gap-8 items-start">
          
          <!-- SIDEBAR -->
          <div class="hidden lg:block w-[300px] shrink-0">
            <AccountSidebar />
          </div>

          <!-- MOBILE NAV: horizontal scroll tabs (Tokopedia-style) -->
          <nav class="lg:hidden w-full -mx-4 px-4">
            <div class="flex items-center gap-1 overflow-x-auto scrollbar-none pb-1 -mb-1">
              <NuxtLink
                v-for="link in mobileNavLinks"
                :key="link.to"
                :to="link.to"
                class="shrink-0 flex items-center gap-1.5 px-3.5 py-2.5 rounded-full text-xs font-bold border transition-colors whitespace-nowrap"
                :class="route.path === link.to
                  ? 'bg-[#03AC0E] text-white border-[#03AC0E]'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-[#03AC0E] hover:text-[#03AC0E]'"
              >
                <UIcon :name="link.icon" class="w-3.5 h-3.5" />
                {{ link.label }}
              </NuxtLink>
            </div>
          </nav>

          <!-- PAGE -->
          <div class="flex-1 min-w-0 w-full bg-white lg:rounded-xl lg:border lg:border-gray-200 lg:shadow-sm overflow-visible">
            <slot />
          </div>

        </div>
      </div>
    </main>

    <!-- FOOTER -->
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
                  ? 'text-zinc-500 group-hover:text-[#03AC0E]'
                  : 'text-gray-600 group-hover:text-[#03AC0E]'
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
                      ? 'bg-zinc-800 group-hover:bg-gradient-to-r from-[#03AC0E] to-[#028C0B] shadow-sm'
                      : 'bg-gray-900 group-hover:bg-[#03AC0E]'
                  "
                >
                  <Icon name="i-lucide-camera" class="w-6 h-6 text-white" />
                </div>
                <span
                  class="text-2xl font-bold tracking-tight uppercase"
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
                      ? 'text-zinc-400 hover:text-[#03AC0E]'
                      : 'text-gray-500 hover:text-[#03AC0E]'
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
            &copy; {{ new Date().getFullYear() }} PasarCctv / PasarCCTV. All Rights
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
              >Syarat &amp; Ketentuan</NuxtLink
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
import { useRoute } from "vue-router";

const route = useRoute();
const isStoreLocator = computed(() => route.path.includes("/store-locator"));

const mobileNavLinks = [
  { label: "Ringkasan", to: "/dashboard", icon: "i-heroicons-user" },
  { label: "Pesanan", to: "/dashboard/orders", icon: "i-heroicons-shopping-bag" },
  { label: "Jasa", to: "/dashboard/jasa", icon: "i-heroicons-wrench-screwdriver" },
  { label: "Wishlist", to: "/dashboard/wishlist", icon: "i-heroicons-heart" },
  { label: "Alamat", to: "/dashboard/address", icon: "i-heroicons-map-pin" },
  { label: "Notifikasi", to: "/dashboard/notifications", icon: "i-heroicons-bell" },
  { label: "Bantuan", to: "/dashboard/help", icon: "i-heroicons-question-mark-circle" },
];

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
