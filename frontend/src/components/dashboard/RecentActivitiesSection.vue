<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <div class="px-4 sm:px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold text-gray-900">Recent Activities</h2>
        <!-- Log Type Filter + Admin Clear -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <label class="text-xs text-gray-600">Filter:</label>
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
          <!-- Admin Clear All Button -->
          <button
            v-if="isAdmin && activities.length > 0"
            @click="showClearConfirm = true"
            class="px-3 py-1 text-xs font-medium text-red-600 hover:text-red-800 hover:bg-red-50 border border-red-300 rounded-lg transition-colors"
            title="Clear all activities (Admin only)"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>

    <!-- Clear Confirmation Modal -->
    <div
      v-if="showClearConfirm"
      class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
      @click.self="showClearConfirm = false"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Clear All Activities</h3>
        <p class="text-sm text-gray-600 mb-4">
          Are you sure you want to delete all <span class="font-bold text-red-600">{{ activities.length }}</span> activity logs?
          This will clear ALL equipment logs across the system. This action cannot be undone.
        </p>
        <div class="flex justify-end gap-2">
          <button
            @click="showClearConfirm = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleClearAll"
            :disabled="clearing"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ clearing ? 'Deleting...' : 'Delete All' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Loading...</p>
    </div>

    <div v-else-if="filteredActivities.length === 0" class="text-center py-12">
      <p class="text-gray-500">{{ selectedLogType ? 'No activities found for this type' : 'No recent activities' }}</p>
    </div>

    <div v-else>
      <!-- Mobile: Card view -->
      <div class="block md:hidden divide-y divide-gray-200">
        <div v-for="activity in filteredActivities" :key="activity.id" class="p-4">
          <div class="flex justify-between items-start mb-2">
            <div class="flex items-center gap-2">
              <router-link
                :to="`/equipment/${activity.equipment_id}`"
                class="font-medium text-sky-600 hover:text-sky-800"
              >
                {{ activity.asset_code }}
              </router-link>
              <span :class="logTypeBadge(activity.log_type)" class="px-2 py-0.5 text-xs font-semibold rounded">
                {{ logTypeLabel(activity.log_type) }}
              </span>
            </div>
            <span class="text-xs text-gray-500">
              {{ formatDateTime(activity.created_at) }}
            </span>
          </div>
          <p class="text-sm text-gray-900">{{ activity.description }}</p>
          <p class="text-xs text-gray-600 mt-1">
            {{ activity.manufacturer }} {{ activity.model }}
          </p>

          <!-- Transfer Flow (Mobile) -->
          <div v-if="isTransferLog(activity)" class="flex items-center gap-2 mt-2 p-2 bg-gray-50 rounded-lg text-xs">
            <div class="flex items-center gap-1">
              <span v-if="parseLogInfo(activity.old_value)?.location" :class="['px-2 py-0.5 rounded', locationBadgeClass(parseLogInfo(activity.old_value)?.location?.type)]">
                {{ parseLogInfo(activity.old_value)?.location?.name || 'N/A' }}
              </span>
              <span v-else class="text-gray-400">N/A</span>
            </div>
            <span class="text-gray-400">-></span>
            <div class="flex items-center gap-1">
              <span v-if="parseLogInfo(activity.new_value)?.location" :class="['px-2 py-0.5 rounded', locationBadgeClass(parseLogInfo(activity.new_value)?.location?.type)]">
                {{ parseLogInfo(activity.new_value)?.location?.name || 'N/A' }}
              </span>
              <span v-else class="text-gray-400">N/A</span>
            </div>
          </div>

          <!-- Maintenance log (Mobile) -->
          <div v-else-if="isMaintenanceLog(activity)" class="flex flex-wrap gap-2 mt-2 p-2 bg-red-50 rounded-lg text-xs">
            <span class="text-gray-500">Last: {{ parseLogInfo(activity.new_value)?.last_maintenance_date || 'N/A' }}</span>
            <span class="text-gray-500">Next: {{ parseLogInfo(activity.new_value)?.next_maintenance_date || 'N/A' }}</span>
          </div>

          <!-- Status-only log (Mobile) -->
          <div v-else-if="isStatusOnlyLog(activity)" class="flex items-center gap-2 mt-2 p-2 bg-blue-50 rounded-lg text-xs">
            <span v-if="parseLogInfo(activity.old_value)?.status" class="px-2 py-0.5 bg-gray-200 text-gray-700 rounded">
              {{ parseLogInfo(activity.old_value)?.status }}
            </span>
            <span class="text-gray-400">-></span>
            <span class="px-2 py-0.5 bg-blue-200 text-blue-800 rounded">
              {{ parseLogInfo(activity.new_value)?.status }}
            </span>
          </div>

          <!-- Deactivate log (Mobile) -->
          <div v-else-if="isDeactivateLog(activity)" class="flex items-center gap-2 mt-2 p-2 bg-red-50 rounded-lg text-xs">
            <span class="px-2 py-0.5 bg-green-200 text-green-800 rounded">Active</span>
            <span class="text-gray-400">-></span>
            <span class="px-2 py-0.5 bg-red-200 text-red-800 rounded">Deactivated</span>
          </div>

          <!-- Project info -->
          <div v-if="activity.project_code" class="text-xs text-sky-700 mt-1">
            Project: {{ activity.project_code }}
          </div>

          <p v-if="activity.created_by_username" class="text-xs text-gray-500 mt-1">
            By: {{ activity.created_by_username }}
          </p>
        </div>
      </div>

      <!-- Desktop: Card-style Log -->
      <div class="hidden md:block divide-y divide-gray-200">
        <div
          v-for="activity in filteredActivities"
          :key="activity.id"
          class="p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex gap-4">
            <!-- Left: Date & Time (Vertical) -->
            <div class="flex-shrink-0 w-32 text-center border-r border-gray-200 pr-4">
              <div class="text-xs font-medium text-gray-500 mb-1">
                {{ new Date(activity.created_at).toLocaleDateString('zh-TW') }}
              </div>
              <div class="text-sm font-semibold text-gray-900">
                {{ new Date(activity.created_at).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }) }}
              </div>
              <div class="mt-2">
                <span :class="logTypeBadge(activity.log_type)" class="px-2 py-1 text-xs font-semibold rounded inline-block">
                  {{ logTypeLabel(activity.log_type) }}
                </span>
              </div>
            </div>

            <!-- Middle: Description & Details -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between mb-1">
                <div>
                  <router-link
                    :to="`/equipment/${activity.equipment_id}`"
                    class="text-sm font-medium text-sky-600 hover:text-sky-800"
                  >
                    {{ activity.asset_code }}
                  </router-link>
                  <span class="text-xs text-gray-500 ml-2">{{ activity.manufacturer }} {{ activity.model }}</span>
                </div>
              </div>

              <p class="text-sm text-gray-900 mb-1">{{ activity.description }}</p>

              <div class="text-xs text-gray-600 space-y-1">
                <!-- Handler (User who performed the action) -->
                <div v-if="activity.created_by_username" class="flex items-center gap-1">
                  <span class="text-gray-400">By:</span>
                  <span class="font-medium text-gray-700">{{ activity.created_by_username }}</span>
                </div>

                <!-- Transfer Flow (From -> To) -->
                <div v-if="isTransferLog(activity)" class="flex items-center gap-2 mt-2 p-2 bg-gray-50 rounded-lg">
                  <!-- From -->
                  <div class="flex items-center gap-1">
                    <span class="text-xs text-gray-500">From:</span>
                    <span v-if="parseLogInfo(activity.old_value)?.location" class="inline-flex items-center gap-1">
                      <span class="text-xs px-2 py-0.5 rounded" :class="locationBadgeClass(parseLogInfo(activity.old_value)?.location?.type)">
                        {{ parseLogInfo(activity.old_value)?.location?.name || 'N/A' }}
                      </span>
                    </span>
                    <span v-else class="text-xs text-gray-400">N/A</span>
                  </div>

                  <!-- Arrow -->
                  <span class="text-gray-400">-></span>

                  <!-- To -->
                  <div class="flex items-center gap-1">
                    <span class="text-xs text-gray-500">To:</span>
                    <span v-if="parseLogInfo(activity.new_value)?.location" class="inline-flex items-center gap-1">
                      <span class="text-xs px-2 py-0.5 rounded" :class="locationBadgeClass(parseLogInfo(activity.new_value)?.location?.type)">
                        {{ parseLogInfo(activity.new_value)?.location?.name || 'N/A' }}
                      </span>
                    </span>
                    <span v-else class="text-xs text-gray-400">N/A</span>
                  </div>
                </div>

                <!-- Maintenance log (show dates) -->
                <div v-else-if="isMaintenanceLog(activity)" class="flex items-center gap-4 mt-2 p-2 bg-red-50 rounded-lg text-xs">
                  <div class="flex items-center gap-1">
                    <span class="text-gray-500">Last:</span>
                    <span class="font-medium text-gray-700">{{ parseLogInfo(activity.new_value)?.last_maintenance_date || 'N/A' }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <span class="text-gray-500">Next:</span>
                    <span class="font-medium text-gray-700">{{ parseLogInfo(activity.new_value)?.next_maintenance_date || 'N/A' }}</span>
                  </div>
                </div>

                <!-- Status-only log (show status change) -->
                <div v-else-if="isStatusOnlyLog(activity)" class="flex items-center gap-2 mt-2 p-2 bg-blue-50 rounded-lg text-xs">
                  <span class="text-gray-500">Status:</span>
                  <span v-if="parseLogInfo(activity.old_value)?.status" class="px-2 py-0.5 bg-gray-200 text-gray-700 rounded">
                    {{ parseLogInfo(activity.old_value)?.status }}
                  </span>
                  <span class="text-gray-400">-></span>
                  <span class="px-2 py-0.5 bg-blue-200 text-blue-800 rounded font-medium">
                    {{ parseLogInfo(activity.new_value)?.status }}
                  </span>
                </div>

                <!-- Deactivate log -->
                <div v-else-if="isDeactivateLog(activity)" class="flex items-center gap-2 mt-2 p-2 bg-red-50 rounded-lg text-xs">
                  <span class="text-gray-500">Active:</span>
                  <span class="px-2 py-0.5 bg-green-200 text-green-800 rounded">True</span>
                  <span class="text-gray-400">-></span>
                  <span class="px-2 py-0.5 bg-red-200 text-red-800 rounded font-medium">False</span>
                </div>

                <!-- Project info -->
                <div v-if="activity.project_code" class="flex items-center gap-1 text-sky-700 mt-1">
                  <span class="font-medium">Project:</span> {{ activity.project_code }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useActivityLog, type ActivityLog } from '@/composables/useActivityLog'

interface Props {
  activities: ActivityLog[]
  loading?: boolean
  isAdmin?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  isAdmin: false,
})

const emit = defineEmits<{
  (e: 'clear-all'): void
}>()

const {
  formatDateTime,
  logTypeLabel,
  logTypeBadge,
  locationBadgeClass,
  parseLogInfo,
  isTransferLog,
  isMaintenanceLog,
  isStatusOnlyLog,
  isDeactivateLog,
} = useActivityLog()

const selectedLogType = ref('')
const showClearConfirm = ref(false)
const clearing = ref(false)

// Filtered activities based on selected log type
const filteredActivities = computed(() => {
  if (!selectedLogType.value) {
    return props.activities
  }
  return props.activities.filter(activity => activity.log_type === selectedLogType.value)
})

async function handleClearAll() {
  clearing.value = true
  try {
    emit('clear-all')
    showClearConfirm.value = false
  } finally {
    clearing.value = false
  }
}
</script>
