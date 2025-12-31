<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <div class="px-6 py-4 border-b border-gray-200 sticky top-0 bg-white z-10">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Activity Log</h2>
          <p class="text-xs text-gray-500 mt-1">Double-click a log to quick-edit status</p>
        </div>
        <!-- Log Type Filter -->
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
              <div v-if="log.created_by_username">
                <span class="font-medium">User:</span> {{ log.created_by_username }}
              </div>
              <div v-if="log.new_value">
                <span class="font-medium">Details:</span> {{ log.new_value }}
              </div>
              <div v-if="log.current_location_name" class="flex items-center gap-1">
                <span>📍</span>
                <span class="font-medium">{{ locationTypeLabel(log.current_location_type) }}:</span>
                {{ log.current_location_name }}
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

          <!-- Right: View Attachments Button -->
          <div class="flex-shrink-0">
            <button
              @click.stop="$emit('viewAttachments', log)"
              class="text-xs px-2 py-1 text-sky-600 hover:text-sky-800 hover:bg-sky-50 rounded transition-colors"
              title="View attachments and actions"
            >
              View
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
            <button
              @click.stop="$emit('viewAttachments', log)"
              class="text-xs px-2 py-1 text-sky-600 hover:text-sky-800"
            >
              View
            </button>
          </div>
          <p class="text-sm text-gray-900 mb-1">{{ log.description }}</p>
          <div v-if="log.current_location_name || log.project_code" class="text-xs text-gray-600 space-y-0.5">
            <div v-if="log.current_location_name">
              📍 {{ locationTypeLabel(log.current_location_type) }}: {{ log.current_location_name }}
            </div>
            <div v-if="log.project_code" class="text-sky-700">
              📋 {{ log.project_code }}
            </div>
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
}

interface Emits {
  (e: 'logDoubleClicked', log: any): void
  (e: 'viewAttachments', log: any): void
}

const props = defineProps<Props>()
defineEmits<Emits>()

const logs = ref<any[]>([])
const selectedLogType = ref('')

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
