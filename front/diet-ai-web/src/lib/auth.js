const TOKEN_KEY = 'auth_token'
const USER_ID_KEY = 'auth_user_id'
const AUTH_STATE_EVENT = 'auth-state-changed'

export function isLoggedIn() {
  return Boolean(localStorage.getItem(TOKEN_KEY))
}

export function getAuthUserId() {
  return localStorage.getItem(USER_ID_KEY)
}

export function saveAuthSession({ token, userId }) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  }

  if (userId !== undefined && userId !== null && `${userId}`.trim()) {
    localStorage.setItem(USER_ID_KEY, `${userId}`)
  }
}

export function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_ID_KEY)
}

export function notifyAuthStateChanged() {
  window.dispatchEvent(new Event(AUTH_STATE_EVENT))
}

export function subscribeAuthStateChange(onChange) {
  const handler = () => onChange(isLoggedIn())

  window.addEventListener('storage', handler)
  window.addEventListener(AUTH_STATE_EVENT, handler)

  return () => {
    window.removeEventListener('storage', handler)
    window.removeEventListener(AUTH_STATE_EVENT, handler)
  }
}
