/**
 * Axios API client configuration with token refresh
 */
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // 自動發送 cookies (httpOnly)
})

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
