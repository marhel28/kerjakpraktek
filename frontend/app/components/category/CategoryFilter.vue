<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps<{
  search: string
  selected: string[]
  price: number[]
  dynamicSuggests?: string[]
}>()

const emit = defineEmits(['update:search', 'update:selected', 'update:price'])

const route = useRoute()
const isPopularRoute = computed(() => route.path.toLowerCase().includes('/popular'))

// ── Icon map per slug ─────────────────────────────────────────────
const CATEGORY_ICON_MAP: Record<string, string> = {
  'kamera-cctv':        'i-heroicons-video-camera',
  'dvr-nvr':            'i-heroicons-cpu-chip',
  'security-alarm':     'i-heroicons-bell-alert',
  'access-control':     'i-heroicons-lock-closed',
  'networking':         'i-heroicons-wifi',
  'cables-accessories': 'i-heroicons-link',
  'smart-home':         'i-heroicons-home-modern',
  'storage':            'i-heroicons-server',
  'paket-cctv':         'i-heroicons-gift',
}

const getIcon = (cat: any) =>
  CATEGORY_ICON_MAP[cat.id] || cat.icon || 'i-heroicons-folder'

// ── Fetch categories ──────────────────────────────────────────────
const { data: categoryMenu, pending } = await useFetch('/api/category', {
  transform: (res: any) => {
    const arr = Array.isArray(res) ? res : res?.data || []
    return arr.map((cat: any) => ({
      id: cat.slug,
      label: cat.name,
      icon: cat.icon_name || 'i-heroicons-folder',
      subs: (cat.subcategories || []).map((s: any) => ({ id: s.slug, label: s.name })),
    }))
  },
  default: () => [],
})

// ── Suggests ──────────────────────────────────────────────────────
const displaySuggests = computed(() =>
  props.dynamicSuggests?.length
    ? props.dynamicSuggests
    : ['CCTV Outdoor', 'DVR 8 Channel', 'IP Camera', 'Hikvision', 'Kabel CCTV']
)

// ── Route → selection sync ────────────────────────────────────────
let lastPath = ''
watch(() => [route.path, categoryMenu.value], ([newPath, menu]) => {
  if (!menu || !(menu as any[]).length || isPopularRoute.value) return
  if (newPath === lastPath) return
  lastPath = newPath as string
  const segs = (newPath as string).toLowerCase().split('/').filter(Boolean)
  const found = new Set<string>()
  ;(menu as any[]).forEach(cat => {
    if (segs.includes(cat.id)) found.add(cat.id)
    cat.subs.forEach((s: any) => { if (segs.includes(s.id)) { found.add(s.id); found.add(cat.id) } })
  })
  if (found.size) emit('update:selected', [...new Set([...props.selected, ...found])])
}, { immediate: true })

// ── Self-healing parent ───────────────────────────────────────────
watch(() => props.selected, sel => {
  if (!categoryMenu.value?.length) return
  const fix = new Set(sel)
  let changed = false
  ;(categoryMenu.value as any[]).forEach(cat => {
    if (cat.subs.some((s: any) => fix.has(s.id)) && !fix.has(cat.id)) {
      fix.add(cat.id); changed = true
    }
  })
  if (changed) emit('update:selected', [...fix])
}, { deep: true })

// ── Toggle ────────────────────────────────────────────────────────
const toggleCategory = (id: string) => {
  let next = [...props.selected]
  const idx = next.indexOf(id)
  if (idx > -1) {
    next.splice(idx, 1)
    const parent = (categoryMenu.value as any[])?.find(c => c.id === id)
    parent?.subs.forEach((s: any) => { const i = next.indexOf(s.id); if (i > -1) next.splice(i, 1) })
  } else {
    next.push(id)
    ;(categoryMenu.value as any[])?.forEach(cat => {
      if (cat.subs.some((s: any) => s.id === id) && !next.includes(cat.id)) next.push(cat.id)
    })
  }
  emit('update:selected', next)
}

const updatePrice = (val: number, type: 'min' | 'max') => {
  const p = [...props.price]
  if (type === 'min') p[0] = Math.min(val, p[1])
  else p[1] = Math.max(val, p[0])
  emit('update:price', p)
}

// ── Expand accordion ─────────────────────────────────────────────
const expanded = ref<string[]>([])
watch(() => props.selected, sel => {
  ;(categoryMenu.value as any[])?.forEach(cat => {
    if ((sel.includes(cat.id) || cat.subs.some((s: any) => sel.includes(s.id))) && !expanded.value.includes(cat.id))
      expanded.value.push(cat.id)
  })
}, { immediate: true })
const toggleExpand = (id: string) => {
  const i = expanded.value.indexOf(id)
  i > -1 ? expanded.value.splice(i, 1) : expanded.value.push(id)
}

// ── Mobile bottom sheet ───────────────────────────────────────────
const sheetOpen = ref(false)
const openSheet  = () => { sheetOpen.value = true; document.body.style.overflow = 'hidden' }
const closeSheet = () => { sheetOpen.value = false; document.body.style.overflow = '' }

const hasActiveFilter = computed(() =>
  props.selected.length > 0 || props.search !== '' || props.price[0] > 0 || props.price[1] < 10000000
)

const resetAll = () => {
  emit('update:selected', [])
  emit('update:price', [0, 10000000])
  emit('update:search', '')
}
</script>

<template>
  <!-- ═══════════════ MOBILE (< lg) ═══════════════ -->
  <div class="lg:hidden">

    <!-- Horizontal Category Chips -->
    <div class="flex items-center gap-2 overflow-x-auto hide-scrollbar pb-1 px-0.5">
      <!-- Filter FAB -->
        <button
          @click="openSheet"
          class="shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-xl border text-[13px] font-bold transition-all"
          :class="hasActiveFilter
            ? 'bg-[#03AC0E] text-white border-[#03AC0E] shadow-sm shadow-emerald-200'
            : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'"
        >
          <UIcon name="i-heroicons-funnel" class="w-4 h-4" />
          Filter
          <span v-if="selected.length" class="bg-white text-[#03AC0E] text-[10px] font-black w-4 h-4 rounded-full flex items-center justify-center leading-none">
            {{ selected.length }}
          </span>
        </button>

        <!-- Category chips -->
        <template v-if="!pending">
          <button
            v-for="cat in (categoryMenu as any[])"
            :key="cat.id"
            @click="toggleCategory(cat.id)"
            class="shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-xl border text-[13px] font-bold whitespace-nowrap transition-all active:scale-95"
            :class="selected.includes(cat.id)
              ? 'bg-[#03AC0E] text-white border-[#03AC0E]'
              : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'"
          >
            <UIcon :name="getIcon(cat)" class="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
            {{ cat.label }}
          </button>
        </template>
      <!-- Skeleton chips -->
      <template v-else>
        <div v-for="i in 5" :key="i" class="shrink-0 h-9 w-24 bg-gray-100 rounded-xl animate-pulse" />
      </template>
    </div>

    <!-- ══ Bottom Sheet ══ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="sheetOpen" class="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm" @click.self="closeSheet" />
      </Transition>

      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="translate-y-full"
        enter-to-class="translate-y-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="translate-y-0"
        leave-to-class="translate-y-full"
      >
        <div v-if="sheetOpen" class="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl shadow-2xl max-h-[85svh] flex flex-col">

          <!-- Drag handle -->
          <div class="flex justify-center pt-3 pb-1 shrink-0">
            <div class="w-10 h-1 bg-gray-200 rounded-full" />
          </div>

          <!-- Sheet header -->
          <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100 shrink-0">
            <h2 class="text-[15px] font-extrabold text-gray-900">Filter Produk</h2>
            <div class="flex items-center gap-2">
              <button v-if="hasActiveFilter" @click="resetAll"
                class="text-[13px] font-bold text-[#03AC0E] px-3 py-1.5 rounded-lg active:bg-[#E6F7E9]">
                Reset
              </button>
              <button @click="closeSheet"
                class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center active:bg-gray-200">
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4 text-gray-600" />
              </button>
            </div>
          </div>

          <!-- Sheet body -->
          <div class="overflow-y-auto overscroll-contain flex-1 px-5 py-4 space-y-6">

            <!-- Search -->
            <section>
              <h3 class="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-2">Cari Produk</h3>
              <div class="relative">
                <UIcon name="i-heroicons-magnifying-glass" class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" aria-hidden="true" />
                <input
                  type="search"
                  :value="search"
                  @input="e => emit('update:search', (e.target as HTMLInputElement).value)"
                  placeholder="Nama produk / brand..."
                  class="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl text-[14px] font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-[#03AC0E]/30 focus:border-[#03AC0E] bg-slate-50"
                  autocomplete="off"
                />
              </div>
              <!-- Suggests -->
              <div class="flex flex-wrap gap-2 mt-3">
                <button v-for="term in displaySuggests" :key="term"
                  @click="emit('update:search', term)"
                  class="text-[12px] font-bold px-3 py-1.5 rounded-full border transition-colors"
                  :class="search === term ? 'bg-[#E6F7E9] border-[#C8E6CC] text-[#03AC0E]' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'">
                  {{ term }}
                </button>
              </div>
            </section>

            <!-- Categories -->
            <section>
              <h3 class="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-3">Kategori</h3>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="cat in (categoryMenu as any[])" :key="cat.id"
                  @click="toggleCategory(cat.id)"
                  class="flex items-center gap-2.5 p-3 rounded-xl border text-left transition-all active:scale-[0.97]"
                  :class="selected.includes(cat.id)
                    ? 'border-[#03AC0E] bg-[#E6F7E9] shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'"
                >
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-colors"
                    :class="selected.includes(cat.id) ? 'bg-[#03AC0E] text-white' : 'bg-slate-100 text-slate-500'">
                    <UIcon :name="getIcon(cat)" class="w-4 h-4" aria-hidden="true" />
                  </div>
                  <span class="text-[13px] font-bold leading-tight"
                    :class="selected.includes(cat.id) ? 'text-[#03AC0E]' : 'text-slate-800'">
                    {{ cat.label }}
                  </span>
                  <UIcon v-if="selected.includes(cat.id)" name="i-heroicons-check-circle-20-solid"
                    class="w-4 h-4 text-[#03AC0E] ml-auto shrink-0" />
                </button>
              </div>
            </section>

            <!-- Price -->
            <section>
              <h3 class="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-3">Rentang Harga</h3>
              <div class="grid grid-cols-2 gap-3 mb-4">
                <div class="bg-slate-50 border border-slate-200 rounded-xl p-3 focus-within:border-[#03AC0E] focus-within:ring-1 focus-within:ring-[#03AC0E] transition-all">
                  <label for="m-price-min" class="text-[9px] font-black text-slate-400 uppercase tracking-widest block mb-1">Min</label>
                  <div class="flex items-center gap-1 font-bold text-slate-800">
                    <span class="text-[13px]">Rp</span>
                    <input id="m-price-min" type="number" inputmode="numeric"
                      :value="price[0]"
                      @change="e => updatePrice(Number((e.target as HTMLInputElement).value), 'min')"
                      class="bg-transparent w-full outline-none border-none focus:ring-0 text-[14px]" />
                  </div>
                </div>
                <div class="bg-slate-50 border border-slate-200 rounded-xl p-3 focus-within:border-[#03AC0E] focus-within:ring-1 focus-within:ring-[#03AC0E] transition-all">
                  <label for="m-price-max" class="text-[9px] font-black text-slate-400 uppercase tracking-widest block mb-1">Max</label>
                  <div class="flex items-center gap-1 font-bold text-slate-800">
                    <span class="text-[13px]">Rp</span>
                    <input id="m-price-max" type="number" inputmode="numeric"
                      :value="price[1]"
                      @change="e => updatePrice(Number((e.target as HTMLInputElement).value), 'max')"
                      class="bg-transparent w-full outline-none border-none focus:ring-0 text-[14px]" />
                  </div>
                </div>
              </div>
              <input type="range" :value="price[1]"
                @input="e => updatePrice(Number((e.target as HTMLInputElement).value), 'max')"
                min="0" max="10000000" step="100000"
                class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#03AC0E]" />
              <div class="flex justify-between text-[11px] font-bold text-slate-400 mt-1">
                <span>Rp 0</span><span>Rp 10 Jt</span>
              </div>
            </section>

            <div class="h-4" />
          </div>

          <!-- Sheet footer CTA -->
          <div class="px-5 py-4 border-t border-slate-100 shrink-0 bg-white">
            <button @click="closeSheet"
              class="w-full bg-[#03AC0E] hover:bg-[#02930c] text-white font-black py-3.5 rounded-xl text-[14px] transition-colors active:scale-[0.98]">
              Tampilkan Produk
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>

  <!-- ═══════════════ DESKTOP (≥ lg) ═══════════════ -->
  <aside
    class="hidden lg:flex flex-col gap-0 bg-white w-full px-4 py-4 rounded-xl border border-slate-200 shadow-2xs"
    aria-label="Filter Marketplace"
  >
    <header class="flex items-center justify-between border-b border-slate-200 pb-3 mb-1">
      <h2 class="font-bold text-slate-900 text-sm tracking-normal">Filter Produk</h2>
      <button v-if="hasActiveFilter" @click="resetAll"
        class="text-xs text-[#03AC0E] hover:text-[#02930c] hover:underline font-semibold transition-colors">
        Reset Semua
      </button>
    </header>

    <!-- Popular -->
    <button v-if="isPopularRoute" @click="toggleCategory('popular')"
      class="w-full flex items-center justify-between p-4 rounded-xl border-2 transition-all overflow-hidden group my-3"
      :class="selected.includes('popular') ? 'border-orange-500 bg-orange-50' : 'border-gray-100 bg-white hover:border-orange-200'">
      <div class="flex items-center gap-3">
        <div class="p-2 rounded-lg transition-colors"
          :class="selected.includes('popular') ? 'bg-orange-500 text-white' : 'bg-orange-100 text-orange-500'">
          <UIcon name="i-heroicons-fire-20-solid" class="w-5 h-5" />
        </div>
        <div class="text-left">
          <p class="text-sm font-black" :class="selected.includes('popular') ? 'text-orange-700' : 'text-gray-800'">Produk Populer</p>
          <p class="text-[10px] font-bold text-gray-400">Trending & Terlaris</p>
        </div>
      </div>
      <div class="w-5 h-5 rounded-md border-2 transition-all flex items-center justify-center"
        :class="selected.includes('popular') ? 'border-orange-500 bg-orange-500' : 'border-gray-300'">
        <UIcon v-if="selected.includes('popular')" name="i-heroicons-check-16-solid" class="w-4 h-4 text-white" />
      </div>
    </button>

    <!-- Search -->
    <section class="py-3.5 space-y-3">
      <h3 class="text-sm font-bold text-slate-900 pb-2 border-b border-slate-200 mb-3">Cari Cepat</h3>
      <div class="relative">
        <UIcon name="i-heroicons-magnifying-glass" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input type="search" :value="search"
          @input="e => emit('update:search', (e.target as HTMLInputElement).value)"
          placeholder="Ketik nama / brand..."
          class="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-[#03AC0E] focus:ring-2 focus:ring-[#03AC0E]/20 bg-white"
          autocomplete="off" />
      </div>
      <div class="flex flex-wrap gap-1.5">
        <button v-for="term in displaySuggests" :key="term"
          @click="emit('update:search', term)"
          class="text-xs px-2.5 py-1 rounded-full border transition-colors"
          :class="search === term ? 'bg-[#E6F7E9] border-[#C8E6CC] text-[#03AC0E] font-semibold' : 'border-slate-200 text-slate-600 hover:bg-slate-50'">
          {{ term }}
        </button>
      </div>
    </section>

    <!-- Categories -->
    <section class="py-3.5 space-y-2">
      <h3 class="text-sm font-bold text-slate-900 pb-2 border-b border-slate-200 mb-3">Kategori</h3>

      <div v-if="pending" class="space-y-3">
        <div v-for="i in 5" :key="i" class="h-8 bg-slate-100 rounded-lg animate-pulse" />
      </div>

      <div v-else class="flex flex-col gap-0.5 max-h-[360px] overflow-y-auto overscroll-contain custom-scrollbar pr-1">
        <div v-for="cat in (categoryMenu as any[])" :key="cat.id" class="flex flex-col">
          <div class="flex items-center justify-between py-1 group">
            <label :for="`cat-${cat.id}`" class="flex items-center gap-2 cursor-pointer flex-1 py-0.5 hover:text-[#03AC0E]">
              <UCheckbox :id="`cat-${cat.id}`" :model-value="selected.includes(cat.id)" color="green" @change="toggleCategory(cat.id)" />
              <UIcon :name="getIcon(cat)" class="w-4 h-4 text-slate-500 shrink-0" aria-hidden="true" />
              <span class="text-sm transition-colors"
                :class="selected.includes(cat.id) ? 'font-semibold text-slate-900' : 'text-slate-700 hover:text-[#03AC0E]'">
                {{ cat.label }}
              </span>
            </label>
            <button v-if="cat.subs.length" @click.stop="toggleExpand(cat.id)"
              class="p-1 hover:bg-slate-100 rounded transition-colors"
              :aria-expanded="expanded.includes(cat.id)">
              <UIcon name="i-heroicons-chevron-down" class="w-4 h-4 text-slate-400 transition-transform duration-200"
                :class="expanded.includes(cat.id) ? 'rotate-180' : ''" />
            </button>
          </div>

          <div v-show="expanded.includes(cat.id) && cat.subs.length" class="ml-6 flex flex-col">
            <label v-for="sub in cat.subs" :key="sub.id" :for="`subcat-${sub.id}`"
              class="flex items-center gap-2 py-0.5 cursor-pointer group hover:text-[#03AC0E]">
              <UCheckbox :id="`subcat-${sub.id}`" :model-value="selected.includes(sub.id)" size="xs" color="green" @change="toggleCategory(sub.id)" />
              <span class="text-xs transition-colors"
                :class="selected.includes(sub.id) ? 'font-semibold text-slate-900' : 'text-slate-700 hover:text-[#03AC0E]'">
                {{ sub.label }}
              </span>
            </label>
          </div>
        </div>
      </div>
    </section>

    <hr class="border-slate-200" />

    <!-- Price -->
    <section class="py-3.5 space-y-3">
      <h3 class="text-sm font-bold text-slate-900 pb-2 border-b border-slate-200 mb-3">Rentang Harga</h3>
      <div class="grid grid-cols-2 gap-2">
        <div class="bg-white border border-slate-300 rounded-lg p-2 focus-within:border-[#03AC0E] focus-within:ring-2 focus-within:ring-[#03AC0E]/20 transition-all min-w-0">
          <label for="d-price-min" class="text-[9px] font-bold text-slate-400 uppercase block mb-0.5">Minimum</label>
          <div class="flex items-center gap-1 font-bold text-slate-700 text-xs sm:text-sm min-w-0">
            <span class="text-slate-400 shrink-0 text-xs">Rp</span>
            <input id="d-price-min" type="number" inputmode="numeric" :value="price[0]"
              @change="e => updatePrice(Number((e.target as HTMLInputElement).value), 'min')"
              class="bg-transparent w-full min-w-0 outline-none p-0 border-none focus:ring-0 text-xs font-semibold text-slate-800" />
          </div>
        </div>
        <div class="bg-white border border-slate-300 rounded-lg p-2 focus-within:border-[#03AC0E] focus-within:ring-2 focus-within:ring-[#03AC0E]/20 transition-all min-w-0">
          <label for="d-price-max" class="text-[9px] font-bold text-slate-400 uppercase block mb-0.5">Maksimum</label>
          <div class="flex items-center gap-1 font-bold text-slate-700 text-xs sm:text-sm min-w-0">
            <span class="text-slate-400 shrink-0 text-xs">Rp</span>
            <input id="d-price-max" type="number" inputmode="numeric" :value="price[1]"
              @change="e => updatePrice(Number((e.target as HTMLInputElement).value), 'max')"
              class="bg-transparent w-full min-w-0 outline-none p-0 border-none focus:ring-0 text-xs font-semibold text-slate-800" />
          </div>
        </div>
      </div>
      <div>
        <input type="range" :value="price[1]"
          @input="e => updatePrice(Number((e.target as HTMLInputElement).value), 'max')"
          min="0" max="10000000" step="100000"
          class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#03AC0E]" />
        <div class="flex justify-between text-[10px] font-bold text-slate-400 mt-1.5">
          <span>Rp 0</span>
          <span>Rp 10 Jt+</span>
        </div>
      </div>
    </section>
  </aside>
</template>

<style scoped>
* {
  -webkit-tap-highlight-color: transparent;
}

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
input[type="number"] { -moz-appearance: textfield; }

.hide-scrollbar::-webkit-scrollbar { display: none; }
.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.custom-scrollbar::-webkit-scrollbar { width: 3px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 10px; }
@media (pointer: fine) {
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #16a34a; }
}
</style>
