<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
      <h2 class="text-lg font-semibold text-gray-900">Sub-Equipment / Components</h2>
      <AppButton
        v-if="authStore.isManager"
        variant="primary"
        size="sm"
        @click="openCreateModal"
      >
        Add Component
      </AppButton>
    </div>

    <div v-if="subEquipmentStore.loading" class="text-center py-8">
      <p class="text-gray-500">Loading...</p>
    </div>

    <div v-else-if="subEquipmentStore.subEquipmentList.length === 0" class="text-center py-8">
      <p class="text-gray-500">No sub-equipment yet</p>
      <p class="text-sm text-gray-400 mt-2">Click "Add Component" to add components</p>
    </div>

    <div v-else>
      <!-- Desktop Table -->
      <div class="hidden md:block overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Asset Code
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Component Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Serial Number
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="subEq in subEquipmentStore.subEquipmentList" :key="subEq.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                {{ subEq.asset_code }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ subEq.component_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ subEq.serial_number || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="statusBadgeClass(subEq.status)" class="px-2 py-1 text-xs font-semibold rounded">
                  {{ statusLabel(subEq.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm space-x-3">
                <router-link
                  :to="`/sub-equipment/${subEq.id}`"
                  class="text-sky-600 hover:text-sky-900"
                >
                  View
                </router-link>
                <button
                  v-if="authStore.isManager"
                  @click="openEditModal(subEq)"
                  class="text-indigo-600 hover:text-indigo-900"
                >
                  Edit
                </button>
                <button
                  v-if="authStore.isManager"
                  @click="handleDelete(subEq)"
                  class="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Cards -->
      <div class="block md:hidden divide-y divide-gray-200">
      <div
        v-for="subEq in subEquipmentStore.subEquipmentList"
        :key="subEq.id"
        class="p-4 hover:bg-gray-50"
      >
        <div class="flex justify-between items-start mb-2">
          <div>
            <p class="font-mono text-sm font-semibold text-gray-900">{{ subEq.asset_code }}</p>
            <p class="text-sm text-gray-600">{{ subEq.component_name }}</p>
          </div>
          <span :class="statusBadgeClass(subEq.status)" class="px-2 py-1 text-xs font-semibold rounded">
            {{ statusLabel(subEq.status) }}
          </span>
        </div>
        <p v-if="subEq.serial_number" class="text-xs text-gray-500 mb-2">
          序號: {{ subEq.serial_number }}
        </p>
        <div class="flex gap-2">
          <router-link
            :to="`/sub-equipment/${subEq.id}`"
            class="text-sm text-sky-600 hover:text-sky-900"
          >
            View
          </router-link>
          <button
            v-if="authStore.isManager"
            @click="openEditModal(subEq)"
            class="text-sm text-indigo-600 hover:text-indigo-900"
          >
            Edit
          </button>
          <button
            v-if="authStore.isManager"
            @click="handleDelete(subEq)"
            class="text-sm text-red-600 hover:text-red-900"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ isEditing ? 'Edit Sub-Equipment' : 'Add Sub-Equipment' }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            ✕
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Component Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.component_name"
              type="text"
              placeholder="e.g., Antenna 1, IMU Cable, IMU Main Unit"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Serial Number (optional)
            </label>
            <input
              v-model="formData.serial_number"
              type="text"
              placeholder="e.g., ANT-001-12345"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            />
          </div>

          <div v-if="isEditing">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              v-model="formData.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            >
              <option value="ordering">Ordering</option>
              <option value="in_stock">In Stock</option>
              <option value="deployed">Deployed</option>
              <option value="rented">Rented</option>
              <option value="repair">Under Repair</option>
              <option value="calibrating">Calibrating</option>
              <option value="disposed">Disposed</option>
              <option value="lost">Lost</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Notes (optional)
            </label>
            <textarea
              v-model="formData.notes"
              placeholder="Notes..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              rows="3"
            ></textarea>
          </div>

          <div class="flex gap-2 justify-end pt-4 border-t">
            <AppButton variant="secondary" @click="closeModal">
              Cancel
            </AppButton>
            <AppButton @click="handleSubmit" :loading="submitting">
              {{ isEditing ? 'Save' : 'Create' }}
            </AppButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSubEquipmentStore } from '@/stores/subEquipment'
import { useUiStore } from '@/stores/ui'
import AppButton from '@/components/common/AppButton.vue'
import type { SubEquipment } from '@/types'

const props = defineProps<{
  parentEquipmentId: number
}>()

const authStore = useAuthStore()
const subEquipmentStore = useSubEquipmentStore()
const uiStore = useUiStore()

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)

const formData = ref({
  component_name: '',
  serial_number: '',
  status: 'in_stock',
  notes: '',
})

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    ordering: 'Ordering',
    in_stock: 'In Stock',
    deployed: 'Deployed',
    rented: 'Rented',
    repair: 'Under Repair',
    calibrating: 'Calibrating',
    disposed: 'Disposed',
    lost: 'Lost',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const variants: Record<string, string> = {
    ordering: 'bg-yellow-100 text-yellow-800',
    in_stock: 'bg-green-100 text-green-800',
    deployed: 'bg-blue-100 text-blue-800',
    rented: 'bg-purple-100 text-purple-800',
    repair: 'bg-orange-100 text-orange-800',
    calibrating: 'bg-cyan-100 text-cyan-800',
    disposed: 'bg-gray-100 text-gray-800',
    lost: 'bg-red-100 text-red-800',
  }
  return variants[status] || 'bg-gray-100 text-gray-800'
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  formData.value = {
    component_name: '',
    serial_number: '',
    status: 'in_stock',
    notes: '',
  }
  showModal.value = true
}

function openEditModal(subEq: SubEquipment) {
  isEditing.value = true
  editingId.value = subEq.id
  formData.value = {
    component_name: subEq.component_name,
    serial_number: subEq.serial_number || '',
    status: subEq.status,
    notes: subEq.notes || '',
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  isEditing.value = false
  editingId.value = null
}

async function handleSubmit() {
  if (!formData.value.component_name.trim()) {
    uiStore.showNotification('error', 'Please enter component name')
    return
  }

  submitting.value = true

  try {
    if (isEditing.value && editingId.value) {
      // Update
      await subEquipmentStore.update(editingId.value, {
        component_name: formData.value.component_name,
        serial_number: formData.value.serial_number || undefined,
        notes: formData.value.notes || undefined,
      })
      uiStore.showNotification('success', 'Sub-equipment updated successfully')
    } else {
      // Create
      await subEquipmentStore.create({
        parent_equipment_id: props.parentEquipmentId,
        component_name: formData.value.component_name,
        serial_number: formData.value.serial_number || undefined,
        notes: formData.value.notes || undefined,
      })
      uiStore.showNotification('success', 'Sub-equipment created successfully')
    }
    closeModal()
    await subEquipmentStore.fetchList(props.parentEquipmentId)
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Operation failed')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(subEq: SubEquipment) {
  if (!confirm(`Are you sure you want to delete sub-equipment "${subEq.component_name}"?`)) return

  try {
    await subEquipmentStore.remove(subEq.id)
    uiStore.showNotification('success', 'Sub-equipment deleted successfully')
    await subEquipmentStore.fetchList(props.parentEquipmentId)
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Delete failed')
  }
}

onMounted(async () => {
  await subEquipmentStore.fetchList(props.parentEquipmentId)
})
</script>
