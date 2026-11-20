<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export interface FilterState {
  categories: string[]
  subcategories: string[]
  brands: string[]
  priceRange: [number, number]
  discount: number[]
  inStockOnly: boolean
  sortBy: string
}

const props = defineProps<{
  modelValue: FilterState
  categoryMenu: any[]
  totalProducts?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: FilterState): void
  (e: 'apply'): void
}>()

const router = useRouter()
const route = useRoute()

const state = ref<FilterState>({
  categories: [...(props.modelValue.categories || [])],
  subcategories: [...(props.modelValue.subcategories || [])],
  brands: [...(props.modelValue.brands || [])],
  priceRange: props.modelValue.priceRange ? [...props.modelValue.priceRange] as [number, number] : [0, 10000000],
  discount: [...(props.modelValue.discount || [])],
  inStockOnly: props.modelValue.inStockOnly || false,
  sortBy: props.modelValue.sortBy || 'newest',
})

const expandedSections = ref<string[]>(['department', 'brand', 'price', 'discount'])

const toggleExpand = (section: string) => {
  const idx = expandedSections.value.indexOf(section)
  if (idx > -1) {
    expandedSections.value.splice(idx, 1)
  } else {
    expandedSections.value.push(section)
  }
}

const emitUpdate = () => {
  emit('update:modelValue', { ...state.value })
}

const applyFilters = () => {
  emitUpdate()
  emit('apply')
}

// Parse query params from URL
const syncFromRoute = () => {
  const q = route.query
  if (q.cat) {
    const raw = Array.isArray(q.cat) ? q.cat : [q.cat]
    state.value.categories = raw.filter((x): x is string => typeof x === 'string')
  }
  if (q.brand) {
    const raw = Array.isArray(q.brand) ? q.brand : [q.brand]
    state.value.brands = raw.filter((x): x is string => typeof x === 'string')
  }
  if (q.min_price) {
    state.value.priceRange[0] = Number(q.min_price) || 0
  }
  if (q.max_price) {
    state.value.priceRange[1] = Number(q.max_price) || 10000000
  }
  if (q.min_discount) {
    const raw = Array.isArray(q.min_discount) ? q.min_discount : [q.min_discount]
    state.value.discount = raw.map(Number).filter(n => !isNaN(n))
  }
  if (q.in_stock) {
    state.value.inStockOnly = q.in_stock === 'true'
  }
  if (q.sort && typeof q.sort === 'string') {
    state.value.sortBy = q.sort
  }
}

onMounted(() => {
  syncFromRoute()
})

watch(() => route.query, () => {
  syncFromRoute()
})

const uniqueBrands = computed(() => {
  const brandsSet = new Set<string>()
  props.categoryMenu.forEach(cat => {
    if (cat.label) brandsSet.add(cat.label)
    ;(cat.subs || []).forEach((sub: any) => {
      if (sub.label) brandsSet.add(sub.label)
    })
  })
  return Array.from(brandsSet).slice(0, 10).sort()
})

const onCategoryChange = (catId: string, checked: boolean) => {
  const list = [...state.value.categories]
  if (checked) {
    if (!list.includes(catId)) list.push(catId)
  } else {
    const idx = list.indexOf(catId)
    if (idx > -1) list.splice(idx, 1)
  }
  state.value.categories = list
  emitUpdate()
  router.push({
    query: {
      ...route.query,
      cat: list.length ? list : undefined,
      page: '1',
    },
  })
}

const onSubcategoryChange = (subId: string, checked: boolean) => {
  const list = [...state.value.subcategories]
  if (checked) {
    if (!list.includes(subId)) list.push(subId)
  } else {
    const idx = list.indexOf(subId)
    if (idx > -1) list.splice(idx, 1)
  }
  state.value.subcategories = list
  emitUpdate()
}

const onBrandChange = (brand: string, checked: boolean) => {
  const list = [...state.value.brands]
  if (checked) {
    if (!list.includes(brand)) list.push(brand)
  } else {
    const idx = list.indexOf(brand)
    if (idx > -1) list.splice(idx, 1)
  }
  state.value.brands = list
  emitUpdate()
  router.push({
    query: {
      ...route.query,
      brand: list.length ? list : undefined,
      page: '1',
    },
  })
}

const onDiscountChange = (val: number, checked: boolean) => {
  const list = [...state.value.discount]
  if (checked) {
    if (!list.includes(val)) list.push(val)
  } else {
    const idx = list.indexOf(val)
    if (idx > -1) list.splice(idx, 1)
  }
  state.value.discount = list
  emitUpdate()
}

const onMinPriceInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  const val = Number(target.value) || 0
  state.value.priceRange[0] = Math.min(val, state.value.priceRange[1])
  emitUpdate()
}

const onMaxPriceInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  const val = Number(target.value) || 0
  state.value.priceRange[1] = Math.max(val, state.value.priceRange[0])
  emitUpdate()
}
</script>

<template>
  <aside class="hidden lg:block w-64 shrink-0 select-none text-xs" aria-label="Filter produk">
    <div class="space-y-4">
      
      <!-- Department / Category Tree -->
      <section class="bg-white rounded-lg border border-neutral-200 shadow-sm overflow-hidden">
        <button
          type="button"
          class="w-full flex items-center justify-between px-3.5 py-2.5 text-left font-bold text-neutral-900 hover:bg-neutral-50 transition-colors"
          @click="toggleExpand('department')"
        >
          <span class="text-xs uppercase tracking-wider text-neutral-700">Departemen</span>
          <UIcon :name="expandedSections.includes('department') ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-4 h-4 text-neutral-500" />
        </button>
        <div v-if="expandedSections.includes('department')" class="border-t border-neutral-100 px-3 py-2 space-y-1 max-h-56 overflow-y-auto">
          <div v-for="cat in categoryMenu" :key="cat.id" class="space-y-1">
            <label class="flex items-center gap-2 cursor-pointer hover:text-neutral-900 transition-colors">
              <input
                type="checkbox"
                :checked="state.categories.includes(cat.id)"
                class="w-3.5 h-3.5 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-800"
                @change="(e) => onCategoryChange(cat.id, (e.target as HTMLInputElement).checked)"
              />
              <span class="font-semibold text-neutral-800">{{ cat.label }}</span>
            </label>

            <!-- Subcategories -->
            <div v-if="cat.subs && cat.subs.length" class="ml-4 pl-2 border-l border-neutral-200 space-y-1">
              <label
                v-for="sub in cat.subs"
                :key="sub.id"
                class="flex items-center gap-2 cursor-pointer hover:text-neutral-900 text-neutral-600"
              >
                <input
                  type="checkbox"
                  :checked="state.subcategories.includes(sub.id)"
                  class="w-3 h-3 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-800"
                  @change="(e) => onSubcategoryChange(sub.id, (e.target as HTMLInputElement).checked)"
                />
                <span>{{ sub.label }}</span>
              </label>
            </div>
          </div>
        </div>
      </section>

      <!-- Deals & Discounts -->
      <section class="bg-white rounded-lg border border-neutral-200 shadow-sm overflow-hidden">
        <button
          type="button"
          class="w-full flex items-center justify-between px-3.5 py-2.5 text-left font-bold text-neutral-900 hover:bg-neutral-50 transition-colors"
          @click="toggleExpand('discount')"
        >
          <span class="text-xs uppercase tracking-wider text-neutral-700">Deals & Diskon</span>
          <UIcon :name="expandedSections.includes('discount') ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-4 h-4 text-neutral-500" />
        </button>
        <div v-if="expandedSections.includes('discount')" class="border-t border-neutral-100 px-3 py-2 space-y-1.5">
          <label
            v-for="pct in [50, 25, 10]"
            :key="pct"
            class="flex items-center gap-2 cursor-pointer hover:text-neutral-900"
          >
            <input
              type="checkbox"
              :checked="state.discount.includes(pct)"
              class="w-3.5 h-3.5 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-800"
              @change="(e) => onDiscountChange(pct, (e.target as HTMLInputElement).checked)"
            />
            <span class="font-medium text-neutral-800">Diskon {{ pct }}% atau lebih</span>
          </label>
        </div>
      </section>

      <!-- Price Range -->
      <section class="bg-white rounded-lg border border-neutral-200 shadow-sm overflow-hidden">
        <button
          type="button"
          class="w-full flex items-center justify-between px-3.5 py-2.5 text-left font-bold text-neutral-900 hover:bg-neutral-50 transition-colors"
          @click="toggleExpand('price')"
        >
          <span class="text-xs uppercase tracking-wider text-neutral-700">Rentang Harga</span>
          <UIcon :name="expandedSections.includes('price') ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-4 h-4 text-neutral-500" />
        </button>
        <div v-if="expandedSections.includes('price')" class="border-t border-neutral-100 px-3 py-2.5 space-y-2">
          <div class="flex items-center gap-2">
            <div class="flex-1">
              <label class="block text-[10px] text-neutral-500 uppercase">Min (Rp)</label>
              <input
                type="number"
                :value="state.priceRange[0]"
                class="w-full px-2 py-1 border border-neutral-300 rounded text-xs focus:ring-1 focus:ring-neutral-800 outline-none"
                @change="onMinPriceInput"
              />
            </div>
            <span class="text-neutral-400 mt-3">-</span>
            <div class="flex-1">
              <label class="block text-[10px] text-neutral-500 uppercase">Max (Rp)</label>
              <input
                type="number"
                :value="state.priceRange[1]"
                class="w-full px-2 py-1 border border-neutral-300 rounded text-xs focus:ring-1 focus:ring-neutral-800 outline-none"
                @change="onMaxPriceInput"
              />
            </div>
          </div>
          <button
            type="button"
            class="w-full mt-2 py-1.5 px-2 border border-[#C8E6CC] bg-[#E6F7E9] hover:bg-[#d5f3da] rounded text-[11px] font-bold text-[#03AC0E] transition-colors"
            @click="applyFilters"
          >
            Terapkan Harga
          </button>
        </div>
      </section>

      <!-- Brands -->
      <section v-if="uniqueBrands.length" class="bg-white rounded-lg border border-neutral-200 shadow-sm overflow-hidden">
        <button
          type="button"
          class="w-full flex items-center justify-between px-3.5 py-2.5 text-left font-bold text-neutral-900 hover:bg-neutral-50 transition-colors"
          @click="toggleExpand('brand')"
        >
          <span class="text-xs uppercase tracking-wider text-neutral-700">Merek</span>
          <UIcon :name="expandedSections.includes('brand') ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-4 h-4 text-neutral-500" />
        </button>
        <div v-if="expandedSections.includes('brand')" class="border-t border-neutral-100 px-3 py-2 space-y-1.5 max-h-48 overflow-y-auto">
          <label
            v-for="b in uniqueBrands"
            :key="b"
            class="flex items-center gap-2 cursor-pointer hover:text-neutral-900"
          >
            <input
              type="checkbox"
              :checked="state.brands.includes(b)"
              class="w-3.5 h-3.5 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-800"
              @change="(e) => onBrandChange(b, (e.target as HTMLInputElement).checked)"
            />
            <span class="text-neutral-800">{{ b }}</span>
          </label>
        </div>
      </section>

      <!-- Stock Availability -->
      <section class="bg-white rounded-lg border border-neutral-200 shadow-sm p-3">
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            :checked="state.inStockOnly"
            class="w-3.5 h-3.5 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-800"
            @change="(e) => { state.inStockOnly = (e.target as HTMLInputElement).checked; emitUpdate() }"
          />
          <span class="font-medium text-neutral-800">Hanya Produk Ready Stock</span>
        </label>
      </section>

    </div>
  </aside>
</template>