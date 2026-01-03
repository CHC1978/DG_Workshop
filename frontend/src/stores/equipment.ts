/**
 * Equipment store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { equipmentApi, type EquipmentFilters } from '@/api/equipment'
import type { Equipment, EquipmentCreateRequest } from '@/types'

export const useEquipmentStore = defineStore('equipment', () => {
  // State
  const equipmentList = ref<Equipment[]>([])
  const currentEquipment = ref<Equipment | null>(null)
  const total = ref(0)
  const loading = ref(false)

  // Actions
  async function fetchList(filters?: EquipmentFilters) {
    loading.value = true
    try {
      if (import.meta.env.DEV) {
        console.log('[equipmentStore.fetchList] Fetching with filters:', filters)
      }
      const response = await equipmentApi.list(filters)
      if (import.meta.env.DEV) {
        console.log('[equipmentStore.fetchList] Got response:', response.data)
      }
      equipmentList.value = response.data.equipments
      total.value = response.data.total
      if (import.meta.env.DEV) {
        console.log('[equipmentStore.fetchList] Updated list, count:', equipmentList.value.length)
      }
    } catch (error) {
      console.error('[equipmentStore.fetchList] Failed:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchById(id: number) {
    loading.value = true
    try {
      const response = await equipmentApi.get(id)
      currentEquipment.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch equipment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchByQR(assetCode: string) {
    loading.value = true
    try {
      const response = await equipmentApi.getByQR(assetCode)
      currentEquipment.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch equipment by QR:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function create(data: EquipmentCreateRequest) {
    loading.value = true
    try {
      const response = await equipmentApi.create(data)
      equipmentList.value.unshift(response.data)
      total.value++
      return response.data
    } catch (error) {
      console.error('Failed to create equipment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function update(id: number, data: Partial<EquipmentCreateRequest>) {
    loading.value = true
    try {
      const response = await equipmentApi.update(id, data)
      const index = equipmentList.value.findIndex((eq) => eq.id === id)
      if (index !== -1) {
        equipmentList.value[index] = response.data
      }
      if (currentEquipment.value?.id === id) {
        currentEquipment.value = response.data
      }
      return response.data
    } catch (error) {
      console.error('Failed to update equipment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    loading.value = true
    try {
      await equipmentApi.delete(id)
      equipmentList.value = equipmentList.value.filter((eq) => eq.id !== id)
      total.value--
    } catch (error) {
      console.error('Failed to delete equipment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function clearCurrent() {
    currentEquipment.value = null
  }

  return {
    // State
    equipmentList,
    currentEquipment,
    total,
    loading,
    // Actions
    fetchList,
    fetchById,
    fetchByQR,
    create,
    update,
    remove,
    clearCurrent,
  }
})
