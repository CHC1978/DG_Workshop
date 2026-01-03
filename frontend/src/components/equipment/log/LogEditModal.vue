<template>
  <BaseModal :show="show" title="Edit Activity Log" size="2xl" @close="$emit('close')">
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
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="$emit('close')">
        Cancel
      </AppButton>
      <AppButton @click="handleSave" :loading="saving">
        Save Changes
      </AppButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseModal from '@/components/common/BaseModal.vue'
import AppButton from '@/components/common/AppButton.vue'
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
