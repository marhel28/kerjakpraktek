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
    async fetchProfile() {
      const config = useRuntimeConfig() // ✅ pindah ke sini

      this.isLoading = true
      this.error = null

      const token = useCookie('token').value

      try {
        const response = await $fetch(
          `${config.public.apiBase}/auth/user/users/me`,
          {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${token}`,
              Accept: 'application/json',
            },
          }
        )

        this.profile = response
      } catch (err: any) {
        this.error = err.data?.message || 'Gagal memuat data pengguna'
        console.error('Fetch Profile Error:', err)
      } finally {
        this.isLoading = false
      }
    },

    async updateProfile(payload: Record<string, any>) {
      const config = useRuntimeConfig() // ✅

      this.isSaving = true
      this.error = null

      const token = useCookie('token').value

      try {
        await $fetch(
          `${config.public.apiBase}/auth/user/users/me`,
          {
            method: 'PATCH',
            headers: {
              Authorization: `Bearer ${token}`,
              Accept: 'application/json',
            },
            body: payload,
          }
        )

        this.profile = {
          ...this.profile,
          ...payload,
          waktu_update: new Date().toISOString(),
        }

        return true
      } catch (err: any) {
        this.error = err.data?.message || 'Gagal memperbarui profil'
        return false
      } finally {
        this.isSaving = false
      }
    },

    async deleteUserData() {
      const config = useRuntimeConfig() // ✅

      this.isSaving = true

      const token = useCookie('auth_token').value

      try {
        await $fetch(
          `${config.public.apiBase}/auth/user/users/me`,
          {
            method: 'DELETE',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )

        this.profile = null

        await navigateTo('/login')
      } catch (err: any) {
        this.error = err.data?.message || 'Gagal menghapus data'
      } finally {
        this.isSaving = false
      }
    },
  },
})