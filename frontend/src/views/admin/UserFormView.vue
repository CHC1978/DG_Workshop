<template>
  <MainLayout>
    <div class="max-w-2xl mx-auto space-y-6">
      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEdit ? 'Edit User' : 'Create New User' }}
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          {{ isEdit ? 'Update user information' : 'Add a new user to the system' }}
        </p>
      </div>

      <!-- Form -->
      <div class="bg-white rounded-lg shadow p-6">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Username (only for new user) -->
          <AppInput
            v-if="!isEdit"
            v-model="formData.username"
            label="Username"
            placeholder="Enter username"
            required
            :error="errors.username"
          />

          <!-- Full Name -->
          <AppInput
            v-model="formData.full_name"
            label="Full Name"
            placeholder="Enter full name"
            required
            :error="errors.full_name"
          />

          <!-- Email -->
          <AppInput
            v-model="formData.email"
            type="email"
            label="Email"
            placeholder="Enter email address"
            required
            :error="errors.email"
          />

          <!-- Password (only for new user) -->
          <AppInput
            v-if="!isEdit"
            v-model="formData.password"
            type="password"
            label="Password"
            placeholder="Minimum 8 characters"
            required
            :error="errors.password"
            hint="Minimum 8 characters"
          />

          <!-- Role -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Role <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.role"
              required
              :disabled="!authStore.isAdmin"
              class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
            >
              <option value="viewer">Viewer</option>
              <option value="operator">Operator</option>
              <option value="manager">Manager</option>
              <option value="admin">Administrator</option>
            </select>
            <p v-if="!authStore.isAdmin" class="mt-1 text-sm text-gray-500">
              Only administrators can change user roles
            </p>
          </div>

          <!-- Active Status (only for edit and admin) -->
          <div v-if="isEdit && authStore.isAdmin" class="flex items-center">
            <input
              v-model="formData.is_active"
              type="checkbox"
              id="is_active"
              class="h-4 w-4 text-sky-600 focus:ring-sky-500 border-gray-300 rounded"
            />
            <label for="is_active" class="ml-2 block text-sm text-gray-900">
              Account is active
            </label>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600">{{ errorMessage }}</p>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3">
            <AppButton
              type="button"
              variant="ghost"
              @click="router.back()"
            >
              Cancel
            </AppButton>
            <AppButton
              type="submit"
              variant="primary"
              :loading="loading"
            >
              {{ isEdit ? 'Update User' : 'Create User' }}
            </AppButton>
          </div>
        </form>
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

const userId = computed(() => {
  const id = route.params.id
  return id ? parseInt(id as string) : null
})

const isEdit = computed(() => !!userId.value)

const loading = ref(false)
const errorMessage = ref('')

const formData = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  role: 'viewer' as 'admin' | 'manager' | 'operator' | 'viewer',
  is_active: true,
})

const errors = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
})

function clearErrors() {
  errors.username = ''
  errors.email = ''
  errors.full_name = ''
  errors.password = ''
  errorMessage.value = ''
}

async function loadUser() {
  if (!userId.value) return

  try {
    const user = await usersStore.fetchById(userId.value)
    formData.email = user.email
    formData.full_name = user.full_name
    formData.role = user.role as any
    formData.is_active = user.is_active
  } catch (error: any) {
    console.error('Failed to load user:', error)
    errorMessage.value = error.response?.data?.detail || 'Failed to load user'
  }
}

async function handleSubmit() {
  clearErrors()

  // Validate
  if (!isEdit.value && !formData.username) {
    errors.username = 'Username is required'
    return
  }
  if (!formData.email) {
    errors.email = 'Email is required'
    return
  }
  if (!formData.full_name) {
    errors.full_name = 'Full name is required'
    return
  }
  if (!isEdit.value && formData.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    return
  }

  loading.value = true

  try {
    if (isEdit.value) {
      // Update user
      await usersStore.update(userId.value!, {
        email: formData.email,
        full_name: formData.full_name,
        role: formData.role,
        is_active: formData.is_active,
      })
      uiStore.showNotification('success', 'User updated successfully')
      router.push('/admin/users')
    } else {
      // Create user
      await usersStore.create({
        username: formData.username,
        email: formData.email,
        full_name: formData.full_name,
        password: formData.password,
        role: formData.role,
      })
      uiStore.showNotification('success', 'User created successfully')
      router.push('/admin/users')
    }
  } catch (error: any) {
    console.error('Failed to save user:', error)
    errorMessage.value = error.response?.data?.detail || 'Failed to save user'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (isEdit.value) {
    loadUser()
  }
})
</script>
