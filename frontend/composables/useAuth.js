/**
 * Auth state management composable.
 * Persists JWT token in localStorage, provides login/register/logout.
 */
import { ref, computed } from 'vue'

const TOKEN_KEY = 'oral_practice_auth'
const USER_KEY = 'oral_practice_user'

const token = ref(localStorage.getItem(TOKEN_KEY) || '')
const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

export const isAuthenticated = computed(() => !!token.value)
export const currentUser = computed(() => user.value)

function setAuth(tokenValue, userValue) {
  token.value = tokenValue
  user.value = userValue
  localStorage.setItem(TOKEN_KEY, tokenValue)
  localStorage.setItem(USER_KEY, JSON.stringify(userValue))
}

export function clearAuth() {
  token.value = ''
  user.value = null
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getAuthHeaders() {
  if (!token.value) return {}
  return { Authorization: `Bearer ${token.value}` }
}

export async function login(email, password) {
  const formData = new FormData()
  formData.append('email', email)
  formData.append('password', password)

  const res = await fetch('/api/auth/login', { method: 'POST', body: formData })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Login failed')
  }
  const data = await res.json()
  setAuth(data.token, data.user)
  return data.user
}

export async function register(email, password, nickname = '') {
  const formData = new FormData()
  formData.append('email', email)
  formData.append('password', password)
  if (nickname) formData.append('nickname', nickname)

  const res = await fetch('/api/auth/register', { method: 'POST', body: formData })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Registration failed')
  }
  const data = await res.json()
  setAuth(data.token, data.user)
  return data.user
}

export function logout() {
  clearAuth()
}
