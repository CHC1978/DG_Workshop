/**
 * Authentication store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginStep1Request, LoginStep2Request } from '@/types'

export const useAuthStore = defineStore(
  'auth',
  () => {
    // State (tokens are now in httpOnly cookies, not in state)
    const user = ref<User | null>(null)
    const totpRequired = ref(false)
    const needs2FASetup = ref(false)  // Flag for users who need to set up 2FA (after reset)

    // Getters
    const isAuthenticated = computed(() => !!user.value)
    const userRole = computed(() => user.value?.role || 'viewer')
    const isAdmin = computed(() => user.value?.role === 'admin')
    const isManager = computed(() =>
      ['admin', 'manager'].includes(user.value?.role || '')
    )
    const isOperator = computed(() =>
      ['admin', 'manager', 'operator'].includes(user.value?.role || '')
    )

    // Actions
    async function loginStep1(credentials: LoginStep1Request) {
      const response = await authApi.loginStep1(credentials)
      // Token is now in httpOnly cookie, just track TOTP requirement
      totpRequired.value = response.data.totp_required
      needs2FASetup.value = response.data.needs_2fa_setup || false

      // If login successful without 2FA and no setup required, fetch user info
      if (!response.data.totp_required && !response.data.needs_2fa_setup) {
        await fetchCurrentUser()
      }

      return response.data
    }

    async function loginStep2(credentials: LoginStep2Request) {
      const response = await authApi.loginStep2(credentials)
      // Token is now in httpOnly cookie, just update user info
      user.value = {
        id: response.data.user_id,
        username: response.data.username,
        role: response.data.role as any,
      } as User
      totpRequired.value = false

      // Fetch full user info
      await fetchCurrentUser()

      return response.data
    }

    async function fetchCurrentUser() {
      try {
        const response = await authApi.getCurrentUser()
        user.value = response.data
      } catch (error) {
        console.error('Failed to fetch user:', error)
        logout()
      }
    }

    async function setup2FA() {
      const response = await authApi.setup2FA()
      return response.data
    }

    async function confirm2FA(totpCode: string) {
      const response = await authApi.confirm2FA(totpCode)
      if (user.value) {
        user.value.totp_enabled = true
      }
      return response.data
    }

    async function logout() {
      try {
        // Call logout API to clear cookies
        await authApi.logout()
      } catch (error) {
        console.error('Logout API error:', error)
        // Continue with local cleanup even if API call fails
      }

      // Clear local state
      user.value = null
      totpRequired.value = false
    }

    return {
      // State
      user,
      totpRequired,
      needs2FASetup,
      // Getters
      isAuthenticated,
      userRole,
      isAdmin,
      isManager,
      isOperator,
      // Actions
      loginStep1,
      loginStep2,
      fetchCurrentUser,
      setup2FA,
      confirm2FA,
      logout,
    }
  },
  {
    persist: {
      paths: ['user'],  // Only persist user info, tokens are in httpOnly cookies
    },
  }
)
