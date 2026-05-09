/**
 * stores/promo.ts
 * Pinia store untuk state promo checkout
 */

import { defineStore } from 'pinia'
import type { PromoResponse, PromoItemBreakdown } from '~/server/api/promo'

export interface PromoCheckoutItem {
  item_uuid: string
  item_type: 'stock' | 'service_package'
  item_name: string
  item_price: number
  thumbnail_url?: string
  quantity: number
}

interface PromoCheckoutState {
  selectedPromo: PromoResponse | null
  items: PromoCheckoutItem[]
  priceBreakdown: PromoItemBreakdown[]
  totalOriginal: number
  totalDiscount: number
  totalDiscounted: number
}

export const usePromoStore = defineStore('promo', {
  state: (): PromoCheckoutState => ({
    selectedPromo: null,
    items: [],
    priceBreakdown: [],
    totalOriginal: 0,
    totalDiscount: 0,
    totalDiscounted: 0,
  }),

  getters: {
    stockItems: (state) =>
      state.items.filter((i) => i.item_type === 'stock'),
    serviceItems: (state) =>
      state.items.filter((i) => i.item_type === 'service_package'),
    totalQuantity: (state) =>
      state.items.reduce((sum, i) => sum + i.quantity, 0),
    hasStockItems: (state) =>
      state.items.some((i) => i.item_type === 'stock'),
    hasServiceItems: (state) =>
      state.items.some((i) => i.item_type === 'service_package'),
  },

  actions: {
    setPromo(promo: PromoResponse) {
      this.selectedPromo = promo
      // Pre-populate items dari promo.items
      this.items = promo.items.map((pi) => ({
        item_uuid: pi.item_uuid,
        item_type: pi.item_type as 'stock' | 'service_package',
        item_name: pi.item_name,
        item_price: pi.item_price,
        thumbnail_url: pi.thumbnail_url,
        quantity: 1,
      }))
    },

    updateQuantity(itemUuid: string, qty: number) {
      const item = this.items.find((i) => i.item_uuid === itemUuid)
      if (item) {
        item.quantity = Math.max(1, qty)
      }
    },

    setPriceResult(result: {
      items: PromoItemBreakdown[]
      items_subtotal_original: number
      total_discount: number
      items_subtotal_discounted: number
    }) {
      this.priceBreakdown = result.items
      this.totalOriginal = result.items_subtotal_original
      this.totalDiscount = result.total_discount
      this.totalDiscounted = result.items_subtotal_discounted
    },

    clearPromo() {
      this.$reset()
    },
  },
})