<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Loading -->
      <div v-if="usersStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading user details...</p>
      </div>

      <!-- User Details -->
      <div v-else-if="user" class="space-y-6">
        <!-- Header -->
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ user.full_name }}</h1>
            <p class="mt-1 text-sm text-gray-500">@{{ user.username }}</p>
          </div>
          <div class="flex space-x-2">
            <AppButton
              v-if="authStore.isAdmin || authStore.user?.id === user.id"
              variant="secondary"
              @click="router.push(`/admin/users/${user.id}/edit`)"
            >
              Edit
            </AppButton>
            <AppButton
              v-if="authStore.user?.id === user.id"
              variant="secondary"
              @click="showPasswordModal = true"
            >
              Change Password
            </AppButton>
          </div>
        </div>

        <!-- Info Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Basic Info -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            <dl class="space-y-3">
              <div>
                <dt class="text-sm font-medium text-gray-500">Email</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ user.email }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Role</dt>
                <dd class="mt-1">
                  <span :class="roleBadgeClass(user.role)">
                    {{ roleLabel(user.role) }}
                  </span>
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Status</dt>
                <dd class="mt-1">
                  <span v-if="user.is_active" class="text-green-600 text-sm font-medium">
                    Active
                  </span>
                  <span v-else class="text-red-600 text-sm font-medium">
                    Inactive
                  </span>
                </dd>
              </div>
            </dl>
          </div>

          <!-- Security Info -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Security</h2>
            <dl class="space-y-3">
              <div>
                <dt class="text-sm font-medium text-gray-500">Two-Factor Authentication</dt>
                <dd class="mt-1">
                  <span v-if="user.totp_enabled" class="text-green-600 text-sm font-medium">
                    Enabled
                  </span>
                  <span v-else class="text-orange-600 text-sm font-medium">
                    Not Set Up
                  </span>
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Created</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ formatDate(user.created_at) }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ formatDate(user.updated_at) }}
                </dd>
              </div>
            </dl>

            <!-- Reset 2FA (Admin only) -->
            <div v-if="authStore.isAdmin && user.totp_enabled" class="mt-4 pt-4 border-t">
              <AppButton
                variant="danger"
                size="sm"
                @click="handleReset2FA"
              >
                Reset 2FA
              </AppButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Password Change Modal (Simple) -->
      <div
        v-if="showPasswordModal"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50"
        @click.self="showPasswordModal = false"
      >
        <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
          <form @submit.prevent="handlePasswordChange" class="space-y-4">
            <AppInput
              v-model="passwordData.old_password"
              type="password"
              label="Current Password"
              required
            />
            <AppInput
              v-model="passwordData.new_password"
              type="password"
              label="New Password"
              required
              hint="Minimum 8 characters"
            />
            <div v-if="passwordError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-600">{{ passwordError }}</p>
            </div>
            <div class="flex justify-end space-x-3">
              <AppButton type="button" variant="ghost" @click="showPasswordModal = false">
                Cancel
              </AppButton>
              <AppButton type="submit" variant="primary" :loading="passwordLoading">
                Update Password
              </AppButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useUiStore } from '@/stores/ui'
import MainLayout from '@/layouts/MainLayout.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const usersStore = useUsersStore()
const uiStore = useUiStore()

const userId = computed(() => parseInt(route.params.id as string))
const user = computed(() => usersStore.currentUser)

const showPasswordModal = ref(false)
const passwordLoading = ref(false)
const passwordError = ref('')

const passwordData = reactive({
  old_password: '',
  new_password: '',
})

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
  const base = 'px-3 py-1 text-sm font-semibold rounded'
  const variants: Record<string, string> = {
    admin: 'bg-red-100 text-red-800',
    manager: 'bg-blue-100 text-blue-800',
    operator: 'bg-green-100 text-green-800',
    viewer: 'bg-gray-100 text-gray-800',
  }
  return `${base} ${variants[role] || 'bg-gray-100 text-gray-800'}`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

async function handleReset2FA() {
  if (!user.value) return

  if (!confirm(`Reset 2FA for ${user.value.full_name}? They will need to set up 2FA again.`)) {
    return
  }

  try {
    await usersStore.reset2FA(user.value.id)
    uiStore.showNotification('success', '2FA reset successfully')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to reset 2FA')
  }
}

async function handlePasswordChange() {
  passwordError.value = ''

  if (passwordData.new_password.length < 8) {
    passwordError.value = 'Password must be at least 8 characters'
    return
  }

  passwordLoading.value = true

  try {
    await usersStore.updatePassword(userId.value, passwordData)
    uiStore.showNotification('success', 'Password updated successfully')
    showPasswordModal.value = false
    passwordData.old_password = ''
    passwordData.new_password = ''
  } catch (error: any) {
    passwordError.value = error.response?.data?.detail || 'Failed to update password'
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  usersStore.fetchById(userId.value)
})
</script>
