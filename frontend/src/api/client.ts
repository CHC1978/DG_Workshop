/**
 * Axios API client configuration
 */
import axios, { type AxiosInstance } from 'axios'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // 自動發送 cookies (httpOnly)
})

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
          // Redirect to login page for protected endpoints
          console.log('401 on protected endpoint, redirecting to login')
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
