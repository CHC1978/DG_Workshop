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
          <p class="text-sm text-gray-600 mb-4">Current Status: {{ equipment.status }}</p>
          <div class="flex flex-wrap gap-3">
            <AppButton
              v-if="equipment.status === 'in_stock' || equipment.status === 'ordering'"
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
              v-if="equipment.status === 'in_stock' || equipment.status === 'deployed'"
              variant="secondary"
              @click="handleSendToRepair"
            >
              Send to Repair
            </AppButton>
            <AppButton
              v-if="equipment.status === 'in_stock' || equipment.status === 'deployed'"
              variant="secondary"
              @click="handleSendToCalibration"
            >
              Send to Calibration
            </AppButton>
          </div>
        </div>

        <!-- Sub-Equipment Section -->
        <SubEquipmentList :parent-equipment-id="equipment.id" />

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
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Attachments
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
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
                    <span v-if="log.is_edited" class="ml-2 text-xs text-gray-400" :title="`Edited ${log.edit_count} time(s), last at ${formatDateTime(log.edited_at)}`">
                      (edited ×{{ log.edit_count }})
                    </span>
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
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-center">
                    <button
                      @click.stop="viewLogAttachments(log)"
                      class="text-sky-600 hover:text-sky-900"
                    >
                      📎 View
                    </button>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      v-if="authStore.isManager"
                      @click.stop="openEditLogModal(log)"
                      class="text-indigo-600 hover:text-indigo-900"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Edit Log Modal -->
        <div
          v-if="showEditLogModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showEditLogModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Edit Activity Log</h3>
              <button @click="showEditLogModal = false" class="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>

            <div v-if="editingLog" class="space-y-4">
              <!-- Read-only Info -->
              <div class="p-3 bg-gray-50 rounded">
                <p class="text-xs text-gray-500 mb-1">Type: {{ logTypeLabel(editingLog.log_type) }}</p>
                <p class="text-xs text-gray-500">Created: {{ formatDateTime(editingLog.created_at) }} by {{ editingLog.created_by_username || 'System' }}</p>
                <p v-if="editingLog.is_edited" class="text-xs text-orange-600 mt-1">
                  Edited {{ editingLog.edit_count }} time(s), last at {{ formatDateTime(editingLog.edited_at) }} by {{ editingLog.edited_by_username }}
                </p>
              </div>

              <!-- Non-editable fields -->
              <div v-if="editingLog.old_value || editingLog.new_value" class="border-l-4 border-gray-300 pl-3">
                <p class="text-xs text-gray-500 mb-1">Change Record (read-only):</p>
                <p v-if="editingLog.old_value" class="text-sm text-gray-600">Old: {{ editingLog.old_value }}</p>
                <p v-if="editingLog.new_value" class="text-sm text-gray-600">New: {{ editingLog.new_value }}</p>
              </div>

              <!-- Editable fields -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Description <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="editLogForm.description"
                  class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sky-500"
                  rows="4"
                  placeholder="Enter description..."
                ></textarea>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Latitude (optional)</label>
                  <input
                    v-model.number="editLogForm.latitude"
                    type="number"
                    step="0.000001"
                    class="w-full px-3 py-2 border rounded-lg"
                    placeholder="e.g., 25.033671"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Longitude (optional)</label>
                  <input
                    v-model.number="editLogForm.longitude"
                    type="number"
                    step="0.000001"
                    class="w-full px-3 py-2 border rounded-lg"
                    placeholder="e.g., 121.564427"
                  />
                </div>
              </div>

              <!-- Actions -->
              <div class="flex justify-end gap-2 pt-4 border-t">
                <AppButton variant="secondary" @click="showEditLogModal = false">
                  Cancel
                </AppButton>
                <AppButton @click="handleUpdateLog" :loading="updatingLog">
                  Save Changes
                </AppButton>
              </div>
            </div>
          </div>
        </div>

        <!-- Log Attachments Modal -->
        <div
          v-if="showAttachmentsModal"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
          @click.self="showAttachmentsModal = false"
        >
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Log Attachments</h3>
              <button @click="showAttachmentsModal = false" class="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>

            <div v-if="selectedLog" class="mb-4 p-3 bg-gray-50 rounded">
              <p class="text-sm font-medium">{{ selectedLog.description }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ formatDateTime(selectedLog.created_at) }}</p>
            </div>

            <!-- Attachments List -->
            <div v-if="loadingAttachments" class="text-center py-8">
              <p class="text-gray-500">Loading attachments...</p>
            </div>

            <div v-else-if="currentAttachments.length === 0" class="text-center py-8">
              <p class="text-gray-500">No attachments yet</p>
            </div>

            <div v-else class="space-y-3 mb-4">
              <div
                v-for="att in currentAttachments"
                :key="att.id"
                class="flex items-center justify-between p-3 border rounded hover:bg-gray-50"
              >
                <div class="flex-1">
                  <a
                    :href="`http://localhost:8000${att.file_url}`"
                    target="_blank"
                    class="text-sm font-medium text-sky-600 hover:text-sky-800"
                  >
                    {{ att.file_name }}
                  </a>
                  <p class="text-xs text-gray-500">
                    {{ (att.file_size / 1024).toFixed(1) }} KB • {{ att.file_type }}
                  </p>
                  <p v-if="att.description" class="text-xs text-gray-600 mt-1">{{ att.description }}</p>
                </div>
                <button
                  @click="deleteAttachment(att.id)"
                  class="ml-4 text-red-600 hover:text-red-800 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>

            <!-- Upload Section -->
            <div class="border-t pt-4">
              <h4 class="text-sm font-semibold mb-3">Upload New Attachment</h4>
              <div class="space-y-3">
                <select
                  v-model="uploadAttachmentType"
                  class="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="calibration_report">Calibration Report</option>
                  <option value="damage_photo">Damage Photo</option>
                  <option value="repair_document">Repair Document</option>
                  <option value="maintenance_record">Maintenance Record</option>
                  <option value="other">Other</option>
                </select>

                <input
                  v-model="uploadDescription"
                  type="text"
                  placeholder="Description (optional)"
                  class="w-full px-3 py-2 border rounded-lg"
                />

                <div class="flex items-center gap-2">
                  <input
                    ref="attachmentFileInput"
                    type="file"
                    @change="handleAttachmentFileChange"
                    class="flex-1 text-sm"
                  />
                  <AppButton
                    v-if="selectedAttachmentFile"
                    @click="uploadAttachment"
                    :loading="uploadingAttachment"
                  >
                    Upload
                  </AppButton>
                </div>
              </div>
            </div>
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
import axios from 'axios'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import SubEquipmentList from '@/components/equipment/SubEquipmentList.vue'

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

// Log Attachments
const showAttachmentsModal = ref(false)
const selectedLog = ref<any>(null)
const currentAttachments = ref<any[]>([])
const loadingAttachments = ref(false)
const uploadingAttachment = ref(false)
const uploadAttachmentType = ref('other')
const uploadDescription = ref('')
const selectedAttachmentFile = ref<File | null>(null)
const attachmentFileInput = ref<HTMLInputElement | null>(null)

// Log Editing
const showEditLogModal = ref(false)
const editingLog = ref<any>(null)
const updatingLog = ref(false)
const editLogForm = ref({
  description: '',
  latitude: null as number | null,
  longitude: null as number | null,
})

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

async function handleSendToRepair() {
  if (!equipment.value) return

  const notes = prompt('Notes for repair (optional):')
  if (notes === null) return

  try {
    await equipmentApi.repair(equipment.value.id, notes || undefined)
    uiStore.showNotification('success', 'Equipment sent to repair')
    await equipmentStore.fetchById(equipmentId.value)
    await loadLogs()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to send to repair')
  }
}

async function handleSendToCalibration() {
  if (!equipment.value) return

  const notes = prompt('Notes for calibration (optional):')
  if (notes === null) return

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

// ==================== Log Editing ====================

function openEditLogModal(log: any) {
  editingLog.value = log
  editLogForm.value = {
    description: log.description || '',
    latitude: log.latitude,
    longitude: log.longitude,
  }
  showEditLogModal.value = true
}

async function handleUpdateLog() {
  if (!editingLog.value || !equipment.value) return

  if (!editLogForm.value.description.trim()) {
    uiStore.showNotification('error', 'Description is required')
    return
  }

  updatingLog.value = true

  try {
    const response = await equipmentApi.updateLog(
      equipment.value.id,
      editingLog.value.id,
      editLogForm.value
    )

    // Update local log in the list
    const index = logs.value.findIndex(l => l.id === editingLog.value.id)
    if (index !== -1) {
      logs.value[index] = response.data
    }

    uiStore.showNotification('success', 'Log updated successfully')
    showEditLogModal.value = false
    editingLog.value = null
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Update failed')
  } finally {
    updatingLog.value = false
  }
}

// ==================== Log Attachments ====================

async function viewLogAttachments(log: any) {
  selectedLog.value = log
  showAttachmentsModal.value = true
  await loadLogAttachments(log.id)
}

async function loadLogAttachments(logId: number) {
  loadingAttachments.value = true
  try {
    const response = await axios.get(`/api/equipment-logs/${logId}/attachments`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('auth') ? JSON.parse(localStorage.getItem('auth')!).token : ''}`
      }
    })
    currentAttachments.value = response.data
  } catch (error) {
    console.error('Failed to load attachments:', error)
    currentAttachments.value = []
  } finally {
    loadingAttachments.value = false
  }
}

function handleAttachmentFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  selectedAttachmentFile.value = target.files?.[0] || null
}

async function uploadAttachment() {
  if (!selectedAttachmentFile.value || !selectedLog.value) return

  uploadingAttachment.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedAttachmentFile.value)
    formData.append('attachment_type', uploadAttachmentType.value)
    if (uploadDescription.value) {
      formData.append('description', uploadDescription.value)
    }

    const authData = localStorage.getItem('auth')
    const token = authData ? JSON.parse(authData).token : ''

    await axios.post(
      `/api/equipment-logs/${selectedLog.value.id}/attachments`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      }
    )

    uiStore.showNotification('success', 'Attachment uploaded successfully')
    selectedAttachmentFile.value = null
    uploadDescription.value = ''
    if (attachmentFileInput.value) {
      attachmentFileInput.value.value = ''
    }
    await loadLogAttachments(selectedLog.value.id)
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Upload failed')
  } finally {
    uploadingAttachment.value = false
  }
}

async function deleteAttachment(attachmentId: number) {
  if (!confirm('Delete this attachment?')) return

  try {
    const authData = localStorage.getItem('auth')
    const token = authData ? JSON.parse(authData).token : ''

    await axios.delete(`/api/log-attachments/${attachmentId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    uiStore.showNotification('success', 'Attachment deleted')
    if (selectedLog.value) {
      await loadLogAttachments(selectedLog.value.id)
    }
  } catch (error: any) {
    uiStore.showNotification('error', 'Delete failed')
  }
}

onMounted(async () => {
  await equipmentStore.fetchById(equipmentId.value)
  loadLogs()
  loadQRCode()
})
</script>
