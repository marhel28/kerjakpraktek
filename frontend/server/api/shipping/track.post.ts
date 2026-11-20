import { defineEventHandler, readBody, createError } from 'h3'

interface TrackingRequest {
  waybill: string
  courier?: string
}

function detectCourier(waybill: string): string {
  const clean = waybill.trim().toUpperCase()
  if (/^(JP|JX|JT)\d+/i.test(clean)) return 'jnt'
  if (/^00\d{10,}/.test(clean)) return 'sicepat'
  if (/^\d{15,16}$/.test(clean)) return 'jne'
  if (/^02\d{10,}/.test(clean)) return 'sicepat'
  if (/^TKP\d+/i.test(clean)) return 'anteraja'
  if (/^1\d{11}$/.test(clean)) return 'anteraja'
  if (/^P\d{10,}/i.test(clean)) return 'pos'
  if (/^\d{11,12}$/.test(clean)) return 'tiki'
  return 'jne'
}

export default defineEventHandler(async (event) => {
  const body = await readBody<TrackingRequest>(event)
  if (!body?.waybill) {
    throw createError({ statusCode: 400, statusMessage: 'Nomor resi wajib diisi' })
  }

  const waybill = body.waybill.trim().toUpperCase()
  const courier = (body.courier || detectCourier(waybill)).toLowerCase()

  const config = useRuntimeConfig()
  const apiKey = config.shippingCost || process.env.SHIPPING_COST || '519655761a6b0c2049ad88d374d6c4d7'
  const url = 'https://rajaongkir.komerce.id/api/v1/waybill'

  // In-memory cache fallback (15 menit TTL)
  const cacheKey = `track:${courier}:${waybill}`
  const cached = (globalThis as any).__trackingCache?.[cacheKey]
  if (cached && Date.now() - cached.timestamp < 15 * 60 * 1000) {
    return cached.data
  }

  try {
    const res = await $fetch<any>(url, {
      method: 'POST',
      headers: {
        key: apiKey,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        waybill,
        courier,
      }).toString(),
    })

    const data = res?.data || res?.rajaongkir?.result || res

    const summary = data?.summary || {
      waybill_number: waybill,
      courier_name: courier.toUpperCase(),
      service_code: data?.service || 'REG',
      waybill_date: data?.date || '',
      shipper_name: 'PasarCCTV Official',
      receiver_name: data?.receiver || '-',
      origin: 'KOTA BOGOR',
      destination: data?.destination || '-',
      status: data?.delivered ? 'DELIVERED' : 'ON_PROCESS',
    }

    const manifests = (data?.manifest || []).map((m: any) => ({
      date: m.manifest_date || m.date,
      time: m.manifest_time || m.time,
      description: m.manifest_description || m.desc,
      city: m.city_name || m.city || '',
    }))

    const result = {
      status: 'success',
      courier: courier.toUpperCase(),
      waybill,
      isDelivered: summary.status === 'DELIVERED',
      summary,
      manifests,
    }

    // Simpan di cache
    if (!(globalThis as any).__trackingCache) {
      ;(globalThis as any).__trackingCache = {}
    }
    ;(globalThis as any).__trackingCache[cacheKey] = {
      timestamp: Date.now(),
      data: result,
    }

    return result
  } catch (err: any) {
    const detail = err?.data?.message || err?.data?.meta?.message || err?.message || 'Resi tidak ditemukan'
    throw createError({ statusCode: 404, statusMessage: detail })
  }
})