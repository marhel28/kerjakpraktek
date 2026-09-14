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
  variant: "chips"
});

const emit = defineEmits(["update:modelValue"]);

// Detail Popup State
const isDetailOpen = ref(false);
const activeDetail = ref<AddonItem | null>(null);

const showDetail = (item: AddonItem) => {
  activeDetail.value = item;
  isDetailOpen.value = true;
};

// Group ordering: required → recommended → optional
const orderedGroups = computed(() => {
  const order = ["required", "recommended", "optional"];
  return [...props.bundle].sort((a, b) => {
    const aIdx = order.indexOf(a.group_type || "optional");
    const bIdx = order.indexOf(b.group_type || "optional");
    return aIdx - bIdx;
  });
});

const groupTypeLabel: Record<string, { label: string; color: string; dot: string }> = {
  required:    { label: "Wajib",       color: "text-red-600 bg-red-50 border-red-200",       dot: "bg-red-500"    },
  recommended: { label: "Direkomendasikan", color: "text-[#03AC0E] bg-green-50 border-green-200", dot: "bg-[#03AC0E]" },
  optional:    { label: "Opsional",    color: "text-gray-500 bg-gray-50 border-gray-200",    dot: "bg-gray-400"   },
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
  new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0 })
    .format(angka || 0)
    .replace("Rp", "Rp ");

const isSelected = (uuid: string) => !!props.modelValue[uuid];
</script>

<template>
  <div class="space-y-5">
    <div
      v-for="group in orderedGroups"
      :key="group.uuid"
      class="addon-group"
    >
      <!-- ── Group Header ── -->
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <!-- Dot accent -->
          <span
            class="w-2 h-2 rounded-full shrink-0"
            :class="groupTypeLabel[group.group_type]?.dot ?? 'bg-gray-400'"
            aria-hidden="true"
          />
          <span class="text-[13px] font-black text-gray-800 leading-none">{{ group.name }}</span>
          <!-- Required / type badge -->
          <span
            class="text-[9px] font-black px-1.5 py-0.5 rounded-full border uppercase tracking-wide leading-none"
            :class="groupTypeLabel[group.group_type]?.color ?? 'text-gray-500 bg-gray-50 border-gray-200'"
          >
            {{ groupTypeLabel[group.group_type]?.label ?? 'Opsional' }}
          </span>
        </div>

        <span class="text-[10px] text-gray-400 font-bold">
          {{ group.selection_type === 'single' ? 'Pilih 1' : 'Pilih beberapa' }}
        </span>
      </div>

      <!-- ── Item List (Tokopedia row style) ── -->
      <div class="space-y-2">
        <div
          v-for="item in group.items"
          :key="item.uuid"
          class="addon-row"
          :class="isSelected(item.uuid)
            ? 'border-[#03AC0E] bg-[#f0fef0]'
            : 'border-gray-100 bg-white hover:border-gray-200'"
          @click="toggleItem(group, item)"
          role="checkbox"
          :aria-checked="isSelected(item.uuid)"
          tabindex="0"
          @keydown.space.prevent="toggleItem(group, item)"
          @keydown.enter.prevent="toggleItem(group, item)"
        >
          <!-- Checkbox / Radio indicator -->
          <div class="shrink-0 mr-3">
            <div
              v-if="group.selection_type === 'single'"
              class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all"
              :class="isSelected(item.uuid)
                ? 'border-[#03AC0E] bg-[#03AC0E]'
                : 'border-gray-300 bg-white'"
            >
              <div
                v-if="isSelected(item.uuid)"
                class="w-1.5 h-1.5 bg-white rounded-full"
              />
            </div>
            <div
              v-else
              class="w-4 h-4 rounded border-2 flex items-center justify-center transition-all"
              :class="isSelected(item.uuid)
                ? 'border-[#03AC0E] bg-[#03AC0E]'
                : 'border-gray-300 bg-white'"
            >
              <UIcon
                v-if="isSelected(item.uuid)"
                name="i-heroicons-check"
                class="w-2.5 h-2.5 text-white"
              />
            </div>
          </div>

          <!-- Thumbnail -->
          <div class="w-10 h-10 shrink-0 rounded-lg overflow-hidden bg-gray-50 border border-gray-100 mr-3 flex items-center justify-center">
            <img
              v-if="item.image_url"
              :src="item.image_url"
              :alt="item.name"
              class="w-full h-full object-cover"
            />
            <UIcon
              v-else
              name="i-heroicons-cube"
              class="w-5 h-5 text-gray-300"
              aria-hidden="true"
            />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p class="text-[13px] font-bold text-gray-800 truncate leading-tight">{{ item.name }}</p>
            <div class="flex items-center gap-2 mt-0.5">
              <span
                v-if="item.price > 0"
                class="text-[12px] font-black"
                :class="isSelected(item.uuid) ? 'text-[#03AC0E]' : 'text-gray-700'"
              >
                +{{ formatRupiah(item.price) }}
              </span>
              <span v-else class="text-[11px] font-black text-[#03AC0E]">GRATIS</span>
              <span
                v-if="item.stock < 10"
                class="text-[9px] font-bold text-orange-500 bg-orange-50 px-1.5 py-0.5 rounded border border-orange-100"
              >
                Sisa {{ item.stock }}
              </span>
            </div>
          </div>

          <!-- Info button -->
          <button
            v-if="item.description"
            class="shrink-0 ml-2 w-7 h-7 flex items-center justify-center rounded-full text-gray-400 hover:text-[#03AC0E] hover:bg-green-50 transition-colors"
            :aria-label="`Detail ${item.name}`"
            @click.stop="showDetail(item)"
          >
            <UIcon name="i-heroicons-information-circle" class="w-4.5 h-4.5" />
          </button>

          <!-- Qty Adjuster (inline) -->
          <div
            v-if="isSelected(item.uuid) && item.allow_quantity"
            class="shrink-0 ml-2 flex items-center border border-[#03AC0E]/30 rounded-lg overflow-hidden bg-white"
            @click.stop
          >
            <button
              class="w-7 h-7 flex items-center justify-center text-[#03AC0E] hover:bg-green-50 transition-colors"
              :disabled="modelValue[item.uuid]?.quantity <= 1"
              @click="updateQty(item.uuid, -1, item.max_quantity)"
            >
              <UIcon name="i-heroicons-minus" class="w-3 h-3" />
            </button>
            <span class="w-6 text-center text-[12px] font-black text-gray-800">
              {{ modelValue[item.uuid]?.quantity ?? 1 }}
            </span>
            <button
              class="w-7 h-7 flex items-center justify-center text-[#03AC0E] hover:bg-green-50 transition-colors"
              :disabled="modelValue[item.uuid]?.quantity >= item.max_quantity"
              @click="updateQty(item.uuid, 1, item.max_quantity)"
            >
              <UIcon name="i-heroicons-plus" class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Detail Modal ── -->
    <UModal
      v-model="isDetailOpen"
      :ui="{
        width: 'sm:max-w-sm',
        rounded: 'rounded-2xl',
        padding: 'p-0',
      }"
    >
      <div v-if="activeDetail" class="p-6">
        <!-- Image -->
        <div class="aspect-square w-32 mx-auto rounded-2xl overflow-hidden bg-gray-50 border border-gray-100 mb-5 flex items-center justify-center">
          <img
            v-if="activeDetail.image_url"
            :src="activeDetail.image_url"
            :alt="activeDetail.name"
            class="w-full h-full object-contain p-3"
          />
          <UIcon v-else name="i-heroicons-cube" class="w-12 h-12 text-gray-200" />
        </div>

        <!-- Info -->
        <div class="text-center mb-5">
          <h4 class="text-base font-black text-gray-900 mb-1">{{ activeDetail.name }}</h4>
          <p v-if="activeDetail.price > 0" class="text-[#03AC0E] font-black text-lg">
            +{{ formatRupiah(activeDetail.price) }}
          </p>
          <p v-else class="text-[#03AC0E] font-black text-lg">GRATIS</p>
        </div>

        <!-- Description -->
        <p class="text-[13px] text-gray-500 leading-relaxed text-center mb-5">
          {{ activeDetail.description || 'Layanan tambahan untuk melengkapi kebutuhan Anda.' }}
        </p>

        <!-- Stats -->
        <div class="flex gap-3 mb-5">
          <div class="flex-1 bg-gray-50 rounded-xl p-3 text-center border border-gray-100">
            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wide mb-1">Stok</p>
            <p class="text-gray-900 font-black text-base">{{ activeDetail.stock }}</p>
          </div>
          <div class="flex-1 bg-gray-50 rounded-xl p-3 text-center border border-gray-100">
            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wide mb-1">Maks. Order</p>
            <p class="text-gray-900 font-black text-base">{{ activeDetail.max_quantity }}</p>
          </div>
        </div>

        <button
          class="w-full py-3 bg-[#03AC0E] text-white font-black rounded-xl text-sm hover:bg-[#028C0B] transition-colors"
          @click="isDetailOpen = false"
        >
          Mengerti
        </button>
      </div>
    </UModal>
  </div>
</template>

<style scoped>
.addon-group {
  background: #fff;
  border: 1.5px solid #f3f4f6;
  border-radius: 14px;
  padding: 14px 14px 12px;
}

.addon-row {
  display: flex;
  align-items: center;
  border: 1.5px solid;
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  outline: none;
  user-select: none;
}

.addon-row:focus-visible {
  box-shadow: 0 0 0 2px #03AC0E40;
}
</style>
