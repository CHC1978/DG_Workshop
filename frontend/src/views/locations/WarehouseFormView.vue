<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? 'Edit Warehouse' : 'New Warehouse' }}
        </h1>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="bg-white rounded-lg shadow p-6 space-y-6">
        <!-- Basic Information -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Display Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Warehouse Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Main Warehouse, Storage A, etc."
              />
            </div>

            <!-- Code -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Location Code</label>
              <input
                v-model="form.code"
                type="text"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="WH001"
              />
            </div>
          </div>
        </div>

        <!-- Address & Contact Information -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Address & Contact</h2>
          <div class="grid grid-cols-1 gap-4">
            <!-- Address -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Address</label>
              <textarea
                v-model="form.address"
                rows="2"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Full address of the warehouse"
              ></textarea>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <!-- Phone -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input
                v-model="form.phone"
                type="tel"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="+886-2-12345678"
              />
            </div>

            <!-- Email -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                v-model="form.email"
                type="email"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="warehouse@example.com"
              />
            </div>

            <!-- Contact Person (改用 User) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Contact Person</label>
              <select
                v-model="form.contact_user_id"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              >
                <option :value="null">None</option>
                <option v-for="user in staffUsers" :key="user.id" :value="user.id">
                  {{ user.full_name }}{{ user.department ? ` (${user.department})` : '' }}
                </option>
              </select>
              <p class="mt-1 text-xs text-gray-500">Select a user as contact person</p>
            </div>
          </div>
        </div>

        <!-- Status (Edit mode only) -->
        <div v-if="isEditMode">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Status</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Active Status</label>
              <select
                v-model="form.is_active"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              >
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="locationStore.error" class="rounded-md bg-red-50 p-4">
          <p class="text-sm text-red-800">{{ locationStore.error }}</p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-6 border-t border-gray-200">
          <AppButton variant="secondary" @click="router.back()">
            Cancel
          </AppButton>
          <AppButton type="submit" :disabled="locationStore.loading">
            {{ locationStore.loading ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Warehouse' }}
          </AppButton>
        </div>
      </form>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLocationStore } from '@/stores/locations'
import { usersApi } from '@/api/users'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { UserStaff } from '@/types'

const router = useRouter()
const route = useRoute()
const locationStore = useLocationStore()

const isEditMode = computed(() => !!route.params.id)
const locationId = computed(() => parseInt(route.params.id as string))

const form = ref({
  name: '',
  code: '',
  location_type: 'warehouse' as const,
  address: '',
  phone: '',
  email: '',
  contact_user_id: null as number | null,  // 改用 User
  is_active: true,
})

const staffUsers = ref<UserStaff[]>([])  // 改用 User staff

async function handleSubmit() {
  try {
    // Clean form data: remove empty strings
    const cleanedData: any = {}
    Object.entries(form.value).forEach(([key, value]) => {
      if (value === '' || value === null) {
        return
      }
      cleanedData[key] = value
    })

    if (isEditMode.value) {
      await locationStore.updateLocation(locationId.value, cleanedData)
      alert('Warehouse updated successfully!')
    } else {
      await locationStore.createLocation(cleanedData)
      alert('Warehouse created successfully!')
    }
    router.push('/locations')
  } catch (error) {
    console.error('Failed to save warehouse:', error)
  }
}

onMounted(async () => {
  // Load staff users for contact person dropdown (改用 User API)
  try {
    const response = await usersApi.getStaff()
    staffUsers.value = response.data
  } catch (error) {
    console.error('Failed to load staff users:', error)
  }

  if (isEditMode.value) {
    const location = await locationStore.fetchById(locationId.value)
    if (location) {
      form.value = {
        name: location.name,
        code: location.code || '',
        location_type: 'warehouse',
        address: location.address || '',
        phone: location.phone || '',
        email: location.email || '',
        contact_user_id: location.contact_user_id || null,  // 改用 contact_user_id
        is_active: location.is_active,
      }
    }
  }
})
</script>
