export default defineNuxtPlugin(() => {
  if (!import.meta.client) return

  const { initAfterLogin } = usePesanStore()
  const { init: initNotifications } = useNotificationStore()

  // Inisialisasi sekali saja saat client mount
  initAfterLogin()
  initNotifications()
})
