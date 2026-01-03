<template>
  <MainLayout>
    <div class="space-y-6">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h1>

      <!-- Dashboard Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <!-- In Stock -->
        <div
          class="bg-white rounded-lg shadow p-4 sm:p-6 cursor-pointer hover:shadow-lg transition-shadow"
          @click="navigateToEquipment('in_stock')"
        >
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">In Stock</h2>
            <span class="text-2xl">📦</span>
          </div>
          <p class="text-3xl font-bold text-green-600">{{ stats.in_stock || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">庫存設備</p>
        </div>

        <!-- Deployed -->
        <div
          class="bg-white rounded-lg shadow p-4 sm:p-6 cursor-pointer hover:shadow-lg transition-shadow"
          @click="navigateToEquipment('deployed')"
        >
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Deployed</h2>
            <span class="text-2xl">🚢</span>
          </div>
          <p class="text-3xl font-bold text-blue-600">{{ stats.deployed || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">已部署設備</p>
        </div>

        <!-- In Repair -->
        <div
          class="bg-white rounded-lg shadow p-4 sm:p-6 cursor-pointer hover:shadow-lg transition-shadow"
          @click="navigateToEquipment('repair')"
        >
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">In Repair</h2>
            <span class="text-2xl">🔧</span>
          </div>
          <p class="text-3xl font-bold text-orange-600">{{ stats.in_repair || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">維修中設備</p>
        </div>

        <!-- Rented -->
        <div
          class="bg-white rounded-lg shadow p-4 sm:p-6 cursor-pointer hover:shadow-lg transition-shadow"
          @click="navigateToEquipment('rented')"
        >
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Rented</h2>
            <span class="text-2xl">📋</span>
          </div>
          <p class="text-3xl font-bold text-purple-600">{{ stats.rented || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">租賃中設備</p>
        </div>

        <!-- Maintenance Due -->
        <div
          class="bg-white rounded-lg shadow p-4 sm:p-6 cursor-pointer hover:shadow-lg transition-shadow"
          @click="router.push('/maintenance')"
        >
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Maintenance Due</h2>
            <span class="text-2xl">⚠️</span>
          </div>
          <p class="text-3xl font-bold text-orange-600">{{ stats.maintenance_due_soon || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">需要維護</p>
        </div>

        <!-- Calibration Due -->
        <div
          class="bg-white rounded-lg shadow p-4 sm:p-6 cursor-pointer hover:shadow-lg transition-shadow"
          @click="router.push('/calibrations')"
        >
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Calibration Due</h2>
            <span class="text-2xl">📊</span>
          </div>
          <p class="text-3xl font-bold text-yellow-600">{{ stats.calibration_due_soon || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">需要校正</p>
        </div>

        <!-- Overdue Rentals -->
        <div
          class="bg-white rounded-lg shadow p-4 sm:p-6 cursor-pointer hover:shadow-lg transition-shadow"
          @click="router.push('/rentals')"
        >
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Overdue Rentals</h2>
            <span class="text-2xl">⏰</span>
          </div>
          <p class="text-3xl font-bold text-red-600">{{ stats.overdue_rentals || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">逾期未還</p>
        </div>
      </div>

      <!-- Recent Activities -->
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
                v-if="isAdmin && recentActivities.length > 0"
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
              Are you sure you want to delete all <span class="font-bold text-red-600">{{ recentActivities.length }}</span> activity logs?
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
                @click="clearAllActivities"
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
                <span class="text-gray-400">→</span>
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
                <span class="text-gray-400">→</span>
                <span class="px-2 py-0.5 bg-blue-200 text-blue-800 rounded">
                  {{ parseLogInfo(activity.new_value)?.status }}
                </span>
              </div>

              <!-- Deactivate log (Mobile) -->
              <div v-else-if="isDeactivateLog(activity)" class="flex items-center gap-2 mt-2 p-2 bg-red-50 rounded-lg text-xs">
                <span class="px-2 py-0.5 bg-green-200 text-green-800 rounded">Active</span>
                <span class="text-gray-400">→</span>
                <span class="px-2 py-0.5 bg-red-200 text-red-800 rounded">Deactivated</span>
              </div>

              <!-- Project info -->
              <div v-if="activity.project_code" class="text-xs text-sky-700 mt-1">
                📋 {{ activity.project_code }}
              </div>

              <p v-if="activity.created_by_username" class="text-xs text-gray-500 mt-1">
                By: {{ activity.created_by_username }}
              </p>
            </div>
          </div>

          <!-- Desktop: Card-style Log (same as Activity Log) -->
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

                    <!-- Transfer Flow (From → To) -->
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
                      <span class="text-gray-400">→</span>

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
                      <span class="text-gray-400">→</span>
                      <span class="px-2 py-0.5 bg-blue-200 text-blue-800 rounded font-medium">
                        {{ parseLogInfo(activity.new_value)?.status }}
                      </span>
                    </div>

                    <!-- Deactivate log -->
                    <div v-else-if="isDeactivateLog(activity)" class="flex items-center gap-2 mt-2 p-2 bg-red-50 rounded-lg text-xs">
                      <span class="text-gray-500">Active:</span>
                      <span class="px-2 py-0.5 bg-green-200 text-green-800 rounded">True</span>
                      <span class="text-gray-400">→</span>
                      <span class="px-2 py-0.5 bg-red-200 text-red-800 rounded font-medium">False</span>
                    </div>

                    <!-- Project info -->
                    <div v-if="activity.project_code" class="flex items-center gap-1 text-sky-700 mt-1">
                      <span>📋</span>
                      <span class="font-medium">Project:</span> {{ activity.project_code }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardApi, type DashboardAlerts, type DashboardStats, type RecentActivity } from '@/api/dashboard'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/layouts/MainLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const showClearConfirm = ref(false)
const clearing = ref(false)

// Check if current user is admin
const isAdmin = computed(() => authStore.user?.role === 'admin')

const stats = ref<DashboardStats>({
  total_equipment: 0,
  in_stock: 0,
  deployed: 0,
  rented: 0,
  in_repair: 0,
  active_rentals: 0,
  maintenance_due_soon: 0,
  calibration_due_soon: 0,
  overdue_rentals: 0,
})
const alerts = ref<DashboardAlerts>({
  maintenance_alerts: [],
  calibration_alerts: [],
  overdue_rentals: [],
})
const recentActivities = ref<RecentActivity[]>([])
const selectedLogType = ref('')

// Filtered activities based on selected log type
const filteredActivities = computed(() => {
  if (!selectedLogType.value) {
    return recentActivities.value
  }
  return recentActivities.value.filter(activity => activity.log_type === selectedLogType.value)
})

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

function logTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    status_change: 'Status',
    location_change: 'Location',
    rental_start: 'Rental',
    rental_end: 'Return',
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

// Check if this is a transfer log (has location info)
function isTransferLog(activity: any): boolean {
  if (!activity.new_value || !activity.new_value.startsWith('{')) return false
  try {
    const parsed = JSON.parse(activity.new_value)
    return parsed.location !== undefined
  } catch {
    return false
  }
}

// Check if this is a maintenance log (has maintenance dates)
function isMaintenanceLog(activity: any): boolean {
  if (!activity.new_value || !activity.new_value.startsWith('{')) return false
  try {
    const parsed = JSON.parse(activity.new_value)
    return parsed.last_maintenance_date !== undefined || parsed.next_maintenance_date !== undefined
  } catch {
    return false
  }
}

// Check if this is a status-only log (no location)
function isStatusOnlyLog(activity: any): boolean {
  if (!activity.new_value || !activity.new_value.startsWith('{')) return false
  try {
    const parsed = JSON.parse(activity.new_value)
    return parsed.status !== undefined && parsed.location === undefined
  } catch {
    return false
  }
}

// Check if this is a delete/deactivate log
function isDeactivateLog(activity: any): boolean {
  if (!activity.new_value || !activity.new_value.startsWith('{')) return false
  try {
    const parsed = JSON.parse(activity.new_value)
    return parsed.is_active !== undefined
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

function navigateToEquipment(status: string) {
  router.push({
    path: '/equipment',
    query: { status }
  })
}

async function loadDashboard() {
  loading.value = true
  try {
    const [statsRes, alertsRes, activitiesRes] = await Promise.all([
      dashboardApi.getStats(),
      dashboardApi.getAlerts(),
      dashboardApi.getRecentActivities(10),
    ])

    stats.value = statsRes.data
    alerts.value = alertsRes.data
    recentActivities.value = activitiesRes.data
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  } finally {
    loading.value = false
  }
}

async function clearAllActivities() {
  clearing.value = true
  try {
    await dashboardApi.clearActivities()
    recentActivities.value = []
    showClearConfirm.value = false
  } catch (error) {
    console.error('Failed to clear activities:', error)
  } finally {
    clearing.value = false
  }
}

onMounted(() => {
  loadDashboard()
})
</script>
