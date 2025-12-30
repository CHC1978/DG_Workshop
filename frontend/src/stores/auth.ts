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
    // State
    const token = ref<string | null>(null)
    const tempToken = ref<string | null>(null)
    const user = ref<User | null>(null)
    const totpRequired = ref(false)

    // Getters
    const isAuthenticated = computed(() => !!token.value && !!user.value)
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
      tempToken.value = response.data.temp_token
      totpRequired.value = response.data.totp_required
      return response.data
    }

    async function loginStep2(credentials: LoginStep2Request) {
      const response = await authApi.loginStep2(credentials)
      token.value = response.data.access_token
      user.value = {
        id: response.data.user_id,
        username: response.data.username,
        role: response.data.role as any,
      } as User
      tempToken.value = null
      totpRequired.value = false

      // Fetch full user info
      await fetchCurrentUser()

      return response.data
    }

    async function fetchCurrentUser() {
      if (!token.value) return

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

    function logout() {
      token.value = null
      tempToken.value = null
      user.value = null
      totpRequired.value = false
    }

    return {
      // State
      token,
      tempToken,
      user,
      totpRequired,
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
      paths: ['token', 'user'],
    },
  }
)
