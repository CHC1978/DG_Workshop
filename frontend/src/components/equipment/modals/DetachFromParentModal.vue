<template>
  <BaseModal :show="show" title="Detach from Parent Equipment" @close="$emit('close')">
    <div v-if="equipment" class="space-y-4">
      <!-- Equipment Info -->
      <div class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
        <p class="text-sm font-medium text-gray-900">{{ equipment.asset_code }}</p>
        <p class="text-xs text-gray-600">{{ equipment.manufacturer }} {{ equipment.model }}</p>
      </div>

      <!-- New Location -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Move to Location <span class="text-red-500">*</span>
        </label>
        <select
          v-model="detachForm.locationId"
          class="w-full px-3 py-2 border rounded-lg"
          required
        >
          <option :value="null">Select location...</option>
          <option v-for="location in locations" :key="location.id" :value="location.id">
            {{ location.name }} ({{ locationTypeLabel(location.location_type) }})
          </option>
        </select>
      </div>

      <!-- New Status -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Set Status <span class="text-red-500">*</span>
        </label>
        <select
          v-model="detachForm.status"
          class="w-full px-3 py-2 border rounded-lg"
          required
        >
          <option value="in_stock">In Stock</option>
          <option value="deployed">Deployed</option>
          <option value="rented">Rented</option>
          <option value="repair">Repair</option>
          <option value="calibrating">Calibrating</option>
        </select>
      </div>

      <!-- Notes -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Reason for Detaching (optional)
        </label>
        <textarea
          v-model="detachForm.notes"
          class="w-full px-3 py-2 border rounded-lg"
          rows="3"
          placeholder="Enter reason for detaching this component..."
        ></textarea>
      </div>
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="$emit('close')">Cancel</AppButton>
      <AppButton @click="submitDetach" :disabled="!detachForm.locationId">Detach</AppButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { equipmentApi } from '@/api/equipment'
import { useUiStore } from '@/stores/ui'
import BaseModal from '@/components/common/BaseModal.vue'
import AppButton from '@/components/common/AppButton.vue'
import type { Equipment, Location } from '@/types'

interface Props {
  show: boolean
  equipment: Equipment | null
  locations: Location[]
}

interface Emits {
  (e: 'close'): void
  (e: 'detached', equipmentId: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const uiStore = useUiStore()

const detachForm = ref({
  locationId: null as number | null,
  status: 'in_stock' as string,
  notes: ''
})

// Reset form when modal closes
watch(() => props.show, (newShow) => {
  if (!newShow) {
    detachForm.value = { locationId: null, status: 'in_stock', notes: '' }
  }
})

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

async function submitDetach() {
  if (!props.equipment || !detachForm.value.locationId) return

  try {
    await equipmentApi.detachFromParent(props.equipment.id, {
      new_location_id: detachForm.value.locationId,
      new_status: detachForm.value.status,
      notes: detachForm.value.notes || undefined
    })
    uiStore.showNotification('success', `${props.equipment.asset_code} detached successfully`)

    emit('detached', props.equipment.id)
    emit('close')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to detach equipment')
  }
}
</script>
