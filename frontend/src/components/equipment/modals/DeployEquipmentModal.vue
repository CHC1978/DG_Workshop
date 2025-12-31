<template>
  <!-- Deploy Equipment Modal -->
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Deploy Equipment</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Deploy to Location
          </label>
          <select
            v-model="deployForm.locationId"
            class="w-full px-3 py-2 border rounded-lg"
            required
          >
            <option :value="null">Select location...</option>
            <option v-for="location in locations" :key="location.id" :value="location.id">
              {{ location.name }} ({{ location.location_type }})
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
          <textarea
            v-model="deployForm.notes"
            class="w-full px-3 py-2 border rounded-lg"
            rows="3"
            placeholder="Enter deployment notes..."
          ></textarea>
        </div>

        <!-- Include Children Option -->
        <div v-if="childrenCount > 0" class="p-3 bg-sky-50 border border-sky-200 rounded-lg">
          <label class="flex items-start gap-2 cursor-pointer">
            <input
              type="checkbox"
              v-model="deployForm.includeChildren"
              class="mt-1 w-4 h-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500"
            />
            <div class="flex-1">
              <span class="text-sm font-medium text-gray-900">Move Child Components Together</span>
              <p class="text-xs text-gray-600 mt-1">
                Deploy all {{ childrenCount }} child component(s) to the same location
              </p>
            </div>
          </label>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t">
          <AppButton variant="secondary" @click="$emit('close')">Cancel</AppButton>
          <AppButton @click="handleDeploy" :disabled="!deployForm.locationId">Deploy</AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { equipmentApi } from '@/api/equipment'
import { useUiStore } from '@/stores/ui'
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
  (e: 'deployed', data: { success: boolean; movedCount?: number; targetLocation?: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const uiStore = useUiStore()

const deployForm = ref({
  locationId: null as number | null,
  notes: '',
  includeChildren: true
})

// Reset form when modal closes
watch(() => props.show, (newShow) => {
  if (!newShow) {
    deployForm.value = { locationId: null, notes: '', includeChildren: true }
  }
})

async function handleDeploy() {
  if (!props.equipment || !deployForm.value.locationId) return

  const includeChildren = deployForm.value.includeChildren && props.childrenCount > 0

  try {
    if (includeChildren) {
      // Use groupMove API to move parent and children together
      const response = await equipmentApi.groupMove(props.equipment.id, {
        location_id: deployForm.value.locationId,
        include_children: true,
        notes: deployForm.value.notes || undefined
      })
      uiStore.showNotification('success',
        `${response.data.moved_count} equipment(s) deployed to ${response.data.target_location}`
      )
      emit('deployed', {
        success: true,
        movedCount: response.data.moved_count,
        targetLocation: response.data.target_location
      })
    } else {
      // Original deploy API for single equipment
      await equipmentApi.deploy(
        props.equipment.id,
        deployForm.value.locationId,
        deployForm.value.notes || undefined
      )
      uiStore.showNotification('success', 'Equipment deployed successfully')
      emit('deployed', { success: true })
    }

    emit('close')
  } catch (error: any) {
    uiStore.showNotification('error', error.response?.data?.detail || 'Failed to deploy equipment')
  }
}
</script>
