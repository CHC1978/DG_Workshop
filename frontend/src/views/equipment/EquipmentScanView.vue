<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-50 to-blue-100 py-8 px-4">
    <div class="max-w-2xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="bg-white rounded-lg shadow-xl p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading equipment...</p>
      </div>

      <!-- Equipment Found -->
      <div v-else-if="equipment" class="space-y-6">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-xl p-6">
          <div class="text-center mb-4">
            <div class="text-4xl mb-2">📦</div>
            <h1 class="text-3xl font-bold text-gray-900">{{ equipment.asset_code }}</h1>
            <p class="text-lg text-gray-600 mt-2">
              {{ equipment.manufacturer }} {{ equipment.model }}
            </p>
          </div>

          <div class="flex justify-center">
            <span :class="statusBadgeClass(equipment.status)" class="text-lg px-4 py-2">
              {{ statusLabel(equipment.status) }}
            </span>
          </div>
        </div>

        <!-- Basic Info (Always visible) -->
        <div class="bg-white rounded-lg shadow-xl p-6">
          <h2 class="text-xl font-semibold mb-4">Basic Information</h2>
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-gray-500">Category</dt>
              <dd class="text-base text-gray-900">{{ categoryLabel(equipment.category) }}</dd>
            </div>
            <div v-if="equipment.serial_number">
              <dt class="text-sm font-medium text-gray-500">Serial Number</dt>
              <dd class="text-base text-gray-900 font-mono">{{ equipment.serial_number }}</dd>
            </div>
          </dl>
        </div>

        <!-- Login prompt if not authenticated -->
        <div v-if="!authStore.isAuthenticated" class="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <p class="text-blue-900 font-medium mb-3">Want to see more details?</p>
          <AppButton
            variant="primary"
            full-width
            @click="router.push('/login')"
          >
            Login to View Full Details
          </AppButton>
        </div>

        <!-- Full details if authenticated -->
        <div v-else class="space-y-6">
          <!-- Scan recorded message -->
          <div v-if="scanRecorded" class="bg-green-50 border border-green-200 rounded-lg p-4">
            <p class="text-green-800 text-sm">
              ✓ Scan recorded with location data
            </p>
          </div>

          <!-- Actions -->
          <div class="bg-white rounded-lg shadow-xl p-6">
            <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <AppButton
                variant="primary"
                @click="router.push(`/equipment/${equipment.id}`)"
              >
                View Full Details
              </AppButton>
              <AppButton
                variant="secondary"
                @click="router.push('/equipment')"
              >
                Back to Equipment List
              </AppButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Not Found -->
      <div v-else-if="!loading" class="bg-white rounded-lg shadow-xl p-8 text-center">
        <div class="text-6xl mb-4">❌</div>
        <h1 class="text-2xl font-bold text-gray-900 mb-2">Equipment Not Found</h1>
        <p class="text-gray-600 mb-6">
          Asset code: <span class="font-mono">{{ assetCode }}</span>
        </p>
        <AppButton
          variant="primary"
          @click="router.push('/equipment')"
        >
          Go to Equipment List
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { equipmentApi } from '@/api/equipment'
import AppButton from '@/components/common/AppButton.vue'
import type { Equipment } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const assetCode = computed(() => route.params.assetCode as string)
const loading = ref(true)
const equipment = ref<Equipment | null>(null)
const scanRecorded = ref(false)

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

async function recordScanEvent() {
  if (!equipment.value || !authStore.isAuthenticated) return

  try {
    // Try to get GPS location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          // Record with GPS
          await equipmentApi.addNote(
            equipment.value!.id,
            `QR code scanned via mobile`,
            position.coords.latitude,
            position.coords.longitude
          )
          scanRecorded.value = true
        },
        async () => {
          // Record without GPS (permission denied or error)
          await equipmentApi.addNote(
            equipment.value!.id,
            `QR code scanned via mobile (no GPS)`
          )
          scanRecorded.value = true
        }
      )
    } else {
      // No geolocation support
      await equipmentApi.addNote(
        equipment.value!.id,
        `QR code scanned via mobile (no GPS support)`
      )
      scanRecorded.value = true
    }
  } catch (error) {
    console.error('Failed to record scan:', error)
  }
}

onMounted(async () => {
  try {
    console.log('Scanning equipment:', assetCode.value)
    const response = await equipmentApi.getByQR(assetCode.value)
    equipment.value = response.data
    console.log('Equipment found:', equipment.value)

    // Record scan event if authenticated
    if (authStore.isAuthenticated) {
      await recordScanEvent()
    }
  } catch (error: any) {
    console.error('Failed to load equipment:', error)
    equipment.value = null
  } finally {
    loading.value = false
  }
})
</script>
