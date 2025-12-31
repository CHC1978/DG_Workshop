<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? 'Edit Person Location' : 'New Person Location' }}
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
                Display Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Person Location Name"
              />
              <p class="mt-1 text-xs text-gray-500">How this location will appear in the system</p>
            </div>

            <!-- Code -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Location Code</label>
              <input
                v-model="form.code"
                type="text"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="PER001"
              />
            </div>
          </div>
        </div>

        <!-- Person Information -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Person Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Person Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Person Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.person_name"
                type="text"
                required
                maxlength="100"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="John Doe"
              />
            </div>

            <!-- Employee ID -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Employee ID</label>
              <input
                v-model="form.employee_id"
                type="text"
                maxlength="30"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="EMP123456"
              />
            </div>

            <!-- Department -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <input
                v-model="form.department"
                type="text"
                maxlength="100"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Engineering, Operations, etc."
              />
            </div>

            <!-- Contact Information -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Contact Information</label>
              <input
                v-model="form.person_contact"
                type="text"
                maxlength="100"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Email, Phone, etc."
              />
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
            {{ locationStore.loading ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Person Location' }}
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
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const route = useRoute()
const locationStore = useLocationStore()

const isEditMode = computed(() => !!route.params.id)
const locationId = computed(() => parseInt(route.params.id as string))

const form = ref({
  name: '',
  code: '',
  location_type: 'person' as const,
  person_name: '',
  employee_id: '',
  department: '',
  person_contact: '',
  is_active: true,
})

async function handleSubmit() {
  try {
    // Clean form data: remove empty strings
    const cleanedData: any = {}
    Object.entries(form.value).forEach(([key, value]) => {
      if (value === '') {
        return
      }
      cleanedData[key] = value
    })

    if (isEditMode.value) {
      await locationStore.updateLocation(locationId.value, cleanedData)
      alert('Person location updated successfully!')
    } else {
      await locationStore.createLocation(cleanedData)
      alert('Person location created successfully!')
    }
    router.push('/locations')
  } catch (error) {
    console.error('Failed to save person location:', error)
  }
}

onMounted(async () => {
  if (isEditMode.value) {
    const location = await locationStore.fetchById(locationId.value)
    if (location) {
      form.value = {
        name: location.name,
        code: location.code || '',
        location_type: 'person',
        person_name: location.person_name || '',
        employee_id: location.employee_id || '',
        department: location.department || '',
        person_contact: location.person_contact || '',
        is_active: location.is_active,
      }
    }
  }
})
</script>
