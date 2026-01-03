<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Edit Activity Log</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          ✕
        </button>
      </div>

      <div v-if="log" class="space-y-4">
        <!-- Read-only Info -->
        <div class="p-3 bg-gray-50 rounded">
          <p class="text-xs text-gray-500 mb-1">Type: {{ logTypeLabel(log.log_type) }}</p>
          <p class="text-xs text-gray-500">Created: {{ formatDateTime(log.created_at) }} by {{ log.created_by_username || 'System' }}</p>
          <p v-if="log.is_edited" class="text-xs text-orange-600 mt-1">
            Edited {{ log.edit_count }} time(s), last at {{ formatDateTime(log.edited_at) }} by {{ log.edited_by_username }}
          </p>
        </div>

        <!-- Change Record Display -->
        <LogChangeRecordDisplay
          :old-value="log.old_value"
          :new-value="log.new_value"
        />

        <!-- Editable fields -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Description <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="form.description"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sky-500"
            rows="4"
            placeholder="Enter description..."
          ></textarea>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-4 border-t">
          <button
            @click="$emit('close')"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleSave"
            :disabled="saving"
            class="px-4 py-2 text-sm font-medium text-white bg-sky-600 hover:bg-sky-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import LogChangeRecordDisplay from './LogChangeRecordDisplay.vue'

interface Props {
  show: boolean
  log: any
}

interface Emits {
  (e: 'close'): void
  (e: 'save', form: { description: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const saving = ref(false)
const form = ref({
  description: ''
})

// Reset form when log changes
watch(() => props.log, (newLog) => {
  if (newLog) {
    form.value.description = newLog.description || ''
  }
}, { immediate: true })

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

function logTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    status_change: 'Status',
    location_change: 'Location',
    rental_start: 'Rental Start',
    rental_end: 'Rental End',
    calibration: 'Calibration',
    maintenance: 'Maintenance',
    note: 'Note',
    created: 'Created',
    updated: 'Updated',
  }
  return labels[type] || type
}

function handleSave() {
  if (!form.value.description.trim()) {
    alert('Description is required')
    return
  }
  emit('save', { description: form.value.description })
}

// Expose saving state for parent to control
defineExpose({
  setSaving: (val: boolean) => { saving.value = val }
})
</script>
