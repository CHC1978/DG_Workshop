<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Add Maintenance Record</h3>

      <div class="space-y-4">
        <!-- Last Maintenance Date -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Last Maintenance Date
          </label>
          <input
            v-model="formData.last_maintenance_date"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
        </div>

        <!-- Next Maintenance Due -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Next Maintenance Due
          </label>
          <input
            v-model="formData.next_maintenance_date"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          />
        </div>

        <!-- Maintenance Notes -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Maintenance Notes <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="formData.maintenance_notes"
            rows="4"
            required
            placeholder="Enter maintenance details, parts replaced, work performed..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500">
            Describe the maintenance work performed
          </p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-4 border-t">
          <AppButton variant="secondary" @click="$emit('close')">
            Cancel
          </AppButton>
          <AppButton
            @click="handleSave"
            :disabled="!formData.maintenance_notes"
          >
            Save Record
          </AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Equipment } from '@/types'

interface Props {
  show: boolean
  equipment: Equipment | null
}

interface Emits {
  (e: 'close'): void
  (e: 'saved', data: MaintenanceData): void
}

interface MaintenanceData {
  last_maintenance_date: string
  next_maintenance_date: string
  maintenance_notes: string
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formData = reactive<MaintenanceData>({
  last_maintenance_date: '',
  next_maintenance_date: '',
  maintenance_notes: '',
})

// Reset form when modal is opened
watch(() => props.show, (newShow) => {
  if (newShow) {
    // Pre-fill with current data if available
    if (props.equipment) {
      formData.last_maintenance_date = props.equipment.last_maintenance_date || ''
      formData.next_maintenance_date = props.equipment.next_maintenance_date || ''
      formData.maintenance_notes = props.equipment.maintenance_notes || ''
    }
  }
})

function handleSave() {
  if (!formData.maintenance_notes.trim()) {
    return
  }

  emit('saved', {
    last_maintenance_date: formData.last_maintenance_date,
    next_maintenance_date: formData.next_maintenance_date,
    maintenance_notes: formData.maintenance_notes,
  })
}
</script>
