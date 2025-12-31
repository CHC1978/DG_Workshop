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

        <!-- Attachments -->
        <div class="space-y-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <label class="block text-sm font-medium text-gray-700">
            Attachments (Optional)
          </label>
          <p class="text-xs text-gray-500">
            Upload maintenance reports, photos, or other relevant documents
          </p>

          <!-- File Input -->
          <input
            ref="fileInput"
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            @change="handleFileSelect"
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100"
          />

          <!-- Selected Files List -->
          <div v-if="selectedFiles.length > 0" class="space-y-2">
            <p class="text-xs font-medium text-gray-700">Selected Files:</p>
            <div
              v-for="(file, index) in selectedFiles"
              :key="index"
              class="flex items-center justify-between p-2 bg-white border border-gray-200 rounded"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-900 truncate">{{ file.name }}</p>
                <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
              </div>
              <button
                @click="removeFile(index)"
                class="ml-2 text-red-600 hover:text-red-800 text-sm"
              >
                Remove
              </button>
            </div>
          </div>
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
  attachments: File[]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])

const formData = reactive<MaintenanceData>({
  last_maintenance_date: '',
  next_maintenance_date: '',
  maintenance_notes: '',
  attachments: [],
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
    // Reset file selection
    selectedFiles.value = []
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
})

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const newFiles = Array.from(target.files)
    selectedFiles.value = [...selectedFiles.value, ...newFiles]
  }
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1)
  // Clear the file input to allow re-selecting the same file
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function handleSave() {
  if (!formData.maintenance_notes.trim()) {
    return
  }

  emit('saved', {
    last_maintenance_date: formData.last_maintenance_date,
    next_maintenance_date: formData.next_maintenance_date,
    maintenance_notes: formData.maintenance_notes,
    attachments: selectedFiles.value,
  })
}
</script>
