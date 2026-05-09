import { defineEventHandler, getQuery, readBody, getCookie, getHeader, createError } from 'h3'
const config = useRuntimeConfig()
const BASE_URL = config.public.apiBase || 'http://127.0.0.1:8000'

// ─── Types ──────────────────────────────────────────────────────────────

export interface PromoItemResponse {
  uuid: string
  item_type: 'stock' | 'service_package'
  item_uuid: string
  item_name: string
  item_slug: string
  item_price: number
  thumbnail_url?: string
  override_discount_value?: number
}

export interface PromoResponse {
  uuid: string
  name: string
  slug: string
  description?: string
  banner_url?: string
  promo_type: 'percentage' | 'fixed' | 'bogo' | 'bundle_disc' | 'flash_sale'
  target: 'stock' | 'service_package' | 'all'
  discount_value: number
  max_discount?: number
  buy_quantity?: number
  get_quantity?: number
  min_purchase: number
  min_qty: number
  quota?: number
  used_count: number
  max_use_per_user?: number
  valid_from: string
  valid_until: string
  is_flash_sale: boolean
  flash_sale_quota?: number
  status: string
  priority: number
  items: PromoItemResponse[]
  is_valid: boolean
  remaining_quota?: number
}

export interface PromoListResponse {
  total: number
  page: number
  size: number
  items: PromoResponse[]
}

export interface PromoValidateResponse {
  is_valid: boolean
  message: string
  promo?: PromoResponse
  price_result?: any
}

export interface PromoCheckoutResponse {
  order_id: string
  promo_transaction_uuid: string
  gross_amount: number
  transaction_status: string
  snap_token?: string
}

// ─── Server Event Handler ───────────────────────────────────────────────

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const action = query.action as string
  const method = event.node.req.method

  // 1. Ambil token secara robust (Cek Header DULU, jika kosong baru cek Cookie)
  const incomingAuthHeader = getHeader(event, 'authorization')
  const tokenCookie = getCookie(event, 'token')
  
  const authHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  }
  
  // Set Authorization Header untuk dilempar ke backend external
  if (incomingAuthHeader) {
    // Jika dari client sudah bawa "Bearer xxxxx"
    authHeaders['Authorization'] = incomingAuthHeader
  } else if (tokenCookie) {
    // Jika dari client cuma bawa cookie
    authHeaders['Authorization'] = `Bearer ${tokenCookie}`
  }

  // 2. Helper untuk fetch ke backend external
  const apiFetch = async <T>(path: string, options: any = {}): Promise<T> => {
    try {
      return await $fetch<T>(`${BASE_URL}${path}`, {
        ...options,
        // Gabungkan authHeaders ke request external
        headers: { ...authHeaders, ...(options.headers || {}) }
      })
    } catch (error: any) {
      console.error(`[API Error] ${path}:`, error?.data || error?.message)
      throw createError({
        statusCode: error?.response?.status || 500,
        statusMessage: error?.response?.statusText || 'Internal Server Error',
        data: error?.data || error?.message
      })
    }
  }

  // 3. Routing berdasarkan action
  if (method === 'GET') {
    switch (action) {
      case 'listPromos':
        return await apiFetch<PromoListResponse>('/promos', {
          query: { 
            target: query.target, 
            page: query.page || 1, 
            size: query.size || 20 
          }
        })
        
      case 'listFlashSales':
        return await apiFetch<PromoListResponse>('/promos/flash-sale', {
          query: { 
            page: query.page || 1, 
            size: query.size || 10 
          }
        })

      case 'getPromo':
        if (!query.slug) throw createError({ statusCode: 400, message: 'Missing slug' })
        return await apiFetch<PromoResponse>(`/promos/${query.slug}`)

      case 'myOrders':
        return await apiFetch('/promos/my-orders', {
          query: { 
            page: query.page || 1, 
            limit: query.limit || 10, 
            status: query.status 
          }
        })

      case 'getOrderDetail':
        if (!query.orderId) throw createError({ statusCode: 400, message: 'Missing orderId' })
        return await apiFetch(`/promos/order/${query.orderId}`)

      case 'getAddresses':
        return await apiFetch('/cek/shipping/address')

      case 'getShippingEstimate':
        return await apiFetch('/transaksi/shipping/estimate', {
          query: {
            address_uuid: query.address_uuid,
            stock_uuid: query.stock_uuid,
            quantity: query.quantity,
            courier: query.courier || 'jne:sicepat:jnt'
          }
        })

      default:
        throw createError({ statusCode: 400, message: 'Invalid or missing GET action' })
    }
  }

  if (method === 'POST') {
    const body = await readBody(event)
    
    switch (action) {
      case 'validatePromo':
        return await apiFetch<PromoValidateResponse>('/promos/validate', { 
          method: 'POST', 
          body 
        })

      case 'checkout':
        return await apiFetch<PromoCheckoutResponse>('/promos/checkout', { 
          method: 'POST', 
          body 
        })

      default:
        throw createError({ statusCode: 400, message: 'Invalid or missing POST action' })
    }
  }

  throw createError({ statusCode: 405, message: 'Method Not Allowed' })
})