/**
 * Equipment API
 */
import apiClient from './client'
import type { Equipment, EquipmentCreateRequest } from '@/types'

export interface EquipmentListResponse {
  equipments: Equipment[]
  total: number
}

export interface EquipmentFilters {
  skip?: number
  limit?: number
  category?: string
  status?: string
  location_id?: number
  search?: string
}

export const equipmentApi = {
  /**
   * List equipment with filters
   */
  list(filters?: EquipmentFilters) {
    return apiClient.get<EquipmentListResponse>('/equipment', { params: filters })
  },

  /**
   * Get equipment by ID
   */
  get(id: number) {
    return apiClient.get<Equipment>(`/equipment/${id}`)
  },

  /**
   * Get equipment by QR code (asset code)
   */
  getByQR(assetCode: string) {
    return apiClient.get<Equipment>(`/equipment/by-qr/${assetCode}`)
  },

  /**
   * Create equipment
   */
  create(data: EquipmentCreateRequest) {
    return apiClient.post<Equipment>('/equipment', data)
  },

  /**
   * Update equipment
   */
  update(id: number, data: Partial<EquipmentCreateRequest>) {
    return apiClient.put<Equipment>(`/equipment/${id}`, data)
  },

  /**
   * Delete equipment
   */
  delete(id: number) {
    return apiClient.delete(`/equipment/${id}`)
  },

  /**
   * Get equipment logs
   */
  getLogs(id: number) {
    return apiClient.get(`/equipment/${id}/logs`)
  },

  /**
   * Deploy equipment
   */
  deploy(
    id: number,
    locationId: number,
    notes?: string,
    latitude?: number,
    longitude?: number
  ) {
    return apiClient.post<Equipment>(`/equipment/${id}/deploy`, {
      location_id: locationId,
      notes,
      latitude,
      longitude,
    })
  },

  /**
   * Return equipment
   */
  return(
    id: number,
    locationId: number,
    notes?: string,
    latitude?: number,
    longitude?: number
  ) {
    return apiClient.post<Equipment>(`/equipment/${id}/return`, {
      location_id: locationId,
      notes,
      latitude,
      longitude,
    })
  },

  /**
   * Send equipment to repair
   */
  repair(id: number, notes?: string) {
    return apiClient.post<Equipment>(`/equipment/${id}/repair`, { notes })
  },

  /**
   * Add note to equipment
   */
  addNote(id: number, note: string, latitude?: number, longitude?: number) {
    return apiClient.post(`/equipment/${id}/note`, {
      note,
      latitude,
      longitude,
    })
  },

  /**
   * Get QR code image URL
   */
  getQRCodeImageUrl(id: number) {
    return `/api/qrcode/${id}/image`
  },

  /**
   * Get QR code info (base64)
   */
  getQRCode(id: number) {
    return apiClient.get(`/qrcode/${id}`)
  },
}
