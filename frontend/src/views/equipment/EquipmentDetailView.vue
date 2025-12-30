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
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ equipment.asset_code }}</h1>
            <p class="mt-1 text-lg text-gray-600">
              {{ equipment.manufacturer }} {{ equipment.model }}
            </p>
          </div>
          <div class="flex space-x-2">
            <AppButton
              v-if="authStore.isManager"
              variant="secondary"
              @click="router.push(`/equipment/${equipment.id}/edit`)"
            >
              Edit
            </AppButton>
            <AppButton
              variant="secondary"
              @click="downloadQRCode"
            >
              Download QR Code
            </AppButton>
          </div>
        </div>

        <!-- Status Badge -->
        <div>
          <span :class="statusBadgeClass(equipment.status)" class="text-lg px-4 py-2">
            {{ statusLabel(equipment.status) }}
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
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ equipment.asset_code }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Category</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ categoryLabel(equipment.category) }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Manufacturer</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ equipment.manufacturer }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Model</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ equipment.model }}</dd>
              </div>
              <div v-if="equipment.serial_number">
                <dt class="text-sm font-medium text-gray-500">Serial Number</dt>
                <dd class="mt-1 text-sm text-gray-900 font-mono">{{ equipment.serial_number }}</dd>
              </div>
            </dl>
          </div>

          <!-- Financial Information -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Financial Information</h2>
            <dl class="space-y-3">
              <div v-if="equipment.purchase_date">
                <dt class="text-sm font-medium text-gray-500">Purchase Date</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ formatDate(equipment.purchase_date) }}</dd>
              </div>
              <div v-if="equipment.purchase_price">
                <dt class="text-sm font-medium text-gray-500">Purchase Price</dt>
                <dd class="mt-1 text-sm text-gray-900">${{ equipment.purchase_price.toLocaleString() }}</dd>
              </div>
              <div v-if="equipment.rental_daily_rate">
                <dt class="text-sm font-medium text-gray-500">Daily Rental Rate</dt>
                <dd class="mt-1 text-sm text-gray-900">${{ equipment.rental_daily_rate.toLocaleString() }}/day</dd>
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

        <!-- Status Actions (Operator+) -->
        <div v-if="authStore.isOperator && canPerformActions" class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Status Actions</h2>
          <div class="flex space-x-3">
            <AppButton
              v-if="equipment.status === 'in_stock'"
              variant="primary"
              @click="showDeployModal = true"
            >
              Deploy Equipment
            </AppButton>
            <AppButton
              v-if="equipment.status === 'deployed' || equipment.status === 'rented'"
              variant="primary"
              @click="showReturnModal = true"
            >
              Return Equipment
            </AppButton>
            <AppButton
              v-if="equipment.status !== 'repair'"
              variant="secondary"
              @click="showRepairModal = true"
            >
              Send to Repair
            </AppButton>
          </div>
        </div>

        <!-- Equipment Logs -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Activity Log</h2>
          <div v-if="logs.length === 0" class="text-center py-8 text-gray-500">
            No activity logs yet
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="log in logs"
              :key="log.id"
              class="border-l-4 border-sky-500 pl-4 py-2"
            >
              <p class="text-sm font-medium text-gray-900">{{ log.description }}</p>
              <p v-if="log.new_value" class="text-xs text-gray-600 mt-1">{{ log.new_value }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ formatDateTime(log.created_at) }}</p>
            </div>
          </div>
        </div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import { equipmentApi } from '@/api/equipment'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()

const equipmentId = computed(() => parseInt(route.params.id as string))
const equipment = computed(() => equipmentStore.currentEquipment)

const qrCodeUrl = ref('')
const logs = ref<any[]>([])
const showDeployModal = ref(false)
const showReturnModal = ref(false)
const showRepairModal = ref(false)

const canPerformActions = computed(() => {
  return equipment.value?.status !== 'disposed' && equipment.value?.status !== 'lost'
})

function categoryLabel(category: string): string {
  const labels: Record<string, string> = {
    mbes: 'MBES - Multibeam Echosounder',
    gnss: 'GNSS - Receiver',
    svp: 'SVP - Sound Velocity Profiler',
    sbp: 'SBP - Sub-bottom Profiler',
    usbl: 'USBL - Ultra-Short Baseline',
    rov: 'ROV - Remotely Operated Vehicle',
    ins: 'INS - Inertial Navigation System',
    magnetometer: 'Magnetometer',
    other: 'Other',
  }
  return labels[category] || category
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    ordering: 'Ordering',
    in_stock: 'In Stock',
    deployed: 'Deployed',
    rented: 'Rented',
    repair: 'Repair',
    disposed: 'Disposed',
    lost: 'Lost',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const base = 'inline-block font-semibold rounded'
  const variants: Record<string, string> = {
    ordering: 'bg-yellow-100 text-yellow-800',
    in_stock: 'bg-green-100 text-green-800',
    deployed: 'bg-blue-100 text-blue-800',
    rented: 'bg-purple-100 text-purple-800',
    repair: 'bg-orange-100 text-orange-800',
    disposed: 'bg-gray-100 text-gray-800',
    lost: 'bg-red-100 text-red-800',
  }
  return `${base} ${variants[status] || 'bg-gray-100 text-gray-800'}`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

function downloadQRCode() {
  if (!equipment.value) return
  const url = equipmentApi.getQRCodeImageUrl(equipment.value.id)
  window.open(url, '_blank')
}

async function loadLogs() {
  if (!equipmentId.value) return

  try {
    const response = await equipmentApi.getLogs(equipmentId.value)
    logs.value = response.data
  } catch (error) {
    console.error('Failed to load logs:', error)
  }
}

async function loadQRCode() {
  if (!equipmentId.value) return

  try {
    const response = await equipmentApi.getQRCode(equipmentId.value)
    qrCodeUrl.value = response.data.qr_code_base64
  } catch (error) {
    console.error('Failed to load QR code:', error)
  }
}

onMounted(async () => {
  await equipmentStore.fetchById(equipmentId.value)
  loadLogs()
  loadQRCode()
})
</script>
