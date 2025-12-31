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
          @click="router.push('/equipment')"
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
            <!-- Log Type Filter -->
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
                <router-link
                  :to="`/equipment/${activity.equipment_id}`"
                  class="font-medium text-sky-600 hover:text-sky-800"
                >
                  {{ activity.asset_code }}
                </router-link>
                <span class="text-xs text-gray-500">
                  {{ formatDateTime(activity.created_at) }}
                </span>
              </div>
              <p class="text-sm text-gray-900">{{ activity.description }}</p>
              <p class="text-xs text-gray-600 mt-1">
                {{ activity.manufacturer }} {{ activity.model }}
              </p>
              <!-- Location and Project -->
              <div class="flex flex-wrap gap-2 mt-2">
                <span v-if="activity.current_location_name" class="text-xs text-gray-600">
                  📍 {{ locationTypeLabel(activity.current_location_type) }}: {{ activity.current_location_name }}
                </span>
                <span v-if="activity.project_code" class="text-xs text-sky-700">
                  📋 {{ activity.project_code }}
                </span>
              </div>
              <p v-if="activity.created_by_username" class="text-xs text-gray-500 mt-1">
                By: {{ activity.created_by_username }}
              </p>
            </div>
          </div>

          <!-- Desktop: Table view -->
          <div class="hidden md:block overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Equipment</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="activity in filteredActivities" :key="activity.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDateTime(activity.created_at) }}
                  </td>
                  <td class="px-6 py-4">
                    <router-link
                      :to="`/equipment/${activity.equipment_id}`"
                      class="text-sm font-medium text-sky-600 hover:text-sky-800"
                    >
                      {{ activity.asset_code }}
                    </router-link>
                    <p class="text-xs text-gray-500">{{ activity.manufacturer }} {{ activity.model }}</p>
                    <!-- Location and Project -->
                    <div class="flex flex-col gap-0.5 mt-1">
                      <span v-if="activity.current_location_name" class="text-xs text-gray-600">
                        📍 {{ locationTypeLabel(activity.current_location_type) }}: {{ activity.current_location_name }}
                      </span>
                      <span v-if="activity.project_code" class="text-xs text-sky-700">
                        📋 {{ activity.project_code }}
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="logTypeBadge(activity.log_type)" class="px-2 py-1 text-xs font-semibold rounded">
                      {{ logTypeLabel(activity.log_type) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900">
                    {{ activity.description }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {{ activity.created_by_username || 'System' }}
                  </td>
                </tr>
              </tbody>
            </table>
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
import MainLayout from '@/layouts/MainLayout.vue'

const router = useRouter()

const loading = ref(true)
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

onMounted(() => {
  loadDashboard()
})
</script>
