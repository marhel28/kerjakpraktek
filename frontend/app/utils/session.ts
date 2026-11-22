import { useCookie } from '#imports'

/**
 * Ambil UUID user backend (bukan ID dari penyedia auth eksternal).
 * Sumber utama: cookie `user_data` dari /api/login.
 * Fallback: baca claim `user.uuid` dari JWT tanpa verifikasi signature.
 */
export function getBackendUserId(tokenValue?: string | null): string {
  try {
    const raw = useCookie<any>('user_data').value as any
    if (raw) {
      const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw
      if (parsed?.uuid) return String(parsed.uuid)
    }
  } catch {
    // lanjut ke fallback
  }

  if (tokenValue) {
    try {
      const payload = JSON.parse(atob(tokenValue.split('.')[1] ?? ''))
      const uuid = payload?.user?.uuid
      if (uuid) return String(uuid)
    } catch {
      // token tidak bisa di-decode
    }
  }
  return ''
}
