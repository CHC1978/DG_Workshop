<template>
  <div class="bg-white rounded-lg shadow p-6">
    <!-- Status Badge -->
    <div class="mb-4">
      <span :class="statusBadgeClass(equipment.status)" class="text-lg px-4 py-2">
        {{ statusLabel(equipment.status, equipment.current_location_type) }}
      </span>
    </div>

    <!-- Status Actions (Operator+ only) -->
    <div v-if="canPerformActions" class="pt-4 border-t border-gray-200">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Status Actions</h2>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Change Status To:
          </label>
          <select
            v-model="selectedAction"
            class="w-full sm:w-auto px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          >
            <option value="">-- Select Action --</option>
            <option value="deploy">Deploy Equipment</option>
            <option value="return">Return Equipment</option>
            <option value="repair">Send to Repair</option>
            <option value="calibration">Send to Calibration</option>
            <option value="in_stock">Set to In Stock</option>
            <option value="rented">Set to Rented</option>
            <option value="maintenance">Add Maintenance Record</option>
          </select>
        </div>

        <AppButton
          :disabled="!selectedAction"
          variant="primary"
          @click="handleExecute"
        >
          Execute Action
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import AppButton from '@/components/common/AppButton.vue'
import { useEquipmentLabels } from '@/composables/useEquipmentLabels'
import type { Equipment } from '@/types'

interface Props {
  equipment: Equipment
  canPerformActions: boolean
}

interface Emits {
  (e: 'action-selected', action: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { statusLabel, statusBadgeClass } = useEquipmentLabels()

const selectedAction = ref('')

// Reset selection when equipment changes
watch(() => props.equipment.id, () => {
  selectedAction.value = ''
})

function handleExecute() {
  if (selectedAction.value) {
    emit('action-selected', selectedAction.value)
    selectedAction.value = ''
  }
}
</script>
