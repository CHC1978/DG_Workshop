/**
 * Dashboard API
 */
import apiClient from './client'

export interface DashboardStats {
  total_equipment: number
  in_stock: number
  deployed: number
  rented: number
  in_repair: number
  active_rentals: number
  maintenance_due_soon: number
  calibration_due_soon: number
  overdue_rentals: number
}

export interface MaintenanceAlert {
  equipment_id: number
  asset_code: string
  manufacturer: string
  model: string
  next_maintenance_date: string
  days_until_due: number
  is_overdue: boolean
}

export interface CalibrationAlert {
  equipment_id: number
  asset_code: string
  manufacturer: string
  model: string
  calibration_id: number
  next_due_date: string
  days_until_due: number
  is_overdue: boolean
}

export interface RentalAlert {
  rental_id: number
  rental_number: string
  equipment_asset_code: string
  customer_company: string
  expected_end_date: string
  days_overdue: number
}

export interface DashboardAlerts {
  maintenance_alerts: MaintenanceAlert[]
  calibration_alerts: CalibrationAlert[]
  overdue_rentals: RentalAlert[]
}

export interface RecentActivity {
  id: number
  equipment_id: number
  asset_code: string
  manufacturer: string
  model: string
  log_type: string
  description: string
  created_by_username: string | null
  created_at: string
  // Location information
  current_location_name?: string
  current_location_type?: string
  // Project information
  project_code?: string
  project_name?: string
  // Transfer information (From → To display)
  old_value?: string
  new_value?: string
}

export const dashboardApi = {
  getStats() {
    return apiClient.get<DashboardStats>('/dashboard/stats')
  },

  getAlerts() {
    return apiClient.get<DashboardAlerts>('/dashboard/alerts')
  },

  getRecentActivities(limit = 10) {
    return apiClient.get<RecentActivity[]>('/dashboard/recent-activities', {
      params: { limit },
    })
  },

  clearActivities() {
    return apiClient.delete<{ message: string; deleted_count: number }>('/dashboard/recent-activities')
  },
}
