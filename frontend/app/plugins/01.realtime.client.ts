export default defineNuxtPlugin(async () => {
  if (!import.meta.client) return

  const { initAfterLogin } = usePesanStore()
  const { init: initNotifications } = useNotificationStore()
  const { setSupabaseSession } = useAuth()

  // Tunggu session Supabase terestore dari cookies
  await setSupabaseSession()

  // Inisialisasi sekali saja saat client mount
  initAfterLogin()
  initNotifications()
})