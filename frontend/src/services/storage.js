const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  THEME: 'theme',
  LANGUAGE: 'language'
}



export const storageService = {
  setToken(token) {
    localStorage.setItem('token', token)
  },
  
  getToken() {
    return localStorage.getItem('token')
  },
  
  removeToken() {
    localStorage.removeItem('token')
  },
  
  setUser(user) {
    localStorage.setItem('user', JSON.stringify(user))
  },
  
  getUser() {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },
  
  removeUser() {
    localStorage.removeItem('user')
  },
  
  clear() {
    localStorage.clear()
  },
  
  isAuthenticated() {
    return !!this.getToken()
  },
  
  getUserRole() {
    const user = this.getUser()
    return user ? user.role : null
  }
}

export function initializeTheme() {
  
  const theme = localStorage.getItem(STORAGE_KEYS.THEME) || 'light'
  document.documentElement.setAttribute('data-theme', theme)
}