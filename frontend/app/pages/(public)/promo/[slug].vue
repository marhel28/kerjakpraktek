<script setup lang="ts">
import { ref, computed, watch } from 'vue'

import type {
  PromoResponse,
  PromoItemResponse,
  PromoPriceResult,
  PromoCheckoutRequest,
  PromoValidateResponse,
  PromoCheckoutResponse
} from '~/server/api/promo'

definePageMeta({ layout: 'public' })

const route = useRoute()
const slug = computed(() => route.params.slug as string)
const toast = useToast()

// ─── KOORDINAT TOKO (Ganti dengan koordinat asli tokomu) ─────────
const STORE_LAT = -6.873200 // Contoh: Latitude Padjajaran CCTV Cimahi
const STORE_LNG = 107.540400 // Contoh: Longitude Padjajaran CCTV Cimahi

// ─── Helpers ──────────────────────────────────────────────────────
const formatRp = (n: number) =>
  new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 })
    .format(n)
    .replace('Rp', 'Rp ')

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })

const todayISO = () => new Date().toISOString().split('T')[0]

const timeLeft = (until: string) => {
  const diff = new Date(until).getTime() - Date.now()
  if (diff <= 0) return 'Berakhir'
  const d = Math.floor(diff / 86400000)
  const h = Math.floor((diff % 86400000) / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  if (d > 0) return `${d} Hari ${h} Jam`
  if (h > 0) return `${h} Jam ${m} Menit`
  return `${m} menit lagi`
}

const discountLabel = (p: PromoResponse) => {
  if (!p) return ''
  if (p.promo_type === 'percentage' || p.promo_type === 'flash_sale') return `DISKON ${p.discount_value}%`
  if (p.promo_type === 'fixed') return `Hemat ${formatRp(p.discount_value)}`
  if (p.promo_type === 'bogo') return `Beli ${p.buy_quantity} Gratis ${p.get_quantity}`
  if (p.promo_type === 'bundle_disc') return `Bundle Diskon ${p.discount_value}%`
  return `Diskon ${p.discount_value}`
}

const quotaPercent = (p: PromoResponse) => {
  if (!p.quota) return 0
  return Math.round((p.used_count / p.quota) * 100)
}

// ─── Promo Data (Nuxt 4 SSR & SEO) ──────────────────────────────
const { data: promo, pending: isLoadingPromo } = await useAsyncData<PromoResponse | null>(
  `promo-${slug.value}`,
  () => $fetch('/api/promo', {
    query: { action: 'getPromo', slug: slug.value }
  }),
  { watch: [slug] }
)

useSeoMeta({
  title: () => promo.value ? `${promo.value.name} — Padjajaran CCTV` : 'Promo — Padjajaran CCTV',
  description: () => promo.value?.description || (promo.value ? `${promo.value.name}. ${discountLabel(promo.value)}. Berlaku hingga ${formatDate(promo.value.valid_until)}.` : 'Detail promo kamera CCTV dan paket instalasi dari Padjajaran CCTV Cimahi.'),
  ogTitle: () => promo.value ? `${promo.value.name} — Padjajaran CCTV` : 'Promo — Padjajaran CCTV',
  ogDescription: () => promo.value?.description || 'Detail promo kamera CCTV dan paket instalasi dari Padjajaran CCTV Cimahi.',
  ogImage: () => promo.value?.banner_url || undefined,
})

useHead({
  script: [
    {
      src: 'https://app.sandbox.midtrans.com/snap/snap.js',
      'data-client-key': 'SB-Mid-client-pn3mYe4w4xeY6F0w',
      async: true,
      tagPosition: 'bodyClose'
    },
  ],
})

// ─── Cart & Item Selection ───────────────────────────────────────
const selectedItems = ref<{ item: PromoItemResponse; quantity: number }[]>([])

const isItemSelected = (uuid: string) =>
  selectedItems.value.some((s) => s.item.item_uuid === uuid)

const toggleItem = (item: PromoItemResponse) => {
  const idx = selectedItems.value.findIndex((s) => s.item.item_uuid === item.item_uuid)
  if (idx >= 0) {
    selectedItems.value.splice(idx, 1)
  } else {
    selectedItems.value.push({ item, quantity: 1 })
  }
  doPricePreview()
}

const setQty = (uuid: string, qty: number) => {
  const entry = selectedItems.value.find((s) => s.item.item_uuid === uuid)
  if (entry) {
    entry.quantity = Math.max(1, qty)
    doPricePreview()
  }
}

// ─── Service Booking Form ────────────────────────────────────────
const hasServiceItems = computed(() =>
  selectedItems.value.some((s) => s.item.item_type === 'service_package')
)
const hasStockItems = computed(() =>
  selectedItems.value.some((s) => s.item.item_type === 'stock')
)

const serviceForm = ref({
  scheduled_date: '',
  time_slot: '',
  address_service: '',
  district: '',
  city: '',
  distance_km: 0 as number | '',
  latitude: undefined as number | undefined,
  longitude: undefined as number | undefined,
  contact_name: '',
  contact_phone: '',
  contact_notes: '',
})

const timeSlots = [
  '08:00-11:00',
  '10:00-13:00',
  '13:00-16:00',
  '15:00-18:00',
]

// ─── Geolocation Jarak Otomatis (Haversine Formula) ──────────────
const isLocating = ref(false)

const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
  const R = 6371 // Radius bumi dalam km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

const getBrowserLocation = () => {
  if (!navigator.geolocation) {
    toast.add({ title: 'Browser Anda tidak mendukung GPS', color: 'red' })
    return
  }

  isLocating.value = true
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const userLat = position.coords.latitude
      const userLng = position.coords.longitude
      
      serviceForm.value.latitude = userLat
      serviceForm.value.longitude = userLng
      
      // Kalkulasi jarak dan bulatkan 1 angka di belakang koma
      const distance = calculateDistance(STORE_LAT, STORE_LNG, userLat, userLng)
      serviceForm.value.distance_km = Number(distance.toFixed(1))
      
      toast.add({ title: 'Jarak berhasil dihitung!', color: 'green' })
      isLocating.value = false
      doPricePreview() // Update harga ongkos transport jika ada
    },
    (error) => {
      isLocating.value = false
      let errMsg = 'Gagal mengambil lokasi.'
      if (error.code === 1) errMsg = 'Izin lokasi ditolak browser.'
      else if (error.code === 2) errMsg = 'Lokasi tidak tersedia.'
      else if (error.code === 3) errMsg = 'Waktu pengambilan lokasi habis.'
      
      toast.add({ title: 'Gagal', description: errMsg, color: 'red' })
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  )
}

// ─── Shipping (for stock) ────────────────────────────────────────
const defaultAddress = ref<any>(null)
const shippingOptions = ref<any[]>([])
const selectedShipping = ref<any>(null)
const isLoadingAddress = ref(false)
const isLoadingShipping = ref(false)

const fetchDefaultAddress = async () => {
  if (!hasStockItems.value) return
  isLoadingAddress.value = true
  try {
    const res = await $fetch<{ data: any[] }>('/api/promo', {
      query: { action: 'getAddresses' }
    })
    const addresses = res.data || []
    defaultAddress.value = addresses.find((a: any) => a.is_default) || addresses[0] || null
    if (defaultAddress.value) fetchShippingOptions()
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingAddress.value = false
  }
}

const fetchShippingOptions = async () => {
  if (!defaultAddress.value || !selectedItems.value.length) return
  const stockEntry = selectedItems.value.find((s) => s.item.item_type === 'stock')
  if (!stockEntry) return
  
  isLoadingShipping.value = true
  try {
    const res = await $fetch<{ options: any[] }>('/api/promo', {
      query: {
        action: 'getShippingEstimate',
        address_uuid: defaultAddress.value.uuid,
        stock_uuid: stockEntry.item.item_uuid,
        quantity: selectedItems.value.filter((s) => s.item.item_type === 'stock').reduce((a, b) => a + b.quantity, 0),
        courier: 'jne:sicepat:jnt',
      }
    })
    shippingOptions.value = res.options || []
    if (shippingOptions.value.length > 0) selectedShipping.value = shippingOptions.value[0]
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingShipping.value = false
  }
}

watch(hasStockItems, (v) => { if (v) fetchDefaultAddress() })

// ─── Price Preview ────────────────────────────────────────────────
const priceResult = ref<PromoPriceResult | null>(null)
const isPreviewing = ref(false)
const previewMessage = ref('')

const doPricePreview = async () => {
  if (!promo.value || selectedItems.value.length === 0) {
    priceResult.value = null
    return
  }
  isPreviewing.value = true
  previewMessage.value = ''
  
  try {
    const stockItems = selectedItems.value
      .filter((s) => s.item.item_type === 'stock')
      .map((s) => ({ stock_uuid: s.item.item_uuid, quantity: s.quantity }))
    const serviceItems = selectedItems.value
      .filter((s) => s.item.item_type === 'service_package')
      .map((s) => ({ package_uuid: s.item.item_uuid, quantity: s.quantity }))

    const token = useCookie('token').value

    const res = await $fetch<PromoValidateResponse>('/api/promo?action=validatePromo', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: {
        promo_uuid: promo.value.uuid,
        stock_items: stockItems,
        service_items: serviceItems,
      }
    })
    
    if (res.is_valid && res.price_result) {
      priceResult.value = res.price_result
    } else {
      previewMessage.value = res.message
      priceResult.value = null
    }
  } catch (e: any) {
    previewMessage.value = e?.data?.detail || 'Gagal menghitung harga'
    priceResult.value = null
  } finally {
    isPreviewing.value = false
  }
}

// ─── Checkout & Error Modal ───────────────────────────────────────
const isCheckingOut = ref(false)
const checkoutStep = ref<'items' | 'detail' | 'confirm'>('items')

// Error Modal State
const showErrorModal = ref(false)
const errorModalTitle = ref('')
const errorModalMsg = ref('')

const canProceedToDetail = computed(() => selectedItems.value.length > 0)

const canConfirm = computed(() => {
  if (hasServiceItems.value) {
    return !!(
      serviceForm.value.scheduled_date &&
      serviceForm.value.time_slot &&
      serviceForm.value.address_service &&
      serviceForm.value.city &&
      serviceForm.value.contact_name &&
      serviceForm.value.contact_phone
    )
  }
  if (hasStockItems.value) {
    return !!defaultAddress.value && !!selectedShipping.value
  }
  return false
})

const handleCheckout = async () => {
  if (!promo.value) return
  isCheckingOut.value = true

  const payload: PromoCheckoutRequest = {
    promo_uuid: promo.value.uuid,
    stock_items: selectedItems.value
      .filter((s) => s.item.item_type === 'stock')
      .map((s) => ({ stock_uuid: s.item.item_uuid, quantity: s.quantity })),
    service_items: selectedItems.value
      .filter((s) => s.item.item_type === 'service_package')
      .map((s) => ({ package_uuid: s.item.item_uuid, quantity: s.quantity })),
  }

  if (hasStockItems.value && defaultAddress.value) {
    payload.address_uuid = defaultAddress.value.uuid
    payload.courier_name = selectedShipping.value?.courier?.toLowerCase() || 'jne'
    payload.courier_service = selectedShipping.value?.service || 'REG'
  }

  if (hasServiceItems.value) {
    Object.assign(payload, { 
      ...serviceForm.value,
      distance_km: Number(serviceForm.value.distance_km) || 0 
    })
  }

  try {
    const token = useCookie('token').value
    const res = await $fetch<PromoCheckoutResponse>('/api/promo?action=checkout', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: payload
    })

    if (res.snap_token && (window as any).snap) {
      ;(window as any).snap.pay(res.snap_token, {
        onSuccess: () => {
          toast.add({ title: 'Pembayaran Berhasil', color: 'green' })
          navigateTo(`/dashboard/promo-orders/${res.order_id}`)
        },
        onPending: () => {
          toast.add({ title: 'Menunggu Pembayaran', description: 'Selesaikan pembayaran Anda.', color: 'orange' })
          navigateTo(`/dashboard/promo-orders/${res.order_id}`)
        },
        onError: () => {
          toast.add({ title: 'Pembayaran Gagal', color: 'red' })
          navigateTo(`/dashboard/promo-orders/${res.order_id}`)
        },
        onClose: () => {
          navigateTo(`/dashboard/promo-orders/${res.order_id}`)
        },
      })
    } else {
      navigateTo(`/dashboard/promo-orders/${res.order_id}`)
    }
  } catch (e: any) {
    const msg = e?.data?.detail || 'Terjadi kesalahan internal saat checkout.'
    
    if (msg.includes('sudah memakai promo ini') || msg.includes('maksimum')) {
      errorModalTitle.value = 'Kuota Promo Habis'
      errorModalMsg.value = 'Anda sudah mencapai batas maksimal penggunaan promo ini. Silakan periksa promo lain yang tersedia.'
    } else {
      errorModalTitle.value = 'Checkout Gagal'
      errorModalMsg.value = msg
    }
    showErrorModal.value = true

  } finally {
    isCheckingOut.value = false
  }
}

const priceAfterDiscount = (item: PromoItemResponse) => {
  if (!promo.value) return item.item_price
  const entry = priceResult.value?.items.find((b) => b.item_uuid === item.item_uuid)
  return entry ? entry.after_discount : item.item_price
}

const discountForItem = (item: PromoItemResponse) => {
  const entry = priceResult.value?.items.find((b) => b.item_uuid === item.item_uuid)
  return entry?.discount_value || 0
}
</script>

<template>
  <main class="bg-[#F3F4F5] min-h-screen font-sans pb-16 text-gray-900">
    <header class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-[1200px] mx-auto px-4 md:px-6 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button @click="$router.back()" class="text-gray-500 hover:text-gray-900 flex items-center justify-center">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <nav class="text-sm font-medium text-gray-500 flex items-center gap-2">
            <NuxtLink to="/promo" class="hover:text-gray-900">Promo</NuxtLink>
            <span class="text-gray-300">/</span>
            <span class="text-gray-900 truncate max-w-[200px]">{{ promo?.name || 'Detail' }}</span>
          </nav>
        </div>

        <div class="hidden md:flex items-center gap-3 text-xs font-semibold">
          <template v-for="(stepName, i) in ['PILIH ITEM', 'PENGIRIMAN', 'KONFIRMASI']" :key="stepName">
            <div class="flex items-center gap-2" :class="checkoutStep === ['items', 'detail', 'confirm'][i] ? 'text-[#03AC0E]' : (i < ['items', 'detail', 'confirm'].indexOf(checkoutStep) ? 'text-[#03AC0E]' : 'text-gray-400')">
              <span class="w-5 h-5 flex items-center justify-center rounded-full text-[10px]" 
                :class="checkoutStep === ['items', 'detail', 'confirm'][i] ? 'bg-[#03AC0E] text-white' : (i < ['items', 'detail', 'confirm'].indexOf(checkoutStep) ? 'bg-[#03AC0E] text-white' : 'bg-gray-100 text-gray-400 border border-gray-200')">
                {{ i + 1 }}
              </span>
              <span class="uppercase tracking-wide">{{ stepName }}</span>
            </div>
            <div v-if="i < 2" class="w-8 h-[1px] bg-gray-200"></div>
          </template>
        </div>
      </div>
    </header>

    <div v-if="isLoadingPromo" class="max-w-[1200px] mx-auto px-4 md:px-6 mt-6 flex flex-col lg:flex-row gap-6">
      <div class="flex-1 space-y-4">
        <div class="h-48 bg-gray-200 animate-pulse rounded-lg"></div>
        <div class="bg-white rounded-lg p-6 space-y-3 border border-gray-200">
          <div class="h-5 bg-gray-100 animate-pulse rounded w-1/3"></div>
          <div class="h-4 bg-gray-100 animate-pulse rounded w-1/4"></div>
        </div>
      </div>
      <div class="w-full lg:w-[340px] h-64 bg-gray-200 animate-pulse rounded-lg shrink-0"></div>
    </div>

    <div v-else-if="promo" class="max-w-[1200px] mx-auto px-4 md:px-6 mt-6">
      <div class="flex flex-col lg:flex-row gap-6 items-start">
        
        <div class="flex-1 min-w-0 space-y-6">
          
          <section class="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col md:flex-row">
            <div class="w-full md:w-[300px] h-48 md:h-auto bg-gray-900 shrink-0">
              <img v-if="promo.banner_url" :src="promo.banner_url" :alt="promo.name" class="w-full h-full object-cover" />
            </div>

            <div class="flex-1 flex flex-col justify-between">
              <div class="p-5 md:p-6">
                <div class="flex items-center gap-2 mb-3">
                  <span v-if="promo.is_flash_sale" class="bg-[#FFEAEA] text-[#EF144A] font-bold text-[10px] uppercase tracking-wider px-2 py-1 rounded">
                    FLASH SALE
                  </span>
                  <span class="bg-[#D6FFDE] text-[#03AC0E] font-bold text-[10px] uppercase tracking-wider px-2 py-1 rounded">
                    {{ discountLabel(promo) }}
                  </span>
                </div>

                <h1 class="text-gray-900 font-bold text-xl md:text-2xl mb-6">{{ promo.name }}</h1>

                <div class="grid grid-cols-2 gap-8">
                  <div>
                    <div class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1">BERLAKU HINGGA</div>
                    <div class="text-sm font-medium text-gray-900">{{ formatDate(promo.valid_until) }}</div>
                    <div class="text-[12px] text-[#EF144A] mt-0.5">{{ timeLeft(promo.valid_until) }}</div>
                  </div>
                  <div v-if="promo.quota">
                    <div class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1">KETERSEDIAAN KUOTA</div>
                    <div class="flex items-center gap-3 mt-1.5">
                      <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                        <div class="bg-gray-300 h-1.5 rounded-full" :style="{ width: `${quotaPercent(promo)}%` }"></div>
                      </div>
                      <span class="text-xs font-medium text-gray-900">{{ promo.remaining_quota || promo.quota }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-3 divide-x divide-gray-100 border-t border-gray-100 bg-gray-50/50">
                <div class="p-4">
                  <div class="text-[11px] font-medium text-gray-500 mb-1">Min. Transaksi</div>
                  <div class="text-[13px] font-medium text-gray-900">{{ promo.min_purchase > 0 ? formatRp(promo.min_purchase) : 'Tanpa minimum' }}</div>
                </div>
                <div class="p-4">
                  <div class="text-[11px] font-medium text-gray-500 mb-1">Batas Penggunaan</div>
                  <div class="text-[13px] font-medium text-gray-900">{{ promo.max_use_per_user ? `Maks. ${promo.max_use_per_user}x per akun` : 'Tanpa batas' }}</div>
                </div>
                <div class="p-4">
                  <div class="text-[11px] font-medium text-gray-500 mb-1">Ketentuan Tambahan</div>
                  <div class="text-[13px] font-medium text-gray-900 line-clamp-2" :title="promo.description">
                    {{ promo.description || 'Syarat & ketentuan berlaku.' }}
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section v-if="checkoutStep === 'items'" class="bg-white rounded-lg border border-gray-200">
            <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 class="font-bold text-lg text-gray-900">Daftar Item Promo</h2>
              <span class="text-xs font-medium text-gray-600 bg-gray-100 px-3 py-1 rounded-md">{{ selectedItems.length }} Terpilih</span>
            </div>

            <div v-if="promo.items.length === 0" class="p-8 text-center border-b border-gray-200">
              <p class="text-sm text-gray-500">Berlaku untuk semua produk/jasa dalam kategori promosi ini.</p>
            </div>

            <div v-else class="divide-y divide-gray-100">
              <label 
                v-for="item in promo.items" 
                :key="item.uuid"
                class="flex items-start md:items-center gap-4 p-5 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div class="pt-1 md:pt-0 shrink-0">
                  <div :class="[
                    'w-[18px] h-[18px] rounded flex items-center justify-center border transition-colors',
                    isItemSelected(item.item_uuid) ? 'bg-[#03AC0E] border-[#03AC0E]' : 'border-gray-300 bg-white'
                  ]">
                    <svg v-if="isItemSelected(item.item_uuid)" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <input type="checkbox" class="hidden" @change="toggleItem(item)" :checked="isItemSelected(item.item_uuid)" />
                </div>

                <div class="w-[60px] h-[60px] rounded border border-gray-200 bg-white flex items-center justify-center overflow-hidden shrink-0">
                  <img v-if="item.thumbnail_url" :src="item.thumbnail_url" class="w-full h-full object-contain" />
                  <span v-else class="text-[10px] text-gray-400 font-medium">NO IMG</span>
                </div>

                <div class="flex-1 min-w-0">
                  <h3 class="font-medium text-sm text-gray-900 leading-snug mb-2">{{ item.item_name }}</h3>
                  <div class="flex items-center gap-2">
                    <span v-if="item.item_type === 'service_package'" class="text-[10px] font-medium text-[#8E44AD] bg-[#F4EAF9] border border-[#E1C2F1] uppercase px-1.5 py-0.5 rounded-sm">
                      JASA INSTALASI
                    </span>
                    <span v-else class="text-[10px] font-medium text-gray-600 bg-gray-100 border border-gray-200 uppercase px-1.5 py-0.5 rounded-sm">
                      PRODUK
                    </span>
                    <span v-if="item.override_discount_value" class="text-[10px] font-medium text-gray-500">
                      Diskon Khusus Item
                    </span>
                  </div>
                </div>

                <div class="text-right shrink-0 flex flex-col items-end gap-1">
                  <div class="text-xs text-gray-400 line-through">{{ formatRp(item.item_price) }}</div>
                  <div class="font-bold text-sm text-gray-900">
                    {{ formatRp(isItemSelected(item.item_uuid) ? priceAfterDiscount(item) : item.item_price) }}
                  </div>
                  
                  <div v-if="isItemSelected(item.item_uuid)" class="flex items-center border border-gray-300 rounded bg-white mt-1">
                    <button @click.stop.prevent="setQty(item.item_uuid, (selectedItems.find(s=>s.item.item_uuid===item.item_uuid)?.quantity||1)-1)" class="w-6 h-6 flex items-center justify-center text-gray-500 hover:bg-gray-50">−</button>
                    <div class="w-8 text-center text-[13px] font-medium text-gray-900 border-x border-gray-300 h-6 flex items-center justify-center">{{ selectedItems.find(s=>s.item.item_uuid===item.item_uuid)?.quantity || 1 }}</div>
                    <button @click.stop.prevent="setQty(item.item_uuid, (selectedItems.find(s=>s.item.item_uuid===item.item_uuid)?.quantity||1)+1)" class="w-6 h-6 flex items-center justify-center text-[#03AC0E] hover:bg-gray-50">+</button>
                  </div>
                </div>
              </label>
            </div>

            <div v-if="previewMessage" class="mx-5 mb-5 mt-2 bg-red-50 text-red-600 text-xs p-3 rounded-md border border-red-100">
              {{ previewMessage }}
            </div>

            <div class="p-5">
              <button
                @click="checkoutStep = 'detail'; fetchDefaultAddress()"
                :disabled="!canProceedToDetail"
                class="w-full bg-[#03AC0E] text-white font-bold py-3 rounded-lg text-[15px] hover:bg-[#028c0b] disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors"
              >
                Lanjutkan
              </button>
            </div>
          </section>

          <section v-if="checkoutStep === 'detail'" class="space-y-6">
            
            <div v-if="hasServiceItems" class="bg-white rounded-lg border border-gray-200">
              <div class="px-5 py-4 border-b border-gray-200">
                <h2 class="font-bold text-lg text-gray-900">Jadwal & Lokasi Pemasangan</h2>
              </div>
              <div class="p-5 space-y-5">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label class="block text-[13px] font-bold text-gray-700 mb-2">Tanggal Pemasangan <span class="text-[#EF144A]">*</span></label>
                    <input v-model="serviceForm.scheduled_date" type="date" :min="todayISO()" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E]" />
                  </div>
                  <div>
                    <label class="block text-[13px] font-bold text-gray-700 mb-2">Slot Waktu <span class="text-[#EF144A]">*</span></label>
                    <div class="grid grid-cols-2 gap-2">
                      <button v-for="slot in timeSlots" :key="slot" @click="serviceForm.time_slot = slot"
                        :class="['text-[13px] font-semibold py-2 px-3 rounded-md border transition-colors',
                          serviceForm.time_slot === slot ? 'bg-[#D6FFDE] text-[#03AC0E] border-[#03AC0E]' : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'
                        ]">{{ slot }}</button>
                    </div>
                  </div>
                </div>

                <div>
                  <label class="block text-[13px] font-bold text-gray-700 mb-2">Alamat Lengkap <span class="text-[#EF144A]">*</span></label>
                  <textarea v-model="serviceForm.address_service" rows="2" placeholder="Detail jalan, nomor rumah..." class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] resize-none"></textarea>
                </div>

                <div class="grid grid-cols-2 gap-5">
                  <div>
                    <label class="block text-[13px] font-bold text-gray-700 mb-2">Kecamatan</label>
                    <input v-model="serviceForm.district" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E]" />
                  </div>
                  <div>
                    <label class="block text-[13px] font-bold text-gray-700 mb-2">Kota / Kabupaten <span class="text-[#EF144A]">*</span></label>
                    <input v-model="serviceForm.city" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E]" />
                  </div>
                </div>

                <div class="bg-gray-50 border border-gray-200 rounded-md p-4">
                  <label class="block text-[13px] font-bold text-gray-700 mb-2">Jarak dari Toko (km)</label>
                  <div class="flex flex-col sm:flex-row gap-3 items-center">
                    <div class="relative w-full sm:w-1/2">
                      <input v-model.number="serviceForm.distance_km" type="number" min="0" step="0.1" @blur="doPricePreview" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E]" />
                      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-gray-400">km</span>
                    </div>
                    <span class="text-[13px] text-gray-400 font-medium">atau</span>
                    <button @click="getBrowserLocation" :disabled="isLocating" class="w-full sm:w-auto bg-white border border-gray-300 text-gray-700 font-bold text-[13px] px-4 py-2 rounded-md hover:bg-gray-50 disabled:opacity-50 flex items-center justify-center gap-2">
                      <svg v-if="isLocating" class="animate-spin w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                      <svg v-else class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                      Hitung Otomatis
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label class="block text-[13px] font-bold text-gray-700 mb-2">Nama Kontak <span class="text-[#EF144A]">*</span></label>
                    <input v-model="serviceForm.contact_name" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E]" />
                  </div>
                  <div>
                    <label class="block text-[13px] font-bold text-gray-700 mb-2">No. Telepon <span class="text-[#EF144A]">*</span></label>
                    <input v-model="serviceForm.contact_phone" type="tel" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E]" />
                  </div>
                </div>
              </div>
            </div>

            <div v-if="hasStockItems" class="bg-white rounded-lg border border-gray-200">
              <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
                <h2 class="font-bold text-lg text-gray-900">Alamat Pengiriman</h2>
                <NuxtLink to="/dashboard/address" class="text-[13px] font-bold text-[#03AC0E] hover:underline">Ubah Alamat</NuxtLink>
              </div>
              <div class="p-5 border-b border-gray-200">
                <div v-if="isLoadingAddress" class="h-12 bg-gray-100 animate-pulse rounded-md"></div>
                <div v-else-if="!defaultAddress" class="text-sm text-gray-500">Belum ada alamat pengiriman.</div>
                <div v-else>
                  <p class="font-bold text-[15px] text-gray-900">{{ defaultAddress.label }}</p>
                  <p class="text-[13px] text-gray-600 mt-1">{{ defaultAddress.full_address }}</p>
                  <p class="text-[13px] text-gray-500 mt-1">{{ defaultAddress.zip_code }}</p>
                </div>
              </div>

              <div v-if="defaultAddress" class="p-5">
                <h3 class="text-[13px] font-bold text-gray-700 mb-3">Metode Pengiriman</h3>
                <div v-if="isLoadingShipping" class="space-y-2">
                  <div v-for="i in 2" :key="i" class="h-12 bg-gray-100 animate-pulse rounded-md"></div>
                </div>
                <div v-else-if="shippingOptions.length === 0" class="text-sm text-gray-500">
                  Tidak ada opsi pengiriman tersedia.
                </div>
                <div v-else class="space-y-3">
                  <label v-for="(opt, i) in shippingOptions" :key="i"
                    :class="['flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors',
                      selectedShipping?.service === opt.service && selectedShipping?.courier === opt.courier ? 'border-[#03AC0E] bg-[#D6FFDE]/30' : 'border-gray-200 hover:border-gray-300'
                    ]">
                    <div class="flex items-center gap-3">
                      <input type="radio" :value="opt" v-model="selectedShipping" class="text-[#03AC0E] focus:ring-[#03AC0E]" />
                      <div>
                        <div class="font-bold text-[13px] text-gray-900 uppercase">{{ opt.courier }} - {{ opt.service }}</div>
                        <div class="text-[12px] text-gray-500 mt-0.5">Estimasi tiba: {{ opt.etd || '-' }}</div>
                      </div>
                    </div>
                    <div class="font-bold text-[13px] text-gray-900">{{ formatRp(opt.price) }}</div>
                  </label>
                </div>
              </div>
            </div>

            <div class="flex gap-4">
              <button @click="checkoutStep = 'items'" class="flex-1 bg-white border border-gray-300 text-gray-700 font-bold py-3 rounded-lg text-[15px] hover:bg-gray-50 transition-colors">Kembali</button>
              <button @click="checkoutStep = 'confirm'" :disabled="!canConfirm" class="flex-1 bg-[#03AC0E] text-white font-bold py-3 rounded-lg text-[15px] hover:bg-[#028c0b] disabled:bg-gray-300 disabled:text-gray-500 transition-colors">Lanjutkan</button>
            </div>
          </section>

          <section v-if="checkoutStep === 'confirm'" class="bg-white rounded-lg border border-gray-200">
            <div class="px-5 py-4 border-b border-gray-200">
              <h2 class="font-bold text-lg text-gray-900">Konfirmasi Pesanan</h2>
            </div>

            <div class="p-5 space-y-6">
              <div>
                <h3 class="text-[13px] font-bold text-gray-700 mb-3 border-b border-gray-100 pb-2">Daftar Item</h3>
                <div class="space-y-3">
                  <div v-for="s in selectedItems" :key="s.item.uuid" class="flex justify-between items-start">
                    <div>
                      <div class="text-[13px] font-medium text-gray-900">{{ s.item.item_name }}</div>
                      <div class="text-[12px] text-gray-500 mt-0.5">{{ s.quantity }} x {{ formatRp(priceAfterDiscount(s.item)) }}</div>
                    </div>
                    <div class="text-[13px] font-bold text-gray-900">{{ formatRp(priceAfterDiscount(s.item) * s.quantity) }}</div>
                  </div>
                </div>
              </div>

              <div v-if="hasServiceItems && serviceForm.scheduled_date">
                <h3 class="text-[13px] font-bold text-gray-700 mb-3 border-b border-gray-100 pb-2">Informasi Pemasangan</h3>
                <div class="text-[13px] text-gray-700 space-y-2">
                  <div class="flex gap-4"><span class="w-24 text-gray-500">Jadwal</span> <span class="font-medium text-gray-900">{{ serviceForm.scheduled_date }}, {{ serviceForm.time_slot }}</span></div>
                  <div class="flex gap-4"><span class="w-24 text-gray-500">Alamat</span> <span class="font-medium text-gray-900">{{ serviceForm.address_service }}, {{ serviceForm.city }} ({{ serviceForm.distance_km || 0 }} km)</span></div>
                  <div class="flex gap-4"><span class="w-24 text-gray-500">Kontak</span> <span class="font-medium text-gray-900">{{ serviceForm.contact_name }} ({{ serviceForm.contact_phone }})</span></div>
                </div>
              </div>

              <div v-if="hasStockItems && defaultAddress">
                <h3 class="text-[13px] font-bold text-gray-700 mb-3 border-b border-gray-100 pb-2">Informasi Pengiriman</h3>
                <div class="text-[13px] text-gray-700 space-y-2">
                  <div class="flex gap-4"><span class="w-24 text-gray-500">Alamat</span> <span class="font-medium text-gray-900">{{ defaultAddress.full_address }}</span></div>
                  <div v-if="selectedShipping" class="flex gap-4"><span class="w-24 text-gray-500">Kurir</span> <span class="font-medium text-gray-900 uppercase">{{ selectedShipping.courier }} - {{ selectedShipping.service }}</span></div>
                </div>
              </div>
            </div>

            <div class="p-5 border-t border-gray-200 bg-gray-50 flex gap-4">
              <button @click="checkoutStep = 'detail'" class="w-1/3 bg-white border border-gray-300 text-gray-700 font-bold py-3 rounded-lg text-[15px] hover:bg-gray-100 transition-colors">Kembali</button>
              <button @click="handleCheckout" :disabled="isCheckingOut" class="w-2/3 bg-[#03AC0E] text-white font-bold py-3 rounded-lg text-[15px] hover:bg-[#028c0b] disabled:opacity-50 transition-colors flex justify-center items-center gap-2">
                <svg v-if="isCheckingOut" class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span v-else>Bayar Sekarang</span>
              </button>
            </div>
          </section>

        </div>

        <aside class="w-full lg:w-[320px] xl:w-[360px] shrink-0">
          <div class="sticky top-24 bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <h3 class="font-bold text-base text-gray-900 pb-4 border-b border-gray-200">Ringkasan Transaksi</h3>

            <div v-if="selectedItems.length === 0" class="text-[13px] text-gray-500 py-12 text-center">
              Belum ada item terpilih
            </div>

            <div v-else class="space-y-3 mt-4 text-[13px]">
              <div class="flex justify-between text-gray-600">
                <span>Total Harga Asli</span>
                <span>{{ priceResult ? formatRp(priceResult.items_subtotal_original) : '-' }}</span>
              </div>
              <div v-if="priceResult && priceResult.total_discount > 0" class="flex justify-between text-[#03AC0E]">
                <span>Total Diskon</span>
                <span>- {{ formatRp(priceResult.total_discount) }}</span>
              </div>
              <div v-if="priceResult && priceResult.service_cost > 0" class="flex justify-between text-gray-600">
                <span>Biaya Transportasi</span>
                <span>{{ formatRp(priceResult.service_cost) }}</span>
              </div>
              <div v-if="selectedShipping" class="flex justify-between text-gray-600">
                <span>Ongkos Kirim</span>
                <span>{{ formatRp(selectedShipping.price || 0) }}</span>
              </div>
            </div>

            <div v-if="isPreviewing" class="my-4 space-y-2">
              <div class="h-2 bg-gray-100 rounded w-full"></div>
              <div class="h-2 bg-gray-100 rounded w-2/3"></div>
            </div>

            <div class="pt-4 mt-4 border-t border-gray-200" v-if="priceResult">
              <div class="flex justify-between items-center">
                <span class="text-sm font-bold text-gray-900">Total Tagihan</span>
                <span class="text-lg font-bold text-gray-900">
                  {{ formatRp(priceResult.items_subtotal_discounted + priceResult.service_cost + (selectedShipping?.price || 0)) }}
                </span>
              </div>
            </div>

            <p class="text-[11px] text-gray-500 mt-6 leading-relaxed text-center">
              Dengan melanjutkan, Anda menyetujui <NuxtLink to="/terms" class="text-gray-900 font-medium underline">Syarat & Ketentuan</NuxtLink>.
            </p>
          </div>
        </aside>

      </div>
    </div>

    <div v-else-if="!isLoadingPromo" class="max-w-[1200px] mx-auto px-4 py-20 text-center">
      <h2 class="font-bold text-gray-900 text-xl">Promo Tidak Ditemukan</h2>
      <p class="text-gray-500 text-sm mt-2 mb-6">Promo yang Anda tuju mungkin sudah berakhir atau tidak tersedia.</p>
      <NuxtLink to="/promo" class="inline-block bg-[#03AC0E] text-white font-bold px-6 py-2.5 rounded-lg hover:bg-[#028c0b] transition-colors text-sm">
        Kembali ke Daftar Promo
      </NuxtLink>
    </div>

    <div v-if="showErrorModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-gray-900/50" @click="showErrorModal = false"></div>
      <div class="relative bg-white rounded-lg w-full max-w-sm shadow-xl p-6 text-center">
        <h3 class="text-lg font-bold text-gray-900 mb-2">{{ errorModalTitle }}</h3>
        <p class="text-[13px] text-gray-600 mb-6 leading-relaxed">{{ errorModalMsg }}</p>
        
        <div class="space-y-3">
          <button @click="showErrorModal = false" class="w-full bg-[#03AC0E] text-white font-bold py-2.5 rounded-lg text-[13px] hover:bg-[#028c0b] transition-colors">
            Tutup
          </button>
          <NuxtLink v-if="errorModalTitle.includes('Habis')" to="/promo" class="block w-full bg-white border border-gray-300 text-gray-700 font-bold py-2.5 rounded-lg text-[13px] hover:bg-gray-50 transition-colors">
            Cari Promo Lain
          </NuxtLink>
        </div>
      </div>
    </div>

  </main>
</template>

<style scoped>
/* Reset form numbers di browser modern */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
}
</style>