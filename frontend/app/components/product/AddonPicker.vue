<script setup lang="ts">
import { ref } from "vue";

interface AddonItem {
  uuid: string;
  name: string;
  price: number;
  stock: number;
  description?: string;
  image_url?: string;
  allow_quantity: boolean;
  max_quantity: number;
  weight: number;
}

interface AddonGroup {
  uuid: string;
  name: string;
  selection_type: "single" | "multi";
  is_required: boolean;
  group_type: "required" | "optional" | "recommended";
  is_global: boolean;
  items: AddonItem[];
}

const props = withDefaults(defineProps<{
  bundle: AddonGroup[];
  modelValue: Record<string, { uuid: string; quantity: number; price: number; name: string; weight: number }>;
  variant?: "cards" | "chips";
}>(), {
  variant: "cards"
});

// Computed for grouped bundles
const groupedBundles = computed(() => {
  const groups = {
    required: [] as AddonGroup[],
    recommended: [] as AddonGroup[],
    optional: [] as AddonGroup[]
  };
  
  props.bundle.forEach(g => {
    const type = g.group_type || (g.is_required ? 'required' : 'optional');
    if (groups[type]) groups[type].push(g);
    else groups.optional.push(g);
  });
  
  return groups;
});

const emit = defineEmits(["update:modelValue"]);

// Detail Popup State
const isDetailOpen = ref(false);
const activeDetail = ref<AddonItem | null>(null);

const showDetail = (item: AddonItem) => {
  activeDetail.value = item;
  isDetailOpen.value = true;
};

const toggleItem = (group: AddonGroup, item: AddonItem) => {
  const current = { ...props.modelValue };
  
  if (group.selection_type === "single") {
    if (current[item.uuid]) {
      if (!group.is_required) delete current[item.uuid];
    } else {
      group.items.forEach((i) => delete current[i.uuid]);
      current[item.uuid] = { uuid: item.uuid, quantity: 1, price: item.price, name: item.name, weight: item.weight };
    }
  } else {
    if (current[item.uuid]) {
      delete current[item.uuid];
    } else {
      current[item.uuid] = { uuid: item.uuid, quantity: 1, price: item.price, name: item.name, weight: item.weight };
    }
  }
  
  emit("update:modelValue", current);
};

const updateQty = (uuid: string, delta: number, max: number) => {
  const current = { ...props.modelValue };
  if (!current[uuid]) return;
  
  const newQty = current[uuid].quantity + delta;
  if (newQty >= 1 && newQty <= max) {
    current[uuid].quantity = newQty;
    emit("update:modelValue", current);
  }
};

const formatRupiah = (angka: number) =>
  new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 }).format(angka || 0);
</script>

<template>
  <div class="space-y-8 py-2">
    <!-- Grouped Sections -->
    <div v-for="(groups, type) in groupedBundles" :key="type">
      <div v-if="groups.length > 0" class="space-y-6">


        <div v-for="group in groups" :key="group.uuid" class="space-y-3">
          <!-- Group Header -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <label class="text-[12px] font-black text-gray-600 tracking-wide">
                {{ group.name }}
              </label>
              <span v-if="group.is_global" class="text-[8px] font-black text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded-full uppercase leading-none border border-indigo-100">
                Global
              </span>
            </div>
            <span v-if="group.selection_type === 'single'" class="text-[9px] text-gray-400 font-bold uppercase tracking-widest">
              Pilih Satu
            </span>
          </div>

          <!-- Addon List -->
          <div class="overflow-x-auto no-scrollbar -mx-4 px-4 sm:mx-0 sm:px-0">
            <div 
              class="flex flex-nowrap sm:flex-wrap gap-2.5 min-w-max sm:min-w-0 pb-2 sm:pb-0"
              :class="{ 'sm:gap-3': variant === 'chips' }"
            >
              <!-- Variant: CARDS -->
              <template v-if="variant === 'cards'">
                <div v-for="item in group.items" :key="item.uuid" 
                  @click="toggleItem(group, item)"
                  :class="[
                    modelValue[item.uuid] 
                      ? 'border-emerald-500 text-emerald-700 bg-emerald-50/50 ring-1 ring-emerald-500/20' 
                      : 'border-gray-200 text-gray-700 hover:border-emerald-500 hover:text-emerald-600 bg-white shadow-sm'
                  ]"
                  class="relative w-[160px] sm:w-[180px] shrink-0 sm:shrink px-3 py-2.5 border-2 transition-all cursor-pointer rounded-2xl text-[12px] font-bold flex flex-col gap-1 group"
                >
                  <!-- Info Icon -->
                  <button 
                    @click.stop="showDetail(item)" 
                    class="absolute top-2 right-2 w-7 h-7 flex items-center justify-center text-gray-400 bg-white shadow-sm border border-gray-100 rounded-full hover:text-emerald-500 hover:border-emerald-200 transition-all z-10"
                  >
                    <UIcon name="i-heroicons-information-circle" class="w-5 h-5" />
                  </button>

                  <!-- Checkmark -->
                  <div v-if="modelValue[item.uuid]" class="absolute bottom-0 right-0 w-6 h-6 bg-emerald-500 flex items-center justify-center rounded-tl-2xl rounded-br-2xl overflow-hidden translate-x-[1.5px] translate-y-[1.5px] shadow-sm">
                    <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>

                  <div class="flex items-center gap-3">
                    <div class="w-12 h-12 shrink-0 bg-gray-50 rounded-2xl overflow-hidden border border-gray-100 shadow-sm p-1">
                      <img v-if="item.image_url" :src="item.image_url" class="w-full h-full object-cover rounded-xl" />
                      <div v-else class="w-full h-full flex items-center justify-center text-gray-200">
                        <UIcon name="i-heroicons-photo" class="w-6 h-6" />
                      </div>
                    </div>
                    <div class="min-w-0 flex-1">
                      <span class="truncate block text-[13px] leading-tight font-black text-gray-800">{{ item.name }}</span>
                      <div class="flex items-center gap-1.5 mt-0.5">
                        <span v-if="item.price > 0" class="text-[12px] font-black text-emerald-600">
                          +{{ formatRupiah(item.price) }}
                        </span>
                        <span v-else class="text-[11px] font-black text-indigo-500">GRATIS</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex items-center justify-between text-[10px] mt-2 opacity-60 border-t border-gray-100 pt-1.5 font-bold">
                    <span :class="item.stock < 10 ? 'text-rose-500' : 'text-gray-500'">Sisa: {{ item.stock }}</span>
                    <span v-if="item.allow_quantity" class="text-gray-500">Maks: {{ item.max_quantity }}</span>
                  </div>

                  <!-- Qty Adjuster -->
                  <div v-if="modelValue[item.uuid] && item.allow_quantity" @click.stop class="mt-2.5 flex items-center justify-between bg-white rounded-xl border border-emerald-200 p-0.5 shadow-sm">
                    <button @click="updateQty(item.uuid, -1, item.max_quantity)" class="w-8 h-8 flex items-center justify-center text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors">
                      <UIcon name="i-heroicons-minus" class="w-4 h-4" />
                    </button>
                    <span class="text-[13px] font-black w-8 text-center text-emerald-700">{{ modelValue[item.uuid].quantity }}</span>
                    <button @click="updateQty(item.uuid, 1, item.max_quantity)" class="w-8 h-8 flex items-center justify-center text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors">
                      <UIcon name="i-heroicons-plus" class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </template>

              <!-- Variant: CHIPS (HDD Style) -->
              <template v-else>
                <div v-for="item in group.items" :key="item.uuid"
                  @click="toggleItem(group, item)"
                  :class="[
                    modelValue[item.uuid]
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-700 ring-1 ring-emerald-500/20'
                      : 'border-gray-200 text-gray-600 hover:border-emerald-500 bg-white'
                  ]"
                  class="relative px-5 py-4 border-2 rounded-2xl transition-all cursor-pointer flex flex-col items-center justify-center min-w-[120px] text-center group"
                >
                  <span class="text-[13px] font-black block leading-none">{{ item.name }}</span>
                  <div class="flex items-center gap-2 mt-1.5">
                    <span v-if="item.price > 0" class="text-[10px] font-bold opacity-70">
                      + {{ formatRupiah(item.price) }}
                    </span>
                    <span v-else class="text-[10px] font-bold text-indigo-500">GRATIS</span>
                  </div>

                  <!-- Qty Adjuster for Chips -->
                  <div v-if="modelValue[item.uuid] && item.allow_quantity" @click.stop class="mt-3 flex items-center justify-between bg-white rounded-lg border border-emerald-200 p-0.5 shadow-sm min-w-[90px]">
                    <button @click="updateQty(item.uuid, -1, item.max_quantity)" class="w-7 h-7 flex items-center justify-center text-emerald-600 hover:bg-emerald-50 rounded-md transition-colors">
                      <UIcon name="i-heroicons-minus" class="w-3.5 h-3.5" />
                    </button>
                    <span class="text-[12px] font-black w-6 text-center text-emerald-700">{{ modelValue[item.uuid].quantity }}</span>
                    <button @click="updateQty(item.uuid, 1, item.max_quantity)" class="w-7 h-7 flex items-center justify-center text-emerald-600 hover:bg-emerald-50 rounded-md transition-colors">
                      <UIcon name="i-heroicons-plus" class="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <!-- Small Checkmark indicator -->
                  <div v-if="modelValue[item.uuid]" class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center shadow-md border-2 border-white">
                    <UIcon name="i-heroicons-check" class="w-3 h-3 text-white" />
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Detail Popup (Modal) ────────────────────────────────── -->
    <UModal v-model="isDetailOpen" :ui="{ width: 'sm:max-w-md', rounded: 'rounded-[40px]', padding: 'p-0' }">
      <div class="relative overflow-hidden">
        <!-- Close Button -->
        <button @click="isDetailOpen = false" class="absolute top-6 right-6 z-20 w-10 h-10 flex items-center justify-center bg-white/80 backdrop-blur-md rounded-full shadow-lg border border-gray-100 hover:bg-gray-50 transition-all">
          <UIcon name="i-heroicons-x-mark" class="w-6 h-6 text-gray-900" />
        </button>

        <div v-if="activeDetail" class="p-8">
          <div class="aspect-square rounded-[32px] overflow-hidden bg-white border border-gray-100 shadow-xl mb-8 group">
            <img v-if="activeDetail.image_url" :src="activeDetail.image_url" class="w-full h-full object-contain p-8 group-hover:scale-110 transition-transform duration-500" />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-100">
              <UIcon name="i-heroicons-photo" class="w-32 h-32" />
            </div>
          </div>

          <div class="space-y-6">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="px-2 py-0.5 bg-indigo-50 text-indigo-600 text-[10px] font-black rounded-md uppercase tracking-widest border border-indigo-100">Info Layanan</span>
              </div>
              <h4 class="text-2xl font-black text-gray-900 leading-tight mb-2">{{ activeDetail.name }}</h4>
              <p v-if="activeDetail.price > 0" class="text-emerald-600 font-black text-2xl">+ {{ formatRupiah(activeDetail.price) }}</p>
              <p v-else class="text-indigo-600 font-black text-2xl uppercase tracking-wider">GRATIS</p>
            </div>

            <div class="text-sm text-gray-600 leading-relaxed bg-gray-50/50 p-5 rounded-[24px] border border-gray-100 italic">
              {{ activeDetail.description || 'Layanan tambahan terbaik untuk melengkapi kebutuhan sistem Anda.' }}
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="bg-white border border-gray-100 p-4 rounded-[24px] text-center shadow-sm">
                <p class="text-[10px] text-gray-400 font-black uppercase tracking-widest mb-1">Stok Ready</p>
                <p class="text-gray-900 font-black text-lg">{{ activeDetail.stock }}</p>
              </div>
              <div class="bg-white border border-gray-100 p-4 rounded-[24px] text-center shadow-sm">
                <p class="text-[10px] text-gray-400 font-black uppercase tracking-widest mb-1">Batas Item</p>
                <p class="text-gray-900 font-black text-lg">{{ activeDetail.max_quantity }}</p>
              </div>
            </div>

            <button 
              class="w-full py-5 bg-black text-white font-black rounded-[24px] text-sm uppercase tracking-[0.2em] shadow-xl hover:bg-gray-800 transition-all active:scale-[0.98] mt-4"
              @click="isDetailOpen = false"
            >
              Lanjutkan
            </button>
          </div>
        </div>
      </div>
    </UModal>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
