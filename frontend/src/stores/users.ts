/**
 * Users store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usersApi } from '@/api/users'
import type { User, UserCreateRequest, UserUpdateRequest, PasswordUpdateRequest } from '@/types'

export const useUsersStore = defineStore('users', () => {
  // State
  const usersList = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const total = ref(0)
  const loading = ref(false)

  // Actions
  async function fetchList(skip = 0, limit = 100) {
    loading.value = true
    try {
      const response = await usersApi.list(skip, limit)
      usersList.value = response.data.users
      total.value = response.data.total
    } catch (error) {
      console.error('Failed to fetch users list:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchById(id: number) {
    loading.value = true
    try {
      const response = await usersApi.get(id)
      currentUser.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch user:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function create(data: UserCreateRequest) {
    loading.value = true
    try {
      const response = await usersApi.create(data)
      usersList.value.unshift(response.data)
      total.value++
      return response.data
    } catch (error) {
      console.error('Failed to create user:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function update(id: number, data: UserUpdateRequest) {
    loading.value = true
    try {
      const response = await usersApi.update(id, data)
      const index = usersList.value.findIndex((u) => u.id === id)
      if (index !== -1) {
        usersList.value[index] = response.data
      }
      if (currentUser.value?.id === id) {
        currentUser.value = response.data
      }
      return response.data
    } catch (error) {
      console.error('Failed to update user:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    loading.value = true
    try {
      await usersApi.delete(id)
      usersList.value = usersList.value.filter((u) => u.id !== id)
      total.value--
    } catch (error) {
      console.error('Failed to delete user:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updatePassword(id: number, data: PasswordUpdateRequest) {
    loading.value = true
    try {
      await usersApi.updatePassword(id, data)
    } catch (error) {
      console.error('Failed to update password:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function reset2FA(id: number) {
    loading.value = true
    try {
      const response = await usersApi.reset2FA(id)
      // Return response data for frontend to handle logout
      return response.data
    } catch (error) {
      console.error('Failed to reset 2FA:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function toggle2FA(id: number, enabled: boolean) {
    loading.value = true
    try {
      const response = await usersApi.toggle2FA(id, enabled)
      // Refresh user data in list if 2FA was actually toggled
      if (!response.data.needs_setup) {
        const index = usersList.value.findIndex((u) => u.id === id)
        if (index !== -1) {
          const userResponse = await usersApi.get(id)
          usersList.value[index] = userResponse.data
        }
      }
      return response.data
    } catch (error) {
      console.error('Failed to toggle 2FA:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function resetPassword(id: number, newPassword: string) {
    loading.value = true
    try {
      await usersApi.resetPassword(id, newPassword)
    } catch (error) {
      console.error('Failed to reset password:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function setup2FA(id: number) {
    loading.value = true
    try {
      const response = await usersApi.setup2FA(id)
      return response.data
    } catch (error) {
      console.error('Failed to setup 2FA:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function confirm2FA(id: number, totpCode: string) {
    loading.value = true
    try {
      const response = await usersApi.confirm2FA(id, totpCode)
      // Refresh user data in list
      const index = usersList.value.findIndex((u) => u.id === id)
      if (index !== -1) {
        const userResponse = await usersApi.get(id)
        usersList.value[index] = userResponse.data
      }
      return response.data
    } catch (error) {
      console.error('Failed to confirm 2FA:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function clearCurrent() {
    currentUser.value = null
  }

  return {
    // State
    usersList,
    currentUser,
    total,
    loading,
    // Actions
    fetchList,
    fetchById,
    create,
    update,
    remove,
    updatePassword,
    reset2FA,
    toggle2FA,
    resetPassword,
    setup2FA,
    confirm2FA,
    clearCurrent,
  }
})
