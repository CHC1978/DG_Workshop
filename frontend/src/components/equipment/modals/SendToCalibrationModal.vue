<template>
  <!-- Send to Calibration Modal -->
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Send to Calibration</h3>
      <div class="space-y-4">
        <!-- Calibration Due Date (Read-only) -->
        <div v-if="equipment?.calibration_due" class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div class="flex items-center gap-2">
            <span class="text-yellow-600 font-medium text-sm">Calibration Due:</span>
            <span class="text-sm text-gray-900">{{ formatDate(equipment.calibration_due) }}</span>
          </div>
          <p v-if="isOverdue" class="text-xs text-red-600 mt-1">This equipment is overdue for calibration!</p>
        </div>
        <div v-else class="p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <span class="text-sm text-gray-500">No calibration due date set</span>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Send to
          </label>
          <select
            v-model="calibrationForm.locationId"
            class="w-full px-3 py-2 border rounded-lg"
          >
            <option :value="null">Select...</option>
            <option v-for="location in filteredLocations" :key="location.id" :value="location.id">
              {{ location.name }} ({{ location.location_type }})
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
          <textarea
            v-model="calibrationForm.notes"
            class="w-full px-3 py-2 border rounded-lg"
            rows="3"
            placeholder="Enter calibration notes..."
          ></textarea>
        </div>

        <!-- Include Children Option -->
        <div v-if="childrenCount > 0" class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
          <label class="flex items-start gap-2 cursor-pointer">
            <input
              type="checkbox"
              v-model="calibrationForm.includeChildren"
              class="mt-1 w-4 h-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500"
            />
            <div class="flex-1">
              <span class="text-sm font-medium text-gray-900">Include Child Components</span>
              <p class="text-xs text-gray-600 mt-1">
                Send all {{ childrenCount }} child component(s) to calibration as well
              </p>
            </div>
          </label>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t">
          <AppButton variant="secondary" @click="$emit('close')">Cancel</AppButton>
          <AppButton @click="handleSubmit" :loading="submitting">Send to Calibration</AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { equipmentApi } from '@/api/equipment'
import { useUiStore } from '@/stores/ui'
import AppButton from '@/components/common/AppButton.vue'
import type { Equipment, Location } from '@/types'

interface Props {
  show: boolean
  equipment: Equipment | null
  childrenCount: number
  locations: Location[]
}

interface Emits {
  (e: 'close'): void
  (e: 'submitted', data: { success: boolean }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const uiStore = useUiStore()

const submitting = ref(false)

// Filter locations to show only warehouses and persons
const filteredLocations = computed(() =>
  props.locations.filter(l => l.location_type === 'warehouse' || l.location_type === 'person')
)

// Check if calibration is overdue
const isOverdue = computed(() => {
  if (!props.equipment?.calibration_due) return false
  return new Date(props.equipment.calibration_due) < new Date()
})

const calibrationForm = ref({
  locationId: null as number | null,
  notes: '',
  includeChildren: true
})

// Reset form when modal closes
watch(() => props.show, (newShow) => {
  if (!newShow) {
    calibrationForm.value = { locationId: null, notes: '', includeChildren: true }
  }
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

async function handleSubmit() {
  if (!props.equipment) return

  submitting.value = true

  try {
    await equipmentApi.sendToCalibration(props.equipment.id, {
      location_id: calibrationForm.value.locationId || undefined,
      notes: calibrationForm.value.notes || undefined
    })

    uiStore.showNotification('success', 'Equipment sent to calibration')
    emit('submitted', { success: true })
    emit('close')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to send to calibration')
  } finally {
    submitting.value = false
  }
}
</script>
