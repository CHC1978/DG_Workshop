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
  needs_2fa_setup?: boolean
  trusted_device?: boolean
  message: string
}

export interface LoginStep2Request {
  temp_token?: string  // Optional: now in httpOnly cookie
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

export type InstallationType = 'permanent' | 'project' | 'temporary'

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
  model_code?: string
  project_id?: number
  installation_type?: InstallationType
  installation_date?: string
  installation_notes?: string

  // Parent-Child relationship
  parent_equipment_id?: number

  is_active: boolean
  created_at: string
  updated_at: string

  // Display fields for Location and Project
  current_location_name?: string
  current_location_type?: string
  project_code?: string
  project_name?: string

  // Display fields for Parent Equipment
  parent_asset_code?: string
  parent_model?: string
  children_count?: number
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
  model_code?: string
  project_id?: number
  installation_type?: InstallationType
  installation_date?: string
  installation_notes?: string

  // Parent-Child relationship
  parent_equipment_id?: number
}

// ==================== Parent-Child Equipment Management ====================

export interface DetachFromParentRequest {
  new_location_id: number
  new_status: string
  notes?: string
}

export interface GroupMoveRequest {
  location_id: number
  include_children?: boolean
  notes?: string
}

export interface SyncChildrenStatusRequest {
  new_status: EquipmentStatus
  include_children?: boolean
  notes?: string
}

// ==================== Location ====================

export type LocationType = 'warehouse' | 'vessel' | 'person' | 'external'

export interface Location {
  id: number
  name: string
  location_type: LocationType
  code?: string

  // Vessel identifiers (legacy)
  imo_number?: string
  call_sign?: string
  owner_company?: string

  // Vessel identifiers (new - multiple options)
  vessel_mmsi?: string
  vessel_national_id?: string
  vessel_internal_code?: string

  // Vessel information
  vessel_name?: string
  vessel_flag?: string
  vessel_type?: string
  vessel_owner?: string

  // Person fields
  person_name?: string
  person_contact?: string
  employee_id?: string
  department?: string

  // Project association
  current_project_id?: number

  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LocationDetail extends Location {
  equipment_count: number
  project_name?: string
  project_code?: string
}

export interface LocationCreateRequest {
  name: string
  location_type: LocationType
  code?: string
  imo_number?: string
  call_sign?: string
  owner_company?: string
  vessel_mmsi?: string
  vessel_national_id?: string
  vessel_internal_code?: string
  vessel_name?: string
  vessel_flag?: string
  vessel_type?: string
  vessel_owner?: string
  person_name?: string
  person_contact?: string
  employee_id?: string
  department?: string
  current_project_id?: number
}

export interface LocationListResponse {
  locations: Location[]
  total: number
}

// ==================== Project ====================

export type ProjectStatus = 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled'

export interface Project {
  id: number
  code: string
  name: string
  description?: string
  client_name?: string
  client_contact?: string
  client_phone?: string
  client_email?: string
  start_date?: string
  end_date?: string
  status: ProjectStatus
  is_active: boolean
  created_at: string
  updated_at: string
  vessel_count: number
  equipment_count: number
}

export interface ProjectCreateRequest {
  code: string
  name: string
  description?: string
  client_name?: string
  client_contact?: string
  client_phone?: string
  client_email?: string
  start_date?: string
  end_date?: string
  status: ProjectStatus
}

export interface ProjectListResponse {
  projects: Project[]
  total: number
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
