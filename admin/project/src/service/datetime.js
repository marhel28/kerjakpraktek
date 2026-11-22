import { ADMIN_TIMEZONE } from './api'

export const formatDateTime = (value, zone = ADMIN_TIMEZONE) => {
  if (!value) return '-'
  try {
    return new Intl.DateTimeFormat('id-ID', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: zone,
      timeZoneName: 'short',
    }).format(new Date(value))
  } catch {
    return String(value)
  }
}

export const formatLocalDate = (value, zone = ADMIN_TIMEZONE) => {
  if (!value) return '-'
  try {
    return new Intl.DateTimeFormat('id-ID', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      timeZone: zone,
      timeZoneName: 'short',
    }).format(new Date(value))
  } catch {
    return String(value)
  }
}
