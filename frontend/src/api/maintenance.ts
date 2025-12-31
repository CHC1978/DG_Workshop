/**
 * Maintenance API
 */
import apiClient from './client'

export interface Maintenance {
  id: number
  equipment_id: number
  maintenance_date: string
  next_due_date: string
  provider: string
  service_type?: string
  cost?: number
  report_url?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface MaintenanceDueSoon {
  maintenance: Maintenance
  equipment_asset_code: string
  equipment_name: string
  days_until_due: number
  is_overdue: boolean
}

export const maintenanceApi = {
  /**
   * Get maintenance list
   */
  list(skip = 0, limit = 100, equipment_id?: number) {
    return apiClient.get<{ maintenances: Maintenance[]; total: number }>('/maintenance', {
      params: { skip, limit, equipment_id },
    })
  },

  /**
   * Get maintenance due soon (within specified days)
   */
  getDueSoon(days = 30) {
    return apiClient.get<MaintenanceDueSoon[]>('/maintenance/due-soon', {
      params: { days },
    })
  },

  /**
   * Get maintenance by ID
   */
  get(id: number) {
    return apiClient.get<Maintenance>(`/maintenance/${id}`)
  },

  /**
   * Create maintenance
   */
  create(data: Partial<Maintenance>) {
    return apiClient.post<Maintenance>('/maintenance', data)
  },

  /**
   * Update maintenance
   */
  update(id: number, data: Partial<Maintenance>) {
    return apiClient.put<Maintenance>(`/maintenance/${id}`, data)
  },

  /**
   * Delete maintenance
   */
  delete(id: number) {
    return apiClient.delete(`/maintenance/${id}`)
  },

  /**
   * Get maintenance for specific equipment
   */
  getEquipmentMaintenance(equipmentId: number, skip = 0, limit = 100) {
    return apiClient.get<Maintenance[]>(`/maintenance/equipment/${equipmentId}`, {
      params: { skip, limit },
    })
  },
}
