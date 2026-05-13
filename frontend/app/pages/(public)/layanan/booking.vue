<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'

/**
 * /layanan/booking — Wizard booking jasa CCTV
 * Theme: Modern Marketplace (Green/White/Soft Gray)
 */

// ─── SEO ─────────────────────────────────────────────────────────
useSeoMeta({
  title: 'Pesan Instalasi CCTV | PasarCctv',
  description: 'Pesan layanan instalasi, maintenance, atau konsultasi CCTV profesional. Teknisi berpengalaman, bergaransi.',
  robots: 'noindex, nofollow',
  ogTitle: 'Pesan Instalasi CCTV | PasarCctv',
  ogDescription: 'Teknisi berpengalaman, bergaransi. Pesan sekarang.',
  viewport: 'width=device-width, initial-scale=1, viewport-fit=cover',
})

const router = useRouter()
const route  = useRoute()

// ─── Auth ────────────────────────────────────────────────────────
const getToken = () => useCookie('token').value

// ─── Fetch Config & Packages dari backend ─────────────────────────
const [
  { data: configData, pending: configLoading, error: configError, refresh: refreshConfig },
  { data: packagesData, pending: packagesLoading }
] = await Promise.all([
  useFetch('/api/proxy/services/config', {
    key: 'service-config',
    lazy: false,
    getCachedData: (key, nuxtApp) => nuxtApp.payload.data[key] ?? nuxtApp.static.data[key],
  }),
  useFetch('/api/proxy/services/packages', {
    key: 'service-packages',
    lazy: true,
    default: () => []
  })
])

const config = computed(() => configData.value as any)
const packagesList = computed(() => (packagesData.value || []) as any[])

// ─── Wizard state ─────────────────────────────────────────────────
const currentStep = ref(1)
const TOTAL_STEPS = 3

const steps = [
  { num: 1, label: 'Konfigurasi' },
  { num: 2, label: 'Jadwal & Lokasi' },
  { num: 3, label: 'Kontak' },
]

const isSubmitting = ref(false)
const submitError  = ref('')

// Session ID — generate sekali, persist selama wizard
const sessionId = useState('booking_session_id', () =>
  Array.from(crypto.getRandomValues(new Uint8Array(16)))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
)

// ─── Form state ────────────────────────────────────────────────────
const form = reactive({
  // Step 1
  category:     '' as string,
  camera_count: 4,
  brand:        '' as string,
  addons:       [] as string[],
  package_uuid: null as string | null,

  // Step 2
  scheduled_date: '' as string,
  time_slot:      '' as string,
  address:        '',
  district:       '',
  city:           '',
  distance_km:    0,
  latitude:       null as number | null,
  longitude:      null as number | null,

  // Step 3
  contact_name:  '',
  contact_phone: '',
  contact_notes: '',
})

// ─── Handlers untuk Paket vs Kustom ───────────────────────────────
const selectedPackageInfo = computed(() => {
  if (!form.package_uuid) return null
  return packagesList.value.find(p => p.uuid === form.package_uuid) || null
})

const selectPackage = (pkg: any) => {
  form.package_uuid = pkg.uuid
  form.category     = pkg.category
  form.camera_count = pkg.camera_count
  form.brand        = pkg.default_brand
  form.addons       = [] // Reset addon saat pilih paket
}

const clearPackageSelection = () => {
  form.package_uuid = null
}

const setManualCategory = (val: string) => { form.category = val; clearPackageSelection() }
const setManualBrand    = (val: string) => { form.brand = val; clearPackageSelection() }
const setManualCamCount = (val: number) => { 
  form.camera_count = val; 
  isCustomCam.value = false; 
  clearPackageSelection() 
}

// ─── Init dari query params ────────────────────────────────────────
const initFromQuery = () => {
  const q = route.query

  if (q.category && typeof q.category === 'string') {
    const validCategories = ['installation', 'maintenance', 'consultation', 'troubleshoot']
    if (validCategories.includes(q.category)) form.category = q.category
  }

  if (q.city && typeof q.city === 'string') {
    form.city = decodeURIComponent(q.city)
  }

  if (q.package && typeof q.package === 'string') {
    form.package_uuid = q.package
    fetchPackageDetail(q.package)
  }

  if (q.step === 'estimate' && form.category) {
    nextTick(() => { currentStep.value = 2 })
  }
}

const fetchPackageDetail = async (uuid: string) => {
  try {
    const pkg = await $fetch<any>(`/api/proxy/services/packages/${uuid}`)
    if (pkg) {
      if (pkg.category)      form.category     = pkg.category
      if (pkg.camera_count)  form.camera_count = pkg.camera_count
      if (pkg.default_brand) form.brand        = pkg.default_brand
    }
  } catch (e) {
    console.warn('Gagal fetch paket detail:', e)
  }
}

// ─── Slot availability ─────────────────────────────────────────────
const slotsData    = ref<any>(null)
const loadingSlots = ref(false)

const fetchSlots = async (d: string) => {
  if (!d) return
  loadingSlots.value = true
  try {
    const data = await $fetch<any>(`/api/proxy/services/slots?target_date=${d}`)
    slotsData.value = data
  } catch { /* silent */ }
  finally { loadingSlots.value = false }
}

watch(() => form.scheduled_date, (d) => {
  if (d) {
    form.time_slot = ''
    fetchSlots(d)
  }
})

// ─── Geolocation ──────────────────────────────────────────────────
const geoLoading   = ref(false)
const geoError     = ref('')
const distanceData = ref<any>(null)

const detectLocation = () => {
  if (!navigator.geolocation) {
    geoError.value = 'Browser tidak mendukung geolocation'
    return
  }
  geoLoading.value = true
  geoError.value   = ''

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      form.latitude  = pos.coords.latitude
      form.longitude = pos.coords.longitude
      try {
        const resp = await $fetch<any>('/api/proxy/services/distance', {
          method: 'POST',
          body: {
            latitude:  form.latitude,
            longitude: form.longitude,
            address:   form.address || undefined,
          },
        })
        distanceData.value = resp
        form.distance_km   = resp.distance_km
        if (!resp.is_within_range) geoError.value = resp.message
      } catch {
        geoError.value = 'Gagal menghitung jarak. Masukkan manual.'
      } finally {
        geoLoading.value = false
      }
    },
    () => {
      geoLoading.value = false
      geoError.value   = 'Akses lokasi ditolak. Masukkan jarak manual.'
    },
    { timeout: 8000, enableHighAccuracy: true }
  )
}

// ─── Estimate real-time ───────────────────────────────────────────
const estimate        = ref<any>(null)
const estimateLoading = ref(false)
let   estimateTimer: ReturnType<typeof setTimeout>

const fetchEstimate = async () => {
  if (!form.category || form.camera_count < 1 || !form.brand) return
  clearTimeout(estimateTimer)
  estimateTimer = setTimeout(async () => {
    estimateLoading.value = true
    try {
      const body: Record<string, any> = {
        category:     form.category,
        camera_count: form.camera_count,
        brand:        form.brand,
        addons:       form.addons,
        distance_km:  form.distance_km,
      }
      if (form.package_uuid) body.package_uuid = form.package_uuid
      const data = await $fetch<any>('/api/proxy/services/estimate', { method: 'POST', body })
      estimate.value = data
    } catch { /* silent */ }
    finally { estimateLoading.value = false }
  }, 500)
}

watch(
  () => [form.category, form.camera_count, form.brand, form.addons.join(','), form.distance_km, form.package_uuid],
  fetchEstimate,
  { deep: true }
)

// ─── Draft Redis ──────────────────────────────────────────────────
const saveDraft = async (step: number, data: Record<string, any>) => {
  try {
    const token = getToken()
    await $fetch('/api/proxy/services/booking/draft', {
      method: 'POST',
      body: { session_id: sessionId.value, step, data },
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
  } catch (e) {
    console.warn('Draft save failed (non-fatal):', e)
  }
}

// ─── Calendar helpers ─────────────────────────────────────────────
const generateDates = () => {
  const dates = []
  const today = new Date()
  for (let i = 1; i <= 14; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    if (d.getDay() !== 0) {
      dates.push({
        value:    d.toISOString().split('T')[0],
        dayShort: d.toLocaleDateString('id-ID', { weekday: 'short' }),
        dayLong:  d.toLocaleDateString('id-ID', { weekday: 'long' }),
        num:      d.getDate(),
        month:    d.toLocaleDateString('id-ID', { month: 'short' }),
        year:     d.getFullYear(),
      })
    }
  }
  return dates
}

const availableDates = ref(generateDates())
const minDate = computed(() => {
  const t = new Date(); t.setDate(t.getDate() + 1)
  return t.toISOString().split('T')[0]
})

const addCustomDate = (e: Event) => {
  const v = (e.target as HTMLInputElement).value
  if (!v) return
  const d = new Date(v + 'T00:00:00')
  const obj = {
    value:    v,
    dayShort: d.toLocaleDateString('id-ID', { weekday: 'short' }),
    dayLong:  d.toLocaleDateString('id-ID', { weekday: 'long' }),
    num:      d.getDate(),
    month:    d.toLocaleDateString('id-ID', { month: 'short' }),
    year:     d.getFullYear(),
  }
  if (!availableDates.value.find(x => x.value === v))
    availableDates.value.unshift(obj)
  form.scheduled_date = v
  form.time_slot = ''
}

const selectedDateLabel = computed(() => {
  const d = availableDates.value.find(x => x.value === form.scheduled_date)
  return d ? `${d.dayLong}, ${d.num} ${d.month} ${d.year}` : ''
})

// ─── Time slot labels ─────────────────────────────────────────────
const SLOT_LABELS: Record<string, string> = {
  '08:00-11:00': 'Pagi (08:00–11:00)',
  '11:00-14:00': 'Siang (11:00–14:00)',
  '14:00-17:00': 'Sore (14:00–17:00)',
}

const DEFAULT_SLOTS = Object.keys(SLOT_LABELS).map(k => ({
  slot: k, label: SLOT_LABELS[k], available: true, remaining: 3,
}))

// ─── Validation per step ──────────────────────────────────────────
const step1Valid = computed(() =>
  !!form.category && form.camera_count >= 1 && !!form.brand
)
const step2Valid = computed(() =>
  !!form.scheduled_date &&
  !!form.time_slot &&
  form.address.length >= 10 &&
  !!form.city &&
  (distanceData.value?.is_within_range !== false)
)
const step3Valid = computed(() =>
  form.contact_name.length >= 2 && form.contact_phone.length >= 9
)

const canNext = computed(() => {
  if (currentStep.value === 1) return step1Valid.value
  if (currentStep.value === 2) return step2Valid.value
  if (currentStep.value === 3) return step3Valid.value
  return false
})

// ─── Navigation ───────────────────────────────────────────────────
const nextStep = async () => {
  if (!canNext.value || isSubmitting.value) return

  if (currentStep.value === 1) {
    await saveDraft(1, {
      category:     form.category,
      camera_count: form.camera_count,
      brand:        form.brand,
      addons:       form.addons,
      package_uuid: form.package_uuid,
    })
    currentStep.value = 2
  } else if (currentStep.value === 2) {
    await saveDraft(2, {
      scheduled_date: form.scheduled_date,
      time_slot:      form.time_slot,
      address:        form.address,
      district:       form.district,
      city:           form.city,
      distance_km:    form.distance_km,
      latitude:       form.latitude,
      longitude:      form.longitude,
    })
    currentStep.value = 3
  } else {
    await handleSubmit()
  }

  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const prevStep = () => {
  submitError.value = ''
  if (currentStep.value > 1) {
    currentStep.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    router.back()
  }
}

// ─── Submit → redirect ke /booking/status/[number] ────────────────
const handleSubmit = async () => {
  isSubmitting.value = true
  submitError.value  = ''

  const token = getToken()
  if (!token) {
    submitError.value = 'Sesi telah habis atau Anda belum login. Silakan login terlebih dahulu.'
    isSubmitting.value = false
    return
  }

  try {
    // 1. Simpan draft step 3
    await saveDraft(3, {
      contact_name:  form.contact_name,
      contact_phone: form.contact_phone,
      contact_notes: form.contact_notes,
    })

    // 2. Submit booking dari draft Redis
    const bookingResult = await $fetch<any>('/api/proxy/services/booking/submit', {
      method: 'POST',
      body:    { session_id: sessionId.value },
      headers: { Authorization: `Bearer ${token}` },
    })

    // Reset session ID untuk booking berikutnya
    sessionId.value = Array.from(crypto.getRandomValues(new Uint8Array(16)))
      .map(b => b.toString(16).padStart(2, '0')).join('')

    // 3. Buat transaksi Midtrans DP
    const paymentResult = await $fetch<any>('/api/proxy/services/payment/create', {
      method: 'POST',
      body:    { booking_uuid: bookingResult.uuid, payment_type: 'DP' },
      headers: { Authorization: `Bearer ${token}` },
    })

    // 4. Redirect ke Midtrans Snap URL atau fallback ke /booking/status/[number]
    if (paymentResult?.payment_url) {
      window.location.href = paymentResult.payment_url
    } else {
      await router.push(`/booking/status/${bookingResult.booking_number}`)
    }

  } catch (e: any) {
    submitError.value =
      e?.data?.detail ||
      e?.statusMessage ||
      'Gagal membuat pesanan. Silakan coba lagi.'
    isSubmitting.value = false
  }
}

// ─── Helpers ─────────────────────────────────────────────────────
const fmt = (n: number) =>
  new Intl.NumberFormat('id-ID', {
    style: 'currency', currency: 'IDR', minimumFractionDigits: 0,
  }).format(n).replace('Rp', 'Rp ')

const toggleAddon = (key: string) => {
  clearPackageSelection() // Opsional: Hapus paket jika fitur diubah manual
  const idx = form.addons.indexOf(key)
  if (idx === -1) form.addons.push(key)
  else form.addons.splice(idx, 1)
}
const hasAddon = (key: string) => form.addons.includes(key)

const CATEGORY_ICONS: Record<string, string> = {
  installation: 'i-heroicons-home',
  maintenance:  'i-heroicons-wrench-screwdriver',
  consultation: 'i-heroicons-chat-bubble-left-ellipsis',
  troubleshoot: 'i-heroicons-magnifying-glass',
}

const CAM_PRESETS = [2, 4, 6, 8, 16]
const isCustomCam = ref(false)

// ─── Lifecycle ────────────────────────────────────────────────────
onMounted(() => {
  initFromQuery()
  if (form.category && form.brand) fetchEstimate()
})
</script>

<template>
  <div class="min-h-screen bg-[#F4F5F7] font-sans pb-32 lg:pb-12 selection:bg-green-600 selection:text-white">

    <!-- ── Loading config ──────────────────────────────────────── -->
    <div v-if="configLoading" class="flex items-center justify-center min-h-screen">
      <div class="flex flex-col items-center gap-4">
        <div class="w-8 h-8 rounded-full border-4 border-green-600 border-t-transparent animate-spin" />
        <p class="text-sm font-semibold text-gray-500">Memuat layanan...</p>
      </div>
    </div>

    <!-- ── Error config ────────────────────────────────────────── -->
    <div v-else-if="configError" class="flex items-center justify-center min-h-screen px-4">
      <div class="text-center bg-white p-8 rounded-2xl shadow-sm border border-gray-100 max-w-sm w-full">
        <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-500" aria-hidden="true" />
        </div>
        <h2 class="text-lg font-bold text-gray-900 mb-2">Gagal Memuat Data</h2>
        <p class="text-sm text-gray-500 mb-6">Tidak dapat terhubung ke server. Periksa koneksi internet Anda.</p>
        <button
          class="w-full bg-green-600 text-white px-6 py-3 rounded-xl text-sm font-semibold hover:bg-green-700 transition-colors shadow-sm"
          @click="refreshConfig()"
        >
          Coba Lagi
        </button>
      </div>
    </div>

    <template v-else-if="config">

      <!-- ── Desktop header ─────────────────────────────────────── -->
      <header class="hidden lg:block bg-white border-b border-gray-100 sticky top-0 z-40 shadow-sm">
        <div class="max-w-7xl mx-auto px-6 h-[72px] flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button
              class="p-2.5 rounded-full bg-gray-50 text-gray-500 hover:bg-gray-100 hover:text-gray-900 transition-colors"
              aria-label="Kembali"
              @click="prevStep"
            >
              <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" aria-hidden="true" />
            </button>
            <div>
              <h1 class="text-xl font-bold text-gray-900 leading-tight">Pesan Layanan CCTV</h1>
              <p class="text-xs font-medium text-gray-500">Cepat, Mudah, dan Transparan</p>
            </div>
          </div>

          <!-- Step indicator desktop -->
          <nav aria-label="Langkah booking" class="flex items-center gap-2">
            <div v-for="(step, i) in steps" :key="step.num" class="flex items-center">
              <div class="flex items-center gap-2 px-3 py-1.5 rounded-full transition-all duration-300"
                   :class="currentStep >= step.num ? 'bg-green-50 text-green-700' : 'bg-transparent text-gray-400'">
                <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                     :class="currentStep >= step.num ? 'bg-green-600 text-white shadow-sm' : 'bg-gray-100 text-gray-500'">
                  <UIcon v-if="currentStep > step.num" name="i-heroicons-check" class="w-3.5 h-3.5" aria-hidden="true" />
                  <span v-else>{{ step.num }}</span>
                </div>
                <span class="text-sm font-semibold">{{ step.label }}</span>
              </div>
              <div v-if="i < steps.length - 1" class="w-8 h-px mx-2 transition-colors duration-300" 
                   :class="currentStep > step.num ? 'bg-green-500' : 'bg-gray-200'" aria-hidden="true" />
            </div>
          </nav>
        </div>
      </header>

      <!-- ── Mobile header ──────────────────────────────────────── -->
      <header class="lg:hidden sticky top-0 z-40 bg-white border-b border-gray-100 shadow-sm">
        <div class="px-4 h-14 flex items-center gap-3">
          <button class="p-2 -ml-2 rounded-full text-gray-500 hover:bg-gray-50 transition-colors" aria-label="Kembali" @click="prevStep">
            <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" aria-hidden="true" />
          </button>
          <div>
            <h1 class="text-sm font-bold text-gray-900">{{ steps[currentStep - 1].label }}</h1>
            <p class="text-xs font-medium text-gray-500">Langkah {{ currentStep }} dari {{ TOTAL_STEPS }}</p>
          </div>
        </div>
        <!-- Progress bar hijau -->
        <div class="h-1 w-full bg-gray-100" role="progressbar" :aria-valuenow="currentStep" :aria-valuemax="TOTAL_STEPS">
          <div class="h-full bg-green-600 transition-all duration-500 ease-out" :style="{ width: `${(currentStep / TOTAL_STEPS) * 100}%` }" />
        </div>
      </header>

      <!-- ── Main content ───────────────────────────────────────── -->
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8 grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">

        <!-- Form area -->
        <div class="lg:col-span-7 xl:col-span-8">

          <!-- ════ STEP 1: Konfigurasi ════ -->
          <transition name="step-fade" mode="out-in">
            <div v-if="currentStep === 1" key="step1" class="space-y-8">

              <!-- Title Mobile Only -->
              <div class="lg:hidden">
                <h2 class="text-xl font-bold text-gray-900">Spesifikasi CCTV</h2>
                <p class="text-sm text-gray-500 mt-1">Pilih paket rekomendasi atau atur sesuai kebutuhan Anda.</p>
              </div>

              <!-- Packages Section (Jika ada data) -->
              <section v-if="packagesList.length > 0" aria-labelledby="packages-heading">
                <div class="flex items-center justify-between mb-4">
                  <h3 id="packages-heading" class="text-sm font-bold text-gray-900">Rekomendasi Paket (Terima Beres)</h3>
                  <span class="text-xs font-semibold text-green-600 bg-green-50 px-2.5 py-1 rounded-full">Lebih Hemat</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div v-for="pkg in packagesList" :key="pkg.uuid"
                       @click="selectPackage(pkg)"
                       :class="form.package_uuid === pkg.uuid 
                          ? 'border-green-600 ring-1 ring-green-600 bg-green-50/20' 
                          : 'border-gray-200 bg-white hover:border-green-400 hover:shadow-md'"
                       class="border rounded-2xl p-4 cursor-pointer transition-all duration-200 flex flex-col h-full shadow-sm">
                    
                    <div class="relative w-full h-32 mb-4 rounded-xl overflow-hidden bg-gray-100">
                      <img v-if="pkg.thumbnail_url" :src="pkg.thumbnail_url" :alt="pkg.name" class="w-full h-full object-cover" loading="lazy" />
                      <div v-else class="w-full h-full flex items-center justify-center text-gray-400"><UIcon name="i-heroicons-photo" class="w-8 h-8" /></div>
                    </div>
                    
                    <h4 class="font-bold text-gray-900 leading-snug mb-1.5 line-clamp-2">{{ pkg.name }}</h4>
                    <p class="text-xs text-gray-500 mb-3 line-clamp-2">{{ pkg.description }}</p>
                    
                    <ul class="space-y-1.5 mb-4">
                      <li v-for="hl in pkg.highlights.slice(0, 3)" :key="hl" class="flex items-start gap-1.5 text-xs text-gray-600 font-medium">
                        <UIcon name="i-heroicons-check-circle-20-solid" class="w-4 h-4 text-green-500 flex-shrink-0" aria-hidden="true" />
                        <span class="leading-tight">{{ hl }}</span>
                      </li>
                    </ul>

                    <div class="mt-auto pt-4 flex items-end justify-between border-t border-gray-100">
                      <div>
                        <p class="text-[10px] font-medium text-gray-500 mb-0.5">Estimasi Total</p>
                        <p class="text-base font-bold text-green-600">{{ fmt(pkg.total_estimated) }}</p>
                      </div>
                      <div :class="form.package_uuid === pkg.uuid ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600'" 
                           class="px-3 py-1.5 rounded-lg text-xs font-bold transition-colors">
                        {{ form.package_uuid === pkg.uuid ? 'Terpilih ✓' : 'Pilih Paket' }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-4 my-8">
                  <div class="flex-1 h-px bg-gray-200"></div>
                  <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">ATAU RAKIT SENDIRI</span>
                  <div class="flex-1 h-px bg-gray-200"></div>
                </div>
              </section>

              <!-- 1. Kategori (Manual) -->
              <section aria-labelledby="category-heading" class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                <h3 id="category-heading" class="text-sm font-bold text-gray-900 mb-4">Jenis Layanan</h3>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <button v-for="cat in config.categories" :key="cat.id" type="button"
                    @click="setManualCategory(cat.id)"
                    class="flex flex-col items-center text-center p-4 rounded-xl border transition-all duration-200"
                    :class="form.category === cat.id && !form.package_uuid
                      ? 'border-green-600 bg-green-50 text-green-700 ring-1 ring-green-600'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-green-300 hover:bg-gray-50'">
                    <UIcon :name="CATEGORY_ICONS[cat.id] || 'i-heroicons-cog-6-tooth'" class="w-6 h-6 mb-2" :class="form.category === cat.id && !form.package_uuid ? 'text-green-600' : 'text-gray-400'" aria-hidden="true" />
                    <span class="text-xs font-bold leading-tight">{{ cat.label }}</span>
                  </button>
                </div>
              </section>

              <!-- 2. Jumlah kamera (Manual) -->
              <section aria-labelledby="cam-heading" class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                <h3 id="cam-heading" class="text-sm font-bold text-gray-900 mb-4">Jumlah Titik Kamera</h3>
                <div class="flex flex-wrap gap-3">
                  <button v-for="n in CAM_PRESETS" :key="n" type="button"
                    class="h-11 px-5 rounded-xl border text-sm font-bold transition-all duration-200"
                    :class="form.camera_count === n && !isCustomCam && !form.package_uuid
                      ? 'border-green-600 bg-green-50 text-green-700 ring-1 ring-green-600'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-green-300 hover:bg-gray-50'"
                    @click="setManualCamCount(n)">
                    {{ n }} Titik
                  </button>
                  
                  <div class="h-11 rounded-xl border overflow-hidden transition-all flex items-center"
                    :class="isCustomCam && !form.package_uuid ? 'border-green-600 ring-1 ring-green-600 bg-white' : 'border-gray-200 bg-white hover:border-green-300'">
                    <button v-if="!isCustomCam" type="button" class="px-5 h-full text-sm font-bold text-gray-700" @click="isCustomCam = true; clearPackageSelection()">
                      Kustom
                    </button>
                    <div v-else class="flex items-center px-3 gap-2 h-full">
                      <span class="text-xs font-semibold text-gray-500">Jumlah:</span>
                      <input v-model.number="form.camera_count" type="number" min="1" max="200" @input="clearPackageSelection()"
                        class="w-16 h-8 text-center text-sm font-bold text-green-700 border-none bg-green-50 rounded-lg focus:ring-0" />
                    </div>
                  </div>
                </div>
              </section>

              <!-- 3. Brand (Manual) -->
              <section aria-labelledby="brand-heading" class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                <h3 id="brand-heading" class="text-sm font-bold text-gray-900 mb-4">Pilih Brand Perangkat</h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button v-for="brand in config.brands" :key="brand.key" type="button"
                    @click="setManualBrand(brand.key)"
                    class="flex items-center justify-between p-4 rounded-xl border transition-all duration-200 text-left"
                    :class="form.brand === brand.key && !form.package_uuid
                      ? 'border-green-600 bg-green-50 ring-1 ring-green-600'
                      : 'border-gray-200 bg-white hover:border-green-300 hover:bg-gray-50'">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-full flex items-center justify-center transition-colors"
                        :class="form.brand === brand.key && !form.package_uuid ? 'bg-green-600 text-white shadow-sm shadow-green-500/30' : 'bg-gray-100 text-gray-500'">
                        <UIcon name="i-heroicons-shield-check" class="w-5 h-5" aria-hidden="true" />
                      </div>
                      <div>
                        <h4 class="text-sm font-bold text-gray-900 uppercase">{{ brand.label }}</h4>
                        <p class="text-xs font-medium text-gray-500">Standard Quality</p>
                      </div>
                    </div>
                    <UIcon v-if="form.brand === brand.key && !form.package_uuid" name="i-heroicons-check-circle-20-solid" class="w-6 h-6 text-green-600" aria-hidden="true" />
                  </button>
                </div>
              </section>

              <!-- 4. Addons (Opsional) -->
              <section v-if="config.addons?.length" aria-labelledby="addon-heading" class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                <h3 id="addon-heading" class="text-sm font-bold text-gray-900 mb-4">Fitur Tambahan <span class="text-xs font-medium text-gray-500">(Opsional)</span></h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button v-for="addon in config.addons" :key="addon.key" type="button"
                    @click="toggleAddon(addon.key)"
                    class="text-left p-4 rounded-xl border transition-all duration-200"
                    :class="hasAddon(addon.key)
                      ? 'border-green-600 bg-green-50/50 ring-1 ring-green-600'
                      : 'border-gray-200 bg-white hover:border-green-300'">
                    <div class="flex justify-between items-start mb-1.5">
                      <span class="text-sm font-bold text-gray-900">{{ addon.label }}</span>
                      <UIcon v-if="hasAddon(addon.key)" name="i-heroicons-check-circle-20-solid" class="w-5 h-5 text-green-600 flex-shrink-0" />
                    </div>
                    <p v-if="addon.description" class="text-xs text-gray-500 leading-relaxed mb-3 line-clamp-2">{{ addon.description }}</p>
                    <p class="text-xs font-bold text-green-700">
                      +{{ fmt(addon.price) }} <span class="text-[10px] font-medium text-gray-500 normal-case">{{ addon.type === 'per_cam' ? '/ Kamera' : 'Flat' }}</span>
                    </p>
                  </button>
                </div>
              </section>
            </div>
          </transition>

          <!-- ════ STEP 2: Jadwal & Lokasi ════ -->
          <transition name="step-fade" mode="out-in">
            <div v-if="currentStep === 2" key="step2" class="space-y-8">
              
              <div class="lg:hidden">
                <h2 class="text-xl font-bold text-gray-900">Jadwal & Lokasi</h2>
                <p class="text-sm text-gray-500 mt-1">Pilih waktu dan tentukan lokasi pemasangan.</p>
              </div>

              <!-- Pilih Tanggal -->
              <section aria-labelledby="date-heading" class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                <h3 id="date-heading" class="text-sm font-bold text-gray-900 mb-4">Pilih Tanggal Kedatangan</h3>
                <div class="flex flex-nowrap overflow-x-auto gap-3 pb-2 hide-scrollbar snap-x">
                  <div class="snap-center flex-shrink-0 relative w-20">
                    <div class="w-full h-[88px] border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center gap-1 hover:border-green-500 hover:bg-green-50 transition-all cursor-pointer">
                      <UIcon name="i-heroicons-calendar-days" class="w-6 h-6 text-gray-400" />
                      <span class="text-[10px] font-semibold text-gray-500 text-center leading-tight">Pilih<br>Lainnya</span>
                    </div>
                    <input type="date" :min="minDate" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" @change="addCustomDate" />
                  </div>

                  <button v-for="d in availableDates" :key="d.value" type="button"
                    class="snap-center flex-shrink-0 w-20 h-[88px] rounded-xl border flex flex-col items-center justify-center transition-all duration-200"
                    :class="form.scheduled_date === d.value
                      ? 'border-green-600 bg-green-600 text-white shadow-md shadow-green-600/20 ring-1 ring-green-600'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-green-300'"
                    @click="form.scheduled_date = d.value">
                    <span class="text-[11px] font-medium" :class="form.scheduled_date === d.value ? 'text-green-100' : 'text-gray-500'">{{ d.dayShort }}</span>
                    <span class="text-xl font-bold leading-none my-1">{{ d.num }}</span>
                    <span class="text-[10px] font-medium" :class="form.scheduled_date === d.value ? 'text-green-100' : 'text-gray-500'">{{ d.month }}</span>
                  </button>
                </div>
              </section>

              <!-- Pilih Jam -->
              <section v-if="form.scheduled_date" aria-labelledby="slot-heading" class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                <div class="flex items-center justify-between mb-4">
                  <h3 id="slot-heading" class="text-sm font-bold text-gray-900">Pilih Jam Kedatangan</h3>
                  <span class="text-xs font-semibold text-gray-500">{{ selectedDateLabel }}</span>
                </div>
                
                <div v-if="loadingSlots" class="flex gap-3">
                  <div v-for="i in 3" :key="i" class="h-16 flex-1 bg-gray-50 rounded-xl border border-gray-100 animate-pulse" />
                </div>
                
                <div v-else class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <button v-for="slot in slotsData?.slots || DEFAULT_SLOTS" :key="slot.slot" type="button"
                    :disabled="!slot.available"
                    class="p-3 rounded-xl border transition-all duration-200 text-left relative overflow-hidden"
                    :class="[
                      form.time_slot === slot.slot
                        ? 'border-green-600 bg-green-50 ring-1 ring-green-600'
                        : slot.available
                          ? 'border-gray-200 bg-white hover:border-green-300'
                          : 'border-gray-100 bg-gray-50 cursor-not-allowed opacity-60'
                    ]"
                    @click="slot.available && (form.time_slot = slot.slot)">
                    <p class="text-sm font-bold mb-1" :class="form.time_slot === slot.slot ? 'text-green-800' : 'text-gray-900'">
                      {{ SLOT_LABELS[slot.slot] || slot.slot }}
                    </p>
                    <p class="text-xs font-medium" :class="slot.available ? (form.time_slot === slot.slot ? 'text-green-600' : 'text-green-600') : 'text-red-500'">
                      {{ slot.available ? `Tersedia ${slot.remaining} Slot` : 'Penuh' }}
                    </p>
                    <UIcon v-if="form.time_slot === slot.slot" name="i-heroicons-check-circle-20-solid" class="absolute right-3 top-1/2 -translate-y-1/2 w-6 h-6 text-green-600" />
                  </button>
                </div>
              </section>

              <!-- Lokasi -->
              <section aria-labelledby="loc-heading" class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                <h3 id="loc-heading" class="text-sm font-bold text-gray-900 mb-4">Lokasi Pemasangan</h3>
                <div class="space-y-4">

                  <!-- Detect GPS -->
                  <button type="button" :disabled="geoLoading"
                    class="w-full flex items-center justify-center gap-2 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm font-semibold transition-all"
                    :class="geoLoading ? 'text-gray-400 cursor-not-allowed' : form.latitude ? 'bg-green-50 border-green-200 text-green-700' : 'text-gray-700 hover:bg-gray-100'"
                    @click="detectLocation">
                    <UIcon :name="geoLoading ? 'i-heroicons-arrow-path' : 'i-heroicons-map-pin'" :class="geoLoading ? 'animate-spin' : ''" class="w-5 h-5" />
                    <span>
                      {{ geoLoading ? 'Mencari lokasi...' : form.latitude ? `Lokasi Akurat Ditemukan (${form.distance_km.toFixed(1)} km)` : 'Gunakan Lokasi Saat Ini (GPS)' }}
                    </span>
                  </button>

                  <!-- Geo error -->
                  <div v-if="geoError" class="flex items-start gap-2 p-3 bg-red-50 border border-red-100 rounded-xl">
                    <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5 text-red-500 flex-shrink-0" />
                    <p class="text-xs font-medium text-red-700 mt-0.5">{{ geoError }}</p>
                  </div>

                  <!-- Distance info (Success) -->
                  <div v-if="distanceData?.is_within_range" class="flex items-center justify-between p-3 bg-green-50 border border-green-100 rounded-xl">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center"><UIcon name="i-heroicons-truck" class="w-4 h-4 text-green-700" /></div>
                      <div>
                        <p class="text-xs font-bold text-green-900">Masuk Area Layanan</p>
                        <p class="text-[11px] font-medium text-green-700">Jarak: {{ form.distance_km.toFixed(1) }} km</p>
                      </div>
                    </div>
                    <p class="text-sm font-bold text-green-700">{{ fmt(distanceData.transport_fee) }}</p>
                  </div>

                  <div class="h-px bg-gray-100 my-4 w-full"></div>

                  <!-- Detail Alamat -->
                  <div class="space-y-4">
                    <div>
                      <label class="block text-xs font-bold text-gray-700 mb-1.5">Alamat Lengkap</label>
                      <textarea v-model="form.address" rows="3" placeholder="Nama jalan, RT/RW, nomor rumah, patokan..."
                        class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all resize-none shadow-sm" />
                    </div>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label class="block text-xs font-bold text-gray-700 mb-1.5">Kota / Kabupaten</label>
                        <input v-model="form.city" type="text" placeholder="Contoh: Bandung"
                          class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all shadow-sm" />
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-700 mb-1.5">Kecamatan <span class="text-gray-400 font-normal">(Opsional)</span></label>
                        <input v-model="form.district" type="text" placeholder="Contoh: Cimahi Tengah"
                          class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all shadow-sm" />
                      </div>
                    </div>

                    <!-- Manual distance jika GPS gagal -->
                    <div v-if="!form.latitude" class="pt-2">
                      <label class="block text-xs font-bold text-gray-700 mb-1.5">Estimasi Jarak Manual (Dari Cimahi)</label>
                      <div class="relative">
                        <input v-model.number="form.distance_km" type="number" min="0" :max="config.max_distance_km" step="0.5"
                          class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all shadow-sm pr-12" />
                        <span class="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-gray-400">km</span>
                      </div>
                      <p class="text-[11px] text-gray-500 mt-1.5 font-medium">Isi manual jika deteksi GPS gagal. Maksimal {{ config.max_distance_km }} km.</p>
                    </div>
                  </div>

                </div>
              </section>
            </div>
          </transition>

          <!-- ════ STEP 3: Kontak ════ -->
          <transition name="step-fade" mode="out-in">
            <div v-if="currentStep === 3" key="step3" class="space-y-8">

              <div class="lg:hidden">
                <h2 class="text-xl font-bold text-gray-900">Informasi Kontak</h2>
                <p class="text-sm text-gray-500 mt-1">Teknisi kami akan menghubungi nomor ini saat tiba di lokasi.</p>
              </div>

              <!-- Form Kontak -->
              <div class="bg-white border border-gray-100 rounded-2xl p-5 sm:p-6 space-y-5 shadow-sm">
                <div>
                  <label for="contact-name" class="block text-xs font-bold text-gray-700 mb-1.5">Nama PIC / Penanggung Jawab</label>
                  <div class="relative shadow-sm rounded-xl">
                    <UIcon name="i-heroicons-user" class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input id="contact-name" v-model="form.contact_name" type="text" placeholder="Masukkan nama lengkap" autocomplete="name"
                      class="w-full bg-white border border-gray-200 rounded-xl pl-11 pr-4 py-3 text-sm font-medium text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all" />
                  </div>
                </div>

                <div>
                  <label for="contact-phone" class="block text-xs font-bold text-gray-700 mb-1.5">Nomor WhatsApp Aktif</label>
                  <div class="relative shadow-sm rounded-xl">
                    <UIcon name="i-heroicons-phone" class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input id="contact-phone" v-model="form.contact_phone" type="tel" placeholder="Contoh: 08123456789" autocomplete="tel"
                      class="w-full bg-white border border-gray-200 rounded-xl pl-11 pr-4 py-3 text-sm font-medium text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all" />
                  </div>
                </div>

                <div>
                  <label for="contact-notes" class="block text-xs font-bold text-gray-700 mb-1.5">Catatan Khusus <span class="text-gray-400 font-normal">(Opsional)</span></label>
                  <textarea id="contact-notes" v-model="form.contact_notes" rows="3" placeholder="Titip KTP ke satpam depan, rumah cat putih..."
                    class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all resize-none shadow-sm" />
                </div>
              </div>

              <!-- Submit Error -->
              <div v-if="submitError" role="alert" class="p-4 bg-red-50 border border-red-100 rounded-xl flex items-start gap-3 shadow-sm">
                <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p class="text-sm font-medium text-red-800">{{ submitError }}</p>
              </div>
            </div>
          </transition>
        </div>

        <!-- ── Sidebar pricing (Desktop) ── -->
        <aside class="hidden lg:flex lg:col-span-5 xl:col-span-4 flex-col" aria-label="Ringkasan Pesanan">
          <div class="sticky top-28 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">

            <!-- Detail Header -->
            <div class="px-6 pt-6 pb-4 border-b border-dashed border-gray-200 relative">
              <h3 class="text-lg font-bold text-gray-900 leading-tight mb-2">
                {{ selectedPackageInfo ? selectedPackageInfo.name : 'Custom CCTV Setup' }}
              </h3>
              
              <div v-if="form.camera_count && form.brand" class="flex flex-wrap gap-2 mt-3">
                <span class="bg-gray-100 text-gray-700 px-2.5 py-1 rounded-md text-xs font-semibold">
                  {{ form.category }}
                </span>
                <span class="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-md text-xs font-semibold">
                  {{ form.camera_count }} Titik
                </span>
                <span class="bg-gray-100 text-gray-700 px-2.5 py-1 rounded-md text-xs font-semibold capitalize">
                  {{ form.brand }}
                </span>
              </div>
              <p v-else class="text-sm text-gray-400 italic">Spesifikasi belum lengkap</p>
            </div>

            <!-- Info Jadwal & Lokasi -->
            <div class="px-6 py-4 border-b border-gray-100 space-y-4">
              <div class="flex items-start gap-3">
                <UIcon name="i-heroicons-calendar-days" class="w-5 h-5 text-gray-400 flex-shrink-0" />
                <div>
                  <p class="text-xs font-semibold text-gray-500 mb-0.5">Jadwal Kedatangan</p>
                  <p class="text-sm font-bold text-gray-900">
                    <template v-if="selectedDateLabel && form.time_slot">
                      {{ selectedDateLabel }} <br /> <span class="text-green-600">{{ SLOT_LABELS[form.time_slot] }}</span>
                    </template>
                    <span v-else class="text-gray-400 font-medium italic text-xs">Belum dipilih</span>
                  </p>
                </div>
              </div>
              
              <div class="flex items-start gap-3">
                <UIcon name="i-heroicons-map-pin" class="w-5 h-5 text-gray-400 flex-shrink-0" />
                <div>
                  <p class="text-xs font-semibold text-gray-500 mb-0.5">Lokasi Pemasangan</p>
                  <p class="text-sm font-bold text-gray-900">
                    <template v-if="form.city">{{ form.city }}</template>
                    <span v-else class="text-gray-400 font-medium italic text-xs">Belum dipilih</span>
                  </p>
                </div>
              </div>
            </div>

            <!-- Pricing Breakdown -->
            <div class="px-6 py-5 bg-gray-50 flex-1">
              <div v-if="estimateLoading" class="flex items-center gap-2 mb-4 text-gray-500">
                <div class="w-4 h-4 rounded-full border-2 border-gray-400 border-t-transparent animate-spin" />
                <span class="text-sm font-medium">Menghitung estimasi...</span>
              </div>

              <p v-else-if="!estimate" class="text-sm text-gray-500 text-center py-4">
                Pilih spesifikasi untuk melihat estimasi harga.
              </p>

              <div v-else class="space-y-3 text-sm">
                <div v-if="estimate.device_price" class="flex justify-between text-gray-600">
                  <span>Perangkat CCTV</span>
                  <span class="font-bold text-gray-900">{{ fmt(estimate.device_price) }}</span>
                </div>
                <div v-if="estimate.service_price" class="flex justify-between text-gray-600">
                  <span>Biaya Jasa</span>
                  <span class="font-bold text-gray-900">{{ fmt(estimate.service_price) }}</span>
                </div>
                <div v-if="estimate.addon_price" class="flex justify-between text-gray-600">
                  <span>Fitur Tambahan</span>
                  <span class="font-bold text-gray-900">{{ fmt(estimate.addon_price) }}</span>
                </div>
                <div v-if="estimate.transport_fee" class="flex justify-between text-gray-600">
                  <span>Transportasi ({{ form.distance_km.toFixed(1) }} km)</span>
                  <span class="font-bold text-gray-900">{{ fmt(estimate.transport_fee) }}</span>
                </div>

                <div class="pt-4 mt-2 border-t border-gray-200">
                  <div class="flex justify-between items-end mb-1">
                    <span class="text-sm font-bold text-gray-900">Total Harga</span>
                    <span class="text-xl font-bold text-green-600">{{ fmt(estimate.total_price) }}</span>
                  </div>
                  <div class="flex justify-between text-xs mt-2 p-2 bg-amber-50 rounded-lg">
                    <span class="text-amber-800 font-medium">Bayar DP ({{ config.dp_percentage || 50 }}%)</span>
                    <span class="text-amber-800 font-bold">{{ fmt(estimate.dp_amount) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Desktop CTA -->
            <div class="p-6 bg-white border-t border-gray-100">
              <button type="button" :disabled="!canNext || isSubmitting"
                class="w-full bg-green-600 text-white py-3.5 px-6 rounded-xl flex items-center justify-center gap-2 transition-all hover:bg-green-700 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold shadow-sm"
                @click="nextStep">
                <UIcon v-if="isSubmitting" name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
                <span>{{ currentStep === TOTAL_STEPS ? 'Selesaikan Pesanan & Bayar DP' : 'Lanjutkan Booking' }}</span>
                <UIcon v-if="!isSubmitting" name="i-heroicons-arrow-right" class="w-5 h-5" />
              </button>
            </div>
          </div>
        </aside>
      </main>

      <!-- ── Mobile bottom bar ───────────────────────────────────── -->
      <div class="lg:hidden fixed bottom-0 inset-x-0 bg-white border-t border-gray-100 px-4 z-50 shadow-[0_-8px_20px_rgba(0,0,0,0.04)]"
           style="padding-bottom: calc(1rem + env(safe-area-inset-bottom))">
        <div class="flex items-center gap-4 py-3">
          <!-- Estimasi Harga -->
          <div class="flex-shrink-0 min-w-[120px]">
            <p class="text-xs font-semibold text-gray-500 mb-0.5">Total Harga</p>
            <div v-if="estimateLoading" class="flex items-center gap-1.5">
              <div class="w-3 h-3 rounded-full border-2 border-green-600 border-t-transparent animate-spin" />
              <span class="text-xs font-medium text-gray-500">Hitung...</span>
            </div>
            <template v-else>
              <p class="text-base font-bold text-green-600 leading-tight">
                {{ estimate ? fmt(estimate.total_price) : 'Rp 0' }}
              </p>
              <p v-if="estimate" class="text-[10px] font-semibold text-amber-600 mt-0.5">
                DP: {{ fmt(estimate.dp_amount) }}
              </p>
            </template>
          </div>

          <!-- Next button -->
          <button type="button" :disabled="!canNext || isSubmitting"
            class="flex-1 bg-green-600 text-white py-3 rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50 active:scale-95 shadow-sm"
            @click="nextStep">
            <UIcon v-if="isSubmitting" name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
            <span class="text-sm font-bold">
              {{ currentStep === TOTAL_STEPS ? 'Pesan Sekarang' : 'Lanjutkan' }}
            </span>
          </button>
        </div>
      </div>

    </template>
  </div>
</template>

<style scoped>
.step-fade-enter-active,
.step-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease-out;
}
.step-fade-enter-from { opacity: 0; transform: translateX(10px); }
.step-fade-leave-to { opacity: 0; transform: translateX(-10px); }

.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.hide-scrollbar::-webkit-scrollbar { display: none; }

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>