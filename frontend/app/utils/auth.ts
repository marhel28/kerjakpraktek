export const isTokenExpired = (token: string | null) => {
    if (!token) return true
  
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const now = Date.now() / 1000
  
      return payload.exp < now
    } catch (e) {
      return true
    }
  }