// stores/compare.ts
import { defineStore } from 'pinia'

// Definisikan tipe data yang lebih lengkap
export interface CompareItem {
  id: string | number
  image: string
  brand: string
  title: string
  price: number
  type?: string
  originalPrice?: number
  soldCount?: number
  specs?: Record<string, any> // 🔥 Menyimpan JSON Specs
}

export const useCompareStore = defineStore('compare', {
  state: () => ({
    items: [] as CompareItem[],
    maxItems: 4 
  }),

  getters: {
    isInCompare: (state) => (id: string | number) => {
      return state.items.some(item => item.id === id)
    },
    count: (state) => state.items.length,
    isFull: (state) => state.items.length >= state.maxItems
  },

  actions: {
    toggle(item: CompareItem) {
      const index = this.items.findIndex(i => i.id === item.id)

      if (index > -1) {
        this.items.splice(index, 1)
      } else {
        if (!this.isFull) {
          this.items.push(item)
        } else {
          console.warn(`Maksimal ${this.maxItems} produk untuk dibandingkan.`)
        }
      }
      this.saveToStorage()
    },

    clear() {
      this.items = []
      this.saveToStorage()
    },

    saveToStorage() {
      if (import.meta.client) {
        localStorage.setItem('compare_items', JSON.stringify(this.items))
      }
    },

    loadFromStorage() {
      if (import.meta.client) {
        const stored = localStorage.getItem('compare_items')
        if (stored) {
          try {
            this.items = JSON.parse(stored)
          } catch (e) {
            console.error('Failed to parse compare items', e)
          }
        }
      }
    }
  }
})