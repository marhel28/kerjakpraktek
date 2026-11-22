<template>
    <span :class="['inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold whitespace-nowrap', config.class]">
      <span :class="['w-1.5 h-1.5 rounded-full shrink-0', config.dot]" />
      {{ config.label }}
    </span>
  </template>
  
  <script setup>
  const props = defineProps({
    type: { type: String, default: 'payment' }, // 'payment' | 'delivery'
    status: { type: String, default: '' },
  })
  
  const PAYMENT_MAP = {
    pending:          { label: 'Menunggu',   class: 'bg-amber-50 text-amber-700',   dot: 'bg-amber-500' },
    pending_payment:  { label: 'Menunggu',   class: 'bg-amber-50 text-amber-700',   dot: 'bg-amber-500' },
    settlement:       { label: 'Lunas',      class: 'bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500' },
    capture:          { label: 'Capture',    class: 'bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500' },
    cancel:           { label: 'Dibatalkan', class: 'bg-slate-100 text-slate-500',   dot: 'bg-slate-400' },
    deny:             { label: 'Ditolak',    class: 'bg-red-50 text-red-600',        dot: 'bg-red-500' },
    expire:           { label: 'Kedaluwarsa',class: 'bg-red-50 text-red-600',        dot: 'bg-red-500' },
    failed:           { label: 'Gagal',      class: 'bg-red-50 text-red-600',        dot: 'bg-red-500' },
    refund:           { label: 'Refund',     class: 'bg-violet-50 text-violet-600',  dot: 'bg-violet-500' },
  }
  
  const DELIVERY_MAP = {
    PENDING:     { label: 'Pending',    class: 'bg-slate-100 text-slate-500',    dot: 'bg-slate-400' },
    PROCESSING:  { label: 'Diproses',   class: 'bg-blue-50 text-blue-600',       dot: 'bg-blue-500' },
    SHIPPED:     { label: 'Dikirim',    class: 'bg-indigo-50 text-indigo-600',   dot: 'bg-indigo-500' },
    DELIVERED:   { label: 'Terkirim',   class: 'bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500' },
    CANCELLED:   { label: 'Dibatalkan', class: 'bg-red-50 text-red-600',         dot: 'bg-red-500' },
    RETURNED:    { label: 'Dikembalikan', class: 'bg-amber-50 text-amber-700',   dot: 'bg-amber-500' },
  }
  
  const FALLBACK = { label: '-', class: 'bg-slate-100 text-slate-400', dot: 'bg-slate-300' }
  
  const config = computed(() => {
    const map = props.type === 'delivery' ? DELIVERY_MAP : PAYMENT_MAP
    return map[props.status] || { ...FALLBACK, label: props.status || '-' }
  })
  </script>
  
  <script>
  import { computed } from 'vue'
  export default { name: 'StatusBadge' }
  </script>