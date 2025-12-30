<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-gray-900">Equipment</h1>
        <AppButton
          v-if="authStore.isManager"
          variant="primary"
          @click="router.push('/equipment/new')"
        >
          + Add Equipment
        </AppButton>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search..."
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
            @input="handleSearch"
          />

          <select
            v-model="filters.category"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
            @change="loadEquipment"
          >
            <option value="">All Categories</option>
            <option value="mbes">MBES</option>
            <option value="gnss">GNSS</option>
            <option value="svp">SVP</option>
            <option value="sbp">SBP</option>
            <option value="usbl">USBL</option>
            <option value="rov">ROV</option>
            <option value="ins">INS</option>
            <option value="magnetometer">Magnetometer</option>
          </select>

          <select
            v-model="filters.status"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
            @change="loadEquipment"
          >
            <option value="">All Status</option>
            <option value="ordering">Ordering</option>
            <option value="in_stock">In Stock</option>
            <option value="deployed">Deployed</option>
            <option value="rented">Rented</option>
            <option value="repair">Repair</option>
          </select>

          <AppButton variant="secondary" @click="resetFilters">
            Reset
          </AppButton>
        </div>
      </div>

      <!-- Equipment List -->
      <div v-if="equipmentStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading...</p>
      </div>

      <div v-else-if="equipmentStore.equipmentList.length === 0" class="text-center py-12">
        <p class="text-gray-500">No equipment found</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="equipment in equipmentStore.equipmentList"
          :key="equipment.id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
          @click="viewEquipment(equipment.id)"
        >
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ equipment.asset_code }}
                </h3>
                <p class="text-sm text-gray-600">
                  {{ equipment.manufacturer }} {{ equipment.model }}
                </p>
              </div>
              <span :class="statusBadgeClass(equipment.status)">
                {{ statusLabel(equipment.status) }}
              </span>
            </div>

            <div class="space-y-2 text-sm text-gray-600">
              <p>
                <strong>Category:</strong> {{ categoryLabel(equipment.category) }}
              </p>
              <p v-if="equipment.serial_number">
                <strong>S/N:</strong> {{ equipment.serial_number }}
              </p>
              <p v-if="equipment.rental_daily_rate">
                <strong>Daily Rate:</strong> ${{ equipment.rental_daily_rate.toLocaleString() }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="equipmentStore.total > filters.limit" class="flex justify-center mt-6">
        <p class="text-sm text-gray-600">
          Showing {{ equipmentStore.equipmentList.length }} of {{ equipmentStore.total }} equipment
        </p>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()

const filters = reactive({
  search: '',
  category: '',
  status: '',
  skip: 0,
  limit: 50,
})

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadEquipment()
  }, 500)
}

async function loadEquipment() {
  try {
    await equipmentStore.fetchList(filters)
  } catch (error) {
    console.error('Failed to load equipment:', error)
  }
}

function resetFilters() {
  filters.search = ''
  filters.category = ''
  filters.status = ''
  loadEquipment()
}

function viewEquipment(id: number) {
  router.push(`/equipment/${id}`)
}

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
  const base = 'px-2 py-1 text-xs font-semibold rounded'
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

onMounted(() => {
  loadEquipment()
})
</script>
