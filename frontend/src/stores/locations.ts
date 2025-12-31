import { defineStore } from 'pinia'
import { ref } from 'vue'
import { locationApi, type LocationFilters } from '@/api/locations'
import type { Location, LocationDetail, LocationCreateRequest } from '@/types'

export const useLocationStore = defineStore('locations', () => {
  const locations = ref<Location[]>([])
  const currentLocation = ref<LocationDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalPages = ref(0)

  // Fetch all locations with optional filters
  async function fetchLocations(params?: LocationFilters) {
    loading.value = true
    error.value = null
    try {
      const response = await locationApi.getAll(params)
      locations.value = response.data.locations
      total.value = response.data.total
      currentPage.value = response.data.page || 1
      pageSize.value = response.data.page_size || params?.limit || 20
      totalPages.value = response.data.total_pages || Math.ceil(total.value / pageSize.value)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch locations'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch location by ID with details
  async function fetchById(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await locationApi.getById(id)
      currentLocation.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch location'
      currentLocation.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create new location
  async function createLocation(data: LocationCreateRequest) {
    loading.value = true
    error.value = null
    try {
      const response = await locationApi.create(data)
      locations.value.unshift(response.data)
      total.value += 1
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create location'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update location
  async function updateLocation(id: number, data: Partial<LocationCreateRequest>) {
    loading.value = true
    error.value = null
    try {
      const response = await locationApi.update(id, data)
      const index = locations.value.findIndex((l) => l.id === id)
      if (index !== -1) {
        locations.value[index] = response.data
      }
      if (currentLocation.value?.id === id) {
        // Merge updated data with current location details
        currentLocation.value = { ...currentLocation.value, ...response.data }
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update location'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Delete location (soft delete)
  async function deleteLocation(id: number) {
    loading.value = true
    error.value = null
    try {
      await locationApi.delete(id)
      locations.value = locations.value.filter((l) => l.id !== id)
      total.value -= 1
      if (currentLocation.value?.id === id) {
        currentLocation.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete location'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Clear current location
  function clearCurrentLocation() {
    currentLocation.value = null
  }

  // Clear error
  function clearError() {
    error.value = null
  }

  return {
    // State
    locations,
    currentLocation,
    loading,
    error,
    total,
    currentPage,
    pageSize,
    totalPages,

    // Actions
    fetchLocations,
    fetchById,
    createLocation,
    updateLocation,
    deleteLocation,
    clearCurrentLocation,
    clearError,
  }
})
