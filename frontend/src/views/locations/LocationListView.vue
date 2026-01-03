<template>
  <MainLayout>
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Locations</h1>
        <div class="flex gap-2">
          <AppButton @click="handleCreateVessel">New Vessel</AppButton>
          <AppButton @click="handleCreateWarehouse" variant="secondary">New Warehouse</AppButton>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by name, code, or identifier..."
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              @input="debouncedSearch"
            />
          </div>

          <!-- Location Type Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Location Type</label>
            <select
              v-model="typeFilter"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              @change="handleFilter"
            >
              <option value="">All</option>
              <option value="vessel">Vessel</option>
              <option value="warehouse">Warehouse</option>
              <option value="platform">Platform</option>
              <option value="vehicle">Vehicle</option>
              <option value="external">External</option>
            </select>
          </div>

          <!-- Active Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Active Status</label>
            <select
              v-model="activeFilter"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-sky-500 focus:ring-sky-500"
              @change="handleFilter"
            >
              <option value="">All</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="locationStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading locations...</p>
      </div>

      <!-- Locations List -->
      <div v-else-if="locationStore.locations.length > 0" class="space-y-4">
        <div
          v-for="location in locationStore.locations"
          :key="location.id"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer"
          @click="handleViewLocation(location)"
        >
          <div class="p-6">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-xl font-semibold text-gray-900">{{ location.name }}</h3>
                  <span :class="typeBadgeClass(location.location_type)" class="px-2 py-1 text-xs font-semibold rounded">
                    {{ typeLabel(location.location_type) }}
                  </span>
                  <span v-if="!location.is_active" class="px-2 py-1 text-xs font-semibold rounded bg-gray-100 text-gray-800">
                    Inactive
                  </span>
                </div>

                <!-- Code -->
                <p v-if="location.code" class="text-sm text-gray-600 font-mono mb-2">{{ location.code }}</p>

                <!-- Vessel Info -->
                <template v-if="location.location_type === 'vessel'">
                  <div class="flex flex-wrap gap-4 text-sm text-gray-500 mb-2">
                    <div v-if="location.vessel_name" class="flex items-center gap-1">
                      <span class="font-medium">Name:</span>
                      <span>{{ location.vessel_name }}</span>
                    </div>
                    <div v-if="location.imo_number" class="flex items-center gap-1">
                      <span class="font-medium">IMO:</span>
                      <span>{{ location.imo_number }}</span>
                    </div>
                    <div v-if="location.vessel_mmsi" class="flex items-center gap-1">
                      <span class="font-medium">MMSI:</span>
                      <span>{{ location.vessel_mmsi }}</span>
                    </div>
                    <div v-if="location.vessel_national_id" class="flex items-center gap-1">
                      <span class="font-medium">National ID:</span>
                      <span>{{ location.vessel_national_id }}</span>
                    </div>
                    <div v-if="location.call_sign" class="flex items-center gap-1">
                      <span class="font-medium">Call Sign:</span>
                      <span>{{ location.call_sign }}</span>
                    </div>
                  </div>
                  <div v-if="location.vessel_type || location.vessel_flag" class="text-sm text-gray-500">
                    <span v-if="location.vessel_type">{{ location.vessel_type }}</span>
                    <span v-if="location.vessel_type && location.vessel_flag"> • </span>
                    <span v-if="location.vessel_flag">Flag: {{ location.vessel_flag }}</span>
                  </div>
                </template>

              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="locationStore.totalPages > 1" class="flex justify-center gap-2 mt-6">
          <AppButton
            variant="secondary"
            size="sm"
            :disabled="locationStore.currentPage === 1"
            @click="handlePageChange(locationStore.currentPage - 1)"
          >
            Previous
          </AppButton>
          <span class="px-4 py-2 text-sm text-gray-700">
            Page {{ locationStore.currentPage }} of {{ locationStore.totalPages }}
          </span>
          <AppButton
            variant="secondary"
            size="sm"
            :disabled="locationStore.currentPage === locationStore.totalPages"
            @click="handlePageChange(locationStore.currentPage + 1)"
          >
            Next
          </AppButton>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500 mb-4">No locations found</p>
        <div class="flex gap-2 justify-center">
          <AppButton @click="handleCreateVessel">Create First Vessel</AppButton>
          <AppButton @click="handleCreateWarehouse" variant="secondary">Create Warehouse</AppButton>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLocationStore } from '@/stores/locations'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Location } from '@/types'

const router = useRouter()
const locationStore = useLocationStore()

const searchQuery = ref('')
const typeFilter = ref('')
const activeFilter = ref('')

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function typeLabel(type: string): string {
  const labels: Record<string, string> = {
    vessel: 'Vessel',
    warehouse: 'Warehouse',
    platform: 'Platform',
    vehicle: 'Vehicle',
    external: 'External',
  }
  return labels[type] || type
}

function typeBadgeClass(type: string): string {
  const variants: Record<string, string> = {
    vessel: 'bg-blue-100 text-blue-800',
    warehouse: 'bg-purple-100 text-purple-800',
    platform: 'bg-amber-100 text-amber-800',
    vehicle: 'bg-teal-100 text-teal-800',
    external: 'bg-gray-100 text-gray-800',
  }
  return variants[type] || 'bg-gray-100 text-gray-800'
}

function debouncedSearch() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    handleFilter()
  }, 300)
}

function handleFilter() {
  const params: any = {
    skip: 0,
    limit: 20,
  }

  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  if (typeFilter.value) {
    params.location_type = typeFilter.value
  }
  if (activeFilter.value) {
    params.is_active = activeFilter.value === 'true'
  }

  locationStore.fetchLocations(params)
}

function handlePageChange(page: number) {
  const params: any = {
    skip: (page - 1) * locationStore.pageSize,
    limit: locationStore.pageSize,
  }

  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  if (typeFilter.value) {
    params.location_type = typeFilter.value
  }
  if (activeFilter.value) {
    params.is_active = activeFilter.value === 'true'
  }

  locationStore.fetchLocations(params)
}

function handleCreateVessel() {
  router.push('/locations/new/vessel')
}

function handleCreateWarehouse() {
  router.push('/locations/new/warehouse')
}

function handleViewLocation(location: Location) {
  // Navigate to detail page
  router.push(`/locations/${location.id}`)
}

onMounted(() => {
  locationStore.fetchLocations({ skip: 0, limit: 20 })
})
</script>
