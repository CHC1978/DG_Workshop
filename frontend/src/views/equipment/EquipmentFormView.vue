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
          <!-- Category -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Category <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.category"
              required
              class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
            >
              <option value="">Select category...</option>
              <option value="mbes">MBES - Multibeam Echosounder</option>
              <option value="gnss">GNSS - Receiver</option>
              <option value="svp">SVP - Sound Velocity Profiler</option>
              <option value="sbp">SBP - Sub-bottom Profiler</option>
              <option value="usbl">USBL - Ultra-Short Baseline</option>
              <option value="rov">ROV - Remotely Operated Vehicle</option>
              <option value="ins">INS - Inertial Navigation System</option>
              <option value="magnetometer">Magnetometer</option>
              <option value="other">Other</option>
            </select>
          </div>

          <!-- Manufacturer -->
          <AppInput
            v-model="formData.manufacturer"
            label="Manufacturer"
            placeholder="e.g., Kongsberg, Trimble"
            required
            :error="errors.manufacturer"
          />

          <!-- Model -->
          <AppInput
            v-model="formData.model"
            label="Model"
            placeholder="e.g., EM2040C, R12"
            required
            :error="errors.model"
          />

          <!-- Serial Number -->
          <AppInput
            v-model="formData.serial_number"
            label="Serial Number"
            placeholder="Optional"
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

          <!-- File Uploads (Edit mode only) -->
          <div v-if="isEdit && equipmentId" class="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 class="text-sm font-semibold text-gray-700">File Attachments</h3>

            <!-- Photo Upload -->
            <FileUpload
              label="Equipment Photo"
              file-type="photo"
              :equipment-id="equipmentId"
              :current-file-url="formData.photo_url"
              accept="image/*"
              hint="Supported: JPG, PNG, GIF, WebP (Max 10MB)"
              @uploaded="handlePhotoUploaded"
              @deleted="handlePhotoDeleted"
            />

            <!-- Manual Upload -->
            <FileUpload
              label="Equipment Manual"
              file-type="manual"
              :equipment-id="equipmentId"
              :current-file-url="formData.manual_url"
              accept=".pdf,.doc,.docx"
              hint="Supported: PDF, DOC, DOCX (Max 10MB)"
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
              hint="Supported: PDF (Max 10MB)"
              @uploaded="handleReportUploaded"
              @deleted="handleReportDeleted"
            />
          </div>

          <!-- Note for new equipment -->
          <div v-if="!isEdit" class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p class="text-sm text-blue-800">
              📝 Note: Create the equipment first, then you can upload files in edit mode.
            </p>
          </div>

          <!-- Maintenance Records -->
          <div v-if="isEdit" class="space-y-4 p-4 bg-yellow-50 rounded-lg">
            <h3 class="text-sm font-semibold text-gray-700">Maintenance Records</h3>

            <div class="grid grid-cols-2 gap-4">
              <AppInput
                v-model="formData.last_maintenance_date"
                type="date"
                label="Last Maintenance Date"
              />
              <AppInput
                v-model="formData.next_maintenance_date"
                type="date"
                label="Next Maintenance Due"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Maintenance Notes
              </label>
              <textarea
                v-model="formData.maintenance_notes"
                rows="3"
                placeholder="Enter maintenance history and notes..."
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
              ></textarea>
            </div>
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
import { useUiStore } from '@/stores/ui'
import MainLayout from '@/layouts/MainLayout.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppButton from '@/components/common/AppButton.vue'
import FileUpload from '@/components/common/FileUpload.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()
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
  serial_number: '',
  status: 'ordering',
  purchase_date: '',
  photo_url: '',
  manual_url: '',
  calibration_report_url: '',
  last_maintenance_date: '',
  next_maintenance_date: '',
  maintenance_notes: '',
  specifications: '',
  notes: '',
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
    formData.serial_number = equipment.serial_number || ''
    formData.status = equipment.status || 'ordering'
    formData.purchase_date = equipment.purchase_date || ''
    formData.photo_url = equipment.photo_url || ''
    formData.manual_url = equipment.manual_url || ''
    formData.calibration_report_url = equipment.calibration_report_url || ''
    formData.last_maintenance_date = equipment.last_maintenance_date || ''
    formData.next_maintenance_date = equipment.next_maintenance_date || ''
    formData.maintenance_notes = equipment.maintenance_notes || ''
    formData.specifications = equipment.specifications || ''
    formData.notes = equipment.notes || ''
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
      serial_number: formData.serial_number || undefined,
      status: isEdit.value ? formData.status : undefined,
      purchase_date: formData.purchase_date || undefined,
      photo_url: formData.photo_url || undefined,
      manual_url: formData.manual_url || undefined,
      calibration_report_url: formData.calibration_report_url || undefined,
      last_maintenance_date: formData.last_maintenance_date || undefined,
      next_maintenance_date: formData.next_maintenance_date || undefined,
      maintenance_notes: formData.maintenance_notes || undefined,
      specifications: formData.specifications || undefined,
      notes: formData.notes || undefined,
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

onMounted(() => {
  if (isEdit.value) {
    loadEquipment()
  }
})
</script>
