import { ref, computed, onMounted, onUnmounted } from 'vue'

export interface FlashSaleItem {
  stock_uuid: string
  title: string
  slug: string
  image: string
  original_price: number
  price: number
  discount_percentage: number
  quota: number
  sold_count: number
  is_almost_sold_out: boolean
}

export interface FlashSaleData {
  promo_uuid: string
  title: string
  mode: 'auto' | 'manual'
  strategy?: string
  valid_from: string
  valid_until: string
  server_now: string
  remaining_seconds: number
  items: FlashSaleItem[]
}

export function useFlashSale() {
  const { data, pending, error, refresh } = useFetch<FlashSaleData>('/api/flashsale', {
    key: 'home-flashsale-active',
    lazy: true,
    server: true,
  })

  const remainingSeconds = ref(0)
  let timer: any = null

  const hours = computed(() => {
    const h = Math.floor(remainingSeconds.value / 3600)
    return String(h).padStart(2, '0')
  })

  const minutes = computed(() => {
    const m = Math.floor((remainingSeconds.value % 3600) / 60)
    return String(m).padStart(2, '0')
  })

  const seconds = computed(() => {
    const s = remainingSeconds.value % 60
    return String(s).padStart(2, '0')
  })

  const isExpired = computed(() => remainingSeconds.value <= 0)

  const startCountdown = () => {
    if (timer) clearInterval(timer)
    if (data.value && data.value.remaining_seconds) {
      remainingSeconds.value = data.value.remaining_seconds
    }

    timer = setInterval(() => {
      if (remainingSeconds.value > 0) {
        remainingSeconds.value--
      } else {
        clearInterval(timer)
        refresh()
      }
    }, 1000)
  }

  watch(data, (newVal) => {
    if (newVal && newVal.remaining_seconds) {
      startCountdown()
    }
  })

  onMounted(() => {
    if (data.value?.remaining_seconds) {
      startCountdown()
    }
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return {
    data,
    pending,
    error,
    refresh,
    hours,
    minutes,
    seconds,
    isExpired,
  }
}