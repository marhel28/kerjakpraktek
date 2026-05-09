<template>
    <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
      <!-- Table wrapper -->
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50/80">
              <th
                v-for="col in columns"
                :key="col.key"
                :class="['px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap', col.thClass || '']"
              >
                {{ col.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <!-- Loading -->
            <tr v-if="loading" v-for="n in 5" :key="'sk-' + n" class="border-b border-slate-50">
              <td v-for="col in columns" :key="col.key" class="px-4 py-3.5">
                <div class="h-4 bg-slate-100 rounded animate-pulse" :style="{ width: Math.random() * 40 + 50 + '%' }" />
              </td>
            </tr>
            <!-- Empty -->
            <tr v-else-if="!rows.length">
              <td :colspan="columns.length" class="text-center py-16 text-slate-400">
                <div class="flex flex-col items-center gap-2">
                  <svg class="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <span class="text-sm">{{ emptyText }}</span>
                </div>
              </td>
            </tr>
            <!-- Rows -->
            <tr
              v-else
              v-for="(row, idx) in rows"
              :key="row[rowKey] || idx"
              :class="[
                'border-b border-slate-50 transition-colors duration-150',
                clickable ? 'cursor-pointer hover:bg-slate-50/80 active:bg-slate-100' : ''
              ]"
              @click="clickable && $emit('row-click', row)"
            >
              <slot name="row" :row="row" :idx="idx">
                <td
                  v-for="col in columns"
                  :key="col.key"
                  :class="['px-4 py-3.5 text-slate-700', col.tdClass || '']"
                >
                  {{ row[col.key] ?? '—' }}
                </td>
              </slot>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- Pagination -->
      <div v-if="total > 0" class="px-5 py-3.5 border-t border-slate-100 flex items-center justify-between">
        <p class="text-xs text-slate-500">
          {{ (page - 1) * limit + 1 }}–{{ Math.min(page * limit, total) }} dari {{ total }} data
        </p>
        <div class="flex items-center gap-1.5">
          <button
            :disabled="page <= 1"
            @click="$emit('update:page', page - 1)"
            class="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >← Prev</button>
          <span class="px-3 py-1.5 rounded-lg bg-slate-900 text-white text-xs font-bold">{{ page }}</span>
          <button
            :disabled="page >= totalPage"
            @click="$emit('update:page', page + 1)"
            class="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >Next →</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  defineProps({
    columns:   { type: Array,   required: true },
    rows:      { type: Array,   default: () => [] },
    loading:   { type: Boolean, default: false },
    clickable: { type: Boolean, default: false },
    rowKey:    { type: String,  default: 'uuid' },
    emptyText: { type: String,  default: 'Tidak ada data' },
    page:      { type: Number,  default: 1 },
    limit:     { type: Number,  default: 10 },
    total:     { type: Number,  default: 0 },
    totalPage: { type: Number,  default: 1 },
  })
  defineEmits(['row-click', 'update:page'])
  </script>