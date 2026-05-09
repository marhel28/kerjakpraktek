import { defineStore } from 'pinia'
import { useCookie, useRuntimeConfig } from '#app'

export interface CartItem {
  cart_uuid?: string
  stock_uuid: string
  title: string
  brand?: string
  category_slug?: string
  specs?: any
  price: number
  original_price?: number
  discount_percentage?: number
  quantity: number
  image: string
  weight?: number
}

// =========================
// GLOBAL DEBOUNCE (SAFE)
// =========================
let timeoutId: any = null

// =========================
// SIMPLE MEMORY CACHE
// =========================
let cartCache: any = null
let cartCacheExpire = 0

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [] as CartItem[],
    isSyncing: false,
    lastFetch: 0,
  }),

  // =========================
  // GETTERS (OPTIMIZED)
  // =========================
  getters: {
    count: (state) =>
      state.items.reduce((acc, item) => acc + item.quantity, 0),

    totalHarga: (state) =>
      state.items.reduce((acc, item) => acc + item.price * item.quantity, 0),

    totalWeight: (state) =>
      state.items.reduce(
        (acc, item) => acc + (item.weight || 0) * item.quantity,
        0
      ),

    isLoggedIn: () => !!useCookie('token').value,
  },

  actions: {
    // =========================
    // FETCH (CACHE + SSR SAFE)
    // =========================
    async fetchCartFromAPI(force = false) {
      if (!this.isLoggedIn) return

      const now = Date.now()

      // ✔ CACHE HIT (30 detik)
      if (!force && cartCache && cartCacheExpire > now) {
        this.items = cartCache
        return
      }

      try {
        const token = useCookie('token').value
        const config = useRuntimeConfig()

        const res: any = await $fetch(`${config.public.apiBase}/cart`, {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 4000,
        })

        const backendItems: CartItem[] = (res.items || []).map(
          (item: any) => ({
            cart_uuid: item.cart_uuid,
            stock_uuid: item.stock.uuid,
            title: item.stock.title,
            brand: item.stock.brand,
            category_slug: item.stock.category_slug || item.stock.type,
            specs: item.stock.specs,
            price: item.stock.online_price,
            original_price: item.stock.original_price,
            discount_percentage: item.stock.discount_percentage,
            image: item.stock.cover_image_url,
            quantity: Math.max(1, Number(item.quantity) || 1),
            weight: item.stock.weight,
          })
        )

        this.items = backendItems

        // ✔ UPDATE CACHE
        cartCache = backendItems
        cartCacheExpire = now + 30000 // 30s cache
      } catch (error) {
        console.error('GET CART ERROR:', error)
      }
    },

    // =========================
    // MERGE CART (OPTIMIZED)
    // =========================
    async mergeCartOnLogin() {
      const token = useCookie('token').value
      if (!token || this.isSyncing) return

      this.isSyncing = true

      try {
        const config = useRuntimeConfig()

        const res: any = await $fetch(`${config.public.apiBase}/cart`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        const backendItems = res.items || []

        if (this.items.length === 0) {
          await this.fetchCartFromAPI(true)
          this.isSyncing = false
          return
        }

        const tasks = this.items.map(async (localItem) => {
          const exist = backendItems.find(
            (b: any) => b.stock.uuid === localItem.stock_uuid
          )

          if (exist) {
            return $fetch(
              `${config.public.apiBase}/cart/${exist.cart_uuid}`,
              {
                method: 'PATCH',
                headers: { Authorization: `Bearer ${token}` },
                body: {
                  quantity:
                    localItem.quantity + Number(exist.quantity),
                },
              }
            ).catch(() => {})
          }

          return $fetch(`${config.public.apiBase}/cart`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body: {
              stock_uuid: localItem.stock_uuid,
              quantity: localItem.quantity,
            },
          }).catch(() => {})
        })

        await Promise.allSettled(tasks)

        this.items = []
        await this.fetchCartFromAPI(true)
      } catch (err) {
        console.error('MERGE CART ERROR:', err)
      } finally {
        this.isSyncing = false
      }
    },

    // =========================
    // ADD (OPTIMISTIC UPDATE)
    // =========================
    async add(product: any) {
      const uuid =
        product.stock_uuid || product.id || product.uuid

      if (!uuid) return

      const qty = Math.max(1, Number(product.quantity) || 1)

      const existing = this.items.find(
        (i) => i.stock_uuid === uuid
      )

      // ✔ optimistik update dulu
      if (existing) {
        existing.quantity += qty
        this.syncUpdate(existing)
        return
      }

      const newItem: CartItem = {
        stock_uuid: uuid,
        title: product.title,
        brand: product.brand,
        category_slug:
          product.category_slug || product.category,
        specs: product.specs,
        price: product.price || product.online_price,
        original_price: product.original_price,
        discount_percentage: product.discount_percentage,
        image: product.image || product.cover_image_url,
        quantity: qty,
        weight: product.weight,
      }

      this.items.push(newItem)

      if (!this.isLoggedIn) return

      try {
        const token = useCookie('token').value
        const config = useRuntimeConfig()

        const res: any = await $fetch(
          `${config.public.apiBase}/cart`,
          {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body: {
              stock_uuid: uuid,
              quantity: qty,
            },
          }
        )

        newItem.cart_uuid = res?.cart_uuid
      } catch (err) {
        console.error('ADD CART ERROR:', err)
      }
    },

    // =========================
    // UPDATE (DEBOUNCE FIXED)
    // =========================
    updateQuantity(stock_uuid: string, change: number) {
      const item = this.items.find(
        (i) => i.stock_uuid === stock_uuid
      )
      if (!item) return

      item.quantity = Math.max(1, item.quantity + change)

      if (!this.isLoggedIn || !item.cart_uuid) return

      clearTimeout(timeoutId)

      timeoutId = setTimeout(() => {
        this.syncUpdate(item)
      }, 300)
    },

    async syncUpdate(item: CartItem) {
      if (!item.cart_uuid) return

      const token = useCookie('token').value
      const config = useRuntimeConfig()

      try {
        await $fetch(
          `${config.public.apiBase}/cart/${item.cart_uuid}`,
          {
            method: 'PATCH',
            headers: { Authorization: `Bearer ${token}` },
            body: { quantity: item.quantity },
          }
        )
      } catch {
        // silent fail (biar UX tidak patah)
      }
    },

    // =========================
    // REMOVE (OPTIMISTIC)
    // =========================
    async remove(stock_uuid: string) {
      const idx = this.items.findIndex(
        (i) => i.stock_uuid === stock_uuid
      )

      if (idx === -1) return

      const item = this.items[idx]

      // ✔ instant UI remove
      this.items.splice(idx, 1)

      if (!this.isLoggedIn || !item.cart_uuid) return

      try {
        const token = useCookie('token').value
        const config = useRuntimeConfig()

        await $fetch(
          `${config.public.apiBase}/cart/${item.cart_uuid}`,
          {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` },
          }
        )
      } catch {
        // silent fail
      }
    },

    clear() {
      this.items = []
      cartCache = null
      cartCacheExpire = 0
    },
  },

  persist: true,
})