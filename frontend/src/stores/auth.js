import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../router/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('aroma_user') || 'null'))
  const accessToken = ref(localStorage.getItem('aroma_access') || '')
  const refreshToken = ref(localStorage.getItem('aroma_refresh') || '')
  const adminSessionActive = ref(localStorage.getItem('aroma_admin_session') === '1')

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_admin === true)
  // True ONLY when the user explicitly logged in via /admin/login
  const isAdminSession = computed(() => isAdmin.value && adminSessionActive.value)

  function setAdminSession(active) {
    adminSessionActive.value = active
    if (active) {
      localStorage.setItem('aroma_admin_session', '1')
    } else {
      localStorage.removeItem('aroma_admin_session')
    }
  }

  function _persist() {
    localStorage.setItem('aroma_user', JSON.stringify(user.value))
    localStorage.setItem('aroma_access', accessToken.value)
    localStorage.setItem('aroma_refresh', refreshToken.value)
  }

  function _setTokens(data) {
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    user.value = data.user
    _persist()
  }

  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    _setTokens(data)
    return data
  }

  async function register(payload) {
    const { data } = await api.post('/auth/register', payload)
    return data
  }

  async function logout() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    adminSessionActive.value = false
    localStorage.removeItem('aroma_user')
    localStorage.removeItem('aroma_access')
    localStorage.removeItem('aroma_refresh')
    localStorage.removeItem('aroma_admin_session')
  }

  async function refreshAccessToken() {
    try {
      const { data } = await api.post('/auth/refresh', { refresh_token: refreshToken.value })
      _setTokens(data)
      return data.access_token
    } catch {
      await logout()
      return null
    }
  }

  async function fetchMe() {
    const { data } = await api.get('/auth/me')
    user.value = data
    localStorage.setItem('aroma_user', JSON.stringify(data))
    return data
  }

  async function forgotPassword(email) {
    await api.post('/auth/forgot-password', { email })
  }

  async function resetPassword(token, new_password) {
    await api.post('/auth/reset-password', { token, new_password })
  }

  async function verifyEmail(token) {
    const { data } = await api.get(`/auth/verify-email?token=${token}`)
    _setTokens(data)
  }

  async function resendVerification(email) {
    await api.post('/auth/resend-verification', { email })
  }

  async function googleLogin(idToken) {
    const { data } = await api.post('/auth/google', { id_token: idToken })
    _setTokens(data)
  }

  return {
    user, accessToken, refreshToken,
    isAuthenticated, isAdmin, isAdminSession,
    login, register, logout,
    refreshAccessToken, fetchMe,
    forgotPassword, resetPassword,
    verifyEmail, resendVerification, googleLogin,
    setAdminSession,
  }
})
