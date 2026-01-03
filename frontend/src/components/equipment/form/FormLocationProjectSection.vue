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
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
        @change="handleLocationChange"
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
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
        @change="$emit('update:modelValue', { ...modelValue, project_id: ($event.target as HTMLSelectElement).value ? parseInt(($event.target as HTMLSelectElement).value) : null })"
      >
        <option :value="null">None</option>
        <option v-for="project in projects" :key="project.id" :value="project.id">
          {{ project.code }} - {{ project.name }}
        </option>
      </select>
      <p v-if="suggestedProject" class="mt-1 text-sm text-sky-600">
        Suggested: {{ suggestedProject.code }} (from selected Vessel)
      </p>
    </div>

    <!-- Installation Type -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Installation Type
      </label>
      <select
        :value="modelValue.installation_type"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
        @change="$emit('update:modelValue', { ...modelValue, installation_type: ($event.target as HTMLSelectElement).value || null })"
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
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
        @input="$emit('update:modelValue', { ...modelValue, installation_date: ($event.target as HTMLInputElement).value })"
      />
    </div>

    <!-- Installation Notes -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Installation Notes
      </label>
      <textarea
        :value="modelValue.installation_notes"
        rows="2"
        placeholder="Installation details, configuration notes, etc."
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
        @input="$emit('update:modelValue', { ...modelValue, installation_notes: ($event.target as HTMLTextAreaElement).value })"
      ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Location, Project } from '@/types'

interface FormData {
  current_location_id: number | null
  project_id: number | null
  installation_type: string | null
  installation_date: string
  installation_notes: string
}

interface Props {
  modelValue: FormData
  locations: Location[]
  projects: Project[]
  suggestedProject: Project | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: FormData): void
  (e: 'location-change', locationId: number | null): void
}>()

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

function handleLocationChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const locationId = target.value ? parseInt(target.value) : null
  emit('update:modelValue', { ...props.modelValue, current_location_id: locationId })
  emit('location-change', locationId)
}
</script>
