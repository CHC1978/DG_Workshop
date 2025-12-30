<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Calibration Management</h1>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex flex-col sm:flex-row gap-3">
          <select
            v-model="filter"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
            @change="loadCalibrations"
          >
            <option value="all">All Calibrations</option>
            <option value="overdue">Overdue</option>
            <option value="7days">Due in 7 Days</option>
            <option value="30days">Due in 30 Days</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading calibrations...</p>
      </div>

      <!-- No Data -->
      <div v-else-if="calibrations.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500">No calibrations found</p>
      </div>

      <!-- Calibrations Display -->
      <div v-else>
        <!-- Desktop: Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden hidden md:block">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Equipment</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Calibration</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Next Due</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Days</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="cal in calibrations" :key="cal.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <router-link
                      :to="`/equipment/${cal.equipment_id}`"
                      class="text-sm font-medium text-sky-600 hover:text-sky-800"
                    >
                      {{ cal.equipment_asset_code }}
                    </router-link>
                    <p class="text-xs text-gray-500">
                      {{ cal.equipment_manufacturer }} {{ cal.equipment_model }}
                    </p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(cal.calibration_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(cal.next_due_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span :class="daysTextClass(cal.days_until_due)">
                      {{ cal.days_until_due >= 0 ? cal.days_until_due : `${Math.abs(cal.days_until_due)} overdue` }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="statusBadge(cal.days_until_due, cal.is_overdue)" class="px-2 py-1 text-xs font-semibold rounded">
                      {{ statusLabel(cal.days_until_due, cal.is_overdue) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {{ cal.provider }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Mobile: Cards -->
        <div class="block md:hidden space-y-4">
        <div v-for="cal in calibrations" :key="cal.id" class="bg-white rounded-lg shadow p-4">
          <div class="flex justify-between items-start mb-3">
            <router-link
              :to="`/equipment/${cal.equipment_id}`"
              class="font-semibold text-sky-600 hover:text-sky-800"
            >
              {{ cal.equipment_asset_code }}
            </router-link>
            <span :class="statusBadge(cal.days_until_due, cal.is_overdue)" class="px-2 py-1 text-xs font-semibold rounded">
              {{ statusLabel(cal.days_until_due, cal.is_overdue) }}
            </span>
          </div>

          <p class="text-sm text-gray-600 mb-2">
            {{ cal.equipment_manufacturer }} {{ cal.equipment_model }}
          </p>

          <div class="grid grid-cols-2 gap-2 text-sm">
            <div>
              <p class="text-gray-500">Last:</p>
              <p class="font-medium">{{ formatDate(cal.calibration_date) }}</p>
            </div>
            <div>
              <p class="text-gray-500">Next:</p>
              <p class="font-medium">{{ formatDate(cal.next_due_date) }}</p>
            </div>
          </div>

          <div class="mt-2 flex justify-between items-center text-sm">
            <span :class="daysTextClass(cal.days_until_due)">
              {{ cal.days_until_due >= 0 ? `${cal.days_until_due} days` : `${Math.abs(cal.days_until_due)} days overdue` }}
            </span>
            <span class="text-gray-600">{{ cal.provider }}</span>
          </div>
        </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { calibrationsApi, type CalibrationWithEquipment } from '@/api/calibrations'
import MainLayout from '@/layouts/MainLayout.vue'

const router = useRouter()

const loading = ref(true)
const calibrations = ref<CalibrationWithEquipment[]>([])
const filter = ref('30days')

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

function statusLabel(days: number, isOverdue: boolean): string {
  if (isOverdue) return 'Overdue'
  if (days <= 7) return 'Urgent'
  if (days <= 30) return 'Due Soon'
  return 'Normal'
}

function statusBadge(days: number, isOverdue: boolean): string {
  const base = 'inline-block'
  if (isOverdue) return `${base} bg-red-100 text-red-800`
  if (days <= 7) return `${base} bg-orange-100 text-orange-800`
  if (days <= 30) return `${base} bg-yellow-100 text-yellow-800`
  return `${base} bg-green-100 text-green-800`
}

function daysTextClass(days: number): string {
  if (days < 0) return 'text-red-600 font-semibold'
  if (days <= 7) return 'text-orange-600 font-semibold'
  if (days <= 30) return 'text-yellow-600 font-medium'
  return 'text-gray-600'
}

async function loadCalibrations() {
  loading.value = true
  try {
    let days = 30
    if (filter.value === '7days') days = 7
    if (filter.value === 'overdue') days = 0
    if (filter.value === 'all') days = 365

    const response = await calibrationsApi.getDueSoon(days)
    calibrations.value = response.data

    // Filter overdue if selected
    if (filter.value === 'overdue') {
      calibrations.value = calibrations.value.filter(c => c.is_overdue)
    }
  } catch (error) {
    console.error('Failed to load calibrations:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCalibrations()
})
</script>
