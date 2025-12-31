<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Maintenance Management</h1>
        <AppButton
          v-if="authStore.isManager"
          variant="primary"
          @click="showAddModal = true"
        >
          + Add Maintenance
        </AppButton>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex flex-col sm:flex-row gap-3">
          <select
            v-model="filter"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
            @change="loadMaintenance"
          >
            <option value="all">All Maintenance</option>
            <option value="overdue">Overdue</option>
            <option value="7days">Due in 7 Days</option>
            <option value="30days">Due in 30 Days</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading maintenance records...</p>
      </div>

      <!-- No Data -->
      <div v-else-if="maintenanceRecords.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500">No maintenance records found</p>
      </div>

      <!-- Maintenance Display -->
      <div v-else>
        <!-- Desktop: Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden hidden md:block">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Equipment</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Maintenance</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Next Due</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Days</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Report</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="maint in maintenanceRecords" :key="maint.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <router-link
                      :to="`/equipment/${maint.equipment_id}`"
                      class="text-sm font-medium text-sky-600 hover:text-sky-800"
                    >
                      {{ maint.equipment_asset_code }}
                    </router-link>
                    <p class="text-xs text-gray-500">
                      {{ maint.equipment_manufacturer }} {{ maint.equipment_model }}
                    </p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(maint.maintenance_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(maint.next_due_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span :class="daysTextClass(maint.days_until_due)">
                      {{ maint.days_until_due >= 0 ? maint.days_until_due : `${Math.abs(maint.days_until_due)} overdue` }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="statusBadge(maint.days_until_due, maint.is_overdue)" class="px-2 py-1 text-xs font-semibold rounded">
                      {{ statusLabel(maint.days_until_due, maint.is_overdue) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {{ maint.provider }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <a
                      v-if="maint.report_url"
                      :href="`http://localhost:8000${maint.report_url}`"
                      target="_blank"
                      class="text-sky-600 hover:text-sky-900"
                    >
                      📄 View
                    </a>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm space-x-3">
                    <button
                      @click="editMaintenance(maint)"
                      class="text-sky-600 hover:text-sky-900"
                    >
                      Edit
                    </button>
                    <button
                      v-if="authStore.isAdmin"
                      @click="handleDelete(maint)"
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
        <div v-for="maint in maintenanceRecords" :key="maint.id" class="bg-white rounded-lg shadow p-4">
          <div class="flex justify-between items-start mb-3">
            <router-link
              :to="`/equipment/${maint.equipment_id}`"
              class="font-semibold text-sky-600 hover:text-sky-800"
            >
              {{ maint.equipment_asset_code }}
            </router-link>
            <span :class="statusBadge(maint.days_until_due, maint.is_overdue)" class="px-2 py-1 text-xs font-semibold rounded">
              {{ statusLabel(maint.days_until_due, maint.is_overdue) }}
            </span>
          </div>

          <p class="text-sm text-gray-600 mb-2">
            {{ maint.equipment_manufacturer }} {{ maint.equipment_model }}
          </p>

          <div class="grid grid-cols-2 gap-2 text-sm">
            <div>
              <p class="text-gray-500">Last:</p>
              <p class="font-medium">{{ formatDate(maint.maintenance_date) }}</p>
            </div>
            <div>
              <p class="text-gray-500">Next:</p>
              <p class="font-medium">{{ formatDate(maint.next_due_date) }}</p>
            </div>
          </div>

          <div class="mt-2 flex justify-between items-center text-sm">
            <span :class="daysTextClass(maint.days_until_due)">
              {{ maint.days_until_due >= 0 ? `${maint.days_until_due} days` : `${Math.abs(maint.days_until_due)} days overdue` }}
            </span>
            <span class="text-gray-600">{{ maint.provider }}</span>
          </div>

          <div class="mt-3 flex justify-between items-center">
            <a
              v-if="maint.report_url"
              :href="`http://localhost:8000${maint.report_url}`"
              target="_blank"
              class="text-sm text-sky-600 hover:text-sky-800"
            >
              📄 View Report
            </a>
            <span v-else class="text-sm text-gray-400">No report</span>
            <div class="flex gap-2">
              <button
                @click="editMaintenance(maint)"
                class="text-sm text-sky-600 hover:text-sky-900"
              >
                Edit
              </button>
              <button
                v-if="authStore.isAdmin"
                @click="handleDelete(maint)"
                class="text-sm text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- Add Maintenance Modal -->
      <div
        v-if="showAddModal"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
        @click.self="showAddModal = false"
      >
        <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            {{ isEditMode ? 'Edit Maintenance Record' : 'Add Maintenance Record' }}
          </h3>
          <form @submit.prevent="handleAddMaintenance" class="space-y-4">
            <!-- Equipment Selection (disabled in edit mode) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Equipment</label>
              <input
                v-model="newMaintenance.equipmentSearch"
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
              v-model="newMaintenance.maintenance_date"
              type="date"
              label="Maintenance Date"
              required
            />

            <AppInput
              v-model="newMaintenance.next_due_date"
              type="date"
              label="Next Due Date"
              required
            />

            <AppInput
              v-model="newMaintenance.provider"
              label="Service Provider"
              required
            />

            <!-- Service Type Dropdown -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
              <select
                v-model="newMaintenance.service_type"
                class="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">Select service type (optional)</option>
                <option value="preventive">Preventive Maintenance</option>
                <option value="repair">Repair</option>
                <option value="overhaul">Overhaul</option>
                <option value="inspection">Inspection</option>
              </select>
            </div>

            <AppInput
              v-model.number="newMaintenance.cost"
              type="number"
              label="Cost (optional)"
            />

            <!-- File Upload (Edit mode only) -->
            <div v-if="isEditMode && editingMaintenanceId" class="p-4 bg-gray-50 rounded-lg">
              <FileUpload
                label="Maintenance Report"
                file-type="maintenance"
                :maintenance-id="editingMaintenanceId"
                :current-file-url="newMaintenance.report_url"
                accept=".pdf"
                hint="Upload maintenance report (PDF, Max 10MB)"
                @uploaded="handleReportUploaded"
                @deleted="handleReportDeleted"
              />
            </div>

            <!-- URL input for create mode -->
            <AppInput
              v-if="!isEditMode"
              v-model="newMaintenance.report_url"
              label="Maintenance Report URL (optional)"
              placeholder="Leave empty, upload file after creation"
              hint="File upload available in edit mode"
            />

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                v-model="newMaintenance.notes"
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
                {{ isEditMode ? 'Update Maintenance' : 'Create Maintenance' }}
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
import { maintenanceApi, type MaintenanceDueSoon } from '@/api/maintenance'
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
const maintenanceRaw = ref<MaintenanceDueSoon[]>([])
const filter = ref('30days')

// Add/Edit Maintenance Modal
const showAddModal = ref(false)
const adding = ref(false)
const addError = ref('')
const selectedEquipment = ref<Equipment | null>(null)
const searchResults = ref<Equipment[]>([])
const editingMaintenanceId = ref<number | null>(null)
const isEditMode = computed(() => editingMaintenanceId.value !== null)

const newMaintenance = ref({
  equipmentSearch: '',
  maintenance_date: '',
  next_due_date: '',
  provider: '',
  service_type: '',
  cost: 0,
  report_url: '',
  notes: '',
})

// Transform data for display
const maintenanceRecords = computed(() => {
  return maintenanceRaw.value.map(item => {
    const [manufacturer, ...modelParts] = item.equipment_name.split(' ')
    return {
      ...item.maintenance,
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

async function loadMaintenance() {
  loading.value = true
  try {
    let days = 30
    if (filter.value === '7days') days = 7
    if (filter.value === 'overdue') days = 0
    if (filter.value === 'all') days = 365

    const response = await maintenanceApi.getDueSoon(days)
    maintenanceRaw.value = response.data

    // Filter overdue if selected
    if (filter.value === 'overdue') {
      maintenanceRaw.value = maintenanceRaw.value.filter(m => m.is_overdue)
    }
  } catch (error: any) {
    console.error('Failed to load maintenance:', error)
    maintenanceRaw.value = []
  } finally {
    loading.value = false
  }
}

async function searchEquipment() {
  if (newMaintenance.value.equipmentSearch.length < 2) {
    searchResults.value = []
    return
  }

  try {
    await equipmentStore.fetchList({ search: newMaintenance.value.equipmentSearch, limit: 10 })
    searchResults.value = equipmentStore.equipmentList
  } catch (error) {
    console.error('Failed to search equipment:', error)
  }
}

function selectEquipment(equipment: Equipment) {
  selectedEquipment.value = equipment
  newMaintenance.value.equipmentSearch = equipment.asset_code
  searchResults.value = []
}

async function handleAddMaintenance() {
  if (!selectedEquipment.value) {
    addError.value = 'Please select an equipment'
    return
  }

  adding.value = true
  addError.value = ''

  try {
    const data = {
      equipment_id: selectedEquipment.value.id,
      maintenance_date: newMaintenance.value.maintenance_date,
      next_due_date: newMaintenance.value.next_due_date,
      provider: newMaintenance.value.provider,
      service_type: newMaintenance.value.service_type || undefined,
      cost: newMaintenance.value.cost > 0 ? newMaintenance.value.cost : undefined,
      report_url: newMaintenance.value.report_url || undefined,
      notes: newMaintenance.value.notes || undefined,
    }

    if (isEditMode.value && editingMaintenanceId.value) {
      // Update existing maintenance
      await maintenanceApi.update(editingMaintenanceId.value, data)
      uiStore.showNotification('success', 'Maintenance record updated')
    } else {
      // Create new maintenance
      await maintenanceApi.create(data)
      uiStore.showNotification('success', 'Maintenance record created')
    }

    showAddModal.value = false
    resetForm()
    await loadMaintenance()
  } catch (error: any) {
    addError.value = error.response?.data?.detail || 'Failed to save maintenance'
  } finally {
    adding.value = false
  }
}

function editMaintenance(maint: any) {
  editingMaintenanceId.value = maint.id
  selectedEquipment.value = {
    id: maint.equipment_id,
    asset_code: maint.equipment_asset_code,
  } as Equipment
  newMaintenance.value = {
    equipmentSearch: maint.equipment_asset_code,
    maintenance_date: maint.maintenance_date,
    next_due_date: maint.next_due_date,
    provider: maint.provider,
    service_type: maint.service_type || '',
    cost: maint.cost || 0,
    report_url: maint.report_url || '',
    notes: maint.notes || '',
  }
  showAddModal.value = true
}

function handleReportUploaded(url: string) {
  newMaintenance.value.report_url = url
  uiStore.showNotification('success', 'Report uploaded successfully')
}

function handleReportDeleted() {
  newMaintenance.value.report_url = ''
  uiStore.showNotification('success', 'Report deleted successfully')
}

async function handleDelete(maint: any) {
  if (!confirm(`Permanently delete maintenance record for ${maint.equipment_asset_code}?\n\nMaintenance Date: ${formatDate(maint.maintenance_date)}\nProvider: ${maint.provider}\n\nThis action CANNOT be undone.`)) {
    return
  }

  try {
    await maintenanceApi.delete(maint.id)
    uiStore.showNotification('success', 'Maintenance record deleted successfully')
    await loadMaintenance()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to delete maintenance')
  }
}

function resetForm() {
  selectedEquipment.value = null
  searchResults.value = []
  editingMaintenanceId.value = null
  newMaintenance.value = {
    equipmentSearch: '',
    maintenance_date: '',
    next_due_date: '',
    provider: '',
    service_type: '',
    cost: 0,
    report_url: '',
    notes: '',
  }
}

onMounted(() => {
  loadMaintenance()
})
</script>
