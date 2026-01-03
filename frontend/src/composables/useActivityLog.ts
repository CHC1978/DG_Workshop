/**
 * Activity Log Composable
 * Shared logic for parsing and displaying activity logs
 */

export interface LogInfo {
  status?: string
  location?: {
    id?: number
    name?: string
    type?: string
  }
  is_active?: boolean
  last_maintenance_date?: string
  next_maintenance_date?: string
  parent_equipment_id?: number | null
  parent_asset_code?: string
}

export interface ActivityLog {
  id: number
  equipment_id: number
  asset_code: string
  manufacturer: string
  model: string
  log_type: string
  description: string
  old_value?: string
  new_value?: string
  project_code?: string
  created_by_username?: string
  created_at: string
}

export function useActivityLog() {
  /**
   * Format date time string to localized format
   */
  function formatDateTime(dateStr: string): string {
    return new Date(dateStr).toLocaleString('zh-TW')
  }

  /**
   * Get human-readable label for log type
   */
  function logTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      status_change: 'Status',
      location_change: 'Location',
      rental_start: 'Rental',
      rental_end: 'Return',
      calibration: 'Calibration',
      maintenance: 'Maintenance',
      note: 'Note',
      created: 'Created',
      updated: 'Updated',
    }
    return labels[type] || type
  }

  /**
   * Get badge CSS class for log type
   */
  function logTypeBadge(type: string): string {
    const base = 'inline-block'
    const variants: Record<string, string> = {
      status_change: 'bg-blue-100 text-blue-800',
      location_change: 'bg-purple-100 text-purple-800',
      rental_start: 'bg-green-100 text-green-800',
      rental_end: 'bg-orange-100 text-orange-800',
      calibration: 'bg-yellow-100 text-yellow-800',
      maintenance: 'bg-red-100 text-red-800',
      note: 'bg-gray-100 text-gray-800',
      created: 'bg-sky-100 text-sky-800',
      updated: 'bg-indigo-100 text-indigo-800',
    }
    return `${base} ${variants[type] || 'bg-gray-100 text-gray-800'}`
  }

  /**
   * Get human-readable label for location type
   */
  function locationTypeLabel(type?: string): string {
    if (!type) return ''
    const labels: Record<string, string> = {
      warehouse: 'Warehouse',
      vessel: 'Vessel',
      person: 'Person',
      external: 'External',
      platform: 'Platform',
      vehicle: 'Vehicle',
    }
    return labels[type] || type
  }

  /**
   * Get badge CSS class for location type
   */
  function locationBadgeClass(type?: string): string {
    const classes: Record<string, string> = {
      warehouse: 'bg-amber-100 text-amber-800',
      vessel: 'bg-blue-100 text-blue-800',
      person: 'bg-green-100 text-green-800',
      external: 'bg-purple-100 text-purple-800',
      platform: 'bg-cyan-100 text-cyan-800',
      vehicle: 'bg-orange-100 text-orange-800',
    }
    return classes[type || ''] || 'bg-gray-100 text-gray-800'
  }

  /**
   * Parse JSON log info from old_value/new_value
   */
  function parseLogInfo(value?: string): LogInfo | null {
    if (!value) return null
    try {
      if (value.startsWith('{')) {
        return JSON.parse(value) as LogInfo
      }
      return null
    } catch {
      return null
    }
  }

  /**
   * Check if this is a transfer log (has location info)
   */
  function isTransferLog(activity: ActivityLog): boolean {
    if (!activity.new_value || !activity.new_value.startsWith('{')) return false
    try {
      const parsed = JSON.parse(activity.new_value)
      return parsed.location !== undefined
    } catch {
      return false
    }
  }

  /**
   * Check if this is a maintenance log (has maintenance dates)
   */
  function isMaintenanceLog(activity: ActivityLog): boolean {
    if (!activity.new_value || !activity.new_value.startsWith('{')) return false
    try {
      const parsed = JSON.parse(activity.new_value)
      return parsed.last_maintenance_date !== undefined || parsed.next_maintenance_date !== undefined
    } catch {
      return false
    }
  }

  /**
   * Check if this is a status-only log (no location)
   */
  function isStatusOnlyLog(activity: ActivityLog): boolean {
    if (!activity.new_value || !activity.new_value.startsWith('{')) return false
    try {
      const parsed = JSON.parse(activity.new_value)
      return parsed.status !== undefined && parsed.location === undefined
    } catch {
      return false
    }
  }

  /**
   * Check if this is a delete/deactivate log
   */
  function isDeactivateLog(activity: ActivityLog): boolean {
    if (!activity.new_value || !activity.new_value.startsWith('{')) return false
    try {
      const parsed = JSON.parse(activity.new_value)
      return parsed.is_active !== undefined
    } catch {
      return false
    }
  }

  return {
    formatDateTime,
    logTypeLabel,
    logTypeBadge,
    locationTypeLabel,
    locationBadgeClass,
    parseLogInfo,
    isTransferLog,
    isMaintenanceLog,
    isStatusOnlyLog,
    isDeactivateLog,
  }
}
