<template>
  <BaseModal :show="show" title="Set to In Stock" @close="$emit('close')">
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Location
        </label>
        <select
          v-model="inStockForm.locationId"
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
          Date
        </label>
        <input
          type="date"
          v-model="inStockForm.date"
          class="w-full px-3 py-2 border rounded-lg"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
        <textarea
          v-model="inStockForm.notes"
          class="w-full px-3 py-2 border rounded-lg"
          rows="3"
          placeholder="Enter notes..."
        ></textarea>
      </div>

      <!-- Include Children Option -->
      <div v-if="childrenCount > 0" class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
        <label class="flex items-start gap-2 cursor-pointer">
          <input
            type="checkbox"
            v-model="inStockForm.includeChildren"
            class="mt-1 w-4 h-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500"
          />
          <div class="flex-1">
            <span class="text-sm font-medium text-gray-900">Include Child Components</span>
            <p class="text-xs text-gray-600 mt-1">
              Set all {{ childrenCount }} child component(s) to in stock as well
            </p>
          </div>
        </label>
      </div>
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="$emit('close')">Cancel</AppButton>
      <AppButton @click="handleSubmit" :loading="submitting">Set to In Stock</AppButton>
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
  (e: 'submitted', data: { success: boolean }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const uiStore = useUiStore()

const submitting = ref(false)

// Filter locations to show only warehouses and persons
const filteredLocations = computed(() =>
  props.locations.filter(l => l.location_type === 'warehouse' || l.location_type === 'person')
)

const inStockForm = ref({
  locationId: null as number | null,
  date: new Date().toISOString().split('T')[0],
  notes: '',
  includeChildren: true
})

// Reset form when modal closes
watch(() => props.show, (newShow) => {
  if (!newShow) {
    inStockForm.value = {
      locationId: null,
      date: new Date().toISOString().split('T')[0],
      notes: '',
      includeChildren: true
    }
  }
})

async function handleSubmit() {
  if (!props.equipment) return

  submitting.value = true

  try {
    // Build notes with date info
    let fullNotes = inStockForm.value.notes || 'Set to in stock'
    if (inStockForm.value.date) {
      fullNotes += ` | Date: ${inStockForm.value.date}`
    }

    // Update status and location
    await equipmentApi.update(props.equipment.id, {
      status: 'in_stock',
      current_location_id: inStockForm.value.locationId || undefined
    })

    uiStore.showNotification('success', 'Equipment set to in stock')
    emit('submitted', { success: true })
    emit('close')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to set status')
  } finally {
    submitting.value = false
  }
}
</script>
