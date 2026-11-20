<template>
  <div
    class="w-full max-w-4xl mx-auto bg-white border border-gray-200 shadow-sm rounded-lg overflow-hidden flex flex-col lg:flex-row font-['Open_Sans',sans-serif]"
  >
    <!-- Left Panel: Hero CCTV Image (Situs Asli) -->
    <div class="hidden lg:block lg:w-1/2 bg-black relative">
      <img
        :src="heroImage"
        alt="PasarCctv Security"
        width="720"
        height="900"
        class="w-full h-full object-cover opacity-35"
        loading="eager"
        fetchpriority="high"
      />
      <div
        class="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent"
        aria-hidden="true"
      />

      <div class="absolute bottom-10 left-8 right-8 text-white">
        <div class="flex flex-col leading-none mb-4">
          <span class="text-3xl font-black text-white tracking-tighter uppercase italic font-['Plus_Jakarta_Sans',sans-serif]">
            PasarCctv
          </span>
          <span class="text-xs font-light text-gray-400 tracking-[0.3em] uppercase mt-1 font-['Plus_Jakarta_Sans',sans-serif]">
            SECURITY SYSTEM
          </span>
        </div>
        <h2 class="text-xl font-black uppercase tracking-tight leading-tight mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
          Sistem Keamanan <br />
          <span class="text-red-600">Nomor 1</span> di Indonesia.
        </h2>
        <p class="text-gray-300 text-xs font-normal leading-relaxed max-w-xs font-['Open_Sans',sans-serif]">
          Akses produk kamera CCTV resmi, garansi distributor, dan teknisi instalasi bersertifikat.
        </p>

        <!-- Security Trust Mini Strip -->
        <div class="mt-6 pt-4 border-t border-white/15 flex items-center gap-3 text-[10px] text-gray-300 font-semibold tracking-wide">
          <span class="flex items-center gap-1">
            <UIcon name="i-heroicons-shield-check" class="w-3.5 h-3.5 text-[#03AC0E]" />
            Garansi Resmi
          </span>
          <span>•</span>
          <span class="flex items-center gap-1">
            <UIcon name="i-heroicons-lock-closed" class="w-3.5 h-3.5 text-[#03AC0E]" />
            SSL 256-Bit
          </span>
        </div>
      </div>
    </div>

    <!-- Right Panel: Amazon Single-Box Structure with PasarCctv Colors (Hitam/Putih/Merah) -->
    <div class="w-full lg:w-1/2 p-6 sm:p-10 flex flex-col justify-center bg-white">
      <!-- Mobile Brand Logo -->
      <div class="mb-5 text-center lg:text-left">
        <div class="flex flex-col leading-none mb-3 lg:hidden items-center">
          <span class="text-2xl font-black text-black tracking-tighter uppercase italic font-['Plus_Jakarta_Sans',sans-serif]">
            PasarCctv
          </span>
          <span class="text-[10px] font-light text-gray-500 tracking-[0.3em] uppercase font-['Plus_Jakarta_Sans',sans-serif]">
            SECURITY SYSTEM
          </span>
        </div>
        <slot name="header-tagline" />
      </div>

      <!-- Main Form Slot -->
      <div class="space-y-4">
        <slot name="form" />
      </div>

      <!-- Divider -->
      <div class="my-5 flex items-center" aria-hidden="true">
        <div class="flex-grow border-t border-gray-200" />
        <span class="mx-3 text-[11px] font-black text-gray-400 uppercase tracking-widest font-['Plus_Jakarta_Sans',sans-serif]">
          Atau
        </span>
        <div class="flex-grow border-t border-gray-200" />
      </div>

      <!-- Secondary Actions (Google Sign-In, dsb) -->
      <div class="space-y-3">
        <slot name="secondary-actions" />
      </div>

      <!-- Footer Action Links -->
      <div class="mt-5 pt-4 border-t border-gray-100 text-center">
        <slot name="footer-links" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    isRegistration?: boolean
    heroImage?: string
  }>(),
  {
    isRegistration: false,
    heroImage: 'https://daganghalal.blob.core.windows.net/44641/Product/cctv-installation-services-1745476968100.jpg',
  }
)
</script>