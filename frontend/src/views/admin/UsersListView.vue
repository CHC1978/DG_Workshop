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
                <select
                  @change="handleUserAction($event, user)"
                  class="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent cursor-pointer"
                >
                  <option value="">-- Select Action --</option>
                  <option value="view">View</option>
                  <option v-if="authStore.isAdmin || authStore.user?.id === user.id" value="edit">Edit</option>
                  <option v-if="authStore.isAdmin" value="reset_password">Reset Password</option>
                  <option v-if="authStore.isAdmin" value="reset_2fa">Reset 2FA</option>
                  <option v-if="authStore.isAdmin && !user.totp_enabled" value="enable_2fa">Enable 2FA</option>
                  <option v-if="authStore.isAdmin && user.totp_enabled" value="disable_2fa">Disable 2FA</option>
                  <option v-if="authStore.isAdmin && user.id !== authStore.user?.id" value="delete" class="text-red-600">Delete</option>
                </select>
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

    <!-- Enable 2FA Modal -->
    <div v-if="show2FAModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          Enable 2FA for {{ selected2FAUser?.full_name }}
        </h3>

        <!-- Step 1: Show QR Code -->
        <div v-if="setup2FAStep === 1">
          <p class="text-sm text-gray-600 mb-4">
            Scan this QR code with Google Authenticator or Microsoft Authenticator:
          </p>

          <div class="flex justify-center mb-4">
            <img v-if="qrCodeData" :src="qrCodeData" alt="2FA QR Code" class="w-48 h-48" />
            <div v-else class="w-48 h-48 bg-gray-100 flex items-center justify-center">
              <span class="text-gray-500">Loading...</span>
            </div>
          </div>

          <div v-if="totpSecret" class="mb-4 p-3 bg-gray-100 rounded-lg">
            <p class="text-xs text-gray-500 mb-1">Manual entry code:</p>
            <p class="font-mono text-sm break-all">{{ totpSecret }}</p>
          </div>

          <div v-if="backupCodes.length > 0" class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p class="text-xs text-yellow-800 font-semibold mb-2">Backup Codes (save these!):</p>
            <div class="grid grid-cols-2 gap-1">
              <span v-for="code in backupCodes" :key="code" class="font-mono text-xs">{{ code }}</span>
            </div>
          </div>

          <div class="flex space-x-3">
            <AppButton variant="ghost" @click="close2FAModal" class="flex-1">
              Cancel
            </AppButton>
            <AppButton variant="primary" @click="setup2FAStep = 2" class="flex-1">
              Next
            </AppButton>
          </div>
        </div>

        <!-- Step 2: Verify TOTP Code -->
        <div v-else-if="setup2FAStep === 2">
          <p class="text-sm text-gray-600 mb-4">
            Enter the 6-digit code from the authenticator app to confirm setup:
          </p>

          <div class="mb-4">
            <input
              v-model="verifyTotpCode"
              type="text"
              maxlength="6"
              placeholder="000000"
              class="w-full px-4 py-2 text-center text-2xl font-mono border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              @keyup.enter="confirmEnable2FA"
            />
          </div>

          <div v-if="enable2FAError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600">{{ enable2FAError }}</p>
          </div>

          <div class="flex space-x-3">
            <AppButton variant="ghost" @click="setup2FAStep = 1" class="flex-1">
              Back
            </AppButton>
            <AppButton
              variant="primary"
              @click="confirmEnable2FA"
              :loading="enabling2FA"
              class="flex-1"
            >
              Enable 2FA
            </AppButton>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
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

// 2FA Modal state
const show2FAModal = ref(false)
const selected2FAUser = ref<User | null>(null)
const setup2FAStep = ref(1)
const qrCodeData = ref('')
const totpSecret = ref('')
const backupCodes = ref<string[]>([])
const verifyTotpCode = ref('')
const enable2FAError = ref('')
const enabling2FA = ref(false)

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

function handleUserAction(event: Event, user: User) {
  const target = event.target as HTMLSelectElement
  const action = target.value

  if (!action) return

  // Execute action
  switch (action) {
    case 'view':
      viewUser(user.id)
      break
    case 'edit':
      editUser(user.id)
      break
    case 'reset_password':
      handleResetPassword(user)
      break
    case 'reset_2fa':
      handleReset2FA(user)
      break
    case 'enable_2fa':
      handleEnable2FA(user)
      break
    case 'disable_2fa':
      handleDisable2FA(user)
      break
    case 'delete':
      handleDelete(user)
      break
  }

  // Reset select to default
  target.value = ''
}

function viewUser(id: number) {
  router.push(`/admin/users/${id}`)
}

function editUser(id: number) {
  router.push(`/admin/users/${id}/edit`)
}

async function handleReset2FA(user: User) {
  const isSelf = user.id === authStore.user?.id
  const userName = isSelf ? 'your' : `${user.full_name}'s (@${user.username})`
  const pronoun = isSelf ? 'your' : 'their'

  const logoutWarning = '\n\n⚠️ The user will be logged out and must set up 2FA on next login.'

  if (!confirm(
    `Reset 2FA for ${userName}?\n\n` +
    `This will:\n` +
    `• Disable ${pronoun} current 2FA\n` +
    `• Clear ${pronoun} TOTP secret\n` +
    `• Force ${isSelf ? 'you' : 'them'} to set up 2FA again on next login` +
    logoutWarning
  )) {
    return
  }

  try {
    const result = await usersStore.reset2FA(user.id)

    if (isSelf) {
      // Current user reset their own 2FA - must logout
      uiStore.showNotification('success', '2FA reset successfully. You will be logged out.')
      // Wait a moment for notification to show
      setTimeout(async () => {
        await authStore.logout()
        router.push('/login')
      }, 1500)
    } else {
      uiStore.showNotification('success', `2FA reset successfully for ${user.full_name}. They must set up 2FA on next login.`)
      await usersStore.fetchList()
    }
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to reset 2FA')
  }
}

async function handleDisable2FA(user: User) {
  const isSelf = user.id === authStore.user?.id
  const userName = isSelf ? 'yourself' : user.full_name
  const pronoun = isSelf ? 'You' : 'They'

  if (!confirm(
    `Disable 2FA for ${userName}?\n\n` +
    `${pronoun} will no longer need 2FA to login.\n\n` +
    `Note: To enable 2FA again, use "Enable 2FA" from the Actions menu.`
  )) {
    return
  }

  try {
    await usersStore.toggle2FA(user.id, false)
    const message = isSelf
      ? '2FA disabled for your account. You can now login without 2FA.'
      : `2FA disabled for ${user.full_name}`
    uiStore.showNotification('success', message)
    await usersStore.fetchList()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to disable 2FA')
  }
}

async function handleEnable2FA(user: User) {
  try {
    // First try to directly enable 2FA (if user has existing secret)
    const result = await usersStore.toggle2FA(user.id, true)

    if (!result.needs_setup) {
      // User has existing secret, 2FA enabled directly
      uiStore.showNotification('success', `2FA enabled for ${user.full_name}`)
      await usersStore.fetchList()
      return
    }

    // User needs to set up 2FA - show QR code modal
    selected2FAUser.value = user
    setup2FAStep.value = 1
    qrCodeData.value = ''
    totpSecret.value = ''
    backupCodes.value = []
    verifyTotpCode.value = ''
    enable2FAError.value = ''
    enabling2FA.value = false

    // Show modal
    show2FAModal.value = true

    // Fetch QR code data
    const data = await usersStore.setup2FA(user.id)
    // Backend already returns complete data URL (data:image/png;base64,...)
    qrCodeData.value = data.qr_code
    totpSecret.value = data.secret
    backupCodes.value = data.backup_codes
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to enable 2FA')
    show2FAModal.value = false
  }
}

function close2FAModal() {
  show2FAModal.value = false
  selected2FAUser.value = null
  qrCodeData.value = ''
  totpSecret.value = ''
  backupCodes.value = []
  verifyTotpCode.value = ''
  enable2FAError.value = ''
}

async function confirmEnable2FA() {
  if (!selected2FAUser.value) return

  if (!verifyTotpCode.value || verifyTotpCode.value.length !== 6) {
    enable2FAError.value = 'Please enter a 6-digit code'
    return
  }

  enabling2FA.value = true
  enable2FAError.value = ''

  try {
    await usersStore.confirm2FA(selected2FAUser.value.id, verifyTotpCode.value)
    uiStore.showNotification('success', `2FA enabled successfully for ${selected2FAUser.value.full_name}`)
    close2FAModal()
    await usersStore.fetchList()
  } catch (error: any) {
    enable2FAError.value = error.response?.data?.detail || 'Invalid TOTP code. Please try again.'
  } finally {
    enabling2FA.value = false
  }
}

async function handleResetPassword(user: User) {
  const newPassword = prompt(
    `Reset password for ${user.full_name} (@${user.username})\n\nEnter new password (minimum 8 characters):`
  )

  if (!newPassword) {
    return
  }

  if (newPassword.length < 8) {
    uiStore.showNotification('error', 'Password must be at least 8 characters')
    return
  }

  // Confirm action
  if (!confirm(`Confirm password reset for ${user.full_name}?`)) {
    return
  }

  try {
    await usersStore.resetPassword(user.id, newPassword)
    uiStore.showNotification('success', `Password reset successfully for ${user.full_name}`)
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to reset password')
  }
}

async function handleDelete(user: User) {
  if (!confirm(`WARNING: Permanently delete user "${user.full_name}" (@${user.username})?\n\nThis action CANNOT be undone. All user data will be permanently removed.`)) {
    return
  }

  // Double confirmation for safety
  if (!confirm(`Are you absolutely sure? Type the username to confirm: ${user.username}`)) {
    return
  }

  try {
    await usersStore.remove(user.id)
    uiStore.showNotification('success', `User ${user.full_name} permanently deleted`)
    await usersStore.fetchList()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to delete user')
  }
}

onMounted(() => {
  usersStore.fetchList()
})
</script>
