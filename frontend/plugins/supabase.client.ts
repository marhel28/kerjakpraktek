import { useSupabaseClientSingleton } from '~/plugins/supabase.client'

const getClient = () => {
  if (import.meta.server) return null
  return useSupabaseClientSingleton()
}