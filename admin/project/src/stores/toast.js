import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const show = ref(false)
  const message = ref('')
  const type = ref('success') // 'success' | 'error' | 'warning' | 'info'
  let timer = null

  const showToast = (msg, toastType = 'success', duration = 3500) => {
    clearTimeout(timer)
    message.value = msg
    type.value = toastType
    show.value = true

    timer = setTimeout(() => {
      show.value = false
    }, duration)
  }

  const success = (msg, duration) => showToast(msg, 'success', duration)
  const error = (msg, duration) => showToast(msg, 'error', duration)
  const warning = (msg, duration) => showToast(msg, 'warning', duration)
  const info = (msg, duration) => showToast(msg, 'info', duration)

  return {
    show,
    message,
    type,
    success,
    error,
    warning,
    info
  }
})
