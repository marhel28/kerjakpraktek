export interface ResolvedBannerLink {
  href: string
  isExternal: boolean
  target: '_blank' | '_self'
  rel?: string
}

const FORBIDDEN_SCHEMES = ['javascript:', 'data:', 'vbscript:', 'file:']

export function useBannerRoute() {
  const sanitizeUrl = (rawUrl?: string | null): string => {
    if (!rawUrl) return '/'
    const trimmed = String(rawUrl).trim()
    const lower = trimmed.toLowerCase()

    if (FORBIDDEN_SCHEMES.some(scheme => lower.startsWith(scheme))) {
      return '/'
    }

    return trimmed
  }

  const resolveBannerLink = (rawUrl?: string | null): ResolvedBannerLink => {
    const clean = sanitizeUrl(rawUrl)
    const isHttp = clean.startsWith('http://') || clean.startsWith('https://')

    if (isHttp) {
      return {
        href: clean,
        isExternal: true,
        target: '_blank',
        rel: 'noopener noreferrer'
      }
    }

    const path = clean.startsWith('/') ? clean : `/${clean}`

    return {
      href: path,
      isExternal: false,
      target: '_self'
    }
  }

  return {
    sanitizeUrl,
    resolveBannerLink
  }
}