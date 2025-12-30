<template>
  <MainLayout>
    <div class="max-w-6xl mx-auto space-y-6">
      <!-- Loading -->
      <div v-if="equipmentStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading equipment details...</p>
      </div>

      <!-- Equipment Details -->
      <div v-else-if="equipment" class="space-y-6">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">{{ equipment.asset_code }}</h1>
            <p class="mt-1 text-base sm:text-lg text-gray-600">
              {{ equipment.manufacturer }} {{ equipment.model }}
            </p>
          </div>
          <div class="flex flex-wrap gap-2">
            <AppButton
              v-if="authStore.isManager"
              variant="secondary"
              size="sm"
              @click="router.push(`/equipment/${equipment.id}/edit`)"
            >
              Edit
            </AppButton>
            <AppButton
              variant="secondary"
              size="sm"
              @click="downloadQRCode"
            >
              Download QR
            </AppButton>
            <AppButton
              v-if="authStore.isAdmin"
              variant="danger"
              size="sm"
              @click="handleDelete"
            >
              Delete
            </AppButton>
          </div>
        </div>

        <!-- Status Badge -->
        <div>
          <span :class="statusBadgeClass(equipment.status)" class="text-lg px-4 py-2">
            {{ statusLabel(equipment.status) }}
          </span>
        </div>

        <!-- Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Basic Information -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            <dl class="space-y-3">
              <div>
                <dt class="text-sm font-medium text-gray-500">Asset Code</dt>
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ equipment.asset_code }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Category</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ categoryLabel(equipment.category) }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Manufacturer</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ equipment.manufacturer }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Model</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ equipment.model }}</dd>
              </div>
              <div v-if="equipment.serial_number">
                <dt class="text-sm font-medium text-gray-500">Serial Number</dt>
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ equipment.serial_number }}</dd>
              </div>
            </dl>
          </div>

          <!-- Equipment Photo -->
          <div v-if="equipment.photo_url" class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Equipment Photo</h2>
            <div class="flex justify-center">
              <img
                :src="getFullUrl(equipment.photo_url)"
                alt="Equipment Photo"
                class="max-w-full h-auto max-h-96 rounded-lg border border-gray-200"
                @error="handleImageError"
              />
            </div>
          </div>

          <!-- Documents & Reports -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Documents & Reports</h2>
            <dl class="space-y-3">
              <div v-if="equipment.purchase_date">
                <dt class="text-sm font-medium text-gray-500">Purchase Date</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDate(equipment.purchase_date) }}</dd>
              </div>
              <div v-if="equipment.manual_url">
                <dt class="text-sm font-medium text-gray-500">Equipment Manual</dt>
                <dd class="mt-1">
                  <a :href="getFullUrl(equipment.manual_url)" target="_blank" class="inline-flex items-center text-sm text-sky-600 hover:text-sky-800">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Download Manual
                  </a>
                </dd>
              </div>
              <div v-if="equipment.calibration_report_url">
                <dt class="text-sm font-medium text-gray-500">Calibration Report</dt>
                <dd class="mt-1">
                  <a :href="getFullUrl(equipment.calibration_report_url)" target="_blank" class="inline-flex items-center text-sm text-sky-600 hover:text-sky-800">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Download Report
                  </a>
                </dd>
              </div>
            </dl>
          </div>

          <!-- QR Code -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">QR Code</h2>
            <div class="flex justify-center">
              <img
                v-if="qrCodeUrl"
                :src="qrCodeUrl"
                alt="QR Code"
                class="w-48 h-48 border border-gray-200 rounded"
              />
              <div v-else class="w-48 h-48 bg-gray-100 flex items-center justify-center rounded">
                <p class="text-gray-500 text-sm">Loading QR Code...</p>
              </div>
            </div>
            <p class="mt-2 text-xs text-gray-500 text-center break-all">
              {{ equipment.qr_code }}
            </p>
          </div>

          <!-- Specifications -->
          <div v-if="equipment.specifications" class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Specifications</h2>
            <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ equipment.specifications }}</p>
          </div>
        </div>

        <!-- Status Actions (Operator+) -->
        <div v-if="authStore.isOperator && canPerformActions" class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Status Actions</h2>
          <div class="flex flex-wrap gap-3">
            <AppButton
              v-if="equipment.status === 'in_stock'"
              variant="primary"
              @click="showDeployModal = true"
            >
              Deploy Equipment
            </AppButton>
            <AppButton
              v-if="equipment.status === 'deployed' || equipment.status === 'rented'"
              variant="primary"
              @click="showReturnModal = true"
            >
              Return Equipment
            </AppButton>
            <AppButton
              v-if="equipment.status !== 'repair' && equipment.status !== 'calibrating'"
              variant="secondary"
              @click="showRepairModal = true"
            >
              Send to Repair
            </AppButton>
            <AppButton
              v-if="equipment.status !== 'calibrating'"
              variant="secondary"
              @click="handleSendToCalibration"
            >
              Send to Calibration
            </AppButton>
          </div>
        </div>

        <!-- Activity Log -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Activity Log</h2>
          </div>

          <div v-if="logs.length === 0" class="text-center py-12 text-gray-500">
            No activity logs yet
          </div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date & Time
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDateTime(log.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span v-if="log.created_by_username" class="text-sm font-medium text-gray-900">
                      {{ log.created_by_username }}
                    </span>
                    <span v-else class="text-sm text-gray-400">System</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="logTypeBadge(log.log_type)" class="px-2 py-1 text-xs font-semibold rounded">
                      {{ logTypeLabel(log.log_type) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900">
                    {{ log.description }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-600">
                    <div v-if="log.new_value" class="max-w-xs truncate" :title="log.new_value">
                      {{ log.new_value }}
                    </div>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span v-if="log.latitude && log.longitude" class="text-gray-600">
                      📍 {{ log.latitude.toFixed(4) }}, {{ log.longitude.toFixed(4) }}
                    </span>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="equipment?.notes" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 class="text-sm font-semibold text-yellow-900 mb-2">Notes</h3>
        <p class="text-sm text-yellow-800 whitespace-pre-wrap">{{ equipment.notes }}</p>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import { useUiStore } from '@/stores/ui'
import { equipmentApi } from '@/api/equipment'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()
const uiStore = useUiStore()

const equipmentId = computed(() => parseInt(route.params.id as string))
const equipment = computed(() => equipmentStore.currentEquipment)

const qrCodeUrl = ref('')
const logs = ref<any[]>([])
const showDeployModal = ref(false)
const showReturnModal = ref(false)
const showRepairModal = ref(false)

const canPerformActions = computed(() => {
  return equipment.value?.status !== 'disposed' && equipment.value?.status !== 'lost'
})

function categoryLabel(category: string): string {
  const labels: Record<string, string> = {
    mbes: 'MBES - Multibeam Echosounder',
    gnss: 'GNSS - Receiver',
    svp: 'SVP - Sound Velocity Profiler',
    sbp: 'SBP - Sub-bottom Profiler',
    usbl: 'USBL - Ultra-Short Baseline',
    rov: 'ROV - Remotely Operated Vehicle',
    ins: 'INS - Inertial Navigation System',
    magnetometer: 'Magnetometer',
    other: 'Other',
  }
  return labels[category] || category
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    ordering: 'Ordering',
    in_stock: 'In Stock',
    deployed: 'Deployed',
    rented: 'Rented',
    repair: 'Repair',
    disposed: 'Disposed',
    lost: 'Lost',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const base = 'inline-block font-semibold rounded'
  const variants: Record<string, string> = {
    ordering: 'bg-yellow-100 text-yellow-800',
    in_stock: 'bg-green-100 text-green-800',
    deployed: 'bg-blue-100 text-blue-800',
    rented: 'bg-purple-100 text-purple-800',
    repair: 'bg-orange-100 text-orange-800',
    disposed: 'bg-gray-100 text-gray-800',
    lost: 'bg-red-100 text-red-800',
  }
  return `${base} ${variants[status] || 'bg-gray-100 text-gray-800'}`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

function logTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    status_change: 'Status',
    location_change: 'Location',
    rental_start: 'Rental Start',
    rental_end: 'Rental End',
    calibration: 'Calibration',
    maintenance: 'Maintenance',
    note: 'Note',
    created: 'Created',
    updated: 'Updated',
  }
  return labels[type] || type
}

function logTypeBadge(type: string): string {
  const base = 'inline-block'
  const variants: Record<string, string> = {
    status_change: 'bg-blue-100 text-blue-800',
    location_change: 'bg-purple-100 text-purple-800',
    rental_start: 'bg-green-100 text-green-800',
    rental_end: 'bg-orange-100 text-orange-800',
    calibration: 'bg-yellow-100 text-yellow-800',
    maintenance: 'bg-red-100 text-red-800',
    note: 'bg-gray-100 text-gray-800',
    created: 'bg-sky-100 text-sky-800',
    updated: 'bg-indigo-100 text-indigo-800',
  }
  return `${base} ${variants[type] || 'bg-gray-100 text-gray-800'}`
}

function getFullUrl(url: string): string {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

function handleImageError(event: Event) {
  console.error('Failed to load image')
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f3f4f6" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af"%3ENo Image%3C/text%3E%3C/svg%3E'
}

function downloadQRCode() {
  if (!equipment.value) return
  const url = equipmentApi.getQRCodeImageUrl(equipment.value.id)
  window.open(url, '_blank')
}

async function handleDelete() {
  if (!equipment.value) return

  const confirmed = confirm(
    `Delete equipment ${equipment.value.asset_code}?\n\n` +
    `This will deactivate the equipment (soft delete).\n` +
    `Are you sure?`
  )

  if (!confirmed) return

  try {
    await equipmentStore.remove(equipment.value.id)
    uiStore.showNotification('success', 'Equipment deleted successfully')
    router.push('/equipment')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to delete equipment')
  }
}

async function handleSendToCalibration() {
  if (!equipment.value) return

  const notes = prompt('Notes for calibration (optional):')
  if (notes === null) return // User cancelled

  try {
    await equipmentApi.sendToCalibration(equipment.value.id, notes || undefined)
    uiStore.showNotification('success', 'Equipment sent to calibration')
    await equipmentStore.fetchById(equipmentId.value)
    await loadLogs()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to send to calibration')
  }
}

async function loadLogs() {
  if (!equipmentId.value) return

  try {
    const response = await equipmentApi.getLogs(equipmentId.value)
    logs.value = response.data
  } catch (error) {
    console.error('Failed to load logs:', error)
  }
}

async function loadQRCode() {
  if (!equipmentId.value) return

  try {
    const response = await equipmentApi.getQRCode(equipmentId.value)
    qrCodeUrl.value = response.data.qr_code_base64
  } catch (error) {
    console.error('Failed to load QR code:', error)
  }
}

onMounted(async () => {
  await equipmentStore.fetchById(equipmentId.value)
  loadLogs()
  loadQRCode()
})
</script>
