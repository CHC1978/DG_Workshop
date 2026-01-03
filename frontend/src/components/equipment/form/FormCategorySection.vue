<template>
  <div class="space-y-4">
    <!-- Category Selection -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Category <span class="text-red-500">*</span>
      </label>
      <select
        :value="category"
        required
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
        :disabled="showParentSelector && !!selectedParent"
        @change="handleCategoryChange"
      >
        <option value="">Select category...</option>
        <option value="mbes">MBES - Multibeam Echosounder</option>
        <option value="gnss">GNSS - Receiver</option>
        <option value="svp">SVP - Sound Velocity Profiler</option>
        <option value="sbp">SBP - Sub-bottom Profiler</option>
        <option value="usbl">USBL - Ultra-Short Baseline</option>
        <option value="rov">ROV - Remotely Operated Vehicle</option>
        <option value="ins">INS - Inertial Navigation System</option>
        <option value="magnetometer">Magnetometer</option>
        <option value="other">Other</option>
      </select>
      <p v-if="showParentSelector && selectedParent" class="mt-1 text-sm text-gray-500">
        Category inherited from parent equipment
      </p>
    </div>

    <!-- Equipment Type Selection (Create mode only) -->
    <div v-if="!isEdit && category" class="p-4 bg-gray-50 rounded-lg border border-gray-200">
      <label class="block text-sm font-medium text-gray-700 mb-3">
        Equipment Type <span class="text-red-500">*</span>
      </label>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label
          class="relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm hover:border-sky-500 transition-colors"
          :class="!showParentSelector ? 'border-sky-500 ring-2 ring-sky-500' : 'border-gray-300'"
        >
          <input
            type="radio"
            name="equipmentType"
            :value="false"
            :checked="!showParentSelector"
            class="sr-only"
            @change="$emit('update:showParentSelector', false)"
          />
          <div class="flex-1">
            <span class="block text-sm font-medium text-gray-900">Standalone Equipment</span>
            <span class="mt-1 flex items-center text-sm text-gray-500">
              Independent equipment unit
            </span>
          </div>
        </label>
        <label
          class="relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm hover:border-sky-500 transition-colors"
          :class="showParentSelector ? 'border-sky-500 ring-2 ring-sky-500' : 'border-gray-300'"
        >
          <input
            type="radio"
            name="equipmentType"
            :value="true"
            :checked="showParentSelector"
            class="sr-only"
            @change="$emit('update:showParentSelector', true)"
          />
          <div class="flex-1">
            <span class="block text-sm font-medium text-gray-900">Sub-Component</span>
            <span class="mt-1 flex items-center text-sm text-gray-500">
              Part of a parent equipment
            </span>
          </div>
        </label>
      </div>
    </div>

    <!-- Parent Equipment Selection -->
    <div v-if="!isEdit && showParentSelector && category" class="p-4 bg-sky-50 rounded-lg border border-sky-200">
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Parent Equipment <span class="text-red-500">*</span>
      </label>
      <select
        :value="parentEquipmentId"
        required
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 sm:text-sm"
        @change="handleParentChange"
      >
        <option :value="null">Select parent equipment...</option>
        <option v-for="eq in availableParentEquipment" :key="eq.id" :value="eq.id">
          {{ eq.asset_code }} - {{ eq.manufacturer }} {{ eq.model }}
        </option>
      </select>
      <p class="mt-1 text-sm text-gray-500">
        Child component will inherit category and manufacturer from parent
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Equipment } from '@/types'

interface Props {
  category: string
  isEdit: boolean
  showParentSelector: boolean
  parentEquipmentId: number | null
  availableParentEquipment: Equipment[]
  selectedParent: Equipment | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:category', value: string): void
  (e: 'update:showParentSelector', value: boolean): void
  (e: 'update:parentEquipmentId', value: number | null): void
  (e: 'category-change'): void
  (e: 'parent-change', parentId: number | null): void
}>()

function handleCategoryChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('update:category', target.value)
  emit('category-change')
}

function handleParentChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const parentId = target.value ? parseInt(target.value) : null
  emit('update:parentEquipmentId', parentId)
  emit('parent-change', parentId)
}
</script>
