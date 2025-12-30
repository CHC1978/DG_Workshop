<template>
  <MainLayout>
    <div class="max-w-6xl mx-auto space-y-6">
      <!-- Loading State -->
      <div v-if="subEquipmentStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading...</p>
      </div>

      <!-- Main Content -->
      <div v-else-if="subEquipment">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 font-mono">{{ subEquipment.asset_code }}</h1>
            <p class="mt-1 text-lg text-gray-600">
              {{ subEquipment.component_name }}
            </p>
            <p v-if="subEquipment.parent_asset_code" class="mt-1 text-sm text-gray-500">
              Parent Equipment:
              <router-link
                :to="`/equipment/${subEquipment.parent_equipment_id}`"
                class="text-sky-600 hover:text-sky-800 font-mono"
              >
                {{ subEquipment.parent_asset_code }}
              </router-link>
              <span v-if="subEquipment.parent_model" class="ml-1">
                - {{ subEquipment.parent_model }}
              </span>
            </p>
          </div>
          <div class="flex gap-2">
            <AppButton
              v-if="authStore.isManager"
              variant="secondary"
              size="sm"
              @click="router.push(`/equipment/${subEquipment.parent_equipment_id}`)"
            >
              Back to Parent Equipment
            </AppButton>
            <AppButton variant="secondary" size="sm" @click="downloadQRCode">
              Download QR Code
            </AppButton>
          </div>
        </div>

        <!-- Status Badge -->
        <div>
          <span :class="statusBadgeClass(subEquipment.status)" class="inline-flex px-3 py-1 text-sm font-semibold rounded-lg">
            {{ statusLabel(subEquipment.status) }}
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
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ subEquipment.asset_code }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Component Name</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ subEquipment.component_name }}</dd>
              </div>
              <div v-if="subEquipment.serial_number">
                <dt class="text-sm font-medium text-gray-500">Serial Number</dt>
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ subEquipment.serial_number }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Status</dt>
                <dd class="mt-1">
                  <span :class="statusBadgeClass(subEquipment.status)" class="px-2 py-1 text-xs font-semibold rounded">
                    {{ statusLabel(subEquipment.status) }}
                  </span>
                </dd>
              </div>
              <div v-if="subEquipment.notes">
                <dt class="text-sm font-medium text-gray-500">Notes</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ subEquipment.notes }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Created At</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDateTime(subEquipment.created_at) }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDateTime(subEquipment.updated_at) }}</dd>
              </div>
            </dl>
          </div>

          <!-- QR Code -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">QR Code</h2>
            <div class="flex flex-col items-center">
              <div class="w-48 h-48 bg-gray-100 flex items-center justify-center rounded border-2 border-gray-300">
                <img
                  v-if="qrCodeUrl"
                  :src="qrCodeUrl"
                  alt="QR Code"
                  class="w-full h-full object-contain"
                />
                <p v-else class="text-gray-400 text-sm">QR Code</p>
              </div>
              <p class="mt-3 text-xs text-gray-500 text-center break-all max-w-xs">
                {{ subEquipment.qr_code }}
              </p>
            </div>
          </div>
        </div>

        <!-- Activity Log -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Maintenance & Change Records</h2>
          </div>

          <div v-if="logs.length === 0" class="text-center py-12 text-gray-500">
            No records yet
          </div>

          <div v-else>
            <!-- Desktop Table -->
            <div class="hidden md:block overflow-x-auto">
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
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ formatDateTime(log.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ log.created_by_username || 'System' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span :class="logTypeBadgeClass(log.log_type)" class="px-2 py-1 text-xs font-semibold rounded">
                        {{ logTypeLabel(log.log_type) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-900">
                      {{ log.description }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Mobile Cards -->
            <div class="block md:hidden divide-y divide-gray-200">
            <div v-for="log in logs" :key="log.id" class="p-4">
              <div class="flex justify-between items-start mb-2">
                <span :class="logTypeBadgeClass(log.log_type)" class="px-2 py-1 text-xs font-semibold rounded">
                  {{ logTypeLabel(log.log_type) }}
                </span>
                <p class="text-xs text-gray-500">{{ formatDateTime(log.created_at) }}</p>
              </div>
              <p class="text-sm text-gray-900 mb-1">{{ log.description }}</p>
              <p class="text-xs text-gray-500">by {{ log.created_by_username || 'System' }}</p>
            </div>
          </div>
          </div>
        </div>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-12">
        <p class="text-gray-500">Sub-equipment not found</p>
        <AppButton variant="secondary" class="mt-4" @click="router.back()">
          Back
        </AppButton>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSubEquipmentStore } from '@/stores/subEquipment'
import { subEquipmentApi } from '@/api/subEquipment'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const subEquipmentStore = useSubEquipmentStore()

const subEquipmentId = computed(() => parseInt(route.params.id as string))
const subEquipment = computed(() => subEquipmentStore.currentSubEquipment)
const logs = ref<any[]>([])
const qrCodeUrl = ref<string | null>(null)

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    ordering: 'Ordering',
    in_stock: 'In Stock',
    deployed: 'Deployed',
    rented: 'Rented',
    repair: 'Under Repair',
    calibrating: 'Calibrating',
    disposed: 'Disposed',
    lost: 'Lost',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const variants: Record<string, string> = {
    ordering: 'bg-yellow-100 text-yellow-800',
    in_stock: 'bg-green-100 text-green-800',
    deployed: 'bg-blue-100 text-blue-800',
    rented: 'bg-purple-100 text-purple-800',
    repair: 'bg-orange-100 text-orange-800',
    calibrating: 'bg-cyan-100 text-cyan-800',
    disposed: 'bg-gray-100 text-gray-800',
    lost: 'bg-red-100 text-red-800',
  }
  return variants[status] || 'bg-gray-100 text-gray-800'
}

function logTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    status_change: 'Status Change',
    location_change: 'Location Change',
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

function logTypeBadgeClass(type: string): string {
  const variants: Record<string, string> = {
    status_change: 'bg-blue-100 text-blue-800',
    location_change: 'bg-purple-100 text-purple-800',
    rental_start: 'bg-green-100 text-green-800',
    rental_end: 'bg-gray-100 text-gray-800',
    calibration: 'bg-cyan-100 text-cyan-800',
    maintenance: 'bg-orange-100 text-orange-800',
    note: 'bg-yellow-100 text-yellow-800',
    created: 'bg-indigo-100 text-indigo-800',
    updated: 'bg-teal-100 text-teal-800',
  }
  return variants[type] || 'bg-gray-100 text-gray-800'
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function downloadQRCode() {
  if (!subEquipment.value || !qrCodeUrl.value) return

  try {
    // Convert base64 to blob and download
    const base64Data = qrCodeUrl.value.split(',')[1]
    const byteCharacters = atob(base64Data)
    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)
    const blob = new Blob([byteArray], { type: 'image/png' })

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${subEquipment.value.asset_code}_QR.png`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to download QR code:', error)
    alert('Failed to download QR code')
  }
}

async function loadQRCode() {
  if (!subEquipmentId.value) return

  try {
    const response = await subEquipmentApi.getQRCode(subEquipmentId.value)
    qrCodeUrl.value = response.data.qr_code_base64
  } catch (error) {
    console.error('Failed to load QR code:', error)
  }
}

async function loadLogs() {
  try {
    const response = await subEquipmentApi.getLogs(subEquipmentId.value)
    logs.value = response.data
  } catch (error) {
    console.error('Failed to load logs:', error)
  }
}

onMounted(async () => {
  await subEquipmentStore.fetchById(subEquipmentId.value)
  await loadQRCode()
  await loadLogs()
})
</script>
