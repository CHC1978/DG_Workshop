<template>
  <BaseModal :show="show" title="Log Attachments" size="2xl" @close="$emit('close')">
    <!-- Log Info -->
    <div v-if="log" class="mb-4 p-3 bg-gray-50 rounded">
      <p class="text-sm font-medium">{{ log.description }}</p>
      <p class="text-xs text-gray-500 mt-1">{{ formatDateTime(log.created_at) }}</p>
    </div>

    <!-- Attachments List -->
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-500">Loading attachments...</p>
    </div>

    <div v-else-if="attachments.length === 0" class="text-center py-8">
      <p class="text-gray-500">No attachments yet</p>
    </div>

    <div v-else class="space-y-3 mb-4">
      <div
        v-for="att in attachments"
        :key="att.id"
        class="flex items-center justify-between p-3 border rounded hover:bg-gray-50"
      >
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{{ att.file_name }}</p>
          <p class="text-xs text-gray-500">
            {{ (att.file_size / 1024).toFixed(1) }} KB · {{ att.file_type }}
          </p>
          <p v-if="att.description" class="text-xs text-gray-600 mt-1">{{ att.description }}</p>
        </div>
        <div class="flex items-center gap-2 ml-4">
          <a
            :href="getAttachmentUrl(att.file_url)"
            target="_blank"
            class="px-2 py-1 text-xs font-medium text-sky-600 hover:text-sky-800 hover:bg-sky-50 rounded transition-colors"
            title="View in new tab"
          >
            View
          </a>
          <a
            :href="getAttachmentUrl(att.file_url)"
            :download="att.file_name"
            class="px-2 py-1 text-xs font-medium text-green-600 hover:text-green-800 hover:bg-green-50 rounded transition-colors"
            title="Download file"
          >
            Download
          </a>
          <button
            @click="handleDelete(att.id)"
            class="px-2 py-1 text-xs font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
            title="Delete attachment"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Section -->
    <div class="border-t pt-4">
      <h4 class="text-sm font-semibold mb-3">Upload New Attachment</h4>
      <div class="space-y-3">
        <select
          v-model="uploadType"
          class="w-full px-3 py-2 border rounded-lg"
        >
          <option value="calibration_report">Calibration Report</option>
          <option value="damage_photo">Damage Photo</option>
          <option value="repair_document">Repair Document</option>
          <option value="maintenance_record">Maintenance Record</option>
          <option value="other">Other</option>
        </select>

        <input
          v-model="uploadDescription"
          type="text"
          placeholder="Description (optional)"
          class="w-full px-3 py-2 border rounded-lg"
        />

        <div class="flex items-center gap-2">
          <input
            ref="fileInput"
            type="file"
            @change="handleFileChange"
            class="flex-1 text-sm"
          />
          <button
            v-if="selectedFile"
            @click="handleUpload"
            :disabled="uploading"
            class="px-4 py-2 text-sm font-medium text-white bg-sky-600 hover:bg-sky-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ uploading ? 'Uploading...' : 'Upload' }}
          </button>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import apiClient from '@/api/client'
import BaseModal from '@/components/common/BaseModal.vue'
import type { EquipmentLog } from '@/types'

interface Attachment {
  id: number
  file_name: string
  file_url: string
  file_size: number
  file_type: string
  description?: string
}

interface Props {
  show: boolean
  log: EquipmentLog | null
}

interface Emits {
  (e: 'close'): void
  (e: 'attachmentDeleted', attachmentId: number): void
  (e: 'attachmentUploaded'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const loading = ref(false)
const uploading = ref(false)
const attachments = ref<Attachment[]>([])
const uploadType = ref('other')
const uploadDescription = ref('')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// Load attachments when modal opens or log changes
watch(() => [props.show, props.log], async ([show, log]) => {
  if (show && log) {
    await loadAttachments(log.id)
  }
}, { immediate: true })

async function loadAttachments(logId: number) {
  loading.value = true
  try {
    const response = await apiClient.get(`/uploads/equipment-logs/${logId}/attachments`)
    attachments.value = response.data
  } catch (error) {
    console.error('Failed to load attachments:', error)
    attachments.value = []
  } finally {
    loading.value = false
  }
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

function getAttachmentUrl(fileUrl: string): string {
  return fileUrl.startsWith('/') ? fileUrl : `/${fileUrl}`
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  selectedFile.value = target.files?.[0] || null
}

async function handleUpload() {
  if (!selectedFile.value || !props.log) return

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('attachment_type', uploadType.value)
    if (uploadDescription.value) {
      formData.append('description', uploadDescription.value)
    }

    await apiClient.post(
      `/uploads/equipment-logs/${props.log.id}/attachments`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    // Reset form
    selectedFile.value = null
    uploadDescription.value = ''
    if (fileInput.value) {
      fileInput.value.value = ''
    }

    // Reload attachments
    await loadAttachments(props.log.id)
    emit('attachmentUploaded')
  } catch (error: any) {
    console.error('Upload failed:', error)
    alert(error.response?.data?.detail || 'Upload failed')
  } finally {
    uploading.value = false
  }
}

async function handleDelete(attachmentId: number) {
  if (!confirm('Delete this attachment?')) return

  try {
    await apiClient.delete(`/uploads/log-attachments/${attachmentId}`)

    // Remove from list
    attachments.value = attachments.value.filter(a => a.id !== attachmentId)
    emit('attachmentDeleted', attachmentId)
  } catch (error: any) {
    console.error('Delete failed:', error)
    alert('Delete failed')
  }
}

// Expose reload method
defineExpose({
  reload: () => props.log && loadAttachments(props.log.id)
})
</script>
