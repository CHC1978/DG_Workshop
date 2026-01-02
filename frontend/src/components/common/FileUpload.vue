<template>
  <div class="w-full">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
    </label>

    <div class="space-y-2">
      <!-- Current File Display -->
      <div v-if="currentFileUrl" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-700">Current file</span>
          <a
            :href="fullUrl"
            target="_blank"
            class="text-sm text-sky-600 hover:text-sky-800"
          >
            {{ getFileName(currentFileUrl) }}
          </a>
        </div>
        <button
          v-if="!disabled"
          type="button"
          @click="handleDelete"
          class="text-sm text-red-600 hover:text-red-800"
        >
          Delete
        </button>
      </div>

      <!-- File Input -->
      <div class="flex items-center space-x-2">
        <input
          ref="fileInput"
          type="file"
          :accept="accept"
          :disabled="disabled || uploading"
          @change="handleFileChange"
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 disabled:opacity-50"
        />
        <AppButton
          v-if="selectedFile && !uploading"
          type="button"
          variant="primary"
          size="sm"
          @click="handleUpload"
          :disabled="disabled"
        >
          Upload
        </AppButton>
      </div>

      <!-- Upload Progress -->
      <div v-if="uploading" class="text-sm text-gray-600">
        Uploading...
      </div>

      <!-- Error Message -->
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <!-- Hint -->
      <p v-if="hint && !error" class="text-sm text-gray-500">{{ hint }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import apiClient from '@/api/client'
import AppButton from './AppButton.vue'

interface Props {
  label?: string
  currentFileUrl?: string
  equipmentId?: number
  calibrationId?: number
  fileType: 'photo' | 'manual' | 'report' | 'calibration'
  accept?: string
  hint?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  accept: '*/*',
  disabled: false,
})

const emit = defineEmits<{
  uploaded: [url: string]
  deleted: []
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const error = ref('')

const fullUrl = computed(() => {
  if (!props.currentFileUrl) return ''
  if (props.currentFileUrl.startsWith('http')) return props.currentFileUrl
  return `http://localhost:8000${props.currentFileUrl}`
})

function getFileName(url: string): string {
  return url.split('/').pop() || 'file'
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    selectedFile.value = file
    error.value = ''
  }
}

async function handleUpload() {
  if (!selectedFile.value) {
    error.value = 'Please select a file'
    return
  }

  if (props.fileType === 'calibration' && !props.calibrationId) {
    error.value = 'Calibration ID required'
    return
  }

  if (props.fileType !== 'calibration' && !props.equipmentId) {
    error.value = 'Equipment ID required'
    return
  }

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  uploading.value = true
  error.value = ''

  try {
    let endpoint = ''
    if (props.fileType === 'calibration') {
      endpoint = `/uploads/calibrations/${props.calibrationId}/report`
    } else {
      endpoint = `/uploads/equipment/${props.equipmentId}/${props.fileType === 'report' ? 'calibration-report' : props.fileType}`
    }

    // Use apiClient which automatically sends httpOnly cookies via withCredentials
    const response = await apiClient.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    emit('uploaded', response.data.url)
    selectedFile.value = null

    // Reset file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (err: any) {
    console.error('Upload failed:', err)
    error.value = err.response?.data?.detail || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

async function handleDelete() {
  if (!confirm('Delete this file?')) {
    return
  }

  try {
    let endpoint = ''
    if (props.fileType === 'calibration') {
      if (!props.calibrationId) return
      endpoint = `/uploads/calibrations/${props.calibrationId}/report`
    } else {
      if (!props.equipmentId) return
      endpoint = `/uploads/equipment/${props.equipmentId}/${props.fileType === 'report' ? 'calibration-report' : props.fileType}`
    }

    // Use apiClient which automatically sends httpOnly cookies via withCredentials
    await apiClient.delete(endpoint)
    emit('deleted')
  } catch (err: any) {
    console.error('Delete failed:', err)
    error.value = err.response?.data?.detail || 'Delete failed'
  }
}
</script>
