<template>
  <MainLayout>
    <div class="space-y-6">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>

      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-sm text-gray-600">Total Equipment</p>
          <p class="text-3xl font-bold text-sky-600 mt-2">--</p>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-sm text-gray-600">In Stock</p>
          <p class="text-3xl font-bold text-green-600 mt-2">--</p>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-sm text-gray-600">Active Rentals</p>
          <p class="text-3xl font-bold text-blue-600 mt-2">--</p>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-sm text-gray-600">Due Calibrations</p>
          <p class="text-3xl font-bold text-orange-600 mt-2">--</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <AppButton
            variant="primary"
            @click="router.push('/equipment')"
          >
            View Equipment
          </AppButton>
          <AppButton
            variant="secondary"
            @click="router.push('/scan')"
          >
            Scan QR Code
          </AppButton>
          <AppButton
            variant="secondary"
            @click="router.push('/rentals')"
          >
            View Rentals
          </AppButton>
        </div>
      </div>

      <!-- Welcome Message -->
      <div class="bg-sky-50 border border-sky-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-sky-900 mb-2">
          Welcome, {{ authStore.user?.full_name }}!
        </h3>
        <p class="text-sm text-sky-700">
          You are logged in as <strong>{{ roleLabel }}</strong>.
        </p>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const authStore = useAuthStore()

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    admin: 'Administrator',
    manager: 'Equipment Manager',
    operator: 'Operator',
    viewer: 'Viewer',
  }
  return labels[authStore.userRole] || authStore.userRole
})
</script>
