/**
 * Location API
 */
import apiClient from './client'
import type { Location } from '@/types'

export interface LocationListResponse {
  locations: Location[]
  total: number
}

export const locationApi = {
  /**
   * List locations
   */
  list(skip = 0, limit = 100, locationType?: string) {
    return apiClient.get<LocationListResponse>('/locations', {
      params: { skip, limit, location_type: locationType },
    })
  },

  /**
   * Get location by ID
   */
  get(id: number) {
    return apiClient.get<Location>(`/locations/${id}`)
  },

  /**
   * Create location
   */
  create(data: Partial<Location>) {
    return apiClient.post<Location>('/locations', data)
  },

  /**
   * Update location
   */
  update(id: number, data: Partial<Location>) {
    return apiClient.put<Location>(`/locations/${id}`, data)
  },

  /**
   * Delete location
   */
  delete(id: number) {
    return apiClient.delete(`/locations/${id}`)
  },

  /**
   * Get equipment at location
   */
  getEquipment(id: number) {
    return apiClient.get(`/locations/${id}/equipment`)
  },
}
