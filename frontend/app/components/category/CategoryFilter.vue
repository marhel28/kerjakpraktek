<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRoute } from "vue-router";

const props = defineProps<{
  search: string;
  selected: string[];
  price: number[];
  dynamicSuggests?: string[];
}>();

const emit = defineEmits(["update:search", "update:selected", "update:price"]);

const route = useRoute();

// 🔥 Cek apakah URL saat ini adalah halaman /popular
const isPopularRoute = computed(() => {
  return route.path.toLowerCase().includes("/popular");
});

const displaySuggests = computed(() => {
  if (props.dynamicSuggests && props.dynamicSuggests.length > 0) {
    return props.dynamicSuggests;
  }
  return ["CCTV Outdoor", "DVR 8 Channel", "Kabel RG59", "IP Camera", "Hikvision"];
});

const applyPopularSearch = (term: string) => {
  emit("update:search", term);
};

// ==========================================
// 🚀 FETCH DATA KATEGORI
// ==========================================
const { data: categoryMenu, pending } = await useFetch("/api/category", {
  transform: (res: any) => {
    const apiData = Array.isArray(res) ? res : res?.data || [];
    return apiData.map((cat: any) => ({
      id: cat.slug,
      label: cat.name,
      icon: cat.icon_name || "i-heroicons-folder",
      subs: (cat.subcategories || []).map((sub: any) => ({
        id: sub.slug,
        label: sub.name,
      })),
    }));
  },
  default: () => [],
});

// ==========================================
// 🌟 1. ROUTE WATCHER (Sync awal dari URL)
// ==========================================
let lastProcessedPath = "";

watch(
  () => [route.path, categoryMenu.value],
  ([newPath, menu]) => {
    if (!menu || (menu as any[]).length === 0) return;
    if (isPopularRoute.value) return;

    // Cegah infinite loop, hanya jalan saat rute benar-benar ganti
    if (newPath === lastProcessedPath) return;
    lastProcessedPath = newPath as string;

    const urlSegments = (newPath as string).toLowerCase().split("/").filter(Boolean);
    const urlSelected = new Set<string>();

    (menu as any[]).forEach((cat) => {
      // Jika Parent ada di URL
      if (urlSegments.includes(cat.id.toLowerCase())) {
        urlSelected.add(cat.id);
      }
      // Jika Child ada di URL
      cat.subs.forEach((sub: any) => {
        if (urlSegments.includes(sub.id.toLowerCase())) {
          urlSelected.add(sub.id);
          urlSelected.add(cat.id); // Paksa Parent ikut
        }
      });
    });

    if (urlSelected.size > 0) {
      const mergedSelection = new Set([...props.selected, ...urlSelected]);
      emit("update:selected", Array.from(mergedSelection));
    }
  },
  { immediate: true }
);

// ==========================================
// 🌟 2. SELF-HEALING STATE (Anti-Bug Parent)
// ==========================================
watch(
  () => props.selected,
  (currentSelected) => {
    if (!categoryMenu.value || categoryMenu.value.length === 0) return;

    const fixedSelection = new Set(currentSelected);
    let needsFix = false;

    categoryMenu.value.forEach((cat) => {
      const hasActiveChild = cat.subs.some((sub: any) => fixedSelection.has(sub.id));

      if (hasActiveChild && !fixedSelection.has(cat.id)) {
        fixedSelection.add(cat.id);
        needsFix = true;
      }
    });

    if (needsFix) {
      emit("update:selected", Array.from(fixedSelection));
    }
  },
  { deep: true }
);

// ==========================================
// ⚙️ LOGIKA FILTERING (Manual Click)
// ==========================================
const toggleCategory = (id: string) => {
  let newSelected = [...props.selected];
  const index = newSelected.indexOf(id);

  if (index > -1) {
    // 1. UNCHECK
    newSelected.splice(index, 1);

    if (categoryMenu.value) {
      const parentCat = categoryMenu.value.find((c: any) => c.id === id);
      if (parentCat) {
        parentCat.subs.forEach((sub: any) => {
          const subIndex = newSelected.indexOf(sub.id);
          if (subIndex > -1) newSelected.splice(subIndex, 1);
        });
      }
    }
  } else {
    // 2. CHECK
    newSelected.push(id);

    if (categoryMenu.value) {
      for (const cat of categoryMenu.value) {
        const isChild = cat.subs.some((sub: any) => sub.id === id);
        if (isChild && !newSelected.includes(cat.id)) {
          newSelected.push(cat.id); // Centang parent juga
        }
      }
    }
  }

  emit("update:selected", newSelected);
};

const updatePrice = (val: number, type: "min" | "max") => {
  const newPrice = [...props.price];
  if (type === "min") newPrice[0] = val > newPrice[1] ? newPrice[1] : val;
  else newPrice[1] = val < newPrice[0] ? newPrice[0] : val;
  emit("update:price", newPrice);
};

const expandedCategories = ref<string[]>([]);

// Auto-expand menu accordion
watch(
  () => props.selected,
  (newSelected) => {
    if (!categoryMenu.value) return;
    categoryMenu.value.forEach((cat) => {
      const hasSelectedChild = cat.subs.some((sub: any) => newSelected.includes(sub.id));
      if (
        (newSelected.includes(cat.id) || hasSelectedChild) &&
        !expandedCategories.value.includes(cat.id)
      ) {
        expandedCategories.value.push(cat.id);
      }
    });
  },
  { immediate: true }
);

const toggleExpand = (id: string) => {
  const index = expandedCategories.value.indexOf(id);
  if (index > -1) expandedCategories.value.splice(index, 1);
  else expandedCategories.value.push(id);
};
</script>

<template>
  <aside
    class="flex flex-col gap-6 bg-white p-4 sm:p-5 sm:rounded-2xl sm:border sm:border-gray-200 sm:shadow-sm sm:sticky sm:top-24 w-full"
    aria-label="Filter Marketplace"
  >
    <header class="flex items-center justify-between border-b border-gray-100 pb-4">
      <h2 class="font-extrabold text-gray-900 text-base lg:text-lg tracking-tight">
        Filter Produk
      </h2>
      <button
        v-if="selected.length > 0 || search !== '' || price[0] > 0 || price[1] < 10000000"
        @click="
          () => {
            emit('update:selected', []);
            emit('update:price', [0, 10000000]);
            emit('update:search', '');
          }
        "
        class="text-xs font-bold text-green-600 active:text-green-800 lg:hover:text-green-700 transition-colors py-2 px-3 -mr-3 rounded-lg active:bg-green-50"
        aria-label="Reset semua filter"
      >
        Reset Semua
      </button>
    </header>

    <button
      v-if="isPopularRoute"
      @click="toggleCategory('popular')"
      class="relative w-full flex items-center justify-between p-4 rounded-xl border-2 transition-all duration-200 overflow-hidden group touch-manipulation active:scale-[0.98]"
      :class="
        selected.includes('popular')
          ? 'border-orange-500 bg-orange-50'
          : 'border-gray-100 bg-white active:bg-gray-50 lg:hover:border-orange-200'
      "
      aria-pressed="selected.includes('popular')"
    >
      <div
        v-if="selected.includes('popular')"
        class="absolute inset-0 bg-gradient-to-r from-orange-100/50 to-transparent pointer-events-none"
      ></div>

      <div class="relative flex items-center gap-3">
        <div
          class="p-2 rounded-lg transition-colors"
          :class="
            selected.includes('popular')
              ? 'bg-orange-500 text-white shadow-md shadow-orange-500/20'
              : 'bg-orange-100 text-orange-500'
          "
        >
          <UIcon
            name="i-heroicons-fire-20-solid"
            class="w-5 h-5"
            :class="selected.includes('popular') ? 'animate-pulse' : ''"
            aria-hidden="true"
          />
        </div>
        <div class="flex flex-col items-start text-left">
          <span
            class="text-sm font-black transition-colors"
            :class="selected.includes('popular') ? 'text-orange-700' : 'text-gray-800'"
            >Produk Populer</span
          >
          <span class="text-[10px] font-bold text-gray-400"
            >Trending & Terlaris Saat Ini</span
          >
        </div>
      </div>

      <div
        class="relative flex items-center justify-center w-5 h-5 rounded-md border-2 transition-all"
        :class="
          selected.includes('popular')
            ? 'border-orange-500 bg-orange-500'
            : 'border-gray-300 bg-transparent'
        "
      >
        <UIcon
          v-if="selected.includes('popular')"
          name="i-heroicons-check-16-solid"
          class="w-4 h-4 text-white"
          aria-hidden="true"
        />
      </div>
    </button>

    <section class="space-y-3">
      <h3 class="text-sm font-bold text-gray-800">Cari Cepat</h3>

      <form @submit.prevent role="search" class="relative flex items-center w-full">
        <label for="search-filter" class="sr-only">Cari produk marketplace</label>
        <UIcon
          name="i-heroicons-magnifying-glass"
          class="absolute left-3.5 w-5 h-5 text-gray-400 pointer-events-none"
          aria-hidden="true"
        />
        <input
          id="search-filter"
          type="search"
          :value="search"
          @input="e => emit('update:search', (e.target as HTMLInputElement).value)"
          placeholder="Ketik nama / brand..."
          class="w-full pl-10 pr-4 py-3 sm:py-2.5 border border-gray-300 rounded-xl text-base sm:text-sm text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all shadow-sm bg-white touch-manipulation"
          autocomplete="off"
        />
      </form>

      <div class="flex flex-wrap gap-2 mt-3">
        <p
          class="text-[10px] font-bold text-gray-400 w-full uppercase tracking-widest mb-0.5"
        >
          Pencarian Teratas:
        </p>
        <button
          v-for="term in displaySuggests"
          :key="term"
          @click="applyPopularSearch(term)"
          class="text-xs sm:text-[10px] font-bold px-3 py-1.5 sm:px-2.5 sm:py-1 rounded-full border transition-colors active:scale-95 touch-manipulation"
          :class="
            search === term
              ? 'bg-green-50 border-green-200 text-green-700'
              : 'bg-white border-gray-200 text-gray-600 active:bg-gray-100 lg:hover:bg-green-50 lg:hover:text-green-600'
          "
        >
          {{ term }}
        </button>
      </div>
    </section>

    <section class="space-y-3">
      <h3 class="text-sm font-bold text-gray-800">Kategori</h3>

      <div v-if="pending" class="space-y-4" aria-busy="true">
        <USkeleton class="h-6 w-full rounded-md bg-gray-100 skeleton-shimmer" />
        <USkeleton class="h-6 w-4/5 rounded-md bg-gray-100 skeleton-shimmer" />
        <USkeleton class="h-6 w-full rounded-md bg-gray-100 skeleton-shimmer" />
      </div>

      <div
        v-else
        class="flex flex-col gap-1 max-h-[350px] overflow-y-auto overscroll-contain custom-scrollbar pr-1 pb-2"
      >
        <div
          v-for="cat in categoryMenu"
          :key="cat.id"
          class="flex flex-col border-b border-gray-50 last:border-0"
        >
          <div class="flex items-center justify-between py-2 sm:py-1.5 group">
            <label
              :for="`cat-${cat.id}`"
              class="flex items-center gap-3 cursor-pointer flex-1 py-1 touch-manipulation"
            >
              <UCheckbox
                :id="`cat-${cat.id}`"
                :model-value="selected.includes(cat.id)"
                color="green"
                @change="toggleCategory(cat.id)"
              />
              <UIcon
                :name="cat.icon"
                class="w-5 h-5 sm:w-4 sm:h-4 text-gray-400 group-active:text-green-600 lg:group-hover:text-green-600 transition-colors"
                aria-hidden="true"
              />
              <span
                class="text-[15px] sm:text-sm transition-colors"
                :class="
                  selected.includes(cat.id)
                    ? 'font-bold text-green-600'
                    : 'text-gray-700 group-active:text-green-600'
                "
              >
                {{ cat.label }}
              </span>
            </label>

            <button
              v-if="cat.subs.length > 0"
              @click.stop="toggleExpand(cat.id)"
              class="p-2 sm:p-1 active:bg-gray-100 lg:hover:bg-gray-100 rounded-lg transition-colors touch-manipulation"
              :aria-expanded="expandedCategories.includes(cat.id)"
              :aria-controls="`sub-${cat.id}`"
              aria-label="Buka sub kategori"
            >
              <UIcon
                name="i-heroicons-chevron-down"
                class="w-5 h-5 sm:w-4 sm:h-4 text-gray-400 transition-transform duration-200"
                :class="expandedCategories.includes(cat.id) ? 'rotate-180' : ''"
              />
            </button>
          </div>

          <div
            v-show="expandedCategories.includes(cat.id) && cat.subs.length > 0"
            :id="`sub-${cat.id}`"
            class="ml-10 flex flex-col gap-1 my-1 border-l-2 border-gray-100 pl-3"
          >
            <label
              v-for="sub in cat.subs"
              :key="sub.id"
              :for="`subcat-${sub.id}`"
              class="flex items-center gap-2.5 py-2 sm:py-1.5 cursor-pointer group touch-manipulation"
            >
              <UCheckbox
                :id="`subcat-${sub.id}`"
                :model-value="selected.includes(sub.id)"
                size="xs"
                color="green"
                @change="toggleCategory(sub.id)"
              />
              <span
                class="text-sm sm:text-[13px] transition-colors"
                :class="
                  selected.includes(sub.id)
                    ? 'font-bold text-green-600'
                    : 'text-gray-500 active:text-gray-800 lg:group-hover:text-green-600'
                "
              >
                {{ sub.label }}
              </span>
            </label>
          </div>
        </div>
      </div>
    </section>

    <hr class="border-gray-100" />

    <section class="space-y-4">
      <h3 class="text-sm font-bold text-gray-800">Rentang Harga</h3>

      <div class="grid grid-cols-2 gap-3 sm:gap-2">
        <div
          class="bg-white border border-gray-300 rounded-xl sm:rounded-lg p-2.5 sm:p-2 focus-within:border-green-500 focus-within:ring-1 focus-within:ring-green-500 transition-all shadow-sm"
        >
          <label
            for="price-min"
            class="text-[9px] font-bold text-gray-400 block mb-0.5 uppercase"
            >Minimum</label
          >
          <div class="flex items-center gap-1 font-bold text-gray-700 text-sm sm:text-xs">
            <span>Rp</span>
            <input
              id="price-min"
              type="number"
              inputmode="numeric"
              pattern="[0-9]*"
              :value="price[0]"
              @change="e => updatePrice(Number((e.target as HTMLInputElement).value), 'min')"
              class="bg-transparent w-full outline-none p-0 border-none focus:ring-0 text-base sm:text-sm"
            />
          </div>
        </div>

        <div
          class="bg-white border border-gray-300 rounded-xl sm:rounded-lg p-2.5 sm:p-2 focus-within:border-green-500 focus-within:ring-1 focus-within:ring-green-500 transition-all shadow-sm"
        >
          <label
            for="price-max"
            class="text-[9px] font-bold text-gray-400 block mb-0.5 uppercase"
            >Maksimum</label
          >
          <div class="flex items-center gap-1 font-bold text-gray-700 text-sm sm:text-xs">
            <span>Rp</span>
            <input
              id="price-max"
              type="number"
              inputmode="numeric"
              pattern="[0-9]*"
              :value="price[1]"
              @change="e => updatePrice(Number((e.target as HTMLInputElement).value), 'max')"
              class="bg-transparent w-full outline-none p-0 border-none focus:ring-0 text-base sm:text-sm"
            />
          </div>
        </div>
      </div>

      <input
        type="range"
        :value="price[1]"
        @input="e => updatePrice(Number((e.target as HTMLInputElement).value), 'max')"
        min="0"
        max="10000000"
        step="100000"
        aria-label="Geser rentang harga maksimum"
        class="w-full h-2.5 sm:h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600 mt-2 touch-none"
      />
    </section>
  </aside>
</template>

<style scoped>
/* 🚀 Menghilangkan highlight abu-abu standar saat area ditekan di HP */
aside,
button,
input,
label {
  -webkit-tap-highlight-color: transparent;
}

/* Mempercepat rendering dengan hardware acceleration untuk animasi */
.skeleton-shimmer {
  will-change: opacity;
}

/* Styling Input Angka agar bersih */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
}

/* Custom Scrollbar responsif */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 10px;
}
/* Hanya munculkan warna hijau di desktop hover (pointer: fine) */
@media (pointer: fine) {
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #16a34a;
  }
}
</style>
