/**
 * Users API
 */
import apiClient from './client'
import type { User } from '@/types'

export interface UserListResponse {
  users: User[]
  total: number
}

export interface UserCreateRequest {
  username: string
  email: string
  full_name: string
  password: string
  role: 'admin' | 'manager' | 'operator' | 'viewer'
}

export interface UserUpdateRequest {
  email?: string
  full_name?: string
  role?: 'admin' | 'manager' | 'operator' | 'viewer'
  is_active?: boolean
}

export interface UserPasswordUpdateRequest {
  old_password: string
  new_password: string
}

export const usersApi = {
  /**
   * List users
   */
  list(skip = 0, limit = 100) {
    return apiClient.get<UserListResponse>('/users', {
      params: { skip, limit },
    })
  },

  /**
   * Get user by ID
   */
  get(id: number) {
    return apiClient.get<User>(`/users/${id}`)
  },

  /**
   * Create user (Admin only)
   */
  create(data: UserCreateRequest) {
    return apiClient.post<User>('/users', data)
  },

  /**
   * Update user
   */
  update(id: number, data: UserUpdateRequest) {
    return apiClient.put<User>(`/users/${id}`, data)
  },

  /**
   * Delete user (Admin only)
   */
  delete(id: number) {
    return apiClient.delete(`/users/${id}`)
  },

  /**
   * Update password
   */
  updatePassword(id: number, data: UserPasswordUpdateRequest) {
    return apiClient.post(`/users/${id}/password`, data)
  },

  /**
   * Reset 2FA (Admin only)
   */
  reset2FA(id: number) {
    return apiClient.post(`/users/${id}/reset-2fa`)
  },

  /**
   * Toggle 2FA (Admin only)
   */
  toggle2FA(id: number, enabled: boolean) {
    return apiClient.put(`/users/${id}/toggle-2fa`, { enabled })
  },

  /**
   * Reset user password (Admin only)
   */
  resetPassword(id: number, newPassword: string) {
    return apiClient.post(`/users/${id}/reset-password`, { new_password: newPassword })
  },
}
