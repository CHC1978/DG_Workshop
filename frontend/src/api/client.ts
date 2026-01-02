/**
 * Axios API client configuration with token refresh and CSRF protection
 */
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'

// CSRF token cookie 名稱
const CSRF_COOKIE_NAME = 'csrf_token'
const CSRF_HEADER_NAME = 'X-CSRF-Token'

// 需要 CSRF 保護的 HTTP 方法
const CSRF_PROTECTED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

/**
 * 從 cookie 讀取 CSRF token
 */
function getCsrfToken(): string | null {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === CSRF_COOKIE_NAME) {
      return decodeURIComponent(value)
    }
  }
  return null
}

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // 自動發送 cookies (httpOnly)
})

// Request interceptor: 自動附加 CSRF token
apiClient.interceptors.request.use(
  (config) => {
    const method = config.method?.toUpperCase() || 'GET'

    // 對需要保護的方法附加 CSRF token
    if (CSRF_PROTECTED_METHODS.includes(method)) {
      const csrfToken = getCsrfToken()
      if (csrfToken) {
        config.headers[CSRF_HEADER_NAME] = csrfToken
      }
    }

    return config
  },
  (error) => Promise.reject(error)
)

// Flag to prevent multiple refresh attempts
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (error: unknown) => void
}> = []

const processQueue = (error: unknown = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve()
    }
  })
  failedQueue = []
}

// Response interceptor with token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Check if this is a 401 error
    if (error.response?.status === 401) {
      // Skip refresh for auth endpoints (except /auth/me and /auth/sessions)
      const url = originalRequest?.url || ''
      const isAuthEndpoint = url.includes('/auth/')
      const isRefreshEndpoint = url.includes('/auth/refresh')
      const isLoginEndpoint = url.includes('/auth/login/')
      const is2FAEndpoint = url.includes('/auth/2fa/')
      const isProtectedAuthEndpoint = url === '/auth/me' || url === '/auth/sessions' || url.startsWith('/auth/sessions/')

      // Don't try to refresh for login, 2FA, or refresh endpoints
      if ((isAuthEndpoint && !isProtectedAuthEndpoint) || isRefreshEndpoint) {
        return Promise.reject(error)
      }

      // Don't retry if already retried
      if (originalRequest._retry) {
        // Refresh failed, redirect to login
        console.log('Token refresh failed, redirecting to login')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }

      // If refresh is already in progress, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => apiClient(originalRequest))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // Attempt to refresh the token
        await apiClient.post('/auth/refresh')
        processQueue()

        // Retry the original request
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError)

        // Refresh failed, redirect to login
        console.log('Token refresh failed, redirecting to login')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }

        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.error('Permission denied:', error.response.data)
    }

    return Promise.reject(error)
  }
)

export default apiClient
