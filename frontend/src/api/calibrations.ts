/**
 * Calibrations API
 */
import apiClient from './client'

export interface Calibration {
  id: number
  equipment_id: number
  calibration_date: string
  next_due_date: string
  provider: string
  certificate_number?: string
  cost?: number
  notes?: string
  created_at: string
  updated_at: string
}

export interface CalibrationDueSoon {
  calibration: Calibration
  equipment_asset_code: string
  equipment_name: string
  days_until_due: number
  is_overdue: boolean
}

export const calibrationsApi = {
  /**
   * Get calibrations list
   */
  list(skip = 0, limit = 100, equipment_id?: number) {
    return apiClient.get<{ calibrations: Calibration[]; total: number }>('/calibrations', {
      params: { skip, limit, equipment_id },
    })
  },

  /**
   * Get calibrations due soon (within specified days)
   */
  getDueSoon(days = 30) {
    return apiClient.get<CalibrationDueSoon[]>('/calibrations/due-soon', {
      params: { days },
    })
  },

  /**
   * Get calibration by ID
   */
  get(id: number) {
    return apiClient.get<Calibration>(`/calibrations/${id}`)
  },

  /**
   * Create calibration
   */
  create(data: Partial<Calibration>) {
    return apiClient.post<Calibration>('/calibrations', data)
  },

  /**
   * Update calibration
   */
  update(id: number, data: Partial<Calibration>) {
    return apiClient.put<Calibration>(`/calibrations/${id}`, data)
  },

  /**
   * Delete calibration
   */
  delete(id: number) {
    return apiClient.delete(`/calibrations/${id}`)
  },

  /**
   * Get calibrations for specific equipment
   */
  getEquipmentCalibrations(equipmentId: number, skip = 0, limit = 100) {
    return apiClient.get<Calibration[]>(`/calibrations/equipment/${equipmentId}`, {
      params: { skip, limit },
    })
  },
}
