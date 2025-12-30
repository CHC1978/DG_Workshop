/**
 * SubEquipment store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { subEquipmentApi } from '@/api/subEquipment'
import type { SubEquipment, SubEquipmentDetail, SubEquipmentCreateRequest } from '@/types'

export const useSubEquipmentStore = defineStore('subEquipment', () => {
  // State
  const subEquipmentList = ref<SubEquipment[]>([])
  const currentSubEquipment = ref<SubEquipmentDetail | null>(null)
  const total = ref(0)
  const loading = ref(false)

  // Actions
  async function fetchList(parentEquipmentId?: number) {
    loading.value = true
    try {
      const response = await subEquipmentApi.list(parentEquipmentId)
      subEquipmentList.value = response.data.sub_equipments
      total.value = response.data.total
    } catch (error) {
      console.error('Failed to fetch sub-equipment list:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchById(id: number) {
    loading.value = true
    try {
      const response = await subEquipmentApi.get(id)
      currentSubEquipment.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch sub-equipment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function create(data: SubEquipmentCreateRequest) {
    loading.value = true
    try {
      const response = await subEquipmentApi.create(data)
      subEquipmentList.value.unshift(response.data)
      total.value++
      return response.data
    } catch (error) {
      console.error('Failed to create sub-equipment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function update(id: number, data: Partial<SubEquipmentCreateRequest>) {
    loading.value = true
    try {
      const response = await subEquipmentApi.update(id, data)
      const index = subEquipmentList.value.findIndex((se) => se.id === id)
      if (index !== -1) {
        subEquipmentList.value[index] = response.data
      }
      if (currentSubEquipment.value?.id === id) {
        currentSubEquipment.value = { ...currentSubEquipment.value, ...response.data }
      }
      return response.data
    } catch (error) {
      console.error('Failed to update sub-equipment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number) {
    loading.value = true
    try {
      await subEquipmentApi.delete(id)
      subEquipmentList.value = subEquipmentList.value.filter((se) => se.id !== id)
      total.value--
    } catch (error) {
      console.error('Failed to delete sub-equipment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function clearCurrent() {
    currentSubEquipment.value = null
  }

  return {
    // State
    subEquipmentList,
    currentSubEquipment,
    total,
    loading,
    // Actions
    fetchList,
    fetchById,
    create,
    update,
    remove,
    clearCurrent,
  }
})
