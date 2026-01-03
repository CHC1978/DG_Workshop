<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <div class="px-6 py-4 border-b border-gray-200 sticky top-0 bg-white z-10">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Activity Log</h2>
          <p class="text-xs text-gray-500 mt-1">Double-click a log to quick-edit status</p>
        </div>
        <!-- Log Type Filter + Admin Clear -->
        <div class="flex items-center gap-3">
          <div>
            <label class="text-xs text-gray-600 mr-2">Filter:</label>
            <select
              v-model="selectedLogType"
              class="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="maintenance">Maintenance</option>
              <option value="calibration">Calibration</option>
              <option value="status_change">Status Change</option>
              <option value="location_change">Location Change</option>
              <option value="rental_start">Rental Start</option>
              <option value="rental_end">Rental End</option>
              <option value="note">Note</option>
              <option value="created">Created</option>
              <option value="updated">Updated</option>
            </select>
          </div>
          <!-- Admin Clear All Logs Button -->
          <button
            v-if="isAdmin && logs.length > 0"
            @click="confirmClearLogs"
            class="px-3 py-1 text-xs font-medium text-red-600 hover:text-red-800 hover:bg-red-50 border border-red-300 rounded-lg transition-colors"
            title="Clear all logs (Admin only)"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>

    <!-- Clear Logs Confirmation Modal -->
    <div
      v-if="showClearConfirm"
      class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
      @click.self="showClearConfirm = false"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Clear All Logs</h3>
        <p class="text-sm text-gray-600 mb-4">
          Are you sure you want to delete all <span class="font-bold text-red-600">{{ logs.length }}</span> logs for this equipment?
          This action cannot be undone.
        </p>
        <div class="flex justify-end gap-2">
          <button
            @click="showClearConfirm = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            @click="clearAllLogs"
            :disabled="clearing"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ clearing ? 'Deleting...' : 'Delete All' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Logs Container with fixed min-height to prevent jumping -->
    <div class="logs-container" style="min-height: 400px;">
      <div v-if="filteredLogs.length === 0" class="text-center py-12 text-gray-500">
        {{ selectedLogType ? 'No logs found for this type' : 'No activity logs yet' }}
      </div>

      <!-- Desktop: Card-style Log -->
      <div v-else class="hidden md:block divide-y divide-gray-200">
        <div
          v-for="log in filteredLogs"
          :key="log.id"
          class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
          @dblclick="$emit('logDoubleClicked', log)"
        >
        <div class="flex gap-4">
          <!-- Left: Date & Time (Vertical) -->
          <div class="flex-shrink-0 w-32 text-center border-r border-gray-200 pr-4">
            <div class="text-xs font-medium text-gray-500 mb-1">
              {{ new Date(log.created_at).toLocaleDateString('zh-TW') }}
            </div>
            <div class="text-sm font-semibold text-gray-900">
              {{ new Date(log.created_at).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }) }}
            </div>
            <div class="mt-2">
              <span :class="logTypeBadge(log.log_type)" class="px-2 py-1 text-xs font-semibold rounded inline-block">
                {{ logTypeLabel(log.log_type) }}
              </span>
            </div>
          </div>

          <!-- Middle: Description & Details -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between mb-1">
              <p class="text-sm font-medium text-gray-900">
                {{ log.description }}
                <span v-if="log.is_edited" class="ml-2 text-xs text-gray-400" :title="`Edited ${log.edit_count} time(s)`">
                  (edited ×{{ log.edit_count }})
                </span>
              </p>
            </div>

            <div class="text-xs text-gray-600 space-y-1">
              <!-- Handler (User who performed the action) -->
              <div v-if="log.created_by_username" class="flex items-center gap-1">
                <span class="text-gray-400">By:</span>
                <span class="font-medium text-gray-700">{{ log.created_by_username }}</span>
              </div>

              <!-- Transfer Flow (From → To) for location change logs -->
              <div v-if="isTransferLog(log)" class="flex items-center gap-2 mt-2 p-2 bg-gray-50 rounded-lg">
                <!-- From -->
                <div class="flex items-center gap-1">
                  <span class="text-xs text-gray-500">From:</span>
                  <span v-if="parseLogInfo(log.old_value)?.location" class="inline-flex items-center gap-1">
                    <span class="text-xs px-2 py-0.5 rounded" :class="locationBadgeClass(parseLogInfo(log.old_value)?.location?.type)">
                      {{ parseLogInfo(log.old_value)?.location?.name || 'N/A' }}
                    </span>
                  </span>
                  <span v-else class="text-xs text-gray-400">N/A</span>
                </div>

                <!-- Arrow -->
                <span class="text-gray-400">→</span>

                <!-- To -->
                <div class="flex items-center gap-1">
                  <span class="text-xs text-gray-500">To:</span>
                  <span v-if="parseLogInfo(log.new_value)?.location" class="inline-flex items-center gap-1">
                    <span class="text-xs px-2 py-0.5 rounded" :class="locationBadgeClass(parseLogInfo(log.new_value)?.location?.type)">
                      {{ parseLogInfo(log.new_value)?.location?.name || 'N/A' }}
                    </span>
                  </span>
                  <span v-else class="text-xs text-gray-400">N/A</span>
                </div>
              </div>

              <!-- Maintenance log (show dates) -->
              <div v-else-if="isMaintenanceLog(log)" class="flex items-center gap-4 mt-2 p-2 bg-red-50 rounded-lg text-xs">
                <div class="flex items-center gap-1">
                  <span class="text-gray-500">Last:</span>
                  <span class="font-medium text-gray-700">{{ parseLogInfo(log.new_value)?.last_maintenance_date || 'N/A' }}</span>
                </div>
                <div class="flex items-center gap-1">
                  <span class="text-gray-500">Next:</span>
                  <span class="font-medium text-gray-700">{{ parseLogInfo(log.new_value)?.next_maintenance_date || 'N/A' }}</span>
                </div>
              </div>

              <!-- Status-only log (show status change) -->
              <div v-else-if="isStatusOnlyLog(log)" class="flex items-center gap-2 mt-2 p-2 bg-blue-50 rounded-lg text-xs">
                <span class="text-gray-500">Status:</span>
                <span v-if="parseLogInfo(log.old_value)?.status" class="px-2 py-0.5 bg-gray-200 text-gray-700 rounded">
                  {{ parseLogInfo(log.old_value)?.status }}
                </span>
                <span class="text-gray-400">→</span>
                <span class="px-2 py-0.5 bg-blue-200 text-blue-800 rounded font-medium">
                  {{ parseLogInfo(log.new_value)?.status }}
                </span>
              </div>

              <!-- Deactivate log -->
              <div v-else-if="isDeactivateLog(log)" class="flex items-center gap-2 mt-2 p-2 bg-red-50 rounded-lg text-xs">
                <span class="text-gray-500">Active:</span>
                <span class="px-2 py-0.5 bg-green-200 text-green-800 rounded">True</span>
                <span class="text-gray-400">→</span>
                <span class="px-2 py-0.5 bg-red-200 text-red-800 rounded font-medium">False</span>
              </div>
              <div v-if="log.project_code" class="flex items-center gap-1 text-sky-700">
                <span>📋</span>
                <span class="font-medium">Project:</span> {{ log.project_code }}
              </div>
              <div v-if="log.latitude && log.longitude" class="text-gray-500">
                GPS: {{ log.latitude.toFixed(4) }}, {{ log.longitude.toFixed(4) }}
              </div>
            </div>
          </div>

          <!-- Right: Attachments & Actions -->
          <div class="flex-shrink-0 flex flex-col items-end gap-1">
            <!-- Attachment buttons if has attachments -->
            <div v-if="log.attachment_count > 0" class="flex items-center gap-1">
              <a
                v-for="att in log.attachments.slice(0, 2)"
                :key="att.id"
                :href="getAttachmentUrl(att.file_url)"
                target="_blank"
                class="text-xs px-2 py-1 text-green-600 hover:text-green-800 hover:bg-green-50 rounded transition-colors"
                :title="`View: ${att.file_name}`"
                @click.stop
              >
                📎 {{ truncateFileName(att.file_name) }}
              </a>
              <span v-if="log.attachment_count > 2" class="text-xs text-gray-500">
                +{{ log.attachment_count - 2 }}
              </span>
            </div>
            <!-- View/Edit button -->
            <button
              @click.stop="$emit('viewAttachments', log)"
              class="text-xs px-2 py-1 text-sky-600 hover:text-sky-800 hover:bg-sky-50 rounded transition-colors"
              title="View details and manage attachments"
            >
              {{ log.attachment_count > 0 ? 'Manage' : 'View' }}
            </button>
          </div>
        </div>
      </div>
      </div>

      <!-- Mobile: Simplified Card Log -->
      <div v-if="filteredLogs.length > 0" class="block md:hidden divide-y divide-gray-200">
        <div
          v-for="log in filteredLogs"
          :key="log.id"
          class="p-4 active:bg-gray-100"
          @dblclick="$emit('logDoubleClicked', log)"
        >
          <div class="flex items-start justify-between mb-2">
            <div class="flex-1">
              <div class="text-xs text-gray-500 mb-1">
                {{ formatDateTime(log.created_at) }}
              </div>
              <span :class="logTypeBadge(log.log_type)" class="px-2 py-1 text-xs font-semibold rounded">
                {{ logTypeLabel(log.log_type) }}
              </span>
            </div>
            <!-- Right: Attachments & Actions (Mobile) -->
            <div class="flex flex-col items-end gap-1">
              <div v-if="log.attachment_count > 0" class="flex items-center gap-1">
                <a
                  v-for="att in log.attachments.slice(0, 1)"
                  :key="att.id"
                  :href="getAttachmentUrl(att.file_url)"
                  target="_blank"
                  class="text-xs px-2 py-1 text-green-600 hover:text-green-800"
                  @click.stop
                >
                  📎 {{ log.attachment_count }} file(s)
                </a>
              </div>
              <button
                @click.stop="$emit('viewAttachments', log)"
                class="text-xs px-2 py-1 text-sky-600 hover:text-sky-800"
              >
                {{ log.attachment_count > 0 ? 'Manage' : 'View' }}
              </button>
            </div>
          </div>

          <!-- Description -->
          <p class="text-sm text-gray-900 mb-1">{{ log.description }}</p>

          <!-- Handler -->
          <div v-if="log.created_by_username" class="text-xs text-gray-600 mb-1">
            <span class="text-gray-400">By:</span>
            <span class="font-medium text-gray-700 ml-1">{{ log.created_by_username }}</span>
          </div>

          <!-- Transfer Flow (Mobile) -->
          <div v-if="isTransferLog(log)" class="flex items-center gap-2 mt-2 p-2 bg-gray-50 rounded-lg text-xs">
            <div class="flex items-center gap-1">
              <span v-if="parseLogInfo(log.old_value)?.location" :class="['px-2 py-0.5 rounded', locationBadgeClass(parseLogInfo(log.old_value)?.location?.type)]">
                {{ parseLogInfo(log.old_value)?.location?.name || 'N/A' }}
              </span>
              <span v-else class="text-gray-400">N/A</span>
            </div>
            <span class="text-gray-400">→</span>
            <div class="flex items-center gap-1">
              <span v-if="parseLogInfo(log.new_value)?.location" :class="['px-2 py-0.5 rounded', locationBadgeClass(parseLogInfo(log.new_value)?.location?.type)]">
                {{ parseLogInfo(log.new_value)?.location?.name || 'N/A' }}
              </span>
              <span v-else class="text-gray-400">N/A</span>
            </div>
          </div>

          <!-- Maintenance log (Mobile) -->
          <div v-else-if="isMaintenanceLog(log)" class="flex flex-wrap gap-2 mt-2 p-2 bg-red-50 rounded-lg text-xs">
            <span class="text-gray-500">Last: {{ parseLogInfo(log.new_value)?.last_maintenance_date || 'N/A' }}</span>
            <span class="text-gray-500">Next: {{ parseLogInfo(log.new_value)?.next_maintenance_date || 'N/A' }}</span>
          </div>

          <!-- Status-only log (Mobile) -->
          <div v-else-if="isStatusOnlyLog(log)" class="flex items-center gap-2 mt-2 p-2 bg-blue-50 rounded-lg text-xs">
            <span v-if="parseLogInfo(log.old_value)?.status" class="px-2 py-0.5 bg-gray-200 text-gray-700 rounded">
              {{ parseLogInfo(log.old_value)?.status }}
            </span>
            <span class="text-gray-400">→</span>
            <span class="px-2 py-0.5 bg-blue-200 text-blue-800 rounded">
              {{ parseLogInfo(log.new_value)?.status }}
            </span>
          </div>

          <!-- Deactivate log (Mobile) -->
          <div v-else-if="isDeactivateLog(log)" class="flex items-center gap-2 mt-2 p-2 bg-red-50 rounded-lg text-xs">
            <span class="px-2 py-0.5 bg-green-200 text-green-800 rounded">Active</span>
            <span class="text-gray-400">→</span>
            <span class="px-2 py-0.5 bg-red-200 text-red-800 rounded">Deactivated</span>
          </div>

          <!-- Project info -->
          <div v-if="log.project_code" class="text-xs text-sky-700 mt-1">
            📋 {{ log.project_code }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { equipmentApi } from '@/api/equipment'

interface Props {
  equipmentId: number
  isAdmin?: boolean
}

interface Emits {
  (e: 'logDoubleClicked', log: any): void
  (e: 'viewAttachments', log: any): void
  (e: 'logsCleared'): void
}

const props = withDefaults(defineProps<Props>(), {
  isAdmin: false
})
const emit = defineEmits<Emits>()

const logs = ref<any[]>([])
const selectedLogType = ref('')
const showClearConfirm = ref(false)
const clearing = ref(false)

// Filtered logs based on selected type
const filteredLogs = computed(() => {
  if (!selectedLogType.value) {
    return logs.value
  }
  return logs.value.filter(log => log.log_type === selectedLogType.value)
})

// Watch equipmentId and auto-load logs
watch(() => props.equipmentId, async (newId) => {
  if (newId) {
    await loadLogs()
  }
}, { immediate: true })

async function loadLogs() {
  if (!props.equipmentId) return

  try {
    const response = await equipmentApi.getLogs(props.equipmentId)
    logs.value = response.data
  } catch (error) {
    console.error('Failed to load logs:', error)
  }
}

function confirmClearLogs() {
  showClearConfirm.value = true
}

async function clearAllLogs() {
  if (!props.equipmentId) return

  clearing.value = true
  try {
    await equipmentApi.clearLogs(props.equipmentId)
    logs.value = []
    showClearConfirm.value = false
    emit('logsCleared')
  } catch (error) {
    console.error('Failed to clear logs:', error)
  } finally {
    clearing.value = false
  }
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

function locationTypeLabel(type?: string): string {
  if (!type) return ''
  const labels: Record<string, string> = {
    warehouse: 'Warehouse',
    vessel: 'Vessel',
    person: 'Person',
    external: 'External',
    platform: 'Platform',
    vehicle: 'Vehicle',
  }
  return labels[type] || type
}

// Parse JSON log info from old_value/new_value
interface LogInfo {
  status?: string
  location?: {
    id?: number
    name?: string
    type?: string
  }
  // Extended fields
  is_active?: boolean
  last_maintenance_date?: string
  next_maintenance_date?: string
  parent_equipment_id?: number | null
  parent_asset_code?: string
}

function parseLogInfo(value?: string): LogInfo | null {
  if (!value) return null
  try {
    if (value.startsWith('{')) {
      return JSON.parse(value) as LogInfo
    }
    return null
  } catch {
    return null
  }
}

// Alias for backward compatibility
function parseTransferInfo(value?: string): LogInfo | null {
  return parseLogInfo(value)
}

// Check if this is a JSON formatted log
function isJsonLog(log: any): boolean {
  if (!log.new_value || !log.new_value.startsWith('{')) return false
  try {
    JSON.parse(log.new_value)
    return true
  } catch {
    return false
  }
}

// Check if this is a transfer log (has location info)
function isTransferLog(log: any): boolean {
  if (!log.new_value || !log.new_value.startsWith('{')) return false
  try {
    const parsed = JSON.parse(log.new_value)
    return parsed.location !== undefined
  } catch {
    return false
  }
}

// Check if this is a maintenance log (has maintenance dates)
function isMaintenanceLog(log: any): boolean {
  if (!log.new_value || !log.new_value.startsWith('{')) return false
  try {
    const parsed = JSON.parse(log.new_value)
    return parsed.last_maintenance_date !== undefined || parsed.next_maintenance_date !== undefined
  } catch {
    return false
  }
}

// Check if this is a delete/deactivate log
function isDeactivateLog(log: any): boolean {
  if (!log.new_value || !log.new_value.startsWith('{')) return false
  try {
    const parsed = JSON.parse(log.new_value)
    return parsed.is_active !== undefined
  } catch {
    return false
  }
}

// Check if this is a status-only log (no location)
function isStatusOnlyLog(log: any): boolean {
  if (!log.new_value || !log.new_value.startsWith('{')) return false
  try {
    const parsed = JSON.parse(log.new_value)
    return parsed.status !== undefined && parsed.location === undefined
  } catch {
    return false
  }
}

// Badge class for location type
function locationBadgeClass(type?: string): string {
  const classes: Record<string, string> = {
    warehouse: 'bg-amber-100 text-amber-800',
    vessel: 'bg-blue-100 text-blue-800',
    person: 'bg-green-100 text-green-800',
    external: 'bg-purple-100 text-purple-800',
    platform: 'bg-cyan-100 text-cyan-800',
    vehicle: 'bg-orange-100 text-orange-800',
  }
  return classes[type || ''] || 'bg-gray-100 text-gray-800'
}

function getAttachmentUrl(fileUrl: string): string {
  // Ensure URL starts with /
  return fileUrl.startsWith('/') ? fileUrl : `/${fileUrl}`
}

function truncateFileName(fileName: string, maxLength: number = 12): string {
  if (fileName.length <= maxLength) return fileName
  const ext = fileName.lastIndexOf('.')
  if (ext > 0) {
    const name = fileName.substring(0, ext)
    const extension = fileName.substring(ext)
    const truncatedName = name.substring(0, maxLength - extension.length - 2)
    return `${truncatedName}..${extension}`
  }
  return fileName.substring(0, maxLength - 2) + '..'
}

// Expose reload method for parent component
defineExpose({
  loadLogs
})
</script>

<style scoped>
.logs-container {
  transition: all 0.2s ease-in-out;
}
</style>
