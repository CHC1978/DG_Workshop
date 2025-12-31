<template>
  <div class="space-y-4 p-4 bg-sky-50 rounded-lg border border-sky-200">
    <h3 class="text-sm font-semibold text-gray-700">Location & Project</h3>

    <!-- Current Location -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Current Location
      </label>
      <select
        :value="modelValue.current_location_id"
        @change="updateLocation"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
      >
        <option :value="null">None (In Stock)</option>
        <optgroup v-if="vesselLocations.length > 0" label="Vessels">
          <option v-for="loc in vesselLocations" :key="loc.id" :value="loc.id">
            {{ loc.name }} {{ loc.code ? `(${loc.code})` : '' }}
          </option>
        </optgroup>
        <optgroup v-if="personLocations.length > 0" label="Persons">
          <option v-for="loc in personLocations" :key="loc.id" :value="loc.id">
            {{ loc.name }} {{ loc.code ? `(${loc.code})` : '' }}
          </option>
        </optgroup>
        <optgroup v-if="warehouseLocations.length > 0" label="Warehouses">
          <option v-for="loc in warehouseLocations" :key="loc.id" :value="loc.id">
            {{ loc.name }} {{ loc.code ? `(${loc.code})` : '' }}
          </option>
        </optgroup>
      </select>
    </div>

    <!-- Project -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Project
      </label>
      <select
        :value="modelValue.project_id"
        @change="updateField('project_id', ($event.target as HTMLSelectElement).value ? parseInt(($event.target as HTMLSelectElement).value) : null)"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
      >
        <option :value="null">None</option>
        <option v-for="project in projects" :key="project.id" :value="project.id">
          {{ project.code }} - {{ project.name }}
        </option>
      </select>
      <p v-if="suggestedProject" class="mt-1 text-sm text-sky-600">
        💡 Suggested: {{ suggestedProject.code }} (from selected Vessel)
      </p>
    </div>

    <!-- Installation Type -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Installation Type
      </label>
      <select
        :value="modelValue.installation_type"
        @change="updateField('installation_type', ($event.target as HTMLSelectElement).value || null)"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
      >
        <option :value="null">Not Specified</option>
        <option value="permanent">Permanent Installation</option>
        <option value="project">Project-Based</option>
        <option value="temporary">Temporary</option>
      </select>
    </div>

    <!-- Installation Date -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Installation Date
      </label>
      <input
        type="date"
        :value="modelValue.installation_date"
        @input="updateField('installation_date', ($event.target as HTMLInputElement).value)"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
      />
    </div>

    <!-- Installation Notes -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Installation Notes
      </label>
      <textarea
        :value="modelValue.installation_notes"
        @input="updateField('installation_notes', ($event.target as HTMLTextAreaElement).value)"
        rows="2"
        placeholder="Installation details, configuration notes, etc."
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
      ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Location, Project } from '@/types'

interface LocationProjectInfo {
  current_location_id: number | null
  project_id: number | null
  installation_type: string | null
  installation_date: string
  installation_notes: string
}

interface Props {
  modelValue: LocationProjectInfo
  locations: Location[]
  projects: Project[]
}

interface Emits {
  (e: 'update:modelValue', value: LocationProjectInfo): void
  (e: 'locationChanged', locationId: number | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const suggestedProject = ref<Project | null>(null)

// Computed: Group locations by type
const vesselLocations = computed(() =>
  props.locations.filter(loc => loc.location_type === 'vessel' && loc.is_active)
)
const personLocations = computed(() =>
  props.locations.filter(loc => loc.location_type === 'person' && loc.is_active)
)
const warehouseLocations = computed(() =>
  props.locations.filter(loc => loc.location_type === 'warehouse' && loc.is_active)
)

function updateField(field: keyof LocationProjectInfo, value: any) {
  emit('update:modelValue', {
    ...props.modelValue,
    [field]: value
  })
}

function updateLocation(event: Event) {
  const target = event.target as HTMLSelectElement
  const locationId = target.value ? parseInt(target.value) : null

  updateField('current_location_id', locationId)
  handleLocationChange(locationId)
  emit('locationChanged', locationId)
}

function handleLocationChange(locationId: number | null) {
  suggestedProject.value = null

  if (!locationId) return

  // Find selected location
  const selectedLocation = props.locations.find(loc => loc.id === locationId)

  if (!selectedLocation) return

  // If it's a vessel with a project, suggest the project
  if (selectedLocation.location_type === 'vessel' && selectedLocation.current_project_id) {
    const vesselProject = props.projects.find(p => p.id === selectedLocation.current_project_id)
    if (vesselProject) {
      suggestedProject.value = vesselProject
      // Auto-select the suggested project
      updateField('project_id', vesselProject.id)
    }
  }
}
</script>
