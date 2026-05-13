<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'

/**
 * /layanan/booking — Wizard booking jasa CCTV
 * Theme: Modern Marketplace (Green/White/Soft Gray)
 */

// ─── SEO ─────────────────────────────────────────────────────────
useSeoMeta({
  title: 'Pesan Instalasi & Konsultasi CCTV | PasarCctv',
  description: 'Pesan layanan instalasi, maintenance, atau konsultasi CCTV profesional secara gratis. Teknisi berpengalaman, bergaransi resmi, pengerjaan cepat.',
  robots: 'index, follow',
  ogTitle: 'Pesan Instalasi & Konsultasi CCTV | PasarCctv',
  ogDescription: 'Pesan layanan instalasi, maintenance, atau konsultasi CCTV profesional secara gratis. Teknisi berpengalaman, bergaransi resmi, pengerjaan cepat.',
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

// ─── Tab State for Packages ───────────────────────────────────────
const activeTab = ref('Populer')

const packageTabs = computed(() => {
  const tabs = ['Populer']
  const counts = new Set<number>()
  packagesList.value.forEach(p => {
    if (p.camera_count) counts.add(p.camera_count)
  })
  const sortedCounts = Array.from(counts).sort((a, b) => a - b)
  sortedCounts.forEach(c => tabs.push(`${c} Kamera`))
  tabs.push('Semua') // Tab semua di akhir
  return tabs
})

const displayedPackages = computed(() => {
  if (activeTab.value === 'Populer') {
    return packagesList.value.slice(0, 2) // 2 teratas sebagai populer
  }
  if (activeTab.value === 'Semua') {
    return packagesList.value
  }
  const match = activeTab.value.match(/(\d+)/)
  if (match) {
    const camCount = parseInt(match[1])
    return packagesList.value.filter(p => p.camera_count === camCount)
  }
  return packagesList.value
})

// Watch packages list to auto-select tab based on URL param
watch(() => packagesList.value, (newList) => {
  if (route.query.package && newList.length > 0) {
    const pkgInfo = newList.find(p => p.uuid === route.query.package)
    if (pkgInfo) {
       const isPopular = newList.slice(0, 2).some(p => p.uuid === pkgInfo.uuid)
       if (!isPopular && pkgInfo.camera_count) {
          activeTab.value = `${pkgInfo.camera_count} Kamera`
       }
    }
  }
}, { immediate: true })

// ─── Wilayah API (Kabupaten → Kecamatan → Desa) ───────────────────
const WILAYAH_BASE = 'https://www.emsifa.com/api-wilayah-indonesia/api'

const kabupatenList  = ref<{id:string,name:string}[]>([])
const kecamatanList  = ref<{id:string,name:string}[]>([])
const desaList       = ref<{id:string,name:string}[]>([])

const selectedKab    = ref('')
const selectedKec    = ref('')
const selectedDesa   = ref('')

const loadingKab  = ref(false)
const loadingKec  = ref(false)
const loadingDesa = ref(false)

// Jawa Barat = id 32
const PROV_JABAR = '32'

const fetchKabupaten = async () => {
  loadingKab.value = true
  try {
    const data = await $fetch<{id:string,name:string}[]>(`${WILAYAH_BASE}/regencies/${PROV_JABAR}.json`)
    kabupatenList.value = data
  } catch {}
  loadingKab.value = false
}

const fetchKecamatan = async (kabId: string) => {
  loadingKec.value = true
  kecamatanList.value = []
  desaList.value = []
  selectedKec.value = ''
  selectedDesa.value = ''
  try {
    const data = await $fetch<{id:string,name:string}[]>(`${WILAYAH_BASE}/districts/${kabId}.json`)
    kecamatanList.value = data
  } catch {}
  loadingKec.value = false
}

const fetchDesa = async (kecId: string) => {
  loadingDesa.value = true
  desaList.value = []
  selectedDesa.value = ''
  try {
    const data = await $fetch<{id:string,name:string}[]>(`${WILAYAH_BASE}/villages/${kecId}.json`)
    desaList.value = data
  } catch {}
  loadingDesa.value = false
}

const onKabChange = () => {
  const kab = kabupatenList.value.find(k => k.id === selectedKab.value)
  if (kab) {
    form.city = kab.name
    form.district = ''
    fetchKecamatan(kab.id)
  }
}

const onKecChange = () => {
  const kec = kecamatanList.value.find(k => k.id === selectedKec.value)
  if (kec) {
    form.district = kec.name
    fetchDesa(kec.id)
  }
}

const onDesaChange = () => {
  const desa = desaList.value.find(d => d.id === selectedDesa.value)
  if (desa) {
    // Append desa ke address hint
    if (!form.address.includes(desa.name)) {
      form.address = form.address ? `${form.address}, ${desa.name}` : desa.name
    }
  }
}

// Load kabupaten saat user tiba di step 2
watch(currentStep, (step) => {
  if (step === 2 && kabupatenList.value.length === 0) fetchKabupaten()
}, { immediate: false })

// Auto-switch ke tab Semua jika navigasi dari homepage via hash
if (process.client && window.location.hash === '#packages') {
  nextTick(() => { activeTab.value = 'Semua' })
}


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

const setManualCategory = (val: string) => { 
  form.category = val
  clearPackageSelection()
  if (val === 'consultation') {
    form.brand = '-'
    form.camera_count = 1
    form.addons = []
  } else if (form.brand === '-') {
    form.brand = ''
  }
}
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
    if (validCategories.includes(q.category)) {
      form.category = q.category
      if (q.category === 'consultation') {
        form.brand = '-'
        form.camera_count = 1
        form.addons = []
      }
    }
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
    
    console.log('[Booking] Fetching estimate...', body)
    const data = await $fetch<any>('/api/proxy/services/estimate', { method: 'POST', body })
    console.log('[Booking] Estimate received:', data)
    estimate.value = data
  } catch (e) {
    console.error('[Booking] Estimate fetch failed:', e)
  }
  finally { estimateLoading.value = false }
}

watch(
  () => [form.category, form.camera_count, form.brand, form.addons.join(','), form.distance_km, form.package_uuid],
  fetchEstimate,
  { deep: true, immediate: true }
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

    // 3. Redirect ke /booking/status/[number]
    // Kita langsung redirect ke status karena payment (DP) baru bisa dibuat 
    // setelah status booking berubah menjadi 'CONFIRMED' oleh admin.
    await router.push(`/booking/status/${bookingResult.booking_number}`)

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
  <div class="min-h-screen bg-[#F3F4F5] font-sans pb-32 lg:pb-16 text-gray-900 selection:bg-[#03AC0E] selection:text-white">

    <div v-if="configLoading" class="flex items-center justify-center min-h-screen">
      <div class="flex flex-col items-center gap-4">
        <div class="w-8 h-8 rounded-full border-4 border-[#03AC0E] border-t-transparent animate-spin" />
        <p class="text-sm font-semibold text-gray-500">Memuat layanan...</p>
      </div>
    </div>

    <div v-else-if="configError" class="flex items-center justify-center min-h-screen px-4">
      <div class="text-center bg-white p-8 rounded-lg shadow-sm border border-gray-200 max-w-sm w-full">
        <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-[#EF144A]" aria-hidden="true" />
        </div>
        <h2 class="text-lg font-bold text-gray-900 mb-2">Gagal Memuat Data</h2>
        <p class="text-[13px] text-gray-500 mb-6">Tidak dapat terhubung ke server. Periksa koneksi internet Anda.</p>
        <button
          class="w-full bg-[#03AC0E] text-white px-6 py-3 rounded-lg text-[15px] font-bold hover:bg-[#028c0b] transition-colors"
          @click="refreshConfig()"
        >
          Coba Lagi
        </button>
      </div>
    </div>

    <template v-else-if="config">

      <header class="hidden lg:block bg-white border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-[1200px] mx-auto px-4 md:px-6 h-16 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <button
              class="text-gray-500 hover:text-gray-900 flex items-center justify-center transition-colors"
              aria-label="Kembali"
              @click="prevStep"
            >
              <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" aria-hidden="true" />
            </button>
            <nav class="flex items-center gap-2">
              <h1 class="text-[15px] font-bold text-gray-900">Pesan Layanan CCTV</h1>
              <span class="text-gray-300">/</span>
              <span class="text-xs font-medium text-gray-500">Formulir Booking</span>
            </nav>
          </div>

          <div class="flex items-center gap-3 text-xs font-semibold">
            <template v-for="(step, i) in steps" :key="step.num">
              <div class="flex items-center gap-2" :class="currentStep >= step.num ? 'text-[#03AC0E]' : 'text-gray-400'">
                <span class="w-5 h-5 flex items-center justify-center rounded-full text-[10px]" 
                  :class="currentStep >= step.num ? 'bg-[#03AC0E] text-white' : 'bg-gray-100 text-gray-400 border border-gray-200'">
                  <UIcon v-if="currentStep > step.num" name="i-heroicons-check" class="w-3.5 h-3.5" aria-hidden="true" />
                  <span v-else>{{ step.num }}</span>
                </span>
                <span class="uppercase tracking-wide">{{ step.label }}</span>
              </div>
              <div v-if="i < steps.length - 1" class="w-8 h-[1px] bg-gray-200"></div>
            </template>
          </div>
        </div>
      </header>

      <header class="lg:hidden sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div class="px-4 h-14 flex items-center gap-3">
          <button class="p-2 -ml-2 rounded-full text-gray-500 hover:bg-gray-50 transition-colors" aria-label="Kembali" @click="prevStep">
            <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" aria-hidden="true" />
          </button>
          <div>
            <h1 class="text-sm font-bold text-gray-900">{{ steps[currentStep - 1].label }}</h1>
            <p class="text-[11px] font-medium text-gray-500">Langkah {{ currentStep }} dari {{ TOTAL_STEPS }}</p>
          </div>
        </div>
        <div class="h-1 w-full bg-gray-100" role="progressbar" :aria-valuenow="currentStep" :aria-valuemax="TOTAL_STEPS">
          <div class="h-full bg-[#03AC0E] transition-all duration-500 ease-out" :style="{ width: `${(currentStep / TOTAL_STEPS) * 100}%` }" />
        </div>
      </header>

      <main class="max-w-[1200px] mx-auto px-4 sm:px-6 mt-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

        <div class="lg:col-span-7 xl:col-span-8 min-w-0">

          <transition name="step-fade" mode="out-in">
            <div v-if="currentStep === 1" key="step1" class="space-y-6">

              <div class="lg:hidden mb-4">
                <h2 class="text-lg font-bold text-gray-900">Spesifikasi CCTV</h2>
                <p class="text-[13px] text-gray-500 mt-1">Pilih paket atau atur sesuai kebutuhan Anda.</p>
              </div>

              <section id="packages" v-if="packagesList.length > 0" aria-labelledby="packages-heading" class="bg-white rounded-lg border border-gray-200 p-5">
                <div class="flex items-center justify-between mb-3">
                  <h3 id="packages-heading" class="text-[15px] font-bold text-gray-900">Pilih Paket Layanan</h3>
                  <span class="text-[10px] font-bold text-[#03AC0E] bg-[#D6FFDE] px-2 py-1 rounded">LEBIH HEMAT</span>
                </div>

                <!-- Tabs Navigation -->
                <div class="flex items-center gap-2 mb-4 overflow-x-auto hide-scrollbar pb-1">
                  <button v-for="tab in packageTabs" :key="tab"
                    @click="activeTab = tab"
                    class="px-4 py-1.5 rounded-full text-[13px] font-bold whitespace-nowrap transition-colors border"
                    :class="activeTab === tab ? 'bg-[#03AC0E] text-white border-[#03AC0E] shadow-sm' : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'"
                  >
                    {{ tab }}
                  </button>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div v-for="pkg in displayedPackages" :key="pkg.uuid"
                       @click="selectPackage(pkg)"
                       :class="form.package_uuid === pkg.uuid 
                          ? 'border-[#03AC0E] bg-[#D6FFDE]/20 ring-1 ring-[#03AC0E]' 
                          : 'border-gray-200 bg-white hover:border-[#03AC0E] hover:shadow-sm'"
                       class="border rounded-lg p-4 cursor-pointer transition-all duration-200 flex flex-col h-full relative overflow-hidden">
                    
                    <UIcon v-if="form.package_uuid === pkg.uuid" name="i-heroicons-check-circle-20-solid" class="absolute top-3 right-3 w-6 h-6 text-[#03AC0E] z-10 bg-white rounded-full" aria-hidden="true" />

                    <div class="mb-4">
                      <BookingImageSectionPreview 
                        :src="pkg.thumbnail_url" 
                        :alt="pkg.name" 
                        aspectClass="w-full h-32" 
                      />
                    </div>
                    
                    <h4 class="font-bold text-[14px] text-gray-900 leading-snug mb-1 line-clamp-2">{{ pkg.name }}</h4>
                    <p class="text-[12px] text-gray-500 mb-3 line-clamp-2">{{ pkg.description }}</p>
                    
                    <ul class="space-y-1.5 mb-4">
                      <li v-for="hl in pkg.highlights.slice(0, 3)" :key="hl" class="flex items-start gap-1.5 text-[12px] text-gray-600 font-medium">
                        <UIcon name="i-heroicons-check" class="w-4 h-4 text-[#03AC0E] flex-shrink-0" aria-hidden="true" />
                        <span class="leading-tight">{{ hl }}</span>
                      </li>
                    </ul>

                    <div class="mt-auto pt-4 border-t border-gray-100 flex items-center justify-between">
                      <div>
                        <p class="text-[10px] font-semibold text-gray-400 mb-0.5 uppercase tracking-wide">Estimasi Total</p>
                        <p class="text-[15px] font-bold text-gray-900">{{ fmt(pkg.total_estimated) }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-4 my-6">
                  <div class="flex-1 h-[1px] bg-gray-200"></div>
                  <span class="text-[11px] font-bold text-gray-400 uppercase tracking-widest">ATAU RAKIT SENDIRI</span>
                  <div class="flex-1 h-[1px] bg-gray-200"></div>
                </div>
              </section>

              <section aria-labelledby="category-heading" class="bg-white p-5 rounded-lg border border-gray-200">
                <h3 id="category-heading" class="text-[15px] font-bold text-gray-900 mb-4">Jenis Layanan</h3>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <button v-for="cat in config.categories" :key="cat.id" type="button"
                    @click="setManualCategory(cat.id)"
                    class="flex flex-col items-center text-center p-4 rounded-lg border transition-all duration-200"
                    :class="form.category === cat.id && !form.package_uuid
                      ? 'border-[#03AC0E] bg-[#D6FFDE]/30 text-[#03AC0E] ring-1 ring-[#03AC0E]'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'">
                    <UIcon :name="CATEGORY_ICONS[cat.id] || 'i-heroicons-cog-6-tooth'" class="w-6 h-6 mb-2" :class="form.category === cat.id && !form.package_uuid ? 'text-[#03AC0E]' : 'text-gray-400'" aria-hidden="true" />
                    <span class="text-[13px] font-bold leading-tight">{{ cat.label }}</span>
                  </button>
                </div>
              </section>

              <section v-if="form.category !== 'consultation'" aria-labelledby="cam-heading" class="bg-white p-5 rounded-lg border border-gray-200">
                <h3 id="cam-heading" class="text-[15px] font-bold text-gray-900 mb-4">Jumlah Titik Kamera</h3>
                <div class="flex flex-wrap gap-3">
                  <button v-for="n in CAM_PRESETS" :key="n" type="button"
                    class="h-10 px-5 rounded border text-[13px] font-bold transition-all duration-200"
                    :class="form.camera_count === n && !isCustomCam && !form.package_uuid
                      ? 'border-[#03AC0E] bg-[#D6FFDE]/30 text-[#03AC0E] ring-1 ring-[#03AC0E]'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'"
                    @click="setManualCamCount(n)">
                    {{ n }} Titik
                  </button>
                  
                  <div class="h-10 rounded border overflow-hidden transition-all flex items-center"
                    :class="isCustomCam && !form.package_uuid ? 'border-[#03AC0E] ring-1 ring-[#03AC0E] bg-white' : 'border-gray-300 bg-white hover:border-gray-400'">
                    <button v-if="!isCustomCam" type="button" class="px-5 h-full text-[13px] font-bold text-gray-700" @click="isCustomCam = true; clearPackageSelection()">
                      Kustom
                    </button>
                    <div v-else class="flex items-center px-3 gap-2 h-full">
                      <span class="text-[12px] font-semibold text-gray-500">Jumlah:</span>
                      <input v-model.number="form.camera_count" type="number" min="1" max="200" @input="clearPackageSelection()"
                        class="w-14 h-7 text-center text-[13px] font-bold text-gray-900 border border-gray-200 bg-gray-50 rounded focus:ring-0 focus:border-[#03AC0E] outline-none" />
                    </div>
                  </div>
                </div>
              </section>

              <section v-if="form.category !== 'consultation'" aria-labelledby="brand-heading" class="bg-white p-5 rounded-lg border border-gray-200">
                <h3 id="brand-heading" class="text-[15px] font-bold text-gray-900 mb-4">Pilih Brand Perangkat</h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button v-for="brand in config.brands" :key="brand.key" type="button"
                    @click="setManualBrand(brand.key)"
                    class="flex items-center justify-between p-4 rounded-lg border transition-all duration-200 text-left"
                    :class="form.brand === brand.key && !form.package_uuid
                      ? 'border-[#03AC0E] bg-[#D6FFDE]/30 ring-1 ring-[#03AC0E]'
                      : 'border-gray-200 bg-white hover:border-gray-300'">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded bg-gray-100 flex items-center justify-center border border-gray-200"
                        :class="form.brand === brand.key && !form.package_uuid ? 'border-[#03AC0E]/50 text-[#03AC0E]' : 'text-gray-400'">
                        <UIcon name="i-heroicons-shield-check" class="w-5 h-5" aria-hidden="true" />
                      </div>
                      <div>
                        <h4 class="text-[14px] font-bold text-gray-900 uppercase">{{ brand.label }}</h4>
                        <p class="text-[11px] font-medium text-gray-500">Standard Quality</p>
                      </div>
                    </div>
                    <UIcon v-if="form.brand === brand.key && !form.package_uuid" name="i-heroicons-check-circle-20-solid" class="w-6 h-6 text-[#03AC0E]" aria-hidden="true" />
                  </button>
                </div>
              </section>

              <section v-if="config.addons?.length && form.category !== 'consultation'" aria-labelledby="addon-heading" class="bg-white p-5 rounded-lg border border-gray-200">
                <h3 id="addon-heading" class="text-[15px] font-bold text-gray-900 mb-4">Fitur Tambahan <span class="text-xs font-normal text-gray-500">(Opsional)</span></h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button v-for="addon in config.addons" :key="addon.key" type="button"
                    @click="toggleAddon(addon.key)"
                    class="text-left p-4 rounded-lg border transition-all duration-200"
                    :class="hasAddon(addon.key)
                      ? 'border-[#03AC0E] bg-[#D6FFDE]/30 ring-1 ring-[#03AC0E]'
                      : 'border-gray-200 bg-white hover:border-gray-300'">
                    <div class="flex justify-between items-start mb-1.5">
                      <span class="text-[13px] font-bold text-gray-900">{{ addon.label }}</span>
                      <div :class="[
                        'w-[18px] h-[18px] rounded flex items-center justify-center border transition-colors shrink-0',
                        hasAddon(addon.key) ? 'bg-[#03AC0E] border-[#03AC0E]' : 'border-gray-300 bg-white'
                      ]">
                        <svg v-if="hasAddon(addon.key)" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    </div>
                    <p v-if="addon.description" class="text-[12px] text-gray-500 leading-relaxed mb-2 line-clamp-2">{{ addon.description }}</p>
                    <p class="text-[13px] font-bold text-gray-900">
                      +{{ fmt(addon.price) }} <span class="text-[10px] font-normal text-gray-500 normal-case">{{ addon.type === 'per_cam' ? '/ Kamera' : 'Flat' }}</span>
                    </p>
                  </button>
                </div>
              </section>
            </div>
          </transition>

          <transition name="step-fade" mode="out-in">
            <div v-if="currentStep === 2" key="step2" class="space-y-6">
              
              <div class="lg:hidden mb-4">
                <h2 class="text-lg font-bold text-gray-900">Jadwal & Lokasi</h2>
                <p class="text-[13px] text-gray-500 mt-1">Pilih waktu dan tentukan lokasi pemasangan.</p>
              </div>

              <section aria-labelledby="date-heading" class="bg-white p-5 rounded-lg border border-gray-200">
                <h3 id="date-heading" class="text-[15px] font-bold text-gray-900 mb-4">Pilih Tanggal Kedatangan</h3>
                <div class="flex flex-nowrap overflow-x-auto gap-3 pb-2 hide-scrollbar snap-x">
                  <div class="snap-center flex-shrink-0 relative w-20">
                    <div class="w-full h-[88px] border border-dashed border-gray-300 rounded flex flex-col items-center justify-center gap-1 hover:border-[#03AC0E] hover:bg-[#D6FFDE]/30 transition-all cursor-pointer">
                      <UIcon name="i-heroicons-calendar-days" class="w-6 h-6 text-gray-400" />
                      <span class="text-[10px] font-bold text-gray-500 text-center leading-tight">Pilih<br>Lainnya</span>
                    </div>
                    <input type="date" :min="minDate" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" @change="addCustomDate" />
                  </div>

                  <button v-for="d in availableDates" :key="d.value" type="button"
                    class="snap-center flex-shrink-0 w-20 h-[88px] rounded border flex flex-col items-center justify-center transition-all duration-200"
                    :class="form.scheduled_date === d.value
                      ? 'border-[#03AC0E] bg-[#D6FFDE]/30 text-[#03AC0E] ring-1 ring-[#03AC0E]'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'"
                    @click="form.scheduled_date = d.value">
                    <span class="text-[11px] font-bold" :class="form.scheduled_date === d.value ? 'text-[#03AC0E]' : 'text-gray-400'">{{ d.dayShort }}</span>
                    <span class="text-[22px] font-bold leading-none my-1" :class="form.scheduled_date === d.value ? 'text-gray-900' : 'text-gray-700'">{{ d.num }}</span>
                    <span class="text-[10px] font-bold" :class="form.scheduled_date === d.value ? 'text-[#03AC0E]' : 'text-gray-400'">{{ d.month }}</span>
                  </button>
                </div>
              </section>

              <section v-if="form.scheduled_date" aria-labelledby="slot-heading" class="bg-white p-5 rounded-lg border border-gray-200">
                <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-100">
                  <h3 id="slot-heading" class="text-[15px] font-bold text-gray-900">Pilih Jam Kedatangan</h3>
                  <span class="text-[12px] font-bold text-gray-500 bg-gray-100 px-2 py-1 rounded">{{ selectedDateLabel }}</span>
                </div>

                <div v-if="slotsData?.message" class="mb-4 p-3 bg-red-50 border border-red-100 rounded flex items-center gap-2 text-[13px] text-[#EF144A] font-bold">
                  <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5" />
                  <span>{{ slotsData.message }}</span>
                </div>
                
                <div v-if="loadingSlots" class="flex gap-3">
                  <div v-for="i in 3" :key="i" class="h-14 flex-1 bg-gray-100 rounded animate-pulse" />
                </div>
                
                <div v-else class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <button v-for="slot in slotsData?.slots || DEFAULT_SLOTS" :key="slot.slot" type="button"
                    :disabled="!slot.available"
                    class="p-3 rounded border transition-all duration-200 text-left relative overflow-hidden"
                    :class="[
                      form.time_slot === slot.slot
                        ? 'border-[#03AC0E] bg-[#D6FFDE]/30 ring-1 ring-[#03AC0E]'
                        : slot.available
                          ? 'border-gray-200 bg-white hover:border-gray-300'
                          : 'border-gray-100 bg-gray-50 cursor-not-allowed opacity-60'
                    ]"
                    @click="slot.available && (form.time_slot = slot.slot)">
                    <p class="text-[13px] font-bold mb-0.5" :class="form.time_slot === slot.slot ? 'text-gray-900' : 'text-gray-800'">
                      {{ SLOT_LABELS[slot.slot] || slot.slot }}
                    </p>
                    <p class="text-[11px] font-medium" :class="slot.available ? (form.time_slot === slot.slot ? 'text-[#03AC0E]' : 'text-[#03AC0E]') : 'text-[#EF144A]'">
                      {{ slot.available ? `Tersedia ${slot.remaining} Slot` : 'Penuh' }}
                    </p>
                    <UIcon v-if="form.time_slot === slot.slot" name="i-heroicons-check-circle-20-solid" class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#03AC0E]" />
                  </button>
                </div>
              </section>

              <section aria-labelledby="loc-heading" class="bg-white p-5 rounded-lg border border-gray-200">
                <h3 id="loc-heading" class="text-[15px] font-bold text-gray-900 mb-4">Lokasi Pemasangan</h3>
                <div class="space-y-4">

                  <button type="button" :disabled="geoLoading"
                    class="w-full flex items-center justify-center gap-2 py-2.5 rounded border border-gray-300 bg-white text-[13px] font-bold transition-all"
                    :class="geoLoading ? 'text-gray-400 cursor-not-allowed' : form.latitude ? 'bg-[#D6FFDE]/30 border-[#03AC0E] text-[#03AC0E]' : 'text-gray-700 hover:bg-gray-50'"
                    @click="detectLocation">
                    <UIcon :name="geoLoading ? 'i-heroicons-arrow-path' : 'i-heroicons-map-pin'" :class="geoLoading ? 'animate-spin' : ''" class="w-4 h-4" />
                    <span>
                      {{ geoLoading ? 'Mencari lokasi...' : form.latitude ? `Lokasi Terdeteksi (${form.distance_km.toFixed(1)} km)` : 'Gunakan Lokasi Saat Ini (GPS)' }}
                    </span>
                  </button>

                  <div v-if="geoError" class="flex items-start gap-2 p-3 bg-red-50 border border-red-100 rounded text-[12px]">
                    <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 text-[#EF144A] flex-shrink-0" />
                    <p class="font-medium text-[#EF144A]">{{ geoError }}</p>
                  </div>

                  <div v-if="distanceData?.is_within_range" class="flex items-center justify-between p-3 bg-[#D6FFDE]/50 border border-[#03AC0E]/20 rounded">
                    <div class="flex items-center gap-3">
                      <div class="w-7 h-7 rounded bg-white flex items-center justify-center border border-[#03AC0E]/20"><UIcon name="i-heroicons-truck" class="w-4 h-4 text-[#03AC0E]" /></div>
                      <div>
                        <p class="text-[12px] font-bold text-gray-900">Masuk Area Layanan</p>
                        <p class="text-[11px] font-medium text-gray-600">Jarak: {{ form.distance_km.toFixed(1) }} km</p>
                      </div>
                    </div>
                    <p class="text-[13px] font-bold text-gray-900">{{ fmt(distanceData.transport_fee) }}</p>
                  </div>

                  <div class="h-[1px] bg-gray-100 my-4 w-full"></div>

                  <div class="space-y-4">
                    <div>
                      <label class="block text-[13px] font-bold text-gray-700 mb-2">Alamat Lengkap <span class="text-[#EF144A]">*</span></label>
                      <textarea v-model="form.address" rows="3" placeholder="Nama jalan, RT/RW, nomor rumah, patokan..."
                        class="w-full bg-white border border-gray-300 rounded px-3 py-2 text-[13px] text-gray-900 placeholder-gray-400 focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all resize-none" />
                    </div>

                    <!-- Wilayah Picker: Kabupaten → Kecamatan → Desa -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <!-- Kabupaten -->
                      <div>
                        <label class="block text-[13px] font-bold text-gray-700 mb-2">Kota / Kabupaten <span class="text-[#EF144A]">*</span></label>
                        <div class="relative">
                          <select v-model="selectedKab" @change="onKabChange"
                            class="w-full appearance-none bg-white border border-gray-300 rounded px-3 py-2 text-[13px] text-gray-900 focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all pr-8"
                            :disabled="loadingKab">
                            <option value="">{{ loadingKab ? 'Memuat...' : '-- Pilih Kabupaten --' }}</option>
                            <option v-for="kab in kabupatenList" :key="kab.id" :value="kab.id">{{ kab.name }}</option>
                          </select>
                          <UIcon :name="loadingKab ? 'i-heroicons-arrow-path' : 'i-heroicons-chevron-down'" :class="loadingKab ? 'animate-spin' : ''" class="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                        </div>
                      </div>

                      <!-- Kecamatan -->
                      <div>
                        <label class="block text-[13px] font-bold text-gray-700 mb-2">Kecamatan <span class="text-[#EF144A]">*</span></label>
                        <div class="relative">
                          <select v-model="selectedKec" @change="onKecChange"
                            class="w-full appearance-none bg-white border border-gray-300 rounded px-3 py-2 text-[13px] text-gray-900 focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all pr-8"
                            :disabled="!selectedKab || loadingKec">
                            <option value="">{{ loadingKec ? 'Memuat...' : !selectedKab ? 'Pilih kabupaten dulu' : '-- Pilih Kecamatan --' }}</option>
                            <option v-for="kec in kecamatanList" :key="kec.id" :value="kec.id">{{ kec.name }}</option>
                          </select>
                          <UIcon :name="loadingKec ? 'i-heroicons-arrow-path' : 'i-heroicons-chevron-down'" :class="loadingKec ? 'animate-spin' : ''" class="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                        </div>
                      </div>

                      <!-- Desa / Kelurahan -->
                      <div class="sm:col-span-2">
                        <label class="block text-[13px] font-bold text-gray-700 mb-2">Desa / Kelurahan <span class="font-normal text-gray-400">(Opsional, untuk detail)</span></label>
                        <div class="relative">
                          <select v-model="selectedDesa" @change="onDesaChange"
                            class="w-full appearance-none bg-white border border-gray-300 rounded px-3 py-2 text-[13px] text-gray-900 focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all pr-8"
                            :disabled="!selectedKec || loadingDesa">
                            <option value="">{{ loadingDesa ? 'Memuat...' : !selectedKec ? 'Pilih kecamatan dulu' : '-- Pilih Desa/Kelurahan --' }}</option>
                            <option v-for="desa in desaList" :key="desa.id" :value="desa.id">{{ desa.name }}</option>
                          </select>
                          <UIcon :name="loadingDesa ? 'i-heroicons-arrow-path' : 'i-heroicons-chevron-down'" :class="loadingDesa ? 'animate-spin' : ''" class="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                        </div>
                      </div>
                    </div>

                    <div v-if="!form.latitude" class="pt-2">
                      <label class="block text-[13px] font-bold text-gray-700 mb-2">Estimasi Jarak Manual <span class="font-normal text-gray-400">(Dari Toko)</span></label>
                      <div class="relative">
                        <input v-model.number="form.distance_km" type="number" min="0" :max="config.max_distance_km" step="0.5"
                          class="w-full bg-white border border-gray-300 rounded px-3 py-2 text-[13px] text-gray-900 focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all pr-12" />
                        <span class="absolute right-3 top-1/2 -translate-y-1/2 text-[13px] font-bold text-gray-400">km</span>
                      </div>
                      <p class="text-[11px] text-gray-500 mt-1.5 font-medium">Isi manual jika deteksi GPS gagal. Maksimal {{ config.max_distance_km }} km.</p>
                    </div>
                  </div>

                </div>
              </section>
            </div>
          </transition>

          <transition name="step-fade" mode="out-in">
            <div v-if="currentStep === 3" key="step3" class="space-y-6">

              <div class="lg:hidden mb-4">
                <h2 class="text-lg font-bold text-gray-900">Informasi Kontak</h2>
                <p class="text-[13px] text-gray-500 mt-1">Teknisi kami akan menghubungi nomor ini saat tiba di lokasi.</p>
              </div>

              <div class="bg-white border border-gray-200 rounded-lg p-5 space-y-5">
                <div>
                  <label for="contact-name" class="block text-[13px] font-bold text-gray-700 mb-2">Nama PIC / Penanggung Jawab <span class="text-[#EF144A]">*</span></label>
                  <div class="relative">
                    <UIcon name="i-heroicons-user" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input id="contact-name" v-model="form.contact_name" type="text" placeholder="Masukkan nama lengkap" autocomplete="name"
                      class="w-full bg-white border border-gray-300 rounded pl-9 pr-3 py-2 text-[13px] text-gray-900 placeholder-gray-400 focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all" />
                  </div>
                </div>

                <div>
                  <label for="contact-phone" class="block text-[13px] font-bold text-gray-700 mb-2">Nomor WhatsApp Aktif <span class="text-[#EF144A]">*</span></label>
                  <div class="relative">
                    <UIcon name="i-heroicons-phone" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input id="contact-phone" v-model="form.contact_phone" type="tel" placeholder="Contoh: 08123456789" autocomplete="tel"
                      class="w-full bg-white border border-gray-300 rounded pl-9 pr-3 py-2 text-[13px] text-gray-900 placeholder-gray-400 focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all" />
                  </div>
                </div>

                <div>
                  <label for="contact-notes" class="block text-[13px] font-bold text-gray-700 mb-2">Catatan Khusus <span class="text-gray-400 font-normal">(Opsional)</span></label>
                  <textarea id="contact-notes" v-model="form.contact_notes" rows="3" placeholder="Titip KTP ke satpam depan, rumah cat putih..."
                    class="w-full bg-white border border-gray-300 rounded px-3 py-2 text-[13px] text-gray-900 placeholder-gray-400 focus:ring-1 focus:ring-[#03AC0E] focus:border-[#03AC0E] outline-none transition-all resize-none" />
                </div>
              </div>

              <div v-if="submitError" role="alert" class="p-3 bg-red-50 border border-red-100 rounded flex items-start gap-2">
                <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 text-[#EF144A] flex-shrink-0 mt-0.5" />
                <p class="text-[12px] font-medium text-[#EF144A]">{{ submitError }}</p>
              </div>
            </div>
          </transition>
        </div>

        <aside class="hidden lg:flex lg:col-span-5 xl:col-span-4 flex-col" aria-label="Ringkasan Pesanan">
          <div class="sticky top-24 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col p-5">

            <h3 class="text-[15px] font-bold text-gray-900 pb-4 border-b border-gray-200 mb-4">Ringkasan Pemesanan</h3>
            
            <div class="mb-4">
              <h4 class="text-[14px] font-bold text-gray-900 leading-tight mb-2">
                {{ selectedPackageInfo ? selectedPackageInfo.name : 'Custom CCTV Setup' }}
              </h4>
              <div v-if="form.camera_count && form.brand" class="flex flex-wrap gap-2">
                <span class="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
                  {{ form.category }}
                </span>
                <span class="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
                  {{ form.camera_count }} Titik
                </span>
                <span class="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
                  {{ form.brand }}
                </span>
              </div>
              <p v-else class="text-[12px] text-gray-400 italic">Spesifikasi belum lengkap</p>
            </div>

            <div class="py-3 border-y border-gray-100 space-y-3">
              <div class="flex items-start gap-3 text-[13px]">
                <UIcon name="i-heroicons-calendar-days" class="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p class="text-gray-900">
                    <template v-if="selectedDateLabel && form.time_slot">
                      <span class="font-medium">{{ selectedDateLabel }}</span> <br /> <span class="font-bold">{{ SLOT_LABELS[form.time_slot] }}</span>
                    </template>
                    <span v-else class="text-gray-400 italic">Jadwal belum dipilih</span>
                  </p>
                </div>
              </div>
              
              <div class="flex items-start gap-3 text-[13px]">
                <UIcon name="i-heroicons-map-pin" class="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p class="text-gray-900">
                    <template v-if="form.city"><span class="font-medium">{{ form.city }}</span></template>
                    <span v-else class="text-gray-400 italic">Lokasi belum dipilih</span>
                  </p>
                </div>
              </div>
            </div>

            <div class="pt-4 flex-1">
              <div v-if="estimateLoading" class="flex items-center gap-2 mb-4 text-gray-500">
                <div class="w-4 h-4 rounded-full border-2 border-gray-300 border-t-transparent animate-spin" />
                <span class="text-[13px]">Menghitung estimasi...</span>
              </div>

              <p v-else-if="!estimate" class="text-[13px] text-gray-500 py-4 text-center">
                Selesaikan form untuk melihat estimasi harga.
              </p>

              <div v-else class="space-y-2 text-[13px]">
                <div v-if="estimate.device_price" class="flex justify-between text-gray-600">
                  <span>Harga Perangkat</span>
                  <span class="text-gray-900">{{ fmt(estimate.device_price) }}</span>
                </div>
                <div v-if="estimate.service_price" class="flex justify-between text-gray-600">
                  <span>Biaya Jasa</span>
                  <span class="text-gray-900">{{ fmt(estimate.service_price) }}</span>
                </div>
                <div v-if="estimate.addon_price" class="flex justify-between text-gray-600">
                  <span>Fitur Tambahan</span>
                  <span class="text-gray-900">{{ fmt(estimate.addon_price) }}</span>
                </div>
                <div v-if="estimate.transport_fee" class="flex justify-between text-gray-600">
                  <span>Ongkos Jalan ({{ form.distance_km.toFixed(1) }} km)</span>
                  <span class="text-gray-900">{{ fmt(estimate.transport_fee) }}</span>
                </div>

                <div class="pt-4 mt-3 border-t border-gray-200">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-[14px] font-bold text-gray-900">Total Tagihan</span>
                    <span class="text-[16px] font-bold text-gray-900">{{ fmt(estimate.total_price) }}</span>
                  </div>
                  <div class="flex justify-between items-center bg-[#FFF8E7] text-[#D48806] px-3 py-2 rounded text-[12px] font-bold">
                    <span>Bayar DP ({{ config.dp_percentage || 50 }}%)</span>
                    <span>{{ fmt(estimate.dp_amount) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <p class="text-[11px] text-gray-500 mt-6 mb-4 text-center leading-relaxed">
              Dengan melanjutkan, Anda menyetujui <NuxtLink to="/terms" class="text-gray-900 font-medium underline">Syarat & Ketentuan</NuxtLink>.
            </p>

            <div>
              <button type="button" :disabled="!canNext || isSubmitting"
                class="w-full bg-[#03AC0E] text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors hover:bg-[#028c0b] disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed text-[15px] font-bold"
                @click="nextStep">
                <UIcon v-if="isSubmitting" name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
                <span v-else>{{ currentStep === TOTAL_STEPS ? 'Bayar Sekarang' : 'Lanjutkan' }}</span>
              </button>
            </div>
          </div>
        </aside>
      </main>

      <div class="lg:hidden fixed bottom-0 inset-x-0 bg-white border-t border-gray-200 px-4 z-50 shadow-[0_-4px_10px_rgba(0,0,0,0.05)]"
           style="padding-bottom: calc(1rem + env(safe-area-inset-bottom))">
        <div class="flex items-center justify-between py-3">
          <div class="flex-shrink-0">
            <p class="text-[11px] font-bold text-gray-500 mb-0.5 uppercase">Total Tagihan</p>
            <div v-if="estimateLoading" class="flex items-center gap-1.5">
              <div class="w-3 h-3 rounded-full border-2 border-[#03AC0E] border-t-transparent animate-spin" />
              <span class="text-[12px] font-medium text-gray-500">Menghitung...</span>
            </div>
            <template v-else>
              <p class="text-[15px] font-bold text-gray-900 leading-tight">
                {{ estimate ? fmt(estimate.total_price) : 'Rp 0' }}
              </p>
              <p v-if="estimate" class="text-[10px] font-bold text-[#D48806] mt-0.5">
                DP: {{ fmt(estimate.dp_amount) }}
              </p>
            </template>
          </div>

          <button type="button" :disabled="!canNext || isSubmitting"
            class="min-w-[140px] bg-[#03AC0E] text-white py-2.5 px-4 rounded-lg flex items-center justify-center transition-colors disabled:bg-gray-300 disabled:text-gray-500"
            @click="nextStep">
            <UIcon v-if="isSubmitting" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin mr-2" />
            <span class="text-[14px] font-bold">
              {{ currentStep === TOTAL_STEPS ? 'Bayar DP' : 'Lanjutkan' }}
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
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.step-fade-enter-from { opacity: 0; transform: translateX(5px); }
.step-fade-leave-to { opacity: 0; transform: translateX(-5px); }

.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.hide-scrollbar::-webkit-scrollbar { display: none; }

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

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