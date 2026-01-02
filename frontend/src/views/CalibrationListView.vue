<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Calibration Management</h1>
        <AppButton
          v-if="authStore.isManager"
          variant="primary"
          @click="showAddModal = true"
        >
          + Add Calibration
        </AppButton>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex flex-col sm:flex-row gap-3">
          <select
            v-model="filter"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
            @change="loadCalibrations"
          >
            <option value="all">All Calibrations</option>
            <option value="overdue">Overdue</option>
            <option value="7days">Due in 7 Days</option>
            <option value="30days">Due in 30 Days</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading calibrations...</p>
      </div>

      <!-- No Data -->
      <div v-else-if="calibrations.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500">No calibrations found</p>
      </div>

      <!-- Calibrations Display -->
      <div v-else>
        <!-- Desktop: Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden hidden md:block">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Equipment</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Calibration</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Next Due</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Days</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Report</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="cal in calibrations" :key="cal.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <router-link
                      :to="`/equipment/${cal.equipment_id}`"
                      class="text-sm font-medium text-sky-600 hover:text-sky-800"
                    >
                      {{ cal.equipment_asset_code }}
                    </router-link>
                    <p class="text-xs text-gray-500">
                      {{ cal.equipment_manufacturer }} {{ cal.equipment_model }}
                    </p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(cal.calibration_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(cal.next_due_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span :class="daysTextClass(cal.days_until_due)">
                      {{ cal.days_until_due >= 0 ? cal.days_until_due : `${Math.abs(cal.days_until_due)} overdue` }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="statusBadge(cal.days_until_due, cal.is_overdue)" class="px-2 py-1 text-xs font-semibold rounded">
                      {{ statusLabel(cal.days_until_due, cal.is_overdue) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {{ cal.provider }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <a
                      v-if="cal.report_url"
                      :href="`http://localhost:8000${cal.report_url}`"
                      target="_blank"
                      class="text-sky-600 hover:text-sky-900"
                    >
                      📄 View
                    </a>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm space-x-3">
                    <button
                      @click="editCalibration(cal)"
                      class="text-sky-600 hover:text-sky-900"
                    >
                      Edit
                    </button>
                    <button
                      v-if="authStore.isAdmin"
                      @click="handleDelete(cal)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Mobile: Cards -->
        <div class="block md:hidden space-y-4">
        <div v-for="cal in calibrations" :key="cal.id" class="bg-white rounded-lg shadow p-4">
          <div class="flex justify-between items-start mb-3">
            <router-link
              :to="`/equipment/${cal.equipment_id}`"
              class="font-semibold text-sky-600 hover:text-sky-800"
            >
              {{ cal.equipment_asset_code }}
            </router-link>
            <span :class="statusBadge(cal.days_until_due, cal.is_overdue)" class="px-2 py-1 text-xs font-semibold rounded">
              {{ statusLabel(cal.days_until_due, cal.is_overdue) }}
            </span>
          </div>

          <p class="text-sm text-gray-600 mb-2">
            {{ cal.equipment_manufacturer }} {{ cal.equipment_model }}
          </p>

          <div class="grid grid-cols-2 gap-2 text-sm">
            <div>
              <p class="text-gray-500">Last:</p>
              <p class="font-medium">{{ formatDate(cal.calibration_date) }}</p>
            </div>
            <div>
              <p class="text-gray-500">Next:</p>
              <p class="font-medium">{{ formatDate(cal.next_due_date) }}</p>
            </div>
          </div>

          <div class="mt-2 flex justify-between items-center text-sm">
            <span :class="daysTextClass(cal.days_until_due)">
              {{ cal.days_until_due >= 0 ? `${cal.days_until_due} days` : `${Math.abs(cal.days_until_due)} days overdue` }}
            </span>
            <span class="text-gray-600">{{ cal.provider }}</span>
          </div>

          <div class="mt-3 flex justify-between items-center">
            <a
              v-if="cal.report_url"
              :href="`http://localhost:8000${cal.report_url}`"
              target="_blank"
              class="text-sm text-sky-600 hover:text-sky-800"
            >
              📄 View Report
            </a>
            <span v-else class="text-sm text-gray-400">No report</span>
            <div class="flex gap-2">
              <button
                @click="editCalibration(cal)"
                class="text-sm text-sky-600 hover:text-sky-900"
              >
                Edit
              </button>
              <button
                v-if="authStore.isAdmin"
                @click="handleDelete(cal)"
                class="text-sm text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- Add Calibration Modal -->
      <div
        v-if="showAddModal"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
        @click.self="showAddModal = false"
      >
        <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            {{ isEditMode ? 'Edit Calibration Record' : 'Add Calibration Record' }}
          </h3>
          <form @submit.prevent="handleAddCalibration" class="space-y-4">
            <!-- Equipment Selection (disabled in edit mode) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Equipment</label>
              <input
                v-model="newCalibration.equipmentSearch"
                type="text"
                placeholder="Search by asset code..."
                class="w-full px-3 py-2 border rounded-lg mb-2"
                :disabled="isEditMode"
                @input="searchEquipment"
              />
              <div v-if="searchResults.length > 0 && !isEditMode" class="border rounded max-h-40 overflow-y-auto">
                <div
                  v-for="eq in searchResults"
                  :key="eq.id"
                  @click="selectEquipment(eq)"
                  class="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  {{ eq.asset_code }} - {{ eq.manufacturer }} {{ eq.model }}
                </div>
              </div>
              <p v-if="selectedEquipment" class="text-sm text-green-600 mt-1">
                Selected: {{ selectedEquipment.asset_code }}
              </p>
            </div>

            <AppInput
              v-model="newCalibration.calibration_date"
              type="date"
              label="Calibration Date"
              required
            />

            <AppInput
              v-model="newCalibration.next_due_date"
              type="date"
              label="Next Due Date"
              required
            />

            <AppInput
              v-model="newCalibration.provider"
              label="Calibration Provider"
              required
            />

            <AppInput
              v-model="newCalibration.certificate_number"
              label="Certificate Number"
            />

            <AppInput
              v-model.number="newCalibration.cost"
              type="number"
              label="Cost (optional)"
            />

            <!-- File Upload (Edit mode only) -->
            <div v-if="isEditMode && editingCalibrationId" class="p-4 bg-gray-50 rounded-lg">
              <FileUpload
                label="Calibration Report"
                file-type="calibration"
                :calibration-id="editingCalibrationId"
                :current-file-url="newCalibration.report_url"
                accept=".pdf"
                hint="Upload calibration report (PDF, Max 100MB)"
                @uploaded="handleReportUploaded"
                @deleted="handleReportDeleted"
              />
            </div>

            <!-- URL input for create mode -->
            <AppInput
              v-if="!isEditMode"
              v-model="newCalibration.report_url"
              label="Calibration Report URL (optional)"
              placeholder="Leave empty, upload file after creation"
              hint="File upload available in edit mode"
            />

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                v-model="newCalibration.notes"
                rows="3"
                class="w-full px-3 py-2 border rounded-lg"
              ></textarea>
            </div>

            <div v-if="addError" class="p-3 bg-red-50 border border-red-200 rounded">
              <p class="text-sm text-red-600">{{ addError }}</p>
            </div>

            <div class="flex justify-end gap-3">
              <AppButton type="button" variant="ghost" @click="showAddModal = false">
                Cancel
              </AppButton>
              <AppButton type="submit" variant="primary" :loading="adding">
                {{ isEditMode ? 'Update Calibration' : 'Create Calibration' }}
              </AppButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import { useUiStore } from '@/stores/ui'
import { calibrationsApi, type CalibrationDueSoon } from '@/api/calibrations'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppInput from '@/components/common/AppInput.vue'
import FileUpload from '@/components/common/FileUpload.vue'
import type { Equipment } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()
const uiStore = useUiStore()

const loading = ref(true)
const calibrationsRaw = ref<CalibrationDueSoon[]>([])
const filter = ref('30days')

// Add/Edit Calibration Modal
const showAddModal = ref(false)
const adding = ref(false)
const addError = ref('')
const selectedEquipment = ref<Equipment | null>(null)
const searchResults = ref<Equipment[]>([])
const editingCalibrationId = ref<number | null>(null)
const isEditMode = computed(() => editingCalibrationId.value !== null)

const newCalibration = ref({
  equipmentSearch: '',
  calibration_date: '',
  next_due_date: '',
  provider: '',
  certificate_number: '',
  cost: 0,
  report_url: '',
  notes: '',
})

// Transform data for display
const calibrations = computed(() => {
  return calibrationsRaw.value.map(item => {
    const [manufacturer, ...modelParts] = item.equipment_name.split(' ')
    return {
      ...item.calibration,
      equipment_asset_code: item.equipment_asset_code,
      equipment_manufacturer: manufacturer,
      equipment_model: modelParts.join(' '),
      days_until_due: item.days_until_due,
      is_overdue: item.is_overdue,
    }
  })
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

function statusLabel(days: number, isOverdue: boolean): string {
  if (isOverdue) return 'Overdue'
  if (days <= 7) return 'Urgent'
  if (days <= 30) return 'Due Soon'
  return 'Normal'
}

function statusBadge(days: number, isOverdue: boolean): string {
  const base = 'inline-block'
  if (isOverdue) return `${base} bg-red-100 text-red-800`
  if (days <= 7) return `${base} bg-orange-100 text-orange-800`
  if (days <= 30) return `${base} bg-yellow-100 text-yellow-800`
  return `${base} bg-green-100 text-green-800`
}

function daysTextClass(days: number): string {
  if (days < 0) return 'text-red-600 font-semibold'
  if (days <= 7) return 'text-orange-600 font-semibold'
  if (days <= 30) return 'text-yellow-600 font-medium'
  return 'text-gray-600'
}

async function loadCalibrations() {
  loading.value = true
  try {
    let days = 30
    if (filter.value === '7days') days = 7
    if (filter.value === 'overdue') days = 0
    if (filter.value === 'all') days = 365

    console.log('[CalibrationListView] Loading with days:', days)
    const response = await calibrationsApi.getDueSoon(days)
    console.log('[CalibrationListView] Response:', response.data)
    calibrationsRaw.value = response.data

    // Filter overdue if selected
    if (filter.value === 'overdue') {
      calibrationsRaw.value = calibrationsRaw.value.filter(c => c.is_overdue)
    }
  } catch (error: any) {
    console.error('Failed to load calibrations:', error)
    console.error('Error status:', error.response?.status)
    console.error('Error detail:', error.response?.data)
    // Set empty array to show "No calibrations found"
    calibrationsRaw.value = []
  } finally {
    loading.value = false
  }
}

async function searchEquipment() {
  if (newCalibration.value.equipmentSearch.length < 2) {
    searchResults.value = []
    return
  }

  try {
    await equipmentStore.fetchList({ search: newCalibration.value.equipmentSearch, limit: 10 })
    searchResults.value = equipmentStore.equipmentList
  } catch (error) {
    console.error('Failed to search equipment:', error)
  }
}

function selectEquipment(equipment: Equipment) {
  selectedEquipment.value = equipment
  newCalibration.value.equipmentSearch = equipment.asset_code
  searchResults.value = []
}

async function handleAddCalibration() {
  if (!selectedEquipment.value) {
    addError.value = 'Please select an equipment'
    return
  }

  adding.value = true
  addError.value = ''

  try {
    const data = {
      equipment_id: selectedEquipment.value.id,
      calibration_date: newCalibration.value.calibration_date,
      next_due_date: newCalibration.value.next_due_date,
      provider: newCalibration.value.provider,
      certificate_number: newCalibration.value.certificate_number || undefined,
      cost: newCalibration.value.cost > 0 ? newCalibration.value.cost : undefined,
      report_url: newCalibration.value.report_url || undefined,
      notes: newCalibration.value.notes || undefined,
    }

    if (isEditMode.value && editingCalibrationId.value) {
      // Update existing calibration
      await calibrationsApi.update(editingCalibrationId.value, data)
      uiStore.showNotification('success', 'Calibration record updated')
    } else {
      // Create new calibration
      await calibrationsApi.create(data)
      uiStore.showNotification('success', 'Calibration record created')
    }

    showAddModal.value = false
    resetForm()
    await loadCalibrations()
  } catch (error: any) {
    addError.value = error.response?.data?.detail || 'Failed to save calibration'
  } finally {
    adding.value = false
  }
}

function editCalibration(cal: any) {
  editingCalibrationId.value = cal.id
  selectedEquipment.value = {
    id: cal.equipment_id,
    asset_code: cal.equipment_asset_code,
  } as Equipment
  newCalibration.value = {
    equipmentSearch: cal.equipment_asset_code,
    calibration_date: cal.calibration_date,
    next_due_date: cal.next_due_date,
    provider: cal.provider,
    certificate_number: cal.certificate_number || '',
    cost: cal.cost || 0,
    report_url: cal.report_url || '',
    notes: cal.notes || '',
  }
  showAddModal.value = true
}

function handleReportUploaded(url: string) {
  newCalibration.value.report_url = url
  uiStore.showNotification('success', 'Report uploaded successfully')
}

function handleReportDeleted() {
  newCalibration.value.report_url = ''
  uiStore.showNotification('success', 'Report deleted successfully')
}

async function handleDelete(cal: any) {
  if (!confirm(`Permanently delete calibration record for ${cal.equipment_asset_code}?\n\nCalibration Date: ${formatDate(cal.calibration_date)}\nProvider: ${cal.provider}\n\nThis action CANNOT be undone.`)) {
    return
  }

  try {
    await calibrationsApi.delete(cal.id)
    uiStore.showNotification('success', 'Calibration record deleted successfully')
    await loadCalibrations()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to delete calibration')
  }
}

function resetForm() {
  selectedEquipment.value = null
  searchResults.value = []
  editingCalibrationId.value = null
  newCalibration.value = {
    equipmentSearch: '',
    calibration_date: '',
    next_due_date: '',
    provider: '',
    certificate_number: '',
    cost: 0,
    report_url: '',
    notes: '',
  }
}

onMounted(() => {
  loadCalibrations()
})
</script>
