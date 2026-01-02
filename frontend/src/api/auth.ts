/**
 * Authentication API
 */
import apiClient from './client'
import type {
  LoginStep1Request,
  LoginStep1Response,
  LoginStep2Request,
  LoginStep2Response,
  Setup2FAResponse,
  User,
  SessionInfo,
  SessionsResponse,
} from '@/types'

export const authApi = {
  /**
   * Step 1: Login with username and password
   */
  loginStep1(credentials: LoginStep1Request) {
    return apiClient.post<LoginStep1Response>('/auth/login/step1', credentials)
  },

  /**
   * Step 2: Login with TOTP code
   */
  loginStep2(credentials: LoginStep2Request) {
    return apiClient.post<LoginStep2Response>('/auth/login/step2', credentials)
  },

  /**
   * Get current user info
   */
  getCurrentUser() {
    return apiClient.get<User>('/auth/me')
  },

  /**
   * Setup 2FA
   */
  setup2FA() {
    return apiClient.post<Setup2FAResponse>('/auth/2fa/setup')
  },

  /**
   * Confirm 2FA setup
   */
  confirm2FA(totpCode: string) {
    return apiClient.post('/auth/2fa/confirm', { totp_code: totpCode })
  },

  /**
   * Disable 2FA
   */
  disable2FA(totpCode: string) {
    return apiClient.post('/auth/2fa/disable', { totp_code: totpCode })
  },

  /**
   * Logout (clear httpOnly cookies)
   */
  logout() {
    return apiClient.post('/auth/logout')
  },

  /**
   * Logout from all devices
   */
  logoutAll() {
    return apiClient.post('/auth/logout', null, {
      params: { logout_all: true }
    })
  },

  /**
   * Refresh access token
   */
  refreshToken() {
    return apiClient.post('/auth/refresh')
  },

  /**
   * Get all active sessions
   */
  getSessions() {
    return apiClient.get<SessionsResponse>('/auth/sessions')
  },

  /**
   * Revoke a specific session
   */
  revokeSession(sessionId: number) {
    return apiClient.delete(`/auth/sessions/${sessionId}`)
  },
}
