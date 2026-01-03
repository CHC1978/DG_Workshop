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
        <EquipmentHeaderSection
          :equipment="equipment"
          :can-edit="authStore.isManager"
          :can-delete="authStore.isAdmin"
          @navigate="(id) => router.push(`/equipment/${id}`)"
          @edit="router.push(`/equipment/${equipment.id}/edit`)"
          @download-qr="downloadQRCode"
          @delete="handleDelete"
        />

        <!-- Status & Actions Card -->
        <StatusActionsCard
          :equipment="equipment"
          :can-perform-actions="authStore.isOperator && canPerformActions"
          @action-selected="executeStatusAction"
        />

        <!-- Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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

          <!-- Basic Information -->
          <BasicInformationCard
            :equipment="equipment"
            :children-equipment="childrenEquipment"
            @navigate="(id) => router.push(`/equipment/${id}`)"
          />

          <!-- Children Equipment Section -->
          <ChildrenEquipmentSection
            v-if="equipment"
            :key="`children-${equipment.id}`"
            :parent-equipment-id="equipment.id"
            :parent-category="equipment.category"
            :can-edit="authStore.isOperator"
            :can-detach="authStore.isManager"
            @detach="handleDetachChild"
            @children-updated="handleChildrenUpdated"
            @children-loaded="childrenEquipment = $event"
            ref="childrenSection"
          />

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

        <!-- Activity Log -->
        <EquipmentLogSection
          v-if="equipmentId"
          :key="`logs-${equipmentId}`"
          :equipment-id="equipmentId"
          :is-admin="authStore.isAdmin"
          @log-double-clicked="handleLogDoubleClick"
          @view-attachments="viewLogAttachmentsQuick"
          @logs-cleared="uiStore.showNotification('success', 'All logs cleared')"
          ref="logSection"
        />

        <!-- Deploy Equipment Modal -->
        <DeployEquipmentModal
          :show="showDeployModal"
          :equipment="equipment"
          :children-count="childrenEquipment.length"
          :locations="locations"
          @close="showDeployModal = false"
          @deployed="handleDeployed"
        />

        <!-- Return Equipment Modal -->
        <ReturnEquipmentModal
          :show="showReturnModal"
          :equipment="equipment"
          :children-count="childrenEquipment.length"
          :locations="locations"
          @close="showReturnModal = false"
          @returned="handleReturned"
        />

        <!-- Send to Repair Modal -->
        <SendToRepairModal
          :show="showRepairModal"
          :equipment="equipment"
          :children-count="childrenEquipment.length"
          :locations="locations"
          @close="showRepairModal = false"
          @submitted="handleRepairSubmitted"
        />

        <!-- Send to Calibration Modal -->
        <SendToCalibrationModal
          :show="showCalibrationModal"
          :equipment="equipment"
          :children-count="childrenEquipment.length"
          :locations="locations"
          @close="showCalibrationModal = false"
          @submitted="handleCalibrationSubmitted"
        />

        <!-- Set to In Stock Modal -->
        <SetToInStockModal
          :show="showInStockModal"
          :equipment="equipment"
          :children-count="childrenEquipment.length"
          :locations="locations"
          @close="showInStockModal = false"
          @submitted="handleInStockSubmitted"
        />

        <!-- Set to Rented Modal -->
        <SetToRentedModal
          :show="showRentedModal"
          :equipment="equipment"
          :children-count="childrenEquipment.length"
          :locations="locations"
          @close="showRentedModal = false"
          @submitted="handleRentedSubmitted"
        />

        <!-- Detach from Parent Modal -->
        <DetachFromParentModal
          :show="showDetachModal"
          :equipment="detachingChild"
          :locations="locations"
          @close="handleDetachModalClose"
          @detached="handleDetached"
        />

        <!-- Add Maintenance Record Modal -->
        <AddMaintenanceRecordModal
          :show="showMaintenanceModal"
          :equipment="equipment"
          @close="showMaintenanceModal = false"
          @saved="handleMaintenanceSaved"
        />

        <!-- Edit Log Modal -->
        <LogEditModal
          :show="showEditLogModal"
          :log="editingLog"
          @close="showEditLogModal = false"
          @save="handleEditLogSave"
          ref="editLogModalRef"
        />

        <!-- Quick Action Modal (from Log Double-Click) -->
        <QuickActionModal
          :show="showQuickStatusModal"
          :log="selectedLog"
          @close="showQuickStatusModal = false"
          @log-updated="handleQuickActionLogUpdate"
          @attachments-changed="handleAttachmentsChanged"
          ref="quickActionModalRef"
        />

        <!-- Note: Log Attachments Modal merged into QuickActionModal -->
        <!-- Attach Equipment Modal is now inside ChildrenEquipmentSection component -->
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import { useUiStore } from '@/stores/ui'
import { equipmentApi } from '@/api/equipment'
import { locationApi } from '@/api/locations'
import apiClient from '@/api/client'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import DeployEquipmentModal from '@/components/equipment/modals/DeployEquipmentModal.vue'
import ReturnEquipmentModal from '@/components/equipment/modals/ReturnEquipmentModal.vue'
import DetachFromParentModal from '@/components/equipment/modals/DetachFromParentModal.vue'
import AddMaintenanceRecordModal from '@/components/equipment/modals/AddMaintenanceRecordModal.vue'
import SendToRepairModal from '@/components/equipment/modals/SendToRepairModal.vue'
import SendToCalibrationModal from '@/components/equipment/modals/SendToCalibrationModal.vue'
import SetToInStockModal from '@/components/equipment/modals/SetToInStockModal.vue'
import SetToRentedModal from '@/components/equipment/modals/SetToRentedModal.vue'
import EquipmentLogSection from '@/components/equipment/sections/EquipmentLogSection.vue'
import ChildrenEquipmentSection from '@/components/equipment/sections/ChildrenEquipmentSection.vue'
import EquipmentHeaderSection from '@/components/equipment/sections/EquipmentHeaderSection.vue'
import StatusActionsCard from '@/components/equipment/sections/StatusActionsCard.vue'
import BasicInformationCard from '@/components/equipment/sections/BasicInformationCard.vue'
import LogEditModal from '@/components/equipment/log/LogEditModal.vue'
import QuickActionModal from '@/components/equipment/modals/QuickActionModal.vue'
import { useEquipmentLabels } from '@/composables/useEquipmentLabels'
import type { Equipment, EquipmentLog } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()
const uiStore = useUiStore()

// Composables
const { statusLabel, statusBadgeClass, categoryLabel, locationTypeLabel, formatDate, formatDateTime, logTypeLabel } = useEquipmentLabels()

const equipmentId = computed(() => parseInt(route.params.id as string))
const equipment = computed(() => equipmentStore.currentEquipment)

const qrCodeUrl = ref('')
const showDeployModal = ref(false)
const showReturnModal = ref(false)
const showMaintenanceModal = ref(false)

// Section refs
const logSection = ref<InstanceType<typeof EquipmentLogSection> | null>(null)
const childrenSection = ref<InstanceType<typeof ChildrenEquipmentSection> | null>(null)
const editLogModalRef = ref<InstanceType<typeof LogEditModal> | null>(null)
const quickActionModalRef = ref<InstanceType<typeof QuickActionModal> | null>(null)

const showRepairModal = ref(false)
const showCalibrationModal = ref(false)
const showInStockModal = ref(false)
const showRentedModal = ref(false)
const showQuickStatusModal = ref(false)
const quickStatusForm = ref({
  action: '',
  notes: '',
  includeChildren: true  // Default to true for convenience
})

// Locations for deploy/return
const locations = ref<any[]>([])

// Detach from Parent
const showDetachModal = ref(false)
const detachingChild = ref<Equipment | null>(null)

// Log selection (for Quick Action Modal)
const selectedLog = ref<EquipmentLog | null>(null)

// Log Editing
const showEditLogModal = ref(false)
const editingLog = ref<EquipmentLog | null>(null)
const updatingLog = ref(false)

// Children Equipment - list maintained for other components to access count
const childrenEquipment = ref<Equipment[]>([])

const canPerformActions = computed(() => {
  return equipment.value?.status !== 'disposed' && equipment.value?.status !== 'lost'
})

// Label functions moved to useEquipmentLabels composable

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

async function downloadQRCode() {
  if (!equipment.value) return

  try {
    // Use the authenticated API to get QR code
    const response = await equipmentApi.getQRCode(equipment.value.id)
    const qrCodeBase64 = response.data.qr_code_base64

    // Create a link and trigger download
    const link = document.createElement('a')
    link.href = qrCodeBase64
    link.download = `QR_${equipment.value.asset_code}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    uiStore.showNotification('success', 'QR Code downloaded successfully')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to download QR code')
  }
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

function executeStatusAction(action: string) {
  if (!equipment.value) return

  switch (action) {
    case 'deploy':
      showDeployModal.value = true
      break
    case 'return':
      showReturnModal.value = true
      break
    case 'repair':
      showRepairModal.value = true
      break
    case 'calibration':
      showCalibrationModal.value = true
      break
    case 'in_stock':
      showInStockModal.value = true
      break
    case 'rented':
      showRentedModal.value = true
      break
    case 'maintenance':
      showMaintenanceModal.value = true
      break
  }
}

async function handleSetStatus(status: string) {
  if (!equipment.value) return

  const notes = prompt(`Notes for setting status to "${statusLabel(status)}" (optional):`)
  if (notes === null) return

  try {
    // Use the update API to change status
    await equipmentApi.update(equipment.value.id, { status })
    uiStore.showNotification('success', `Equipment status changed to ${statusLabel(status)}`)
    // Refresh equipment data and logs
    await equipmentStore.fetchById(equipmentId.value)
    logSection.value?.loadLogs()
    childrenSection.value?.loadChildren()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to update status')
  }
}

async function handleRepairSubmitted() {
  // Refresh equipment data and logs after repair
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  childrenSection.value?.loadChildren()
}

async function handleCalibrationSubmitted() {
  // Refresh equipment data and logs after calibration
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  childrenSection.value?.loadChildren()
}

async function handleInStockSubmitted() {
  // Refresh equipment data and logs after setting to in stock
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  childrenSection.value?.loadChildren()
}

async function handleRentedSubmitted() {
  // Refresh equipment data and logs after setting to rented
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  childrenSection.value?.loadChildren()
}

async function handleDeployed() {
  // Refresh equipment data after deployment
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  childrenSection.value?.loadChildren()
}

async function handleReturned() {
  // Refresh equipment data after return
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  childrenSection.value?.loadChildren()
}

async function handleMaintenanceSaved(data: { last_maintenance_date?: string; next_maintenance_date?: string; maintenance_notes?: string }) {
  try {
    // Step 1: Add maintenance record (updates equipment and creates MAINTENANCE log)
    const response = await equipmentApi.addMaintenanceRecord(
      equipmentId.value,
      data.maintenance_notes,
      data.last_maintenance_date || undefined,
      data.next_maintenance_date || undefined
    )

    if (import.meta.env.DEV) console.log('Maintenance record response:', response.data)

    const logId = response.data.log_id

    // Step 2: If there are attachments, upload them to the maintenance log
    if (data.attachments && data.attachments.length > 0) {
      for (const file of data.attachments) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('attachment_type', 'maintenance_record')
        formData.append('description', file.name)

        // 使用 apiClient，會自動處理 CSRF token 和 cookies 認證
        await apiClient.post(
          `/uploads/equipment-logs/${logId}/attachments`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            }
          }
        )
      }

      uiStore.showNotification('success', `Maintenance record saved with ${data.attachments.length} attachment(s)`)
    } else {
      uiStore.showNotification('success', 'Maintenance record saved successfully')
    }

    showMaintenanceModal.value = false

    // Refresh equipment data and logs
    await equipmentStore.fetchById(equipmentId.value)
    logSection.value?.loadLogs()
  } catch (error: any) {
    console.error('Failed to save maintenance record:', error)
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to save maintenance record')
  }
}

async function handleChildrenUpdated() {
  // Refresh parent equipment data when children are updated
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
}

// locationTypeLabel moved to useEquipmentLabels composable

function handleLogDoubleClick(log: EquipmentLog) {
  if (!authStore.isOperator) return
  selectedLog.value = log
  showQuickStatusModal.value = true
}

function viewLogAttachmentsQuick(log: EquipmentLog) {
  selectedLog.value = log
  showQuickStatusModal.value = true
}

async function executeQuickStatusChange() {
  if (!equipment.value || !quickStatusForm.value.action) return

  const action = quickStatusForm.value.action
  const notes = quickStatusForm.value.notes || undefined
  const includeChildren = quickStatusForm.value.includeChildren && childrenEquipment.value.length > 0

  try {
    switch (action) {
      case 'deploy':
        showQuickStatusModal.value = false
        showDeployModal.value = true
        deployForm.value.notes = notes || ''
        deployForm.value.includeChildren = includeChildren
        break
      case 'return':
        showQuickStatusModal.value = false
        showReturnModal.value = true
        returnForm.value.notes = notes || ''
        returnForm.value.includeChildren = includeChildren
        break
      case 'repair':
      case 'calibration':
        // Use syncChildrenStatus API if includeChildren is enabled
        if (includeChildren) {
          const targetStatus = action === 'repair' ? 'repair' : 'calibrating'
          const response = await equipmentApi.syncChildrenStatus(equipment.value.id, {
            new_status: targetStatus,
            include_children: true,
            notes
          })
          uiStore.showNotification('success',
            `${response.data.updated_count} equipment(s) ${action === 'repair' ? 'sent to repair' : 'sent to calibration'}`
          )
        } else {
          // Original behavior for single equipment
          if (action === 'repair') {
            await equipmentApi.repair(equipment.value.id, notes)
            uiStore.showNotification('success', 'Equipment sent to repair')
          } else {
            await equipmentApi.sendToCalibration(equipment.value.id, notes)
            uiStore.showNotification('success', 'Equipment sent to calibration')
          }
        }
        showQuickStatusModal.value = false
        await equipmentStore.fetchById(equipmentId.value)
        logSection.value?.loadLogs()
        childrenSection.value?.loadChildren()
        break
      case 'in_stock':
      case 'rented':
        // Use syncChildrenStatus API if includeChildren is enabled
        if (includeChildren) {
          const response = await equipmentApi.syncChildrenStatus(equipment.value.id, {
            new_status: action,
            include_children: true,
            notes
          })
          uiStore.showNotification('success',
            `${response.data.updated_count} equipment(s) status changed to ${statusLabel(action)}`
          )
        } else {
          await equipmentApi.update(equipment.value.id, { status: action })
          uiStore.showNotification('success', `Equipment status changed to ${statusLabel(action)}`)
        }
        showQuickStatusModal.value = false
        await equipmentStore.fetchById(equipmentId.value)
        logSection.value?.loadLogs()
        childrenSection.value?.loadChildren()
        break
    }

    // Reset form
    quickStatusForm.value = { action: '', notes: '', includeChildren: true }
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to change status')
  }
}

// loadLogs() moved to EquipmentLogSection component

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

function openEditLogModal(log: EquipmentLog) {
  editingLog.value = log
  showEditLogModal.value = true
}

// Handle save from LogEditModal
async function handleEditLogSave(form: { description: string }) {
  if (!editingLog.value || !equipment.value) return

  editLogModalRef.value?.setSaving(true)

  try {
    await equipmentApi.updateLog(
      equipment.value.id,
      editingLog.value.id,
      { description: form.description }
    )

    uiStore.showNotification('success', 'Log updated successfully')
    showEditLogModal.value = false
    editingLog.value = null
    logSection.value?.loadLogs()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Update failed')
  } finally {
    editLogModalRef.value?.setSaving(false)
  }
}

// Handle log update from QuickActionModal
async function handleQuickActionLogUpdate(updatedLog: EquipmentLog) {
  if (!equipment.value) return

  quickActionModalRef.value?.setSaving(true)

  try {
    await equipmentApi.updateLog(
      equipment.value.id,
      updatedLog.id,
      { description: updatedLog.description }
    )

    uiStore.showNotification('success', 'Log updated successfully')
    showQuickStatusModal.value = false
    selectedLog.value = null
    logSection.value?.loadLogs()
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Update failed')
  } finally {
    quickActionModalRef.value?.setSaving(false)
  }
}

// Handle attachments change from QuickActionModal
function handleAttachmentsChanged() {
  // Optionally refresh log section if needed
  logSection.value?.loadLogs()
}

async function loadLocations() {
  try {
    const response = await locationApi.getAll({ limit: 100, is_active: true })
    locations.value = response.data.locations || []
  } catch (error) {
    console.error('Failed to load locations:', error)
  }
}

// ==================== Children Equipment Management ====================

// loadChildren(), openAttachEquipmentModal(), loadAvailableEquipment(), handleAttachEquipment()
// All moved to ChildrenEquipmentSection component

function handleDetachChild(child: Equipment) {
  // Open detach modal for user to select location and status
  detachingChild.value = child
  showDetachModal.value = true
}

function handleDetachModalClose() {
  showDetachModal.value = false
  detachingChild.value = null
}

async function handleDetached() {
  // Refresh equipment data after detachment
  childrenSection.value?.loadChildren()
  await equipmentStore.fetchById(equipmentId.value)
  logSection.value?.loadLogs()
  detachingChild.value = null
}

// Watch for route parameter changes (when navigating between equipment pages)
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    // Reset state to avoid showing stale data
    childrenEquipment.value = []

    // Load new equipment data
    await equipmentStore.fetchById(parseInt(newId as string))
    loadQRCode()
    // Note: Logs and Children sections will auto-reload via their own watchers
  }
})

onMounted(async () => {
  await equipmentStore.fetchById(equipmentId.value)
  loadQRCode()
  loadLocations()
  // Note: Logs and Children are loaded automatically by their respective section components
})
</script>
