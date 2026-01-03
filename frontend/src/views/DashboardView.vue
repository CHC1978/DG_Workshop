<template>
  <MainLayout>
    <div class="space-y-6">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h1>

      <!-- Dashboard Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <DashboardStatsCard
          title="In Stock"
          icon="box"
          :value="stats.in_stock || 0"
          subtitle="Available"
          color="green"
          @click="navigateToEquipment('in_stock')"
        />

        <DashboardStatsCard
          title="Deployed"
          icon="ship"
          :value="stats.deployed || 0"
          subtitle="In Use"
          color="blue"
          @click="navigateToEquipment('deployed')"
        />

        <DashboardStatsCard
          title="In Repair"
          icon="wrench"
          :value="stats.in_repair || 0"
          subtitle="Under Repair"
          color="orange"
          @click="navigateToEquipment('repair')"
        />

        <DashboardStatsCard
          title="Rented"
          icon="clipboard"
          :value="stats.rented || 0"
          subtitle="Rented Out"
          color="purple"
          @click="navigateToEquipment('rented')"
        />

        <DashboardStatsCard
          title="Maintenance Due"
          icon="alert"
          :value="stats.maintenance_due_soon || 0"
          subtitle="Needs Maintenance"
          color="orange"
          @click="router.push('/maintenance')"
        />

        <DashboardStatsCard
          title="Calibration Due"
          icon="chart"
          :value="stats.calibration_due_soon || 0"
          subtitle="Needs Calibration"
          color="yellow"
          @click="router.push('/calibrations')"
        />

        <DashboardStatsCard
          title="Overdue Rentals"
          icon="clock"
          :value="stats.overdue_rentals || 0"
          subtitle="Past Due"
          color="red"
          @click="router.push('/rentals')"
        />
      </div>

      <!-- Recent Activities -->
      <RecentActivitiesSection
        :activities="recentActivities"
        :loading="loading"
        :is-admin="isAdmin"
        @clear-all="clearAllActivities"
      />
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardApi, type DashboardAlerts, type DashboardStats, type RecentActivity } from '@/api/dashboard'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/layouts/MainLayout.vue'
import DashboardStatsCard from '@/components/dashboard/DashboardStatsCard.vue'
import RecentActivitiesSection from '@/components/dashboard/RecentActivitiesSection.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)

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
  try {
    await dashboardApi.clearActivities()
    recentActivities.value = []
  } catch (error) {
    console.error('Failed to clear activities:', error)
  }
}

onMounted(() => {
  loadDashboard()
})
</script>
