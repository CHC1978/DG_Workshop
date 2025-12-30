<template>
  <MainLayout>
    <div class="space-y-6">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h1>

      <!-- Time-Sensitive Alerts -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
        <!-- Maintenance Alerts -->
        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Maintenance Due</h2>
            <span class="text-2xl">🔧</span>
          </div>
          <p class="text-3xl font-bold text-orange-600">{{ alerts.maintenance_alerts?.length || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">Equipment需要維護</p>
          <div v-if="alerts.maintenance_alerts && alerts.maintenance_alerts.length > 0" class="mt-4">
            <router-link to="/equipment" class="text-sm text-sky-600 hover:text-sky-800">
              View details →
            </router-link>
          </div>
        </div>

        <!-- Calibration Alerts -->
        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Calibration Due</h2>
            <span class="text-2xl">📊</span>
          </div>
          <p class="text-3xl font-bold text-yellow-600">{{ alerts.calibration_alerts?.length || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">需要校正</p>
          <div v-if="alerts.calibration_alerts && alerts.calibration_alerts.length > 0" class="mt-4">
            <router-link to="/calibrations" class="text-sm text-sky-600 hover:text-sky-800">
              View details →
            </router-link>
          </div>
        </div>

        <!-- Overdue Rentals -->
        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Overdue Rentals</h2>
            <span class="text-2xl">⏰</span>
          </div>
          <p class="text-3xl font-bold text-red-600">{{ alerts.overdue_rentals?.length || 0 }}</p>
          <p class="text-sm text-gray-600 mt-2">逾期未還</p>
          <div v-if="alerts.overdue_rentals && alerts.overdue_rentals.length > 0" class="mt-4">
            <router-link to="/rentals" class="text-sm text-sky-600 hover:text-sky-800">
              View details →
            </router-link>
          </div>
        </div>
      </div>

      <!-- Recent Activities -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="px-4 sm:px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-gray-900">Recent Activities</h2>
        </div>

        <div v-if="loading" class="text-center py-12">
          <p class="text-gray-500">Loading...</p>
        </div>

        <div v-else-if="recentActivities.length === 0" class="text-center py-12">
          <p class="text-gray-500">No recent activities</p>
        </div>

        <div v-else>
          <!-- Mobile: Card view -->
          <div class="block md:hidden divide-y divide-gray-200">
            <div v-for="activity in recentActivities" :key="activity.id" class="p-4">
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
                <tr v-for="activity in recentActivities" :key="activity.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDateTime(activity.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <router-link
                      :to="`/equipment/${activity.equipment_id}`"
                      class="text-sm font-medium text-sky-600 hover:text-sky-800"
                    >
                      {{ activity.asset_code }}
                    </router-link>
                    <p class="text-xs text-gray-500">{{ activity.manufacturer }} {{ activity.model }}</p>
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

      <!-- Quick Actions -->
      <div class="bg-white rounded-lg shadow p-4 sm:p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <AppButton
            variant="primary"
            @click="router.push('/equipment')"
          >
            View Equipment
          </AppButton>
          <AppButton
            variant="secondary"
            @click="router.push('/rentals')"
          >
            View Rentals
          </AppButton>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardApi, type DashboardAlerts, type RecentActivity } from '@/api/dashboard'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()

const loading = ref(true)
const alerts = ref<DashboardAlerts>({
  maintenance_alerts: [],
  calibration_alerts: [],
  overdue_rentals: [],
})
const recentActivities = ref<RecentActivity[]>([])

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

async function loadDashboard() {
  loading.value = true
  try {
    const [alertsRes, activitiesRes] = await Promise.all([
      dashboardApi.getAlerts(),
      dashboardApi.getRecentActivities(10),
    ])

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
