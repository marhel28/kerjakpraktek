// stores/wishlist.ts
import { defineStore } from 'pinia'

// Schema berdasarkan response API
export interface WishlistItem {
  wishlist_uuid: string;
  created_at?: string;
  notes?: string;
  stock: {
    uuid: string; // ID dari produk/stock
    title: string;
    slug?: string;
    online_price: number;
    is_active?: boolean;
    cover_image_url: string;
    weight: number,
  }
}

export const useWishlistStore = defineStore('wishlist', {
  state: () => ({
    items: [] as WishlistItem[],
  }),

  getters: {
    count: (state) => state.items.length,
    
    // Cek berdasarkan ID Produk (stock_uuid)
    isInWishlist: (state) => (stockUuid: string | number) => 
      state.items.some(item => String(item.stock.uuid) === String(stockUuid)),
    
    // Ambil wishlist_uuid untuk keperluan Delete API
    getWishlistUuid: (state) => (stockUuid: string | number) => {
      const item = state.items.find(item => String(item.stock.uuid) === String(stockUuid))
      return item ? item.wishlist_uuid : null
    }
  },

  actions: {
    // ==========================================
    // FETCH DATA DARI API
    // ==========================================
    async fetchWishlist() {
      try {
        const data = await $fetch<WishlistItem[]>('/api/wishlist')
        if (data) this.items = data
      } catch (err) {
        console.error('Gagal mengambil wishlist:', err)
      }
    },

    // ==========================================
    // TOGGLE (ADD/REMOVE) DENGAN OPTIMISTIC UI
    // ==========================================
    async toggle(productData: any) {
      // Pastikan kita mendapatkan UUID produk dengan aman dari berbagai komponen
      // Handle berbagai shape: { id }, { stock_uuid }, { uuid }, { stock: { uuid } }
      const stockUuid = String(
        productData.id ||
        productData.stock_uuid ||
        productData.uuid ||
        productData.stock?.uuid
      )
      const isAlreadyInWishlist = this.isInWishlist(stockUuid)

      if (isAlreadyInWishlist) {
        // ------------------------------------------
        // OPTIMISTIC DELETE
        // ------------------------------------------
        const wishlistUuid = this.getWishlistUuid(stockUuid)
        
        // 🔥 PERBAIKAN 1: Cegah pengiriman 'temp-' ke backend (Mencegah Error 422)
        if (wishlistUuid && wishlistUuid.startsWith('temp-')) {
          // Jika masih 'temp-', berarti user klik Hapus sebelum POST selesai.
          // Langsung hapus dari state UI saja tanpa hit API DELETE.
          this.items = this.items.filter(item => item.wishlist_uuid !== wishlistUuid)
          return
        }

        const backupItems = [...this.items]
        
        // Langsung hapus dari state (UI seketika berubah)
        this.items = this.items.filter(item => item.wishlist_uuid !== wishlistUuid)

        try {
          // Hit API Nuxt Server di background
          await $fetch(`/api/wishlist/${wishlistUuid}`, { method: 'DELETE' })
        } catch (err) {
          // Jika API gagal, kembalikan state seperti semula
          this.items = backupItems
          console.error('Gagal menghapus wishlist:', err)
          try {
            const toast = useToast()
            toast.add({ title: 'Gagal', description: 'Gagal menghapus dari wishlist', color: 'error' })
          } catch {}
        }

      } else {
        // ------------------------------------------
        // OPTIMISTIC ADD
        // ------------------------------------------
        const tempWishlistUuid = `temp-${Date.now()}` // Buat UUID sementara
        
        const newItem: WishlistItem = {
          wishlist_uuid: tempWishlistUuid,
          stock: {
            uuid: stockUuid,
            title: productData.title,
            online_price: productData.price || productData.online_price,
            cover_image_url: productData.image || productData.cover_image_url,
            weight: productData.weight
          }
        }
        
        // Langsung tambah ke state (UI seketika berubah)
        this.items.push(newItem)

        try {
          // Hit API Nuxt Server
          const response = await $fetch<any>('/api/wishlist', {
            method: 'POST',
            body: { stock_uuid: stockUuid }
          })

          // 🔥 PERBAIKAN 2: Ekstraksi UUID Super Aman
          // Menangani berbagai format response JSON dari FastAPI/Pydantic
          let actualWishlistUuid = null
          if (typeof response === 'string') {
            actualWishlistUuid = response
          } else if (response) {
            actualWishlistUuid = 
              response.wishlist_uuid || 
              response.id || 
              response.uuid ||
              response.data?.wishlist_uuid || 
              response.data?.id
          }

          // Update UUID sementara ('temp-') dengan UUID asli dari backend
          const index = this.items.findIndex(item => item.wishlist_uuid === tempWishlistUuid)
          
          if (index !== -1) {
            if (actualWishlistUuid) {
              this.items[index].wishlist_uuid = actualWishlistUuid
            } else {
              console.warn('Gagal membaca format UUID dari backend. Response:', response)
            }
          }
        } catch (err) {
          // Jika POST gagal, hapus item yang baru ditambahkan secara optimis
          this.items = this.items.filter(item => item.wishlist_uuid !== tempWishlistUuid)
          console.error('Gagal menambah wishlist:', err)
        }
      }
    }
  },
  
  // Tetap pertahankan state sementara saat user pindah rute sebelum data difetch
  persist: true 
})