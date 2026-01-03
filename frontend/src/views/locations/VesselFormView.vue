<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? 'Edit Vessel' : 'New Vessel' }}
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
                placeholder="Vessel Location Name"
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
                placeholder="VSL001"
              />
            </div>
          </div>
        </div>

        <!-- Vessel Identifiers (at least one required) -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-2">
            Vessel Identifiers <span class="text-red-500">*</span>
          </h2>
          <p class="text-sm text-gray-600 mb-4">At least one identifier is required</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- IMO Number -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">IMO Number</label>
              <input
                v-model="form.imo_number"
                type="text"
                maxlength="20"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="IMO1234567"
              />
            </div>

            <!-- MMSI -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">MMSI</label>
              <input
                v-model="form.vessel_mmsi"
                type="text"
                maxlength="9"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="123456789"
              />
            </div>

            <!-- National Registration ID -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">National Registration ID</label>
              <input
                v-model="form.vessel_national_id"
                type="text"
                maxlength="30"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="National ID"
              />
            </div>

            <!-- Internal Code -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Internal Vessel Code</label>
              <input
                v-model="form.vessel_internal_code"
                type="text"
                maxlength="20"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Internal Code"
              />
            </div>

            <!-- Call Sign -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Call Sign</label>
              <input
                v-model="form.call_sign"
                type="text"
                maxlength="20"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Call Sign"
              />
            </div>
          </div>

          <!-- Validation Error -->
          <p v-if="identifierError" class="mt-2 text-sm text-red-600">
            {{ identifierError }}
          </p>
        </div>

        <!-- Vessel Information -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Vessel Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Vessel Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Vessel Name</label>
              <input
                v-model="form.vessel_name"
                type="text"
                maxlength="100"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Vessel's Official Name"
              />
            </div>

            <!-- Vessel Flag -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Flag / Country</label>
              <input
                v-model="form.vessel_flag"
                type="text"
                maxlength="50"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Panama"
              />
            </div>

            <!-- Vessel Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Vessel Type</label>
              <input
                v-model="form.vessel_type"
                type="text"
                maxlength="50"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Research Vessel, Cargo Ship, etc."
              />
            </div>

            <!-- Vessel Owner -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Vessel Owner</label>
              <input
                v-model="form.vessel_owner"
                type="text"
                maxlength="100"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Owner Name"
              />
            </div>

            <!-- Owner Company (Legacy) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Owner Company (Legacy)</label>
              <input
                v-model="form.owner_company"
                type="text"
                maxlength="100"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
                placeholder="Company Name"
              />
            </div>
          </div>
        </div>

        <!-- Vessel Photo & Contact Person -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Photo & Contact</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Vessel Photo -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Vessel Photo</label>
              <div v-if="form.photo_url" class="mb-3">
                <img
                  :src="form.photo_url"
                  alt="Vessel Photo"
                  class="w-32 h-32 object-cover rounded-lg border"
                />
                <button
                  v-if="isEditMode"
                  type="button"
                  @click="handleDeletePhoto"
                  class="mt-2 text-sm text-red-600 hover:text-red-800"
                >
                  Remove Photo
                </button>
              </div>
              <input
                v-if="isEditMode"
                type="file"
                accept="image/*"
                @change="handlePhotoUpload"
                class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100"
              />
              <p v-if="!isEditMode" class="text-xs text-gray-500">Photo can be uploaded after creating the vessel</p>
              <p v-if="uploadingPhoto" class="mt-1 text-xs text-sky-600">Uploading...</p>
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

        <!-- Project Association -->
        <div class="border-b border-gray-200 pb-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Project Association</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Current Project -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Current Project</label>
              <select
                v-model="form.current_project_id"
                class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              >
                <option :value="null">None</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.code }} - {{ project.name }}
                </option>
              </select>
              <p class="mt-1 text-xs text-gray-500">Equipment deployed to this vessel will inherit this project</p>
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
            {{ locationStore.loading ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Vessel' }}
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
import { useProjectStore } from '@/stores/projects'
import { locationApi } from '@/api/locations'
import { usersApi } from '@/api/users'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { UserStaff } from '@/types'

const router = useRouter()
const route = useRoute()
const locationStore = useLocationStore()
const projectStore = useProjectStore()

const isEditMode = computed(() => !!route.params.id)
const locationId = computed(() => parseInt(route.params.id as string))

const form = ref({
  name: '',
  code: '',
  location_type: 'vessel' as const,
  imo_number: '',
  vessel_mmsi: '',
  vessel_national_id: '',
  vessel_internal_code: '',
  call_sign: '',
  vessel_name: '',
  vessel_flag: '',
  vessel_type: '',
  vessel_owner: '',
  owner_company: '',
  photo_url: '' as string | null,
  contact_user_id: null as number | null,  // 改用 User
  current_project_id: null as number | null,
  is_active: true,
})

const identifierError = ref('')
const projects = ref<any[]>([])
const staffUsers = ref<UserStaff[]>([])  // 改用 User staff
const uploadingPhoto = ref(false)

// Validate that at least one identifier is provided
function validateIdentifiers(): boolean {
  const identifiers = [
    form.value.imo_number,
    form.value.vessel_mmsi,
    form.value.vessel_national_id,
    form.value.vessel_internal_code,
    form.value.call_sign,
  ]

  if (!identifiers.some((id) => id && id.trim() !== '')) {
    identifierError.value = 'At least one vessel identifier is required'
    return false
  }

  identifierError.value = ''
  return true
}

async function handleSubmit() {
  // Validate identifiers
  if (!validateIdentifiers()) {
    return
  }

  try {
    // Clean form data: remove empty strings and null values
    const cleanedData: any = {}
    Object.entries(form.value).forEach(([key, value]) => {
      if (value === '' || value === null) {
        // Skip empty strings and null values
        return
      }
      cleanedData[key] = value
    })

    if (import.meta.env.DEV) console.log('Cleaned data to send:', cleanedData)

    if (isEditMode.value) {
      await locationStore.updateLocation(locationId.value, cleanedData)
      alert('Vessel updated successfully!')
    } else {
      await locationStore.createLocation(cleanedData)
      alert('Vessel created successfully!')
    }
    router.push('/locations')
  } catch (error: any) {
    console.error('Failed to save vessel:', error)
    console.error('Error response:', error.response?.data)

    // Display detailed error message
    const errorMsg = error.response?.data?.detail ||
                     JSON.stringify(error.response?.data) ||
                     'Failed to save vessel'
    alert(`Error: ${errorMsg}`)
  }
}

async function handlePhotoUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length || !isEditMode.value) return

  const file = input.files[0]
  uploadingPhoto.value = true

  try {
    const response = await locationApi.uploadPhoto(locationId.value, file)
    form.value.photo_url = response.data.url
    alert('Photo uploaded successfully!')
  } catch (error: any) {
    console.error('Failed to upload photo:', error)
    alert(error.response?.data?.detail || 'Failed to upload photo')
  } finally {
    uploadingPhoto.value = false
  }
}

async function handleDeletePhoto() {
  if (!isEditMode.value || !form.value.photo_url) return

  if (!confirm('Are you sure you want to delete this photo?')) return

  try {
    await locationApi.deletePhoto(locationId.value)
    form.value.photo_url = null
    alert('Photo deleted successfully!')
  } catch (error: any) {
    console.error('Failed to delete photo:', error)
    alert(error.response?.data?.detail || 'Failed to delete photo')
  }
}

onMounted(async () => {
  // Load projects for dropdown
  try {
    await projectStore.fetchProjects({ skip: 0, limit: 100, is_active: true })
    projects.value = projectStore.projects
  } catch (error) {
    console.error('Failed to load projects:', error)
  }

  // Load staff users for contact person dropdown (改用 User API)
  try {
    const response = await usersApi.getStaff()
    staffUsers.value = response.data
  } catch (error) {
    console.error('Failed to load staff users:', error)
  }

  // Load location data if editing
  if (isEditMode.value) {
    const location = await locationStore.fetchById(locationId.value)
    if (location) {
      form.value = {
        name: location.name,
        code: location.code || '',
        location_type: 'vessel',
        imo_number: location.imo_number || '',
        vessel_mmsi: location.vessel_mmsi || '',
        vessel_national_id: location.vessel_national_id || '',
        vessel_internal_code: location.vessel_internal_code || '',
        call_sign: location.call_sign || '',
        vessel_name: location.vessel_name || '',
        vessel_flag: location.vessel_flag || '',
        vessel_type: location.vessel_type || '',
        vessel_owner: location.vessel_owner || '',
        owner_company: location.owner_company || '',
        photo_url: location.photo_url || null,
        contact_user_id: location.contact_user_id || null,  // 改用 contact_user_id
        current_project_id: location.current_project_id || null,
        is_active: location.is_active,
      }
    }
  }
})
</script>
