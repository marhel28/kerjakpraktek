// stores/checkout.ts
import { defineStore } from 'pinia'

export const useCheckoutStore = defineStore('checkout', {
  state: () => ({
    // Menampung barang yang dicentang dari keranjang
    items: [] as {
      id: string
      title: string
      price: number
      image: string
      quantity: number
      weight: number
      options: any
      stock_uuid: string   // ✅ tambahan
    }[],
    
    discountPromo: 0,
    promoCode: ''
  }),

  getters: {
    totalQuantity: (state) => state.items.reduce((total, item) => total + item.quantity, 0),
    
    subtotal: (state) => state.items.reduce((total, item) => {
      const basePrice = item.price * item.quantity
      const addonsPrice = (item.options?.addons || []).reduce(
        (aAcc: number, a: any) => aAcc + (Number(a.price || 0) * Number(a.quantity || 1)),
        0
      )
      return total + basePrice + (addonsPrice * item.quantity)
    }, 0),

    totalWeight: (state) => state.items.reduce((total, item) => {
      const baseWeight = (item.weight || 0) * item.quantity
      const addonsWeight = (item.options?.addons || []).reduce(
        (wAcc: number, a: any) => wAcc + (Number(a.weight || 0) * Number(a.quantity || 1)),
        0
      )
      return total + baseWeight + (addonsWeight * item.quantity)
    }, 0),

    grandTotal: (state) => {
      return Math.max(0, state.items.reduce((total, item) => {
        const basePrice = item.price * item.quantity
        const addonsPrice = (item.options?.addons || []).reduce(
          (aAcc: number, a: any) => aAcc + (Number(a.price || 0) * Number(a.quantity || 1)),
          0
        )
        return total + basePrice + (addonsPrice * item.quantity)
      }, 0) - state.discountPromo)
    }
  },

  actions: {
    setCheckoutData(selectedItems: any[], discount: number, code: string) {
      // Deep copy, sertakan stock_uuid
      this.items = JSON.parse(JSON.stringify(selectedItems))
      this.discountPromo = discount
      this.promoCode = code
    },

    setPromo(discount: number, code: string) {
      this.discountPromo = discount
      this.promoCode = code
    },

    clearCheckoutData() {
      this.items = []
      this.discountPromo = 0
      this.promoCode = ''
    }
  }
})