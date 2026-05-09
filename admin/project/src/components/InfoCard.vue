<template>
    <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
      <!-- Header -->
      <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div v-if="icon" :class="['w-7 h-7 rounded-lg flex items-center justify-center shrink-0', iconBg]">
            <svg class="w-4 h-4" :class="iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icon" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-800">{{ title }}</h3>
            <p v-if="subtitle" class="text-xs text-slate-400 mt-0.5">{{ subtitle }}</p>
          </div>
        </div>
        <slot name="action" />
      </div>
      <!-- Body -->
      <div class="p-5">
        <slot />
      </div>
    </div>
  </template>
  
  <script setup>
  defineProps({
    title:    { type: String, required: true },
    subtitle: { type: String, default: '' },
    icon:     { type: String, default: '' },
    iconBg:   { type: String, default: 'bg-slate-100' },
    iconColor:{ type: String, default: 'text-slate-600' },
  })
  </script>