<template>
  <MainLayout>
    <div class="max-w-6xl mx-auto">
      <!-- Loading -->
      <div v-if="locationStore.loading" class="text-center py-12">
        <p class="text-gray-500">Loading...</p>
      </div>

      <!-- Location Details -->
      <div v-else-if="location">
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ location.name }}</h1>
            <p v-if="location.code" class="mt-1 text-lg text-gray-600 font-mono">{{ location.code }}</p>
          </div>
          <div class="flex gap-2">
            <AppButton v-if="authStore.isManager" variant="secondary" size="sm" @click="handleEdit">
              Edit
            </AppButton>
            <AppButton v-if="authStore.isAdmin" variant="danger" size="sm" @click="handleDelete">
              Delete
            </AppButton>
          </div>
        </div>

        <!-- Type Badge -->
        <div class="mb-6 flex gap-2">
          <span :class="typeBadgeClass(location.location_type)" class="inline-flex px-3 py-1 text-sm font-semibold rounded-lg">
            {{ typeLabel(location.location_type) }}
          </span>
          <span v-if="!location.is_active" class="inline-flex px-3 py-1 text-sm font-semibold rounded-lg bg-gray-100 text-gray-800">
            Inactive
          </span>
        </div>

        <!-- Vessel Information -->
        <template v-if="location.location_type === 'vessel'">
          <!-- Vessel Photo Banner -->
          <div v-if="location.photo_url" class="mb-6 bg-white rounded-lg shadow overflow-hidden flex justify-center items-center bg-gray-50">
            <img
              :src="location.photo_url"
              :alt="location.name"
              class="max-w-full max-h-64 md:max-h-80 lg:max-h-96 w-auto h-auto object-contain"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Vessel Identifiers -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Vessel Identifiers</h2>
              <dl class="space-y-3">
                <div v-if="location.imo_number">
                  <dt class="text-sm font-medium text-gray-500">IMO Number</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.imo_number }}</dd>
                </div>
                <div v-if="location.vessel_mmsi">
                  <dt class="text-sm font-medium text-gray-500">MMSI</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.vessel_mmsi }}</dd>
                </div>
                <div v-if="location.vessel_national_id">
                  <dt class="text-sm font-medium text-gray-500">National Registration ID</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.vessel_national_id }}</dd>
                </div>
                <div v-if="location.vessel_internal_code">
                  <dt class="text-sm font-medium text-gray-500">Internal Code</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.vessel_internal_code }}</dd>
                </div>
                <div v-if="location.call_sign">
                  <dt class="text-sm font-medium text-gray-500">Call Sign</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.call_sign }}</dd>
                </div>
              </dl>
            </div>

            <!-- Vessel Details -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Vessel Details</h2>
              <dl class="space-y-3">
                <div v-if="location.vessel_name">
                  <dt class="text-sm font-medium text-gray-500">Vessel Name</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.vessel_name }}</dd>
                </div>
                <div v-if="location.vessel_type">
                  <dt class="text-sm font-medium text-gray-500">Vessel Type</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.vessel_type }}</dd>
                </div>
                <div v-if="location.vessel_flag">
                  <dt class="text-sm font-medium text-gray-500">Flag / Country</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.vessel_flag }}</dd>
                </div>
                <div v-if="location.vessel_owner">
                  <dt class="text-sm font-medium text-gray-500">Owner</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.vessel_owner }}</dd>
                </div>
                <div v-if="location.owner_company">
                  <dt class="text-sm font-medium text-gray-500">Owner Company (Legacy)</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.owner_company }}</dd>
                </div>
                <!-- Contact User (新：指向 User) -->
                <div v-if="location.contact_user_name">
                  <dt class="text-sm font-medium text-gray-500">Contact Person</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.contact_user_name }}</dd>
                </div>
                <!-- Contact Person (舊：指向 Location，作為 fallback) -->
                <div v-else-if="location.contact_person_name">
                  <dt class="text-sm font-medium text-gray-500">Contact Person</dt>
                  <dd class="mt-1 text-sm text-gray-900">
                    <router-link
                      v-if="location.contact_person_id"
                      :to="`/locations/${location.contact_person_id}`"
                      class="text-sky-600 hover:text-sky-800 hover:underline"
                    >
                      {{ location.contact_person_name }}
                    </router-link>
                    <span v-else>{{ location.contact_person_name }}</span>
                  </dd>
                </div>
              </dl>
            </div>

            <!-- Project Association -->
            <div v-if="location.current_project_id" class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Current Project</h2>
              <dl class="space-y-3">
                <div v-if="location.project_code">
                  <dt class="text-sm font-medium text-gray-500">Project Code</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.project_code }}</dd>
                </div>
                <div v-if="location.project_name">
                  <dt class="text-sm font-medium text-gray-500">Project Name</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.project_name }}</dd>
                </div>
              </dl>
            </div>

            <!-- Statistics -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
              <dl class="space-y-3">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Equipment Count</dt>
                  <dd class="mt-1 text-2xl font-bold text-sky-600">{{ location.equipment_count }}</dd>
                </div>
              </dl>
            </div>
          </div>
        </template>

        <!-- Person Information -->
        <template v-else-if="location.location_type === 'person'">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Person Photo & Details -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Person Information</h2>

              <!-- Photo -->
              <div class="flex items-start gap-4 mb-4">
                <div v-if="location.photo_url" class="flex-shrink-0">
                  <img
                    :src="location.photo_url"
                    :alt="location.person_name || location.name"
                    class="w-24 h-24 object-cover rounded-full border-2 border-gray-200"
                  />
                </div>
                <div v-else class="flex-shrink-0 w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center">
                  <svg class="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <div v-if="location.person_name" class="text-lg font-medium text-gray-900">{{ location.person_name }}</div>
                  <div v-if="location.department" class="text-sm text-gray-500">{{ location.department }}</div>
                  <div v-if="location.employee_id" class="text-sm text-gray-500 font-mono">{{ location.employee_id }}</div>
                </div>
              </div>

              <dl class="space-y-3">
                <div v-if="location.person_name">
                  <dt class="text-sm font-medium text-gray-500">Name</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.person_name }}</dd>
                </div>
                <div v-if="location.employee_id">
                  <dt class="text-sm font-medium text-gray-500">Employee ID</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.employee_id }}</dd>
                </div>
                <div v-if="location.department">
                  <dt class="text-sm font-medium text-gray-500">Department</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.department }}</dd>
                </div>
                <div v-if="location.person_contact">
                  <dt class="text-sm font-medium text-gray-500">Contact Information</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.person_contact }}</dd>
                </div>
              </dl>
            </div>

            <!-- Statistics -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
              <dl class="space-y-3">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Equipment Count</dt>
                  <dd class="mt-1 text-2xl font-bold text-sky-600">{{ location.equipment_count }}</dd>
                </div>
              </dl>
            </div>
          </div>
        </template>

        <!-- Warehouse Information -->
        <template v-else-if="location.location_type === 'warehouse'">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Basic Information -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
              <dl class="space-y-3">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Location Name</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.name }}</dd>
                </div>
                <div v-if="location.code">
                  <dt class="text-sm font-medium text-gray-500">Location Code</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.code }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Created At</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ formatDateTime(location.created_at) }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ formatDateTime(location.updated_at) }}</dd>
                </div>
              </dl>
            </div>

            <!-- Address & Contact -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Address & Contact</h2>
              <dl class="space-y-3">
                <div v-if="location.address">
                  <dt class="text-sm font-medium text-gray-500">Address</dt>
                  <dd class="mt-1 text-sm text-gray-900 whitespace-pre-line">{{ location.address }}</dd>
                </div>
                <div v-if="location.phone">
                  <dt class="text-sm font-medium text-gray-500">Phone</dt>
                  <dd class="mt-1 text-sm text-gray-900">
                    <a :href="'tel:' + location.phone" class="text-sky-600 hover:text-sky-800">{{ location.phone }}</a>
                  </dd>
                </div>
                <div v-if="location.email">
                  <dt class="text-sm font-medium text-gray-500">Email</dt>
                  <dd class="mt-1 text-sm text-gray-900">
                    <a :href="'mailto:' + location.email" class="text-sky-600 hover:text-sky-800">{{ location.email }}</a>
                  </dd>
                </div>
                <!-- Contact User (新：指向 User) -->
                <div v-if="location.contact_user_name">
                  <dt class="text-sm font-medium text-gray-500">Contact Person</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.contact_user_name }}</dd>
                </div>
                <!-- Contact Person (舊：指向 Location，作為 fallback) -->
                <div v-else-if="location.contact_person_name">
                  <dt class="text-sm font-medium text-gray-500">Contact Person</dt>
                  <dd class="mt-1 text-sm text-gray-900">
                    <router-link
                      v-if="location.contact_person_id"
                      :to="`/locations/${location.contact_person_id}`"
                      class="text-sky-600 hover:text-sky-800 hover:underline"
                    >
                      {{ location.contact_person_name }}
                    </router-link>
                    <span v-else>{{ location.contact_person_name }}</span>
                  </dd>
                </div>
                <div v-if="!location.address && !location.phone && !location.email && !location.contact_person_name && !location.contact_user_name">
                  <p class="text-sm text-gray-400 italic">No contact information available</p>
                </div>
              </dl>
            </div>

            <!-- Statistics -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
              <dl class="space-y-3">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Equipment Count</dt>
                  <dd class="mt-1 text-2xl font-bold text-sky-600">{{ location.equipment_count }}</dd>
                </div>
              </dl>
            </div>
          </div>
        </template>

        <!-- External Location -->
        <template v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Basic Information -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
              <dl class="space-y-3">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Location Name</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ location.name }}</dd>
                </div>
                <div v-if="location.code">
                  <dt class="text-sm font-medium text-gray-500">Location Code</dt>
                  <dd class="mt-1 text-sm text-gray-900 font-mono">{{ location.code }}</dd>
                </div>
              </dl>
            </div>

            <!-- Statistics -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
              <dl class="space-y-3">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Equipment Count</dt>
                  <dd class="mt-1 text-2xl font-bold text-sky-600">{{ location.equipment_count }}</dd>
                </div>
              </dl>
            </div>
          </div>
        </template>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-12">
        <p class="text-gray-500">Location not found</p>
        <AppButton variant="secondary" class="mt-4" @click="router.push('/locations')">
          Back to Locations
        </AppButton>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLocationStore } from '@/stores/locations'
import MainLayout from '@/layouts/MainLayout.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const locationStore = useLocationStore()

const locationId = computed(() => parseInt(route.params.id as string))
const location = computed(() => locationStore.currentLocation)

function typeLabel(type: string): string {
  const labels: Record<string, string> = {
    vessel: 'Vessel',
    person: 'Person',
    warehouse: 'Warehouse',
    external: 'External',
  }
  return labels[type] || type
}

function typeBadgeClass(type: string): string {
  const variants: Record<string, string> = {
    vessel: 'bg-blue-100 text-blue-800',
    person: 'bg-green-100 text-green-800',
    warehouse: 'bg-purple-100 text-purple-800',
    external: 'bg-gray-100 text-gray-800',
  }
  return variants[type] || 'bg-gray-100 text-gray-800'
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

function handleEdit() {
  if (location.value) {
    router.push(`/locations/${locationId.value}/edit/${location.value.location_type}`)
  }
}

async function handleDelete() {
  if (!confirm('Are you sure you want to delete this location? This action cannot be undone.')) {
    return
  }

  try {
    await locationStore.deleteLocation(locationId.value)
    alert('Location deleted successfully!')
    router.push('/locations')
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Failed to delete location')
  }
}

onMounted(() => {
  locationStore.fetchById(locationId.value)
})
</script>
