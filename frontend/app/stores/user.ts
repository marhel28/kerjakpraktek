// stores/user.ts
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null as any | null,
    isLoading: false,
    isSaving: false,
    error: null as string | null,
  }),

  actions: {
    // 1. GET: Fetch User Profile
    async fetchProfile() {
      this.isLoading = true
      this.error = null
      
      // Asumsi token disimpan di cookie 'auth_token'
      const token = useCookie('token').value 
      
      try {
        const response = await $fetch('http://127.0.0.1:8000/auth/user/users/me', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          }
        })
        this.profile = response
      } catch (err: any) {
        this.error = err.data?.message || 'Gagal memuat data pengguna'
        console.error('Fetch Profile Error:', err)
      } finally {
        this.isLoading = false
      }
    },

    // 2. PUT: Update User Profile
    async updateProfile(payload: Record<string, any>) {
      this.isSaving = true
      this.error = null
      const token = useCookie('token').value

      try {
        const response = await $fetch('http://127.0.0.1:8000/auth/user/users/me', { // Sesuaikan endpoint PUT Anda
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
          },
          body: payload
        })
        
        // Optimistic Update
        this.profile = { ...this.profile, ...payload, waktu_update: new Date().toISOString() }
        return true
      } catch (err: any) {
        this.error = err.data?.message || 'Gagal memperbarui profil'
        return false
      } finally {
        this.isSaving = false
      }
    },

    // 3. DELETE: Hapus Keterangan User (Reset/Delete)
    async deleteUserData() {
      this.isSaving = true
      const token = useCookie('auth_token').value

      try {
        await $fetch('http://127.0.0.1:8000/auth/user/users/me', { // Sesuaikan endpoint DELETE Anda
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        // Reset state
        this.profile = null
        // Redirect ke login
        navigateTo('/login')
      } catch (err: any) {
        this.error = err.data?.message || 'Gagal menghapus data'
      } finally {
        this.isSaving = false
      }
    }
  }
})