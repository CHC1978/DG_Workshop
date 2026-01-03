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
            <option value="calibrating">Calibrating</option>
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
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
        >
          <div class="p-6 cursor-pointer" @click="viewEquipment(equipment.id)">
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
              <p v-if="equipment.purchase_date">
                <strong>Purchased:</strong> {{ new Date(equipment.purchase_date).toLocaleDateString() }}
              </p>
            </div>

            <!-- Location and Project Info -->
            <div v-if="equipment.current_location_name || equipment.project_code" class="mt-3 pt-3 border-t border-gray-200">
              <div class="flex flex-col gap-1 text-sm">
                <div v-if="equipment.current_location_name" class="flex items-center gap-1 text-gray-700">
                  <span class="text-base">📍</span>
                  <span><strong>{{ locationTypeLabel(equipment.current_location_type) }}:</strong> {{ equipment.current_location_name }}</span>
                </div>
                <div v-if="equipment.project_code" class="flex items-center gap-1 text-sky-700">
                  <span class="text-base">📋</span>
                  <span><strong>Project:</strong> {{ equipment.project_code }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Child Components Section -->
          <div v-if="equipment.children_count && equipment.children_count > 0" class="border-t border-gray-200 bg-gray-50">
            <button
              @click.stop="toggleChildren(equipment.id)"
              class="w-full px-6 py-3 flex items-center justify-between text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <span class="flex items-center gap-2">
                <span>🔧</span>
                <span>{{ equipment.children_count }} Component(s)</span>
              </span>
              <svg
                :class="['w-5 h-5 transition-transform', expandedEquipment[equipment.id] ? 'rotate-180' : '']"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Child Equipment List (Expanded) -->
            <div v-if="expandedEquipment[equipment.id]" class="px-6 pb-4">
              <div v-if="loadingChildren[equipment.id]" class="text-center py-4 text-sm text-gray-500">
                Loading components...
              </div>
              <div v-else-if="childrenMap[equipment.id] && childrenMap[equipment.id].length > 0" class="space-y-2">
                <div
                  v-for="child in childrenMap[equipment.id]"
                  :key="child.id"
                  class="p-3 bg-white rounded border border-gray-200 hover:border-sky-400 transition-colors cursor-pointer"
                  @click.stop="viewEquipment(child.id)"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex-1">
                      <p class="text-sm font-semibold text-gray-900">{{ child.asset_code }}</p>
                      <p class="text-xs text-gray-600">{{ child.model }}</p>
                    </div>
                    <span :class="statusBadgeClass(child.status)" class="text-xs">
                      {{ statusLabel(child.status) }}
                    </span>
                  </div>
                </div>
              </div>
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
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEquipmentStore } from '@/stores/equipment'
import { equipmentApi } from '@/api/equipment'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Equipment } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const equipmentStore = useEquipmentStore()

const filters = reactive({
  search: '',
  category: '',
  status: route.query.status as string || '',  // Auto-fill from URL query
  skip: 0,
  limit: 50,
})

// Child equipment management
const expandedEquipment = ref<Record<number, boolean>>({})
const childrenMap = ref<Record<number, Equipment[]>>({})
const loadingChildren = ref<Record<number, boolean>>({})

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadEquipment()
  }, 500)
}

async function loadEquipment() {
  try {
    if (import.meta.env.DEV) console.log('Loading equipment with filters:', filters)
    await equipmentStore.fetchList(filters)
    if (import.meta.env.DEV) console.log('Equipment loaded:', equipmentStore.equipmentList.length, 'items')
  } catch (error: any) {
    console.error('Failed to load equipment:', error)
    console.error('Error details:', error.response?.data)
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
    calibrating: 'Calibrating',
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
    calibrating: 'bg-cyan-100 text-cyan-800',
    disposed: 'bg-gray-100 text-gray-800',
    lost: 'bg-red-100 text-red-800',
  }
  return `${base} ${variants[status] || 'bg-gray-100 text-gray-800'}`
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

async function toggleChildren(equipmentId: number) {
  // Toggle expanded state
  expandedEquipment.value[equipmentId] = !expandedEquipment.value[equipmentId]

  // Load children if expanding and not already loaded
  if (expandedEquipment.value[equipmentId] && !childrenMap.value[equipmentId]) {
    loadingChildren.value[equipmentId] = true
    try {
      const response = await equipmentApi.getChildren(equipmentId)
      childrenMap.value[equipmentId] = response.data
      if (import.meta.env.DEV) console.log(`Loaded ${response.data.length} children for equipment ${equipmentId}`)
    } catch (error: any) {
      console.error('Failed to load children:', error)
      // Reset expanded state on error
      expandedEquipment.value[equipmentId] = false
    } finally {
      loadingChildren.value[equipmentId] = false
    }
  }
}

onMounted(() => {
  loadEquipment()
})
</script>
