import apiClient from './client'

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
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled'
  is_active: boolean
  created_at: string
  updated_at: string
  vessel_count: number
  equipment_count: number
}

export interface ProjectCreate {
  code: string
  name: string
  description?: string
  client_name?: string
  client_contact?: string
  client_phone?: string
  client_email?: string
  start_date?: string
  end_date?: string
  status?: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled'
}

export interface ProjectUpdate {
  code?: string
  name?: string
  description?: string
  client_name?: string
  client_contact?: string
  client_phone?: string
  client_email?: string
  start_date?: string
  end_date?: string
  status?: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled'
  is_active?: boolean
}

export interface ProjectListResponse {
  projects: Project[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const projectApi = {
  // Get all projects with pagination and filters
  getAll: (params?: {
    skip?: number
    limit?: number
    status?: string
    search?: string
    is_active?: boolean
  }) => {
    return apiClient.get<ProjectListResponse>('/projects', { params })
  },

  // Get project by ID
  getById: (id: number) => {
    return apiClient.get<Project>(`/projects/${id}`)
  },

  // Create new project
  create: (data: ProjectCreate) => {
    return apiClient.post<Project>('/projects', data)
  },

  // Update project
  update: (id: number, data: ProjectUpdate) => {
    return apiClient.put<Project>(`/projects/${id}`, data)
  },

  // Delete project (soft delete)
  delete: (id: number) => {
    return apiClient.delete(`/projects/${id}`)
  },
}
