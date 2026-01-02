/**
 * Axios API client configuration with token refresh and CSRF protection
 */
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'

// CSRF token cookie 名稱
const CSRF_COOKIE_NAME = 'csrf_token'
const CSRF_HEADER_NAME = 'X-CSRF-Token'

// 需要 CSRF 保護的 HTTP 方法
const CSRF_PROTECTED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

// ==================== Security Audit Logging ====================

interface SecurityEvent {
  type: 'auth_failure' | 'token_refresh_failure' | 'permission_denied' | 'csrf_error' | 'suspicious_activity'
  timestamp: string
  url?: string
  method?: string
  statusCode?: number
  message?: string
  userAgent?: string
}

// Security event buffer for batch reporting
const securityEventBuffer: SecurityEvent[] = []
const MAX_BUFFER_SIZE = 10
const FLUSH_INTERVAL_MS = 60000  // 1 minute

/**
 * Log a security event
 */
function logSecurityEvent(event: Omit<SecurityEvent, 'timestamp' | 'userAgent'>): void {
  const fullEvent: SecurityEvent = {
    ...event,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
  }

  // Log to console in development
  if (import.meta.env.DEV) {
    console.warn('[Security Audit]', fullEvent)
  }

  // Add to buffer
  securityEventBuffer.push(fullEvent)

  // Flush if buffer is full
  if (securityEventBuffer.length >= MAX_BUFFER_SIZE) {
    flushSecurityEvents()
  }
}

/**
 * Flush security events to localStorage for persistence
 * In production, this could be sent to a security logging endpoint
 */
function flushSecurityEvents(): void {
  if (securityEventBuffer.length === 0) return

  try {
    // Get existing events
    const existingEvents = JSON.parse(localStorage.getItem('security_audit_log') || '[]')

    // Append new events (keep last 100)
    const allEvents = [...existingEvents, ...securityEventBuffer].slice(-100)

    localStorage.setItem('security_audit_log', JSON.stringify(allEvents))

    // Clear buffer
    securityEventBuffer.length = 0
  } catch (e) {
    console.error('[Security Audit] Failed to flush events:', e)
  }
}

// Periodic flush
setInterval(flushSecurityEvents, FLUSH_INTERVAL_MS)

// Flush on page unload
window.addEventListener('beforeunload', flushSecurityEvents)

/**
 * Track consecutive failures for suspicious activity detection
 */
const failureTracker = {
  authFailures: 0,
  tokenRefreshFailures: 0,
  permissionDenials: 0,
  lastReset: Date.now(),
}

const FAILURE_WINDOW_MS = 300000  // 5 minutes
const SUSPICIOUS_AUTH_THRESHOLD = 5
const SUSPICIOUS_403_THRESHOLD = 10

function resetFailureTrackerIfNeeded(): void {
  const now = Date.now()
  if (now - failureTracker.lastReset > FAILURE_WINDOW_MS) {
    failureTracker.authFailures = 0
    failureTracker.tokenRefreshFailures = 0
    failureTracker.permissionDenials = 0
    failureTracker.lastReset = now
  }
}

function trackAuthFailure(url?: string): void {
  resetFailureTrackerIfNeeded()
  failureTracker.authFailures++

  if (failureTracker.authFailures >= SUSPICIOUS_AUTH_THRESHOLD) {
    logSecurityEvent({
      type: 'suspicious_activity',
      url,
      message: `Detected ${failureTracker.authFailures} authentication failures in ${FAILURE_WINDOW_MS / 1000}s`,
    })
  }
}

function trackPermissionDenial(url?: string): void {
  resetFailureTrackerIfNeeded()
  failureTracker.permissionDenials++

  if (failureTracker.permissionDenials >= SUSPICIOUS_403_THRESHOLD) {
    logSecurityEvent({
      type: 'suspicious_activity',
      url,
      message: `Detected ${failureTracker.permissionDenials} permission denials in ${FAILURE_WINDOW_MS / 1000}s`,
    })
  }
}

// ==================== End Security Audit Logging ====================

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
    const url = originalRequest?.url || ''
    const method = originalRequest?.method?.toUpperCase() || 'UNKNOWN'
    const statusCode = error.response?.status

    // Check if this is a 401 error
    if (error.response?.status === 401) {
      // Skip refresh for auth endpoints (except /auth/me and /auth/sessions)
      const isAuthEndpoint = url.includes('/auth/')
      const isRefreshEndpoint = url.includes('/auth/refresh')
      const isLoginEndpoint = url.includes('/auth/login/')
      const is2FAEndpoint = url.includes('/auth/2fa/')
      const isProtectedAuthEndpoint = url === '/auth/me' || url === '/auth/sessions' || url.startsWith('/auth/sessions/')

      // Log auth failure for login attempts
      if (isLoginEndpoint || is2FAEndpoint) {
        logSecurityEvent({
          type: 'auth_failure',
          url,
          method,
          statusCode,
          message: 'Authentication failed',
        })
        trackAuthFailure(url)
      }

      // Don't try to refresh for login, 2FA, or refresh endpoints
      if ((isAuthEndpoint && !isProtectedAuthEndpoint) || isRefreshEndpoint) {
        return Promise.reject(error)
      }

      // Don't retry if already retried
      if (originalRequest._retry) {
        // Refresh failed, redirect to login
        logSecurityEvent({
          type: 'token_refresh_failure',
          url,
          method,
          statusCode,
          message: 'Token refresh failed after retry',
        })
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

        // Log token refresh failure
        logSecurityEvent({
          type: 'token_refresh_failure',
          url: '/auth/refresh',
          method: 'POST',
          statusCode: (refreshError as AxiosError).response?.status,
          message: 'Token refresh request failed',
        })

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
      const errorData = error.response.data as { detail?: string } | undefined
      const isCsrfError = errorData?.detail?.toLowerCase().includes('csrf')

      if (isCsrfError) {
        logSecurityEvent({
          type: 'csrf_error',
          url,
          method,
          statusCode,
          message: 'CSRF token verification failed',
        })
      } else {
        logSecurityEvent({
          type: 'permission_denied',
          url,
          method,
          statusCode,
          message: errorData?.detail || 'Permission denied',
        })
        trackPermissionDenial(url)
      }

      console.error('Permission denied:', error.response.data)
    }

    return Promise.reject(error)
  }
)

export default apiClient
