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
    subtotal: (state) => state.items.reduce((total, item) => total + (item.price * item.quantity), 0),
    totalWeight: (state) => state.items.reduce((total, item) => total + ((item.weight || 0) * item.quantity), 0),
    grandTotal: (state) => {
      const total = state.items.reduce((t, item) => t + (item.price * item.quantity), 0)
      return Math.max(0, total - state.discountPromo)
    }
  },

  actions: {
    setCheckoutData(selectedItems: any[], discount: number, code: string) {
      // Deep copy, sertakan stock_uuid
      this.items = JSON.parse(JSON.stringify(selectedItems))
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