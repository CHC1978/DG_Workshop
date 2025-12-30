<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-gray-900">User Management</h1>
        <AppButton
          v-if="authStore.isAdmin"
          variant="primary"
          @click="router.push('/admin/users/new')"
        >
          + Add User
        </AppButton>
      </div>

      <!-- Users Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div v-if="usersStore.loading" class="text-center py-12">
          <p class="text-gray-500">Loading users...</p>
        </div>

        <div v-else-if="usersStore.usersList.length === 0" class="text-center py-12">
          <p class="text-gray-500">No users found</p>
        </div>

        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                2FA
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in usersStore.usersList" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ user.full_name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      @{{ user.username }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ user.email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="roleBadgeClass(user.role)">
                  {{ roleLabel(user.role) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="user.totp_enabled" class="text-green-600 text-sm">Enabled</span>
                <span v-else class="text-gray-400 text-sm">Disabled</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="user.is_active" class="text-green-600 text-sm">Active</span>
                <span v-else class="text-red-600 text-sm">Inactive</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex space-x-2">
                  <button
                    @click="viewUser(user.id)"
                    class="text-sky-600 hover:text-sky-900"
                  >
                    View
                  </button>
                  <button
                    v-if="authStore.isAdmin || authStore.user?.id === user.id"
                    @click="editUser(user.id)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    Edit
                  </button>
                  <button
                    v-if="authStore.isAdmin && user.totp_enabled"
                    @click="handleReset2FA(user)"
                    class="text-orange-600 hover:text-orange-900"
                  >
                    Reset 2FA
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="usersStore.total > 0" class="text-center text-sm text-gray-600">
        Showing {{ usersStore.usersList.length }} of {{ usersStore.total }} users
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useUiStore } from '@/stores/ui'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { User } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const usersStore = useUsersStore()
const uiStore = useUiStore()

function roleLabel(role: string): string {
  const labels: Record<string, string> = {
    admin: 'Administrator',
    manager: 'Manager',
    operator: 'Operator',
    viewer: 'Viewer',
  }
  return labels[role] || role
}

function roleBadgeClass(role: string): string {
  const base = 'px-2 py-1 text-xs font-semibold rounded'
  const variants: Record<string, string> = {
    admin: 'bg-red-100 text-red-800',
    manager: 'bg-blue-100 text-blue-800',
    operator: 'bg-green-100 text-green-800',
    viewer: 'bg-gray-100 text-gray-800',
  }
  return `${base} ${variants[role] || 'bg-gray-100 text-gray-800'}`
}

function viewUser(id: number) {
  router.push(`/admin/users/${id}`)
}

function editUser(id: number) {
  router.push(`/admin/users/${id}/edit`)
}

async function handleReset2FA(user: User) {
  if (!confirm(`Reset 2FA for ${user.full_name}? They will need to set up 2FA again on next login.`)) {
    return
  }

  try {
    await usersStore.reset2FA(user.id)
    uiStore.showNotification('success', `2FA reset for ${user.full_name}`)
    await usersStore.fetchList()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to reset 2FA')
  }
}

onMounted(() => {
  usersStore.fetchList()
})
</script>
