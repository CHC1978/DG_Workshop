<template>
  <BaseModal :show="show" title="Return Equipment" @close="$emit('close')">
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Return to
        </label>
        <select
          v-model="returnForm.locationId"
          class="w-full px-3 py-2 border rounded-lg"
          required
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
          v-model="returnForm.notes"
          class="w-full px-3 py-2 border rounded-lg"
          rows="3"
          placeholder="Enter return notes..."
        ></textarea>
      </div>

      <!-- Include Children Option -->
      <div v-if="childrenCount > 0" class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
        <label class="flex items-start gap-2 cursor-pointer">
          <input
            type="checkbox"
            v-model="returnForm.includeChildren"
            class="mt-1 w-4 h-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500"
          />
          <div class="flex-1">
            <span class="text-sm font-medium text-gray-900">Return Child Components Together</span>
            <p class="text-xs text-gray-600 mt-1">
              Return all {{ childrenCount }} child component(s) to the same location
            </p>
          </div>
        </label>
      </div>
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="$emit('close')">Cancel</AppButton>
      <AppButton @click="handleReturn" :disabled="!returnForm.locationId">Return</AppButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { equipmentApi } from '@/api/equipment'
import { useUiStore } from '@/stores/ui'
import BaseModal from '@/components/common/BaseModal.vue'
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
  (e: 'returned', data: { success: boolean; movedCount?: number; targetLocation?: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const uiStore = useUiStore()

// Filter locations to show only warehouses and persons
const filteredLocations = computed(() =>
  props.locations.filter(l => l.location_type === 'warehouse' || l.location_type === 'person')
)

const returnForm = ref({
  locationId: null as number | null,
  notes: '',
  includeChildren: true
})

// Reset form when modal closes
watch(() => props.show, (newShow) => {
  if (!newShow) {
    returnForm.value = { locationId: null, notes: '', includeChildren: true }
  }
})

async function handleReturn() {
  if (!props.equipment || !returnForm.value.locationId) return

  const includeChildren = returnForm.value.includeChildren && props.childrenCount > 0

  try {
    if (includeChildren) {
      // Use groupMove API to return parent and children together
      const response = await equipmentApi.groupMove(props.equipment.id, {
        location_id: returnForm.value.locationId,
        include_children: true,
        notes: returnForm.value.notes || undefined
      })
      uiStore.showNotification('success',
        `${response.data.moved_count} equipment(s) returned to ${response.data.target_location}`
      )
      emit('returned', {
        success: true,
        movedCount: response.data.moved_count,
        targetLocation: response.data.target_location
      })
    } else {
      // Original return API for single equipment
      await equipmentApi.return(
        props.equipment.id,
        returnForm.value.locationId,
        returnForm.value.notes || undefined
      )
      uiStore.showNotification('success', 'Equipment returned successfully')
      emit('returned', { success: true })
    }

    emit('close')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to return equipment')
  }
}
</script>
