/**
 * Composable for equipment-related label and badge formatting
 */

export function useEquipmentLabels() {
  /**
   * Get category display label
   */
  function categoryLabel(category: string): string {
    const labels: Record<string, string> = {
      mbes: 'MBES - Multibeam Echosounder',
      gnss: 'GNSS - Receiver',
      svp: 'SVP - Sound Velocity Profiler',
      sbp: 'SBP - Sub-bottom Profiler',
      usbl: 'USBL - Ultra-Short Baseline',
      rov: 'ROV - Remotely Operated Vehicle',
      ins: 'INS - Inertial Navigation System',
      magnetometer: 'Magnetometer',
      other: 'Other',
    }
    return labels[category] || category
  }

  /**
   * Get status display label
   * @param status - Equipment status
   * @param locationType - Optional location type for contextual label
   */
  function statusLabel(status: string, locationType?: string): string {
    // When deployed to a Vessel, show "Operational" instead of "Deployed"
    if (status === 'deployed' && locationType === 'vessel') {
      return 'Operational'
    }

    const labels: Record<string, string> = {
      ordering: 'Ordering',
      in_stock: 'In Stock',
      deployed: 'Deployed',
      rented: 'Rented',
      repair: 'Repair',
      disposed: 'Disposed',
      lost: 'Lost',
    }
    return labels[status] || status
  }

  /**
   * Get status badge CSS class
   */
  function statusBadgeClass(status: string): string {
    const base = 'inline-block font-semibold rounded'
    const variants: Record<string, string> = {
      ordering: 'bg-yellow-100 text-yellow-800',
      in_stock: 'bg-green-100 text-green-800',
      deployed: 'bg-blue-100 text-blue-800',
      rented: 'bg-purple-100 text-purple-800',
      repair: 'bg-orange-100 text-orange-800',
      disposed: 'bg-gray-100 text-gray-800',
      lost: 'bg-red-100 text-red-800',
    }
    return `${base} ${variants[status] || 'bg-gray-100 text-gray-800'}`
  }

  /**
   * Get log type display label
   */
  function logTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      status_change: 'Status',
      location_change: 'Location',
      rental_start: 'Rental Start',
      rental_end: 'Rental End',
      calibration: 'Calibration',
      maintenance: 'Maintenance',
      note: 'Note',
      created: 'Created',
      updated: 'Updated',
    }
    return labels[type] || type
  }

  /**
   * Get log type badge CSS class
   */
  function logTypeBadgeClass(type: string): string {
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
   * Get location type display label
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
   * Format date string to localized date
   */
  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('zh-TW')
  }

  /**
   * Format date string to localized date and time
   */
  function formatDateTime(dateStr: string): string {
    return new Date(dateStr).toLocaleString('zh-TW')
  }

  return {
    categoryLabel,
    statusLabel,
    statusBadgeClass,
    logTypeLabel,
    logTypeBadgeClass,
    locationTypeLabel,
    formatDate,
    formatDateTime,
  }
}
