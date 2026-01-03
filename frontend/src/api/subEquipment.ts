/**
 * SubEquipment API
 */
import apiClient from './client'
import type {
  SubEquipment,
  SubEquipmentDetail,
  SubEquipmentCreateRequest,
  SubEquipmentListResponse,
} from '@/types'

export const subEquipmentApi = {
  /**
   * List sub-equipment with optional filtering
   */
  list(parentEquipmentId?: number) {
    const params: { parent_equipment_id?: number } = {}
    if (parentEquipmentId) {
      params.parent_equipment_id = parentEquipmentId
    }
    return apiClient.get<SubEquipmentListResponse>('/sub-equipment', { params })
  },

  /**
   * Get sub-equipment by ID
   */
  get(id: number) {
    return apiClient.get<SubEquipmentDetail>(`/sub-equipment/${id}`)
  },

  /**
   * Create sub-equipment
   */
  create(data: SubEquipmentCreateRequest) {
    return apiClient.post<SubEquipment>('/sub-equipment', data)
  },

  /**
   * Update sub-equipment
   */
  update(id: number, data: Partial<SubEquipmentCreateRequest>) {
    return apiClient.put<SubEquipment>(`/sub-equipment/${id}`, data)
  },

  /**
   * Delete sub-equipment (soft delete)
   */
  delete(id: number) {
    return apiClient.delete(`/sub-equipment/${id}`)
  },

  /**
   * Get sub-equipment logs
   */
  getLogs(id: number) {
    return apiClient.get(`/sub-equipment/${id}/logs`)
  },

  /**
   * Get QR code info (base64)
   */
  getQRCode(id: number) {
    return apiClient.get(`/qrcode/sub/${id}`)
  },
}
