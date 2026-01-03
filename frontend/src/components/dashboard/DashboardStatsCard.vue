<template>
  <div
    class="bg-white rounded-lg shadow p-4 sm:p-6 cursor-pointer hover:shadow-lg transition-shadow"
    @click="$emit('click')"
  >
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">{{ title }}</h2>
      <span class="text-2xl">{{ iconEmoji }}</span>
    </div>
    <p :class="['text-3xl font-bold', colorClass]">{{ value }}</p>
    <p class="text-sm text-gray-600 mt-2">{{ subtitle }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  icon: string
  value: number
  subtitle: string
  color?: 'green' | 'blue' | 'orange' | 'purple' | 'yellow' | 'red'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'blue',
})

defineEmits<{
  (e: 'click'): void
}>()

const iconMap: Record<string, string> = {
  box: '\uD83D\uDCE6',      // 📦
  ship: '\uD83D\uDEA2',     // 🚢
  wrench: '\uD83D\uDD27',   // 🔧
  clipboard: '\uD83D\uDCCB', // 📋
  alert: '\u26A0\uFE0F',    // ⚠️
  chart: '\uD83D\uDCCA',    // 📊
  clock: '\u23F0',          // ⏰
}

const iconEmoji = computed(() => iconMap[props.icon] || props.icon)

const colorClasses: Record<string, string> = {
  green: 'text-green-600',
  blue: 'text-blue-600',
  orange: 'text-orange-600',
  purple: 'text-purple-600',
  yellow: 'text-yellow-600',
  red: 'text-red-600',
}

const colorClass = colorClasses[props.color] || 'text-blue-600'
</script>
