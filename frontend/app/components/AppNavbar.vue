<template>
  <div>
    <header
      class="w-full z-50 shadow-sm font-sans bg-white sticky top-0 transition-all duration-300 hidden lg:block"
    >
      <div
        class="text-white transition-all duration-300 ease-in-out overflow-hidden"
        :class="[
          isScrolled ? 'h-0 opacity-0 pointer-events-none' : 'h-[34px] opacity-100',
          isComparePage ? 'bg-neutral-900' : 'bg-black'
        ]"
      >
        <div class="max-w-[1400px] mx-auto w-full px-4 lg:px-10 h-full flex justify-between items-center text-[11px] font-bold tracking-wider uppercase">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-truck" class="w-4 h-4" aria-hidden="true" />
            <span>Pengiriman Seluruh Indonesia!</span>
          </div>
          <div class="flex items-center gap-5">
            <NuxtLink to="/login" class="hover:text-gray-300 transition-colors">Masuk | Daftar</NuxtLink>
            <NuxtLink to="/store-locator" class="hover:text-gray-300 transition-colors">Lokasi Toko</NuxtLink>
            <NuxtLink to="/track" class="hover:text-gray-300 transition-colors">Lacak Pesanan</NuxtLink>
            <NuxtLink to="/help" class="hover:text-gray-300 transition-colors">Bantuan</NuxtLink>
            <div class="flex items-center gap-1 border-l border-gray-700 pl-4 ml-2">
              <img src="https://flagcdn.com/w20/id.png" alt="Indonesia" width="16" height="12" class="object-cover rounded-sm" />
              <span>Indonesia</span>
              <UIcon name="i-heroicons-chevron-down" class="w-3 h-3" aria-hidden="true" />
            </div>
          </div>
        </div>
      </div>

      <nav class="bg-white px-4 lg:px-10 py-3 lg:py-4 border-b border-gray-100">
        <div class="max-w-[1200px] mx-auto flex items-center justify-between gap-6 lg:gap-12">

          <NuxtLink to="/" class="flex-shrink-0 group flex items-center transition-transform active:scale-95" aria-label="Padjajaran CCTV - Beranda">
            <NuxtImg
              src="/pasarcctv.png"
              alt="Padjajaran CCTV"
              format="webp"
              height="80"
              class="h-10 lg:h-18 w-auto object-contain transition-opacity group-hover:opacity-80"
              loading="eager"
              fetchpriority="high"
              preload
            />
          </NuxtLink>

          <div class="flex-1 max-w-[700px] relative" ref="searchContainerRef">
            <div
              class="relative w-full flex rounded-md overflow-hidden border-2 transition-colors duration-200 bg-white"
              :class="[
                isComparePage ? 'border-neutral-800' : 'border-[#32cd32]',
                isSearchFocused ? 'ring-2 ring-green-100' : ''
              ]"
            >
              <div class="relative">
                <button
                  :aria-expanded="isTypeMenuOpen"
                  aria-haspopup="listbox"
                  aria-label="Pilih tipe pencarian"
                  class="h-full bg-white px-3 py-2.5 text-sm font-bold text-gray-700 border-r border-gray-200 flex items-center gap-1.5 hover:bg-gray-50 whitespace-nowrap min-w-[100px] justify-between"
                  @click="isTypeMenuOpen = !isTypeMenuOpen"
                >
                  {{ selectedTypeLabel }}
                  <UIcon name="i-heroicons-chevron-down" class="w-3.5 h-3.5 text-gray-400" aria-hidden="true" />
                </button>
                <div
                  v-if="isTypeMenuOpen"
                  role="listbox"
                  class="absolute top-full left-0 mt-1 w-[130px] bg-white border border-gray-100 shadow-lg rounded-lg py-1 z-50"
                >
                  <button
                    v-for="opt in searchOptions"
                    :key="opt.value"
                    role="option"
                    :aria-selected="selectedSearchType === opt.value"
                    class="w-full text-left px-4 py-2 text-sm font-semibold hover:bg-green-50 hover:text-green-700 transition-colors"
                    :class="selectedSearchType === opt.value ? 'text-green-600 bg-green-50/50' : 'text-gray-700'"
                    @click="selectSearchType(opt)"
                  >
                    {{ opt.label }}
                  </button>
                </div>
              </div>

              <input
                v-model="searchQuery"
                type="search"
                placeholder="Cari perangkat keamanan..."
                autocomplete="off"
                aria-label="Cari produk"
                class="w-full bg-transparent px-4 py-2.5 text-sm font-medium focus:outline-none text-gray-800"
                @focus="isSearchFocused = true; isTypeMenuOpen = false"
                @keyup.enter="handleSearchSubmit(searchQuery)"
              />

              <div v-if="isSearching" class="absolute right-16 top-1/2 -translate-y-1/2" aria-hidden="true">
                <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 text-gray-400 animate-spin" />
              </div>

              <button
                :aria-label="`Cari ${searchQuery || 'produk'}`"
                class="text-white px-5 flex items-center justify-center transition-colors duration-200"
                :class="isComparePage ? 'bg-neutral-800 hover:bg-neutral-900' : 'bg-[#32cd32] hover:bg-green-600'"
                @click="handleSearchSubmit(searchQuery)"
              >
                <UIcon name="i-heroicons-magnifying-glass" class="w-5 h-5" aria-hidden="true" />
              </button>
            </div>

            <Transition
              enter-active-class="transition duration-150 ease-out"
              enter-from-class="-translate-y-2 opacity-0"
              enter-to-class="translate-y-0 opacity-100"
              leave-active-class="transition duration-100 ease-in"
              leave-from-class="translate-y-0 opacity-100"
              leave-to-class="-translate-y-2 opacity-0"
            >
              <div
                v-if="isSearchFocused"
                class="absolute top-[110%] left-0 w-full bg-white border border-gray-100 shadow-2xl rounded-xl overflow-hidden flex flex-col z-50 max-h-[520px] overflow-y-auto custom-scrollbar"
                role="listbox"
                aria-label="Hasil pencarian"
              >
                <div v-if="searchQuery.length < 2" class="p-4">
                  <h4 class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                    <UIcon name="i-heroicons-fire" class="w-3.5 h-3.5 text-red-500" aria-hidden="true" />
                    Trending
                  </h4>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="trend in trendingSearches"
                      :key="trend"
                      class="text-xs bg-gray-50 border border-gray-100 hover:border-green-300 hover:bg-green-50 hover:text-green-700 px-3 py-1.5 rounded-lg transition-all font-bold text-gray-600"
                      @click="handleSearchSubmit(trend)"
                    >
                      {{ trend }}
                    </button>
                  </div>
                </div>

                <template v-else-if="searchResults">
                  <div v-if="searchResults.suggestion" class="px-4 py-2.5 border-b border-gray-50 bg-yellow-50/60">
                    <p class="text-xs text-gray-600 font-medium">
                      Mungkin maksud Anda:
                      <button class="font-bold text-[#32cd32] hover:underline" @click="handleSearchSubmit(searchResults.suggestion!)">
                        {{ searchResults.suggestion }}
                      </button>?
                    </p>
                  </div>
                  <div v-if="searchResults.categories?.length" class="px-4 py-2.5 border-b border-gray-50">
                    <h4 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Kategori</h4>
                    <div class="flex gap-1.5 flex-wrap">
                      <button
                        v-for="cat in searchResults.categories"
                        :key="cat"
                        class="text-xs bg-gray-100 hover:bg-green-50 hover:text-green-700 px-3 py-1 rounded-full transition-colors font-bold text-gray-600"
                        @click="goToCategory(cat)"
                      >
                        {{ cat.replace(/-/g, ' ') }}
                      </button>
                    </div>
                  </div>
                  <div v-if="searchResults.brands?.length" class="px-4 py-2.5 border-b border-gray-50">
                    <h4 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Brand</h4>
                    <div class="flex gap-1.5 flex-wrap">
                      <button
                        v-for="b in searchResults.brands"
                        :key="b"
                        class="text-xs border border-gray-200 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-700 px-3 py-1 rounded-lg transition-colors font-bold text-gray-700"
                        @click="goToBrand(b)"
                      >
                        {{ b }}
                      </button>
                    </div>
                  </div>
                  <div v-if="searchResults.items?.length" class="p-2">
                    <h4 class="px-3 pt-1 pb-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Produk</h4>
                    <NuxtLink
                      v-for="item in searchResults.items"
                      :key="item.uuid"
                      :to="`/product/${item.uuid}`"
                      class="flex items-center gap-3 p-2.5 hover:bg-gray-50 rounded-xl transition-colors group"
                      @click="closeSearch"
                    >
                      <div class="w-11 h-11 bg-white border border-gray-100 rounded-lg overflow-hidden flex-shrink-0 flex items-center justify-center p-1">
                        <NuxtImg
                          v-if="item.image"
                          :src="item.image"
                          :alt="item.title"
                          width="44"
                          height="44"
                          format="webp"
                          class="w-full h-full object-contain mix-blend-multiply"
                          loading="lazy"
                        />
                        <UIcon v-else name="i-heroicons-photo" class="w-5 h-5 text-gray-300" aria-hidden="true" />
                      </div>
                      <div class="flex flex-col flex-1 min-w-0">
                        <span class="text-sm font-bold text-gray-800 group-hover:text-[#32cd32] truncate transition-colors">{{ item.title }}</span>
                        <span class="text-xs text-red-600 font-black">Rp {{ item.price.toLocaleString('id-ID') }}</span>
                      </div>
                    </NuxtLink>
                  </div>
                  <div v-if="!searchResults.items?.length && !searchResults.suggestion && !isSearching" class="p-8 text-center flex flex-col items-center">
                    <UIcon name="i-heroicons-magnifying-glass" class="w-8 h-8 text-gray-200 mb-2" aria-hidden="true" />
                    <span class="text-gray-500 text-sm font-medium">Tidak ditemukan untuk "<strong class="text-black">{{ searchQuery }}</strong>"</span>
                  </div>
                  <button
                    v-if="searchResults.items?.length"
                    class="w-full p-3.5 text-xs font-black text-center text-[#32cd32] bg-green-50/50 hover:bg-green-100 transition-colors border-t border-green-100 uppercase tracking-widest"
                    @click="handleSearchSubmit(searchQuery)"
                  >
                    Lihat Semua Hasil
                  </button>
                </template>
              </div>
            </Transition>
          </div>

          <div class="flex items-center gap-4 lg:gap-5 flex-shrink-0">
            <div class="relative inline-flex">
              <UserDropdown />
              <span
                v-if="notificationStore.unreadCount > 0"
                class="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 bg-red-500 text-white text-[10px] font-black rounded-full flex items-center justify-center border-2 border-white shadow-sm pointer-events-none z-10"
              >
                {{ notificationStore.unreadCount > 9 ? '9+' : notificationStore.unreadCount }}
              </span>
            </div>
            
            <Whitlish  />
            <ClientOnly>
              <Cart />
            </ClientOnly>
          </div>
        </div>
      </nav>

      <div class="bg-white border-b border-gray-200 relative z-20">
        <div class="max-w-[1400px] mx-auto px-4 lg:px-10 flex items-center gap-8 py-0">
          <CategoryMenu ref="categoryMenuRef" class="flex-shrink-0" />
          <div class="flex items-center gap-8 text-[13px] font-bold text-gray-700 overflow-x-auto no-scrollbar py-3">
            <div @mouseenter="openBrandMenu" @mouseleave="closeBrandMenu">
              <NuxtLink to="/brands" class="nav-link" :class="isComparePage ? 'hover:text-red-600' : 'hover:text-[#32cd32]'">Brand</NuxtLink>
            </div>
            <NuxtLink to="/about" class="nav-link" :class="isComparePage ? 'hover:text-red-600' : 'hover:text-[#32cd32]'">Tentang Kami</NuxtLink>
            <NuxtLink to="/search" class="nav-link" :class="isComparePage ? 'hover:text-red-600' : 'hover:text-[#32cd32]'">Belanja</NuxtLink>
            <NuxtLink to="/blog" class="nav-link" :class="isComparePage ? 'hover:text-red-600' : 'hover:text-[#32cd32]'">Artikel</NuxtLink>
            <NuxtLink to="/services/booking" class="nav-link" :class="isComparePage ? 'hover:text-red-600' : 'hover:text-[#32cd32]'">Maintenense & Service</NuxtLink>
            <NuxtLink to="/contact" class="nav-link" :class="isComparePage ? 'hover:text-red-600' : 'hover:text-[#32cd32]'">Kontak</NuxtLink>
            <NuxtLink 
              to="/promo"
              class="flex items-center gap-1.5 transition-colors group"
              :class="isComparePage ? 'hover:text-red-600' : 'hover:text-[#32cd32]'"
            >
              <UIcon name="i-heroicons-receipt-percent" class="w-4 h-4 text-gray-400 group-hover:text-[#32cd32]" aria-hidden="true" />
              Diskon Unggulan
            </NuxtLink>
          </div>
        </div>
      </div>

      <BrandPop :is-open="isBrandMenuOpen" @mouseenter="openBrandMenu" @mouseleave="closeBrandMenu" />
    </header>

    <header class="lg:hidden sticky top-0 z-50 bg-white border-b border-gray-100 shadow-sm">
      <div class="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-2.5">
        
        <button
          class="p-1.5 text-gray-600 hover:bg-gray-100 rounded-md transition-colors flex-shrink-0"
          @click="isMobileMenuOpen = true"
          aria-label="Buka Menu Sidebar"
        >
          <UIcon name="i-heroicons-bars-3" class="w-5 h-5 sm:w-6 sm:h-6" aria-hidden="true" />
        </button>

        <NuxtLink to="/" aria-label="Beranda" class="flex-shrink-0 hidden min-[360px]:block mr-1">
          <NuxtImg
            src="/pasarcctv.png"
            alt="Padjajaran CCTV"
            format="webp"
            width="70"
            height="28"
            class="h-6 sm:h-7 w-auto object-contain"
            loading="eager"
            fetchpriority="high"
          />
        </NuxtLink>

        <button
          class="flex-1 flex items-center gap-1.5 bg-gray-100 rounded-xl px-2 sm:px-2.5 py-1.5 text-left min-w-0"
          aria-label="Cari produk"
          @click="isMobileSearchOpen = true"
        >
          <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4 text-gray-400 flex-shrink-0" aria-hidden="true" />
          <span class="text-[11px] sm:text-sm text-gray-400 font-medium truncate">Cari di Padjajaran...</span>
        </button>

        <NuxtLink 
          to="/dashboard/notifications" 
          class="relative p-1.5 text-gray-600 hover:bg-gray-100 rounded-md transition-colors flex-shrink-0" 
          aria-label="Notifikasi"
        >
          <UIcon name="i-heroicons-bell" class="w-5 h-5 sm:w-6 sm:h-6" aria-hidden="true" />
          <span v-if="notificationStore.unreadCount > 0" class="absolute top-0.5 right-0.5 min-w-[14px] h-[14px] bg-red-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center px-0.5 border border-white">
            {{ notificationStore.unreadCount > 9 ? '9+' : notificationStore.unreadCount }}
          </span>
        </NuxtLink>

        <Cart class="flex-shrink-0" />
      </div>
    </header>

    <Teleport to="body">
      <Transition name="fade-overlay">
        <div
          v-if="isMobileMenuOpen"
          class="fixed inset-0 z-[250] bg-gray-900/60 backdrop-blur-sm flex lg:hidden"
          @click.self="isMobileMenuOpen = false"
        >
          <Transition name="slide-left" appear>
            <div class="bg-white w-[80vw] max-w-[300px] h-full flex flex-col shadow-2xl">
              
              <div class="flex items-center justify-between px-4 py-4 border-b border-gray-100 bg-white">
                <NuxtImg src="/pasarcctv.png" alt="Logo" class="h-6 w-auto object-contain" />
                <button
                  class="p-1 rounded-full text-gray-500 hover:bg-gray-100 transition-colors"
                  @click="isMobileMenuOpen = false"
                >
                  <UIcon name="i-heroicons-x-mark" class="w-6 h-6" />
                </button>
              </div>

              <div class="flex-1 overflow-y-auto py-2 custom-scrollbar">
                
                <div class="px-5 py-2">
                  <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Eksplorasi</span>
                </div>
                
                <NuxtLink to="/promo" class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors" @click="isMobileMenuOpen = false">
                  <UIcon name="i-heroicons-receipt-percent" class="w-5 h-5 text-red-500" />
                  <span class="text-[13px] font-bold text-gray-800">Diskon Unggulan</span>
                  <span class="ml-auto bg-red-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">Promo</span>
                </NuxtLink>

                <NuxtLink to="/search" class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors" @click="isMobileMenuOpen = false">
                  <UIcon name="i-heroicons-shopping-bag" class="w-5 h-5 text-gray-400" />
                  <span class="text-[13px] font-bold text-gray-800">Belanja</span>
                </NuxtLink>

                <NuxtLink to="/dashboard/orders" class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors" @click="isMobileMenuOpen = false">
                  <UIcon name="i-heroicons-cube" class="w-5 h-5 text-gray-400" />
                  <span class="text-[13px] font-bold text-gray-800">Pesanan Saya</span>
                </NuxtLink>
                
                <NuxtLink to="/services/booking" class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors" @click="isMobileMenuOpen = false">
                  <UIcon name="i-heroicons-wrench-screwdriver" class="w-5 h-5 text-gray-400" />
                  <span class="text-[13px] font-bold text-gray-800">Maintenense & Service</span>
                </NuxtLink>
                
                <NuxtLink to="/brands" class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors" @click="isMobileMenuOpen = false">
                  <UIcon name="i-heroicons-star" class="w-5 h-5 text-gray-400" />
                  <span class="text-[13px] font-bold text-gray-800">Brand Kami</span>
                </NuxtLink>

                <div class="h-px bg-gray-100 my-2 mx-5"></div>

                <div class="px-5 py-2">
                  <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Informasi</span>
                </div>
                
                <NuxtLink to="/blog" class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors" @click="isMobileMenuOpen = false">
                  <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-gray-400" />
                  <span class="text-[13px] font-bold text-gray-800">Artikel & Panduan</span>
                </NuxtLink>
                
                <NuxtLink to="/about" class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors" @click="isMobileMenuOpen = false">
                  <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-gray-400" />
                  <span class="text-[13px] font-bold text-gray-800">Tentang Kami</span>
                </NuxtLink>
                
                <NuxtLink to="/contact" class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50 transition-colors" @click="isMobileMenuOpen = false">
                  <UIcon name="i-heroicons-phone" class="w-5 h-5 text-gray-400" />
                  <span class="text-[13px] font-bold text-gray-800">Kontak Support</span>
                </NuxtLink>
              </div>

            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-2"
      >
        <div
          v-if="isMobileSearchOpen"
          class="fixed inset-0 z-[200] bg-white flex flex-col lg:hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Pencarian produk"
        >
          <div class="flex items-center gap-2 px-3 py-3 border-b border-gray-100">
            <button
              class="p-2 rounded-full hover:bg-gray-100 transition-colors flex-shrink-0"
              aria-label="Tutup pencarian"
              @click="isMobileSearchOpen = false; searchQuery = ''"
            >
              <UIcon name="i-heroicons-arrow-left" class="w-5 h-5 text-gray-700" aria-hidden="true" />
            </button>

            <div class="flex-1 flex items-center gap-2 bg-gray-100 rounded-xl px-3 py-2">
              <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4 text-gray-400 flex-shrink-0" aria-hidden="true" />
              <input
                ref="mobileSearchInputRef"
                v-model="searchQuery"
                type="search"
                placeholder="Cari produk, brand, kategori..."
                autocomplete="off"
                class="flex-1 bg-transparent text-sm font-medium text-gray-800 focus:outline-none"
                @keyup.enter="handleSearchSubmit(searchQuery); isMobileSearchOpen = false"
              />
              <button
                v-if="searchQuery"
                class="p-0.5"
                aria-label="Hapus pencarian"
                @click="searchQuery = ''"
              >
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4 text-gray-400" aria-hidden="true" />
              </button>
            </div>

            <button
              class="text-white bg-[#32cd32] px-4 py-2 rounded-xl text-sm font-bold flex-shrink-0 transition-colors hover:bg-green-600"
              @click="handleSearchSubmit(searchQuery); isMobileSearchOpen = false"
            >
              Cari
            </button>
          </div>

          <div class="flex-1 overflow-y-auto">
            <div v-if="searchQuery.length < 2" class="p-4">
              <h4 class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                <UIcon name="i-heroicons-fire" class="w-3.5 h-3.5 text-red-500" aria-hidden="true" />
                Trending
              </h4>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="trend in trendingSearches"
                  :key="trend"
                  class="text-xs bg-gray-50 border border-gray-100 hover:border-green-300 hover:bg-green-50 hover:text-green-700 px-3 py-2 rounded-lg font-bold text-gray-600 transition-all"
                  @click="handleSearchSubmit(trend); isMobileSearchOpen = false"
                >
                  {{ trend }}
                </button>
              </div>
            </div>

            <template v-else-if="searchResults">
              <div v-if="searchResults.suggestion" class="px-4 py-3 bg-yellow-50 border-b border-yellow-100">
                <p class="text-sm text-gray-600">
                  Mungkin: <button class="font-bold text-[#32cd32]" @click="handleSearchSubmit(searchResults.suggestion!); isMobileSearchOpen = false">{{ searchResults.suggestion }}</button>
                </p>
              </div>
              <div v-if="searchResults.categories?.length" class="px-4 py-3 border-b border-gray-50">
                <h4 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Kategori</h4>
                <div class="flex gap-2 flex-wrap">
                  <button
                    v-for="cat in searchResults.categories"
                    :key="cat"
                    class="text-xs bg-gray-100 px-3 py-1.5 rounded-full font-bold text-gray-700"
                    @click="goToCategory(cat); isMobileSearchOpen = false"
                  >
                    {{ cat.replace(/-/g, ' ') }}
                  </button>
                </div>
              </div>
              <div v-if="searchResults.brands?.length" class="px-4 py-3 border-b border-gray-50">
                <h4 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Brand</h4>
                <div class="flex gap-2 flex-wrap">
                  <button
                    v-for="b in searchResults.brands"
                    :key="b"
                    class="text-xs border border-gray-200 px-3 py-1.5 rounded-lg font-bold text-gray-700"
                    @click="goToBrand(b); isMobileSearchOpen = false"
                  >
                    {{ b }}
                  </button>
                </div>
              </div>
              <div v-if="searchResults.items?.length">
                <h4 class="px-4 pt-3 pb-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Produk</h4>
                <NuxtLink
                  v-for="item in searchResults.items"
                  :key="item.uuid"
                  :to="`/product/${item.uuid}`"
                  class="flex items-center gap-3 px-4 py-3 border-b border-gray-50 active:bg-gray-50"
                  @click="isMobileSearchOpen = false; searchQuery = ''"
                >
                  <div class="w-12 h-12 bg-gray-50 rounded-xl border border-gray-100 flex-shrink-0 flex items-center justify-center p-1.5">
                    <NuxtImg
                      v-if="item.image"
                      :src="item.image"
                      :alt="item.title"
                      width="48"
                      height="48"
                      format="webp"
                      class="w-full h-full object-contain mix-blend-multiply"
                      loading="lazy"
                    />
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-bold text-gray-800 truncate">{{ item.title }}</p>
                    <p class="text-sm font-black text-red-600">Rp {{ item.price.toLocaleString('id-ID') }}</p>
                  </div>
                  <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-300 flex-shrink-0" aria-hidden="true" />
                </NuxtLink>
              </div>
              <div v-if="!searchResults.items?.length && !isSearching" class="p-10 text-center">
                <UIcon name="i-heroicons-magnifying-glass" class="w-10 h-10 text-gray-200 mx-auto mb-3" aria-hidden="true" />
                <p class="text-gray-500 text-sm font-medium">Tidak ditemukan untuk "<strong class="text-black">{{ searchQuery }}</strong>"</p>
              </div>
            </template>

            <div v-if="isSearching" class="flex justify-center py-8">
              <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-green-500 animate-spin" aria-hidden="true" />
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <nav
      class="lg:hidden fixed bottom-0 inset-x-0 z-50 bg-white border-t border-gray-100 bottom-nav"
      aria-label="Navigasi utama"
      role="navigation"
    >
      <div class="flex items-stretch h-[62px] pb-safe">

        <NuxtLink
          to="/"
          class="bottom-nav__item"
          :class="isActiveRoute('/') ? 'bottom-nav__item--active' : ''"
          aria-label="Beranda"
        >
          <UIcon
            :name="isActiveRoute('/') ? 'i-heroicons-home-solid' : 'i-heroicons-home'"
            class="bottom-nav__icon"
            aria-hidden="true"
          />
          <span class="bottom-nav__label">Beranda</span>
        </NuxtLink>

        <button
          class="bottom-nav__item"
          :class="isActiveRoute('/category') ? 'bottom-nav__item--active' : ''"
          aria-label="Buka kategori"
          @click="categoryMenuRef?.openMobileSidebar()"
        >
          <UIcon
            :name="isActiveRoute('/category') ? 'i-heroicons-squares-2x2-solid' : 'i-heroicons-squares-2x2'"
            class="bottom-nav__icon"
            aria-hidden="true"
          />
          <span class="bottom-nav__label">Kategori</span>
        </button>

        <button
          class="bottom-nav__cta"
          aria-label="Cari produk"
          @click="isMobileSearchOpen = true"
        >
          <div class="bottom-nav__cta-inner">
            <UIcon name="i-heroicons-magnifying-glass" class="w-6 h-6 text-white" aria-hidden="true" />
          </div>
        </button>

        <NuxtLink
          to="/wishlist"
          class="bottom-nav__item relative"
          :class="isActiveRoute('/wishlist') ? 'bottom-nav__item--active' : ''"
          aria-label="Wishlist"
        >
          <div class="relative">
            <UIcon
              :name="isActiveRoute('/wishlist') ? 'i-heroicons-heart-solid' : 'i-heroicons-heart'"
              class="bottom-nav__icon"
              aria-hidden="true"
            />
            <span
              v-if="wishlistCount > 0"
              class="absolute -top-1.5 -right-2 min-w-[16px] h-4 bg-red-500 text-white text-[9px] font-black rounded-full flex items-center justify-center px-1"
            >
              {{ wishlistCount > 9 ? '9+' : wishlistCount }}
            </span>
          </div>
          <span class="bottom-nav__label">Wishlist</span>
        </NuxtLink>

        <NuxtLink
          to="/dashboard"
          class="bottom-nav__item"
          :class="isActiveRoute('/dashboard') ? 'bottom-nav__item--active' : ''"
          aria-label="Akun saya"
        >
          <div class="relative">
            <UIcon
              :name="isActiveRoute('/dashboard') ? 'i-heroicons-user-solid' : 'i-heroicons-user'"
              class="bottom-nav__icon"
              aria-hidden="true"
            />
            <span
              v-if="notificationStore.unreadCount > 0"
              class="absolute -top-1.5 -right-2 min-w-[16px] h-4 bg-red-500 text-white text-[9px] font-black rounded-full flex items-center justify-center px-1"
            >
              {{ notificationStore.unreadCount > 9 ? '9+' : notificationStore.unreadCount }}
            </span>
          </div>
          <span class="bottom-nav__label">Akun</span>
        </NuxtLink>

      </div>
    </nav>

  

    <Teleport to="body">
      <Transition
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="activeToast"
          class="fixed top-20 right-4 md:top-24 md:right-8 z-[9999] w-[90vw] max-w-sm rounded-xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.2)] border overflow-hidden pointer-events-auto flex flex-col bg-white"
          :class="isToastWarning ? 'border-red-200' : 'border-gray-200'"
        >
          <div class="p-4 flex items-start gap-3" :class="isToastWarning ? 'bg-red-50' : 'bg-white'">
            <div class="flex-shrink-0 mt-0.5">
              <div v-if="isToastWarning" class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-600">
                <UIcon name="i-heroicons-exclamation-triangle-solid" class="w-5 h-5" aria-hidden="true" />
              </div>
              <div v-else class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-[#32cd32]">
                <UIcon name="i-heroicons-bell-alert-solid" class="w-5 h-5" aria-hidden="true" />
              </div>
            </div>
            
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-bold truncate" :class="isToastWarning ? 'text-red-800' : 'text-gray-900'">
                {{ activeToast.title }}
              </h3>
              <p class="mt-1 text-xs line-clamp-2" :class="isToastWarning ? 'text-red-600' : 'text-gray-600'">
                {{ activeToast.content }}
              </p>
            </div>
            
            <button @click="closeToast" class="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors p-1" aria-label="Tutup notifikasi">
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5" aria-hidden="true" />
            </button>
          </div>

          <div class="h-1 w-full bg-gray-100 absolute bottom-0 left-0">
            <div class="h-full toast-progress" :class="isToastWarning ? 'bg-red-500' : 'bg-[#32cd32]'"></div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CategoryMenu from '~/components/CategoryMenu.vue'
import BrandPop from '~/components/brands/BrandPop.vue'
import Whitlish from './header/whitlish.vue'
import Cart from './header/Cart.vue'

// Import Notification Store
import { useNotificationStore } from '~/stores/notificationStore'

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()

// ─── UI state ────────────────────────────────────────────────────
const isScrolled = ref(false)
const isBrandMenuOpen = ref(false)
const isMobileSearchOpen = ref(false)
const isMobileMenuOpen = ref(false) // <--- Sidebar State di-inject ulang
const categoryMenuRef = ref<InstanceType<typeof CategoryMenu> | null>(null)
const searchContainerRef = ref<HTMLElement | null>(null)
const mobileSearchInputRef = ref<HTMLInputElement | null>(null)
const wishlistCount = ref(3)
let hoverTimeout: ReturnType<typeof setTimeout> | null = null

// ─── Toast Notification Logic ────────────────────────────────────
const activeToast = ref<any>(null)
let toastTimeout: ReturnType<typeof setTimeout> | null = null
let lastSeenId = 0

// Evaluasi warna warning untuk popup toast
const isToastWarning = computed(() => {
  if (!activeToast.value) return false
  const title = (activeToast.value.title || '').toLowerCase()
  const type = (activeToast.value.type || '').toLowerCase()
  return title.includes('warning') || type === 'warning'
})

const showToast = (notif: any) => {
  activeToast.value = notif
  if (toastTimeout) clearTimeout(toastTimeout)
  
  // Timer otomatis hide setelah 5 detik
  toastTimeout = setTimeout(() => {
    activeToast.value = null
  }, 5000)
}

const closeToast = () => {
  activeToast.value = null
  if (toastTimeout) clearTimeout(toastTimeout)
}

// Watcher untuk ngecek notif real-time baru
watch(() => notificationStore.notifications, (newNotifs) => {
  if (!newNotifs || newNotifs.length === 0) return

  const latestNotif = newNotifs[0]

  if (lastSeenId === 0) {
    lastSeenId = Math.max(...newNotifs.map(n => n.id))
    return
  }

  if (latestNotif.id > lastSeenId) {
    lastSeenId = latestNotif.id
    activeToast.value = null
    setTimeout(() => {
      showToast(latestNotif)
    }, 50)
  }
}, { deep: true })

// ─── Search state ────────────────────────────────────────────────
const searchQuery = ref('')
const isSearchFocused = ref(false)
const isSearching = ref(false)
const searchResults = ref<{
  suggestion: string | null
  categories: string[]
  brands: string[]
  items: any[]
} | null>(null)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

const searchOptions = [
  { label: 'Semua', value: 'all' },
  { label: 'Produk', value: 'produk' },
  { label: 'Kategori', value: 'kategori' },
  { label: 'Brand', value: 'brand' },
]
const selectedSearchType = ref('all')
const selectedTypeLabel = computed(
  () => searchOptions.find((o) => o.value === selectedSearchType.value)?.label || 'Semua'
)
const isTypeMenuOpen = ref(false)

const isComparePage = computed(() => route.path === '/compare')

// Active route helper untuk bottom nav
const isActiveRoute = (path: string) =>
  path === '/' ? route.path === '/' : route.path.startsWith(path)

// ─── Trending ────────────────────────────────────────────────────
const { data: trendingSearches } = await useFetch('/api/trending', {
  lazy: true,
  key: 'trending',
  getCachedData: (key, nuxtApp) => nuxtApp.payload.data[key] ?? nuxtApp.static.data[key],
})

// ─── Search logic ────────────────────────────────────────────────
const closeSearch = () => {
  isSearchFocused.value = false
  isTypeMenuOpen.value = false
}

const selectSearchType = (opt: { label: string; value: string }) => {
  selectedSearchType.value = opt.value
  isTypeMenuOpen.value = false
  if (searchQuery.value.length >= 2) triggerSearch()
}

const handleSearchSubmit = (q: string) => {
  if (!q.trim()) return
  closeSearch()
  if (selectedSearchType.value === 'brand') {
    router.push({ path: `/brands/${q.toLowerCase().replace(/\s+/g, '-')}` })
  } else {
    router.push({
      path: '/search',
      query: {
        q,
        type: selectedSearchType.value !== 'all' ? selectedSearchType.value : undefined,
      },
    })
  }
}

const goToCategory = (slug: string) => { closeSearch(); router.push(`/category/${slug}`) }
const goToBrand = (name: string) => { closeSearch(); router.push(`/brands/${name.toLowerCase().replace(/\s+/g, '-')}`) }

const triggerSearch = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  isSearching.value = true
  debounceTimer = setTimeout(async () => {
    try {
      const data = await $fetch('/api/smartsearchbar', {
        params: { q: searchQuery.value, type: selectedSearchType.value },
      })
      searchResults.value = data as any
    } catch {
      // silent fail
    } finally {
      isSearching.value = false
    }
  }, 350)
}

watch(searchQuery, (q) => {
  if (q.length < 2) { searchResults.value = null; isSearching.value = false; return }
  triggerSearch()
})

// Auto-focus input saat mobile search dibuka
watch(isMobileSearchOpen, async (open) => {
  if (open) {
    await nextTick()
    mobileSearchInputRef.value?.focus()
  } else {
    searchQuery.value = ''
    searchResults.value = null
  }
})

// Menutup seluruh modal overlay ketika navigasi berpindah URL (Route Change)
watch(() => route.path, () => {
  closeSearch()
  isMobileSearchOpen.value = false
  isMobileMenuOpen.value = false
  if (categoryMenuRef.value?.isOpen) categoryMenuRef.value.isOpen = false
})

// ─── Scroll & click outside ──────────────────────────────────────
const handleClickOutside = (e: MouseEvent) => {
  if (searchContainerRef.value && !searchContainerRef.value.contains(e.target as Node)) closeSearch()
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 0
}

const openBrandMenu = () => {
  if (hoverTimeout) clearTimeout(hoverTimeout)
  isBrandMenuOpen.value = true
  if (categoryMenuRef.value?.isOpen) categoryMenuRef.value.isOpen = false
}
const closeBrandMenu = () => {
  hoverTimeout = setTimeout(() => { isBrandMenuOpen.value = false }, 150)
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  document.addEventListener('click', handleClickOutside)
  notificationStore.init()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('click', handleClickOutside)
  if (debounceTimer) clearTimeout(debounceTimer)
  if (hoverTimeout) clearTimeout(hoverTimeout)
  if (toastTimeout) clearTimeout(toastTimeout)
})
</script>

<style scoped>
@reference "~/assets/main.css";

.nav-link {
  @apply relative transition-colors duration-200;
}

/* ── Floating Overlay Transitions (Sidebar Mobile) ────────────── */
.fade-overlay-enter-active, .fade-overlay-leave-active { transition: opacity 0.3s ease; }
.fade-overlay-enter-from, .fade-overlay-leave-to { opacity: 0; }

.slide-left-enter-active, .slide-left-leave-active { transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-left-enter-from, .slide-left-leave-to { transform: translateX(-100%); }

/* ── Animasi Toast Notification Progress ───────────────────────── */
.toast-progress {
  animation: shrink-progress 5s linear forwards;
}

@keyframes shrink-progress {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

/* ── Bottom nav ───────────────────────────────────────────────── */
.bottom-nav {
  /* Glassmorphism ringan */
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 -1px 0 rgba(0,0,0,0.06), 0 -4px 16px rgba(0,0,0,0.04);
}

.bottom-nav__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 6px 0;
  color: #9ca3af;
  text-decoration: none;
  transition: color 0.15s;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.bottom-nav__item--active {
  color: #22c55e;
}

.bottom-nav__icon {
  width: 1.375rem;
  height: 1.375rem;
  transition: transform 0.15s;
}

.bottom-nav__item:active .bottom-nav__icon {
  transform: scale(0.88);
}

.bottom-nav__label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.01em;
  line-height: 1;
}

/* CTA tengah — floating button efek */
.bottom-nav__cta {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  padding-bottom: 8px;
}

.bottom-nav__cta-inner {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #32cd32 0%, #22a622 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(50, 205, 50, 0.4);
  transition: transform 0.15s, box-shadow 0.15s;
}

.bottom-nav__cta:active .bottom-nav__cta-inner {
  transform: scale(0.9);
  box-shadow: 0 2px 8px rgba(50, 205, 50, 0.3);
}

/* iOS safe area bottom */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

/* Scrollbar utilities */
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 10px; }
</style>