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

          <!-- Purchase Date -->
          <AppInput
            v-model="formData.purchase_date"
            type="date"
            label="Purchase Date"
          />

          <!-- Photo URL -->
          <AppInput
            v-model="formData.photo_url"
            label="Photo URL"
            placeholder="URL to equipment photo"
            hint="Upload photo and enter URL"
          />

          <!-- Manual URL -->
          <AppInput
            v-model="formData.manual_url"
            label="Manual URL"
            placeholder="URL to equipment manual (PDF)"
            hint="Upload manual and enter URL"
          />

          <!-- Calibration Report URL -->
          <AppInput
            v-model="formData.calibration_report_url"
            label="Calibration Report URL"
            placeholder="URL to calibration report (PDF)"
            hint="Upload report and enter URL"
          />

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
              Notes
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
  purchase_date: '',
  photo_url: '',
  manual_url: '',
  calibration_report_url: '',
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
  errors.purchase_price = ''
  errors.rental_daily_rate = ''
  errorMessage.value = ''
  successMessage.value = ''
}

async function loadEquipment() {
  if (!equipmentId.value) return

  try {
    const equipment = await equipmentStore.fetchById(equipmentId.value)
    formData.category = equipment.category
    formData.manufacturer = equipment.manufacturer
    formData.model = equipment.model
    formData.serial_number = equipment.serial_number || ''
    formData.purchase_date = equipment.purchase_date || ''
    formData.photo_url = equipment.photo_url || ''
    formData.manual_url = equipment.manual_url || ''
    formData.calibration_report_url = equipment.calibration_report_url || ''
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
      purchase_date: formData.purchase_date || undefined,
      photo_url: formData.photo_url || undefined,
      manual_url: formData.manual_url || undefined,
      calibration_report_url: formData.calibration_report_url || undefined,
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
