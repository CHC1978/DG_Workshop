<template>
  <div v-if="oldValue || newValue" class="p-3 bg-gray-50 rounded-lg">
    <p class="text-xs text-gray-500 mb-2 font-medium">Change Record</p>

    <!-- Transfer log (has location) -->
    <div v-if="isTransferLog" class="flex items-center gap-3 flex-wrap">
      <!-- From -->
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-500">From:</span>
        <span v-if="oldInfo?.location"
              :class="['text-sm px-2 py-1 rounded', getLocationBadgeClass(oldInfo.location.type)]">
          {{ oldInfo.location.name || 'N/A' }}
        </span>
        <span v-else class="text-sm text-gray-400">N/A</span>
      </div>
      <!-- Arrow -->
      <span class="text-gray-400 text-lg">→</span>
      <!-- To -->
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-500">To:</span>
        <span v-if="newInfo?.location"
              :class="['text-sm px-2 py-1 rounded', getLocationBadgeClass(newInfo.location.type)]">
          {{ newInfo.location.name || 'N/A' }}
        </span>
        <span v-else class="text-sm text-gray-400">N/A</span>
      </div>
      <!-- Status badge -->
      <span v-if="newInfo?.status"
            class="ml-auto text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
        {{ newInfo.status }}
      </span>
    </div>

    <!-- Maintenance log -->
    <div v-else-if="isMaintenanceLog" class="flex items-center gap-4 text-sm">
      <div class="flex items-center gap-1">
        <span class="text-gray-500">Last:</span>
        <span class="font-medium text-gray-700">{{ newInfo?.last_maintenance_date || 'N/A' }}</span>
      </div>
      <div class="flex items-center gap-1">
        <span class="text-gray-500">Next:</span>
        <span class="font-medium text-gray-700">{{ newInfo?.next_maintenance_date || 'N/A' }}</span>
      </div>
    </div>

    <!-- Status-only log -->
    <div v-else-if="isStatusOnlyLog" class="flex items-center gap-2 text-sm">
      <span class="text-gray-500">Status:</span>
      <span v-if="oldInfo?.status" class="px-2 py-0.5 bg-gray-200 text-gray-700 rounded">
        {{ oldInfo.status }}
      </span>
      <span class="text-gray-400">→</span>
      <span class="px-2 py-0.5 bg-blue-200 text-blue-800 rounded font-medium">
        {{ newInfo?.status }}
      </span>
    </div>

    <!-- Deactivate log -->
    <div v-else-if="isDeactivateLog" class="flex items-center gap-2 text-sm">
      <span class="text-gray-500">Active:</span>
      <span class="px-2 py-0.5 bg-green-200 text-green-800 rounded">True</span>
      <span class="text-gray-400">→</span>
      <span class="px-2 py-0.5 bg-red-200 text-red-800 rounded font-medium">False</span>
    </div>

    <!-- Fallback for old format -->
    <div v-else class="text-sm text-gray-600 space-y-1">
      <p v-if="oldValue">Old: {{ oldValue }}</p>
      <p v-if="newValue">New: {{ newValue }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface LogInfo {
  status?: string
  location?: {
    id?: number
    name?: string
    type?: string
  }
  is_active?: boolean
  last_maintenance_date?: string
  next_maintenance_date?: string
  parent_equipment_id?: number | null
  parent_asset_code?: string
}

interface Props {
  oldValue?: string
  newValue?: string
}

const props = defineProps<Props>()

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

const oldInfo = computed(() => parseLogInfo(props.oldValue))
const newInfo = computed(() => parseLogInfo(props.newValue))

const isTransferLog = computed(() => {
  return newInfo.value?.location !== undefined
})

const isMaintenanceLog = computed(() => {
  return newInfo.value?.last_maintenance_date !== undefined ||
         newInfo.value?.next_maintenance_date !== undefined
})

const isStatusOnlyLog = computed(() => {
  return newInfo.value?.status !== undefined &&
         newInfo.value?.location === undefined &&
         newInfo.value?.is_active === undefined &&
         newInfo.value?.last_maintenance_date === undefined
})

const isDeactivateLog = computed(() => {
  return newInfo.value?.is_active !== undefined
})

function getLocationBadgeClass(type?: string): string {
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
</script>
