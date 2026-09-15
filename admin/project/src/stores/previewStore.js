import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const DEFAULT_PREVIEW_URL = 'https://marketplace-pi-sable.vercel.app/login'

export const usePreviewStore = defineStore('preview', () => {
  const previewUrl = ref(localStorage.getItem('admin_preview_url') || DEFAULT_PREVIEW_URL)

  const baseUrl = computed(() => {
    try {
      const parsed = new URL(previewUrl.value)
      return `${parsed.protocol}//${parsed.host}`
    } catch {
      return 'https://marketplace-pi-sable.vercel.app'
    }
  })

  const setPreviewUrl = (url) => {
    const trimmed = (url || '').trim() || DEFAULT_PREVIEW_URL
    previewUrl.value = trimmed
    localStorage.setItem('admin_preview_url', trimmed)
  }

  const resetToDefault = () => {
    setPreviewUrl(DEFAULT_PREVIEW_URL)
  }

  const resolveUrl = (path = '') => {
    if (!path) return previewUrl.value
    if (path.startsWith('http://') || path.startsWith('https://')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${baseUrl.value}${cleanPath}`
  }

  return {
    previewUrl,
    baseUrl,
    setPreviewUrl,
    resetToDefault,
    resolveUrl,
  }
})
