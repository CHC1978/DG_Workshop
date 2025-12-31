<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
      <div>
        <h2 class="text-lg font-semibold text-gray-900">Child Components</h2>
        <p class="text-xs text-gray-500 mt-1">{{ children.length }} component(s)</p>
      </div>
      <div v-if="canEdit" class="flex gap-2">
        <AppButton
          variant="primary"
          size="sm"
          @click="openAttachModal"
        >
          Attach Existing
        </AppButton>
      </div>
    </div>

    <div v-if="loadingChildren" class="text-center py-12 text-gray-500">
      Loading components...
    </div>

    <div v-else-if="children.length === 0" class="text-center py-12 text-gray-500">
      No child components yet
    </div>

    <div v-else class="divide-y divide-gray-200">
      <div
        v-for="child in children"
        :key="child.id"
        class="p-4 hover:bg-gray-50 transition-colors"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <h3
                class="font-semibold text-sky-700 hover:text-sky-900 hover:underline cursor-pointer"
                @click="navigateToChild(child.id)"
              >
                {{ child.asset_code }}
              </h3>
              <span :class="statusBadgeClass(child.status)" class="px-2 py-1 text-xs rounded">
                {{ statusLabel(child.status) }}
              </span>
            </div>
            <p class="text-sm text-gray-700">{{ child.model }}</p>
            <p v-if="child.serial_number" class="text-xs text-gray-500 mt-1 font-mono">SN: {{ child.serial_number }}</p>
            <div v-if="child.current_location_name" class="mt-2 text-xs text-gray-600">
              📍 {{ locationTypeLabel(child.current_location_type) }}: {{ child.current_location_name }}
            </div>
          </div>
          <div class="flex-shrink-0">
            <button
              v-if="canDetach"
              @click.stop="$emit('detach', child)"
              class="text-xs px-3 py-1 text-orange-600 hover:text-orange-800 hover:bg-orange-50 rounded transition-colors border border-orange-300"
              title="Detach from parent (Manager+ only)"
            >
              Detach
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Attach Existing Equipment Modal -->
    <div
      v-if="showAttachModal"
      class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
      @click.self="closeAttachModal"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Attach Existing Equipment</h3>
          <button @click="closeAttachModal" class="text-gray-400 hover:text-gray-600">
            ✕
          </button>
        </div>

        <p class="text-sm text-gray-600 mb-4">
          Select an existing standalone equipment to attach as a child component.
          Only equipment with the same category ({{ parentCategory?.toUpperCase() }}) are shown.
        </p>

        <!-- Search Filter -->
        <div class="mb-4">
          <input
            v-model="attachSearch"
            type="text"
            placeholder="Search by asset code, manufacturer, or model..."
            class="w-full px-3 py-2 border rounded-lg"
          />
        </div>

        <!-- Loading State -->
        <div v-if="loadingAvailable" class="text-center py-8">
          <p class="text-gray-500">Loading available equipment...</p>
        </div>

        <!-- No Equipment Available -->
        <div v-else-if="filteredAvailable.length === 0" class="text-center py-8">
          <p class="text-gray-500">No available equipment found</p>
        </div>

        <!-- Equipment List -->
        <div v-else class="space-y-2 mb-4 max-h-96 overflow-y-auto">
          <label
            v-for="eq in filteredAvailable"
            :key="eq.id"
            class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
            :class="selectedEquipment?.id === eq.id ? 'border-sky-500 bg-sky-50' : 'border-gray-200'"
          >
            <input
              type="radio"
              name="equipmentToAttach"
              :value="eq"
              v-model="selectedEquipment"
              class="w-4 h-4 text-sky-600"
            />
            <div class="flex-1">
              <p class="font-semibold text-gray-900">{{ eq.asset_code }}</p>
              <p class="text-sm text-gray-600">{{ eq.manufacturer }} {{ eq.model }}</p>
              <p v-if="eq.serial_number" class="text-xs text-gray-500 font-mono">SN: {{ eq.serial_number }}</p>
              <div v-if="eq.current_location_name" class="mt-1 text-xs text-gray-600">
                📍 {{ eq.current_location_name }}
              </div>
            </div>
            <span :class="statusBadgeClass(eq.status)" class="px-2 py-1 text-xs rounded">
              {{ statusLabel(eq.status) }}
            </span>
          </label>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-4 border-t">
          <AppButton variant="secondary" @click="closeAttachModal">
            Cancel
          </AppButton>
          <AppButton
            @click="handleAttach"
            :disabled="!selectedEquipment"
            :loading="attaching"
          >
            Attach Equipment
          </AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { equipmentApi } from '@/api/equipment'
import { useUiStore } from '@/stores/ui'
import AppButton from '@/components/common/AppButton.vue'
import type { Equipment } from '@/types'

interface Props {
  parentEquipmentId: number
  parentCategory: string
  canEdit: boolean
  canDetach: boolean
}

interface Emits {
  (e: 'detach', child: Equipment): void
  (e: 'childrenUpdated'): void
  (e: 'childrenLoaded', children: Equipment[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const router = useRouter()
const uiStore = useUiStore()

// Children state
const children = ref<Equipment[]>([])
const loadingChildren = ref(false)

// Attach modal state
const showAttachModal = ref(false)
const availableEquipment = ref<Equipment[]>([])
const loadingAvailable = ref(false)
const selectedEquipment = ref<Equipment | null>(null)
const attachSearch = ref('')
const attaching = ref(false)

// Filtered available equipment
const filteredAvailable = computed(() => {
  if (!attachSearch.value) {
    return availableEquipment.value
  }

  const search = attachSearch.value.toLowerCase()
  return availableEquipment.value.filter(eq =>
    eq.asset_code?.toLowerCase().includes(search) ||
    eq.manufacturer?.toLowerCase().includes(search) ||
    eq.model?.toLowerCase().includes(search)
  )
})

// Watch parentEquipmentId and auto-load children
watch(() => props.parentEquipmentId, async (newId) => {
  if (newId) {
    await loadChildren()
  }
}, { immediate: true })

async function loadChildren() {
  if (!props.parentEquipmentId) return

  loadingChildren.value = true
  try {
    const response = await equipmentApi.getChildren(props.parentEquipmentId)
    children.value = response.data
    emit('childrenLoaded', response.data)
  } catch (error) {
    console.error('Failed to load children equipment:', error)
    children.value = []
    emit('childrenLoaded', [])
  } finally {
    loadingChildren.value = false
  }
}

async function openAttachModal() {
  showAttachModal.value = true
  await loadAvailableEquipment()
}

function closeAttachModal() {
  showAttachModal.value = false
  selectedEquipment.value = null
  attachSearch.value = ''
}

async function loadAvailableEquipment() {
  loadingAvailable.value = true
  try {
    // Load all equipment with same category, excluding children and current parent
    const response = await equipmentApi.list({
      skip: 0,
      limit: 1000,
      category: props.parentCategory
    })

    // Filter to only show standalone equipment (not already children)
    availableEquipment.value = response.data.equipments.filter(
      (eq: any) => !eq.parent_equipment_id && eq.id !== props.parentEquipmentId
    )
  } catch (error) {
    console.error('Failed to load available equipment:', error)
    availableEquipment.value = []
  } finally {
    loadingAvailable.value = false
  }
}

async function handleAttach() {
  if (!selectedEquipment.value) return

  attaching.value = true
  try {
    const updateData = {
      parent_equipment_id: props.parentEquipmentId
    }

    // Update the selected equipment to set its parent_equipment_id
    await equipmentApi.update(selectedEquipment.value.id, updateData)

    uiStore.showNotification('success', `${selectedEquipment.value.asset_code} attached successfully`)

    closeAttachModal()

    // Reload children list (which will emit childrenLoaded) and notify parent
    await loadChildren()
    emit('childrenUpdated')
  } catch (error: any) {
    console.error('Failed to attach equipment:', error)
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to attach equipment')
  } finally {
    attaching.value = false
  }
}

function navigateToChild(childId: number) {
  router.push(`/equipment/${childId}`)
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    ordering: 'Ordering',
    in_stock: 'In Stock',
    deployed: 'Deployed',
    rented: 'Rented',
    repair: 'Repair',
    disposed: 'Disposed',
    lost: 'Lost',
    calibrating: 'Calibrating',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const base = 'inline-block font-semibold rounded'
  const variants: Record<string, string> = {
    ordering: 'bg-yellow-100 text-yellow-800',
    in_stock: 'bg-green-100 text-green-800',
    deployed: 'bg-blue-100 text-blue-800',
    rented: 'bg-purple-100 text-purple-800',
    repair: 'bg-orange-100 text-orange-800',
    disposed: 'bg-gray-100 text-gray-800',
    lost: 'bg-red-100 text-red-800',
    calibrating: 'bg-cyan-100 text-cyan-800',
  }
  return `${base} ${variants[status] || 'bg-gray-100 text-gray-800'}`
}

function locationTypeLabel(type?: string): string {
  if (!type) return ''
  const labels: Record<string, string> = {
    warehouse: 'Warehouse',
    vessel: 'Vessel',
    person: 'Person',
    external: 'External',
    platform: 'Platform',
    vehicle: 'Vehicle',
  }
  return labels[type] || type
}

// Expose reload method for parent component
defineExpose({
  loadChildren
})
</script>
