<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCheckoutStore } from '~/stores/checkout'

definePageMeta({ layout: 'public' })

useHead({
  script: [
    {
      src: 'https://app.sandbox.midtrans.com/snap/snap.js',
      'data-client-key': 'SB-Mid-client-pn3mYe4w4xeY6F0w', 
      async: true
    }
  ]
})

const checkoutStore = useCheckoutStore()
const API_TRANSAKSI = 'http://127.0.0.1:8000/transaksi'
const API_CEK = 'http://127.0.0.1:8000/cek'

const getToken = () => useCookie('token').value
const toast = useToast()

const defaultAddress = ref<any>(null)
const shippingOptions = ref<any[]>([])
const selectedShipping = ref<any>(null)

const isLoadingAddress = ref(true)
const isLoadingShipping = ref(false)
const isCheckingOut = ref(false)

onMounted(() => {
  if (checkoutStore.items.length === 0) {
    navigateTo('/cart')
    return
  }
  fetchDefaultAddress()
})

const fetchDefaultAddress = async () => {
  isLoadingAddress.value = true
  try {
    const response: any = await $fetch(`${API_CEK}/shipping/address`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    
    const addresses = response.data || []
    defaultAddress.value = addresses.find((a: any) => a.is_default) || addresses[0] || null

    if (defaultAddress.value) {
      await fetchShippingEstimate()
    }
  } catch (err) {
    console.error('Gagal mengambil alamat:', err)
  } finally {
    isLoadingAddress.value = false
  }
}

const fetchShippingEstimate = async () => {
  isLoadingShipping.value = true
  try {
    const representativeStockUuid = checkoutStore.items[0].stock_uuid
    
    const response: any = await $fetch(`${API_TRANSAKSI}/shipping/estimate`, {
      method: 'GET',
      query: {
        address_uuid: defaultAddress.value.uuid,
        stock_uuid: representativeStockUuid,
        quantity: checkoutStore.totalQuantity,
        courier: 'jne:sicepat:jnt'
        
      },
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    
    shippingOptions.value = response.options || []
    if (shippingOptions.value.length > 0) {
      selectedShipping.value = shippingOptions.value[0]
    }
  } catch (err) {
    console.error('Gagal memuat estimasi ongkir:', err)
    toast.add({ title: 'Ongkir Gagal', description: 'Gagal memuat layanan pengiriman.', color: 'red' })
  } finally {
    isLoadingShipping.value = false
  }
}

const getStandardCourierCode = (rawName: string) => {
  const name = (rawName || '').toLowerCase()
  if (name.includes('jne')) return 'jne'
  if (name.includes('j&t') || name.includes('jnt')) return 'jnt'
  if (name.includes('sicepat')) return 'sicepat'
  if (name.includes('pos')) return 'pos'
  return 'jne' 
}

const handleCheckout = async () => {
  if (!defaultAddress.value) {
    alert('Silakan tambahkan alamat pengiriman terlebih dahulu.')
    return
  }
  if (!selectedShipping.value) {
    alert('Silakan pilih layanan pengiriman.')
    return
  }

  isCheckingOut.value = true

  const payload = {
    items: checkoutStore.items.map(item => ({
      stock_uuid: item.stock_uuid,
      quantity: item.quantity
    })),
    address_uuid: defaultAddress.value.uuid,
    courier_name: getStandardCourierCode(selectedShipping.value.courier),
    courier_service: selectedShipping.value.service,
    coupon_code: checkoutStore.promoCode || null 
  }

  try {
    const response: any = await $fetch(`${API_TRANSAKSI}/checkout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: payload
    })

    checkoutStore.clearCheckoutData()

    if (response.snap_token && (window as any).snap) {
      (window as any).snap.pay(response.snap_token, {
        onSuccess: function(result: any) {
          toast.add({ title: 'Pembayaran Berhasil', color: 'green' })
          navigateTo(`/dashboard/order/${response.order_id}`)
        },
        onPending: function(result: any) {
          toast.add({ title: 'Menunggu Pembayaran', description: 'Selesaikan pembayaran Anda.', color: 'orange' })
          navigateTo(`/dashboard/order/${response.order_id}`)
        },
        onError: function(result: any) {
          toast.add({ title: 'Pembayaran Gagal', color: 'red' })
          navigateTo(`/dashboard/order/${response.order_id}`)
        },
        onClose: function() {
          navigateTo(`/dashboard/order/${response.order_id}`)
        }
      })
    } else {
      navigateTo(`/dashboard/order/${response.order_id}`)
    }
    
  } catch (err: any) {
    console.error('Checkout Error:', err)
    const errorMsg = err.data?.detail || 'Terjadi kesalahan saat memproses pesanan.'
    alert(`Gagal Checkout: ${errorMsg}`)
  } finally {
    isCheckingOut.value = false
  }
}

const formatRupiah = (angka: number) => {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(angka || 0).replace('Rp', 'Rp ')
}

// ✅ TAMBAHAN: Formatter Berat (Gram / Kg)
const formatWeight = (grams: number | undefined) => {
  if (!grams) return '0 gr'
  return grams >= 1000 ? `${(grams / 1000).toFixed(2).replace(/\.00$/, '')} kg` : `${grams} gr`
}

const shippingCost = computed(() => selectedShipping.value?.price || 0)
const finalGrandTotal = computed(() => checkoutStore.grandTotal + shippingCost.value)
</script>

<template>
  <main class="bg-[#F3F4F5] min-h-screen py-10 font-sans">
    <div class="max-w-[1100px] mx-auto px-4 md:px-6">
      
      <div class="mb-8 flex items-center gap-4">
        <button @click="$router.push('/cart')" class="text-gray-500 hover:text-black">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
        </button>
        <h1 class="text-2xl font-black text-gray-900 tracking-tight">Pengiriman & Pembayaran</h1>
      </div>

      <div class="flex flex-col lg:flex-row gap-8 items-start">
        
        <div class="flex-1 min-w-0 space-y-6">
          
          <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <h2 class="font-bold text-gray-900">Alamat Pengiriman</h2>
              <NuxtLink to="/dashboard/address" class="text-sm font-bold text-[#03AC0E] hover:text-[#028c0b] transition-colors">
                Pilih Alamat Lain
              </NuxtLink>
            </div>
            
            <div class="p-6">
              <div v-if="isLoadingAddress" class="h-24 bg-gray-100 animate-pulse rounded-lg"></div>
              
              <div v-else-if="!defaultAddress" class="text-center py-6">
                <p class="text-gray-500 mb-4">Anda belum memiliki alamat pengiriman.</p>
                <NuxtLink to="/dashboard/address" class="px-6 py-2 bg-[#03AC0E] text-white font-bold rounded-lg shadow-sm">
                  Tambah Alamat
                </NuxtLink>
              </div>

              <div v-else class="flex gap-4">
                <UIcon name="i-heroicons-map-pin" class="w-6 h-6 text-[#03AC0E] mt-0.5 shrink-0" />
                <div>
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-bold text-gray-900">Rumah / Utama</span>
                    <span class="px-2 py-0.5 bg-green-100 text-[#03AC0E] text-[10px] font-bold rounded-sm">Utama</span>
                  </div>
                  <p class="text-gray-800 font-semibold text-sm mb-1">{{ defaultAddress.label }}</p>
                  <p class="text-gray-600 text-sm leading-relaxed">{{ defaultAddress.full_address }}</p>
                  <p class="text-gray-500 text-sm mt-1">Kode Pos: <span class="font-medium text-gray-800">{{ defaultAddress.zip_code }}</span></p>
                </div>
              </div>
            </div>
          </section>

          <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h2 class="font-bold text-gray-900">Pesanan Anda</h2>
            </div>
            <div class="p-6 space-y-5">
              <div v-for="item in checkoutStore.items" :key="item.stock_uuid" class="flex gap-4">
                <div class="w-20 h-20 shrink-0 bg-gray-50 rounded-lg border border-gray-100 overflow-hidden p-1">
                  <NuxtImg :src="item.image || 'https://via.placeholder.com/100'" class="w-full h-full object-contain bg-white" />
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-800 text-sm leading-snug">{{ item.title }}</h3>
                  <div class="flex items-center gap-2 mt-1">
                    <p class="text-xs text-gray-500 uppercase tracking-wider">{{ item.brand || 'NO BRAND' }}</p>
                    <span v-if="item.weight" class="text-[10px] text-gray-400 bg-gray-100 border border-gray-200 px-1.5 py-0.5 rounded font-medium">{{ formatWeight(item.weight) }}</span>
                  </div>
                  <p class="font-bold text-gray-900 mt-2">{{ formatRupiah(item.price) }} <span class="text-gray-500 font-normal text-xs ml-1">x {{ item.quantity }}</span></p>
                </div>
                <div class="text-right">
                  <p class="font-black text-gray-900">{{ formatRupiah(item.price * item.quantity) }}</p>
                </div>
              </div>
            </div>
          </section>

          <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h2 class="font-bold text-gray-900">Pilih Pengiriman</h2>
            </div>
            
            <div class="p-6">
              <div v-if="!defaultAddress" class="text-sm text-red-500 font-semibold bg-red-50 p-4 rounded-lg">
                Isi alamat terlebih dahulu untuk melihat opsi pengiriman.
              </div>
              
              <div v-else-if="isLoadingShipping" class="flex flex-col gap-3">
                <div v-for="i in 3" :key="i" class="h-16 bg-gray-100 animate-pulse rounded-xl border border-gray-200"></div>
              </div>

              <div v-else-if="shippingOptions.length === 0" class="text-sm text-orange-600 font-semibold bg-orange-50 p-4 rounded-lg border border-orange-100">
                Tidak ada layanan pengiriman yang tersedia untuk alamat ini.
              </div>

              <div v-else class="grid grid-cols-1 gap-3">
                <label 
                  v-for="(option, index) in shippingOptions" 
                  :key="index"
                  class="flex items-start gap-4 p-4 border rounded-xl cursor-pointer transition-all"
                  :class="selectedShipping?.service === option.service && selectedShipping?.courier === option.courier ? 'border-[#03AC0E] bg-green-50/20 shadow-[0_0_0_1px_#03AC0E]' : 'border-gray-200 hover:border-green-300'"
                >
                  <div class="flex items-center h-5 mt-0.5">
                    <input 
                      type="radio" 
                      name="shipping" 
                      :value="option" 
                      v-model="selectedShipping" 
                      class="w-4 h-4 text-[#03AC0E] border-gray-300 focus:ring-[#03AC0E]"
                    >
                  </div>
                  <div class="flex-1">
                    <div class="flex justify-between items-start">
                      <div>
                        <p class="font-bold text-gray-900">{{ option.courier }} - <span class="text-[#03AC0E]">{{ option.service }}</span></p>
                        <p class="text-xs text-gray-500 mt-1">Estimasi tiba: <span class="font-semibold text-gray-700">{{ option.etd || 'Mengikuti jadwal kurir' }}</span></p>
                      </div>
                      <span class="font-black text-gray-900">{{ formatRupiah(option.price) }}</span>
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </section>

        </div>

        <div class="w-full lg:w-[380px] shrink-0">
          <div class="sticky top-24 bg-white rounded-2xl p-6 shadow-md border border-gray-200">
            <h3 class="font-bold text-gray-900 mb-6 pb-4 border-b border-gray-100">
              Ringkasan Belanja
            </h3>
            
            <div class="space-y-4 text-sm text-gray-600 mb-6">
              <div class="flex justify-between">
                <span>Total Harga ({{ checkoutStore.totalQuantity }} barang)</span>
                <span class="font-semibold text-gray-900">{{ formatRupiah(checkoutStore.subtotal) }}</span>
              </div>
              
              <div class="flex justify-between">
                <span>Total Berat</span>
                <span class="font-semibold text-gray-900">{{ formatWeight(checkoutStore.totalWeight) }}</span>
              </div>

              <div v-if="checkoutStore.discountPromo > 0" class="flex justify-between text-[#03AC0E]">
                <span>Total Diskon Barang</span>
                <span class="font-bold">- {{ formatRupiah(checkoutStore.discountPromo) }}</span>
              </div>
              
              <div class="flex justify-between">
                <span>Total Ongkos Kirim</span>
                <span class="font-semibold text-gray-900">{{ formatRupiah(shippingCost) }}</span>
              </div>
            </div>

            <div class="pt-4 border-t border-gray-200 mb-6 flex justify-between items-end">
              <span class="font-bold text-gray-900 text-base">Total Tagihan</span>
              <span class="text-xl font-black text-red-600 leading-none">{{ formatRupiah(finalGrandTotal) }}</span>
            </div>

            <button
              @click="handleCheckout"
              :disabled="isCheckingOut || !selectedShipping || !defaultAddress"
              class="w-full bg-[#03AC0E] text-white font-bold py-3.5 rounded-xl text-sm transition-all hover:bg-[#028c0b] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <svg v-if="isCheckingOut" class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span v-else>Buat Pesanan & Bayar</span>
            </button>

            <p class="text-[10px] text-gray-400 mt-4 text-center">
              Dengan membuat pesanan, Anda menyetujui Syarat & Ketentuan yang berlaku.
            </p>
          </div>
        </div>

      </div>
    </div>
  </main>
</template>