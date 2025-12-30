/**
 * Axios API client configuration
 */
import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from localStorage directly to avoid circular dependency
    const authData = localStorage.getItem('auth')
    if (authData) {
      try {
        const auth = JSON.parse(authData)

        // Don't add token to login endpoints
        if (config.url?.includes('/auth/login/step1')) {
          return config
        }

        // Use tempToken for 2FA setup endpoints, otherwise use token
        const token = config.url?.includes('/auth/2fa/')
          ? (auth.tempToken || auth.token)
          : auth.token

        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
      } catch (e) {
        console.error('Failed to parse auth data:', e)
      }
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      // Handle 401 Unauthorized
      if (error.response.status === 401) {
        // Don't auto-logout for 2FA setup endpoints - let component handle it
        const is2FAEndpoint = error.config?.url?.includes('/auth/2fa/')
        const isLoginEndpoint = error.config?.url?.includes('/auth/login/')

        if (!is2FAEndpoint && !isLoginEndpoint) {
          // Clear auth data and redirect only for protected endpoints
          console.log('401 on protected endpoint, logging out')
          localStorage.removeItem('auth')
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        } else {
          console.log('401 on auth endpoint, not auto-redirecting')
        }
      }

      // Handle 403 Forbidden
      if (error.response.status === 403) {
        console.error('Permission denied:', error.response.data)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
