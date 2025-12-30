/**
 * UI state store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  // State
  const sidebarOpen = ref(true)
  const loading = ref(false)
  const notification = ref<{
    show: boolean
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
  }>({
    show: false,
    type: 'info',
    message: '',
  })

  // Actions
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function showNotification(
    type: 'success' | 'error' | 'warning' | 'info',
    message: string,
    duration = 3000
  ) {
    notification.value = { show: true, type, message }

    if (duration > 0) {
      setTimeout(() => {
        notification.value.show = false
      }, duration)
    }
  }

  function hideNotification() {
    notification.value.show = false
  }

  function setLoading(value: boolean) {
    loading.value = value
  }

  return {
    // State
    sidebarOpen,
    loading,
    notification,
    // Actions
    toggleSidebar,
    showNotification,
    hideNotification,
    setLoading,
  }
})
