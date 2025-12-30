/**
 * TypeScript type definitions
 */

// ==================== User & Auth ====================

export type UserRole = 'admin' | 'manager' | 'operator' | 'viewer'

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: UserRole
  totp_enabled: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginStep1Request {
  username: string
  password: string
  device_fingerprint?: string
  device_name?: string
}

export interface LoginStep1Response {
  temp_token?: string
  access_token?: string
  totp_required: boolean
  trusted_device?: boolean
  message: string
}

export interface LoginStep2Request {
  temp_token: string
  totp_code: string
  remember_device?: boolean
  device_fingerprint?: string
  device_name?: string
}

export interface LoginStep2Response {
  access_token: string
  token_type: string
  user_id: number
  username: string
  role: string
}

export interface Setup2FAResponse {
  secret: string
  qr_code: string
  backup_codes: string[]
  message: string
}

// ==================== Equipment ====================

export type EquipmentCategory =
  | 'mbes'
  | 'gnss'
  | 'svp'
  | 'sbp'
  | 'usbl'
  | 'rov'
  | 'ins'
  | 'magnetometer'
  | 'other'

export type EquipmentStatus =
  | 'ordering'
  | 'in_stock'
  | 'deployed'
  | 'rented'
  | 'repair'
  | 'calibrating'
  | 'disposed'
  | 'lost'

export interface Equipment {
  id: number
  asset_code: string
  qr_code: string
  category: EquipmentCategory
  manufacturer: string
  model: string
  serial_number?: string
  status: EquipmentStatus
  current_location_id?: number
  purchase_date?: string
  photo_url?: string
  manual_url?: string
  calibration_report_url?: string
  specifications?: string
  notes?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EquipmentCreateRequest {
  category: EquipmentCategory
  manufacturer: string
  model: string
  serial_number?: string
  purchase_date?: string
  photo_url?: string
  manual_url?: string
  calibration_report_url?: string
  current_location_id?: number
  specifications?: string
  notes?: string
}

// ==================== Location ====================

export type LocationType =
  | 'warehouse'
  | 'vessel'
  | 'platform'
  | 'vehicle'
  | 'external'

export interface Location {
  id: number
  name: string
  location_type: LocationType
  code?: string
  imo_number?: string
  call_sign?: string
  owner_company?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// ==================== Customer ====================

export interface Customer {
  id: number
  company_name: string
  tax_id?: string
  contact_person: string
  phone: string
  email?: string
  address?: string
  notes?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// ==================== Rental ====================

export type RentalStatus =
  | 'draft'
  | 'confirmed'
  | 'active'
  | 'overdue'
  | 'returned'
  | 'cancelled'

export interface Rental {
  id: number
  rental_number: string
  equipment_id: number
  customer_id: number
  start_date: string
  expected_end_date: string
  actual_end_date?: string
  daily_rate: number
  deposit_amount?: number
  total_amount?: number
  status: RentalStatus
  notes?: string
  delivery_notes?: string
  return_notes?: string
  created_at: string
  updated_at: string
}

// ==================== Calibration ====================

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

// ==================== SubEquipment ====================

export interface SubEquipment {
  id: number
  parent_equipment_id: number
  asset_code: string
  qr_code: string
  component_name: string
  serial_number?: string
  status: EquipmentStatus
  notes?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SubEquipmentDetail extends SubEquipment {
  parent_asset_code?: string
  parent_model?: string
}

export interface SubEquipmentCreateRequest {
  parent_equipment_id: number
  component_name: string
  serial_number?: string
  notes?: string
}

export interface SubEquipmentListResponse {
  sub_equipments: SubEquipment[]
  total: number
}

// ==================== API Response ====================

export interface ApiResponse<T> {
  data: T
}

export interface ListResponse<T> {
  items: T[]
  total: number
}

export interface ApiError {
  detail: string
}
