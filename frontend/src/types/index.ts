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
  // Person 資訊欄位（從 Location type=person 合併）
  employee_id?: string
  department?: string
  phone?: string
  photo_url?: string
  created_at: string
  updated_at: string
}

// 簡化的使用者資訊（用於聯繫人/負責人下拉選單）
export interface UserStaff {
  id: number
  username: string
  full_name: string
  employee_id?: string
  department?: string
  photo_url?: string
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

export interface SessionInfo {
  id: number
  device_fingerprint?: string
  user_agent?: string
  ip_address?: string
  created_at?: string
  last_used_at?: string
  expires_at?: string
  is_current: boolean
}

export interface SessionsResponse {
  sessions: SessionInfo[]
  total: number
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

  // 設備負責人（Person 合併到 User 後使用）
  assigned_user_id?: number
  assigned_user_name?: string

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

  // 設備負責人
  assigned_user_id?: number
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

export type LocationType = 'warehouse' | 'vessel' | 'platform' | 'vehicle' | 'external'

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

  // Photo (for Vessel and Person)
  photo_url?: string

  // Warehouse fields
  address?: string
  phone?: string
  email?: string

  // Contact person (舊欄位，待遷移後移除)
  contact_person_id?: number

  // Contact user (新欄位，Person 合併到 User 後使用)
  contact_user_id?: number

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
  contact_person_name?: string  // 舊欄位
  contact_user_name?: string    // 新欄位
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
  photo_url?: string
  address?: string
  phone?: string
  email?: string
  contact_person_id?: number  // 舊欄位
  contact_user_id?: number    // 新欄位
  current_project_id?: number
}

export interface LocationListResponse {
  locations: Location[]
  total: number
  page?: number
  page_size?: number
  total_pages?: number
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

// ==================== Equipment Log ====================

export type EquipmentLogType =
  | 'create'
  | 'update'
  | 'deploy'
  | 'return'
  | 'repair'
  | 'calibration'
  | 'status_change'
  | 'note'
  | 'maintenance'
  | 'scan'
  | 'transfer'
  | 'deactivate'

export interface EquipmentLog {
  id: number
  equipment_id: number
  log_type: EquipmentLogType
  title: string
  details?: string
  old_status?: EquipmentStatus
  new_status?: EquipmentStatus
  old_location_id?: number
  new_location_id?: number
  old_project_id?: number
  new_project_id?: number
  latitude?: number
  longitude?: number
  is_active: boolean
  created_at: string
  updated_at?: string
  created_by_id?: number
  edited_by_id?: number

  // Display fields
  created_by_username?: string
  edited_by_username?: string
  old_location_name?: string
  new_location_name?: string
  old_project_name?: string
  new_project_name?: string

  // Attachment info
  attachments_count?: number
}

export interface LogAttachment {
  id: number
  log_id: number
  file_name: string
  file_path: string
  file_type: string
  file_size: number
  attachment_type: string
  description?: string
  created_at: string
  created_by_id?: number
  created_by_username?: string
}

// ==================== Maintenance ====================

export interface Maintenance {
  id: number
  equipment_id: number
  maintenance_date: string
  next_due_date?: string
  maintenance_type: string
  description?: string
  performed_by?: string
  cost?: number
  notes?: string
  created_at: string
  updated_at: string

  // Display fields
  equipment_asset_code?: string
  equipment_model?: string
}

export interface MaintenanceCreateRequest {
  equipment_id: number
  maintenance_date: string
  next_due_date?: string
  maintenance_type: string
  description?: string
  performed_by?: string
  cost?: number
  notes?: string
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
  report_url?: string
  created_at: string
  updated_at: string

  // Display fields
  equipment_asset_code?: string
  equipment_model?: string
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

// ==================== Filter Types ====================

export interface PaginationFilter {
  skip?: number
  limit?: number
}

export interface EquipmentFilter extends PaginationFilter {
  search?: string
  category?: EquipmentCategory | ''
  status?: EquipmentStatus | ''
  is_active?: boolean
}

export interface LocationFilter extends PaginationFilter {
  search?: string
  location_type?: LocationType | ''
  is_active?: boolean
}

export interface ProjectFilter extends PaginationFilter {
  search?: string
  status?: ProjectStatus | ''
  is_active?: boolean
}

export interface CalibrationFilter extends PaginationFilter {
  equipment_id?: number
  due_within_days?: number
  overdue_only?: boolean
}

export interface MaintenanceFilter extends PaginationFilter {
  equipment_id?: number
  due_within_days?: number
  overdue_only?: boolean
}

export interface UserFilter extends PaginationFilter {
  search?: string
  role?: UserRole | ''
  is_active?: boolean
}

// ==================== User Management Types ====================

export interface UserCreateRequest {
  username: string
  email: string
  full_name: string
  password: string
  role: UserRole
  // Person 資訊欄位
  employee_id?: string
  department?: string
  phone?: string
}

export interface UserUpdateRequest {
  email?: string
  full_name?: string
  role?: UserRole
  is_active?: boolean
  // Person 資訊欄位
  employee_id?: string
  department?: string
  phone?: string
}

export interface PasswordUpdateRequest {
  old_password: string
  new_password: string
}
