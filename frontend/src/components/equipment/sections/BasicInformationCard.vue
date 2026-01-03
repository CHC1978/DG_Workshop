<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
    <dl class="space-y-3">
      <!-- Asset Code -->
      <div>
        <dt class="text-sm font-medium text-gray-500">Asset Code</dt>
        <dd class="mt-1 text-sm text-gray-900 font-mono">{{ equipment.asset_code }}</dd>
      </div>

      <!-- Category -->
      <div>
        <dt class="text-sm font-medium text-gray-500">Category</dt>
        <dd class="mt-1 text-sm text-gray-900">{{ categoryLabel(equipment.category) }}</dd>
      </div>

      <!-- Manufacturer -->
      <div>
        <dt class="text-sm font-medium text-gray-500">Manufacturer</dt>
        <dd class="mt-1 text-sm text-gray-900">{{ equipment.manufacturer }}</dd>
      </div>

      <!-- Model -->
      <div>
        <dt class="text-sm font-medium text-gray-500">Model</dt>
        <dd class="mt-1 text-sm text-gray-900">{{ equipment.model }}</dd>
      </div>

      <!-- Serial Number -->
      <div v-if="equipment.serial_number">
        <dt class="text-sm font-medium text-gray-500">Serial Number</dt>
        <dd class="mt-1 text-sm text-gray-900 font-mono">{{ equipment.serial_number }}</dd>
      </div>

      <!-- Location Info -->
      <div v-if="equipment.current_location_name" class="pt-3 border-t border-gray-200">
        <dt class="text-sm font-medium text-gray-500 flex items-center gap-1">
          <span>📍</span>
          Current Location
        </dt>
        <dd class="mt-1 text-sm text-gray-900">
          <span class="font-medium">{{ locationTypeLabel(equipment.current_location_type) }}:</span>
          {{ equipment.current_location_name }}
        </dd>
      </div>

      <!-- Project Info -->
      <div v-if="equipment.project_code">
        <dt class="text-sm font-medium text-gray-500 flex items-center gap-1">
          <span>📋</span>
          Project
        </dt>
        <dd class="mt-1 text-sm text-gray-900">
          <div class="font-medium text-sky-700">{{ equipment.project_code }}</div>
          <div v-if="equipment.project_name" class="text-xs text-gray-600">{{ equipment.project_name }}</div>
        </dd>
      </div>

      <!-- Assigned User -->
      <div v-if="equipment.assigned_user_name">
        <dt class="text-sm font-medium text-gray-500 flex items-center gap-1">
          <span>👤</span>
          Assigned User
        </dt>
        <dd class="mt-1 text-sm text-gray-900">
          {{ equipment.assigned_user_name }}
        </dd>
      </div>

      <!-- Parent Equipment Info -->
      <div v-if="equipment.parent_equipment_id" class="pt-3 border-t border-gray-200">
        <dt class="text-sm font-medium text-gray-500 flex items-center gap-1">
          <span>🔗</span>
          Parent Equipment
        </dt>
        <dd class="mt-1 text-sm text-gray-900">
          <span
            class="font-medium text-sky-700 hover:text-sky-900 hover:underline cursor-pointer"
            @click="$emit('navigate', equipment.parent_equipment_id)"
          >
            {{ equipment.parent_asset_code }}
          </span>
          <div v-if="equipment.parent_model" class="text-xs text-gray-600 mt-1">{{ equipment.parent_model }}</div>
        </dd>
      </div>

      <!-- Children Components List -->
      <div v-if="childrenEquipment.length > 0" class="pt-3 border-t border-gray-200">
        <dt class="text-sm font-medium text-gray-500 flex items-center gap-1 mb-2">
          <span>🔧</span>
          Child Components ({{ childrenEquipment.length }})
        </dt>
        <dd class="mt-1 space-y-1">
          <div
            v-for="child in childrenEquipment"
            :key="child.id"
            class="text-sm text-gray-900"
          >
            <span
              class="font-medium text-sky-700 hover:text-sky-900 hover:underline cursor-pointer"
              @click="$emit('navigate', child.id)"
            >
              {{ child.asset_code }}
            </span>
            <span class="text-xs text-gray-500 ml-1">- {{ child.model }}</span>
          </div>
        </dd>
      </div>
    </dl>
  </div>
</template>

<script setup lang="ts">
import { useEquipmentLabels } from '@/composables/useEquipmentLabels'
import type { Equipment } from '@/types'

interface Props {
  equipment: Equipment
  childrenEquipment: Equipment[]
}

interface Emits {
  (e: 'navigate', id: number): void
}

defineProps<Props>()
defineEmits<Emits>()

const { categoryLabel, locationTypeLabel } = useEquipmentLabels()
</script>
