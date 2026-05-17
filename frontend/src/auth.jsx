import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import axios from 'axios'

export const API = import.meta.env.DEV ? 'http://localhost:3000' : ''
const TOKEN_KEY = 'contextguard_token'

const AuthContext = createContext(null)

let interceptorReady = false

function setupAxiosAuth() {
  if (interceptorReady) return
  interceptorReady = true

  axios.interceptors.request.use((config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      const url = error.config?.url || ''
      const isAuthRoute = url.includes('/api/auth/login') || url.includes('/api/auth/register')
      if (error.response?.status === 401 && !isAuthRoute) {
        localStorage.removeItem(TOKEN_KEY)
        if (window.location.pathname.startsWith('/dashboard')) {
          window.location.assign('/login')
        }
      }
      return Promise.reject(error)
    }
  )
}

export function AuthProvider({ children }) {
  setupAxiosAuth()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setUser(null)
      setLoading(false)
      return null
    }
    try {
      const res = await axios.get(`${API}/api/auth/me`)
      setUser(res.data)
      return res.data
    } catch {
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  const login = async (email, password) => {
    const res = await axios.post(`${API}/api/auth/login`, { email, password })
    localStorage.setItem(TOKEN_KEY, res.data.access_token)
    setUser(res.data.user)
    return res.data.user
  }

  const register = async (name, email, password) => {
    const res = await axios.post(`${API}/api/auth/register`, { name, email, password })
    localStorage.setItem(TOKEN_KEY, res.data.access_token)
    setUser(res.data.user)
    return res.data.user
  }

  const logout = async () => {
    try {
      await axios.post(`${API}/api/auth/logout`)
    } catch {
      /* token may already be invalid */
    }
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
