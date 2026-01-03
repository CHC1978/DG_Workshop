<template>
  <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
    <div>
      <!-- Parent Equipment (if exists) -->
      <div v-if="equipment.parent_equipment_id" class="mb-2">
        <p class="text-xs text-gray-500 mb-1">Parent Equipment</p>
        <h2
          class="text-3xl sm:text-4xl font-bold text-sky-700 hover:text-sky-900 hover:underline cursor-pointer"
          @click="$emit('navigate', equipment.parent_equipment_id)"
        >
          {{ equipment.parent_asset_code }}
        </h2>
        <p v-if="equipment.parent_model" class="text-sm text-gray-600 mt-1">
          {{ equipment.parent_model }}
        </p>
      </div>

      <!-- Current Equipment -->
      <div>
        <p v-if="equipment.parent_equipment_id" class="text-xs text-gray-500 mb-1">Child Component</p>
        <h1 :class="equipment.parent_equipment_id ? 'text-xl sm:text-2xl' : 'text-2xl sm:text-3xl'" class="font-bold text-gray-900">
          {{ equipment.asset_code }}
        </h1>
        <p class="mt-1 text-base sm:text-lg text-gray-600">
          {{ equipment.manufacturer }} {{ equipment.model }}
        </p>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap gap-2">
      <AppButton
        v-if="canEdit"
        variant="secondary"
        size="sm"
        @click="$emit('edit')"
      >
        Edit
      </AppButton>
      <AppButton
        variant="secondary"
        size="sm"
        @click="$emit('download-qr')"
      >
        Download QR
      </AppButton>
      <AppButton
        v-if="canDelete"
        variant="danger"
        size="sm"
        @click="$emit('delete')"
      >
        Delete
      </AppButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppButton from '@/components/common/AppButton.vue'
import type { Equipment } from '@/types'

interface Props {
  equipment: Equipment
  canEdit: boolean
  canDelete: boolean
}

interface Emits {
  (e: 'navigate', id: number): void
  (e: 'edit'): void
  (e: 'download-qr'): void
  (e: 'delete'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>
