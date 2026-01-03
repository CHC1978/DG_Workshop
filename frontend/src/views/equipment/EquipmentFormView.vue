<template>
  <MainLayout>
    <div class="max-w-3xl mx-auto space-y-6">
      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEdit ? 'Edit Equipment' : 'Add New Equipment' }}
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          {{ isEdit ? 'Update equipment information' : 'Register new equipment in the system' }}
        </p>
      </div>

      <!-- Form -->
      <div class="bg-white rounded-lg shadow p-6">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Category, Equipment Type, Parent Selection -->
          <FormCategorySection
            v-model:category="formData.category"
            v-model:showParentSelector="showParentSelector"
            v-model:parentEquipmentId="formData.parent_equipment_id"
            :is-edit="isEdit"
            :available-parent-equipment="availableParentEquipment"
            :selected-parent="selectedParentEquipment"
            @category-change="handleCategoryChange"
            @parent-change="handleParentEquipmentChange"
          />

          <!-- Manufacturer -->
          <AppInput
            v-model="formData.manufacturer"
            label="Manufacturer"
            placeholder="e.g., Kongsberg, Trimble"
            required
            :error="errors.manufacturer"
          />

          <!-- Model -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Model <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.model"
              type="text"
              required
              class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
              placeholder="e.g., EM2040C, R12"
              @input="autoGenerateModelCode"
            />
          </div>

          <!-- Model Code -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Model Code <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.model_code"
              type="text"
              required
              maxlength="50"
              class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
              placeholder="e.g., EM2040C, SEAPATH330"
            />
            <p class="mt-1 text-sm text-gray-500">
              Used to generate Asset Code. Auto-filled from Model but can be customized.
            </p>
          </div>

          <!-- Serial Number -->
          <AppInput
            v-model="formData.serial_number"
            label="Serial Number"
            placeholder="Optional - used in Asset Code if provided"
          />

          <!-- Status (Edit mode only) -->
          <div v-if="isEdit">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Equipment Status
            </label>
            <select
              v-model="formData.status"
              class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
            >
              <option value="ordering">Ordering</option>
              <option value="in_stock">In Stock</option>
              <option value="deployed">Deployed</option>
              <option value="rented">Rented</option>
              <option value="repair">Repair</option>
              <option value="calibrating">Calibrating</option>
              <option value="disposed">Disposed</option>
              <option value="lost">Lost</option>
            </select>
            <p class="mt-1 text-sm text-gray-500">
              New equipment default to 'Ordering' status
            </p>
          </div>

          <!-- Purchase Date -->
          <AppInput
            v-model="formData.purchase_date"
            type="date"
            label="Purchase Date"
          />

          <!-- Location & Project Section -->
          <FormLocationProjectSection
            v-model="locationFormData"
            :locations="locations"
            :projects="projects"
            :suggested-project="suggestedProject"
            @location-change="handleLocationChange"
          />

          <!-- Assigned User (設備負責人) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Assigned User
            </label>
            <select
              v-model="formData.assigned_user_id"
              class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
            >
              <option :value="null">None</option>
              <option v-for="user in staffUsers" :key="user.id" :value="user.id">
                {{ user.full_name }}{{ user.department ? ` (${user.department})` : '' }}
              </option>
            </select>
            <p class="mt-1 text-sm text-gray-500">
              Assign a user responsible for this equipment
            </p>
          </div>

          <!-- Photo Upload (Available in both Create and Edit modes) -->
          <div class="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 class="text-sm font-semibold text-gray-700">Equipment Photo</h3>

            <!-- Photo Upload in Edit Mode -->
            <div v-if="isEdit && equipmentId">
              <FileUpload
                label="Equipment Photo"
                file-type="photo"
                :equipment-id="equipmentId"
                :current-file-url="formData.photo_url"
                accept="image/*"
                hint="Supported: JPG, PNG, GIF, WebP (Max 100MB)"
                @uploaded="handlePhotoUploaded"
                @deleted="handlePhotoDeleted"
              />
            </div>

            <!-- Photo Selection in Create Mode -->
            <div v-else>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Equipment Photo
              </label>
              <input
                ref="photoFileInput"
                type="file"
                accept="image/*"
                @change="handlePhotoFileSelected"
                class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100"
              />
              <p class="mt-1 text-sm text-gray-500">
                Photo will be uploaded after creating the equipment
              </p>
              <div v-if="pendingPhotoFile" class="mt-2 text-sm text-green-600">
                ✓ Selected: {{ pendingPhotoFile.name }}
              </div>
            </div>
          </div>

          <!-- Other File Uploads (Edit mode only) -->
          <div v-if="isEdit && equipmentId" class="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 class="text-sm font-semibold text-gray-700">Other Attachments</h3>

            <!-- Manual Upload -->
            <FileUpload
              label="Equipment Manual"
              file-type="manual"
              :equipment-id="equipmentId"
              :current-file-url="formData.manual_url"
              accept=".pdf,.doc,.docx"
              hint="Supported: PDF, DOC, DOCX (Max 100MB)"
              @uploaded="handleManualUploaded"
              @deleted="handleManualDeleted"
            />

            <!-- Calibration Report Upload -->
            <FileUpload
              label="Calibration Report"
              file-type="report"
              :equipment-id="equipmentId"
              :current-file-url="formData.calibration_report_url"
              accept=".pdf"
              hint="Supported: PDF (Max 100MB)"
              @uploaded="handleReportUploaded"
              @deleted="handleReportDeleted"
            />
          </div>

          <!-- Specifications -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Specifications
            </label>
            <textarea
              v-model="formData.specifications"
              rows="4"
              placeholder="Enter technical specifications..."
              class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
            ></textarea>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              General Notes
            </label>
            <textarea
              v-model="formData.notes"
              rows="3"
              placeholder="Enter any additional notes..."
              class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
            ></textarea>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600">{{ errorMessage }}</p>
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="p-4 bg-green-50 border border-green-200 rounded-lg">
            <p class="text-sm text-green-600">{{ successMessage }}</p>
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
              {{ isEdit ? 'Update Equipment' : 'Create Equipment' }}
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
import { useEquipmentStore } from '@/stores/equipment'
import { useLocationStore } from '@/stores/locations'
import { useProjectStore } from '@/stores/projects'
import { useUiStore } from '@/stores/ui'
import apiClient from '@/api/client'
import { usersApi } from '@/api/users'
import MainLayout from '@/layouts/MainLayout.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppButton from '@/components/common/AppButton.vue'
import FileUpload from '@/components/common/FileUpload.vue'
import FormCategorySection from '@/components/equipment/form/FormCategorySection.vue'
import FormLocationProjectSection from '@/components/equipment/form/FormLocationProjectSection.vue'
import type { Location, Project, UserStaff } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()
const locationStore = useLocationStore()
const projectStore = useProjectStore()
const uiStore = useUiStore()

const equipmentId = computed(() => {
  const id = route.params.id
  return id ? parseInt(id as string) : null
})

const isEdit = computed(() => !!equipmentId.value)

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const formData = reactive({
  category: '',
  manufacturer: '',
  model: '',
  model_code: '',
  serial_number: '',
  status: 'ordering',
  purchase_date: '',
  current_location_id: null as number | null,
  project_id: null as number | null,
  installation_type: null as string | null,
  installation_date: '',
  installation_notes: '',
  photo_url: '',
  manual_url: '',
  calibration_report_url: '',
  last_maintenance_date: '',
  next_maintenance_date: '',
  maintenance_notes: '',
  specifications: '',
  notes: '',
  parent_equipment_id: null as number | null,
  assigned_user_id: null as number | null,  // 設備負責人
})

// Location and Project data
const locations = ref<Location[]>([])
const projects = ref<Project[]>([])
const suggestedProject = ref<Project | null>(null)

// Staff users for assigned user dropdown
const staffUsers = ref<UserStaff[]>([])

// Parent Equipment data (for sub-components)
const showParentSelector = ref(false)
const parentEquipmentSelection = ref<number | null>(null)
const availableParentEquipment = ref<any[]>([])
const selectedParentEquipment = ref<any | null>(null)

// Photo file for create mode
const photoFileInput = ref<HTMLInputElement | null>(null)
const pendingPhotoFile = ref<File | null>(null)

// Computed: Location form data for FormLocationProjectSection
const locationFormData = computed({
  get: () => ({
    current_location_id: formData.current_location_id,
    project_id: formData.project_id,
    installation_type: formData.installation_type,
    installation_date: formData.installation_date,
    installation_notes: formData.installation_notes,
  }),
  set: (value: {
    current_location_id: number | null
    project_id: number | null
    installation_type: string | null
    installation_date: string
    installation_notes: string
  }) => {
    formData.current_location_id = value.current_location_id
    formData.project_id = value.project_id
    formData.installation_type = value.installation_type
    formData.installation_date = value.installation_date
    formData.installation_notes = value.installation_notes
  },
})

const errors = reactive({
  manufacturer: '',
  model: '',
})

function clearErrors() {
  errors.manufacturer = ''
  errors.model = ''
  errorMessage.value = ''
  successMessage.value = ''
}

// Auto-generate model code from model name
const previousModelValue = ref('')
function autoGenerateModelCode() {
  const currentCleanedModel = cleanModelName(formData.model)
  const previousCleanedModel = cleanModelName(previousModelValue.value)

  // Only auto-update if model_code was auto-generated (matches previous cleaned model) or is empty
  if (!formData.model_code || formData.model_code === previousCleanedModel) {
    formData.model_code = currentCleanedModel
  }

  previousModelValue.value = formData.model
}

function cleanModelName(model: string): string {
  if (!model) return ''
  // Remove special characters except - and _, uppercase, trim
  return model
    .replace(/[^a-zA-Z0-9\-_]/g, '')
    .toUpperCase()
    .substring(0, 20)
}

// Handle location change - suggest project if vessel selected
function handleLocationChange(locationId: number | null) {
  suggestedProject.value = null

  if (!locationId) return

  // Find selected location
  const selectedLocation = locations.value.find(loc => loc.id === locationId)

  if (!selectedLocation) return

  // If it's a vessel with a project, suggest the project
  if (selectedLocation.location_type === 'vessel' && selectedLocation.current_project_id) {
    const vesselProject = projects.value.find(p => p.id === selectedLocation.current_project_id)
    if (vesselProject) {
      suggestedProject.value = vesselProject
      // Auto-select the suggested project
      formData.project_id = vesselProject.id
    }
  }
}

// Category change handler
async function handleCategoryChange() {
  // Reload parent equipment list when category changes
  if (showParentSelector.value) {
    await loadParentEquipment()
  }
}

// Parent Equipment handling
function enableParentSelector() {
  showParentSelector.value = true
  formData.parent_equipment_id = null
  // Load parent equipment when enabling selector
  loadParentEquipment()
}

function disableParentSelector() {
  showParentSelector.value = false
  formData.parent_equipment_id = null
  selectedParentEquipment.value = null
}

async function handleParentEquipmentChange() {
  if (!formData.parent_equipment_id) {
    selectedParentEquipment.value = null
    return
  }

  // Find selected parent equipment
  const parent = availableParentEquipment.value.find(eq => eq.id === formData.parent_equipment_id)

  if (parent) {
    selectedParentEquipment.value = parent

    // Inherit category and manufacturer from parent
    formData.category = parent.category
    formData.manufacturer = parent.manufacturer

    // Inherit location and project if parent has them
    if (parent.current_location_id) {
      formData.current_location_id = parent.current_location_id
    }
    if (parent.project_id) {
      formData.project_id = parent.project_id
    }

    uiStore.showNotification('info', `Inherited category and manufacturer from parent equipment`)
  }
}

// Load locations, projects, and staff users
async function loadLocationsAndProjects() {
  try {
    // Load locations
    const locResponse = await locationStore.fetchLocations({ skip: 0, limit: 1000, is_active: true })
    locations.value = locationStore.locations

    // Load projects
    const projResponse = await projectStore.fetchProjects({ skip: 0, limit: 100, is_active: true })
    projects.value = projectStore.projects

    // Load staff users for assigned user dropdown
    const usersResponse = await usersApi.getStaff()
    staffUsers.value = usersResponse.data
  } catch (error) {
    console.error('Failed to load locations/projects/users:', error)
  }
}

// Load available parent equipment (for sub-component creation)
async function loadParentEquipment() {
  try {
    await equipmentStore.fetchList({ skip: 0, limit: 1000 })
    // Only show equipment that are NOT sub-components themselves
    // And if category is selected, only show equipment with the same category
    availableParentEquipment.value = equipmentStore.equipmentList.filter(
      eq => !eq.parent_equipment_id && eq.is_active &&
            (!formData.category || eq.category === formData.category)
    )
    if (import.meta.env.DEV) console.log(`Loaded ${availableParentEquipment.value.length} available parent equipment`)
  } catch (error) {
    console.error('Failed to load parent equipment:', error)
  }
}

// Photo file selection for create mode
function handlePhotoFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    pendingPhotoFile.value = file
  }
}

// Upload pending photo file
async function uploadPendingPhoto(equipmentId: number) {
  if (!pendingPhotoFile.value) return

  const formData = new FormData()
  formData.append('file', pendingPhotoFile.value)

  try {
    // 使用 apiClient，會自動處理 CSRF token 和 cookies 認證
    await apiClient.post(
      `/uploads/equipment/${equipmentId}/photo`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      }
    )

    uiStore.showNotification('success', 'Photo uploaded successfully')
  } catch (error: any) {
    console.error('Failed to upload photo:', error)
    uiStore.showNotification('error', 'Failed to upload photo')
  }
}

// File upload handlers
function handlePhotoUploaded(url: string) {
  formData.photo_url = url
  uiStore.showNotification('success', 'Photo uploaded successfully')
  loadEquipment() // Refresh equipment data
}

function handlePhotoDeleted() {
  formData.photo_url = ''
  uiStore.showNotification('success', 'Photo deleted successfully')
  loadEquipment()
}

function handleManualUploaded(url: string) {
  formData.manual_url = url
  uiStore.showNotification('success', 'Manual uploaded successfully')
  loadEquipment()
}

function handleManualDeleted() {
  formData.manual_url = ''
  uiStore.showNotification('success', 'Manual deleted successfully')
  loadEquipment()
}

function handleReportUploaded(url: string) {
  formData.calibration_report_url = url
  uiStore.showNotification('success', 'Report uploaded successfully')
  loadEquipment()
}

function handleReportDeleted() {
  formData.calibration_report_url = ''
  uiStore.showNotification('success', 'Report deleted successfully')
  loadEquipment()
}

async function loadEquipment() {
  if (!equipmentId.value) return

  try {
    const equipment = await equipmentStore.fetchById(equipmentId.value)
    formData.category = equipment.category
    formData.manufacturer = equipment.manufacturer
    formData.model = equipment.model
    formData.model_code = equipment.model_code || ''
    formData.serial_number = equipment.serial_number || ''
    formData.status = equipment.status || 'ordering'
    formData.purchase_date = equipment.purchase_date || ''
    formData.current_location_id = equipment.current_location_id || null
    formData.project_id = equipment.project_id || null
    formData.installation_type = equipment.installation_type || null
    formData.installation_date = equipment.installation_date || ''
    formData.installation_notes = equipment.installation_notes || ''
    formData.photo_url = equipment.photo_url || ''
    formData.manual_url = equipment.manual_url || ''
    formData.calibration_report_url = equipment.calibration_report_url || ''
    formData.last_maintenance_date = equipment.last_maintenance_date || ''
    formData.next_maintenance_date = equipment.next_maintenance_date || ''
    formData.maintenance_notes = equipment.maintenance_notes || ''
    formData.specifications = equipment.specifications || ''
    formData.notes = equipment.notes || ''
    formData.assigned_user_id = equipment.assigned_user_id || null  // 設備負責人
  } catch (error: any) {
    console.error('Failed to load equipment:', error)
    errorMessage.value = error.response?.data?.detail || 'Failed to load equipment'
  }
}

async function handleSubmit() {
  clearErrors()

  // Validate
  if (!formData.category) {
    errorMessage.value = 'Please select a category'
    return
  }
  if (!formData.manufacturer) {
    errors.manufacturer = 'Manufacturer is required'
    return
  }
  if (!formData.model) {
    errors.model = 'Model is required'
    return
  }

  loading.value = true

  try {
    const data = {
      category: formData.category,
      manufacturer: formData.manufacturer,
      model: formData.model,
      model_code: formData.model_code || undefined,
      serial_number: formData.serial_number || undefined,
      status: isEdit.value ? formData.status : undefined,
      purchase_date: formData.purchase_date || undefined,
      current_location_id: formData.current_location_id || undefined,
      project_id: formData.project_id || undefined,
      installation_type: formData.installation_type || undefined,
      installation_date: formData.installation_date || undefined,
      installation_notes: formData.installation_notes || undefined,
      photo_url: formData.photo_url || undefined,
      manual_url: formData.manual_url || undefined,
      calibration_report_url: formData.calibration_report_url || undefined,
      // Maintenance records are now managed through Equipment Detail > Status Actions
      // last_maintenance_date, next_maintenance_date, and maintenance_notes are excluded
      specifications: formData.specifications || undefined,
      notes: formData.notes || undefined,
      parent_equipment_id: formData.parent_equipment_id || undefined,
      assigned_user_id: formData.assigned_user_id || undefined,  // 設備負責人
    }

    if (isEdit.value) {
      // Update equipment
      await equipmentStore.update(equipmentId.value!, data)
      uiStore.showNotification('success', 'Equipment updated successfully')
      router.push(`/equipment/${equipmentId.value}`)
    } else {
      // Create equipment
      const newEquipment = await equipmentStore.create(data)
      successMessage.value = `Equipment created successfully! Asset Code: ${newEquipment.asset_code}`
      uiStore.showNotification('success', `Equipment created: ${newEquipment.asset_code}`)

      // Upload pending photo if exists
      if (pendingPhotoFile.value) {
        await uploadPendingPhoto(newEquipment.id)
      }

      // Redirect after 1 second
      setTimeout(() => {
        router.push(`/equipment/${newEquipment.id}`)
      }, 1000)
    }
  } catch (error: any) {
    console.error('Failed to save equipment:', error)
    errorMessage.value = error.response?.data?.detail || 'Failed to save equipment'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // Load locations and projects first
  await loadLocationsAndProjects()

  // Load parent equipment (for sub-component creation)
  if (!isEdit.value) {
    await loadParentEquipment()

    // Check if parent_id is provided in URL query
    const parentId = route.query.parent_id
    if (parentId) {
      showParentSelector.value = true
      parentEquipmentSelection.value = 0
      formData.parent_equipment_id = parseInt(parentId as string)
      await handleParentEquipmentChange()
    }
  }

  // Then load equipment if editing
  if (isEdit.value) {
    await loadEquipment()
    // Trigger location change to check for suggested project
    if (formData.current_location_id) {
      handleLocationChange()
    }
  }
})
</script>
