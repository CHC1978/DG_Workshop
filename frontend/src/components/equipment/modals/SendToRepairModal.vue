<template>
  <!-- Send to Repair Modal -->
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Send to Repair</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Send to
          </label>
          <select
            v-model="repairForm.locationId"
            class="w-full px-3 py-2 border rounded-lg"
          >
            <option :value="null">Select...</option>
            <option v-for="location in filteredLocations" :key="location.id" :value="location.id">
              {{ location.name }} ({{ location.location_type }})
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Expected Return Date
          </label>
          <input
            type="date"
            v-model="repairForm.expectedReturnDate"
            class="w-full px-3 py-2 border rounded-lg"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
          <textarea
            v-model="repairForm.notes"
            class="w-full px-3 py-2 border rounded-lg"
            rows="3"
            placeholder="Enter repair notes, fault description..."
          ></textarea>
        </div>

        <!-- File Upload for Fault Report -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Fault Report (optional)
          </label>
          <input
            ref="fileInput"
            type="file"
            @change="handleFileChange"
            class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
          />
          <p class="text-xs text-gray-500 mt-1">Supported: PDF, Word, Images</p>
        </div>

        <!-- Include Children Option -->
        <div v-if="childrenCount > 0" class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
          <label class="flex items-start gap-2 cursor-pointer">
            <input
              type="checkbox"
              v-model="repairForm.includeChildren"
              class="mt-1 w-4 h-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500"
            />
            <div class="flex-1">
              <span class="text-sm font-medium text-gray-900">Include Child Components</span>
              <p class="text-xs text-gray-600 mt-1">
                Send all {{ childrenCount }} child component(s) to repair as well
              </p>
            </div>
          </label>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t">
          <AppButton variant="secondary" @click="$emit('close')">Cancel</AppButton>
          <AppButton @click="handleSubmit" :loading="submitting">Send to Repair</AppButton>
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

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const submitting = ref(false)

// Filter locations to show only warehouses and persons
const filteredLocations = computed(() =>
  props.locations.filter(l => l.location_type === 'warehouse' || l.location_type === 'person')
)

const repairForm = ref({
  locationId: null as number | null,
  expectedReturnDate: '',
  notes: '',
  includeChildren: true
})

// Reset form when modal closes
watch(() => props.show, (newShow) => {
  if (!newShow) {
    repairForm.value = { locationId: null, expectedReturnDate: '', notes: '', includeChildren: true }
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
})

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    selectedFile.value = input.files[0]
  }
}

async function handleSubmit() {
  if (!props.equipment) return

  submitting.value = true

  try {
    await equipmentApi.repair(props.equipment.id, {
      location_id: repairForm.value.locationId || undefined,
      expected_return_date: repairForm.value.expectedReturnDate || undefined,
      notes: repairForm.value.notes || undefined
    })

    // TODO: Upload fault report file if selected
    // This would require a separate API endpoint for log attachments

    uiStore.showNotification('success', 'Equipment sent to repair')
    emit('submitted', { success: true })
    emit('close')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to send to repair')
  } finally {
    submitting.value = false
  }
}
</script>
