/**
 * Location API Client
 */
import apiClient from './client'
import type {
  Location,
  LocationDetail,
  LocationCreateRequest,
  LocationListResponse,
} from '@/types'

export interface LocationFilters {
  skip?: number
  limit?: number
  location_type?: string
  search?: string
  is_active?: boolean
  project_id?: number
}

export const locationApi = {
  /**
   * Get all locations with filters
   */
  getAll: (params?: LocationFilters) =>
    apiClient.get<LocationListResponse>('/locations', { params }),

  /**
   * Get location by ID with details (includes equipment_count and project info)
   */
  getById: (id: number) =>
    apiClient.get<LocationDetail>(`/locations/${id}`),

  /**
   * Create a new location
   */
  create: (data: LocationCreateRequest) =>
    apiClient.post<Location>('/locations', data),

  /**
   * Update an existing location
   */
  update: (id: number, data: Partial<LocationCreateRequest>) =>
    apiClient.put<Location>(`/locations/${id}`, data),

  /**
   * Delete a location (soft delete)
   */
  delete: (id: number) =>
    apiClient.delete(`/locations/${id}`),

  /**
   * Get equipment at location
   */
  getEquipment: (id: number) =>
    apiClient.get(`/locations/${id}/equipment`),
}
